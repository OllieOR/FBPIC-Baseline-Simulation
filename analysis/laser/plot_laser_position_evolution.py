from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import hilbert
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

selected_iterations = [500, 900, 1200, 1500, 1750]

laser_positions = []
laser_peaks = []

fig, axes = plt.subplots(
    len(selected_iterations),
    1,
    figsize=(10, 13)
)

for ax, iteration in zip(axes, selected_iterations):
    Ex, info = ts.get_field(
        iteration=iteration,
        field="E",
        coord="x",
        theta=0.0
    )

    # Average the two cells immediately adjacent to the axis
    centre = Ex.shape[0] // 2

    Ex_axis = 0.5 * (Ex[centre - 1, :] + Ex[centre, :])

    Ex_axis_TVm = Ex_axis / 1.e12

    # Construct the longitudinal coordinate
    z_min = info.imshow_extent[0]
    z_max = info.imshow_extent[1]

    z_um = np.linspace(z_min, z_max, Ex_axis.size) * 1.e6

    # Remove any constant offset before calculating the envelope
    Ex_axis_TVm = Ex_axis_TVm - np.mean(Ex_axis_TVm)

    # Analytic-signal envelope of the rapidly oscillating laser field
    envelope = np.abs(hilbert(Ex_axis_TVm))

    peak_index = np.argmax(envelope)

    laser_z = z_um[peak_index]
    peak_envelope = envelope[peak_index]

    laser_positions.append(laser_z)
    laser_peaks.append(peak_envelope)

    # Physical time corresponding to this iteration
    index = np.where(ts.iterations == iteration)[0][0]

    time_fs = ts.t[index] * 1.e15

    ax.plot(
        z_um,
        Ex_axis_TVm,
        linewidth=0.8,
        alpha=0.5,
        label=r"$E_x$"
    )

    ax.plot(
        z_um,
        envelope,
        linewidth=1.5,
        label="Envelope"
    )

    ax.axvline(
        laser_z,
        linestyle="--",
        linewidth=1
    )

    ax.set_title(
        f"Iteration {iteration} — {time_fs:.1f} fs"
    )

    ax.set_ylabel(
        r"$E_x$ (TV m$^{-1}$)"
    )

    ax.legend(
        loc="upper left"
    )

    print(
        f"Iteration {iteration:4d} | "
        f"time = {time_fs:6.2f} fs | "
        f"laser peak z = {laser_z:7.3f} um | "
        f"peak envelope = {peak_envelope:6.3f} TV/m"
    )

axes[-1].set_xlabel(
    r"$z$ ($\mu$m)"
)

fig.suptitle(
    "Evolution of the on-axis laser field and envelope",
    fontsize=14
)

Path("figures/laser").mkdir(parents=True, exist_ok=True)

plt.tight_layout()

plt.savefig(
    "figures/laser/laser_position_evolution.png",
    dpi=200
)

plt.show()
