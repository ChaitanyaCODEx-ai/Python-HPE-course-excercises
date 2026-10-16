"""Pure, individually testable formula functions (Section 6 of the vision doc)."""
from typing import Optional


def addressable_population(population: float, target_income_share: float) -> float:
    """Addressable population = population x target_income_share."""
    return population * target_income_share


def annual_visitors(addressable: float, footfall_rate: float) -> float:
    """Annual visitors = addressable population x footfall_rate."""
    return addressable * footfall_rate


def annual_revenue(visitors: float, conversion_rate: float, aov: float) -> float:
    """Annual revenue = visitors x conversion_rate x AOV."""
    return visitors * conversion_rate * aov


def annual_operating_cost(base_rent: float, rent_index: float,
                          staff_cost: float, fixed_opex: float) -> float:
    """Operating cost = (base_rent x rent_index) + staff_cost + fixed_opex."""
    return base_rent * rent_index + staff_cost + fixed_opex


def annual_net_profit(revenue: float, operating_cost: float) -> float:
    """Net profit = revenue - operating cost."""
    return revenue - operating_cost


def payback_period(setup_cost: float, net_profit: float) -> Optional[float]:
    """Payback (years) = setup_cost / net_profit; None ("Never") if profit <= 0."""
    if net_profit <= 0:
        return None
    return setup_cost / net_profit


def roi_percent(net_profit: float, setup_cost: float) -> float:
    """ROI (%) = net_profit / setup_cost x 100."""
    return net_profit / setup_cost * 100
