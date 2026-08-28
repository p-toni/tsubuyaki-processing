import json
from pathlib import Path
from tempfile import TemporaryDirectory

from PIL import Image

from phenotype_preference_evidence import resolve_phenotype_promotion_evidence
from review_evidence_queue import create_review_bundle
from triad_review_evidence_queue import (
    _validate_tiers,
    create_triad_review_bundle,
    decode_triad_phenotype_evidence,
)

TIMES=(0,1,2)
BRIEF='triad transport test'
FRAMES_A=[Image.new('RGB',(64,64),(40+i,10,10)) for i in range(3)]
FRAMES_B=[Image.new('RGB',(64,64),(10,40+i,10)) for i in range(3)]
FRAMES_C=[Image.new('RGB',(64,64),(10,10,40+i)) for i in range(3)]


def _create(root,order=('A','B','C'),review_group='route:secret-family'):
    items={
        'A':('cand-A',FRAMES_A),
        'B':('cand-B',FRAMES_B),
        'C':('cand-C',FRAMES_C),
    }
    vals=[items[label] for label in order]
    return create_triad_review_bundle(
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


def _complete_by_candidate(root,triad_id,tiers_by_candidate,*,source_class='human',confidence='strong'):
    sealed,_,decisions=_docs(root)
    label_by_candidate={item['candidateId']:label for label,item in sealed['triads'][triad_id].items()}
    tiers=[[label_by_candidate[cid] for cid in tier] for tier in tiers_by_candidate]
    decisions['decisions'][triad_id].update({
        'tiers':tiers,
        'sourceClass':source_class,
        'sourceId':'reviewer-1',
        'confidence':confidence,
        'rationale':'explicit triad ranking',
    })
    (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return label_by_candidate


def _fp_by_candidate(root,triad_id):
    sealed,_,_=_docs(root)
    return {item['candidateId']:item['phenotypeFingerprint'] for item in sealed['triads'][triad_id].values()}


def _evidence_for(evidence,left_fp,right_fp):
    pair=tuple(sorted((left_fp,right_fp)))
    matches=[ev for ev in evidence if ev.phenotype_fingerprints==pair]
    assert len(matches)==1
    return matches[0]


def _assert_decode_fails(root,contains=None):
    try:
        decode_triad_phenotype_evidence(root)
    except ValueError as e:
        if contains is not None:
            assert contains in str(e)
    else:
        raise AssertionError('expected triad replay to fail closed')


def test_bundle_is_blinded_and_panel_exists():
    with TemporaryDirectory() as td:
        root=Path(td); tid=_create(root)
        sealed,queue,decisions=_docs(root)
        assert tid in sealed['triads'] and tid in queue['triads'] and tid in decisions['decisions']
        assert Path(queue['triads'][tid]['panel']).exists()
        assert sealed['reviewGroups'][tid]=='route:secret-family'
        public=json.dumps(queue,sort_keys=True)
        for secret in ('cand-A','cand-B','cand-C','route:secret-family'):
            assert secret not in public
        for item in sealed['triads'][tid].values():
            assert item['phenotypeFingerprint'] not in public
        assert 'reviewGroups' not in queue


def test_input_order_does_not_change_task_or_anonymous_mapping():
    with TemporaryDirectory() as a_td, TemporaryDirectory() as b_td:
        a=Path(a_td); b=Path(b_td)
        tid_a=_create(a,('A','B','C'))
        tid_b=_create(b,('C','A','B'))
        assert tid_a==tid_b
        sealed_a,_,_=_docs(a); sealed_b,_,_=_docs(b)
        assert sealed_a['triads'][tid_a]==sealed_b['triads'][tid_b]


def test_completed_ranking_decodes_to_exact_existing_pair_ids_and_semantics():
    with TemporaryDirectory() as td, TemporaryDirectory() as pair_td:
        root=Path(td); tid=_create(root)
        _complete_by_candidate(root,tid,[['cand-C'],['cand-A','cand-B']])
        fps=_fp_by_candidate(root,tid)
        evidence=decode_triad_phenotype_evidence(root)
        assert len(evidence)==3

        ab=_evidence_for(evidence,fps['cand-A'],fps['cand-B'])
        ac=_evidence_for(evidence,fps['cand-A'],fps['cand-C'])
        bc=_evidence_for(evidence,fps['cand-B'],fps['cand-C'])
        assert ab.winner_fingerprint is None
        assert ac.winner_fingerprint==fps['cand-C']
        assert bc.winner_fingerprint==fps['cand-C']

        pair_id=create_review_bundle(
            Path(pair_td),brief=BRIEF,times=TIMES,
            a_frames=FRAMES_A,b_frames=FRAMES_C,
            a_candidate_id='cand-A',b_candidate_id='cand-C',
        )
        assert ac.pair_id==pair_id

        assert resolve_phenotype_promotion_evidence([ab],pair_id=ab.pair_id).confidence=='clear'
        ac_resolution=resolve_phenotype_promotion_evidence([ac],pair_id=ac.pair_id)
        assert ac_resolution.confidence=='clear'
        assert ac_resolution.winner_fingerprint==fps['cand-C']


def test_low_confidence_and_same_model_remain_non_authoritative():
    for source_class,confidence in (('human','low'),('same-model','strong')):
        with TemporaryDirectory() as td:
            root=Path(td); tid=_create(root)
            _complete_by_candidate(root,tid,[['cand-C'],['cand-A'],['cand-B']],source_class=source_class,confidence=confidence)
            for ev in decode_triad_phenotype_evidence(root):
                resolution=resolve_phenotype_promotion_evidence([ev],pair_id=ev.pair_id)
                assert resolution.confidence=='defer'
                assert resolution.review_needed


def test_unresolved_decision_decodes_to_no_evidence():
    with TemporaryDirectory() as td:
        root=Path(td); _create(root)
        assert decode_triad_phenotype_evidence(root)==[]


def test_invalid_tiers_fail_closed():
    invalid=(
        [['A'],['B']],
        [['A','A'],['B','C']],
        [['A'],[],['B','C']],
        [['A'],['B'],['D']],
        'ABC',
        [],
    )
    for value in invalid:
        try:
            _validate_tiers(value)
        except ValueError:
            pass
        else:
            raise AssertionError(f'expected invalid triad tiers to fail: {value!r}')


def test_missing_or_invalid_provenance_fails_closed():
    for field,value in (('sourceClass',None),('sourceClass','unknown'),('sourceId',None),('confidence',None),('confidence','maybe')):
        with TemporaryDirectory() as td:
            root=Path(td); tid=_create(root)
            _complete_by_candidate(root,tid,[['cand-C'],['cand-A'],['cand-B']])
            _,_,decisions=_docs(root)
            decisions['decisions'][tid][field]=value
            (root/'decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
            _assert_decode_fails(root)


def test_queue_identity_metadata_drift_fails_replay_integrity():
    mutations=(
        ('brief','tampered brief'),
        ('times',[0,1,99]),
        ('triadId','tampered-id'),
        ('promptVersion','future-triad-prompt'),
    )
    for field,value in mutations:
        with TemporaryDirectory() as td:
            root=Path(td); tid=_create(root)
            _complete_by_candidate(root,tid,[['cand-C'],['cand-A'],['cand-B']])
            _,queue,_=_docs(root)
            queue['triads'][tid][field]=value
            (root/'queue.json').write_text(json.dumps(queue,indent=2)+'\n')
            _assert_decode_fails(root)


def test_sealed_fingerprint_drift_fails_replay_integrity():
    with TemporaryDirectory() as td:
        root=Path(td); tid=_create(root)
        _complete_by_candidate(root,tid,[['cand-C'],['cand-A'],['cand-B']])
        sealed,_,_=_docs(root)
        sealed['triads'][tid]['A']['phenotypeFingerprint']='tampered-phenotype-fingerprint'
        (root/'sealed-mapping.json').write_text(json.dumps(sealed,indent=2)+'\n')
        _assert_decode_fails(root,'replay-integrity')


def test_incompatible_document_schema_fails_closed():
    for filename in ('sealed-mapping.json','queue.json','decisions.json'):
        with TemporaryDirectory() as td:
            root=Path(td); tid=_create(root)
            _complete_by_candidate(root,tid,[['cand-C'],['cand-A'],['cand-B']])
            path=root/filename; doc=json.loads(path.read_text()); doc['version']=999
            path.write_text(json.dumps(doc,indent=2)+'\n')
            _assert_decode_fails(root,'v1 triad schema')


def test_duplicate_visible_phenotypes_are_rejected_before_review():
    with TemporaryDirectory() as td:
        try:
            create_triad_review_bundle(
                Path(td),brief=BRIEF,times=TIMES,
                a_frames=FRAMES_A,b_frames=FRAMES_A,c_frames=FRAMES_C,
                a_candidate_id='cand-A',b_candidate_id='cand-B',c_candidate_id='cand-C',
            )
        except ValueError as e:
            assert 'distinct phenotype fingerprints' in str(e)
        else:
            raise AssertionError('expected duplicate phenotype rejection')


def main():
    for name,fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn(); print(name,'PASS')

if __name__=='__main__': main()
