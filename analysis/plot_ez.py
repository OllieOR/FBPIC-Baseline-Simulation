import numpy as np
import matplotlib.pyplot as plt
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iteration = 1750

Ez, info = ts.get_field(
    field="E",
    coord="z",
    iteration=iteration,
    theta=0
)

Ez_GVm = Ez / 1e9
extent_um = np.asarray(info.imshow_extent) * 1e6

# Use a symmetric colour scale so positive and negative fields
# are represented equally.
field_limit = np.max(np.abs(Ez_GVm))

fig, ax = plt.subplots(figsize=(9, 4.5))

image = ax.imshow(
    Ez_GVm,
    extent=extent_um,
    origin="lower",
    aspect="auto",
    cmap="RdBu_r",
    vmin=-field_limit,
    vmax=field_limit
)

colourbar = fig.colorbar(image, ax=ax)
colourbar.set_label(r"$E_z$ (GV m$^{-1}$)")

time_fs = ts.t[ts.iterations == iteration][0] * 1e15

ax.set_xlabel(r"$z$ ($\mu$m)")
ax.set_ylabel(r"$r$ ($\mu$m)")
ax.set_title(
    f"Longitudinal electric field at {time_fs:.1f} fs "
    f"(iteration {iteration})"
)

fig.tight_layout()
fig.savefig("figures/ez_final_full_scale.png", dpi=300)
plt.show()
