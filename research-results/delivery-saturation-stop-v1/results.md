# Delivery saturation stop v1 — result

Decision: **SATURATION_STOP_NOT_PROMISING**

The exact preregistered stable-three rule is stopped.

## Evidence

Frozen population: 20 master seeds × recurrence/orbit/filament × 15 structural targets = 900 paired cells.

Frozen non-inferiority margin: `0.003255297955511336`, exactly half of #106's confirmed max-dispersion delivery gain.

Compute savings were real:

- early stops: **44/60 (73.33%)**
- median attempts saved: **3**
- mean attempts saved: **2.8**
- median hypothetical stop: attempt **17**

But capacity retention failed the preregistered boundary:

- mean delivery loss: `0.0009394779239665187` — below margin
- one-sided 95% upper delivery loss: `0.0040042705081515875` — **above margin**
- mean full-prefix archive loss: `0.005014214564779022` — **above margin**
- one-sided 95% upper archive loss: `0.007111723935182653` — **above margin**

Route mean delivery loss stayed below margin:

- recurrence `0.0002652711884527196`
- orbit `0.0001574044922893462`
- filament `0.0023957580911574904`

But every route's mean archive loss exceeded the margin:

- recurrence `0.006121491233982623`
- orbit `0.004773686314788942`
- filament `0.004147466145565499`

## Interpretation

The promoted three-item max-dispersion delivery surface can become stable while the underlying discovery archive is still gaining meaningful structural capacity. **Delivery saturation is not archive saturation.**

The rule would often save compute, but the omitted suffix remains scientifically valuable. Therefore keep the full 20-attempt incumbent-only mixed native+spectral search budget.

Per preregistration, do not tune any nearby form of this rule on the consumed `744xxx` evidence:

- minimum valid prefix remains untuned;
- stability count remains untuned;
- pixel-distance representation remains untuned;
- non-inferiority margin remains untuned.

A future efficiency experiment must use a materially different hypothesis rather than a nearby stopping-rule parameterization.

## Provenance

Scientific source head: `7221e012f504bed0ddd62abb88e9754ff4ce59d7`.

The frozen 20 seeds completed in operational parallel run `33400268616`. Its aggregate job failed before reduction only because the aggregate runner omitted the Python requirements install (`ModuleNotFoundError: numpy`). No seed artifact was opened.

Recovery run `33400912694` downloaded those exact 20 completed artifacts and executed the unchanged frozen reducer. Authoritative summary artifact:

- artifact `9761179376`
- digest `sha256:e181ea9efd16584cebd360ad2be5bb8d40191101978df2520cebf9ae7f68bf5f`

The original/duplicate sequential runs were not used or inspected.
