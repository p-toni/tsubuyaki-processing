from __future__ import annotations

import json
import statistics

from field import (
    coefficient_dimension,
    coefficient_similarity,
    deterministic_subset,
    irregular_line_zero_samples,
    perturb_points,
    random_field,
    reconstruct_from_zero_points,
    reference_zero_cloud,
    regular_line_zero_samples,
    symmetric_chamfer,
)

BANDWIDTHS = (1, 2)
SEEDS = (91001, 91007, 91019, 91033)
NOISE_SIGMA = 1e-4


def main() -> None:
    cases = []
    noisy_min_errors = []
    noisy_2x_errors = []
    failures = []

    for bandwidth in BANDWIDTHS:
        dimension = coefficient_dimension(bandwidth)
        expected_dimension = (2 * bandwidth + 1) ** 2
        if dimension != expected_dimension:
            failures.append(f"K={bandwidth}: coefficient dimension mismatch")
        geometry_dof = dimension - 1

        for seed in SEEDS:
            source = random_field(bandwidth, seed)
            if source.coefficient_dof != dimension or source.geometry_dof != geometry_dof:
                failures.append(f"K={bandwidth} seed={seed}: DOF accounting mismatch")

            reference = reference_zero_cloud(source)
            scaled_reference = reference_zero_cloud(source.scaled(-3.7))
            scale_chamfer = symmetric_chamfer(reference, scaled_reference)
            if scale_chamfer > 1e-10:
                failures.append(
                    f"K={bandwidth} seed={seed}: scale invariance chamfer {scale_chamfer:.3e}"
                )

            samplers = {
                "regular-lines": regular_line_zero_samples(source),
                "irregular-lines": irregular_line_zero_samples(source, seed + 1000),
            }

            for sampler_name, observations in samplers.items():
                if len(observations) < 2 * geometry_dof:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"only {len(observations)} observations"
                    )
                    continue

                minimal = deterministic_subset(observations, geometry_dof, seed + 11)
                under = deterministic_subset(observations, geometry_dof - 1, seed + 13)
                oversampled = deterministic_subset(observations, 2 * geometry_dof, seed + 17)

                minimal_reconstruction = reconstruct_from_zero_points(bandwidth, minimal)
                under_reconstruction = reconstruct_from_zero_points(bandwidth, under)
                oversampled_reconstruction = reconstruct_from_zero_points(bandwidth, oversampled)

                minimal_similarity = coefficient_similarity(source, minimal_reconstruction.field)
                oversampled_similarity = coefficient_similarity(source, oversampled_reconstruction.field)

                if minimal_reconstruction.rank != geometry_dof:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"minimal rank={minimal_reconstruction.rank}, expected={geometry_dof}"
                    )
                if minimal_reconstruction.nullity != 1:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"minimal nullity={minimal_reconstruction.nullity}"
                    )
                if minimal_similarity < 0.999999:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"minimal similarity={minimal_similarity:.9f}"
                    )
                if under_reconstruction.nullity < 2:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"underdetermined nullity={under_reconstruction.nullity}"
                    )
                if oversampled_similarity < 0.999999:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"2x exact similarity={oversampled_similarity:.9f}"
                    )

                reconstructed_reference = reference_zero_cloud(oversampled_reconstruction.field)
                reconstruction_chamfer = symmetric_chamfer(reference, reconstructed_reference)
                if reconstruction_chamfer > 1e-6:
                    failures.append(
                        f"K={bandwidth} seed={seed} {sampler_name}: "
                        f"2x exact chamfer={reconstruction_chamfer:.3e}"
                    )

                noisy_min = perturb_points(minimal, NOISE_SIGMA, seed + 23)
                noisy_2x = perturb_points(oversampled, NOISE_SIGMA, seed + 29)
                noisy_min_reconstruction = reconstruct_from_zero_points(bandwidth, noisy_min)
                noisy_2x_reconstruction = reconstruct_from_zero_points(bandwidth, noisy_2x)
                noisy_min_similarity = coefficient_similarity(source, noisy_min_reconstruction.field)
                noisy_2x_similarity = coefficient_similarity(source, noisy_2x_reconstruction.field)

                noisy_min_errors.append(1.0 - noisy_min_similarity)
                noisy_2x_errors.append(1.0 - noisy_2x_similarity)

                cases.append(
                    {
                        "bandwidth": bandwidth,
                        "seed": seed,
                        "sampler": sampler_name,
                        "coefficientDimension": dimension,
                        "geometryDOF": geometry_dof,
                        "observationCount": len(observations),
                        "scaleChamfer": scale_chamfer,
                        "minimal": {
                            "rank": minimal_reconstruction.rank,
                            "nullity": minimal_reconstruction.nullity,
                            "coefficientSimilarity": minimal_similarity,
                        },
                        "under": {"nullity": under_reconstruction.nullity},
                        "exact2x": {
                            "coefficientSimilarity": oversampled_similarity,
                            "geometryChamfer": reconstruction_chamfer,
                        },
                        "noisy1x": {"coefficientSimilarity": noisy_min_similarity},
                        "noisy2x": {"coefficientSimilarity": noisy_2x_similarity},
                    }
                )

    noisy_2x_similarities = [1.0 - error for error in noisy_2x_errors]
    stable_density = {
        "noiseSigma": NOISE_SIGMA,
        "median1xError": statistics.median(noisy_min_errors),
        "median2xError": statistics.median(noisy_2x_errors),
        "median2xSimilarity": statistics.median(noisy_2x_similarities),
        "minimum2xSimilarity": min(noisy_2x_similarities),
    }

    if stable_density["median2xSimilarity"] < 0.999:
        failures.append(
            f"stable-density median 2x similarity={stable_density['median2xSimilarity']:.9f}"
        )
    if stable_density["minimum2xSimilarity"] < 0.99:
        failures.append(
            f"stable-density minimum 2x similarity={stable_density['minimum2xSimilarity']:.9f}"
        )
    if stable_density["median2xError"] >= stable_density["median1xError"]:
        failures.append("stable-density oversampling did not reduce median coefficient error")

    invariants = {
        "completeRectangle": len(cases) == len(BANDWIDTHS) * len(SEEDS) * 2,
        "exactAccounting": not any(
            "DOF accounting" in failure or "dimension mismatch" in failure
            for failure in failures
        ),
        "scaleInvariant": not any("scale invariance" in failure for failure in failures),
        "informationMinimum": not any(
            (
                "minimal rank" in failure
                or "minimal nullity" in failure
                or "minimal similarity" in failure
                or "underdetermined" in failure
            )
            for failure in failures
        ),
        "resamplingEquivalent": not any("2x exact" in failure for failure in failures),
        "stableDensity": not any("stable-density" in failure for failure in failures),
    }

    result = {
        "experiment": "sampling-invariance-v1",
        "stage": "A-excluded-smoke",
        "population": "excluded-synthetic",
        "bandwidths": list(BANDWIDTHS),
        "seeds": list(SEEDS),
        "cases": cases,
        "stableDensity": stable_density,
        "invariants": invariants,
        "failures": failures,
    }
    result["decision"] = (
        "STAGE_A_VALID"
        if invariants["completeRectangle"] and all(invariants.values()) and not failures
        else "STAGE_A_INVALID"
    )

    print(json.dumps(result, indent=2, sort_keys=True))
    if result["decision"] != "STAGE_A_VALID":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
