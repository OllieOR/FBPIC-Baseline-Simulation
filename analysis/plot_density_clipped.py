from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries
from scipy.constants import e

DIAGNOSTIC_PATH = "diags/hdf5"
ITERATION = 1750

# Background electron density
n_0 = 4.0e18 * 1.0e6  # cm^-3 -> m^-3

figure_directory = Path("figures")
figure_directory.mkdir(exist_ok=True)

ts = OpenPMDTimeSeries(DIAGNOSTIC_PATH)

rho, info = ts.get_field(
    field="rho",
    iteration=ITERATION,
    theta=0.0,
)

r = np.asarray(info.r)
z = np.asarray(info.z)

# Ensure array ordering is (r, z)
if rho.shape == (z.size, r.size):
    rho = rho.T
elif rho.shape != (r.size, z.size):
    raise ValueError(
        f"Unexpected rho shape {rho.shape}; "
        f"expected {(r.size, z.size)} or {(z.size, r.size)}."
    )

# Electron density normalised to the background density.
# This assumes rho is dominated by the electron charge density.
density_ratio = -rho / (e * n_0)

fig, ax = plt.subplots(figsize=(12, 6))

image = ax.imshow(
    density_ratio,
    extent=[
        z.min() * 1e6,
        z.max() * 1e6,
        r.min() * 1e6,
        r.max() * 1e6,
    ],
    origin="lower",
    aspect="auto",
    cmap="viridis",
    vmin=0.0,
    vmax=5.0,
)

colourbar = fig.colorbar(image, ax=ax, extend="max")
colourbar.set_label(r"$n_e/n_0$")

ax.set_xlabel(r"$z\;(\mu\mathrm{m})$")
ax.set_ylabel(r"$r\;(\mu\mathrm{m})$")
ax.set_title(
    rf"Electron density at iteration {ITERATION}, "
    rf"colour scale clipped to $0$--$5n_0$"
)

fig.tight_layout()

output_path = figure_directory / "electron_density_final_clipped_0_5n0.png"
fig.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"Maximum density in the complete data: {np.nanmax(density_ratio):.2f} n_0")
print(f"Saved clipped density figure to: {output_path}")

plt.show()
