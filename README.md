
# Informational Universe Lab

A minimalist repository illustrating the **informational diffusivity reinterpretation of gravitational-wave ringdown**.  
The project is intentionally lightweight — a single executable module, `ringdown.py`, enabling researchers to explore the telegraph-based ringdown model with minimal setup.

---
````markdown
## Quick Start

```bash
python ringdown.py --event GW150914
python ringdown.py --custom tau_ms=4.0 freq_hz=251
````

Each command prints:

* Damping time
* Ringdown frequency
* Informational diffusivity ( D = c^{2}\tau_{220} )
* Resulting characteristic speed

All outputs use explicit SI units via `astropy.units`.

---

## Posterior Sampling Workflow (Bilby + GWOSC)

### 1. Install dependencies (Python ≥ 3.10)

```bash
python -m venv venv
source venv/bin/activate
pip install bilby gwosc astropy numpy scipy matplotlib
```

### 2. Download strain data from GWOSC

```python
from gwosc import datasets

datasets.find_datasets(event="GW150914")
datasets.download_dataset(event="GW150914", path="./gw150914")
```

### 3. Run Bilby ringdown inference

```python
import bilby

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

### 4. Extract summary statistics and run ringdown.py

```python
tau_ms = result.posterior["tau_220"].median() * 1e3
freq_hz = result.posterior["freq_220"].median()
```

```bash
python ringdown.py --custom tau_ms=${tau_ms} freq_hz=${freq_hz}
```

Scientific provenance is kept clear:

1. Raw strain data → GWOSC
2. Bayesian inference → Bilby
3. Transport reinterpretation → `ringdown.py`

---

## Module Overview: `ringdown.py`

* Contains a compact `RingdownEvent` dataclass
* Includes a minimal catalogue of published detections
* Offers a command-line interface for human-readable or JSON output
* Fully self-contained — suitable for notebooks, scripts, or standalone experimentation

---

## Future Extensions

Additional modules exploring broader aspects of informational physics and causal telegraph transport will be added in future updates.


