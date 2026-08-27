#!/usr/bin/env python3
from __future__ import annotations

import json, random, tempfile
from pathlib import Path

import run
from checkers import check_candidate


def checked(route, genome):
    return check_candidate(route, genome, run.TIMES, run.ROUTES[route]['geometry'], run.W, run.H)


def find_valid(route, seed):
    rng = random.Random(seed)
    for _ in range(100):
        g = run.ROUTES[route]['seed'](rng)
        c = checked(route, g)
        if c['valid']:
            return g, c
    raise AssertionError(f'could not find valid seed for {route}')


def main():
    # Probe-renderer parity: the checker view and renderer are the same geometry source.
    rg, rc = find_valid('recurrence', 101)
    fg, fc = find_valid('family', 202)
    for t in run.TIMES:
        assert run.recurrence_points(rg, t) == run.recurrence_geometry(rg, t)['all']
        assert run.family_points(fg, t) == run.family_geometry(fg, t)['all']

    # Healthy candidates pass.
    assert rc['valid'], rc
    assert fc['valid'], fc

    # A sparse / subtle filament is not rejected merely because its side structure is faint.
    sparse = dict(rg)
    sparse['side'] = 0.5
    sparse_check = checked('recurrence', sparse)
    assert sparse_check['valid'], sparse_check
    assert sparse_check['diagnostics']['occupancyUsedAsGate'] is False
    assert any('subtle' in w for w in sparse_check['warnings'])

    # Exploding projection must fail framing / spine survival.
    bad_rec = dict(rg)
    bad_rec['sx'] = 1200
    bad_rec['sy'] = 900
    bad_rec_check = checked('recurrence', bad_rec)
    assert not bad_rec_check['valid'], bad_rec_check

    # Broken family semantics: fewer than 3 siblings is invalid.
    bad_family = dict(fg)
    bad_family['organs'] = 2
    bad_family_check = checked('family', bad_family)
    assert not bad_family_check['valid'], bad_family_check
    assert any('fewer than three' in f for f in bad_family_check['failures'])

    # Broken family framing: giant organ length sends tips off-canvas.
    offscreen = dict(fg)
    offscreen['organ_len'] = 950
    offscreen_check = checked('family', offscreen)
    assert not offscreen_check['valid'], offscreen_check

    # End-to-end smoke: finalists must all satisfy route checkers.
    with tempfile.TemporaryDirectory() as td:
        brief = run.default_brief()
        state, report = run.run_search(brief, 260826, Path(td))
        assert report['winnerChecks']['valid']
        assert all(f['valid'] for f in report['finalists'])
        assert report['checkerSummary']['occupancyPolicy'].startswith('diagnostic-only')

    print('route-specific checker tests: PASS')

if __name__ == '__main__':
    main()
