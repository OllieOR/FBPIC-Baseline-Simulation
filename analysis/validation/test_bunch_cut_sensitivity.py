from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import e
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries(
    "diags/hdf5"
)

# Locates the propagation CSV relative to this script
csv_path = Path(__file__).resolve().parents[2] / "results/laser_propagation.csv"
laser_data = np.genfromtxt(csv_path, delimiter=",", names=True)

# Saves these checks in their own folder
output_dir = Path(__file__).resolve().parents[2] / "figures" / "validation" / "bunch_cut_sensitivity"
output_dir.mkdir(parents=True, exist_ok=True)

for iteration in (1450, 1500, 1750):

    # Matches the CSV row to the correct iteration
    matching_rows = laser_data[laser_data["iteration"] == iteration]

    if len(matching_rows) != 1:
        raise ValueError(f"Expected one CSV row for iteration {iteration}")

    laser_z_um = matching_rows["laser_z_um"][0]

    # Gets macroparticle information from the dataset
    z, ux, uy, uz, w = ts.get_particle(
        var_list=["z", "ux", "uy", "uz", "w"],
        iteration=iteration,
        species="electrons",
    )

    # Converts to a coordinate relative to the laser
    xi_um = z * 1.e6 - laser_z_um

    for uz_min in (4.0, 4.5, 5.0):

        bunch_mask = (
            (xi_um >= -20.0)
            & (xi_um <= -14.0)
            & (uz >= uz_min)
        )

        selected_weights = w[bunch_mask]
        charge_pC = np.sum(selected_weights) * e * 1.e12

        print(
            f"Iteration {iteration}, u_z cut {uz_min}: "
            f"{charge_pC:.3g} pC, "
            f"{selected_weights.size} macroparticles"
        )

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
        ax.set_title(f"Iteration {iteration}, u_z ≥ {uz_min}")
        ax.legend()

        fig.savefig(
            output_dir / f"bunch_phase_space_{iteration}_uz_{uz_min:.1f}.png",
            dpi=200,
        )
        plt.close(fig)

print(f"Figures saved to: {output_dir}")