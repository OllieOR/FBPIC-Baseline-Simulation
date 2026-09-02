from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, e, m_e
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iteration = ts.iterations[-1]

ux, uy, uz, w = ts.get_particle(
    var_list=["ux", "uy", "uz", "w"],
    iteration=iteration,
    species="electrons"
)

gamma = np.sqrt(1.0 + ux**2 + uy**2 + uz**2)

energy_MeV = (gamma - 1.0) * m_e * c**2 / e / 1.e6

print(f"Iteration: {iteration}")
print(f"Saved macroparticles: {len(energy_MeV)}")
print(f"Minimum energy: {np.min(energy_MeV):.3f} MeV")
print(f"Maximum energy: {np.max(energy_MeV):.3f} MeV")

mean_energy = np.average(energy_MeV, weights=w)

variance = np.average((energy_MeV - mean_energy)**2, weights=w)

rms_energy = np.sqrt(variance)

print(f"Weighted mean energy: {mean_energy:.3f} MeV")
print(f"Weighted RMS spread: {rms_energy:.3f} MeV")

# Total charge represented by the saved particles
total_charge_pC = np.sum(w) * e * 1.e12

print(f"Total saved-particle charge: {total_charge_pC:.3f} pC")

n_bins = 80

weighted_counts, edges = np.histogram(
    energy_MeV,
    bins=n_bins,
    weights=w
)

bin_widths = np.diff(edges)
bin_centres = 0.5 * (edges[:-1] + edges[1:])

# Convert physical electron count to charge density in pC/MeV
charge_per_MeV = weighted_counts * e * 1.e12 / bin_widths

fig, ax = plt.subplots(figsize=(9, 5))

ax.step(
    bin_centres,
    charge_per_MeV,
    where="mid"
)

ax.set_xlabel("Electron kinetic energy (MeV)")
ax.set_ylabel(r"$dQ/dE$ (pC MeV$^{-1}$)")
ax.set_title(
    f"Weighted electron energy spectrum at iteration {iteration}"
)

Path("figures").mkdir(exist_ok=True)

plt.tight_layout()

plt.savefig(
    "figures/electron_energy_spectrum_final.png",
    dpi=200
)

plt.show()
