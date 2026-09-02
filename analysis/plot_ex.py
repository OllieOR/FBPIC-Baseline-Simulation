from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iteration = ts.iterations[-1]

Ex, info = ts.get_field(
    iteration=iteration,
    field="E",
    coord="x",
    theta=0.0
)

Ex_TVm = Ex / 1.e12

extent_um = [value * 1.e6 for value in info.imshow_extent]

print(f"Iteration: {iteration}")
print(f"Minimum Ex: {np.min(Ex_TVm):.3f} TV/m")
print(f"Maximum Ex: {np.max(Ex_TVm):.3f} TV/m")
print(f"Peak |Ex|:  {np.max(np.abs(Ex_TVm)):.3f} TV/m")

fig, ax = plt.subplots(figsize=(10, 5))

limit = np.max(np.abs(Ex_TVm))

im = ax.imshow(
    Ex_TVm,
    extent=extent_um,
    origin="lower",
    aspect="auto",
    cmap="RdBu_r",
    vmin=-limit,
    vmax=limit
)

cbar = fig.colorbar(im, ax=ax)
cbar.set_label(r"$E_x$ (TV m$^{-1}$)")

ax.set_xlabel(r"$z$ ($\mu$m)")
ax.set_ylabel(r"transverse position ($\mu$m)")
ax.set_title(
    f"Transverse laser electric field at iteration {iteration}"
)

Path("figures").mkdir(exist_ok=True)

plt.tight_layout()
plt.savefig(
    "figures/ex_final_full_scale.png",
    dpi=200
)

plt.show()
