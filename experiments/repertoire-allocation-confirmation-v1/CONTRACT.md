# Decision contract

Authoritative run: the first pull-request-triggered `repertoire-allocation-confirmation-v1` workflow run whose excluded seed-9001 smoke passes.

Fresh outcomes remain sealed until all 120 route×seed blocks complete and the reducer produces the summary artifact.

`CONFIRMED` requires all four reducer gates:

1. complete hard-invariant rectangle;
2. primary one-sided 95% Student-t lower bound > 0;
3. every primary leave-one-route-out route mean > 0;
4. robustness one-sided 95% Student-t lower bound > 0.

Any failure yields `NOT_CONFIRMED`. There is no sequential stopping, outcome-driven seed replacement, route voting, or post-hoc threshold change.
