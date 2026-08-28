#!/usr/bin/env python3
from __future__ import annotations

import itertools
from reproduce import base


def test_all_27_complete_pair_matrices_are_representable_explicitly():
    keys=(('A','B'),('A','C'),('B','C'))
    choices=(('A','B','tie'),('A','C','tie'),('B','C','tie'))
    matrices=[]
    for vals in itertools.product(*choices):
        matrix=dict(zip(keys,vals))
        assert set(matrix)==set(keys)
        matrices.append(matrix)
    assert len(matrices)==27


def test_rank_transport_covers_only_13_of_27_pair_matrices():
    keys=(('A','B'),('A','C'),('B','C'))
    choices=(('A','B','tie'),('A','C','tie'),('B','C','tie'))
    rankable=0
    for vals in itertools.product(*choices):
        if base.order_for_outcomes(dict(zip(keys,vals))) is not None:
            rankable+=1
    assert rankable==13
    assert 27-rankable==14


def test_cycle_is_valid_explicit_pair_evidence_but_not_a_rank():
    cycle={('A','B'):'A',('A','C'):'C',('B','C'):'B'}
    assert base.order_for_outcomes(cycle) is None
    for pair,winner in cycle.items():
        assert winner in pair


def main():
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')

if __name__=='__main__':
    main()
