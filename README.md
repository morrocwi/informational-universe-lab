# Informational Universe Lab

A minimalist repository illustrating the informational diffusivity
reinterpretation of gravitational-wave ringdown. The project has been
reduced to a single executable module, `ringdown.py`, so that researchers
can explore the telegraph model with minimal setup.

## Quick Start

```bash
python ringdown.py --event GW150914
python ringdown.py --custom tau_ms=4.0 freq_hz=251
```

Each command prints the damping time, ringdown frequency, informational
diffusivity \(D=c^2\tau_{220}\), and the resulting characteristic speed.
All results are expressed with explicit SI units through
[`astropy.units`](https://docs.astropy.org/en/stable/units/).

## Posterior Sampling Workflow (Bilby + GWOSC)

To replace the built-in catalogue values with posterior samples obtained
from public data:

1. **Install dependencies** (Python \>=3.10):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install bilby gwosc astropy numpy scipy matplotlib
   ```
2. **Download the strain data** for the event of interest using
   [`gwosc`](https://www.gw-openscience.org/):
   ```python
   from gwosc import datasets
   datasets.find_datasets(event="GW150914")
   datasets.download_dataset(event="GW150914", path="./gw150914")
   ```
3. **Run Bilby ringdown inference** (schematic example):
   ```python
   import bilby

   # Configure the ringdown model and priors following the Bilby tutorials
   likelihood = bilby.gw.likelihood.RingdownLikelihood(
       interferometer_list=bilby.gw.detector.InterferometerList(["H1", "L1"]),
       waveform_generator=bilby.gw.waveform_generator.WaveformGenerator(
           duration=0.5,
           sampling_frequency=4096,
           frequency_domain_source_model=bilby.gw.source.ringdown,
       ),
   )

   result = bilby.run_sampler(
       likelihood=likelihood,
       priors={
           "tau_220": bilby.core.prior.Uniform(name="tau_220", minimum=1e-3, maximum=1e-2),
           "freq_220": bilby.core.prior.Uniform(name="freq_220", minimum=150, maximum=400),
       },
       sampler="dynesty",
       nlive=1000,
       outdir="ringdown_posteriors",
       label="GW150914",
   )
   result.plot_corner()
   ```
4. **Extract summary statistics** (e.g., median damping time) and feed
   them into `ringdown.py`:
   ```python
   tau_ms = result.posterior["tau_220"].median() * 1e3
   freq_hz = result.posterior["freq_220"].median()
   ```
   ```bash
   python ringdown.py --custom tau_ms=${tau_ms} freq_hz=${freq_hz}
   ```

This workflow keeps the scientific provenance clear: raw strain data from
GWOSC, Bayesian inference via Bilby, and phenomenological transport
interpretation through `ringdown.py`.

## Module Overview

`ringdown.py` defines a compact `RingdownEvent` dataclass, a minimal
catalogue of published detections, and a command-line interface that
reports diffusivities either in human-readable form or as JSON. The file
is self-contained and can be copied into notebooks or scripts for quick
experimentation with new posterior samples or hypothetical merger
scenarios.
