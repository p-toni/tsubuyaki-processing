from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Iterable, Iterator, List

import core
import representations

# This is an evidence-authority boundary, not a generic inference from the
# representation registry. The spectral/restart line was confirmed only on
# recurrence, orbit, and filament. Keep this list explicit until new evidence
# authorizes another route class.
EVIDENCE_AUTHORIZED_RESTART_ROUTES = ("recurrence", "orbit", "filament")


def eligible_restart_routes(brief: Dict[str, object]) -> List[str]:
    active = list(brief.get("routes") or [])
    return [r for r in active if r in EVIDENCE_AUTHORIZED_RESTART_ROUTES]


@contextmanager
def restart_route_registry(routes: Iterable[str]) -> Iterator[None]:
    """Temporarily expose evidence-authorized experimental route adapters.

    `orbit` intentionally remains outside the baseline representation registry.
    Sidecar generation and reviewed-lineage execution may opt into it, but the
    process-global baseline registry is restored exactly on exit.
    """
    requested = set(routes)
    unsupported = sorted(requested - set(EVIDENCE_AUTHORIZED_RESTART_ROUTES))
    if unsupported:
        raise ValueError(f"route(s) lack restart evidence authority: {unsupported}")

    if "orbit" not in requested:
        # recurrence and filament are baseline registry members. Still fail
        # closed if that assumption drifts.
        missing = sorted(r for r in requested if r not in core.ROUTES)
        if missing:
            raise ValueError(f"authorized restart route(s) missing from runtime registry: {missing}")
        yield
        return

    from orbit_representation import register_orbit

    had_representation = "orbit" in representations.REPRESENTATIONS
    prior_representation = representations.REPRESENTATIONS.get("orbit")
    had_route = "orbit" in core.ROUTES
    prior_route = core.ROUTES.get("orbit")
    prior_checker = core.check_candidate
    had_flag = hasattr(core, "_orbit_checker_registered")
    prior_flag = getattr(core, "_orbit_checker_registered", None)

    register_orbit()
    try:
        missing = sorted(r for r in requested if r not in core.ROUTES)
        if missing:
            raise ValueError(f"authorized restart route(s) missing after registration: {missing}")
        yield
    finally:
        if had_representation:
            representations.REPRESENTATIONS["orbit"] = prior_representation
        else:
            representations.REPRESENTATIONS.pop("orbit", None)

        if had_route:
            core.ROUTES["orbit"] = prior_route
        else:
            core.ROUTES.pop("orbit", None)

        core.check_candidate = prior_checker
        if had_flag:
            core._orbit_checker_registered = prior_flag
        elif hasattr(core, "_orbit_checker_registered"):
            delattr(core, "_orbit_checker_registered")
