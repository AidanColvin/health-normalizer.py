"""
Unit tests for the Metric to Imperial Converter.

This module uses the standard 'unittest' library to validate the logic
of the convert_health_metrics function. It covers standard cases,
edge cases (zeros), and error handling (negative inputs).
"""

import unittest
from metric_to_imperial import convert_health_metrics

class TestHealthConverter(unittest.TestCase):
    """Defines test cases for the health metric conversion utility."""

    def test_standard_conversion(self):
        """Checks if standard inputs return the expected imperial values."""
        # Test Case: 70.5 kg (approx 155 lbs) and 178 cm (approx 5ft 10in)
        # We allow a small margin of error for floating point math if needed,
        # but our function rounds output, so we check exact matches.
        
        result = convert_health_metrics(weight_kg=70.5, height_cm=178.0)
        
        self.assertEqual(result['weight_lbs'], 155)
        self.assertEqual(result['weight_oz'], 6.8) # 155.42 lbs -> .42 * 16 = 6.72 -> rounds to 6.7/6.8 depending on float
        self.assertEqual(result['height_ft'], 5)
        self.assertEqual(result['height_in'], 10.1)

    def test_zero_input(self):
        """Checks if 0 input results in 0 output (mathematically correct)."""
        result = convert_health_metrics(weight_kg=0, height_cm=0)
        self.assertEqual(result['weight_lbs'], 0)
        self.assertEqual(result['height_ft'], 0)

    def test_negative_input_raises_error(self):
        """Ensures that negative physical measurements raise a ValueError."""
        # The function should refuse to process -50kg
        with self.assertRaises(ValueError):
            convert_health_metrics(weight_kg=-50, height_cm=180)

if __name__ == '__main__':
    unittest.main()
