import importlib.util
from pathlib import Path


def _load_experiment():
    path=Path(__file__).resolve().parents[2]/"experiments"/"dynamic-lazy-review-v1"/"reproduce.py"
    spec=importlib.util.spec_from_file_location("dynamic_lazy_review_v1",path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def test_pending_caps_converge_on_same_dynamic_search_trajectory():
    result=_load_experiment().run_experiment(quick=True)
    assert result["blockCount"]==1
    assert result["trajectoryAgreement"].startswith("all caps exactly match")
    summary=result["summary"]
    assert summary["2"]["meanRatings"]<=summary["eager"]["meanRatings"]
    assert summary["2"]["meanReviewRounds"]<=summary["1"]["meanReviewRounds"]
