# Laser-HHG-EUV Lab — Module Reference

**Parameterized HHG / EUV architectural modeling lab.** This document
maps the backend modules and explains the epistemic-tier discipline
that governs every output. For the project-level overview and scope
disclaimers, see `README.md`.

## Repositioning

The repository was previously framed as a "Chip-Scale Coherent EUV
Source" with patent claims for a programmable lithography platform.
That framing conflates four physically distinct things:

1. The EUV-source problem solved by ASML's LPP (250 W at 13.5 nm
   intermediate focus).
2. Tabletop HHG sources (nanowatts to microwatts at 13.5 nm; many
   orders of magnitude below LPP).
3. The vdW intracavity DUV modulation architecture (193 / 248 nm,
   downstream of any EUV stage and physically separate).
4. Multi-beam writer-array packaging (a separate engineering concern
   from the upstream photon source).

The current framing positions the repo as a *generation-side
architectural modeling lab* that complements `vdw-polaritonics-lab` at
the front-end driver-conditioning interface. The strongest defensible
claim is that the same programmable-control-plane logic that operates
on the cavity-amplified DUV source can, at the driver-laser front end,
apply spectral and temporal conditioning that systematically shifts the
harmonic output of a connected HHG stage. The HHG stage is the EUV
generation mechanism; the cavity is not at EUV.

## Epistemic-Tier Discipline

Every quantitative or qualitative output in this repository carries an
explicit tier label rendered as a colored badge in the UI:

```
[ANALYTICAL]   green    Closed-form, exact within stated assumptions.
[PARAMETERIZED] blue    Single-atom / small-system response from a model.
[ARCHITECTURE] purple   System diagram or control-plane narrative.
[LITERATURE]   amber    Quoted from a cited paper or industrial datasheet.
```

The taxonomy is implemented in `backend/epistemic.py`:

* `EpistemicTier`     — four-level enum
* `TierLabel`          — tier + claim + optional note
* `render_badge`       — inline HTML badge
* `render_label`       — full HTML for a labelled claim
* `render_key`         — four-tier legend
* `inject_epistemic_assets` — adds CSS + scope banner to a page

Every analytical-calculator return type in `backend/hhg_analytical.py`
carries a `TierLabel` field by default, so a downstream caller cannot
forget to label the output.

## Backend Modules

```
backend/
  epistemic.py              # NEW. Tier taxonomy + UI helpers.
  hhg_analytical.py         # NEW. Analytical / formula-based calculators.
  wavelength_bridge.py      # NEW. Driver -> harmonic cascade figure.
  hhg_model.py              # Compatibility shim over hhg_analytical.
  optical_pipeline.py       # Architectural HHG generation chain
                            # + generated/beamline/delivered FluxBudget.
  visualization.py          # 2D resist process pipeline (PARAMETERIZED).
  visualization_3d.py       # 3D pipeline view (ARCHITECTURE).
  visualization_psf.py      # PSF synthesis (PARAMETERIZED).
  visualization_multihead.py# Multi-head packaging (ARCHITECTURE).
  visualization_fleet.py    # Fleet economics sensitivity (ARCHITECTURE).
  visualization_11dof.py    # 11-DOF writer-head exploded view (ARCHITECTURE).
  psf_synthesis.py          # PSF compositing engine.
  multihead_model.py        # Multi-head tiling and stitching.
  lithography_model.py      # 2D aerial image + resist process.
  fleet_economics.py        # Cost-of-ownership / throughput model.
  dose_engine.py            # Phoenix adaptive-dose engine state.
  euv_psf.py                # Native EUV PSF helpers.
  resist_model.py           # Chemically amplified resist.
  physics_engine.py         # Shared physics utilities.
  citations.py              # Citation rendering / references panel.
  references.py             # Reference bibliography.
```

## Generated vs. Delivered Flux

`EUVOpticalPipeline.compute_flux_budget()` returns a `FluxBudget`
dataclass with three explicitly tier-labelled fields:

| Field | Tier | Source |
| --- | --- | --- |
| `source_photons_per_second` | `LITERATURE` | KMLabs XUUS-4 white paper anchors per gas. |
| `beamline_transmission` | `ANALYTICAL` | `R^N · T^M` from `analytical_beamline_transmission`. |
| `delivered_photons_per_second` | `PARAMETERIZED` | `source × beamline`; ignores sample absorption and detector QE. |

The repo never reports a single "delivered EUV power" without exposing
this three-way split.

## Wavelength-Bridge Figure

`backend/wavelength_bridge.py` renders a single architecture-level
figure that places, on one wavelength axis from ~3 µm to ~1 nm:

* driver bands (Ti:Sa 800 nm, Yb:YAG 1030 nm, MIR OPCPA 1800-3000 nm)
* HHG-conversion arrows (analytical `E_cut` at representative I)
* DUV / VUV / EUV / SXR spectral regions
* the operating region of `vdw-polaritonics-lab` (193 / 248 nm DUV)
* the operating region of THIS repo (HHG plateau 60-13.5 nm)
* industrial anchors (DUV 193/248 nm, actinic 30 nm, ASML LPP 13.5 nm)

The figure communicates the complementarity portfolio argument
immediately — both repos sit on one wavelength axis, with the cavity
upstream in DUV and the HHG chain downstream in EUV.

## Tests

```bash
pytest tests/ -v
```

New tests added in this pass:

* `tests/test_hhg_analytical.py` — cutoff scaling, U_p formula,
  efficiency anti-scaling, phase-matching window, beamline transmission
  multiplicativity, generated-vs-delivered flux split.
* `tests/test_epistemic.py` — every tier round-trips a label;
  `render_badge` produces valid HTML; the scope banner is injected
  into pages.
* `tests/test_wavelength_bridge.py` — figure has all three repo
  overlays and at least one HHG-conversion arrow per driver.

Existing tests for the resist model, PSF synthesis, multihead model,
fleet economics, and 3D pipeline continue to pass.

## License

Proprietary. Patent pending. (See `README.md` for scope and
limitations.)
