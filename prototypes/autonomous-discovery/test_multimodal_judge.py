#!/usr/bin/env python3
from __future__ import annotations
import copy, json, random, tempfile
from pathlib import Path

import run
from multimodal_judge import DirectMultimodalSelector, MultimodalEscalatingSelector
from pairwise_selector import DeterministicTemporalSelector, PairwiseDecision, PairwiseSelector, DimensionVote


def make_valid(route, seed, cid):
    rng=random.Random(seed)
    for _ in range(100):
        g=run.ROUTES[route]['seed'](rng)
        c=run.Candidate(cid,route,cid,g,None,'test')
        run.evaluate_candidate(c,run.default_brief())
        if c.checks['valid']: return c
    raise AssertionError('no valid candidate')


def resp(verdict, confidence='clear', rid='r1'):
    body={
        'verdict':verdict,'confidence':confidence,'rationale':'test rationale',
        'brief_adherence':verdict if verdict!='tie' else 'tie',
        'composition_material':verdict if verdict!='tie' else 'tie',
        'temporal_quality':verdict if verdict!='tie' else 'tie',
        'originality':verdict if verdict!='tie' else 'tie',
    }
    return {'id':rid,'output':[{'type':'message','content':[{'type':'output_text','text':json.dumps(body)}]}],'usage':{'input_tokens':10,'output_tokens':5}}


class SeqTransport:
    def __init__(self, outputs): self.outputs=list(outputs); self.payloads=[]
    def __call__(self,payload):
        self.payloads.append(payload)
        if not self.outputs: raise AssertionError('unexpected extra call')
        out=self.outputs.pop(0)
        if isinstance(out,Exception): raise out
        return out


class AlwaysTie(PairwiseSelector):
    name='always-tie'
    def compare(self,a,b,brief):
        return PairwiseDecision(a.id,b.id,'tie','defer',(DimensionVote('test','tie','force escalation'),),self.name)


def main():
    brief=run.default_brief(); brief['artistic_intent']='test artistic intent'
    a=make_valid('family',101,'A'); b=make_valid('family',202,'B')

    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        # Symmetry: pass1 A wins, pass2 B wins => same actual candidate A.
        tr=SeqTransport([resp('A',rid='ab'),resp('B',rid='ba')])
        judge=DirectMultimodalSelector(run._render_candidate_frame,run.TIMES,transport=tr,cache_path=td/'cache.json',audit_dir=td/'audit')
        d=judge.compare(a,b,brief)
        assert d.verdict=='a' and d.confidence=='clear',d.to_json()
        assert len(tr.payloads)==2
        p=tr.payloads[0]
        assert p['model']=='gpt-5.6-terra' and p['store'] is False
        assert p['text']['format']['type']=='json_schema' and p['text']['format']['strict'] is True
        user=p['input'][1]['content']
        assert sum(x['type']=='input_image' for x in user)==1
        assert user[-1]['image_url'].startswith('data:image/png;base64,')
        assert 'A' not in json.dumps(p).split('ARTISTIC BRIEF')[0]  # no candidate IDs in developer content

        # Cache replay: no new transport calls.
        d2=judge.compare(a,b,brief)
        assert d2.verdict=='a' and len(tr.payloads)==2

        # Phenotype change invalidates cache.
        b2=copy.deepcopy(b); b2.id='B2'; b2.genome=dict(b.genome); b2.genome['organ_len']*=.96; run.evaluate_candidate(b2,brief)
        tr.outputs.extend([resp('tie','defer','x'),resp('tie','defer','y')])
        d3=judge.compare(a,b2,brief)
        assert d3.verdict=='tie' and len(tr.payloads)==4

    # Symmetry disagreement -> tie.
    tr=SeqTransport([resp('A'),resp('A')])  # first actual A, second actual B
    judge=DirectMultimodalSelector(run._render_candidate_frame,run.TIMES,transport=tr)
    assert judge.compare(a,b,brief).verdict=='tie'

    # Model defer -> tie.
    tr=SeqTransport([resp('A','defer'),resp('B','defer')])
    judge=DirectMultimodalSelector(run._render_candidate_frame,run.TIMES,transport=tr)
    assert judge.compare(a,b,brief).verdict=='tie'

    # API failure -> tie, never fabricated winner.
    tr=SeqTransport([RuntimeError('boom'),RuntimeError('boom2')])
    judge=DirectMultimodalSelector(run._render_candidate_frame,run.TIMES,transport=tr)
    assert judge.compare(a,b,brief).verdict=='tie'

    # Budget exhaustion -> tie without transport calls.
    tr=SeqTransport([])
    judge=DirectMultimodalSelector(run._render_candidate_frame,run.TIMES,transport=tr,max_api_calls=1,symmetry=True)
    assert judge.compare(a,b,brief).verdict=='tie' and not tr.payloads

    # Invalid candidate short circuits API.
    bad=copy.deepcopy(b); bad.id='BAD'; bad.checks={'valid':False,'failures':['bad'],'diagnostics':{}}
    tr=SeqTransport([])
    judge=DirectMultimodalSelector(run._render_candidate_frame,run.TIMES,transport=tr)
    assert judge.compare(a,bad,brief).verdict=='a' and not tr.payloads

    # Escalator calls multimodal only on tie.
    tr=SeqTransport([resp('A'),resp('B')])
    esc=MultimodalEscalatingSelector(AlwaysTie(),render_frame=run._render_candidate_frame,times=run.TIMES,transport=tr)
    assert esc.compare(a,b,brief).verdict=='a' and len(tr.payloads)==2

    print('multimodal judge tests: PASS')

if __name__=='__main__': main()
