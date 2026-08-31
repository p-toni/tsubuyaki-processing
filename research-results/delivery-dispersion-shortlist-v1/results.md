# Delivery dispersion shortlist v1 — result

Decision: `DISPERSION_SHORTLIST_PROMISING`.

Authoritative run: `33393096273`  
Artifact: `9758648314`  
Digest: `sha256:be4eb59c173126ee81d720823a6a309cdedf32df4cddcde5ec67e17cf57c5d12`

## Frozen result

- 16 fresh master seeds.
- 3 routes × 15 frozen structural targets = 720 paired cells.
- Mean seed-level dispersion-minus-quantile recovery: `+0.006510595911022672`.
- One-sided 95% bootstrap lower bound: `+0.0011871329689249832`.
- Route mean effects:
  - recurrence: `+0.00827211150397907`
  - orbit: `+0.005570540130965609`
  - filament: `+0.005689136098123338`
- Mean full-archive regret:
  - generation quantiles: `0.024071582134709685`
  - max dispersion: `0.017560986223687014`
- Median target-blind minimum-pairwise-distance lift: `+0.0009850326797385617`.
- Strict distance lift occurred in `47/48` route-seed blocks; the remaining block tied and none regressed.

All preregistered recovery gates passed.

## Interpretation

#104 and #105 established the architectural boundary:

- plurality has artistic value at the archive/delivery surface;
- distributing a fixed search budget across plural parents harms search recovery.

#106 now supplies the missing delivery mechanism. The efficient incumbent-only mixed search can remain unchanged while a target-blind max-dispersion shortlist exposes three archive members that retain more of the archive's external structural coverage than simple generation-order quantiles.

This remains mechanical evidence, not artistic authority. The preregistered next step is a fresh blinded human comparison of **max-dispersion shortlist vs generation-quantile shortlist** from the same mixed archive. Do not tune the distance resolution, shortlist size, or objective on these consumed seeds.
