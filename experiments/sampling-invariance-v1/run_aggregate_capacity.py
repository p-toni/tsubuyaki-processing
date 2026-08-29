from __future__ import annotations

import sys

import field as frozen_field

sys.modules.setdefault("sampling_invariance_field", frozen_field)

import aggregate_capacity


if __name__ == "__main__":
    aggregate_capacity.main()
