import unittest
from height_normalizer import parse_height_to_us, format_height

class TestHeightNormalizer(unittest.TestCase):

    def test_composite_feet_inches(self):
        """Verifies standard 5'11 formats."""
        # 5' 10" -> (5, 10.0)
        self.assertEqual(parse_height_to_us("5'10"), (5, 10.0))
        self.assertEqual(parse_height_to_us("5ft 10"), (5, 10.0))
        self.assertEqual(parse_height_to_us("5-10"), (5, 10.0))
        self.assertEqual(parse_height_to_us("6 foot 2"), (6, 2.0))

    def test_metric_conversions(self):
        """Verifies precise CM and Meter math."""
        # 180 cm = 70.866 inches = 5' 10.87"
        ft, ins = parse_height_to_us("180cm")
        self.assertEqual(ft, 5)
        self.assertAlmostEqual(ins, 10.87, places=2)

        # 1.75 meters = 68.897 inches = 5' 8.9"
        ft, ins = parse_height_to_us("1.75m")
        self.assertEqual(ft, 5)
        self.assertAlmostEqual(ins, 8.89, places=1)

    def test_decimal_feet_trap(self):
        """Crucial: Ensures 5.5ft is 5'6\", NOT 5'5\"."""
        # 5.5 ft -> Half a foot is 6 inches
        self.assertEqual(parse_height_to_us("5.5 ft"), (5, 6.0))
        
        # 5.1 ft -> 0.1 * 12 = 1.2 inches
        ft, ins = parse_height_to_us("5.1 ft")
        self.assertEqual(ft, 5)
        self.assertAlmostEqual(ins, 1.2, places=2)

    def test_inches_only(self):
        """Verifies straight inch conversion."""
        # 70 inches = 5' 10"
        self.assertEqual(parse_height_to_us("70 inches"), (5, 10.0))
        self.assertEqual(parse_height_to_us("70\""), (5, 10.0))

    def test_heuristics_ambiguous(self):
        """Verifies logic when no units are provided."""
        # 180 -> CM range (5' 10.8")
        ft, ins = parse_height_to_us("180")
        self.assertEqual(ft, 5)
        self.assertAlmostEqual(ins, 10.87, places=2)

        # 1.8 -> Meter range (5' 10.8")
        ft, ins = parse_height_to_us("1.8")
        self.assertEqual(ft, 5) 
        self.assertAlmostEqual(ins, 10.87, places=2)

        # 6.0 -> Feet range
        self.assertEqual(parse_height_to_us("6"), (6, 0.0))

    def test_formatter(self):
        """Verifies display string generation."""
        self.assertEqual(format_height(5, 10.866), "5' 10.87\"")
        # Test rounding edge case (11.999 -> 12 -> Next foot)
        self.assertEqual(format_height(5, 11.999), "6' 0\"")

if __name__ == "__main__":
    unittest.main()
