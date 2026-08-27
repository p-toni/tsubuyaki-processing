# Autonomous Discovery Prototype

Executable prototype of the mathematical-discovery loop developed in the tsubuyaki-processing research.

## Current architecture

```text
brief
  ↓
route proposals
  ↓
multiple basin representatives
  ↓
route-specific hard validity
  ↓
shared exploration
  ↓
pairwise temporal selector
  ├─ clear win
  ├─ clear loss
  └─ tie / defer
  ↓
uncertainty-aware allocation
  ↓
local refinement + late structural escape
  ↓
artistic frontier
```

The description-length / golf boundary is intentionally not implemented yet. Search stays compression-blind.

## 1. Route-specific validity layer

`checkers.py`

Validity is separate from artistic judgment.

### recurrence / filament

Hard checks:
- finite geometry
- in-frame survival
- axial-spine survival
- spine continuity
- meaningful axial coverage
- temporal continuity

**Occupancy is not a validity gate.** Sparse filamentary work is allowed.

### family

Hard checks:
- root survives
- expected sibling count survives
- anchors remain in frame
- organ tips mostly remain in frame
- repeated-family scale coherence

The checkers consume semantic geometry from the same generator used by the renderer, preventing probe–renderer drift.

## 2. Pairwise selector layer

`pairwise_selector.py`

The search loop no longer promotes with `max(score)` or a scalar fitness value.

Selector contract:

```text
A vs B across matched temporal horizon
→ A wins | B wins | tie/defer
```

The bundled `DeterministicTemporalSelector` is only a conservative executable proxy. It votes independently on auditable dimensions such as:
- composition span
- framing balance
- temporal interest
- temporal consistency
- recurrence continuity / axial span
- family coherence / separation

It deliberately does **not** claim to encode artistic quality.

For recurrence, occupancy is absent from selector dimensions as well as validity.

Ties preserve the incumbent or preserve multiple live representatives; they are not broken by the old diagnostic score.

The previous scalar remains in `report.json` only as `diagnosticScore`, so future experiments can measure disagreement with the selector. `diagnosticScoreUsedForPromotion` must remain false.

## 3. Real human/model judgment bridge

`judge_queue.py`

The prototype can export every unresolved selector pair as a blinded matched-time panel:

```bash
python run.py \
  --brief brief.json \
  --seed 260826 \
  --out run-with-queue \
  --judge-queue judge-queue
```

This writes:

```text
judge-queue/
├─ panels/<pair-id>.png
├─ queue.json
├─ decisions-template.json
└─ sealed-mapping.json
```

The evaluator sees only A / B / tie. `sealed-mapping.json` preserves candidate identity separately.

Fill `decisions-template.json`, then replay the exact same seeded search with:

```bash
python run.py \
  --brief brief.json \
  --seed 260826 \
  --out replayed-run \
  --blind-decisions-dir judge-queue
```

The same interface is now also backed directly by `multimodal_judge.py`; the filesystem queue remains useful for independent human/external review and offline replay.

## 4. Route-aware selection

A cross-route tie must not shield same-route losses.

The selector therefore reduces candidates within each route first, then compares route champions. If the cross-route judgment is uncertain, each route keeps its local artistic frontier.

This matters because the current deterministic proxy is intentionally much more confident comparing two recurrence variants or two repeated-family variants than comparing unrelated representations.

## Tests

```bash
python test_checkers.py
python test_selector.py
python test_judge_queue.py
python test_multimodal_judge.py
```

Current adversarial coverage includes:
- healthy recurrence passes
- healthy family passes
- extremely sparse filament still passes
- exploding/offscreen recurrence fails
- broken family count fails
- giant offscreen family organs fail
- renderer/checker geometry parity
- pair reversal consistency
- exact clone produces tie/defer
- invalid candidate loses before artistic judgment
- recorded human/external decisions replay correctly
- tie/defer preserves both candidates
- judge queue deduplicates repeated comparisons
- end-to-end search uses pairwise decisions, not diagnostic score, for promotion

## Smoke run

```bash
python run.py --brief brief.json --seed 260826 --out example_run
```

Outputs:
- `stage1_representatives.png`
- `stage2_survivors.png`
- `finalists.png`
- `winner_timeline.png`
- `report.json`
- `search_state.json`

## Current limitation

The deterministic proxy is intentionally conservative and the direct multimodal judge has not been live-calibrated in this environment because no API key is available here. Its request/response contract, symmetry logic, caching, failure semantics, and search integration are covered by injected-transport tests.

The important architectural boundary remains:

```text
search policy
≠ artistic judge
```

Human, external-agent, deterministic, and direct multimodal judgments can all use the same pairwise interface without rewriting search policy.

## 5. Direct multimodal judge

`multimodal_judge.py`

The filesystem review bridge now has a direct API-backed implementation.

The search architecture is:

```text
route-specific validity
→ deterministic coarse selector
   ├─ clear win/loss → use decision
   └─ tie/defer → direct multimodal judge
                  ├─ A
                  ├─ B
                  └─ tie/defer
```

The direct judge sees only:
- the artistic brief;
- candidate A across the matched temporal horizon;
- candidate B across the same horizon.

It does **not** receive candidate IDs, genomes, route internals, code length, compression estimates, or `diagnosticScore`.

### A/B order-symmetry guard

By default every escalated pair is judged twice:

```text
pass 1: A=candidate1, B=candidate2
pass 2: A=candidate2, B=candidate1
```

A clear preference is accepted only when both passes resolve to the same actual candidate. Any disagreement, a tie in either pass, API failure, or API-budget exhaustion becomes `tie/defer`.

This intentionally spends more judge calls in exchange for lower position-bias risk. Disable only for experiments with:

```bash
--judge-no-symmetry
```

### OpenAI Responses API

Set an API key:

```bash
export OPENAI_API_KEY=...
```

Then run:

```bash
python run.py \
  --brief brief.json \
  --seed 260826 \
  --out direct-judge-run \
  --multimodal-judge
```

Default judge model:

```text
gpt-5.6-terra
```

Override it with:

```bash
--judge-model gpt-5.6-luna
--judge-model gpt-5.6-sol
```

or `OPENAI_JUDGE_MODEL`.

Other controls:

```bash
--judge-reasoning low|medium|high|max
--judge-image-detail low|high|auto
--judge-max-api-calls N
--judge-cache PATH
--judge-audit-dir PATH
```

The implementation uses the Responses API directly over HTTPS with image input and a strict JSON-schema output contract. `store=false` is set on judge requests.

### Persistent judgment cache

Every direct judgment is cached with:
- model;
- reasoning effort;
- prompt version;
- temporal horizon;
- brief hash;
- **rendered phenotype fingerprint for both candidates**;
- both symmetry-pass outputs and response IDs;
- usage metadata.

A candidate ID alone is never enough for a cache hit. If the rendered phenotype changes, the pair is judged again.

By default the run writes:

```text
<out>/judge-cache.json
<out>/judge-audit/panels/<pair>-ab.png
<out>/judge-audit/panels/<pair>-ba.png
```

This makes multimodal decisions auditable and replayable rather than ephemeral.

### Failure semantics

The multimodal judge is not allowed to fail open.

```text
missing/invalid candidate → hard validity layer decides
API unavailable           → tie/defer
malformed model output     → tie/defer
A/B symmetry conflict      → tie/defer
call budget exhausted      → tie/defer
low model confidence       → tie/defer
```

The search may preserve optionality or export unresolved ties through `judge_queue.py`; it must never invent an artistic winner because the judge failed.

## Direct-judge tests

```bash
python test_multimodal_judge.py
```

Coverage includes:
- strict multimodal Responses payload shape;
- structured output contract;
- A/B reversal consistency;
- symmetry disagreement → tie;
- model `confidence=defer` → tie;
- invalid candidate short-circuits API;
- persistent cache replay;
- phenotype change invalidates cache;
- API-call budget exhaustion → tie;
- coarse selector escalates only unresolved pairs.

The tests use an injected fake transport and require no API key. A live API smoke test is intentionally not run in CI by default.
