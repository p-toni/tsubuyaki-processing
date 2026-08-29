from __future__ import annotations

"""Loader shim for capacity.py.

Stage-A field.py uses postponed annotations plus dataclasses. capacity.py deliberately
loads it under an experiment-specific module name; dataclasses expect that name to
already exist in sys.modules while the module executes. Register the already-normal
same-file import under that alias before loading capacity. This changes no field,
target, archive, metric, or reducer semantics.
"""

import sys

import field as frozen_field

sys.modules.setdefault("sampling_invariance_field", frozen_field)

import capacity


if __name__ == "__main__":
    capacity.main()
