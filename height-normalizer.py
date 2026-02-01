"""
Global Height Normalization Utility.

This module provides high-precision conversion from global height units
(cm, meters, decimal feet) to standardized US Customary Units (Feet & Inches).

Key Logic:
    - Distinguishes "5.11 ft" (Decimal) from "5'11" (Composite).
    - Handles Metric (1.8m, 180cm) conversions with floating point precision.
    - Normalizes "apostrophe/quote" notation (5' 10").
"""

import re
from typing import Tuple, Union, Optional

# --- CONSTANTS ---
# Exact scientific conversion factors
CM_TO_INCH = 0.3937007874
M_TO_INCH = 39.37007874

def parse_height_to_us(input_str: Union[str, float, int]) -> Tuple[int, float]:
    """
    Parses global height formats into US Standard (Feet, Inches).

    Returns:
        Tuple[int, float]: (Feet, Inches). 
        Example: 180cm -> (5, 10.87)
    
    Raises:
        ValueError: If input is unparseable or negative.
    """
    if not input_str:
        raise ValueError("Input cannot be empty.")

    # 1. Normalize String (Lower, strip, standardize separators)
    s = str(input_str).lower().strip()
    s = re.sub(r'^(height|ht\.?|h:?)\s*', '', s)  # Remove "ht: " prefixes
    
    # --- STRATEGY 1: COMPOSITE (Feet & Inches) ---
    # Matches: 5'11, 5' 11", 5ft 10, 5-11, 6 foot 2
    # Logic: Look for a "Feet" indicator followed immediately by a number
    composite_pattern = r"^(\d+)\s*(?:'|ft|feet|foot|-)\s*(\d+(?:\.\d+)?)\s*(?:\"|in|ins|inches)?$"
    match = re.search(composite_pattern, s)
    
    if match:
        feet = int(match.group(1))
        inches = float(match.group(2))
        
        # Validation: Inches shouldn't exceed 11.99 in composite mode
        if inches >= 12:
            raise ValueError(f"Invalid composite height: {inches} inches exceeds standard format.")
            
        return (feet, inches)

    # --- STRATEGY 2: METRIC (Meters & CM) ---
    
    # Case A: Centimeters (e.g., 175cm, 175 cms)
    cm_match = re.search(r"^(\d+(?:\.\d+)?)\s*(?:cm|cms|centimeters?)$", s)
    if cm_match:
        total_inches = float(cm_match.group(1)) * CM_TO_INCH
        return _inches_to_ft_in(total_inches)

    # Case B: Meters (e.g., 1.8m, 1.8 meters)
    m_match = re.search(r"^(\d+(?:\.\d+)?)\s*(?:m|meter|meters?)$", s)
    if m_match:
        total_inches = float(m_match.group(1)) * M_TO_INCH
        return _inches_to_ft_in(total_inches)

    # --- STRATEGY 3: DECIMAL FEET or INCHES ONLY ---
    
    # Case C: Inches Only (e.g., 72 inches, 72")
    in_match = re.search(r"^(\d+(?:\.\d+)?)\s*(?:\"|in|ins|inches?)$", s)
    if in_match:
        return _inches_to_ft_in(float(in_match.group(1)))

    # Case D: Decimal Feet (e.g., 5.9 ft)
    # DANGER: 5.9 ft is NOT 5'9". It is 5' 10.8"
    ft_match = re.search(r"^(\d+(?:\.\d+)?)\s*(?:'|ft|feet|foot)$", s)
    if ft_match:
        total_feet = float(ft_match.group(1))
        feet = int(total_feet)
        inches = (total_feet - feet) * 12.0
        return (feet, inches)

    # --- STRATEGY 4: AMBIGUOUS NUMBERS (Heuristics) ---
    # If passed just "180" or "1.75" or "5.9" without units.
    try:
        val = float(s)
        
        # Heuristic A: > 30 is likely Centimeters (Adult height)
        # (Shortest adult is ~54cm, tallest ~272cm)
        if 50 <= val <= 300: 
            # Treat as CM
            return _inches_to_ft_in(val * CM_TO_INCH)
            
        # Heuristic B: < 3.0 is likely Meters
        # (Most humans are 1.5 - 2.2 meters)
        if 0.5 <= val < 3.0:
            # Treat as Meters
            return _inches_to_ft_in(val * M_TO_INCH)

        # Heuristic C: 3.0 - 8.0 is likely Decimal Feet
        # (Most humans are 4 - 7 feet)
        if 3.0 <= val < 8.5:
             # Treat as Decimal Feet (Standard US assumption if small number)
             feet = int(val)
             inches = (val - feet) * 12.0
             return (feet, inches)
             
    except ValueError:
        pass

    raise ValueError(f"Could not parse height from: {input_str}")

def _inches_to_ft_in(total_inches: float) -> Tuple[int, float]:
    """Helper to convert total inches float to (ft, in) tuple."""
    feet = int(total_inches // 12)
    inches = total_inches % 12
    return (feet, inches)

def format_height(feet: int, inches: float) -> str:
    """Returns standardized string: 5' 11.5\" """
    # Round inches to 2 decimal places for display cleanup
    # Handle the edge case where rounding pushes 11.99 to 12.0
    if round(inches, 2) == 12.00:
        return f"{feet + 1}' 0\""
    return f"{feet}' {inches:.2f}\""
