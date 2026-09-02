from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

selected_iterations = [500, 900, 1200, 1500, 1750]

fig, axes = plt.subplots(
    len(selected_iterations),
    1,
    figsize=(10, 14),
    sharey=True
)

for ax, iteration in zip(axes, selected_iterations):
    z, uz = ts.get_particle(
        var_list=["z", "uz"],
        iteration=iteration,
        species="electrons"
    )

    z_um = z * 1.e6

    # Find the physical time corresponding to this iteration
    index = np.where(ts.iterations == iteration)[0][0]
    time_fs = ts.t[index] * 1.e15

    ax.scatter(
        z_um,
        uz,
        s=2,
        alpha=0.25
    )

    ax.set_title(
        f"Iteration {iteration} — {time_fs:.1f} fs"
    )

    ax.set_ylabel(
        r"$u_z=p_z/(m_ec)$"
    )

    print(
        f"Iteration {iteration:4d} | "
        f"time = {time_fs:6.2f} fs | "
        f"saved particles = {len(uz):6d} | "
        f"max uz = {np.max(uz):6.3f}"
    )

axes[-1].set_xlabel(r"$z$ ($\mu$m)")

fig.suptitle(
    r"Evolution of electron longitudinal phase space "
    r"($u_z \geq 1$ saved population)",
    fontsize=14
)

Path("figures").mkdir(exist_ok=True)

plt.tight_layout()

plt.savefig(
    "figures/z_uz_phase_space_evolution.png",
    dpi=200
)

plt.show()
