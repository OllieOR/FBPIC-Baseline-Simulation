import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

iterations = ts.iterations
times_fs = ts.t * 1.e15

ez_min = []
ez_max = []

for iteration in iterations:
    Ez, info = ts.get_field(
        iteration=iteration,
        field="E",
        coord="z",
        theta=0.0
    )

    # Average the two cells immediately adjacent to the axis
    centre = Ez.shape[0] // 2

    Ez_axis = 0.5 * (Ez[centre - 1, :] + Ez[centre, :])

    Ez_axis_GVm = Ez_axis / 1.e9

    ez_min.append(np.min(Ez_axis_GVm))
    ez_max.append(np.max(Ez_axis_GVm))

ez_min = np.array(ez_min)
ez_max = np.array(ez_max)

print(
    "Iteration    Time (fs)    "
    "Ez min (GV/m)    Ez max (GV/m)"
)

for iteration, time_fs, minimum, maximum in zip(
    iterations,
    times_fs,
    ez_min,
    ez_max
):
    print(
        f"{iteration:8d}    "
        f"{time_fs:8.2f}    "
        f"{minimum:13.2f}    "
        f"{maximum:13.2f}"
    )

fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    times_fs,
    ez_max,
    marker="o",
    markersize=3,
    label=r"$E_{z,\max}$"
)

ax.plot(
    times_fs,
    ez_min,
    marker="o",
    markersize=3,
    label=r"$E_{z,\min}$"
)

ax.axhline(
    0,
    linewidth=0.8
)

ax.set_xlabel("Time (fs)")
ax.set_ylabel(r"On-axis $E_z$ (GV m$^{-1}$)")
ax.set_title("On-axis longitudinal-field extrema versus time")

ax.legend()
ax.grid(alpha=0.25)

Path("figures").mkdir(exist_ok=True)

plt.tight_layout()

plt.savefig(
    "figures/ez_extrema_vs_time.png",
    dpi=200
)

plt.show()
