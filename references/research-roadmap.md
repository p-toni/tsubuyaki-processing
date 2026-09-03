# Research roadmap

This file records future research branches that are promising enough to preserve without allowing them to bypass active preregistered evidence chains.

## Active principle

Move one evidentiary layer at a time:

```text
operator primitive
→ equal-budget portfolio usefulness
→ isolated runtime replay
→ artistic authority when relevant
→ broader integration only after the required authority exists
```

Do not let a new idea bypass a currently open causal chain.

## Completed chain — family projected-spectral material control

The family-specific projected-spectral line has now reached its terminal boundary:

```text
#131  operator primitive                 mechanically positive
#133  equal-budget portfolio             mechanically positive
#134  integrated adaptive runtime        mechanically positive
#135  blinded human artistic usefulness  not demonstrated
```

#135 produced 24/24 reviewable blocks but only 6 decisive judgments; projected-spectral won 2/6, native-only won 4/6, and the frozen artistic support gate failed. The family projected-spectral runtime therefore remains mechanically supported, opt-in, and default-off. Do not tune the consumed `765xxx` population.

This terminal result releases the recurrent learned-operator branch below.

## Active branch — recurrent learned discovery operator

### Motivation

Recent work on small weight-tied recurrent transformers such as Sotaku suggests a distinct compute regime from the one this project has explored most deeply.

Most current discovery work scales compute by evaluating more alternatives:

```text
state
→ generate candidate set
→ validate
→ preserve archive / delivery
→ allocate more search
```

The recurrent alternative would learn one transition operator and apply it repeatedly to an evolving mathematical state:

```text
s0
→ Fθ(s0)
→ Fθ(s1)
→ Fθ(s2)
→ …
```

The important hypothesis is **not** that more local iterations should beat breadth under the current mutation operators. Existing restart/breadth evidence remains valid. The new hypothesis is that an operator explicitly trained to remain useful on its own outputs may exhibit qualitatively different long-horizon behavior.

### First isolated experiment

Question:

> Can a small weight-tied learned transition operator continue improving mechanically measurable mathematical structure beyond its training horizon while preserving hard validity and defining representation laws?

No artistic judge is required for the first test.

Candidate design:

- small shared neural transition `Fθ`;
- persistent mathematical/morphology state plus a small latent working state if needed;
- train through short recurrent windows;
- expose training to later recurrent states using no-gradient burn-in followed by short gradient-tracked windows;
- train horizon initially around 8–16 recurrent applications;
- no semantic target or aesthetic scorer in the initial study.

Evaluation horizon:

```text
1, 2, 4, 8, 16, 32, 64, 128, 256
```

Primary measurements:

- hard-valid rate;
- defining-law preservation;
- structural-recovery trajectory;
- phenotype displacement / novelty trajectory;
- convergence, fixed points, cycles, and collapse;
- performance beyond the training horizon.

Critical controls:

1. current supported native mutation;
2. current supported native + spectral machinery where applicable;
3. weight-tied recurrent `Fθ`;
4. equal-parameter/equal-compute untied or unrolled transition stack.

The tied-vs-untied control is essential: it tests whether weight sharing itself provides a useful optimization/algorithmic forcing function rather than merely reducing parameter count.

### Advancement boundary

Promising evidence requires a stable positive trajectory beyond the training horizon without validity collapse, plus a meaningful advantage over the untied/equivalent-compute control.

A peak near the training horizon followed by degradation closes the first recurrent-operator hypothesis rather than triggering horizon/architecture tuning on the consumed population.

### Relationship to prior negative work

This is not a revival of the failed learned-world-model / MPC line.

Prior learned-dynamics work approximated:

```text
state + action → predicted consequence
```

and then used an external controller to navigate.

The recurrent branch instead learns the transition/computation itself:

```text
state → next state
```

with the same operator repeatedly consuming its own outputs.

### Priority

**Active.** The family projected-spectral causal chain has reached its terminal artistic boundary, so this branch is now the next independent research direction.
