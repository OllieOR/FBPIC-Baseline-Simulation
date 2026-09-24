from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, e, m_e
from openpmd_viewer import OpenPMDTimeSeries

ts = OpenPMDTimeSeries("diags/hdf5")

# Locates the propagation CSV relative to this script
csv_path = Path(__file__).resolve().parents[2] / "results/laser_propagation.csv"

# Read the named columns from the laser-propagation CSV.
laser_data = np.genfromtxt(csv_path, delimiter=",", names=True)


for iteration in (1450, 1500, 1750):

#Gets the macroparticle data

    z, ux, uy, uz, w = ts.get_particle(
            var_list=["z", "ux", "uy", "uz", "w"],
            iteration=iteration,
            species="electrons",
        )

    #Assigns the iteration to rows in the CSV
    matching_rows = laser_data[laser_data["iteration"] == iteration]

    #Validation
    if len(matching_rows) != 1:
        raise ValueError(f"Expected one CSV row for iteration {iteration}")

    #Finds the laser position from the CSV data
    laser_z_um = matching_rows["laser_z_um"][0]

    #Finds position of emacroparticles relative to laser
    z_um = z * 1.e6
    xi_um = z_um - laser_z_um

    #Mask parameters
    xi_min = -20.0
    xi_max = -14.0
    uz_min = 4.0

    #Creates mask
    bunch_mask = (
            (xi_um >= xi_min)
            & (xi_um <= xi_max)
            & (uz >= uz_min)
        )

    #Use mask to find number of bunch macroparticles and bunch charge
    w_bunch = w[bunch_mask]

    selected_uz = uz[bunch_mask]

    bins = np.arange(4.0, selected_uz.max() + 0.25, 0.25)

    fig, axes = plt.subplots(
        2,
        1,
        figsize=(8, 6),
        sharex=True,
    )

    counts, _, _ = axes[0].hist(
        selected_uz,
        bins=bins,
        color="tab:blue",
        edgecolor="white",
    )

    charge_by_bin, _, _ = axes[1].hist(
        selected_uz,
        bins=bins,
        weights=w[bunch_mask] * e * 1e12,
        color="tab:orange",
        edgecolor="white",
    )

    axes[0].axvline(
        4.5,
        color="gray",
        linestyle="--",
        label=r"$u_z = 4.5$",
    )

    axes[1].axvline(
        4.5,
        color="gray",
        linestyle="--",
    )

    axes[0].set_ylabel("Macroparticles per bin")
    axes[1].set_ylabel("Charge per bin (pC)")
    axes[1].set_xlabel(r"Longitudinal momentum $u_z$")
    axes[0].legend()

    for ax in axes:
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)

    fig.suptitle(f"Candidate momentum distribution at iteration {iteration}")
    fig.tight_layout()
    fig.savefig(Path(__file__).resolve().parents[2] / "figures" / "validation" / "check_momentum_histogram" / f"candidate_momentum_histogram_{iteration}.png", dpi=200)

plt.show()