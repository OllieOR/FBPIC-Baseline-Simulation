from pathlib import Path

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

# The reconstructed slice has two cells immediately beside r = 0.
# Averaging them gives an estimate of the on-axis field.
middle = Ez.shape[0] // 2
Ez_axis = 0.5 * (Ez[middle - 1, :] + Ez[middle, :])

z_um = info.z * 1e6
Ez_axis_GVm = Ez_axis / 1e9

minimum_index = np.argmin(Ez_axis_GVm)
maximum_index = np.argmax(Ez_axis_GVm)

print(
    f"Minimum on-axis Ez: {Ez_axis_GVm[minimum_index]:.2f} GV/m "
    f"at z = {z_um[minimum_index]:.2f} um"
)

print(
    f"Maximum on-axis Ez: {Ez_axis_GVm[maximum_index]:.2f} GV/m "
    f"at z = {z_um[maximum_index]:.2f} um"
)

time_fs = ts.t[ts.iterations == iteration][0] * 1e15

fig, ax = plt.subplots(figsize=(9, 4.5))

ax.plot(z_um, Ez_axis_GVm, color="navy", linewidth=1.5)
ax.axhline(0, color="black", linewidth=0.8)

ax.fill_between(
    z_um,
    Ez_axis_GVm,
    0,
    where=Ez_axis_GVm < 0,
    color="royalblue",
    alpha=0.25,
    label=r"$E_z<0$: forward force on electrons"
)

ax.fill_between(
    z_um,
    Ez_axis_GVm,
    0,
    where=Ez_axis_GVm > 0,
    color="firebrick",
    alpha=0.20,
    label=r"$E_z>0$: backward force on electrons"
)

ax.set_xlabel(r"$z$ ($\mu$m)")
ax.set_ylabel(r"On-axis $E_z$ (GV m$^{-1}$)")
ax.set_title(
    f"On-axis longitudinal field at {time_fs:.1f} fs "
    f"(iteration {iteration})"
)

ax.grid(alpha=0.25)
ax.legend()
fig.tight_layout()

Path("figures/wake").mkdir(parents=True, exist_ok=True)
fig.savefig("figures/wake/ez_final_on_axis.png", dpi=300)
plt.show()
