"""
clinical-tool.py: The Master Utility.

This single script ties together the entire Clinical Normalization suite.
It handles the complex 'hyphenated-filename' imports and provides two modes:
1. INTERACTIVE: Accepts user input for Height/Weight.
2. TEST SUITE: Runs the full 'Gauntlet' of edge cases to verify logic.
"""

import sys
import unittest
import importlib.util

# --- PART 1: DYNAMIC IMPORTS (The "Glue") ---
# We must use importlib because 'weight-normalizer.py' has a hyphen.

def load_module(module_name, file_path):
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None:
            raise FileNotFoundError
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except FileNotFoundError:
        print(f"\n[CRITICAL ERROR] Could not find library file: '{file_path}'")
        print("Please ensure 'weight-normalizer.py' and 'height-normalizer.py' are in this folder.")
        sys.exit(1)

# Load the libraries
print("Loading libraries...", end="")
weight_lib = load_module("weight_normalizer", "weight-normalizer.py")
height_lib = load_module("height_normalizer", "height-normalizer.py")
print(" Done.\n")

# Aliases for easier usage
parse_weight = weight_lib.parse_weight_to_lbs
parse_height = height_lib.parse_height_to_us
format_height = height_lib.format_height


# --- PART 2: THE TEST SUITE (The "Quality Control") ---

class ClinicalGauntlet(unittest.TestCase):
    """The full battery of tests for both Height and Weight."""

    def test_weight_logic(self):
        # Standard
        self.assertAlmostEqual(parse_weight("70kg"), 154.32, places=2)
        # Composite (Stone + Lbs)
        self.assertEqual(parse_weight("11st 6lb"), 160.0)
        self.assertEqual(parse_weight("11-6"), 160.0)
        # International
        self.assertAlmostEqual(parse_weight("100 jin"), 110.23, places=2)
        # Typo tolerance
        self.assertAlmostEqual(parse_weight("70 killograms"), 154.32, places=2)

    def test_height_logic(self):
        # The "Decimal Trap" (5.5ft != 5'5")
        self.assertEqual(parse_height("5.5 ft"), (5, 6.0))
        # Composite
        self.assertEqual(parse_height("5'11"), (5, 11.0))
        # Unitless Inference
        self.assertEqual(parse_height("180"), (5, 10.86614173228346)) # cm inferred


# --- PART 3: INTERACTIVE CLI (The "User Interface") ---

def run_interactive():
    print("="*50)
    print("      INTERACTIVE CLINICAL CONVERTER")
    print("      Type 'q' to return to menu.")
    print("="*50)

    while True:
        print("\n--- NEW PATIENT ---")
        
        # 1. Weight Input
        w_in = input("Input Weight (e.g. 70kg, 11st6): ").strip()
        if w_in.lower() == 'q': return

        # 2. Height Input
        h_in = input("Input Height (e.g. 180cm, 5'11): ").strip()
        if h_in.lower() == 'q': return

        # 3. Process & Display
        try:
            # Convert
            w_val = parse_weight(w_in)
            h_val = parse_height(h_in)
            
            # Format
            h_fmt = format_height(*h_val)
            
            print(f"\n✅ OUTPUT:")
            print(f"   WEIGHT: {w_val:.2f} lbs")
            print(f"   HEIGHT: {h_fmt}")
            
        except ValueError as e:
            print(f"\n❌ ERROR: {e}")
            print("   Please check your formatting and try again.")

def run_tests():
    print("Running System Diagnostics...")
    # Load tests from the ClinicalGauntlet class defined above
    suite = unittest.TestLoader().loadTestsFromTestCase(ClinicalGauntlet)
    # Run them
    unittest.TextTestRunner(verbosity=2).run(suite)
    input("\nPress Enter to return to menu...")

# --- MAIN MENU ---

def main_menu():
    while True:
        print("\n" + "="*40)
        print("   CLINICAL DATA NORMALIZER: MAIN MENU")
        print("="*40)
        print("1. Run Interactive Tool (User Input)")
        print("2. Run Test Suite (Quality Check)")
        print("3. Exit")
        
        choice = input("\nSelect Option [1-3]: ").strip()
        
        if choice == '1':
            run_interactive()
        elif choice == '2':
            run_tests()
        elif choice == '3':
            print("Exiting.")
            sys.exit(0)
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting.")
