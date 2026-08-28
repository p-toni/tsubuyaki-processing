#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from reproduce import FileBackedProposalSelector,Proposal,TIMES
from review_evidence_queue import pair_id_for_phenotypes

BRIEF='scheduler-safety-test'
ROUTE='recurrence'


def _proposal(index,*,a_id='A',b_id=None,afp='fp-A',bfp=None,route=ROUTE,b_route=None,stage='explore',parent='A'):
    b_id=b_id or f'B{index}'
    bfp=bfp or f'fp-B{index}'
    b_route=b_route or route
    pid=pair_id_for_phenotypes(brief=BRIEF,times=TIMES,a_fingerprint=afp,b_fingerprint=bfp)
    return Proposal(
        index,pid,BRIEF,a_id,b_id,afp,bfp,(),(),route,b_route,
        'start',stage,None,parent,
    )


def _selector(td):
    root=Path(td)
    return FileBackedProposalSelector(pair_queue=root/'pairs',triad_queue=root/'triads')


def test_same_stage_fixed_explore_and_rounda_siblings_pack():
    for stage in ('explore','roundA'):
        with TemporaryDirectory() as td:
            selector=_selector(td)
            p=_proposal(0,stage=stage,b_id='B',bfp='fp-B')
            q=_proposal(1,stage=stage,b_id='C',bfp='fp-C')
            triad=selector._triad_for(p,[p,q],set())
            assert triad is not None
            assert triad[0] is p and triad[1] is q


def test_refine_never_packs():
    with TemporaryDirectory() as td:
        selector=_selector(td)
        p=_proposal(0,stage='refine',b_id='B',bfp='fp-B')
        q=_proposal(1,stage='refine',b_id='C',bfp='fp-C')
        assert selector._triad_for(p,[p,q],set()) is None


def test_cross_route_wrong_parent_or_different_stage_never_pack():
    unsafe=(
        _proposal(1,b_id='C',bfp='fp-C',b_route='family'),
        _proposal(1,b_id='C',bfp='fp-C',parent='other-parent'),
        _proposal(1,b_id='C',bfp='fp-C',stage='roundA'),
    )
    with TemporaryDirectory() as td:
        selector=_selector(td)
        p=_proposal(0,b_id='B',bfp='fp-B')
        for q in unsafe:
            assert selector._triad_for(p,[p,q],set()) is None


def test_existing_authoritative_relation_blocks_triad_upgrade():
    with TemporaryDirectory() as td:
        selector=_selector(td)
        p=_proposal(0,b_id='B',bfp='fp-B')
        q=_proposal(1,b_id='C',bfp='fp-C')
        bc=pair_id_for_phenotypes(brief=BRIEF,times=TIMES,a_fingerprint=p.bfp,b_fingerprint=q.bfp)
        for resolved in ({p.pair_id},{q.pair_id},{bc}):
            assert selector._triad_for(p,[p,q],resolved) is None


def test_distinct_sibling_identity_and_phenotype_are_required():
    with TemporaryDirectory() as td:
        selector=_selector(td)
        p=_proposal(0,b_id='B',bfp='fp-B')
        same_id=_proposal(1,b_id='B',bfp='fp-C')
        same_fp=_proposal(1,b_id='C',bfp='fp-B')
        assert selector._triad_for(p,[p,same_id],set()) is None
        assert selector._triad_for(p,[p,same_fp],set()) is None


def main():
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')

if __name__=='__main__': main()
