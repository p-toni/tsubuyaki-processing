from pathlib import Path
from tempfile import TemporaryDirectory

from screened_search import _load_default_dependencies


def test_default_screened_runtime_registers_five_routes():
    routes, times, render, generate, run_from_starts = _load_default_dependencies(include_orbit=True)
    assert set(routes) == {"recurrence", "orbit", "family", "sheet", "filament"}
    assert len(times) >= 2
    assert callable(render) and callable(generate) and callable(run_from_starts)


def test_actual_reviewed_starts_enter_adaptive_search():
    routes, times, render, generate, run_from_starts = _load_default_dependencies(include_orbit=True)
    brief = {
        "name": "reviewed-start-smoke",
        "artistic_intent": "Preserve exact reviewed start phenotypes while entering adaptive search.",
        "routes": ["recurrence"],
        "bbox_target": [.55, .82],
        "explore_per_basin": 0,
        "roundA_per_survivor": 1,
        "total_extra_budget": 0,
    }
    starts, _ = generate(brief, 380021, "recurrence", 2)
    expected = {c.id for c in starts}
    with TemporaryDirectory() as td:
        state, report = run_from_starts(brief, 380021, Path(td), starts)
        assert expected.issubset(state.candidates)
        assert report["checkerSummary"]["invalidByRoute"]["recurrence"] == 0


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn(); print(name, "PASS")
