# Research Basis: Controllable Complexity (v0.3)

This note records the research synthesis behind the v0.3 morphology workflow. The goal was to answer a narrow engineering question:

> How can a tweet-sized mathematical sketch create a creature with **more visible anatomical complexity and more user control** without spending one code path per visible part?

The answer is not to import any one modeling system literally. It is to borrow the **representational principles** that create high phenotype complexity from low description complexity, then translate them into p5.js expressions, index arithmetic, shared fields, and code-golfable local frames.

## 1. Karl Sims — directed genotype graphs and replicated substructure

**Source:** Karl Sims, *Evolving Virtual Creatures*, SIGGRAPH 1994.

- https://www.karlsims.com/papers/siggraph94.pdf
- DOI: https://doi.org/10.1145/192161.192167

Sims represents creature morphology with a directed graph of nodes/connections rather than specifying every final body element independently. His developmental process allows similar components to be defined once and replicated; attachment positions are constrained to parent surfaces, reflection describes symmetric subtrees, and recursive/repeated structure expands a compact genotype into a larger phenotype.

### Translation to Tsubuyaki Processing

Do **not** implement the actual articulated-block system. Retain these ideas:

1. describe morphology as a graph during reasoning;
2. merge siblings into reusable organ families;
3. encode attachment relative to the parent;
4. use symmetry/repetition operators instead of duplicated formulas;
5. regard the final tweet code as an indirect genotype.

This directly addresses the 259-weighted-character bottleneck: complexity should scale with reuse, not with the number of visible organs.

## 2. L-systems — compact developmental rules and local frames

**Sources:** Przemyslaw Prusinkiewicz, *Graphical Applications of L-systems* (Graphics Interface 1986); Prusinkiewicz & Lindenmayer, *The Algorithmic Beauty of Plants* (1990).

- https://algorithmicbotany.org/papers/graphical.gi86.html
- https://algorithmicbotany.org/papers/

L-systems show that concise rewriting rules can generate branching, hierarchical geometry. Their turtle interpretation is especially relevant because geometry is produced in a **current local frame** rather than from unrelated global coordinates. The plant literature also demonstrates parametric and stochastic variants that generate related but non-identical instances.

### Translation

A literal grammar/string interpreter is far too expensive for a tweet. The useful concepts are:

- hierarchical parent → child generation;
- local orientation inherited along the hierarchy;
- repeated family rules;
- parameters that alter growth/branching systematically.

In tiny p5 code, local frames become parent phase/radius reuse (`childPhase=c+offset`) or, in readable code, a small rotation transform around a parent anchor.

## 3. Wolpert — positional information and regional identity

**Source:** Lewis Wolpert, *Positional information and the spatial pattern of cellular differentiation*, Journal of Theoretical Biology 25(1), 1969, pp. 1–47.

- https://www.sciencedirect.com/science/article/pii/S0022519369800160
- DOI: https://doi.org/10.1016/S0022-5193(69)80016-0

Wolpert's key abstraction is that a developing system can specify position in a coordinate system and then interpret that positional information differently to create different spatial patterns.

### Translation

This suggests a high-leverage architecture for tiny generative creatures:

1. establish shared positional fields (`e`, `k`, `d`);
2. create region identity by interpreting those fields with thresholds/envelopes;
3. reuse the same positional fields for width, attachment, phase, cavity, and surface detail.

This is much cheaper than giving head, torso, tail, and appendages unrelated coordinate systems.

The skill uses this as a **design metaphor**, not as a claim of biological simulation.

## 4. CPPNs — symmetry, repetition, and repetition with variation

**Source:** Kenneth O. Stanley, *Compositional Pattern Producing Networks: A Novel Abstraction of Development*, Genetic Programming and Evolvable Machines 8(2), 2007, pp. 131–162.

- DOI: https://doi.org/10.1007/s10710-007-9028-8
- Bibliographic record: https://stars.library.ucf.edu/facultybib2000/7682/

CPPNs show how compositions of simple functions over geometric coordinates can compactly encode regular spatial patterns. Later descriptions of the approach emphasize symmetry, repetition and **repetition with variation**: combine regular coordinate frames/functions with asymmetric/global coordinates so repeated motifs remain related but differ with position.

### Translation

This maps almost perfectly to Tsubuyaki formulas:

```js
side=i&1
member=i%n
phase=base+member*a+e*b+t*c
size=L+sin(member+e)*v
```

Here discrete residue creates the repeated family while continuous body position modifies each instance. This avoids both extremes:

- independent organ formulas;
- sterile exact cloning/mandala symmetry.

## 5. Skeletal implicit modeling — structure separate from material

**Source:** Jules Bloomenthal and related implicit-modeling work, *Interactive Techniques for Implicit Modeling*.

- https://www.bloomenthal.com/JBloom/pdf/interactive.pdf

Skeletal implicit modeling defines shapes from lower-dimensional skeletons (points, curves, polygonal elements) plus fields that create a blended surface around them. A major modeling advantage is that topology/connection can be handled at the implicit level rather than explicitly stitching parametric patches.

### Translation

The skill does not need polygonization or full implicit surfaces. The important mental separation is:

- **skeleton / attachment structure** = positional coordinate, anchor, spine, family relationship;
- **material / surface** = distance/envelope/fold field around that structure.

This helps prevent the common failure where adding surface detail accidentally moves anatomy.

## 6. Shape grammars and procedural modeling — hierarchy before instance detail

Classic procedural/grammar systems demonstrate that repeated transformations and hierarchical rules can encode large structured models compactly. The specific grammar machinery is less useful here than the general compression principle:

> specify a class of related structures once, then instantiate it through transformations/conditions.

In Tsubuyaki Processing, modulo/parity, index ranges, ternaries, and shared projection fields are the tiny-code equivalents of production/instancing machinery.

## 7. Why not reaction-diffusion / pure morphogenesis simulation?

Reaction-diffusion and related morphogenetic systems are excellent for **surface pattern formation**, but the v0.3 problem is primarily controllable **body-plan topology and attachment**. A reaction-diffusion field can create spots/stripes/folds, yet does not cheaply answer:

- where a fin attaches;
- how four tendrils share a generator;
- which region is head vs trunk;
- how a child follows parent motion.

Therefore v0.3 treats morphogen-like positional fields as regional selectors, but does not make reaction-diffusion the core architecture.

## 8. Why not a literal scene graph?

A conventional scene graph provides excellent explicit control, but its representation cost scales too directly with part count:

- nodes
- transforms
- traversal
- separate draw calls
- state

The tweet budget makes that a poor final representation. v0.3 uses a morphology graph only at **design time**, then compiles it into algebraic selectors and reusable generators.

## 9. Why not one giant neural/procedural network?

A learned network/CPPN could generate complex forms, but shipping weights/topology/evaluation code is incompatible with the target budget and would weaken human/agent reasoning about specific morphology controls.

The skill borrows CPPN's compositional-function lesson while keeping explicit compact formulas.

## 10. Derived design principles

The cross-source synthesis yields nine practical principles:

### P1. Genotype/phenotype separation
The expanded reasoning structure may be rich; the final code is its compressed indirect encoding.

### P2. Shared positional information
Use one coordinate language for many anatomical interpretations.

### P3. Rooted hierarchy
Every child has a parent/attachment law; avoid arbitrary global placement.

### P4. Organ families, not individual organs
One generator should create repeated siblings.

### P5. Repetition with variation
Combine residue identity with continuous body fields.

### P6. Local-frame inheritance
Child pose derives from parent phase/orientation.

### P7. Structure/material separation
Body plan and attachment should remain conceptually separate from folds/texture.

### P8. Hierarchical motion
Children inherit root motion before adding local phase.

### P9. Semantic-control locality
Readable controls should have predictable effects; test them before code golf destroys names/abstraction boundaries.

## 11. Capacity model for tweet-sized morphology

The final program has roughly 259 X-weighted characters available before `//#つぶやきProcessing`. This strongly favors **O(rules)** representation rather than **O(parts)** representation.

A useful compound organism usually has capacity for something like:

- one sampling/index scheme;
- one root body field;
- one regional selector/envelope;
- one repeated-family generator;
- one shared projection;
- one temporal law;
- perhaps one high-leverage surface deformation.

The exact count varies with formula/golf opportunities. The point is qualitative: each additional independent rule has substantial source cost, whereas an additional *instance generated by an existing rule* can cost almost nothing.

## 12. What v0.3 deliberately does not promise

v0.3 does **not** make arbitrary requested anatomy feasible within a tweet. It improves the frontier of controllable complexity by forcing factorization.

When a request needs many semantically independent parts that cannot share coordinates/generators, the correct behavior is to simplify the body plan while preserving its defining hierarchy—not to hide conventional multi-object code behind unreadable golf or exceed the limit.

## 13. Evaluation implications

A v0.3 benchmark should test more than visual density and length:

1. **body-plan recognition** — root/secondary/tertiary hierarchy is visible;
2. **attachment coherence** — children stay connected while the root moves;
3. **family reuse** — repeated anatomy comes from one generator;
4. **variation quality** — repeated parts are related, not exact clones or random;
5. **control locality** — changing a local readable control changes the intended region more than unrelated anatomy;
6. **compression survival** — the morphology still reads after golf;
7. **tweet validity** — final weighted/raw length passes.