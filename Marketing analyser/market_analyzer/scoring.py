"""Rule-based 100-point feasibility score (Section 7)."""
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from calculator import addressable_population
from models import City, ScoreLine

# Scoring weights (named constants; they sum to 100)
W_MARKET = 25.0
W_INCOME = 25.0
W_COMPETITION = 20.0
W_RENT = 15.0
W_INFRA = 15.0


@dataclass(frozen=True)
class DatasetContext:
    """Dataset-wide reference values used to scale scores."""
    max_addressable: float
    max_income: float
    min_rent_index: float


def build_context(cities: Sequence[City]) -> DatasetContext:
    return DatasetContext(
        max_addressable=max(addressable_population(c.population, c.target_income_share) for c in cities),
        max_income=max(c.avg_household_income for c in cities),
        min_rent_index=min(c.rent_index for c in cities),
    )


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def competition_points(level: int, max_pts: float = W_COMPETITION) -> float:
    """Level 1 -> 20, level 5 -> 4 (linear: 24 - 4 x level)."""
    return _clamp(24.0 - 4.0 * level, 4.0, 20.0) * max_pts / W_COMPETITION


def scaled_weights(weights=None) -> dict:
    """Max points per factor; custom weights are rescaled so they always total 100."""
    base = {"market": W_MARKET, "income": W_INCOME, "competition": W_COMPETITION,
            "rent": W_RENT, "infra": W_INFRA}
    if not weights:
        return base
    raw = {k: max(0.0, float(weights.get(k, base[k]))) for k in base}
    total = sum(raw.values())
    return base if total <= 0 else {k: v / total * 100 for k, v in raw.items()}


def score_city(city: City, ctx: DatasetContext, weights=None) -> Tuple[float, List[ScoreLine]]:
    """Return (total score 0-100, per-factor breakdown with reasons)."""
    w = scaled_weights(weights)
    addr = addressable_population(city.population, city.target_income_share)
    market_ratio = _clamp(addr / ctx.max_addressable, 0, 1)
    income_ratio = _clamp(city.avg_household_income / ctx.max_income, 0, 1)
    rent_ratio = _clamp(ctx.min_rent_index / city.rent_index, 0, 1)
    level = city.competition_level
    label = "low" if level <= 2 else "moderate" if level == 3 else "high"

    lines: List[ScoreLine] = [
        ("Market size", round(w["market"] * market_ratio, 1), w["market"],
         f"addressable population {addr:,.0f} is {market_ratio:.0%} of the largest city"),
        ("Income strength", round(w["income"] * income_ratio, 1), w["income"],
         f"avg household income {city.avg_household_income:,.0f} is {income_ratio:.0%} of the highest"),
        ("Competition", round(competition_points(level, w["competition"]), 1), w["competition"],
         f"{label} competition level {level}"),
        ("Rent affordability", round(w["rent"] * rent_ratio, 1), w["rent"],
         f"rent index {city.rent_index:.2f} vs lowest {ctx.min_rent_index:.2f} in dataset"),
        ("Infrastructure", round(city.infrastructure_score / 10 * w["infra"], 1), w["infra"],
         f"infrastructure score {city.infrastructure_score:g}/10"),
    ]
    total = _clamp(round(sum(line[1] for line in lines), 1), 0.0, 100.0)
    return total, lines
