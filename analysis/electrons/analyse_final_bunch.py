from pathlib import Path

import matplotlib.pyplot as plt
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

laser_index = np.argmax(envelope)
laser_z_um = z_field_um[laser_index]

z, ux, uy, uz, w = ts.get_particle(
    var_list=["z", "ux", "uy", "uz", "w"],
    iteration=iteration,
    species="electrons"
)

z_um = z * 1.e6
xi_um = z_um - laser_z_um

gamma = np.sqrt(1.0 + ux**2 + uy**2 + uz**2)

energy_MeV = (gamma - 1.0) * m_e * c**2 / e / 1.e6

# Candidate bunch identified from the late high-momentum wake branch
xi_min = -20.0
xi_max = -14.0
uz_min = 4.0

bunch_mask = (
    (xi_um >= xi_min)
    & (xi_um <= xi_max)
    & (uz >= uz_min)
)

xi_bunch = xi_um[bunch_mask]
uz_bunch = uz[bunch_mask]
energy_bunch = energy_MeV[bunch_mask]
w_bunch = w[bunch_mask]

if len(energy_bunch) == 0:
    raise RuntimeError("No particles found inside bunch selection.")

saved_charge_pC = np.sum(w) * e * 1.e12
bunch_charge_pC = np.sum(w_bunch) * e * 1.e12

charge_fraction = bunch_charge_pC / saved_charge_pC * 100.0

mean_energy = np.average(energy_bunch, weights=w_bunch)

variance = np.average((energy_bunch - mean_energy)**2, weights=w_bunch)

rms_spread = np.sqrt(variance)

relative_rms_spread = rms_spread / mean_energy * 100.0

max_energy = np.max(energy_bunch)

n_bins = 50

weighted_counts, edges = np.histogram(
    energy_bunch,
    bins=n_bins,
    weights=w_bunch
)

bin_widths = np.diff(edges)

bin_centres = 0.5 * (edges[:-1] + edges[1:])

charge_per_MeV = weighted_counts * e * 1.e12 / bin_widths

peak_index = np.argmax(charge_per_MeV)
peak_energy = bin_centres[peak_index]

print(f"Iteration: {iteration}")
print(f"Laser peak position: {laser_z_um:.3f} um")
print()

print("Candidate bunch selection:")
print(f"{xi_min:.1f} <= xi <= {xi_max:.1f} um")
print(f"uz >= {uz_min:.1f}")
print()

print(f"Saved macroparticles:     {len(z)}")
print(f"Bunch macroparticles:     {len(energy_bunch)}")
print()

print(f"Saved-population charge:  {saved_charge_pC:.3f} pC")
print(f"Candidate bunch charge:   {bunch_charge_pC:.3f} pC")
print(f"Fraction of saved charge: {charge_fraction:.2f} %")
print()

print(f"Weighted mean energy:     {mean_energy:.3f} MeV")
print(f"Histogram peak energy:    {peak_energy:.3f} MeV")
print(f"Maximum bunch energy:     {max_energy:.3f} MeV")
print(f"Weighted RMS spread:      {rms_spread:.3f} MeV")
print(f"Relative RMS spread:      {relative_rms_spread:.2f} %")

fig, ax = plt.subplots(figsize=(10, 5))

ax.scatter(
    xi_um,
    uz,
    s=3,
    alpha=0.15,
    label="All saved electrons"
)

ax.scatter(
    xi_bunch,
    uz_bunch,
    s=5,
    alpha=0.5,
    label="Candidate bunch"
)

ax.axvline(
    0.0,
    linestyle="--",
    linewidth=1,
    label="Laser envelope peak"
)

ax.axvline(xi_min, linestyle=":", linewidth=1)
ax.axvline(xi_max, linestyle=":", linewidth=1)
ax.axhline(uz_min, linestyle=":", linewidth=1)

ax.set_xlabel(r"$\xi=z-z_{\rm laser}$ ($\mu$m)")

ax.set_ylabel(r"$u_z=p_z/(m_ec)$")

ax.set_title("Final electron phase space and candidate bunch selection")

ax.legend()

Path("figures/electrons").mkdir(parents=True, exist_ok=True)

plt.tight_layout()

plt.savefig("figures/electrons/final_bunch_selection.png", dpi=200)

plt.show()

fig, ax = plt.subplots(figsize=(9, 5))

ax.step(
    bin_centres,
    charge_per_MeV,
    where="mid"
)

ax.axvline(
    mean_energy,
    linestyle="--",
    linewidth=1,
    label=f"Weighted mean = {mean_energy:.2f} MeV"
)

ax.set_xlabel("Electron kinetic energy (MeV)")

ax.set_ylabel(r"$dQ/dE$ (pC MeV$^{-1}$)")

ax.set_title("Weighted energy spectrum of candidate wake bunch")

ax.legend()

plt.tight_layout()

plt.savefig("figures/electrons/final_bunch_energy_spectrum.png", dpi=200)

plt.show()
