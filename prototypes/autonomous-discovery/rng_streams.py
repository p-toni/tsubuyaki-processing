from __future__ import annotations
import hashlib
import random


def derived_seed(master_seed: int, *labels: object) -> int:
    payload = "::".join([str(master_seed), *map(str, labels)]).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def representation_rng(master_seed: int, representation_id: str, representation_version: str = "1", stream: str = "search") -> random.Random:
    return random.Random(derived_seed(master_seed, "representation", representation_id, representation_version, stream))
