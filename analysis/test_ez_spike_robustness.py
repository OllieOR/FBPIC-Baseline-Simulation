from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from openpmd_viewer import OpenPMDTimeSeries

DIAGNOSTIC_PATH = "diags/hdf5"
ITERATION = 1750

# Region containing the wake spike but excluding the laser pulse
WAKE_Z_MIN_UM = 78.0
WAKE_Z_MAX_UM = 98.0

figure_directory = Path("figures")
figure_directory.mkdir(exist_ok=True)

ts = OpenPMDTimeSeries(DIAGNOSTIC_PATH)

Ez, info = ts.get_field(
    field="E",
    coord="z",
    iteration=ITERATION,
    theta=0.0,
)

r = np.asarray(info.r)
z = np.asarray(info.z)

if Ez.shape == (z.size, r.size):
    Ez = Ez.T
elif Ez.shape != (r.size, z.size):
    raise ValueError(
        f"Unexpected Ez shape {Ez.shape}; "
        f"expected {(r.size, z.size)} or {(z.size, r.size)}."
    )

# Construct the on-axis field.
# Use the r=0 cell if present; otherwise average the two cells
# immediately adjacent to the axis.
zero_indices = np.where(np.isclose(r, 0.0, atol=1e-15))[0]

if zero_indices.size > 0:
    Ez_axis = Ez[zero_indices[0], :]
else:
    negative_indices = np.where(r < 0.0)[0]
    positive_indices = np.where(r > 0.0)[0]

    i_negative = negative_indices[np.argmax(r[negative_indices])]
    i_positive = positive_indices[np.argmin(r[positive_indices])]

    Ez_axis = 0.5 * (Ez[i_negative, :] + Ez[i_positive, :])

z_um = z * 1e6
Ez_axis_GVm = Ez_axis / 1e9

wake_mask = (
    (z_um >= WAKE_Z_MIN_UM)
    & (z_um <= WAKE_Z_MAX_UM)
    & np.isfinite(Ez_axis_GVm)
)

z_wake = z_um[wake_mask]
Ez_wake = Ez_axis_GVm[wake_mask]

if Ez_wake.size < 5:
    raise ValueError("The selected wake region contains fewer than five cells.")


def moving_average(x, y, number_of_cells):
    """Return cell-centred moving averages of x and y."""
    kernel = np.ones(number_of_cells) / number_of_cells

    x_average = np.convolve(x, kernel, mode="valid")
    y_average = np.convolve(y, kernel, mode="valid")

    return x_average, y_average

raw_index = np.argmin(Ez_wake)
raw_minimum = Ez_wake[raw_index]
raw_position = z_wake[raw_index]

z_three, Ez_three = moving_average(z_wake, Ez_wake, 3)
z_five, Ez_five = moving_average(z_wake, Ez_wake, 5)

three_index = np.argmin(Ez_three)
five_index = np.argmin(Ez_five)

three_cell_minimum = Ez_three[three_index]
five_cell_minimum = Ez_five[five_index]

# Low-field percentile across the selected wake region
first_percentile = np.percentile(Ez_wake, 1.0)

print(f"Wake region: {WAKE_Z_MIN_UM:.1f}--{WAKE_Z_MAX_UM:.1f} um")
print()
print(
    f"Raw minimum:          {raw_minimum:.2f} GV/m "
    f"at z = {raw_position:.3f} um"
)
print(
    f"Three-cell minimum:   {three_cell_minimum:.2f} GV/m "
    f"at z = {z_three[three_index]:.3f} um"
)
print(
    f"Five-cell minimum:    {five_cell_minimum:.2f} GV/m "
    f"at z = {z_five[five_index]:.3f} um"
)
print(f"First percentile:     {first_percentile:.2f} GV/m")
print()
print(
    "Three-cell/raw magnitude ratio: "
    f"{abs(three_cell_minimum / raw_minimum):.3f}"
)
print(
    "Five-cell/raw magnitude ratio:  "
    f"{abs(five_cell_minimum / raw_minimum):.3f}"
)

fig, ax = plt.subplots(figsize=(11, 6))

ax.plot(
    z_wake,
    Ez_wake,
    color="navy",
    linewidth=1.5,
    label=r"Raw on-axis $E_z$",
)

ax.plot(
    z_three,
    Ez_three,
    color="darkorange",
    linewidth=2.0,
    label="Three-cell average",
)

ax.plot(
    z_five,
    Ez_five,
    color="green",
    linewidth=2.0,
    label="Five-cell average",
)

ax.axhline(
    first_percentile,
    color="crimson",
    linestyle="--",
    linewidth=1.5,
    label="First percentile in wake region",
)

ax.axhline(0.0, color="black", linewidth=0.8)

ax.set_xlim(WAKE_Z_MIN_UM, WAKE_Z_MAX_UM)
ax.set_xlabel(r"$z\;(\mu\mathrm{m})$")
ax.set_ylabel(r"On-axis $E_z\;(\mathrm{GV\,m^{-1}})$")
ax.set_title(r"Robustness test of the longitudinal-field spike")
ax.grid(alpha=0.25)
ax.legend()

fig.tight_layout()

output_path = figure_directory / "ez_spike_robustness.png"
fig.savefig(output_path, dpi=300, bbox_inches="tight")

print(f"\nSaved robustness figure to: {output_path}")

plt.show()
