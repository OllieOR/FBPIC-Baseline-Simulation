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


def measure_candidate_bunch(z, ux, uy, uz, w, laser_z_um):
    # Position relative to the laser peak.
    z_um = z * 1.e6
    xi_um = z_um - laser_z_um

    # Kinetic energy from the three momentum components.
    gamma = np.sqrt(1.0 + ux**2 + uy**2 + uz**2)
    energy_MeV = (gamma - 1.0) * m_e * c**2 / e / 1.e6

    # Candidate bunch identified from the late high-momentum wake branch
    xi_min = -20.0
    xi_max = -14.0
    uz_min = 4.0

    # Apply the same selection at each saved iteration.
    bunch_mask = (
        (xi_um >= xi_min)
        & (xi_um <= xi_max)
        & (uz >= uz_min)
    )

    charge_by_cut = {}

    for uz_min in (4.5, 5.0):

        cut_mask = (
                (xi_um >= -20.0)
                & (xi_um <= -14.0)
                & (uz >= uz_min)
            )
        charge_by_cut[uz_min] = np.sum(w[cut_mask]) * e * 1.e12

    energy_bunch = energy_MeV[bunch_mask]
    w_bunch = w[bunch_mask]

    if np.sum(w_bunch) == 0:
        return len(w_bunch), 0.0, np.nan, np.nan, np.nan, 0.0, 0.0
    
    # The weights represent the number of electrons per macroparticle.
    bunch_charge_pC = np.sum(w_bunch) * e * 1.e12

    mean_energy_MeV = np.average(energy_bunch, weights=w_bunch)

    # Energy spread of the selected population.
    variance = np.average((energy_bunch - mean_energy_MeV)**2, weights=w_bunch)
    rms_spread = np.sqrt(variance)
    relative_rms_spread = rms_spread / mean_energy_MeV * 100.0
    max_energy_MeV = np.max(energy_bunch)
    bunch_macroparticles = len(w_bunch)

    return (
        bunch_macroparticles,
        bunch_charge_pC,
        mean_energy_MeV,
        relative_rms_spread,
        max_energy_MeV,
        charge_by_cut[4.5],
        charge_by_cut[5.0]
    )

# One value per saved iteration.
bunch_macroparticles_values = []
bunch_charge_pC_values = []
mean_energy_MeV_values = []
relative_rms_spread_values = []
max_energy_MeV_values = []
propagation_distance_values = []
initial_laser_z_um = laser_data["laser_z_um"][0]
spot_size_um_values = []
peak_a0_values = []
charge_by_cut_45_values = []
charge_by_cut_50_values = []


for iteration in ts.iterations:

    # Match the particle snapshot to its measured laser position.
    matching_rows = laser_data[laser_data["iteration"] == iteration]

    if len(matching_rows) != 1:
        raise ValueError(f"Expected one CSV row for iteration {iteration}")

    laser_z_um = matching_rows["laser_z_um"][0]
    spot_size_um = matching_rows["spot_size_um"][0]
    peak_a0 = matching_rows["peak_a0"][0]

    z, ux, uy, uz, w = ts.get_particle(
        var_list=["z", "ux", "uy", "uz", "w"],
        iteration=iteration,
        species="electrons",
    )

    results = measure_candidate_bunch(z, ux, uy, uz, w, laser_z_um)

    bunch_macroparticles = results[0]
    bunch_charge_pC = results[1]
    mean_energy_MeV = results[2]
    relative_rms_spread = results[3]
    max_energy_MeV = results[4]
    charge_by_cut_45 = results[5]
    charge_by_cut_50 = results[6]
    bunch_macroparticles_values.append(bunch_macroparticles)
    bunch_charge_pC_values.append(bunch_charge_pC)
    mean_energy_MeV_values.append(mean_energy_MeV)
    relative_rms_spread_values.append(relative_rms_spread)
    max_energy_MeV_values.append(max_energy_MeV)
    propagation_distance_values.append(laser_z_um - initial_laser_z_um)
    spot_size_um_values.append(spot_size_um)
    peak_a0_values.append(peak_a0)
    charge_by_cut_45_values.append(charge_by_cut_45)
    charge_by_cut_50_values.append(charge_by_cut_50)

    

bunch_macroparticles_values = np.asarray(bunch_macroparticles_values)
bunch_charge_pC_values = np.asarray(bunch_charge_pC_values)
mean_energy_MeV_values = np.asarray(mean_energy_MeV_values)
relative_rms_spread_values = np.asarray(relative_rms_spread_values)
max_energy_MeV_values = np.asarray(max_energy_MeV_values)
propagation_distance_values = np.asarray(propagation_distance_values)
spot_size_um_values = np.asarray(spot_size_um_values)
peak_a0_values = np.asarray(peak_a0_values)
charge_by_cut_45_values = np.asarray(charge_by_cut_45_values)
charge_by_cut_50_values = np.asarray(charge_by_cut_50_values)

fig, axes = plt.subplots(
    3,
    1,
    figsize=(8, 7),
    sharex=True,
)

axes[0].plot(
    propagation_distance_values,
    bunch_charge_pC_values,
    marker="o",
)

axes[0].set_ylabel("Selected charge (pC)")
axes[0].set_title("Candidate population: charge evolution")
axes[0].grid(alpha=0.25)

axes[1].plot(
    propagation_distance_values,
    mean_energy_MeV_values,
    marker="o",
)

axes[1].set_ylabel("Weighted mean energy (MeV)")
axes[1].set_title("Candidate population: mean energy evolution")
axes[1].grid(alpha=0.25)

axes[2].plot(
    propagation_distance_values,
    relative_rms_spread_values,
    marker="o",
)

axes[2].set_xlabel("Propagation distance (μm)")
axes[2].set_ylabel("Relative RMS spread (%)")
axes[2].set_title("Candidate population: energy spread evolution")
axes[2].grid(alpha=0.25)

fig.tight_layout()

output_path = Path(__file__).resolve().parents[2] / "figures" / "electrons" / "bunch_evolution.png"
output_path.parent.mkdir(parents=True, exist_ok=True)

fig.savefig(output_path, dpi=200)
print(f"Saved figure to: {output_path}")

# Compare the measured laser and selected charge on the same distance axis.
fig2, axes2 = plt.subplots(
    3,
    1,
    figsize=(8, 9),
    sharex=True,
)

axes2[0].plot(
    propagation_distance_values,
    spot_size_um_values,
    marker="o",
    label="Measured spot size",
)
axes2[0].axhline(
    spot_size_um_values[0],
    color="gray",
    linestyle=":",
    label="Initial measured spot size",
)
axes2[0].set_ylabel("Spot size (μm)")
axes2[0].set_title("Laser spot-size evolution with propagation distance")
axes2[0].grid(alpha=0.25)
axes2[0].legend()

axes2[1].plot(
    propagation_distance_values,
    peak_a0_values,
    marker="o",
    label="Measured peak a₀",
)
axes2[1].axhline(
    peak_a0_values[0],
    color="red",
    linestyle=":",
    label="Initial measured peak a₀",
)
axes2[1].set_ylabel("Peak a₀")
axes2[1].set_title("Laser amplitude evolution with propagation distance")
axes2[1].grid(alpha=0.25)
axes2[1].legend()

axes2[2].plot(
    propagation_distance_values,
    bunch_charge_pC_values,
    marker="o",
)
axes2[2].set_xlabel("Propagation distance (μm)")
axes2[2].set_ylabel("Selected charge (pC)")
axes2[2].set_title("Candidate population: charge evolution")
axes2[2].grid(alpha=0.25)

fig2.tight_layout()

comparison_path = (
    Path(__file__).resolve().parents[2]
    / "figures"
    / "electrons"
    / "laser_bunch_comparison.png"
)
comparison_path.parent.mkdir(parents=True, exist_ok=True)

fig2.savefig(comparison_path, dpi=200)
print(f"Saved figure to: {comparison_path}")

# A higher momentum cut must select no more charge than a lower cut.
if (
    np.any(charge_by_cut_45_values > bunch_charge_pC_values + 1.e-10)
    or np.any(charge_by_cut_50_values > charge_by_cut_45_values + 1.e-10)
):
    raise ValueError("Selected charge increased when the u_z cut was raised.")

fig3, ax3 = plt.subplots(figsize=(9, 5.5))

curves = (
    (bunch_charge_pC_values, 4.0, "tab:blue", "-", "o"),
    (charge_by_cut_45_values, 4.5, "tab:orange", "--", "s"),
    (charge_by_cut_50_values, 5.0, "tab:green", "-.", "^"),
)

for charge_values, uz_cut, color, line_style, marker in curves:
    # Zero charge is retained in the array but cannot appear on a log axis.
    visible_charge = np.where(charge_values > 0, charge_values, np.nan)

    ax3.plot(
        propagation_distance_values,
        visible_charge,
        color=color,
        linestyle=line_style,
        marker=marker,
        markersize=4,
        linewidth=2,
        label=rf"$u_z \geq {uz_cut:.1f}$",
    )

ax3.set_yscale("log")
ax3.set_xlabel("Laser propagation distance (μm)")
ax3.set_ylabel("Selected charge (pC)")
ax3.set_title("Candidate charge sensitivity to longitudinal momentum cut")
ax3.grid(which="major", alpha=0.25)
ax3.grid(which="minor", axis="y", alpha=0.1)
ax3.legend()

# Mark the snapshot where the difference between cuts is most striking.
index_1500 = np.flatnonzero(np.asarray(ts.iterations) == 1500)
if index_1500.size == 1:
    distance_1500 = propagation_distance_values[index_1500[0]]
    ax3.axvline(distance_1500, color="0.5", linestyle=":", linewidth=1)
    ax3.text(
        distance_1500 + 0.8,
        0.96,
        "iteration 1500",
        transform=ax3.get_xaxis_transform(),
        color="0.4",
        fontsize=9,
        va="top",
    )

fig3.tight_layout()

cut_path = (
    Path(__file__).resolve().parents[2]
    / "figures"
    / "electrons"
    / "charge_evolution_cutoff_comparison.png"
)
cut_path.parent.mkdir(parents=True, exist_ok=True)
fig3.savefig(cut_path, dpi=200)
print(f"Saved figure to: {cut_path}")

plt.show()