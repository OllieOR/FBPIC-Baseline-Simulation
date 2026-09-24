import unittest

import numpy as np
from scipy.constants import c, e, m_e

from analysis.laser.analyse_laser_propagation import (
    matched_waist,
    measure_laser_snapshot,
    normalized_vector_potential,
)


class LaserPropagationTests(unittest.TestCase):
    def test_field_to_a0_conversion(self):
        wavelength = 0.8e-6
        expected_a0 = 4.0
        angular_frequency = 2.0 * np.pi * c / wavelength
        field = expected_a0 * m_e * c * angular_frequency / e

        self.assertAlmostEqual(
            normalized_vector_potential(field, wavelength), expected_a0
        )

    def test_baseline_matched_waist(self):
        waist = matched_waist(4.0e24, 4.0)

        self.assertTrue(np.isclose(waist, 10.63e-6, rtol=3.0e-3))

    def test_recovers_synthetic_gaussian_laser(self):
        wavelength = 0.8e-6
        expected_waist = 5.0e-6
        expected_a0 = 3.2
        x = np.linspace(-20.0e-6, 20.0e-6, 201)
        z = np.linspace(-20.0e-6, 20.0e-6, 1001)

        angular_frequency = 2.0 * np.pi * c / wavelength
        peak_field = expected_a0 * m_e * c * angular_frequency / e
        transverse_envelope = np.exp(-(x / expected_waist) ** 2)
        longitudinal_envelope = np.exp(-0.5 * (z / 4.0e-6) ** 2)
        carrier = np.cos(2.0 * np.pi * z / wavelength)
        field = (
            peak_field
            * transverse_envelope[:, np.newaxis]
            * longitudinal_envelope[np.newaxis, :]
            * carrier[np.newaxis, :]
        )

        result = measure_laser_snapshot(field, x, z, wavelength)

        self.assertTrue(
            np.isclose(result["spot_size"], expected_waist, rtol=2.0e-2)
        )
        self.assertTrue(np.isclose(result["peak_a0"], expected_a0, rtol=2.0e-2))
        self.assertAlmostEqual(result["laser_z"], 0.0, delta=0.15e-6)
        self.assertLess(result["edge_fluence_fraction"], 1.0e-8)


if __name__ == "__main__":
    unittest.main()
