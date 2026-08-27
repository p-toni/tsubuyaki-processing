#!/usr/bin/env python3
from __future__ import annotations

import copy
import random
import tempfile
from pathlib import Path

import run
from pairwise_selector import (
    DeterministicTemporalSelector,
    RecordedDecisionSelector,
    incumbent_challenge,
    clear_loss_frontier,
)


def make_valid(route: str, seed: int, cid: str):
    rng = random.Random(seed)
    for _ in range(100):
        g = run.ROUTES[route]['seed'](rng)
        c = run.Candidate(cid, route, cid, g, None, 'test')
        run.evaluate_candidate(c, run.default_brief())
        if c.checks['valid']:
            return c
    raise AssertionError(f'no valid {route} candidate')


def main():
    brief = run.default_brief()
    proxy = DeterministicTemporalSelector()

    a = make_valid('recurrence', 111, 'A')
    b = make_valid('recurrence', 222, 'B')

    # Pair reversal must preserve the semantic winner.
    ab = proxy.compare(a, b, brief)
    ba = proxy.compare(b, a, brief)
    if ab.verdict == 'a':
        assert ba.verdict == 'b', (ab, ba)
    elif ab.verdict == 'b':
        assert ba.verdict == 'a', (ab, ba)
    else:
        assert ba.verdict == 'tie', (ab, ba)

    # No recurrence selector dimension may use occupancy.
    assert not any('occupancy' in d.name for d in ab.dimensions), ab.to_json()

    # Exact clone must tie/defer.
    clone = copy.deepcopy(a)
    clone.id = 'A2'
    tie = proxy.compare(a, clone, brief)
    assert tie.verdict == 'tie' and tie.confidence == 'defer', tie.to_json()

    # Invalid candidate loses automatically without artistic arithmetic.
    bad = copy.deepcopy(a)
    bad.id = 'BAD'
    bad.checks = {'valid': False, 'failures': ['synthetic invalid'], 'diagnostics': {}}
    invalid = proxy.compare(a, bad, brief)
    assert invalid.verdict == 'a' and invalid.confidence == 'clear', invalid.to_json()

    # Recorded independent judgments can replace the proxy without changing policy.
    recorded = RecordedDecisionSelector({'A::B': 'B'}, fallback=proxy)
    rd = recorded.compare(a, b, brief)
    assert rd.verdict == 'b' and rd.source == recorded.name, rd.to_json()

    # Tie/defer preserves both members of the frontier.
    recorded_tie = RecordedDecisionSelector({'A::A2': 'tie'})
    champ, frontier, decisions = clear_loss_frontier(recorded_tie, [a, clone], brief)
    assert {x.id for x in frontier} == {'A','A2'}, [x.id for x in frontier]

    # Elite-preserving promotion: challenger replaces incumbent only on clear win.
    chosen, decision = incumbent_challenge(recorded_tie, a, clone, brief)
    assert chosen.id == 'A' and decision.verdict == 'tie'

    # Full search uses selector decisions, not diagnostic score, for promotion.
    with tempfile.TemporaryDirectory() as td:
        state, report = run.run_search(brief, 260826, Path(td), selector=proxy)
        assert report['selectorSummary']['diagnosticScoreUsedForPromotion'] is False
        assert report['selectorSummary']['decisionCount'] > 0
        assert report['selector'] == proxy.name
        assert report['selectionStatus'] in {'clear', 'tie-defer'}
        assert report['artisticFrontier']
        assert any('verdict' in d for d in state.stage_decisions)

    print('pairwise selector tests: PASS')


if __name__ == '__main__':
    main()
