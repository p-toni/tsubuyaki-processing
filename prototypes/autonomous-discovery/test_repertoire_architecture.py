from __future__ import annotations

import math
import random

import pytest
from PIL import Image

from basin_identity import (
    BasinIdentity,
    PARTITIONS,
    same_anchor,
    same_trust_region,
    validate_partition,
)
from orbit_representation import ORBIT_SPEC
from phenotype_descriptors import (
    PhenotypeDescriptor,
    describe_frames,
    describe_images,
    niche_key,
)
from repertoire_archive import ArchiveEntry, RepertoireArchive
from representations import REPRESENTATIONS


def _seed_genomes():
    out = {route: spec.seed(random.Random(100 + i)) for i, (route, spec) in enumerate(REPRESENTATIONS.items())}
    out["orbit"] = ORBIT_SPEC.seed(random.Random(777))
    return out


def test_promoted_partitions_are_disjoint_and_exhaustive_for_all_five_routes():
    genomes = _seed_genomes()
    assert set(genomes) == set(PARTITIONS)
    for route, genome in genomes.items():
        validate_partition(route, genome)


def test_basin_lineage_is_explicit_while_anchor_tracks_structural_boundary():
    genome = _seed_genomes()["recurrence"]
    base = BasinIdentity.from_lineage("recurrence", "RS1", genome)

    local = dict(genome)
    local["f3"] *= 1.05
    assert same_anchor("recurrence", genome, local)
    assert same_trust_region("recurrence", genome, local)
    assert BasinIdentity.from_lineage("recurrence", "RS1", local) == base

    # Sampling resolution is not mathematical identity, although trust-region
    # exploitation freezes it for event-aligned causal comparison.
    resampled = dict(genome)
    resampled["samples"] += 1
    assert same_anchor("recurrence", genome, resampled)
    assert not same_trust_region("recurrence", genome, resampled)
    assert BasinIdentity.from_lineage("recurrence", "RS1", resampled) == base

    # Crossing an identity key changes structural-anchor metadata, but it does
    # not silently mint a new basin lineage. New basin creation is a search event.
    identity_jump = dict(genome)
    identity_jump["base_r"] *= 1.05
    assert not same_anchor("recurrence", genome, identity_jump)
    drifted_same_lineage = BasinIdentity.from_lineage("recurrence", "RS1", identity_jump)
    assert drifted_same_lineage.basin_id == base.basin_id == "RS1"
    assert drifted_same_lineage.anchor != base.anchor

    # Conversely, two explicitly distinct discovered basins may initially share
    # the same structural anchor; lineage identity still keeps them separate.
    sibling = BasinIdentity.from_lineage("recurrence", "RS2", genome)
    assert sibling.basin_id != base.basin_id
    assert sibling.anchor == base.anchor


def _ring(n=96, radius=30.0, dx=0.0, dy=0.0):
    return [
        (dx + radius * math.cos(2 * math.pi * i / n), dy + radius * math.sin(2 * math.pi * i / n))
        for i in range(n)
    ]


def _line(n=97, scale=1.0, dx=0.0, dy=0.0):
    return [(dx + scale * (i - (n - 1) / 2), dy) for i in range(n)]


def test_structural_descriptor_is_translation_and_scale_invariant():
    a = describe_frames([_ring()], intrinsic_dimension=1)
    b = describe_frames([_ring(radius=93, dx=120, dy=-47)], intrinsic_dimension=1)
    assert a.anisotropy == pytest.approx(b.anisotropy, abs=1e-12)
    assert a.central_void == pytest.approx(b.central_void, abs=1e-12)
    assert a.radial_cv == pytest.approx(b.radial_cv, abs=1e-12)
    assert a.angular_coverage == pytest.approx(b.angular_coverage, abs=1e-12)
    assert niche_key(a) == niche_key(b)


def test_niche_key_is_independent_of_representation_intrinsic_dimension_metadata():
    one_d = describe_frames([_ring()], intrinsic_dimension=1)
    two_d = describe_frames([_ring()], intrinsic_dimension=2)
    assert one_d.intrinsic_dimension != two_d.intrinsic_dimension
    assert niche_key(one_d) == niche_key(two_d)


def test_structural_descriptor_distinguishes_ring_from_axial_form():
    ring = describe_frames([_ring()], intrinsic_dimension=1)
    line = describe_frames([_line()], intrinsic_dimension=1)
    assert ring.anisotropy < 0.05
    assert line.anisotropy > 0.95
    assert ring.central_void > 0.90
    assert line.central_void < 0.30
    assert niche_key(ring) != niche_key(line)


def test_shape_motion_ignores_translation_scale_and_resampling_but_detects_deformation():
    base = _line(n=97)
    rigid = _line(n=997, scale=4.0, dx=100, dy=-40)
    bent = [(x, 18 * math.sin(x / 12.0)) for x, _ in base]
    invariant = describe_frames([base, rigid], intrinsic_dimension=1)
    deformed = describe_frames([base, bent], intrinsic_dimension=1)
    assert invariant.shape_motion < 0.02
    assert deformed.shape_motion > 0.05


def _support_image(value: int) -> Image.Image:
    image = Image.new("L", (64, 64), 9)
    pixels = image.load()
    for x in range(12, 52):
        y = 32 + int(round(8 * math.sin(x / 7.0)))
        for dy in (-1, 0, 1):
            pixels[x, y + dy] = value
    return image


def test_rendered_support_descriptor_ignores_foreground_intensity_above_threshold():
    faint = _support_image(40)
    bright = _support_image(240)
    a = describe_images([faint], intrinsic_dimension=1)
    b = describe_images([bright], intrinsic_dimension=1)
    assert a == b
    assert niche_key(a) == niche_key(b)


def test_rendered_support_shape_motion_is_zero_when_only_intensity_changes():
    faint = _support_image(40)
    bright = _support_image(240)
    descriptor = describe_images([faint, bright], intrinsic_dimension=1)
    assert descriptor.shape_motion == pytest.approx(0.0, abs=1e-12)


def _descriptor(anisotropy=0.2, void=0.2, motion=0.2):
    return PhenotypeDescriptor(
        intrinsic_dimension=1,
        anisotropy=anisotropy,
        central_void=void,
        radial_cv=0.3,
        angular_coverage=0.8,
        shape_motion=motion,
    )


def _entry(cid, route, basin, descriptor=None):
    return ArchiveEntry(cid, route, basin, descriptor or _descriptor())


def test_archive_preserves_route_strata_and_never_auto_replaces_incumbents():
    archive = RepertoireArchive(max_basins_per_route=2)
    a1 = _entry("A1", "family", "basin-a")
    a2 = _entry("A2", "family", "basin-a")
    b1 = _entry("B1", "family", "basin-b")
    c1 = _entry("C1", "family", "basin-c")
    sheet = _entry("S1", "sheet", "sheet-a")

    assert archive.insert(a1).accepted
    same_basin_decision = archive.insert(a2)
    assert same_basin_decision.review_required
    assert same_basin_decision.review_with == ("A1",)
    assert len(archive) == 1

    assert archive.insert(b1).accepted
    capacity = archive.insert(c1)
    assert capacity.review_required
    assert set(capacity.review_with) == {"A1", "B1"}
    assert len(archive) == 2

    # Same phenotype niche, different representation: independent stratum.
    assert archive.insert(sheet).accepted
    assert len(archive) == 3
    assert archive.summary()["automaticReplacement"] is False

    # Explicit reviewer decision can replace within the same route+niche only.
    archive.replace("A1", a2)
    assert archive.get("A2").basin_id == "basin-a"
    with pytest.raises(KeyError):
        archive.get("A1")


def test_archive_rejects_cross_niche_or_cross_route_replacement():
    archive = RepertoireArchive(max_basins_per_route=2)
    incumbent = _entry("A1", "family", "basin-a")
    assert archive.insert(incumbent).accepted

    different_niche = _entry("A2", "family", "basin-a", _descriptor(anisotropy=0.95))
    with pytest.raises(ValueError, match="same phenotype niche"):
        archive.replace("A1", different_niche)

    different_route = _entry("S1", "sheet", "sheet-a")
    with pytest.raises(ValueError, match="same route stratum"):
        archive.replace("A1", different_route)


def test_explicit_replacement_cannot_collapse_two_slots_to_the_same_basin():
    archive = RepertoireArchive(max_basins_per_route=2)
    assert archive.insert(_entry("A1", "family", "basin-a")).accepted
    assert archive.insert(_entry("B1", "family", "basin-b")).accepted

    duplicate_b = _entry("B2", "family", "basin-b")
    with pytest.raises(ValueError, match="already represented"):
        archive.replace("A1", duplicate_b)

    assert {e.basin_id for e in archive.entries()} == {"basin-a", "basin-b"}
