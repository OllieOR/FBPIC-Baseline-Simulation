from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iteration = ts.iterations[-1]

z, uz = ts.get_particle(
    var_list=["z", "uz"],
    iteration=iteration,
    species="electrons"
)

z_um = z * 1.e6

print(f"Iteration: {iteration}")
print(f"Number of saved electrons: {len(z)}")
print(f"z range: {np.min(z_um):.3f} to {np.max(z_um):.3f} um")
print(f"u_z range: {np.min(uz):.3f} to {np.max(uz):.3f}")
print(f"Median u_z: {np.median(uz):.3f}")
print(f"95th percentile u_z: {np.percentile(uz, 95):.3f}")
print(f"99th percentile u_z: {np.percentile(uz, 99):.3f}")

fig, ax = plt.subplots(figsize=(10, 5))

ax.scatter(
    z_um,
    uz,
    s=4,
    alpha=0.35
)

ax.set_xlabel(r"$z$ ($\mu$m)")
ax.set_ylabel(r"$u_z = p_z/(m_e c)$")
ax.set_title(f"Electron longitudinal phase space at iteration {iteration}")

Path("figures/electrons").mkdir(parents=True, exist_ok=True)

plt.tight_layout()
plt.savefig(
    "figures/electrons/z_uz_phase_space_final.png",
    dpi=200
)

plt.show()
