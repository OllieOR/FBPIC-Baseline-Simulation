import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c, e, epsilon_0, m_e, pi
from scipy.signal import find_peaks
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

# Detect successive positive wakefield maxima
dz_um = np.mean(np.diff(z_um))

n_e = 4.0e18 * 1.0e6
omega_p = np.sqrt(n_e * e**2 / (m_e * epsilon_0))
reference_wavelength_um = 2.0 * pi * c / omega_p * 1e6

minimum_distance_um = 0.6 * reference_wavelength_um
minimum_distance_points = int(minimum_distance_um / dz_um)

peak_indices, _ = find_peaks(
    Ez_axis_GVm,
    prominence=50,
    distance=minimum_distance_points
)

peak_positions_um = z_um[peak_indices]
peak_fields_GVm = Ez_axis_GVm[peak_indices]

if len(peak_positions_um) < 2:
    raise RuntimeError(
        "Fewer than two suitable wake peaks were detected."
    )
wavelength_um = peak_positions_um[1] - peak_positions_um[0]
percentage_difference = (wavelength_um / reference_wavelength_um - 1) * 100

print(f"Peak positions: {peak_positions_um} um")
print(f"Peak fields: {peak_fields_GVm} GV/m")
print(f"Measured separation: {wavelength_um:.4f} um")
print(f"Reference plasma wavelength: {reference_wavelength_um:.4f} um")
print(f"Percentage difference: {percentage_difference:.2f} %")

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

ax.scatter(
    peak_positions_um,
    peak_fields_GVm,
    color="black",
    marker="x",
    s=80,
    linewidths=2,
    label="Detected maxima",
    zorder=5
)

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

fig.savefig("figures/measure_wake_wavelength.png", dpi=300)
plt.show()
