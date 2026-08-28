import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image, ImageDraw

from candidate_review_scheduler import ReviewProposal, flush_review_proposals, pending_pair_ids, pending_triad_ids
from review_evidence_queue import pair_id_for_phenotypes, phenotype_fingerprint

TIMES=(0,1)
BRIEF='x'


def frames(value):
    out=[]
    for t in TIMES:
        im=Image.new('L',(40,40),0); d=ImageDraw.Draw(im)
        d.rectangle((4+value,6+t,18+value,20+t),outline=150+value,width=2)
        out.append(im)
    return tuple(out)


def proposal(index,a_id,b_id,a_value,b_value,*,stage='explore',parent=None,route='recurrence',b_route=None,review_group='route:recurrence'):
    afr=frames(a_value); bfr=frames(b_value)
    afp=phenotype_fingerprint(afr); bfp=phenotype_fingerprint(bfr)
    pid=pair_id_for_phenotypes(brief=BRIEF,times=TIMES,a_fingerprint=afp,b_fingerprint=bfp)
    return ReviewProposal(
        index=index,pair_id=pid,brief_text=BRIEF,a_id=a_id,b_id=b_id,afp=afp,bfp=bfp,
        a_frames=afr,b_frames=bfr,a_route=route,b_route=b_route or route,
        a_stage='start',b_stage=stage,a_parent=None,b_parent=a_id if parent is None else parent,
        review_group=review_group,
    )


@dataclass(frozen=True)
class Ev:
    pair_id:str
    authoritative:bool=True


def test_fixed_siblings_pack_to_one_explicit_triad():
    p=proposal(0,'a','b',1,7)
    q=proposal(1,'a','c',1,13)
    with TemporaryDirectory() as td:
        root=Path(td); pairq=root/'pairs'; triadq=root/'triads'
        tasks=flush_review_proposals(
            [p,q],evidence=[],pair_queue_dir=pairq,triad_queue_dir=triadq,times=TIMES,
            enable_triads=True,max_tasks=2,max_tasks_per_group=1,
        )
        assert len(tasks)==1 and tasks[0]['kind']=='triad'
        assert len(tasks[0]['pairIds'])==3
        assert not (pairq/'decisions.json').exists()
        triads=json.loads((triadq/'decisions.json').read_text())['decisions']
        assert len(triads)==1 and pending_triad_ids(triadq)==set(triads)


def test_refine_and_wrong_parent_never_pack():
    cases=[
        (proposal(0,'a','b',1,7,stage='refine'),proposal(1,'a','c',1,13,stage='refine')),
        (proposal(0,'a','b',1,7,parent='other'),proposal(1,'a','c',1,13,parent='other')),
        (proposal(0,'a','b',1,7),proposal(1,'a','c',1,13,b_route='family',review_group='cross:family|recurrence')),
    ]
    for p,q in cases:
        with TemporaryDirectory() as td:
            root=Path(td); pairq=root/'pairs'; triadq=root/'triads'
            tasks=flush_review_proposals(
                [p,q],evidence=[],pair_queue_dir=pairq,triad_queue_dir=triadq,times=TIMES,
                enable_triads=True,max_tasks=2,max_tasks_per_group=None,
            )
            assert tasks and all(task['kind']=='pair' for task in tasks)
            assert not (triadq/'decisions.json').exists()


def test_authoritative_challenger_relation_blocks_triad():
    p=proposal(0,'a','b',1,7)
    q=proposal(1,'a','c',1,13)
    bc=pair_id_for_phenotypes(brief=BRIEF,times=TIMES,a_fingerprint=p.bfp,b_fingerprint=q.bfp)
    with TemporaryDirectory() as td:
        root=Path(td); pairq=root/'pairs'; triadq=root/'triads'
        tasks=flush_review_proposals(
            [p,q],evidence=[Ev(bc)],pair_queue_dir=pairq,triad_queue_dir=triadq,times=TIMES,
            enable_triads=True,max_tasks=2,max_tasks_per_group=1,
        )
        assert tasks and tasks[0]['kind']=='pair'
        assert not (triadq/'decisions.json').exists()


def test_pending_work_blocks_next_batch():
    p=proposal(0,'a','b',1,7)
    q=proposal(1,'a','c',1,13)
    with TemporaryDirectory() as td:
        root=Path(td); pairq=root/'pairs'; triadq=root/'triads'
        first=flush_review_proposals(
            [p],evidence=[],pair_queue_dir=pairq,triad_queue_dir=triadq,times=TIMES,
            enable_triads=False,max_tasks=1,max_tasks_per_group=1,
        )
        assert len(first)==1 and pending_pair_ids(pairq)
        blocked=flush_review_proposals(
            [q],evidence=[],pair_queue_dir=pairq,triad_queue_dir=triadq,times=TIMES,
            enable_triads=True,max_tasks=2,max_tasks_per_group=1,
        )
        assert blocked==[]


def test_none_review_group_preserves_single_route_k2_behavior():
    p=proposal(0,'a','b',1,7,review_group=None)
    q=proposal(1,'a','c',1,13,stage='refine',review_group=None)
    with TemporaryDirectory() as td:
        root=Path(td); pairq=root/'pairs'
        tasks=flush_review_proposals(
            [p,q],evidence=[],pair_queue_dir=pairq,triad_queue_dir=None,times=TIMES,
            enable_triads=False,max_tasks=2,max_tasks_per_group=1,
        )
        assert len(tasks)==2 and all(task['kind']=='pair' for task in tasks)


if __name__=='__main__':
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')
