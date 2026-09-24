from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

# Locates the propagation CSV relative to this script
csv_path = Path(__file__).resolve().parents[2] / "results/laser_propagation.csv"

laser_data = np.genfromtxt(csv_path, delimiter=",", names=True)

for iteration in (1450, 1500):

    # Match the snapshot to the measured laser position.
    matching_rows = laser_data[laser_data["iteration"] == iteration]

    if len(matching_rows) != 1:
        raise ValueError(f"Expected one CSV row for iteration {iteration}")

    laser_z_um = matching_rows["laser_z_um"][0]

    z, uz, w = ts.get_particle(
        var_list=["z", "uz", "w"],
        iteration=iteration,
        species="electrons",
    )
    xi_um = z * 1.e6 - laser_z_um

    # Candidate bunch identified from the late high-momentum wake branch
    xi_min = -20.0
    xi_max = -14.0
    uz_min = 4.0

    bunch_mask = (
        (xi_um >= xi_min)
        & (xi_um <= xi_max)
        & (uz >= uz_min)
    )

    selected_weights = w[bunch_mask]
    weight_sum = np.sum(selected_weights)
    weight_median = np.median(selected_weights)
    weight_max = np.max(selected_weights)

    fig, ax = plt.subplots()
    ax.scatter(xi_um, uz, s=3, alpha=0.3)
    selected_points = ax.scatter(
        xi_um[bunch_mask],
        uz[bunch_mask],
        c=np.log10(selected_weights),
        cmap="viridis",
        vmin=0,
        vmax=6,
        s=12,
        label="Selected particles",
    )

    fig.colorbar(
        selected_points,
        ax=ax,
        label="log₁₀(macroparticle weight)",
    )
    ax.set_xlim(-25, -10)
    ax.set_xlabel("Position relative to laser, ξ (μm)")
    ax.set_ylabel("Longitudinal momentum, u_z")
    ax.legend()
    output_dir = Path(__file__).resolve().parents[2] / "figures" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"bunch_phase_space_{iteration}.png", dpi=200)

    print(
        f"Iteration {iteration}: "
        f"selected={selected_weights.size}, "
        f"weight sum={weight_sum:.3g}, "
        f"median weight={weight_median:.3g}, "
        f"maximum weight={weight_max:.3g}"
    )

plt.show()
