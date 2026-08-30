#!/usr/bin/env python3
from __future__ import annotations

import json

import calibrate
import fast_grayscale_metric

# Transport/performance substitution only. validate_fast_grayscale_metric.py must pass first.
calibrate.metric = fast_grayscale_metric

print(json.dumps(calibrate.run(), indent=2, sort_keys=True))
