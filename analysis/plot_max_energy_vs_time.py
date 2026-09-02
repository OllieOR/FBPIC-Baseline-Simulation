from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, e, m_e
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iterations = ts.iterations
times_fs = ts.t * 1.e15

max_energies = []

for iteration in iterations:
    ux, uy, uz = ts.get_particle(
        var_list=["ux", "uy", "uz"],
        iteration=iteration,
        species="electrons"
    )

    # Some early snapshots may contain no particles satisfying u_z >= 1
    if len(uz) == 0:
        max_energies.append(np.nan)
        continue

    gamma = np.sqrt(1.0 + ux**2 + uy**2 + uz**2)

    energy_MeV = (gamma - 1.0) * m_e * c**2 / e / 1.e6

    max_energies.append(np.max(energy_MeV))

max_energies = np.array(max_energies)

print("Iteration    Time (fs)    Maximum energy (MeV)")

for iteration, time_fs, energy in zip(
    iterations,
    times_fs,
    max_energies
):
    print(
        f"{iteration:8d}    "
        f"{time_fs:8.2f}    "
        f"{energy:8.3f}"
    )

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    times_fs,
    max_energies,
    marker="o",
    markersize=3
)

ax.set_xlabel("Time (fs)")
ax.set_ylabel("Maximum electron kinetic energy (MeV)")
ax.set_title("Maximum saved-electron energy versus time")

ax.grid(alpha=0.25)

Path("figures").mkdir(exist_ok=True)

plt.tight_layout()

plt.savefig(
    "figures/max_electron_energy_vs_time.png",
    dpi=200
)

plt.show()
