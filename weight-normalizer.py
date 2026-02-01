"""
Global Weight Normalization Utility (Production Grade).

This module provides high-precision conversion from global weight units
to US Pounds (lbs). It features a multi-stage parser designed to handle
clinical messiness, composite units (stones/pounds), and international characters.

Complexity:
    - Lookup: O(1) average case via hash sets.
    - Parsing: O(N) where N is string length (Regex).
"""

import re
import warnings
from typing import Dict, Optional, Set, Union

# --- CONFIGURATION & CONSTANTS ---
# Precision: International Avoirdupois & Trade Standards
CONVERSION_FACTORS = {
    'kg': 2.2046226218,
    'lb': 1.0,
    'st': 14.0,
    'jin': 1.10231131,  # Mainland China Standard (500g)
    'kan': 8.267328,    # Historical Japanese
    'arroba': 25.35316  # Spanish/Portuguese Standard
}

# Thresholds for validation
MAX_REASONABLE_WEIGHT_LBS = 1500.0 
MAX_STONE_VAL = 100
MAX_POUNDS_IN_STONE = 14.0

def _normalize_unit_string(unit_raw: str) -> str:
    """
    Normalizes a raw unit string to a canonical key using O(1) set lookups.
    """
    u = unit_raw.lower().strip(' .')

    # 1. Kilograms
    if u in {'kg', 'kgs', 'kilogram', 'kilograms', 'kilo', 'kilos', 
             'kilo gram', 'kilogramme', 'kilog', 'kgram'}:
        return 'kg'

    # 2. Pounds
    if u in {'lb', 'lbs', 'pound', 'pounds', 'pount', 'pouds', 
             'lbses', 'poundes', 'lbse'}:
        return 'lb'

    # 3. Stones
    if u in {'st', 'sts', 'stone', 'stones', 'ston', 'stonnes'}:
        return 'st'

    # 4. Jin / Catty (Unified for Clinical Context)
    if u in {'jin', 'jins', 'jing', 'gin', '斤',
             'catty', 'catties', 'kati', 'katii', 'caty'}:
        return 'jin'

    # 5. Kan
    if u in {'kan', 'kans', '貫'}:
        return 'kan'

    # 6. Arroba
    if u in {'arroba', 'arrobas', 'arrobe', 'aroba', '@'}:
        return 'arroba'

    return u  # Return as-is if unrecognized (will fail later safely)


def parse_weight_to_lbs(input_str: Union[str, float, int]) -> float:
    """
    Parses complex weight strings into a float (lbs).
    
    Strategy:
    1. Sanitize input.
    2. Attempt Composite Parsing (Stones + Pounds).
    3. Attempt Simple Parsing (Number + Unit).
    4. Validate constraints.
    """
    if not input_str:
        raise ValueError("Input cannot be empty.")
        
    # Handle non-string inputs gracefully
    if isinstance(input_str, (float, int)):
        return float(input_str)

    # Pre-cleaning: Remove noise words
    s = str(input_str).lower().strip()
    s = re.sub(r'^(weighs?|about|approx|~|wt\.?|weight:?)\s*', '', s)
    
    # --- STRATEGY A: COMPOSITE UNITS (Stone + Lbs) ---
    # Patterns: "11st 6", "11 stone 6lbs", "11-6"
    # Note: We must check this BEFORE the general parser to avoid 
    # matching "11st" and ignoring the "6lbs".
    stone_composite_pattern = r'^(\d+(?:\.\d+)?)\s*(?:st|stone|s|-)\s*(\d+(?:\.\d+)?)(?:\s*lbs?)?$'
    
    composite_match = re.search(stone_composite_pattern, s)
    if composite_match:
        stones = float(composite_match.group(1))
        pounds = float(composite_match.group(2))
        
        # Clinical Validation
        if pounds >= MAX_POUNDS_IN_STONE:
            raise ValueError(f"Invalid composite weight: {pounds} lbs exceeds 1 stone.")
            
        return (stones * CONVERSION_FACTORS['st']) + pounds

    # --- STRATEGY B: STANDARD UNITS (Value + Unit) ---
    # Patterns: "70kg", "120jin", "150"
    # The regex allows for a number, optional space, and optional unit text.
    general_match = re.search(r'^(-?[0-9]+(?:\.[0-9]+)?)\s*([a-zA-Z斤貫@\s]+)?$', s)
    
    if not general_match:
        raise ValueError(f"Unparseable weight format: {input_str}")

    val = float(general_match.group(1))
    unit_raw = general_match.group(2)
    
    # Validation: Negative Weights
    if val < 0:
        raise ValueError("Weight cannot be negative.")

    # Determine Conversion Factor
    if unit_raw:
        canonical_unit = _normalize_unit_string(unit_raw)
        if canonical_unit in CONVERSION_FACTORS:
            factor = CONVERSION_FACTORS[canonical_unit]
        else:
            # Fallback: if unit is text but unknown (e.g., "70 gloops")
            # We treat this as an error to ensure data integrity.
            # However, if unit was just whitespace/empty, we default to lbs.
            if not unit_raw.strip():
                factor = 1.0
            else:
                # If strictly keeping "garbage in, error out":
                raise ValueError(f"Unknown unit: {unit_raw}")
    else:
        # Default to Pounds if no unit specified (e.g. "150")
        factor = 1.0

    result = val * factor

    # --- FINAL SAFETY CHECK ---
    if result > MAX_REASONABLE_WEIGHT_LBS:
        warnings.warn(f"Result {result:.1f} lbs is unusually high for human weight.")

    return result

def parse_weight_safe(input_str: str) -> Optional[float]:
    """Safe wrapper for batch processing (ETL pipelines). Returns None on failure."""
    try:
        return parse_weight_to_lbs(input_str)
    except (ValueError, TypeError, AttributeError):
        return None
