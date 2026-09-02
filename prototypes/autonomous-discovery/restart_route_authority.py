from __future__ import annotations

from contextlib import contextmanager
from typing import Dict, Iterable, Iterator, List

import core
import representations

# Scientific authority is explicit rather than inferred from the mutable route
# registry. #128 mechanically authorized family/sheet for exploratory sidecar
# generation only; it did not grant artistic reviewed-lineage authority.
REVIEWED_START_EVIDENCE_AUTHORIZED_ROUTES = ("recurrence", "orbit", "filament")
SIDECAR_EVIDENCE_AUTHORIZED_ROUTES = (
    "recurrence",
    "orbit",
    "filament",
    "family",
    "sheet",
)

# Backward-compatible name for callers that mean restart-sidecar generation.
EVIDENCE_AUTHORIZED_RESTART_ROUTES = SIDECAR_EVIDENCE_AUTHORIZED_ROUTES


def eligible_restart_routes(brief: Dict[str, object]) -> List[str]:
    active = list(brief.get("routes") or [])
    return [r for r in active if r in SIDECAR_EVIDENCE_AUTHORIZED_ROUTES]


@contextmanager
def restart_route_registry(routes: Iterable[str]) -> Iterator[None]:
    """Temporarily expose evidence-authorized restart route adapters.

    `orbit` intentionally remains outside the baseline representation registry.
    This registry helper covers exploratory sidecar generation; callers with a
    narrower authority surface (for example reviewed-start handoff) must enforce
    that boundary before entering it. Process-global baseline state is restored
    exactly on exit.
    """
    requested = set(routes)
    unsupported = sorted(requested - set(SIDECAR_EVIDENCE_AUTHORIZED_ROUTES))
    if unsupported:
        raise ValueError(f"route(s) lack restart sidecar evidence authority: {unsupported}")

    if "orbit" not in requested:
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
