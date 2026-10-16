"""CSV and JSON loading with validation (Section 13)."""
import csv
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from exceptions import (DataFileError, EmptyDatasetError, InvalidInputError,
                        MissingColumnError)
from models import BrandInputs, City

logger = logging.getLogger("analyzer")

REQUIRED_COLUMNS = ("city", "state", "tier", "population", "target_income_share",
                    "avg_household_income", "rent_index", "competition_level",
                    "infrastructure_score")
VALID_TIERS = {2, 3}


def normalize_name(name: str) -> str:
    """Collapse whitespace and title-case a city/state name."""
    return " ".join(name.split()).title()


def to_number(value: object, field: str, lo: Optional[float] = None,
              hi: Optional[float] = None, lo_inclusive: bool = True) -> float:
    """Parse a number and range-check it; raise InvalidInputError otherwise."""
    text = str(value).strip().replace(",", "")
    if text == "":
        raise InvalidInputError(f"{field} is empty")
    try:
        number = float(text)
    except ValueError:
        raise InvalidInputError(f"{field} must be a number, got {value!r}") from None
    if number != number or number in (float("inf"), float("-inf")):
        raise InvalidInputError(f"{field} must be a finite number")
    if lo is not None and (number < lo or (number == lo and not lo_inclusive)):
        op = ">=" if lo_inclusive else ">"
        raise InvalidInputError(f"{field} must be {op} {lo:g}, got {number:g}")
    if hi is not None and number > hi:
        raise InvalidInputError(f"{field} must be <= {hi:g}, got {number:g}")
    return number


def parse_city_row(row: Dict[str, str]) -> City:
    name = normalize_name(row["city"] or "")
    if not name:
        raise InvalidInputError("city name is empty")
    tier = int(to_number(row["tier"], "tier"))
    if tier not in VALID_TIERS:
        raise InvalidInputError(f"tier must be 2 or 3, got {tier}")
    return City(
        city=name,
        state=normalize_name(row["state"] or ""),
        tier=tier,
        population=to_number(row["population"], "population", 0, lo_inclusive=False),
        target_income_share=to_number(row["target_income_share"], "target_income_share", 0, 1),
        avg_household_income=to_number(row["avg_household_income"], "avg_household_income", 0),
        rent_index=to_number(row["rent_index"], "rent_index", 0, lo_inclusive=False),
        competition_level=int(to_number(row["competition_level"], "competition_level", 1, 5)),
        infrastructure_score=to_number(row["infrastructure_score"], "infrastructure_score", 1, 10),
    )


def load_cities(path: Union[str, Path]) -> List[City]:
    """Read cities.csv. Bad rows are skipped with a warning; structural problems raise."""
    path = Path(path)
    try:
        handle = path.open(newline="", encoding="utf-8-sig")
    except OSError as exc:
        raise DataFileError(f"Cannot read city file '{path}': {exc.strerror or exc}") from exc

    with handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise EmptyDatasetError(f"'{path}' is empty - add a header row and some cities.")
        headers = {h.strip() for h in reader.fieldnames if h}
        missing = [c for c in REQUIRED_COLUMNS if c not in headers]
        if missing:
            raise MissingColumnError(f"Missing required column(s): {', '.join(missing)}")

        cities: List[City] = []
        seen = set()
        for row_no, raw in enumerate(reader, start=2):
            row = {(k or "").strip(): (v or "") for k, v in raw.items()}
            try:
                city = parse_city_row(row)
            except InvalidInputError as exc:
                logger.warning("Row %d skipped: %s", row_no, exc)
                continue
            key = city.city.casefold()
            if key in seen:
                logger.warning("Row %d: duplicate city '%s' ignored (keeping first)", row_no, city.city)
                continue
            seen.add(key)
            cities.append(city)

    if not cities:
        raise EmptyDatasetError(f"No valid city rows found in '{path}'.")
    return cities


def validate_brand_inputs(raw: Dict[str, object]) -> BrandInputs:
    """Validate a dict of brand assumptions (from JSON or interactive prompts)."""
    keys = ("aov", "conversion_rate", "footfall_rate", "setup_cost",
            "base_rent", "staff_cost", "fixed_opex")
    missing = [k for k in keys if k not in raw]
    if missing:
        raise MissingColumnError(f"Missing brand input(s): {', '.join(missing)}")
    return BrandInputs(
        aov=to_number(raw["aov"], "aov", 0, lo_inclusive=False),
        conversion_rate=to_number(raw["conversion_rate"], "conversion_rate", 0, 1),
        footfall_rate=to_number(raw["footfall_rate"], "footfall_rate", 0, 1),
        setup_cost=to_number(raw["setup_cost"], "setup_cost", 0, lo_inclusive=False),
        base_rent=to_number(raw["base_rent"], "base_rent", 0),
        staff_cost=to_number(raw["staff_cost"], "staff_cost", 0),
        fixed_opex=to_number(raw["fixed_opex"], "fixed_opex", 0),
    )


def load_config(path: Union[str, Path]) -> BrandInputs:
    path = Path(path)
    try:
        with path.open(encoding="utf-8") as handle:
            raw = json.load(handle)
    except OSError as exc:
        raise DataFileError(f"Cannot read config file '{path}': {exc.strerror or exc}") from exc
    except json.JSONDecodeError as exc:
        raise InvalidInputError(f"Config file '{path}' is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise InvalidInputError("Config file must contain a JSON object")
    return validate_brand_inputs(raw)
