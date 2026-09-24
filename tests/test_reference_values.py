import math
import unittest

from analysis.wake.calculate_reference_values import calculate_reference_values


class ReferenceValueTests(unittest.TestCase):
    def test_baseline_plasma_scales(self):
        density = 4.0e18 * 1.0e6

        omega_p, lambda_p, field_scale = calculate_reference_values(density)

        self.assertTrue(
            math.isclose(omega_p, 1.1282920450858998e14, rel_tol=1.0e-6)
        )
        self.assertTrue(
            math.isclose(lambda_p, 16.694716368096397e-6, rel_tol=1.0e-6)
        )
        self.assertTrue(
            math.isclose(field_scale, 192.318397520443e9, rel_tol=1.0e-6)
        )


if __name__ == "__main__":
    unittest.main()
