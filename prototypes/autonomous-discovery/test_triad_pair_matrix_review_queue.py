import itertools
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from phenotype_preference_evidence import resolve_phenotype_promotion_evidence
from review_evidence_queue import create_review_bundle
from triad_pair_matrix_review_queue import (
    PAIR_KEYS,
    _validate_pair_verdicts,
    create_triad_pair_matrix_bundle,
    decode_triad_pair_matrix_evidence,
)

TIMES=(0,1,2)
BRIEF='pair-matrix transport test'
FRAMES_A=[Image.new('RGB',(64,64),(40+i,10,10)) for i in range(3)]
FRAMES_B=[Image.new('RGB',(64,64),(10,40+i,10)) for i in range(3)]
FRAMES_C=[Image.new('RGB',(64,64),(10,10,40+i)) for i in range(3)]


def _create(root,order=('A','B','C'),review_group='route:secret-family'):
    items={'A':('cand-A',FRAMES_A),'B':('cand-B',FRAMES_B),'C':('cand-C',FRAMES_C)}
    vals=[items[label] for label in order]
    return create_triad_pair_matrix_bundle(
        root,brief=BRIEF,times=TIMES,
        a_candidate_id=vals[0][0],a_frames=vals[0][1],
        b_candidate_id=vals[1][0],b_frames=vals[1][1],
        c_candidate_id=vals[2][0],c_frames=vals[2][1],
        review_group=review_group,
    )


def _docs(root):
    return (
        json.loads((root/'sealed-mapping.json').read_text()),
        json.loads((root/'queue.json').read_text()),
        json.loads((root/'decisions.json').read_text()),
    )


def _label_by_candidate(root,task_id):
    sealed,_,_=_docs(root)
    return {item['candidateId']:label for label,item in sealed['triads'][task_id].items()}


def _fp_by_candidate(root,task_id):
    sealed,_,_=_docs(root)
    return {item['candidateId']:item['phenotypeFingerprint'] for item in sealed['triads'][task_id].values()}


def _pair_key(a,b):
    return ':'.join(sorted((a,b)))


def _complete_by_candidate(root,task_id,outcomes,*,source_class='human',confidence='strong'):
    label_by_candidate=_label_by_candidate(root,task_id)
    _,_,decisions=_docs(root)
    verdicts={}
    for (left_id,right_id),winner_id in outcomes.items():
        left=label_by_candidate[left_id]; right=label_by_candidate[right_id]
        key=_pair_key(left,right)
        if winner_id=='tie': verdict='tie'
        else: verdict=label_by_candidate[winner_id]
        verdicts[key]=verdict
    assert set(verdicts)==set(PAIR_KEYS)
    decisions['decisions'][task_id].update({
        'pairVerdicts':verdicts,
        'sourceClass':source_class,
        'sourceId':'reviewer-1',
        'confidence':confidence,
        'rationale':'three explicit pair judgments',
    })
    (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')


def _evidence_for(evidence,left_fp,right_fp):
    pair=tuple(sorted((left_fp,right_fp)))
    matches=[ev for ev in evidence if ev.phenotype_fingerprints==pair]
    assert len(matches)==1
    return matches[0]


def _assert_decode_fails(root,contains=None):
    try:
        decode_triad_pair_matrix_evidence(root)
    except ValueError as e:
        if contains is not None: assert contains in str(e)
    else:
        raise AssertionError('expected pair-matrix replay to fail closed')


def test_all_27_pair_matrices_validate_without_transitivity_filter():
    choices={'A:B':('A','B','tie'),'A:C':('A','C','tie'),'B:C':('B','C','tie')}
    seen=0
    for vals in itertools.product(*(choices[key] for key in PAIR_KEYS)):
        verdicts=dict(zip(PAIR_KEYS,vals))
        assert _validate_pair_verdicts(verdicts)==verdicts
        seen+=1
    assert seen==27


def test_cycle_decodes_as_three_explicit_pair_relations():
    # cand-A > cand-B > cand-C > cand-A: deliberately non-transitive.
    outcomes={
        ('cand-A','cand-B'):'cand-A',
        ('cand-A','cand-C'):'cand-C',
        ('cand-B','cand-C'):'cand-B',
    }
    with TemporaryDirectory() as td:
        root=Path(td); task_id=_create(root)
        _complete_by_candidate(root,task_id,outcomes)
        fps=_fp_by_candidate(root,task_id)
        evidence=decode_triad_pair_matrix_evidence(root)
        assert len(evidence)==3
        assert _evidence_for(evidence,fps['cand-A'],fps['cand-B']).winner_fingerprint==fps['cand-A']
        assert _evidence_for(evidence,fps['cand-A'],fps['cand-C']).winner_fingerprint==fps['cand-C']
        assert _evidence_for(evidence,fps['cand-B'],fps['cand-C']).winner_fingerprint==fps['cand-B']


def test_pair_ids_match_existing_v3_pair_queue_exactly():
    outcomes={
        ('cand-A','cand-B'):'cand-A',
        ('cand-A','cand-C'):'cand-C',
        ('cand-B','cand-C'):'tie',
    }
    with TemporaryDirectory() as td, TemporaryDirectory() as pair_td:
        root=Path(td); task_id=_create(root)
        _complete_by_candidate(root,task_id,outcomes)
        fps=_fp_by_candidate(root,task_id)
        evidence=decode_triad_pair_matrix_evidence(root)
        ac=_evidence_for(evidence,fps['cand-A'],fps['cand-C'])
        pair_id=create_review_bundle(
            Path(pair_td),brief=BRIEF,times=TIMES,
            a_frames=FRAMES_A,b_frames=FRAMES_C,
            a_candidate_id='cand-A',b_candidate_id='cand-C',
        )
        assert ac.pair_id==pair_id


def test_bundle_is_blinded_and_input_order_independent():
    with TemporaryDirectory() as a_td, TemporaryDirectory() as b_td:
        a=Path(a_td); b=Path(b_td)
        a_id=_create(a,('A','B','C')); b_id=_create(b,('C','A','B'))
        assert a_id==b_id
        sealed_a,queue_a,_=_docs(a); sealed_b,queue_b,_=_docs(b)
        assert sealed_a['triads'][a_id]==sealed_b['triads'][b_id]
        assert Path(queue_a['triads'][a_id]['panel']).exists()
        public=json.dumps(queue_a,sort_keys=True)
        for secret in ('cand-A','cand-B','cand-C','route:secret-family'):
            assert secret not in public
        for item in sealed_a['triads'][a_id].values():
            assert item['phenotypeFingerprint'] not in public
        assert 'reviewGroups' not in queue_a


def test_ties_and_authority_semantics_are_unchanged():
    outcomes={
        ('cand-A','cand-B'):'tie',
        ('cand-A','cand-C'):'cand-A',
        ('cand-B','cand-C'):'cand-C',
    }
    with TemporaryDirectory() as td:
        root=Path(td); task_id=_create(root); _complete_by_candidate(root,task_id,outcomes)
        fps=_fp_by_candidate(root,task_id); evidence=decode_triad_pair_matrix_evidence(root)
        ab=_evidence_for(evidence,fps['cand-A'],fps['cand-B'])
        assert ab.winner_fingerprint is None
        assert resolve_phenotype_promotion_evidence([ab],pair_id=ab.pair_id).confidence=='clear'

    for source_class,confidence in (('human','low'),('same-model','strong')):
        with TemporaryDirectory() as td:
            root=Path(td); task_id=_create(root)
            _complete_by_candidate(root,task_id,outcomes,source_class=source_class,confidence=confidence)
            for ev in decode_triad_pair_matrix_evidence(root):
                resolution=resolve_phenotype_promotion_evidence([ev],pair_id=ev.pair_id)
                assert resolution.confidence=='defer' and resolution.review_needed


def test_unresolved_is_empty_but_partial_completion_fails_closed():
    with TemporaryDirectory() as td:
        root=Path(td); task_id=_create(root)
        assert decode_triad_pair_matrix_evidence(root)==[]
        _,_,decisions=_docs(root)
        decisions['decisions'][task_id]['pairVerdicts']['A:B']='A'
        (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
        _assert_decode_fails(root,'partially completed')


def test_malformed_pair_keys_and_verdicts_fail_closed():
    invalid=(
        {'A:B':'A','A:C':'A'},
        {'A:B':'C','A:C':'A','B:C':'B'},
        {'A:B':'A','A:C':'B','B:C':'B'},
        {'A:B':'A','A:C':'C','B:C':'A'},
        [('A:B','A')],
    )
    for value in invalid:
        try:
            _validate_pair_verdicts(value)
        except ValueError:
            pass
        else:
            raise AssertionError(f'expected invalid pair matrix: {value!r}')


def test_invalid_provenance_and_schema_fail_closed():
    outcomes={
        ('cand-A','cand-B'):'cand-A',
        ('cand-A','cand-C'):'cand-C',
        ('cand-B','cand-C'):'cand-B',
    }
    for field,value in (('sourceClass',None),('sourceClass','unknown'),('sourceId',None),('confidence',None),('confidence','maybe')):
        with TemporaryDirectory() as td:
            root=Path(td); task_id=_create(root); _complete_by_candidate(root,task_id,outcomes)
            _,_,decisions=_docs(root); decisions['decisions'][task_id][field]=value
            (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
            _assert_decode_fails(root)
    for filename in ('sealed-mapping.json','queue.json','decisions.json'):
        with TemporaryDirectory() as td:
            root=Path(td); task_id=_create(root); _complete_by_candidate(root,task_id,outcomes)
            path=root/filename; doc=json.loads(path.read_text()); doc['version']=999
            path.write_text(json.dumps(doc,indent=2)+'\n')
            _assert_decode_fails(root,'v1 pair-matrix schema')


def test_replay_metadata_or_fingerprint_drift_fails_closed():
    outcomes={
        ('cand-A','cand-B'):'cand-A',
        ('cand-A','cand-C'):'cand-C',
        ('cand-B','cand-C'):'cand-B',
    }
    for field,value in (('brief','tampered'),('times',[0,1,99]),('triadId','tampered-id'),('promptVersion','future-prompt'),('pairKeys',['A:B'])):
        with TemporaryDirectory() as td:
            root=Path(td); task_id=_create(root); _complete_by_candidate(root,task_id,outcomes)
            _,queue,_=_docs(root); queue['triads'][task_id][field]=value
            (root/'queue.json').write_text(json.dumps(queue,indent=2)+'\n')
            _assert_decode_fails(root)
    with TemporaryDirectory() as td:
        root=Path(td); task_id=_create(root); _complete_by_candidate(root,task_id,outcomes)
        sealed,_,_=_docs(root); sealed['triads'][task_id]['A']['phenotypeFingerprint']='tampered-fingerprint'
        (root/'sealed-mapping.json').write_text(json.dumps(sealed,indent=2)+'\n')
        _assert_decode_fails(root,'replay-integrity')


def test_duplicate_visible_phenotypes_are_rejected():
    with TemporaryDirectory() as td:
        try:
            create_triad_pair_matrix_bundle(
                Path(td),brief=BRIEF,times=TIMES,
                a_frames=FRAMES_A,b_frames=FRAMES_A,c_frames=FRAMES_C,
                a_candidate_id='cand-A',b_candidate_id='cand-B',c_candidate_id='cand-C',
            )
        except ValueError as e:
            assert 'distinct phenotype fingerprints' in str(e)
        else:
            raise AssertionError('expected duplicate phenotype rejection')
