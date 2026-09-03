from __future__ import annotations

import importlib.util
import random
import sys
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
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _valid_genome(route: str, seed: int):
    rng = random.Random(seed)
    for _ in range(128):
        genome = core.ROUTES[route]['seed'](rng)
        checks = check_candidate(route, genome, core.TIMES, core.ROUTES[route]['geometry'], core.W, core.H)
        if checks['valid']:
            return genome
    raise AssertionError(f'fixture failed to find valid {route} genome')


def _valid_recurrence(seed: int = 731):
    return _valid_genome('recurrence', seed)


def _valid_family(seed: int = 733):
    return _valid_genome('family', seed)


def _valid_sheet(seed: int = 739):
    return _valid_genome('sheet', seed)


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
    assert record['type'] == material_control.CONTROL_TYPE
    assert record['coefficients'] == pytest.approx(field.coefficients.tolist(), abs=1e-15)
    assert record['velocityRms'] == pytest.approx(frozen_control.velocity_rms(field), abs=1e-12)
    frozen_rms = frozen_control.velocity_rms(field)
    for t in core.TIMES:
        native = core.ROUTES['recurrence']['geometry'](genome, t)
        expected = frozen_control.warp_geometry(field, native, 16.0, core.W, core.H, rms=frozen_rms)
        actual = material_control.candidate_geometry(core.ROUTES['recurrence'], controlled, t, core.W, core.H)
        assert frozen_control.max_point_delta(expected, actual) < 1e-9


def test_runtime_family_projected_control_matches_frozen_projection_operator():
    frozen_field = _load('runtime_family_equiv_field', ROOT / 'experiments' / 'sampling-invariance-v1' / 'field.py')
    frozen_control = _load('runtime_family_equiv_control', ROOT / 'experiments' / 'spectral-material-control-v1' / 'spectral_control.py')
    frozen_projection = _load('runtime_family_equiv_projection', ROOT / 'experiments' / 'family-spectral-projection-v1' / 'family_projection.py')
    genome = _valid_family(913)
    field_seed = 987654323
    controlled = material_control.with_family_projected_spectral_control(genome, field_seed)
    record = controlled[material_control.CONTROL_KEY]
    field = frozen_field.random_field(2, field_seed)
    assert record['type'] == material_control.FAMILY_PROJECTED_CONTROL_TYPE
    assert record['coefficients'] == pytest.approx(field.coefficients.tolist(), abs=1e-15)
    assert record['velocityRms'] == pytest.approx(frozen_control.velocity_rms(field), abs=1e-12)
    frozen_rms = frozen_control.velocity_rms(field)
    for t in core.TIMES:
        native = core.ROUTES['family']['geometry'](genome, t)
        expected = frozen_projection.warp_family_projected(
            field, native, 16.0, core.W, core.H, rms=frozen_rms
        )
        actual = material_control.candidate_geometry(
            core.ROUTES['family'], controlled, t, core.W, core.H
        )
        assert frozen_control.max_point_delta(expected, actual) < 1e-9
        assert frozen_projection.terminal_length_error(native, actual) < 1e-9


def test_portfolio_schedules_keep_authority_surfaces_separate():
    mixed_1d = {'mutation_portfolio': search_engine.MIXED_1D_V1, 'routes': ['recurrence', 'family']}
    assert [search_engine._operator_for(mixed_1d, 'recurrence', i, 6) for i in range(6)] == ['native'] * 3 + ['spectral'] * 3
    assert [search_engine._operator_for(mixed_1d, 'recurrence', i, 3) for i in range(3)] == ['native', 'native', 'spectral']
    assert [search_engine._operator_for(mixed_1d, 'family', i, 6) for i in range(6)] == ['native'] * 6
    assert search_engine._eligible_routes_for_portfolio(mixed_1d) == ['recurrence']

    family = {'mutation_portfolio': search_engine.FAMILY_PROJECTED_V1, 'routes': ['recurrence', 'family', 'sheet']}
    assert [search_engine._operator_for(family, 'family', i, 6) for i in range(6)] == ['native'] * 3 + ['projected-spectral'] * 3
    assert [search_engine._operator_for(family, 'family', i, 3) for i in range(3)] == ['native', 'native', 'projected-spectral']
    assert [search_engine._operator_for(family, 'recurrence', i, 6) for i in range(6)] == ['native'] * 6
    assert [search_engine._operator_for(family, 'sheet', i, 6) for i in range(6)] == ['native'] * 6
    assert search_engine._eligible_routes_for_portfolio(family) == ['family']
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

    family = material_control.with_family_projected_spectral_control(_valid_family(1561), 9983)
    family_record = family[material_control.CONTROL_KEY]
    family_child = material_control.mutate_native(core.ROUTES['family'], family, random.Random(14), 0.55)
    assert family_child[material_control.CONTROL_KEY] == family_record
    assert material_control.CONTROL_KEY not in material_control._native_genome(family_child)


def test_family_projected_control_fails_closed_on_sheet_topology():
    sheet = material_control.with_family_projected_spectral_control(_valid_sheet(1601), 9985)
    with pytest.raises(ValueError, match='family anchor/organ topology'):
        material_control.candidate_geometry(core.ROUTES['sheet'], sheet, 90, core.W, core.H)


def test_family_runtime_spawn_serializes_projected_control_and_operator():
    genome = _valid_family(1621)
    parent = core.Candidate('F0', 'family', 'F0', genome, None, 'start')
    brief = {
        'name': 'family-runtime-test',
        'artistic_intent': 'test only',
        'routes': ['family'],
        'bbox_target': [.55, .82],
        'mutation_portfolio': search_engine.FAMILY_PROJECTED_V1,
    }
    child = search_engine._spawn(
        brief, 88123, parent, 'F0-E4', 'explore', 3, 4, random.Random(3), 1.0
    )
    assert child.checks['generationOperator'] == 'projected-spectral'
    record = child.genome[material_control.CONTROL_KEY]
    assert record['type'] == material_control.FAMILY_PROJECTED_CONTROL_TYPE
    assert record['bandwidth'] == 2
    assert record['amplitude'] == 16.0
