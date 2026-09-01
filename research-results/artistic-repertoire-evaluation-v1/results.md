# Artistic repertoire evaluation v1

Decision: **ARTISTIC_NOT_SUPPORTED**.

This resolves the previously generated but never rated blind artistic review from PR #79 after the repertoire-preserving allocator was mechanically confirmed in #78.

## Frozen evidence

- Original review PR: #79
- Frozen generation head: `e62c1ed99105dfa56b9cd96bb9e5ba8cc7f4f9ac`
- Frozen reducer blob: `3d801493849fc806aae45ff81546f8a2e0259571`
- Review workflow run: `33267664869`
- Reviewer sheets artifact: `9719175928`
- Reviewer sheets digest: `sha256:1e01cb7cafe406a8264a07c87b7c79106fb66c7eeed970c989e3dafb80b1d13b`
- Blind-key artifact: `9719176083`
- Blind-key digest: `sha256:63300cd6d0f977caa2117658294a732768d8a12ac5f852eec11be1283d3699ab`
- 20 frozen review blocks across five route strata
- One human reviewer
- Judgments were fixed before the blind key was opened.

## Judgments

All 20 blocks were judged **equivalent**.

- reviewable: **20 / 20**
- decisive: **0**
- equivalent: **20**
- unreviewable: **0**
- candidate wins: **0**
- baseline wins: **0**
- net preference: **0**
- every route net: **0**
- every leave-one-route-out net: **0**
- exact one-sided sign-test diagnostic: **p = 1.0**

## Preregistered gates

`ARTISTIC_SUPPORT` required all three:

1. at least 15 / 20 reviewable — **PASS**
2. candidate-vs-baseline total net preference > 0 — **FAIL** (`0`)
3. every leave-one-route-out net preference > 0 — **FAIL** (all `0`)

Therefore the frozen decision is **ARTISTIC_NOT_SUPPORTED**.

## Interpretation

The repertoire-preserving allocator remains a confirmed **mechanical search primitive**: under its frozen target-recovery evaluation it improved recovery of unseen structural targets.

But under the independent blind portfolio presentation frozen in #79, that mechanical advantage produced **no perceived artistic difference at all** for this reviewer. The evidence therefore does not authorize repertoire-preserving parent selection as a default production/runtime policy.

The useful architectural conclusion is narrower:

> repertoire/niche history may remain explicit search state and a research substrate, but mechanical target-recovery gains cannot be promoted into artistic authority without a human-visible benefit.

Do not tune the #77/#78 allocator from these consumed review blocks. Close this exact automatic allocator line.
