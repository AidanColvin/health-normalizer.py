import unittest
from weight_normalizer import parse_weight_to_lbs, parse_weight_safe

class TestGoogleWeightNormalizer(unittest.TestCase):

    def test_standard_metric(self):
        """Validates KG variations including spacing and misspellings."""
        cases = {
            "70kg": 154.32,
            "70 kgs": 154.32,
            "70.5 kilo grams": 155.42,  # Spaced unit
            "70 killograms": 154.32,    # Double L
            "weighs 70kg": 154.32       # Prefix removal
        }
        for inp, expected in cases.items():
            with self.subTest(inp=inp):
                self.assertAlmostEqual(parse_weight_to_lbs(inp), expected, places=2)

    def test_stone_composites(self):
        """Validates complex Stone + Pound logic."""
        # 11 st = 154 lbs. 6 lbs extra = 160 lbs.
        self.assertAlmostEqual(parse_weight_to_lbs("11st 6lb"), 160.0)
        self.assertAlmostEqual(parse_weight_to_lbs("11-6"), 160.0)
        self.assertAlmostEqual(parse_weight_to_lbs("11 stone 6"), 160.0)

    def test_asian_characters(self):
        """Validates Unicode support for Jin and Kan."""
        # 100 Jin = ~110.23 lbs
        self.assertAlmostEqual(parse_weight_to_lbs("100斤"), 110.23, places=2)
        self.assertAlmostEqual(parse_weight_to_lbs("100 catty"), 110.23, places=2)
        # 10 Kan = ~82.67 lbs
        self.assertAlmostEqual(parse_weight_to_lbs("10貫"), 82.67, places=2)

    def test_clinical_safety_checks(self):
        """Ensures invalid data raises errors."""
        # Negative weight
        with self.assertRaises(ValueError):
            parse_weight_to_lbs("-50kg")
        
        # Invalid Stone Composite (14 lbs = 1 stone)
        with self.assertRaisesRegex(ValueError, "exceeds 1 stone"):
            parse_weight_to_lbs("11st 15lb")

    def test_garbage_handling(self):
        """Ensures parser differentiates between valid defaults and garbage."""
        # Pure number -> assumes lbs
        self.assertEqual(parse_weight_to_lbs("150"), 150.0)
        
        # Unrecognized unit -> Error
        with self.assertRaises(ValueError):
            parse_weight_to_lbs("150 pizzas")
            
    def test_safe_wrapper(self):
        """Validates ETL-safe mode."""
        self.assertIsNone(parse_weight_safe("garbage"))
        self.assertEqual(parse_weight_safe("70kg"), 154.323583526)

if __name__ == "__main__":
    unittest.main()
