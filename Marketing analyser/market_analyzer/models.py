"""Data classes and enums shared across the project."""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple


class Scenario(Enum):
    """The three analysis cases (see scenarios.py for multipliers)."""
    CONSERVATIVE = "conservative"
    BASE = "base"
    OPTIMISTIC = "optimistic"


@dataclass(frozen=True)
class City:
    """One row of cities.csv."""
    city: str
    state: str
    tier: int
    population: float
    target_income_share: float
    avg_household_income: float
    rent_index: float
    competition_level: int
    infrastructure_score: float


@dataclass(frozen=True)
class BrandInputs:
    """Brand-specific assumptions (config.json or typed at runtime)."""
    aov: float
    conversion_rate: float
    footfall_rate: float
    setup_cost: float
    base_rent: float
    staff_cost: float
    fixed_opex: float


# (factor name, points earned, max points, one-line reason)
ScoreLine = Tuple[str, float, float, str]


@dataclass(frozen=True)
class CityResult:
    """All computed numbers for one city under one set of inputs."""
    city: City
    addressable_population: float
    annual_visitors: float
    revenue: float
    operating_cost: float
    net_profit: float
    payback_years: Optional[float]   # None means "Never"
    roi_pct: float
    feasibility: float
    score_breakdown: List[ScoreLine] = field(default_factory=list)
    rank: int = 0

    @property
    def is_profitable(self) -> bool:
        return self.net_profit > 0

    @property
    def payback_label(self) -> str:
        return "Never" if self.payback_years is None else f"{self.payback_years:.2f} yrs"
