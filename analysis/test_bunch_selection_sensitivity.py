import numpy as np
from scipy.constants import c, e, m_e
from scipy.signal import hilbert
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")
iteration = ts.iterations[-1]

Ex, info = ts.get_field(
    iteration=iteration,
    field="E",
    coord="x",
    theta=0.0
)

centre = Ex.shape[0] // 2

Ex_axis = 0.5 * (Ex[centre - 1, :] + Ex[centre, :])

z_field_um = np.linspace(info.imshow_extent[0], info.imshow_extent[1], Ex_axis.size) * 1.e6

Ex_axis = Ex_axis - np.mean(Ex_axis)
envelope = np.abs(hilbert(Ex_axis))

laser_z_um = z_field_um[np.argmax(envelope)]

z, ux, uy, uz, w = ts.get_particle(
    var_list=["z", "ux", "uy", "uz", "w"],
    iteration=iteration,
    species="electrons"
)

z_um = z * 1.e6
xi_um = z_um - laser_z_um

gamma = np.sqrt(1.0 + ux**2 + uy**2 + uz**2)

energy_MeV = (gamma - 1.0) * m_e * c**2 / e / 1.e6


def bunch_metrics(xi_min, xi_max, uz_min):
    mask = (
        (xi_um >= xi_min)
        & (xi_um <= xi_max)
        & (uz >= uz_min)
    )

    energies = energy_MeV[mask]
    weights = w[mask]

    if len(energies) == 0:
        return np.nan, np.nan, np.nan, 0

    charge_pC = np.sum(weights) * e * 1.e12

    mean_energy = np.average(energies, weights=weights)

    variance = np.average((energies - mean_energy)**2, weights=weights)

    rms_spread = np.sqrt(variance)

    relative_spread = rms_spread / mean_energy * 100.0

    return charge_pC, mean_energy, relative_spread, len(energies)

print()
print("Momentum-cut sensitivity")
print()

print(
    "uz_min    "
    "Q (pC)    "
    "Mean E (MeV)    "
    "Rel. RMS (%)    "
    "Macroparticles"
)

for uz_min in [3.5, 4.0, 4.5, 5.0]:
    charge, mean_E, spread, count = bunch_metrics(
        -20.0,
        -14.0,
        uz_min
    )

    print(
        f"{uz_min:5.1f}    "
        f"{charge:7.3f}    "
        f"{mean_E:12.3f}    "
        f"{spread:11.2f}    "
        f"{count:14d}"
    )

print()
print("Spatial-window sensitivity")
print()

print(
    "xi range (um)        "
    "Q (pC)    "
    "Mean E (MeV)    "
    "Rel. RMS (%)    "
    "Macroparticles"
)

spatial_windows = [
    (-21.0, -14.0),
    (-20.0, -14.0),
    (-19.0, -14.0),
    (-20.0, -13.0),
    (-20.0, -15.0)
]

for xi_min, xi_max in spatial_windows:
    charge, mean_E, spread, count = bunch_metrics(
        xi_min,
        xi_max,
        4.0
    )

    print(
        f"{xi_min:5.1f} to {xi_max:5.1f}    "
        f"{charge:7.3f}    "
        f"{mean_E:12.3f}    "
        f"{spread:11.2f}    "
        f"{count:14d}"
    )
