"""
make-test.py: Unified Test Suite.

Runs a comprehensive battery of tests on both weight and height logic.
Checks for edge cases like the "Decimal Feet Trap" and "Composite Stones".
"""

import unittest
import sys
import importlib.util

# --- DYNAMIC IMPORT SETUP ---
def load_library(module_name, file_path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise FileNotFoundError
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError:
        print(f"[CRITICAL] Missing file: {file_path}")
        sys.exit(1)

weight_lib = load_library("weight-normalizer", "weight-normalizer.py")
height_lib = load_library("height-normalizer", "height-normalizer.py")

# --- TEST CLASSES ---

class TestClinicalLogic(unittest.TestCase):

    # --- WEIGHT TESTS ---
    
    def test_weight_metric(self):
        """Verifies KG to LBS conversion."""
        # 70kg is approx 154.32 lbs
        self.assertAlmostEqual(weight_lib.parse_weight_to_lbs("70kg"), 154.32, places=2)
        self.assertAlmostEqual(weight_lib.parse_weight_to_lbs("70 kgs"), 154.32, places=2)

    def test_weight_composite(self):
        """Verifies Stone + Pounds logic."""
        # 11st (154) + 6lb = 160.0
        self.assertEqual(weight_lib.parse_weight_to_lbs("11st 6lb"), 160.0)
        self.assertEqual(weight_lib.parse_weight_to_lbs("11-6"), 160.0)

    def test_weight_international(self):
        """Verifies Jin and Arroba."""
        # 100 Jin = ~110.23 lbs
        self.assertAlmostEqual(weight_lib.parse_weight_to_lbs("100 jin"), 110.23, places=2)
        # 2 Arroba = ~50.71 lbs
        self.assertAlmostEqual(weight_lib.parse_weight_to_lbs("2 arroba"), 50.71, places=2)

    # --- HEIGHT TESTS ---

    def test_height_decimal_trap(self):
        """CRITICAL: Ensures 5.5 ft is 5' 6", NOT 5' 5"."""
        # 5.5 ft -> 5 feet + 0.5 feet (6 inches)
        self.assertEqual(height_lib.parse_height_to_us("5.5 ft"), (5, 6.0))

    def test_height_composite(self):
        """Ensures 'Visual' notation works."""
        # 5' 11"
        self.assertEqual(height_lib.parse_height_to_us("5'11"), (5, 11.0))

    def test_height_inference(self):
        """Ensures unitless numbers are guessed correctly."""
        # 180 -> CM range -> ~5' 11"
        ft, ins = height_lib.parse_height_to_us("180")
        self.assertEqual(ft, 5)
        self.assertAlmostEqual(ins, 10.87, places=2)
        
        # 1.8 -> Meter range -> ~5' 11"
        ft, ins = height_lib.parse_height_to_us("1.8")
        self.assertEqual(ft, 5)

if __name__ == "__main__":
    print("Running Clinical Data Gauntlet...")
    unittest.main(verbosity=2)
