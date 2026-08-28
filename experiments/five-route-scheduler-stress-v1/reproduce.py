#!/usr/bin/env python3
"""Final scheduler-semantic stress: five routes, normal probe depth, larger search."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "prototypes" / "autonomous-discovery"
sys.path.insert(0, str(PROTO))

# Register orbit before loading modules that snapshot/use core.ROUTES.
from orbit_representation import register_orbit
register_orbit()

BASE_PATH = ROOT / "experiments" / "screened-triad-runtime-replay-v1" / "reproduce.py"
spec = importlib.util.spec_from_file_location("screened_runtime_replay_v1", BASE_PATH)
base = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(base)

ROUTES = ("recurrence", "orbit", "family", "sheet", "filament")
SEEDS = (89, 97)
BRIEFS = {
    "living-form": {
        "intent": "Discover an original mathematically generated living form with coherent material, strong composition, and meaningful motion across time. Prefer distinctive non-generic structure over merely filling the canvas.",
        "bbox": [0.55, 0.82],
    },
    "open-asymmetry": {
        "intent": "Discover a living mathematical form with asymmetric open structure, deliberate negative space, coherent material, and motion that changes the form without dissolving it.",
        "bbox": [0.45, 0.74],
    },
    "layered-field": {
        "intent": "Discover a broad layered living field with connected material, internal organization, and meaningful temporal deformation. Prefer structure with depth over generic canvas filling.",
        "bbox": [0.62, 0.90],
    },
}
ORACLE_ID = "synthetic-five-route-scheduler-stress-oracle-v1"
ROUTE_SCREEN_ID = "synthetic-five-route-all-keep-stress-fixture-v1"
PROBE_BUDGET = 10
TOTAL_START_BUDGET = 15

# Use a fresh deterministic preference function while preserving the exact queue decoder.
base.ORACLE_ID = ORACLE_ID


def _brief(name: str) -> dict:
    if name not in BRIEFS:
        raise ValueError(f"unknown brief {name!r}; available={sorted(BRIEFS)}")
    cfg = BRIEFS[name]
    brief = base.default_brief()
    brief.update(
        name=f"five-route-scheduler-stress-{name}",
        artistic_intent=cfg["intent"],
        routes=list(ROUTES),
        bbox_target=list(cfg["bbox"]),
        explore_per_basin=3,
        roundA_per_survivor=2,
        total_extra_budget=6,
    )
    return brief


def _fill_route_screen(out: Path) -> None:
    screen = Path(out) / "route-screen"
    sealed = json.loads((screen / "sealed-mapping.json").read_text())
    decisions = json.loads((screen / "decisions-template.json").read_text())
    for label in sealed["groups"]:
        decisions["decisions"][label].update(
            verdict="keep",
            confidence="strong",
            rationale=(
                "synthetic all-keep stress fixture; authoritative class is used only "
                "to exercise screened allocation control flow, not as artistic evidence"
            ),
        )
    (screen / "decisions-template.json").write_text(json.dumps(decisions, indent=2) + "\n")


def _prepare(out: Path, brief: dict, seed: int) -> dict:
    state = base.prepare_probe(
        brief=brief,
        seed=seed,
        out_dir=out,
        probe_budget=PROBE_BUDGET,
        minimum_per_route=2,
        include_orbit=True,
        routes=ROUTES,
        times=base.TIMES,
        render_frame=base.render_candidate_frame,
        generate_route_archive=base._generate_route_archive,
    )
    expected = {route: 2 for route in ROUTES}
    if state["probeAllocation"] != expected:
        raise AssertionError(f"unexpected probe allocation: {state['probeAllocation']} != {expected}")
    _fill_route_screen(out)
    return state


def _assert_triad_batches(batches: list[list[dict]]) -> None:
    for index, batch in enumerate(batches, 1):
        if len(batch) > 2:
            raise AssertionError(f"triad batch {index} exceeds K=2: {len(batch)}")
        groups = [task.get("group") for task in batch]
        if any(group is None for group in groups):
            raise AssertionError(f"triad batch {index} lost hidden scheduling group metadata")
        if len(groups) != len(set(groups)):
            raise AssertionError(f"triad batch {index} contains duplicate scheduling groups: {groups}")


def _run_policy(brief_name: str, seed: int, *, triads: bool, max_replays: int = 140) -> dict:
    brief = _brief(brief_name)
    with TemporaryDirectory() as td:
        root = Path(td)
        probe_state = _prepare(root, brief, seed)
        pairq = root / "candidate-review"
        triadq = root / "candidate-triad-review" if triads else None
        rounds = 0
        replays = 0
        batches: list[list[dict]] = []
        captured: dict = {}
        last_result: dict | None = None

        while replays < max_replays:
            replays += 1
            captured.clear()

            def capture_run(active_brief, run_seed, out, starts, selector=None):
                state, report = base.run_search_from_starts(active_brief, run_seed, out, starts, selector)
                captured["state"] = state
                captured["report"] = report
                return state, report

            result = base.resume_adaptive_search(
                out_dir=root,
                total_start_budget=TOTAL_START_BUDGET,
                source_class="independent-model",
                source_id=ROUTE_SCREEN_ID,
                evidence_authoritative_promotion=True,
                candidate_review_queue=pairq,
                candidate_max_pending_reviews=2,
                candidate_max_pending_reviews_per_group=1,
                candidate_pair_matrix_triads=triads,
                candidate_triad_review_queue=triadq,
                render_frame=base.render_candidate_frame,
                generate_route_archive=base._generate_route_archive,
                run_search_from_starts=capture_run,
            )
            last_result = result
            if tuple(result["activeRoutes"]) != ROUTES:
                raise AssertionError(f"active-route drift: {result['activeRoutes']} != {list(ROUTES)}")
            expected_added = {route: 1 for route in ROUTES}
            if result["additionalStartsByRoute"] != expected_added:
                raise AssertionError(
                    f"unexpected added-start allocation: {result['additionalStartsByRoute']} != {expected_added}"
                )

            pending_pairs = base._pending_pair_ids(pairq)
            pending_triads = base._pending_triad_ids(triadq) if triadq is not None else []
            if triads:
                queued = result["candidateQueuedReviewTasks"]
                if queued:
                    batches.append(queued)
            elif pending_pairs:
                batches.append([{"kind": "pair", "id": pid} for pid in pending_pairs])

            if not pending_pairs and not pending_triads:
                break
            base._resolve_pair_pending(pairq)
            if triadq is not None:
                base._resolve_triad_pending(triadq)
            rounds += 1
        else:
            raise AssertionError(
                f"five-route stress did not converge brief={brief_name} seed={seed} triads={triads}"
            )

        if last_result is None:
            raise AssertionError("stress run produced no screened-search result")
        if triads:
            _assert_triad_batches(batches)

        pairs, n_triads = base._task_counts(pairq, triadq)
        state = captured["state"]
        report = captured["report"]
        counts_by_route = {
            route: sum(candidate.route == route for candidate in state.candidates.values())
            for route in ROUTES
        }
        if any(counts_by_route[route] == 0 for route in ROUTES):
            raise AssertionError(f"representation starvation in candidate graph: {counts_by_route}")

        return {
            "policy": "screened-matrix-triad-k2" if triads else "screened-current-pair-k2",
            "reviewTasks": pairs + n_triads,
            "reviewRounds": rounds,
            "searchReplays": replays,
            "candidateExposures": pairs * 2 + n_triads * 3,
            "pairRelationsElicited": pairs + n_triads * 3,
            "pairTasks": pairs,
            "triadTasks": n_triads,
            "trajectorySignature": base._signature(state, report),
            "winner": report.get("winner"),
            "provisionalChampion": report.get("provisionalChampion"),
            "selectionStatus": report.get("selectionStatus"),
            "frontier": sorted(report.get("artisticFrontier", [])),
            "candidateCountsByRoute": counts_by_route,
            "probeAllocation": probe_state["probeAllocation"],
            "additionalStartsByRoute": last_result["additionalStartsByRoute"],
            "reviewBatches": batches,
        }


def run_scenario(brief_name: str, seed: int) -> dict:
    if seed not in SEEDS:
        raise ValueError(f"seed {seed} is not predeclared; allowed={SEEDS}")
    if brief_name not in BRIEFS:
        raise ValueError(f"brief {brief_name!r} is not predeclared")

    pair = _run_policy(brief_name, seed, triads=False)
    triad = _run_policy(brief_name, seed, triads=True)

    if pair["trajectorySignature"] != triad["trajectorySignature"]:
        raise AssertionError(f"trajectory divergence brief={brief_name} seed={seed}")
    for key in ("winner", "provisionalChampion", "selectionStatus", "frontier"):
        if pair[key] != triad[key]:
            raise AssertionError(f"final-state divergence {key} brief={brief_name} seed={seed}")
    for metric in ("reviewTasks", "reviewRounds", "searchReplays", "candidateExposures"):
        if triad[metric] > pair[metric]:
            raise AssertionError(
                f"triad scheduler regressed {metric} brief={brief_name} seed={seed}: "
                f"{triad[metric]} > {pair[metric]}"
            )
    if triad["triadTasks"] < 1:
        raise AssertionError(f"stress scenario queued no triads brief={brief_name} seed={seed}")

    return {
        "version": 1,
        "brief": brief_name,
        "seed": seed,
        "routes": list(ROUTES),
        "probeBudget": PROBE_BUDGET,
        "totalStartBudget": TOTAL_START_BUDGET,
        "currentPairK2": pair,
        "matrixTriadK2": triad,
        "gates": {
            "sameFullTrajectory": True,
            "sameFinalState": True,
            "noTaskRegression": triad["reviewTasks"] <= pair["reviewTasks"],
            "noRoundRegression": triad["reviewRounds"] <= pair["reviewRounds"],
            "noReplayRegression": triad["searchReplays"] <= pair["searchReplays"],
            "noExposureRegression": triad["candidateExposures"] <= pair["candidateExposures"],
            "allFiveRoutesActive": True,
            "normalTwoProbeDepth": pair["probeAllocation"] == {route: 2 for route in ROUTES},
            "oneAdditionalStartPerRoute": pair["additionalStartsByRoute"] == {route: 1 for route in ROUTES},
            "triadPathActuallyExercised": triad["triadTasks"] > 0,
            "strictTaskSaving": triad["reviewTasks"] < pair["reviewTasks"],
        },
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", choices=sorted(BRIEFS), required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    args = parser.parse_args()
    print(json.dumps(run_scenario(args.brief, args.seed), indent=2))


if __name__ == "__main__":
    main()
