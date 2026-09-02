from __future__ import annotations

import restart_sidecar as sidecar


def test_restart_sidecar_default_budget_matches_mechanical_evidence():
    # PR #126 established that only k=8 met the frozen >=90% coverage rule.
    assert sidecar.DEFAULT_ATTEMPTS_PER_ROUTE == 8
