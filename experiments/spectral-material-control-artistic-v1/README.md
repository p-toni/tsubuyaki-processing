# Spectral material-control blinded artistic review v1

## Question

Under equal search compute, does the confirmed `native-spectral-50-50-v1` runtime leave a human reviewer with a stronger final form than `native-only` when both arms use the **same incumbent grammar, route, seed, start phenotype, search budget, runtime selector, and presentation**?

This is the human-evidence boundary authorized by the fresh runtime replay result. It deliberately does **not** repeat the invalid #87 comparison between naked spectral zero-set contours and complete incumbent grammars.

## Frozen population

Review-only seeds, checked absent from repository code and commit-message history before branch creation:

- `126007`
- `126011`
- `126019`
- `126031`

Fixed intrinsic-1D route strata:

- recurrence
- orbit
- filament

This yields **12 anonymous A/B blocks**. Excluded smoke seed: `126999`.

## Frozen generation

For each route × review seed:

- run the current confirmed runtime search twice from the same deterministic seed;
- baseline arm: `native-only`;
- candidate arm: `native-spectral-50-50-v1`;
- exactly one hard-valid start per arm;
- exact start genome and rendered phenotype must match across arms;
- exactly 20 challenger attempts per arm;
- native-only = 20 native challengers;
- mixed = 10 native + 10 spectral challengers;
- use the unchanged deterministic temporal selector;
- present the runtime-selected `provisionalChampion` from each arm;
- no structural target, semantic target, diagnostic metric, LLM judge, human prior, or post-hoc artistic selector chooses the displayed candidates.

The experiment tests the runtime *as integrated*, not an oracle-selected best candidate from its archive.

## Frozen presentation

Each side is one three-frame raw temporal strip at `t = 30, 90, 150` from `core.render_candidate_frame`, with identical resizing and no autocontrast. Reviewer-facing files contain only block ID and `A` / `B` labels.

Route, seed, runtime mode, candidate ID, genome, operator history, and A/B assignment are absent from reviewer-facing files.

A/B assignment is deterministic from a frozen blind salt and block ID. The mapping is written only to a separately uploaded key artifact. The key must remain unopened until all R01–R12 judgments are fixed.

## Allowed judgment

For every block choose exactly one:

- `A>B`
- `B>A`
- `equivalent`
- `unreviewable`

Question to answer:

> Which side is the stronger mathematical form worth keeping or developing further?

Judge the overall temporal form, coherence, richness, legibility, and interest. Do not try to infer which mechanism produced it.

## Preregistered support gate

After all judgments are frozen and the key is opened, candidate (`native-spectral-50-50-v1`) receives +1 for a win, baseline (`native-only`) −1 for a win, and equivalent / unreviewable 0.

`ARTISTIC_SUPPORT` requires all of:

1. at least **9/12** blocks reviewable;
2. total mixed-vs-native net preference **> 0**;
3. every leave-one-route-out mixed-vs-native net preference **> 0**.

Route-specific nets and exact sign tests are diagnostics only and cannot override the frozen gate.

## Authority boundary

A positive result supports artistic usefulness of the opt-in mixed spectral material-control runtime for this independent reviewer and these intrinsic-1D grammars. It does not establish universal aesthetic superiority, justify removing native search, or automatically make mixed search the default.

A negative result leaves the spectral mechanism as mechanically confirmed but artistically unproven. It does not invalidate the prior structural-capacity or fixed-budget recovery results.
