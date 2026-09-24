import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import c, e, epsilon_0, m_e, pi
from scipy.signal import hilbert


WAVELENGTH = 0.8e-6
INITIAL_WAIST = 5.0e-6
INITIAL_A0 = 4.0
PLATEAU_DENSITY = 4.0e18 * 1.0e6

RAMP_START = 30.0e-6
RAMP_END = 70.0e-6


def bandpass_laser_field(field, z, wavelength=WAVELENGTH):
    """Keep the longitudinal wavenumbers around the laser carrier."""
    dz = np.mean(np.diff(z))

    field = field - np.mean(field, axis=1, keepdims=True)
    spectrum = np.fft.rfft(field, axis=1)

    k = 2.0 * pi * np.fft.rfftfreq(z.size, d=abs(dz))
    k_0 = 2.0 * pi / wavelength

    laser_band = (k >= 0.5 * k_0) & (k <= 1.5 * k_0)
    spectrum[:, ~laser_band] = 0.0

    return np.fft.irfft(spectrum, n=z.size, axis=1)


def normalized_vector_potential(field_envelope, wavelength=WAVELENGTH):
    omega_0 = 2.0 * pi * c / wavelength
    return e * field_envelope / (m_e * c * omega_0)


def matched_waist(density, a0):
    omega_p = np.sqrt(density * e**2 / (epsilon_0 * m_e))
    k_p = omega_p / c
    return 2.0 * np.sqrt(a0) / k_p


def pulse_window(longitudinal_intensity, fraction=0.01):
    peak = np.argmax(longitudinal_intensity)
    threshold = fraction * longitudinal_intensity[peak]

    left = peak
    while left > 0 and longitudinal_intensity[left - 1] >= threshold:
        left -= 1

    right = peak
    while (
        right < longitudinal_intensity.size - 1
        and longitudinal_intensity[right + 1] >= threshold
    ):
        right += 1

    return slice(left, right + 1)


def measure_laser_snapshot(field, x, z, wavelength=WAVELENGTH):
    laser_field = bandpass_laser_field(field, z, wavelength)
    envelope = np.abs(hilbert(laser_field, axis=1))
    envelope_squared = envelope**2

    longitudinal_intensity = np.sum(envelope_squared, axis=0)
    window = pulse_window(longitudinal_intensity)

    # Integrate across the pulse before taking the transverse moment.
    transverse_fluence = np.sum(envelope_squared[:, window], axis=1)
    total_fluence = np.sum(transverse_fluence)

    x_centroid = np.sum(x * transverse_fluence) / total_fluence
    variance = (
        np.sum((x - x_centroid) ** 2 * transverse_fluence)
        / total_fluence
    )

    # For I proportional to exp(-2x^2/w^2), w = 2 sigma_x.
    spot_size = 2.0 * np.sqrt(variance)

    centre_indices = np.argsort(np.abs(x))[:2]
    field_axis = np.mean(laser_field[centre_indices, :], axis=0)
    envelope_axis = np.abs(hilbert(field_axis))

    peak_index = np.argmax(envelope_axis)
    peak_field = envelope_axis[peak_index]

    n_edge = max(1, int(np.ceil(0.1 * x.size)))
    edge_fluence = np.sum(transverse_fluence[:n_edge])
    edge_fluence += np.sum(transverse_fluence[-n_edge:])

    return {
        "laser_z": z[peak_index],
        "spot_size": spot_size,
        "peak_a0": normalized_vector_potential(peak_field, wavelength),
        "peak_field": peak_field,
        "transverse_centroid": x_centroid,
        "edge_fluence_fraction": edge_fluence / total_fluence,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--diagnostics", default="diags/hdf5")
    parser.add_argument("--show", action="store_true")
    args = parser.parse_args()

    from openpmd_viewer import OpenPMDTimeSeries

    ts = OpenPMDTimeSeries(args.diagnostics)

    rows = []

    for iteration, time_s in zip(ts.iterations, ts.t):
        Ex, info = ts.get_field(
            iteration=int(iteration),
            field="E",
            coord="x",
            theta=0.0,
        )

        x = np.linspace(
            info.imshow_extent[2],
            info.imshow_extent[3],
            Ex.shape[0],
        )
        z = np.linspace(
            info.imshow_extent[0],
            info.imshow_extent[1],
            Ex.shape[1],
        )

        result = measure_laser_snapshot(Ex, x, z)

        row = {
            "iteration": int(iteration),
            "time_fs": time_s * 1.0e15,
            "laser_z_um": result["laser_z"] * 1.0e6,
            "spot_size_um": result["spot_size"] * 1.0e6,
            "peak_a0": result["peak_a0"],
            "peak_field_TVm": result["peak_field"] / 1.0e12,
            "transverse_centroid_um": result["transverse_centroid"] * 1.0e6,
            "edge_fluence_fraction": result["edge_fluence_fraction"],
        }

        rows.append(row)

        print(
            f"Iteration {row['iteration']:4d} | "
            f"time = {row['time_fs']:7.2f} fs | "
            f"w = {row['spot_size_um']:6.3f} um | "
            f"peak a0 = {row['peak_a0']:6.3f}"
        )

    results_path = Path("results/laser_propagation.csv")
    results_path.parent.mkdir(exist_ok=True)

    with results_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    time_fs = np.array([row["time_fs"] for row in rows])
    laser_z_um = np.array([row["laser_z_um"] for row in rows])
    spot_size_um = np.array([row["spot_size_um"] for row in rows])
    peak_a0 = np.array([row["peak_a0"] for row in rows])

    matched_waist_um = matched_waist(
        PLATEAU_DENSITY,
        INITIAL_A0,
    ) * 1.0e6

    rayleigh_length_um = pi * (INITIAL_WAIST * 1.0e6) ** 2 / (
        WAVELENGTH * 1.0e6
    )

    propagation_distance_um = laser_z_um - laser_z_um[0]

    vacuum_waist_um = INITIAL_WAIST * 1.0e6 * np.sqrt(
        1.0 + (propagation_distance_um / rayleigh_length_um) ** 2
    )

    ramp_start_fs = np.interp(RAMP_START * 1.0e6, laser_z_um, time_fs)
    plateau_start_fs = np.interp(RAMP_END * 1.0e6, laser_z_um, time_fs)

    fig, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

    axes[0].plot(
        time_fs,
        spot_size_um,
        marker="o",
        markersize=3,
        label="Measured spot size",
    )

    axes[0].plot(
        time_fs,
        vacuum_waist_um,
        color="black",
        linestyle="-.",
        label="Vacuum diffraction",
    )

    axes[0].axhline(
        INITIAL_WAIST * 1.0e6,
        color="gray",
        linestyle="--",
        label="Input waist",
    )

    axes[0].axhline(
        matched_waist_um,
        color="tab:red",
        linestyle=":",
        label="Approx. plateau matched waist",
    )

    for ax in axes:
        ax.axvline(
            ramp_start_fs,
            color="tab:green",
            linestyle="--",
            linewidth=1,
        )
        ax.axvline(
            plateau_start_fs,
            color="tab:purple",
            linestyle="--",
            linewidth=1,
        )
        ax.grid(alpha=0.25)

    axes[0].text(
        ramp_start_fs,
        0.96,
        " Plasma starts",
        color="tab:green",
        rotation=90,
        va="top",
        transform=axes[0].get_xaxis_transform(),
    )

    axes[0].text(
        plateau_start_fs,
        0.96,
        " Plateau starts",
        color="tab:purple",
        rotation=90,
        va="top",
        transform=axes[0].get_xaxis_transform(),
    )

    axes[0].set_ylabel(r"$w$ ($\mu$m)")
    axes[0].legend()

    axes[1].plot(
        time_fs,
        peak_a0,
        marker="o",
        markersize=3,
    )

    axes[1].axhline(
        INITIAL_A0,
        color="gray",
        linestyle="--",
        label=r"Input $a_0$",
    )

    axes[1].set_xlabel("Time (fs)")
    axes[1].set_ylabel(r"Peak $a_0$")
    axes[1].legend()

    fig.suptitle("Laser propagation in the FBPIC baseline")
    fig.tight_layout()

    figure_path = Path("figures/laser/laser_propagation_evolution.png")
    figure_path.parent.mkdir(exist_ok=True)
    fig.savefig(figure_path, dpi=200, bbox_inches="tight")

    if args.show:
        plt.show()

    plt.close(fig)

    waist_change = (spot_size_um[-1] / spot_size_um[0] - 1.0) * 100.0
    a0_change = (peak_a0[-1] / peak_a0[0] - 1.0) * 100.0

    print()
    print(f"Initial spot size: {spot_size_um[0]:.3f} um")
    print(f"Final spot size:   {spot_size_um[-1]:.3f} um")
    print(f"Spot-size change:  {waist_change:+.2f} %")
    print()
    print(f"Initial peak a0:   {peak_a0[0]:.3f}")
    print(f"Final peak a0:     {peak_a0[-1]:.3f}")
    print(f"Peak-a0 change:    {a0_change:+.2f} %")
    print()
    print(f"Final vacuum waist: {vacuum_waist_um[-1]:.3f} um")
    print(f"Plateau matched waist: {matched_waist_um:.3f} um")
    print(f"Saved data to: {results_path}")
    print(f"Saved figure to: {figure_path}")


if __name__ == "__main__":
    main()
