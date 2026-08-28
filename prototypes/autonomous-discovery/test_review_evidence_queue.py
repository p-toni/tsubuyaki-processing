import json
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image
from review_evidence_queue import create_review_bundle, decode_review_evidence, pair_id_for_phenotypes, phenotype_fingerprint
from preference_evidence import resolve_promotion_evidence

frames_a = [Image.new("RGB", (64,64), (30+i,20,20)) for i in range(3)]
frames_b = [Image.new("RGB", (64,64), (20,30+i,20)) for i in range(3)]

with TemporaryDirectory() as td:
    root = Path(td)
    pid = create_review_bundle(root, brief="cold test", times=[0,1,2], a_frames=frames_a, b_frames=frames_b,
                               a_candidate_id="A1", b_candidate_id="B1")
    helper_pid = pair_id_for_phenotypes(
        brief="cold test", times=[0,1,2],
        a_fingerprint=phenotype_fingerprint(frames_a),
        b_fingerprint=phenotype_fingerprint(frames_b),
    )
    assert helper_pid == pid
    sealed = json.loads((root / "sealed-mapping.json").read_text())
    assert pid in sealed["pairs"]
    d = json.loads((root / "decisions.json").read_text())
    d["decisions"][pid].update({
        "verdict":"A", "sourceClass":"human", "sourceId":"reviewer-1", "confidence":"low", "rationale":"hard to read"
    })
    (root / "decisions.json").write_text(json.dumps(d, indent=2)+"\n")
    ev = decode_review_evidence(root)
    assert len(ev) == 1 and ev[0].confidence == "low"
    assert resolve_promotion_evidence(ev).confidence == "defer"

    d["decisions"][pid]["confidence"] = "strong"
    (root / "decisions.json").write_text(json.dumps(d, indent=2)+"\n")
    ev = decode_review_evidence(root)
    assert resolve_promotion_evidence(ev).confidence == "clear"

print("review evidence queue v3: PASS")
