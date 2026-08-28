"""Decode v3 review bundles into order-independent phenotype evidence."""
from __future__ import annotations
import json
from pathlib import Path
from phenotype_preference_evidence import PhenotypePreferenceEvidence
from review_evidence_queue import VERSION


def decode_review_phenotype_evidence(out_dir:Path)->list[PhenotypePreferenceEvidence]:
    out_dir=Path(out_dir)
    sealed=json.loads((out_dir/'sealed-mapping.json').read_text())
    decisions=json.loads((out_dir/'decisions.json').read_text())
    if sealed.get('version')!=VERSION or decisions.get('version')!=VERSION:
        raise ValueError('review bundle must be v3')
    out=[]
    for pair_id,item in decisions['decisions'].items():
        verdict=item.get('verdict')
        if verdict is None: continue
        if verdict not in {'A','B','tie'}: raise ValueError(f'invalid verdict for {pair_id}')
        source_class=item.get('sourceClass'); source_id=item.get('sourceId'); confidence=item.get('confidence')
        if not source_class or not source_id or not confidence:
            raise ValueError(f'decision {pair_id} is missing provenance/confidence')
        mapping=sealed['pairs'][pair_id]
        afp=mapping['A']['phenotypeFingerprint']; bfp=mapping['B']['phenotypeFingerprint']
        winner=None if verdict=='tie' or afp==bfp else mapping[verdict]['phenotypeFingerprint']
        out.append(PhenotypePreferenceEvidence(
            pair_id=pair_id,
            phenotype_fingerprints=(afp,bfp),
            winner_fingerprint=winner,
            source_class=source_class,
            source_id=source_id,
            confidence=confidence,
            rationale=item.get('rationale',''),
        ))
    return out
