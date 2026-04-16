# Laser-HHG-EUV Lab

**A parameterized HHG / EUV architectural modeling lab.**

This repository is a *simulation-and-architecture study* for laser-driven
high-harmonic generation (HHG) sources in the DUV / VUV / EUV / soft X-ray
bands. It is **not** a device demonstration, **not** a production EUV
lithography source, and **not** a claim that gas-jet HHG can replace
laser-produced-plasma (LPP) sources for high-volume manufacturing.

The repo's role is to model the *generation-side* chain — driver-laser
conditioning, gas-target conversion, beamline optics — that complements
the companion `vdw-polaritonics-lab` (DUV intracavity modulation at 193 /
248 nm). The two systems share an architectural control-plane concept
(programmable optical transfer function); they are physically distinct,
because van der Waals materials absorb at EUV.

## Evidence Architecture and Claim Taxonomy

Every quantitative or qualitative output in this repository carries an
explicit epistemic-tier label. The tiers, in decreasing order of
physical commitment, are:

| Tier | Meaning | Examples in this repo |
| --- | --- | --- |
| `ANALYTICAL` | Closed-form expression, exact within stated assumptions. | Cutoff energy `E_cut = 3.17 U_p + I_p`; beamline transmission `R^N · T^M`; harmonic-order-to-wavelength conversion. |
| `PARAMETERIZED` | Single-atom or small-system response from a parameterized model. Output shape is meaningful; absolute device flux is not. | Single-atom HHG yield (`λ^-(5..6.5)` scaling anchored to a literature baseline); Gaussian PSF compositing; Mack-dissolution resist response. |
| `ARCHITECTURE` | System diagram, control-plane narrative, "consistent with published experimental feasibility" claim. No quantitative device-performance assertion. | The 3D pipeline view; the wavelength-bridge figure; the multi-head writer-array packaging concept. |
| `LITERATURE` | Value quoted from a cited experimental paper or industrial datasheet. The repo does not reproduce the measurement. | Source-side photon-flux anchors (KMLabs XUUS-4); Mo/Si reflectivity at 13.5 nm; ionization potentials. |

A fifth tier — *demonstrated subsystem behaviour* — is intentionally
excluded. No module in this repo physically builds or measures a device;
that tier is the province of cited references only.

## Generated vs. Delivered Distinction

The repo strictly separates three planes when reporting photon flux:

1. **Source-side (generated)**: photons per second per harmonic at the
   gas-jet exit. Anchored to published industrial HHG sources
   (`SOURCE_SIDE_LITERATURE_ANCHORS` in `backend/optical_pipeline.py`).
   Tier: `LITERATURE` unless the caller supplies a model.
2. **Beamline transmission**: compound throughput through Mo/Si
   multilayer mirrors and metal foil filters. Tier: `ANALYTICAL`
   (`R^N · T^M`).
3. **Delivered (application-plane, in-vacuum)**: source × beamline.
   Ignores sample absorption and detector quantum efficiency. Tier:
   `PARAMETERIZED`.

`EUVOpticalPipeline.compute_flux_budget()` returns a `FluxBudget`
dataclass that carries each value with its own tier label.

## What This Repo Models

* **Analytical HHG calculators** (`backend/hhg_analytical.py`):
  cutoff energy, single-atom efficiency anti-scaling, phase-matching
  window proxy (critical ionization fraction), beamline transmission.
* **Wavelength-bridge figure** (`backend/wavelength_bridge.py`):
  driver bands (Ti:Sa 800 nm, Yb:YAG 1030 nm, MIR OPCPA 1800-3000 nm),
  HHG-conversion arrows, DUV / VUV / EUV / SXR regions, and the
  operating regions of both companion repos.
* **3D pipeline architecture** (`backend/optical_pipeline.py`,
  `backend/visualization_3d.py`): driver → focusing optic → gas cell
  → metal filter → Mo/Si mirror(s) → application plane. Architectural
  view; the multi-head packaging is illustrative.
* **Resist process pipeline** (`backend/lithography_model.py`,
  `backend/visualization.py`): parameterized 2D aerial image →
  acid map → PEB → Mack dissolution. Illustrative trade-off explorer,
  not a calibrated process model.
* **PSF synthesis** (`backend/psf_synthesis.py`): incoherent and
  coherent compositing of Gaussian sub-exposures; coupled
  spatial-temporal optimization. Tier: `PARAMETERIZED`.

## Scope and Limitations

* High-volume manufacturing EUV lithography uses laser-produced-plasma
  (LPP) sources at ~250 W intermediate-focus power. Tabletop HHG
  delivers nanowatts to microwatts at 13.5 nm; the gap is physical
  (conversion efficiency, duty cycle, repetition rate), not
  engineering. This repo does not assert otherwise.
* The vdW intracavity modulation stack operates at DUV (193 / 248 nm).
  EUV (13.5 nm) is beyond the absorption edge of MoS₂, graphene, hBN,
  and black phosphorus. The cavity does not operate at EUV; the HHG
  stage is the EUV generation mechanism, downstream and physically
  separate.
* Cavity-enhanced HHG (CE-HHG) — femtosecond enhancement cavities at
  the NIR driver wavelength — is a distinct, demonstrated architecture
  (JILA / MPQ since 2005). It is **not** the same thing as the vdW
  cavity, and conflating the two is a credibility-destroying overclaim
  for expert readers.
* `EUVOpticalPipeline.compute_power_budget()` traces *transmission
  products only*. The gas-cell entry is the single-atom conversion
  efficiency, not a macroscopic flux.

## Defensible Use Cases

* Coherent diffractive imaging (CDI)
* Ptychography
* Actinic EUV mask inspection
* Angle-resolved photoemission (ARPES with CE-HHG)

These are the wavelength-and-coherence regimes where tabletop HHG is
the right tool. EUV lithography source replacement is not.

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/` for the dashboard, or
`http://127.0.0.1:8000/docs` for the FastAPI-generated API docs.

## API Endpoints

| Endpoint | Tier | Description |
| --- | --- | --- |
| `GET /` | — | Dashboard with epistemic-tier banner. |
| `GET /api/wavelength-bridge` | `ARCHITECTURE` | Driver → harmonic cascade → DUV/VUV/EUV figure. |
| `GET /api/hhg-analytical` | `ANALYTICAL` | Cutoff, efficiency-scaling, phase-matching, beamline-transmission calculators. |
| `GET /api/visualize-3d` | `ARCHITECTURE` | 3D HHG generation-chain view. |
| `GET /api/visualize` | `PARAMETERIZED` | Resist-process trade-off explorer. |
| `GET /api/psf-synthesis` | `PARAMETERIZED` | PSF compositing study. |
| `GET /api/multihead` | `ARCHITECTURE` | Multi-head writer-array packaging concept. |
| `GET /api/fleet-economics` | `ARCHITECTURE` | Cost/throughput sensitivity table. |

## Tests

```bash
pytest tests/ -v
```

Tests cover analytical-calculator monotonicity, single-atom efficiency
scaling, phase-matching-window proxy, beamline-transmission
multiplicativity, epistemic-label discipline (every public visualization
must include a tier label), and the existing PSF / resist / multihead /
fleet checks.

## License

[Add your license here]
