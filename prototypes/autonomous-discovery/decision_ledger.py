from __future__ import annotations
from pathlib import Path
from judge_queue import decode_blind_decisions


def decode_blind_decision_dirs(queue_dirs):
    """Merge completed v2 review queues into one phenotype-safe replay ledger.

    Repeated identical records are harmless. Conflicting judgments for the same
    brief+horizon+phenotype pair fail closed instead of being resolved implicitly.
    """
    merged = {}
    for queue_dir in queue_dirs:
        for pair_id, result in decode_blind_decisions(Path(queue_dir)).items():
            if pair_id in merged and merged[pair_id] != result:
                raise ValueError(f"conflicting recorded judgments for phenotype pair {pair_id}")
            merged[pair_id] = result
    return merged
