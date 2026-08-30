from __future__ import annotations

import importlib.util
import random
from pathlib import Path

import pytest

import core
import material_control
import search_engine
from checkers import check_candidate

ROOT = Path(__file__).resolve().parents[2]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _valid_recurrence(seed: int = 731):
    rng = random.Random(seed)
    for _ in range(128):
        genome = core.ROUTES['recurrence']['seed'](rng)
        checks = check_candidate('recurrence', genome, core.TIMES, core.ROUTES['recurrence']['geometry'], core.W, core.H)
        if checks['valid']:
            return genome
    raise AssertionError('fixture failed to find valid recurrence genome')


def test_native_render_and_geometry_remain_exact():
    genome = _valid_recurrence()
    cand = core.Candidate('x', 'recurrence', 'x', genome, None, 'start')
    for t in core.TIMES:
        expected_points = core.ROUTES['recurrence']['render'](genome, t)
        got = core.render_candidate_frame(cand, t)
        expected = core.draw_points(expected_points, genome['alpha'])
        assert got.tobytes() == expected.tobytes()
        assert material_control.candidate_geometry(core.ROUTES['recurrence'], genome, t, core.W, core.H) == core.ROUTES['recurrence']['geometry'](genome, t)


def test_runtime_spectral_control_matches_frozen_research_operator():
    frozen_field = _load('runtime_equiv_field', ROOT / 'experiments' / 'sampling-invariance-v1' / 'field.py')
    frozen_control = _load('runtime_equiv_control', ROOT / 'experiments' / 'spectral-material-control-v1' / 'spectral_control.py')
    genome = _valid_recurrence(911)
    field_seed = 987654321
    controlled = material_control.with_spectral_control(genome, field_seed)
    record = controlled[material_control.CONTROL_KEY]
    field = frozen_field.random_field(2, field_seed)
    assert record['coefficients'] == pytest.approx(field.coefficients.tolist(), abs=1e-15)
    assert record['velocityRms'] == pytest.approx(frozen_control.velocity_rms(field), abs=1e-12)
    for t in core.TIMES:
        native = core.ROUTES['recurrence']['geometry'](genome, t)
        expected = frozen_control.warp_geometry(field, native, 16.0, core.W, core.H, rms=frozen_control.velocity_rms(field))
        actual = material_control.candidate_geometry(core.ROUTES['recurrence'], controlled, t, core.W, core.H)
        assert frozen_control.max_point_delta(expected, actual) < 1e-9


def test_portfolio_schedule_is_native_prefix_and_intrinsic_1d_only():
    mixed = {'mutation_portfolio': search_engine.MIXED_1D_V1}
    assert [search_engine._operator_for(mixed, 'recurrence', i, 6) for i in range(6)] == ['native'] * 3 + ['spectral'] * 3
    assert [search_engine._operator_for(mixed, 'recurrence', i, 3) for i in range(3)] == ['native', 'native', 'spectral']
    assert [search_engine._operator_for(mixed, 'family', i, 6) for i in range(6)] == ['native'] * 6
    assert [search_engine._operator_for({}, 'recurrence', i, 6) for i in range(6)] == ['native'] * 6


def test_native_only_spawn_matches_legacy_mutator_and_rng_consumption():
    genome = _valid_recurrence(1237)
    parent = core.Candidate('p', 'recurrence', 'p', genome, None, 'start')
    rng_expected = random.Random(441)
    rng_actual = random.Random(441)
    expected = core.ROUTES['recurrence']['mutate'](genome, rng_expected, 0.7)
    child = search_engine._spawn({}, 77, parent, 'c', 'roundA', 0, 3, rng_actual, 0.7)
    assert child.genome == expected
    assert child.checks['generationOperator'] == 'native'
    assert rng_actual.random() == rng_expected.random()


def test_native_mutation_preserves_selected_material_field():
    genome = material_control.with_spectral_control(_valid_recurrence(1559), 9981)
    record = genome[material_control.CONTROL_KEY]
    child = material_control.mutate_native(core.ROUTES['recurrence'], genome, random.Random(12), 0.55)
    assert child[material_control.CONTROL_KEY] == record
    assert material_control.CONTROL_KEY not in material_control._native_genome(child)
