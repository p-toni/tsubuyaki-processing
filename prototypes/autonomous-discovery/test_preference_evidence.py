from preference_evidence import PreferenceEvidence, resolve_promotion_evidence

P = "pair-1"

def ev(v, cls, sid, conf="strong"):
    return PreferenceEvidence(P, v, cls, sid, conf)

r = resolve_promotion_evidence([ev("a", "same-model", "gpt-a")])
assert (r.verdict, r.confidence) == ("tie", "defer")

r = resolve_promotion_evidence([ev("b", "human", "toni", "low")])
assert (r.verdict, r.confidence) == ("tie", "defer")

r = resolve_promotion_evidence([ev("b", "human", "toni")])
assert (r.verdict, r.confidence) == ("b", "clear")

r = resolve_promotion_evidence([
    ev("b", "human", "toni"),
    ev("a", "same-model", "gpt-a"),
    ev("a", "deterministic-proxy", "proxy-v1"),
])
assert (r.verdict, r.confidence) == ("b", "clear")

r = resolve_promotion_evidence([
    ev("a", "human", "toni"),
    ev("b", "independent-model", "judge-b"),
])
assert (r.verdict, r.confidence) == ("tie", "defer")

r = resolve_promotion_evidence([
    ev("a", "human", "toni"),
    ev("a", "human", "toni"),
])
assert r.authoritative_sources == ("toni",)

r = resolve_promotion_evidence([
    ev("a", "human", "toni"),
    ev("b", "human", "toni"),
])
assert (r.verdict, r.confidence) == ("tie", "defer")

r = resolve_promotion_evidence([
    ev("a", "human", "toni"),
    ev("a", "independent-model", "judge-b"),
])
assert (r.verdict, r.confidence) == ("a", "clear")

print("preference evidence policy: PASS")
