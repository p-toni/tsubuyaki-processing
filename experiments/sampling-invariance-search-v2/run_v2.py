from __future__ import annotations

"""Thin semantic wrapper for the frozen v2 runner.

A basin-2 anchor that remains the final H2 winner is still a basin-2 win even when
none of its four descendants displaces it. This wrapper corrects that diagnostic
classification without changing generation, allocation, scoring, or any gate input.
"""

import run_search_v2 as core

_original_target_run = core._target_run


def _target_run(*args, **kwargs):
    result = _original_target_run(*args, **kwargs)
    h2 = result["policies"]["hybrid-top2"]
    h2["winnerFromSecondBasin"] = bool(
        h2["winnerFromSecondBasin"] or h2["winner"] == result["anchor2"]["id"]
    )
    return result


core._target_run = _target_run


if __name__ == "__main__":
    core.main()
