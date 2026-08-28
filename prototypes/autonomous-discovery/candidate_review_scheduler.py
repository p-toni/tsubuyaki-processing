"""Post-search scheduling for evidence-authoritative candidate review tasks.

The existing selector's eager pair-queue path remains the default. This module
supports the opt-in collect->flush path validated by the triad queue replay
experiments: unresolved comparisons are collected without changing search
traversal, then a bounded batch is materialized after the replay. Dependency-safe
fixed siblings may share one transitivity-free A/B/C review panel; every other
comparison remains an ordinary v3 pair task.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from review_evidence_queue import create_review_bundle, pair_id_for_phenotypes
from triad_pair_matrix_review_queue import (
    PAIR_KEYS,
    create_triad_pair_matrix_bundle,
    triad_matrix_id_for_phenotypes,
)

SAFE_TRIAD_STAGES = frozenset(("explore", "roundA"))


@dataclass(frozen=True)
class ReviewProposal:
    index: int
    pair_id: str
    brief_text: str
    a_id: str
    b_id: str
    afp: str
    bfp: str
    a_frames: tuple
    b_frames: tuple
    a_route: str
    b_route: str
    a_stage: str
    b_stage: str
    a_parent: str | None
    b_parent: str | None
    review_group: str | None = None

    @property
    def structural_group(self) -> str:
        if self.a_route == self.b_route:
            return f"route:{self.a_route}"
        return "cross:" + "|".join(sorted((self.a_route, self.b_route)))


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def pending_pair_ids(queue_dir: Path | None) -> set[str]:
    if queue_dir is None:
        return set()
    doc = _load_json(Path(queue_dir) / "decisions.json")
    return {
        pid
        for pid, item in doc.get("decisions", {}).items()
        if item.get("verdict") is None
    }


def pending_triad_ids(queue_dir: Path | None) -> set[str]:
    if queue_dir is None:
        return set()
    doc = _load_json(Path(queue_dir) / "decisions.json")
    pending = set()
    for tid, item in doc.get("decisions", {}).items():
        verdicts = item.get("pairVerdicts")
        if not isinstance(verdicts, dict) or any(verdicts.get(key) is None for key in PAIR_KEYS):
            pending.add(tid)
    return pending


def _existing_pair_ids(queue_dir: Path | None) -> set[str]:
    if queue_dir is None:
        return set()
    return set(_load_json(Path(queue_dir) / "decisions.json").get("decisions", {}))


def _existing_triad_ids(queue_dir: Path | None) -> set[str]:
    if queue_dir is None:
        return set()
    return set(_load_json(Path(queue_dir) / "decisions.json").get("decisions", {}))


def _safe_sibling(proposal: ReviewProposal) -> bool:
    return (
        proposal.a_route == proposal.b_route
        and proposal.b_stage in SAFE_TRIAD_STAGES
        and proposal.b_parent == proposal.a_id
    )


def _triad_for(
    proposal: ReviewProposal,
    unresolved: Sequence[ReviewProposal],
    *,
    authoritative_pair_ids: set[str],
    existing_triad_ids: set[str],
    times: Sequence[float],
):
    if not _safe_sibling(proposal):
        return None
    for other in unresolved:
        if other.index <= proposal.index:
            continue
        if other.structural_group != proposal.structural_group:
            continue
        if other.a_id != proposal.a_id or other.afp != proposal.afp:
            continue
        if other.b_stage != proposal.b_stage or not _safe_sibling(other):
            continue
        if other.b_id == proposal.b_id or other.bfp == proposal.bfp:
            continue
        bc_pair_id = pair_id_for_phenotypes(
            brief=proposal.brief_text,
            times=times,
            a_fingerprint=proposal.bfp,
            b_fingerprint=other.bfp,
        )
        pair_ids = {proposal.pair_id, other.pair_id, bc_pair_id}
        if pair_ids & authoritative_pair_ids:
            continue
        task_id = triad_matrix_id_for_phenotypes(
            brief=proposal.brief_text,
            times=times,
            fingerprints=(proposal.afp, proposal.bfp, other.bfp),
        )
        if task_id in existing_triad_ids:
            continue
        return proposal, other, bc_pair_id, task_id
    return None


def flush_review_proposals(
    proposals: Sequence[ReviewProposal],
    *,
    evidence: Sequence,
    pair_queue_dir: Path,
    triad_queue_dir: Path | None,
    times: Sequence[float],
    enable_triads: bool,
    max_tasks: int | None,
    max_tasks_per_group: int | None,
) -> list[dict]:
    """Materialize one bounded review batch after a search replay.

    Existing pending pair or triad work blocks creation of a new batch. This keeps
    reviewer rounds explicit and prevents speculative queue growth. A triad is
    eligible only at the fixed-sibling boundary proven by replay experiments; no
    relation is inferred from ranking or transitivity.
    """
    if max_tasks is not None and max_tasks < 1:
        raise ValueError("max_tasks must be >= 1 or None")
    if max_tasks_per_group is not None and max_tasks_per_group < 1:
        raise ValueError("max_tasks_per_group must be >= 1 or None")
    pair_queue_dir = Path(pair_queue_dir)
    triad_queue_dir = Path(triad_queue_dir) if triad_queue_dir is not None else None
    if pending_pair_ids(pair_queue_dir) or pending_triad_ids(triad_queue_dir):
        return []

    authoritative_pair_ids = {ev.pair_id for ev in evidence if getattr(ev, "authoritative", False)}
    unresolved = [
        proposal
        for proposal in sorted(proposals, key=lambda p: p.index)
        if proposal.pair_id not in authoritative_pair_ids
    ]
    existing_pair_ids = _existing_pair_ids(pair_queue_dir)
    existing_triad_ids = _existing_triad_ids(triad_queue_dir)
    selected: list[dict] = []
    covered_pair_ids: set[str] = set()
    group_counts: dict[str, int] = {}

    def group_available(proposal: ReviewProposal) -> bool:
        if proposal.review_group is None or max_tasks_per_group is None:
            return True
        return group_counts.get(proposal.review_group, 0) < max_tasks_per_group

    def consume_group(proposal: ReviewProposal) -> None:
        if proposal.review_group is not None:
            group_counts[proposal.review_group] = group_counts.get(proposal.review_group, 0) + 1

    for proposal in unresolved:
        if max_tasks is not None and len(selected) >= max_tasks:
            break
        if proposal.pair_id in covered_pair_ids or not group_available(proposal):
            continue

        triad = None
        if enable_triads and triad_queue_dir is not None:
            triad = _triad_for(
                proposal,
                unresolved,
                authoritative_pair_ids=authoritative_pair_ids,
                existing_triad_ids=existing_triad_ids,
                times=times,
            )
        if triad is not None:
            first, second, bc_pair_id, expected_task_id = triad
            task_id = create_triad_pair_matrix_bundle(
                triad_queue_dir,
                brief=first.brief_text,
                times=times,
                a_frames=first.a_frames,
                b_frames=first.b_frames,
                c_frames=second.b_frames,
                a_candidate_id=first.a_id,
                b_candidate_id=first.b_id,
                c_candidate_id=second.b_id,
                review_group=first.review_group,
            )
            if task_id != expected_task_id:
                raise RuntimeError("triad review bundle id drift")
            pair_ids = {first.pair_id, second.pair_id, bc_pair_id}
            covered_pair_ids.update(pair_ids)
            existing_triad_ids.add(task_id)
            consume_group(first)
            selected.append(
                {
                    "kind": "triad",
                    "id": task_id,
                    "group": first.review_group,
                    "pairIds": sorted(pair_ids),
                }
            )
            continue

        # A resolved weak decision already stored in this queue cannot be safely
        # overwritten by create_review_bundle. It must receive fresh evidence via
        # another bundle (for example an eligible triad) or an external evidence
        # directory, matching the existing eager selector semantics.
        if proposal.pair_id in existing_pair_ids:
            continue
        created = create_review_bundle(
            pair_queue_dir,
            brief=proposal.brief_text,
            times=times,
            a_frames=proposal.a_frames,
            b_frames=proposal.b_frames,
            a_candidate_id=proposal.a_id,
            b_candidate_id=proposal.b_id,
            review_group=proposal.review_group,
        )
        if created != proposal.pair_id:
            raise RuntimeError("pair review bundle id drift")
        existing_pair_ids.add(created)
        covered_pair_ids.add(created)
        consume_group(proposal)
        selected.append(
            {
                "kind": "pair",
                "id": created,
                "group": proposal.review_group,
                "pairIds": [created],
            }
        )
    return selected
