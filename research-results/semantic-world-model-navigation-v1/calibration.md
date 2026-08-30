# Semantic world-model navigation v1 — calibration result

Decision: **WORLD_MODEL_NOT_CALIBRATED**.

The target-agnostic global surrogate was trained on 5,760 generator states and evaluated on 1,536 fresh target-free states. It improved held-out descriptor MSE only 7.17% over a route/operator mean baseline, below the frozen 20% gate. Recurrence (+11.54%) and filament (+12.15%) generalized modestly, but orbit was worse than baseline (-15.27%).

Generic retrieval also failed: the actual nearest held-out state appeared in the surrogate-predicted top eight only 18.75% of the time. Predicted top-one did beat the candidate-set median 83.33% of the time, just below the 85% gate.

No semantic evaluation seed was consumed. The result rejects this **global raw-genome -> visual-state surrogate architecture**, not the broader learning/controller hypothesis.

Next hypothesis: learn local intervention effects instead — `current visual state + mathematical action -> delta visual state` — and preregister a fresh target-free action-ranking calibration before any semantic evaluation.
