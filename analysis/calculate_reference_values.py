import numpy as np
from scipy.constants import c, e, epsilon_0, m_e, pi


def calculate_reference_values(n_e):
    """Return plasma frequency, wavelength and cold field scale for density n_e."""
    omega_p = np.sqrt(n_e * e**2 / (m_e * epsilon_0))
    lambda_p = 2.0 * pi * c / omega_p
    E_0 = m_e * c * omega_p / e

    return omega_p, lambda_p, E_0


if __name__ == "__main__":
    n_e = 4.0e18 * 1.0e6  # cm^-3 -> m^-3
    omega_p, lambda_p, E_0 = calculate_reference_values(n_e)

    print(f"Electron density:       {n_e:.6e} m^-3")
    print(f"Plasma frequency:       {omega_p:.6e} rad/s")
    print(f"Plasma wavelength:      {lambda_p * 1e6:.4f} um")
    print(f"Wave-breaking field:    {E_0 / 1e9:.3f} GV/m")
