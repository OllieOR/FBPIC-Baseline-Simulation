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

## Main results

|Quantity|Result|What this shows|
|-|-:|-|
|Reference plasma wavelength|16.6947 μm|Calculated directly from the input density|
|Final laser-envelope peak|102.832 μm|Position found from the on-axis transverse-field envelope|
|Late high-momentum branch|Approximately 84-87 μm|About one reference plasma wavelength behind the laser|
|Raw minimum on-axis longitudinal field|-679.76 GV m⁻¹|A very local peak rather than an average wake amplitude|
|Smoothed longitudinal-field minimum|Below approximately -600 GV m⁻¹|The feature survives three- and five-cell averaging|
|Candidate-bunch charge|43.254 pC|Depends on the chosen phase-space cuts|
|Candidate-bunch weighted mean energy|3.235 MeV|More representative than the 5.611 MeV maximum|
|Candidate-bunch relative RMS spread|33.14%|The selected population is broad rather than quasi-monoenergetic|

The complete reasoning and numerical checks are in
[LWFA\_analysis.md](LWFA_analysis.md). I also included a
[PDF copy](LWFA_analysis.pdf) because it is easier to open when the Markdown
image paths are not available. The main values are stored separately in
[results/summary.csv](results/summary.csv).

## Main diagnostics

The full density plot was dominated by a narrow on-axis compression reaching
about 127.6 times the background density. I produced a second plot with the
colour scale limited to five times the background density. The underlying data
were not changed. This makes the depleted cavity and dense sheath much easier
to see.

!\[Electron density with the colour scale clipped to five times the background density](figures/electron\_density\_final\_clipped\_0\_5n0.png)

The longitudinal phase space was then followed through five saved times. This
showed that the early regular pattern moves with the laser, whereas a different
high-momentum branch develops behind it later in the run.

!\[Evolution of electron longitudinal phase space](figures/z\_uz\_phase\_space\_evolution.png)

For the final bunch calculation, I selected the late branch relative to the
measured laser position. The spatial and momentum limits are shown on the plot
and are tested against nearby choices in the full analysis. The exact charge
and energy values move with the lower momentum cut, but the main conclusion
does not: the selected population contains tens of pC at a few MeV and has a
broad energy spread.

!\[Final phase space and candidate-bunch selection](figures/final\_bunch\_selection.png)

## Repository contents

|Path|Contents|
|-|-|
|[simulation/](simulation/)|Adapted CPU simulation input|
|[analysis/](analysis/)|Scripts used for the calculations and figures|
|[figures/](figures/)|Figures produced from the completed run|
|[results/](results/)|CSV summary of the main numerical results|
|[tests/](tests/)|Small checks for the reference calculations|
|[LWFA\_analysis.md](LWFA_analysis.md)|Full analysis, interpretation and limitations|
|[LWFA\_analysis.pdf](LWFA_analysis.pdf)|PDF copy of the full analysis|
|[environment.yml](environment.yml)|Conda environment used for the workflow|

## Running the baseline

Create the environment from the repository root:

```bash
conda env create -f environment.yml
conda activate fbpic-lwfa-baseline
```

Run the simulation:

```bash
python simulation/lwfa\\\_baseline.py
```

FBPIC writes the openPMD diagnostics to `diags/hdf5`. These raw HDF5 files are
not included because of their size. My completed run contained 36 snapshots
from iterations 0 to 1750.

Check that the diagnostic output is available:

```bash
python check\\\_diagnostics.py
```

The analysis scripts can then be run separately. For example:

```bash
python analysis/plot\\\_ez.py
python analysis/plot\\\_z\\\_uz.py
python analysis/analyse\\\_final\\\_bunch.py
```

To run all analysis scripts without opening each plot window:

```bash
for script in analysis/\\\*.py; do MPLBACKEND=Agg python "$script"; done
```

Run the repository checks with:

```bash
python -m unittest discover -s tests
```

## Limits of this baseline

* The particle diagnostic only saved electrons with `u\\\_z >= 1`. The particle
plots therefore do not show the full plasma-electron population.
* The candidate bunch is defined using spatial and momentum cuts. Its general
position and interpretation are stable, but the charge and energy values
change when the lower momentum threshold is moved.
* The raw field and density extrema are very local. Their exact values still
need checks using different resolutions, particle sampling and retained
azimuthal modes.
* The Hilbert envelope gives the position and peak value of the on-axis
transverse field. It does not measure the total laser energy or depletion.
* Particle IDs were not followed between saved times. The plots show how the
populations change, but they do not track one electron through the run.
* This baseline should be numerically checked before it is used for parameter
optimisation.

## Source and references

The simulation input was adapted from the
[standard FBPIC LWFA example](https://fbpic.github.io/example_input/lwfa_script.html)
and run with FBPIC 0.27.0 on CPU. The original FBPIC licence is included at
[licenses/FBPIC-LICENSE.txt](licenses/FBPIC-LICENSE.txt).

* R. Lehe *et al.*, “A spectral, quasi-cylindrical and dispersion-free
Particle-In-Cell algorithm,” *Computer Physics Communications* **203**,
66-82 (2016), [doi:10.1016/j.cpc.2016.02.007](https://doi.org/10.1016/j.cpc.2016.02.007).
* [FBPIC documentation](https://fbpic.github.io/)
* [openPMD-viewer documentation](https://openpmd-viewer.readthedocs.io/)

