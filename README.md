# Global Clinical Data Normalizer

A production-grade Python library for normalizing disparate global clinical measurements (Weight & Height) into standardized formats for data analysis and health informatics applications.

## Purpose

In healthcare and clinical research, patient data arrives in numerous formats across different regions and systems. This utility handles the messy reality of user-generated and clinical data, solving common issues such as:

* **The "Decimal Feet Trap":** Correctly distinguishes "5.10 ft" (5 feet 1.2 inches) from "5' 10"" (5 feet 10.0 inches).
* **Composite Units:** Parses mixed units like "11st 6lb" or "5ft 11in".
* **Ambiguity Heuristics:** Infers units for raw numbers based on clinical reference ranges (e.g., "180" is treated as cm, "1.8" as meters).
* **International Support:** Handles localized units including Jin (China), Kan (Japan), and Arroba (Latin America).
* **Messy Input:** Handles common misspellings, typos, and informal notations.

## Project Structure

All files are located in the root directory for ease of access and robust importing.

* `weight-normalizer.py`: Main library logic for weight conversion.
* `height-normalizer.py`: Main library logic for height conversion.
* `make-run.py`: Interactive CLI tool for manual data entry.
* `make-test.py`: Unified test suite for verifying logic.
* `README.md`: Documentation.

## Quick Start

### 1. Interactive Mode
To manually input patient data and see the conversion results in your terminal:

```bash
python make-run.py

```

### 2. Running Tests

To run the full battery of edge-case tests (The "Gauntlet") to verify the logic:

```bash
python make-test.py

```

## Features and Supported Units

### Weight Support

| Unit Category | Supported Formats | Examples |
| --- | --- | --- |
| **Kilograms** | kg, kgs, kilogram, kilo, 斤 (Chinese jin) | 70kg, 70 kilos, 70.5 kilo grams |
| **Pounds** | lb, lbs, pound | 150 lbs, 150 pounds, 150 |
| **Stones** | st, stone (with composite format) | 11st, 11 stone 6, 11-6, 12 stones |
| **Jin/Catty** | jin, catty, 斤 | 120 jin, 120斤, 100 catty |
| **Kan** | kan, 貫 | 10 kan, 10貫 |
| **Arroba** | arroba, @ | 2 arroba, 1@ |

### Height Support

| Unit Category | Supported Formats | Examples |
| --- | --- | --- |
| **Metric** | cm, m, meter | 180cm, 1.8m, 1.75 meters |
| **Imperial** | ft, in, feet, inches | 5'11", 5ft 10, 70 inches |
| **Decimal** | ft (mathematical) | 5.5 ft (Calculated as 5' 6") |

## Engineering Logic

### Height Logic: The "Decimal Trap"

Height data is notoriously difficult due to the ambiguity of decimal notation. This library applies a **Strict Priority Strategy**:

1. **Composite Pattern ("5'11"):** Highest priority. Treated as 5 ft + 11 inches.
2. **Explicit Metric ("180cm", "1.8m"):** Converted with scientific precision (1 inch = 2.54 cm).
3. **Decimal Feet ("5.11 ft"):** Treated mathematically. 0.11 ft * 12 = 1.32 inches.
4. **Inference Heuristics:** Used for unitless numbers based on standard human ranges (e.g., 50 < x < 300 is assumed to be cm).

### Weight Logic: Chain of Responsibility

Weight parsing uses a Token Normalization Map for O(1) unit lookups, followed by a multi-stage parser.

1. **Sanitization:** Remove prefixes ("weighs", "about") and noise.
2. **Composite Check:** Look for "Stone + Pounds" pattern first to avoid partial matches.
3. **General Parse:** Extract number and unit string using Regex.
4. **Normalization:** Map unit string to canonical factor.
5. **Validation:** Check constraints (e.g., pounds in a stone < 14).

## Developer Note on Imports

Because the library files use hyphens (e.g., `weight-normalizer.py`), they cannot be imported using standard Python `import` syntax.

To use these libraries in your own scripts, use `importlib`:

```python
import importlib.util

spec = importlib.util.spec_from_file_location("weight_lib", "weight-normalizer.py")
weight_lib = importlib.util.module_from_spec(spec)
spec.loader.exec_module(weight_lib)

# Usage
print(weight_lib.parse_weight_to_lbs("70kg"))

```

## License

MIT License. Built for production use in healthcare informatics and clinical research.

