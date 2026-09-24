# FBPIC Baseline Simulation and Analysis

This was my first complete FBPIC run before starting my MPhys project,
*Optimising Laser Wakefield Acceleration*. The main aim was to get a working
FBPIC and openPMD workflow, then use the saved data to produce a proper set of
diagnostic figures and calculations.

The simulation input is a lightly adapted CPU version of the standard FBPIC
LWFA example. My own work focused on the analysis. I examined the electric
fields, electron density and longitudinal phase space, followed the laser and
saved electron population through time, and calculated weighted quantities for
a possible late-time bunch. I also checked how much the main results changed
when local field values were averaged or the bunch-selection limits were moved.

This is a learning and validation baseline rather than an optimised accelerator
result. Numerical convergence has not yet been tested, so the exact peak values
should not be treated as final predictions.

The depleted cavity and dense sheath, the longitudinal field behind the laser,
and the later high-momentum branch together provide strong evidence that a wake
formed. The saved snapshots also show a candidate accelerated population
developing behind the laser late in the run.

## Main results

| Quantity | Result | What this shows |
| --- | ---: | --- |
| Reference plasma wavelength | 16.6947 μm | Calculated directly from the input density |
| Final laser-envelope peak | 102.832 μm | Position found from the on-axis transverse-field envelope |
| Laser spot size | 5.052 to 6.542 μm | The driver expands throughout the short run |
| Peak normalised vector potential | 3.988 to 3.118 | The on-axis amplitude falls as the spot expands |
| Final vacuum comparison | Measured spot about 2.5% smaller | Close to vacuum diffraction; this difference does not establish plasma focusing |
| Late high-momentum branch | Approximately 84-87 μm | About one reference plasma wavelength behind the laser |
| Raw minimum on-axis longitudinal field | -679.76 GV m⁻¹ | A very local peak rather than an average wake amplitude |
| Smoothed longitudinal-field minimum | Below approximately -600 GV m⁻¹ | The feature survives three- and five-cell averaging; convergence has not been tested |
| Final candidate-bunch charge | 43.254 pC | Depends on the chosen phase-space cuts |
| Final candidate-bunch weighted mean energy | 3.235 MeV | More representative than the 5.611 MeV maximum |
| Final candidate-bunch relative RMS spread | 33.14% | The selected population is broad rather than quasi-monoenergetic |

The complete reasoning and numerical checks are in
[LWFA_analysis.md](LWFA_analysis.md). The main values are stored separately in
[results/summary.csv](results/summary.csv), with the laser-propagation series in
[results/laser_propagation.csv](results/laser_propagation.csv).

## Main diagnostics

The full density plot was dominated by a narrow on-axis compression reaching
about 127.6 times the background density. I produced a second plot with the
colour scale limited to five times the background density. The underlying data
were not changed. This makes the depleted cavity and dense sheath much easier
to see. The sheath closes near the strongest negative on-axis longitudinal
field, behind the measured laser position. These features together provide
strong evidence of a wake; the exact density and field peaks still need
numerical checks.

![Electron density with the colour scale clipped to five times the background density](figures/wake/electron_density_final_clipped_0_5n0.png)

The longitudinal phase space was then followed through five saved times. This
showed that the early regular pattern moves with the laser, whereas a different
high-momentum branch develops behind it later in the run.

![Evolution of electron longitudinal phase space](figures/electrons/z_uz_phase_space_evolution.png)

The laser-propagation diagnostic measures the transverse fluence across the
pulse, uses its second moment to calculate the spot radius, and converts the
peak field envelope to the normalised vector potential. The spot radius grows
from 5.052 to 6.542 μm while the peak normalised vector potential falls from
3.988 to 3.118. The final spot is only about 2.5% smaller than the vacuum
prediction, which is consistent with mainly diffraction-like propagation over
this short distance. Without a vacuum control run or an uncertainty estimate
for the measured spot size, that difference does not establish plasma focusing.

![Evolution of the measured laser spot size and peak normalised vector potential](figures/laser/laser_propagation_evolution.png)

For the final bunch calculation, I selected the late branch relative to the
measured laser position. The spatial and momentum limits are shown on the plot
and are tested against nearby choices in the full analysis. The exact charge
and energy values move with the lower momentum cut. At the final snapshot, the
tested cuts still leave tens of pC at a few MeV with a broad energy spread.

![Final phase space and candidate-bunch selection](figures/electrons/final_bunch_selection.png)

Applying the same selection at every saved iteration showed that selected
charge grew late in the run, but the rise around iteration 1500 depends strongly
on the momentum cut. At that snapshot, 2.628 pC passes $u_z\geq4$, while only
0.00112 pC passes $u_z\geq5$. Charge above the stricter cut grows later, reaching
31.316 pC in the final snapshot. These independently selected snapshots show
how the candidate population changes; they do not identify when individual
electrons were injected.

![Selected charge under three longitudinal-momentum cuts](figures/electrons/charge_evolution_cutoff_comparison.png)

The follow-on diagnostics show the
[candidate population through the saved snapshots](figures/electrons/bunch_evolution.png)
and [the laser and selected charge on one distance axis](figures/electrons/laser_bunch_comparison.png).

## Repository contents

| Path | Contents |
| --- | --- |
| [simulation/](simulation/) | Adapted CPU simulation input |
| [analysis/laser/](analysis/laser/) and [figures/laser/](figures/laser/) | Laser field and propagation |
| [analysis/wake/](analysis/wake/) and [figures/wake/](figures/wake/) | Wake fields and electron density |
| [analysis/electrons/](analysis/electrons/) and [figures/electrons/](figures/electrons/) | Electron phase space and candidate bunch |
| [analysis/validation/](analysis/validation/) and [figures/validation/](figures/validation/) | Sensitivity checks and supporting plots |
| [results/](results/) | CSV summary of the main numerical results |
| [tests/](tests/) | Checks for the reference values and laser-propagation calculations |
| [LWFA_analysis.md](LWFA_analysis.md) | Full analysis, interpretation and limitations |
| [environment.yml](environment.yml) | Conda environment used for the workflow |

## Running the baseline

Create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate fbpic-lwfa-baseline
```

Run the simulation:

```bash
python simulation/lwfa_baseline.py
```

FBPIC writes the openPMD diagnostics to `diags/hdf5`. These raw HDF5 files are
not included because of their size. My completed run contained 36 snapshots
from iterations 0 to 1750.

If the diagnostics already live elsewhere, link them at the expected location
before running the scripts. For my completed run in WSL:

```bash
mkdir -p diags
ln -s /home/ollie/fbpic-projects/first-run/diags_baseline_full_cpu/hdf5 diags/hdf5
```

Run these commands from the repository root. Skip the link if `diags/hdf5`
already exists.

Check that the diagnostic output is available:

```bash
python check_diagnostics.py
```

The analysis scripts can then be run separately. For example:

```bash
python analysis/wake/plot_ez.py
python analysis/electrons/plot_z_uz.py
python analysis/laser/analyse_laser_propagation.py
python analysis/electrons/analyse_final_bunch.py
python analysis/electrons/analyse_bunch_evolution.py
```

The bunch-evolution and validation scripts read `results/laser_propagation.csv`;
run the laser-propagation script first if that CSV has not been generated.
The scripts in `analysis/validation/` check the sensitivity of selected
measurements and write their plots under `figures/validation/`.

Run the repository checks with:

```bash
python -m unittest discover -s tests
```

## Limits of this baseline

- The particle diagnostic only saved electrons with `u_z >= 1`. The particle
  plots therefore do not show the full plasma-electron population.
- The candidate bunch is defined using spatial and momentum cuts. Its general
  position is clear in phase space, but the charge and energy values change
  when the lower momentum threshold is moved, especially during the early
  rise. The charge has not been checked against radial position or the local
  accelerating field at each particle.
- The raw field and density extrema are very local. Their exact values still
  need checks using different resolutions, particle sampling and retained
  azimuthal modes. Averaging the field over several cells is not a numerical
  convergence test, and the reconstructed density includes a small unphysical
  negative minimum whose precise cause is not established.
- The Hilbert envelope gives the position and peak value of the on-axis
  transverse field. It does not measure the total laser energy or depletion.
- Particle IDs were not followed between saved times. The plots show how the
  populations change, but they do not track one electron through the run.
- This baseline should be numerically checked before it is used for parameter
  optimisation.

## Source and references

The simulation input was adapted from the
[standard FBPIC LWFA example](https://fbpic.github.io/example_input/lwfa_script.html)
and run with FBPIC 0.27.0 on CPU. The original FBPIC licence is included at
[licenses/FBPIC-LICENSE.txt](licenses/FBPIC-LICENSE.txt).

- R. Lehe *et al.*, “A spectral, quasi-cylindrical and dispersion-free
  Particle-In-Cell algorithm,” *Computer Physics Communications* **203**,
  66-82 (2016), [doi:10.1016/j.cpc.2016.02.007](https://doi.org/10.1016/j.cpc.2016.02.007).
- [FBPIC documentation](https://fbpic.github.io/)
- [openPMD-viewer documentation](https://openpmd-viewer.readthedocs.io/)
