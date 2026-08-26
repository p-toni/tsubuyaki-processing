#!/usr/bin/env python3
"""Reproduce the uncertainty-aware racing candidate genotypes.

Dependency:
    experiments/hybrid-portfolio-search/reproduce.py

That merged experiment defines the exact start genotypes and route-local mutation
generators. This script deliberately reuses them so the racing experiment changes
allocation policy rather than proposal mechanics.

Run from repository root:
    python experiments/racing-portfolio-search/reproduce.py

Outputs:
    experiments/racing-portfolio-search/_generated/racing-candidates.json
"""
import importlib.util
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HYBRID = ROOT / "experiments" / "hybrid-portfolio-search" / "reproduce.py"
OUT = Path(__file__).resolve().parent / "_generated"
OUT.mkdir(exist_ok=True)

spec = importlib.util.spec_from_file_location("hybrid_reproduce", HYBRID)
hybrid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hybrid)

rec_rng = random.Random(26082671)
rec_explore = {}
for s in range(1, 5):
    base = hybrid.REC_STARTS[f"Rstart{s}"]
    arr = []
    for j in range(5):
        g, roles = hybrid.mutate_rec(base, rec_rng)
        arr.append({"id": f"RE-S{s}-{j+1}", "g": g, "roles": roles})
    rec_explore[s] = arr

fam_rng = random.Random(26082681)
fam_explore = {}
for s in range(1, 5):
    base = hybrid.FAM_STARTS[f"Fstart{s}"]
    arr = []
    for j in range(5):
        g, roles = hybrid.mutate_fam(base, fam_rng)
        arr.append({"id": f"FE-S{s}-{j+1}", "g": g, "roles": roles})
    fam_explore[s] = arr

rec_A = {}
rec_parents = {
    1: rec_explore[1][4]["g"],
    3: rec_explore[3][2]["g"],
}
for basin, base in rec_parents.items():
    rng = random.Random(26082800 + basin)
    arr = []
    for i in range(4):
        g, roles = hybrid.mutate_rec(base, rng)
        arr.append({"id": f"RR-A-B{basin}-{i+1}", "g": g, "roles": roles})
    rec_A[basin] = arr

rec_B_parent = rec_A[1][3]["g"]
rng = random.Random(26082820)
rec_B = []
for i in range(12):
    g, roles = hybrid.mutate_rec(rec_B_parent, rng)
    rec_B.append({"id": f"RR-B-B1-{i+1}", "g": g, "roles": roles})

fam_A = {}
fam_parents = {
    4: fam_explore[4][0]["g"],
    1: fam_explore[1][2]["g"],
    3: fam_explore[3][2]["g"],
}
for basin, base in fam_parents.items():
    rng = random.Random(26082900 + basin)
    arr = []
    for i in range(4):
        g, roles = hybrid.mutate_fam(base, rng)
        arr.append({"id": f"FR-A-B{basin}-{i+1}", "g": g, "roles": roles})
    fam_A[basin] = arr

fam_B = {}
rng = random.Random(26082920)
arr = []
for i in range(4):
    g, roles = hybrid.mutate_fam(fam_A[4][3]["g"], rng)
    arr.append({"id": f"FR-B-B4-{i+1}", "g": g, "roles": roles})
fam_B[4] = arr

rng = random.Random(26082921)
arr = []
for i in range(4):
    g, roles = hybrid.mutate_fam(fam_A[1][2]["g"], rng)
    arr.append({"id": f"FR-B-B1-{i+1}", "g": g, "roles": roles})
fam_B[1] = arr

result = {
    "seeds": {
        "sharedRecurrenceExploration": 26082671,
        "sharedFamilyExploration": 26082681,
        "recurrenceRoundA": {"1": 26082801, "3": 26082803},
        "recurrenceRoundB": 26082820,
        "familyRoundA": {"4": 26082904, "1": 26082901, "3": 26082903},
        "familyRoundB": {"4": 26082920, "1": 26082921},
    },
    "recordedDecisions": {
        "recurrence": {
            "afterExploration": {"survive": [1, 3], "discard": [2, 4]},
            "afterRoundA": {"survive": [1], "discard": [3]},
            "roundBParent": "RR-A-B1-4",
            "winner": "RR-B-B1-12",
        },
        "family": {
            "afterExploration": {"survive": [4, 1, 3], "discard": [2]},
            "afterRoundA": {"survive": [4, 1], "discard": [3], "decision": "tie/defer between 4 and 1"},
            "roundBParents": {"4": "FR-A-B4-4", "1": "FR-A-B1-3"},
            "winner": "FR-B-B4-3",
        },
    },
    "sharedExploration": {"recurrence": rec_explore, "family": fam_explore},
    "racing": {
        "recurrence": {"roundA": rec_A, "roundB": rec_B},
        "family": {"roundA": fam_A, "roundB": fam_B},
    },
}

path = OUT / "racing-candidates.json"
path.write_text(json.dumps(result, indent=2) + "\n")
print(path)
