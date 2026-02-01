# Global Clinical Data Normalizer

A production-grade Python library for normalizing disparate global clinical measurements (Weight & Height) into standardized formats for data analysis and health informatics applications.

## Purpose

In healthcare and clinical research, patient data arrives in numerous formats across different regions and systems. This utility handles the messy reality of user-generated and clinical data, solving common issues such as:

* **The "Decimal Feet Trap":** Correctly distinguishes "5.10 ft" (5 feet 1.2 inches) from "5' 10"" (5 feet 10.0 inches).
* **Composite Units:** Parses mixed units like "11st 6lb" or "5ft 11in".
* **Ambiguity Heuristics:** Infers units for raw numbers based on clinical reference ranges (e.g., "180" is treated as cm, "1.8" as meters).
* **International Support:** Handles localized units including Jin (China), Kan (Japan), and Arroba (Latin America).
* **Messy Input:** Handles common misspellings, typos, and informal notations.

## Features

### 1. Comprehensive Unit Support

| Unit Category | Supported Formats | Examples |
| :--- | :--- | :--- |
| **Kilograms** | kg, kgs, kilogram, kilo, 斤 (Chinese jin) | 70kg, 70 kilos, 70.5 kilo grams |
| **Pounds** | lb, lbs, pound | 150 lbs, 150 pounds, 150 |
| **Stones** | st, stone (with composite format) | 11st, 11 stone 6, 11-6, 12 stones |
| **Jin/Catty** | jin, catty, 斤 | 120 jin, 120斤, 100 catty |
| **Kan** | kan, 貫 | 10 kan, 10貫 |
| **Arroba** | arroba, @ | 2 arroba, 1@ |
| **Height** | cm, m, ft, in, composite | 180cm, 1.8m, 5'11", 5.5 ft |

### 2. Robust Parsing Logic

* **Misspelling tolerance:** Handles "killograms", "pount", "stonnes".
* **Prefix handling:** Strips noise like "weighs 70kg", "about 150 lbs", "~70 kilos", "Height: 5'9".
* **Case insensitive:** "70KG", "70kg", "70Kg" all work.
* **Flexible spacing:** "70kg", "70 kg", "70  kilograms".
* **Decimal support:** Handles "70.5kg", "11.5 stone", "5.5 ft".

### 3. Data Quality & Safety

* **Validation:** Rejects negative values and unreasonable extremes.
* **Error handling:** Clear ValueError messages for invalid inputs.
* **Safe mode:** Optional wrappers that return None instead of raising exceptions for batch processing.
* **Precision:** Uses international standard conversion factors.

## Project Structure

* `weight_normalizer.py`: Main library for weight logic (Classes & Regex).
* `height_normalizer.py`: Main library for height logic & heuristics.
* `make-test.py`: Unified edge case test runner (The Gauntlet).
* `make-run.py`: Interactive CLI for terminal usage.
* `README.md`: Documentation.

## Installation

No external dependencies required - uses only the Python standard library.

```bash
# Clone the repository
git clone <repository-url>
cd clinical-normalizer

```

## Quick Start

### Interactive CLI

To test the normalizer with manual input in your terminal:

```bash
python make-run.py

```

### Library Usage: Weight Normalization

Normalizes inputs to **US Pounds (lbs)**.

```python
from weight_normalizer import parse_weight_to_lbs

# Simple conversions
print(parse_weight_to_lbs("70kg"))          # Returns 154.32
print(parse_weight_to_lbs("11 stone 6"))    # Returns 160.0 (Composite)
print(parse_weight_to_lbs("120斤"))         # Returns 132.28 (International)

# Handles messy input
print(parse_weight_to_lbs("weighs about 70 kilos")) # Returns 154.32

```

### Library Usage: Height Normalization

Normalizes inputs to a tuple of **(Feet, Inches)**.

```python
from height_normalizer import parse_height_to_us, format_height

# The "Decimal Trap" Handling
# 5.5 ft is mathematically 5 feet and 6 inches (0.5 * 12)
print(parse_height_to_us("5.5 ft"))         # Returns (5, 6.0)

# Composite Handling
print(parse_height_to_us("5' 11\""))        # Returns (5, 11.0)

# Unitless Heuristics (Inferred based on human physiology)
print(parse_height_to_us("180"))            # Returns (5, 10.87) (Inferred CM)
print(parse_height_to_us("1.8"))            # Returns (5, 10.87) (Inferred Meters)

# Formatting Output
ft, ins = parse_height_to_us("180cm")
print(format_height(ft, ins))               # Returns "5' 10.87""

```

### Safe Mode (Batch Processing)

Use `_safe` functions for ETL pipelines where you want to skip errors rather than crash.

```python
from weight_normalizer import parse_weight_safe

# Returns None instead of raising ValueError
result = parse_weight_safe("invalid data")  # Returns None
result = parse_weight_safe("70kg")          # Returns 154.32

```

## Testing

The project maintains a comprehensive test suite covering edge cases, international units, and common data entry errors.

```bash
# Run the full edge-case gauntlet for both Height and Weight
python make-test.py

# Run specific module tests
python -m unittest weight_normalizer.py
python -m unittest height_normalizer.py

```

**Test Coverage Highlights:**

* **Weight:** "11st 6lb" (Composite), "100斤" (Unicode), "70 killograms" (Typos).
* **Height:** "5.9 ft" vs "5'9"", "180" (Unitless CM), "72 inches".
* **Safety:** Negative numbers, zero values, and unreasonable extremes.

## Implementation Details

### Height Logic: The "Decimal Trap"

Height data is notoriously difficult due to the ambiguity of decimal notation. This library applies a **Strict Priority Strategy**:

1. **Composite Pattern ("5'11"):** Highest priority. Treated as 5 ft + 11 inches.
2. **Explicit Metric ("180cm", "1.8m"):** Converted with scientific precision (1 inch = 2.54 cm).
3. **Decimal Feet ("5.11 ft"):** Treated mathematically. 0.11 ft * 12 = 1.32 inches.
4. **Inference Heuristics:** Used for unitless numbers based on standard human ranges (e.g., 50 < x < 300 is assumed to be cm).

### Weight Logic: Chain of Responsibility

Weight parsing uses a Token Normalization Map for O(1) unit lookups, followed by a multi-stage parser.

1. **Sanitization:** Remove prefixes and noise.
2. **Composite Check:** Look for "Stone + Pounds" pattern first.
3. **General Parse:** Extract number and unit string.
4. **Normalization:** Map unit string (e.g., "kgs", "kilo") to canonical factor.
5. **Validation:** Check constraints (e.g., pounds in a stone < 14).

## Conversion Reference

**Exact Conversion Factors used:**

* **KG_TO_LB:** 2.2046226218
* **ST_TO_LB:** 14.0
* **JIN_TO_LB:** 1.10231131 (Chinese jin, 500g)
* **KAN_TO_LB:** 8.267328 (Japanese kan, 3.75kg)
* **ARROBA_TO_LB:** 25.35316 (Spanish/Latin American)
* **CM_TO_INCH:** 0.3937007874

## Technical Highlights

For resume/portfolio presentations:

* **Regex Engineering:** Complex pattern matching for composite units.
* **Data Normalization:** Handles real-world messy clinical data.
* **Type Safety:** Full Python type hints.
* **International Standards:** Uses exact WHO/ISO conversion factors.
* **Error Handling:** Comprehensive validation and informative errors.

## License

MIT License - feel free to use in your projects.

## Contact

For questions or suggestions, please open an issue or contact the maintainer.
Built for production use in healthcare informatics and clinical research.

```

```
