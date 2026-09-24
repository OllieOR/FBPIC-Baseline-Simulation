from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import e
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iteration = ts.iterations[-1]

rho, info = ts.get_field(
    iteration=iteration,
    field="rho",
    theta=0.0
)

# Baseline plasma density
n0 = 4.e18 * 1.e6  # m^-3

# Electron charge density: rho_e = -e n_e
ne = -rho / e

ne_norm = ne / n0

print(f"Iteration: {iteration}")
print(f"Minimum n_e/n0: {np.nanmin(ne_norm):.3f}")
print(f"Maximum n_e/n0: {np.nanmax(ne_norm):.3f}")
print(f"Median n_e/n0:  {np.nanmedian(ne_norm):.3f}")
print(f"99th percentile: {np.nanpercentile(ne_norm, 99):.3f}")

extent_um = [value * 1.e6 for value in info.imshow_extent]

fig, ax = plt.subplots(figsize=(10, 5))

im = ax.imshow(
    ne_norm,
    extent=extent_um,
    origin="lower",
    aspect="auto"
)

cbar = fig.colorbar(im, ax=ax)
cbar.set_label(r"$n_e/n_0$")

ax.set_xlabel(r"$z\;(\mu\mathrm{m})$")
ax.set_ylabel(r"$r\;(\mu\mathrm{m})$")
ax.set_title(f"Electron density at iteration {iteration}")

Path("figures/wake").mkdir(parents=True, exist_ok=True)

plt.tight_layout()
plt.savefig(
    "figures/wake/electron_density_final_full_scale.png",
    dpi=200
)

plt.show()
