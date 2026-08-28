#!/usr/bin/env python3
from __future__ import annotations
import itertools
from reproduce import order_for_outcomes,outcomes_for_order,weak_orders


def test_exactly_thirteen_weak_orders():
    orders=weak_orders()
    assert len(orders)==13
    assert len(set(orders))==13


def test_every_weak_order_round_trips():
    for order in weak_orders():
        outcomes=outcomes_for_order(order)
        assert order_for_outcomes(outcomes)==order


def test_all_rankable_pair_matrices_decode_uniquely():
    keys=(('A','B'),('A','C'),('B','C'))
    choices=tuple(tuple(pair)+('tie',) for pair in keys)
    decoded={}
    for vals in itertools.product(*choices):
        outcomes=dict(zip(keys,vals))
        order=order_for_outcomes(outcomes)
        if order is not None:
            decoded[tuple(vals)]=order
    # Exactly the 13 total preorders are rankable. The remaining 14 complete
    # pairwise matrices contain an intransitivity that must fall back to pairs.
    assert len(decoded)==13
    assert 27-len(decoded)==14


def test_cycles_are_rejected_not_transitivized():
    cycle={('A','B'):'A',('A','C'):'C',('B','C'):'B'}  # A>B>C>A
    assert order_for_outcomes(cycle) is None
    reverse={('A','B'):'B',('A','C'):'A',('B','C'):'C'}  # B>A>C>B
    assert order_for_outcomes(reverse) is None


def main():
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')

if __name__=='__main__': main()
