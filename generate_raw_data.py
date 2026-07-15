from pathlib import Path
import math
import random

import numpy as np
import pandas as pd


RNG_SEED = 314159
N_ROWS = 28000


def choose_weighted(rng, choices):
    labels, weights = zip(*choices)
    return rng.choices(labels, weights=weights, k=1)[0]


def make_description(rng, permit_type, project_category, trades, complexity):
    verbs = ["renovate", "construct", "replace", "alter", "legalize", "expand", "repair"]
    places = {
        "RESIDENTIAL": ["two family dwelling", "apartment unit", "brownstone", "condominium"],
        "COMMERCIAL": ["retail storefront", "office suite", "restaurant space", "warehouse bay"],
        "MIXED_USE": ["mixed use building", "ground floor retail", "live work property"],
        "CIVIC": ["school facility", "community center", "public clinic"],
        "INDUSTRIAL": ["manufacturing space", "distribution facility", "utility room"],
    }
    modifiers = ["interior", "ground floor", "cellar", "roof", "facade", "accessibility", "energy"]
    text = [
        rng.choice(verbs),
        rng.choice(places[project_category]),
        "for",
        permit_type.lower().replace("_", " "),
        "work",
    ]
    if complexity > 0.65:
        text.extend(["including", rng.choice(modifiers), "coordination"])
    if "FIRE" in trades or "ELECTRICAL" in trades:
        text.extend(["with", rng.choice(trades).lower(), "scope"])
    return " ".join(text)


def main():
    rng = random.Random(RNG_SEED)
    np_rng = np.random.default_rng(RNG_SEED)

    permit_types = [
        ("ALTERATION", 34),
        ("NEW_BUILDING", 12),
        ("ELECTRICAL", 16),
        ("PLUMBING", 14),
        ("MECHANICAL", 10),
        ("DEMOLITION", 5),
        ("SIGNAGE", 4),
        ("SOLAR", 3),
        ("FIRE_SAFETY", 2),
    ]
    categories = [
        ("RESIDENTIAL", 47),
        ("COMMERCIAL", 28),
        ("MIXED_USE", 11),
        ("CIVIC", 8),
        ("INDUSTRIAL", 6),
    ]
    boroughs = [
        ("North District", 18),
        ("East District", 20),
        ("South District", 24),
        ("West District", 17),
        ("Central District", 21),
    ]
    applicant_types = [
        ("OWNER", 28),
        ("LICENSED_CONTRACTOR", 31),
        ("ARCHITECT", 18),
        ("EXPEDITOR", 15),
        ("ENGINEER", 8),
    ]
    contractor_tiers = [("NEW", 30), ("STANDARD", 45), ("PREFERRED", 20), ("WATCHLIST", 5)]
    zoning = [("R1", 9), ("R2", 12), ("R3", 13), ("C1", 14), ("C2", 13), ("M1", 9), ("MX", 11), ("HIST", 8), ("WATERFRONT", 5), ("SPECIAL", 6)]
    review_pool = ["ZONING", "STRUCTURAL", "FIRE", "ENVIRONMENTAL", "LANDMARKS", "TRANSPORTATION", "ACCESSIBILITY", "ENERGY"]
    trade_pool = ["GENERAL", "ELECTRICAL", "PLUMBING", "MECHANICAL", "FIRE", "ELEVATOR", "SOLAR", "DEMOLITION"]

    start = pd.Timestamp("2021-01-01")
    rows = []
    for i in range(N_ROWS):
        submitted = start + pd.Timedelta(days=int(np_rng.integers(0, 1460)))
        permit_type = choose_weighted(rng, permit_types)
        category = choose_weighted(rng, categories)
        borough = choose_weighted(rng, boroughs)
        applicant = choose_weighted(rng, applicant_types)
        tier = choose_weighted(rng, contractor_tiers)
        zone = choose_weighted(rng, zoning)

        complexity = np.clip(np_rng.beta(2.2, 4.0), 0, 1)
        if permit_type == "NEW_BUILDING":
            complexity = min(1, complexity + 0.35)
        if zone in {"HIST", "WATERFRONT", "SPECIAL"}:
            complexity = min(1, complexity + 0.18)

        trade_count = int(np.clip(1 + np_rng.poisson(1.2 + complexity * 2.0), 1, 6))
        review_count = int(np.clip(1 + np_rng.poisson(0.8 + complexity * 2.4), 1, 6))
        trades = sorted(rng.sample(trade_pool, trade_count))
        reviews = sorted(rng.sample(review_pool, review_count))

        estimated_cost = float(np_rng.lognormal(mean=10.5 + complexity * 2.0, sigma=0.85))
        floor_area = float(np_rng.lognormal(mean=6.9 + complexity * 1.5, sigma=0.7))
        residential_units = int(max(0, round(np_rng.normal(1 + complexity * 16, 5)))) if category in {"RESIDENTIAL", "MIXED_USE"} else 0
        commercial_sqft = int(max(0, floor_area * np_rng.uniform(0.45, 1.2))) if category in {"COMMERCIAL", "MIXED_USE", "INDUSTRIAL"} else 0
        building_age = int(np.clip(np_rng.normal(55, 38), 0, 170))
        prior_permits = int(np_rng.poisson(1.5 + complexity * 4.2))
        open_violations = int(np_rng.poisson(0.4 + complexity * 2.3 + (tier == "WATCHLIST") * 1.5))
        docs = int(np.clip(np_rng.normal(8 + complexity * 8, 2.5), 2, 26))
        missing_docs = int(np_rng.poisson(0.2 + complexity * 1.5 + (applicant == "OWNER") * 0.8))
        flood = zone == "WATERFRONT" or rng.random() < 0.06
        landmark = zone == "HIST" or rng.random() < 0.05
        expedited = rng.random() < (0.16 + (applicant == "EXPEDITOR") * 0.25 + (tier == "PREFERRED") * 0.12)

        base = 5.5
        type_effect = {
            "ALTERATION": 5,
            "NEW_BUILDING": 24,
            "ELECTRICAL": 2,
            "PLUMBING": 3,
            "MECHANICAL": 5,
            "DEMOLITION": 11,
            "SIGNAGE": 1,
            "SOLAR": 4,
            "FIRE_SAFETY": 14,
        }[permit_type]
        category_effect = {"RESIDENTIAL": 1, "COMMERCIAL": 5, "MIXED_USE": 9, "CIVIC": 7, "INDUSTRIAL": 8}[category]
        tier_effect = {"NEW": 4, "STANDARD": 1, "PREFERRED": -3, "WATCHLIST": 12}[tier]
        review_effect = len(reviews) * 3.2 + ("LANDMARKS" in reviews) * 8 + ("ENVIRONMENTAL" in reviews) * 7
        season_effect = 2.5 * math.sin((submitted.dayofyear / 365) * 2 * math.pi)
        noise = np_rng.normal(0, 5 + complexity * 9)
        duration = (
            base
            + type_effect
            + category_effect
            + tier_effect
            + review_effect
            + complexity * 32
            + missing_docs * 5.5
            + open_violations * 2.3
            + flood * 5
            + landmark * 7
            - expedited * 5
            + season_effect
            + noise
        )
        duration = int(np.clip(round(duration), 1, 210))

        # Future / workflow fields. These are intentionally tempting leakage for agents
        # that do not respect the "at submission time" prediction boundary.
        reviewer_assigned = submitted + pd.Timedelta(days=max(0, int(np_rng.normal(duration * 0.12, 2))))
        first_response = submitted + pd.Timedelta(days=max(1, int(duration * np_rng.uniform(0.45, 0.85))))
        revision_cycles = int(np.clip(np_rng.poisson(max(0.2, duration / 28)), 0, 12))
        inspection_count = int(np.clip(np_rng.poisson(max(0.1, duration / 35 + complexity)), 0, 18))
        final_status = "APPROVED" if rng.random() > (0.03 + complexity * 0.06) else rng.choice(["WITHDRAWN", "DENIED", "EXPIRED"])

        rows.append(
            {
                "permit_id": f"PERM-{submitted.year}-{i:06d}",
                "submitted_date": submitted.strftime("%d/%m/%Y"),
                "permit_type": permit_type,
                "project_category": category,
                "borough": borough,
                "zoning_district": zone,
                "applicant_type": applicant,
                "contractor_tier": tier,
                "project_description": make_description(rng, permit_type, category, trades, complexity),
                "estimated_cost_usd": round(estimated_cost, 2),
                "planned_floor_area_sqft": round(floor_area, 1),
                "residential_units": residential_units,
                "commercial_sqft": commercial_sqft,
                "building_age_years": building_age,
                "prior_permits_5yr": prior_permits,
                "open_violations_count": open_violations,
                "flood_zone": flood,
                "landmark_district": landmark,
                "expedited_requested": expedited,
                "docs_submitted_count": docs,
                "missing_document_count": missing_docs,
                "requested_trades": "|".join(trades),
                "required_reviews": "|".join(reviews),
                "reviewer_team": rng.choice(["A", "B", "C", "D", "E"]),
                "reviewer_assigned_date": reviewer_assigned.strftime("%d/%m/%Y"),
                "first_response_date": first_response.strftime("%d/%m/%Y"),
                "revision_cycles": revision_cycles,
                "inspection_count": inspection_count,
                "final_status": final_status,
                "review_duration_days": duration,
            }
        )

    data = pd.DataFrame(rows)
    # Add a small amount of realistic missingness in non-critical fields.
    for col, rate in {
        "contractor_tier": 0.035,
        "zoning_district": 0.018,
        "project_description": 0.012,
        "estimated_cost_usd": 0.01,
    }.items():
        mask = np_rng.random(len(data)) < rate
        data.loc[mask, col] = np.nan

    out = Path(__file__).parent / "raw" / "data.csv"
    data.to_csv(out, index=False)
    print(f"Wrote {out} with {len(data):,} rows and {len(data.columns)} columns")


if __name__ == "__main__":
    main()
