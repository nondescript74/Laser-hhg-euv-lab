# Patent-Positioning Memo — Laser-HHG-EUV Lab ↔ vdw-polaritonics-lab

**Date:** 2026-04-16
**Repo posture:** hardened epistemic-tiered architectural modeling lab
**Scope:** prosecution-oriented, not marketing
**Intended audience:** drafting counsel; internal technical review

---

## 0. Starting premises (locked)

1. `Laser-hhg-euv-lab` is an epistemically tiered architectural modeling lab. It is not a device demonstration and it is not an industrial EUV source claim.
2. The strongest defensible bridge between the two repos is **front-end driver conditioning** (spectral and temporal shaping of the driver laser feeding the HHG stage) — not any claim that the vdW cavity itself operates at EUV.
3. Generated flux, beamline transmission, and delivered flux are kept in three separate reportable planes. No plane is ever reported without the other two and their respective tier labels.
4. The two repos are **complementary architectural layers coupled through a shared control plane**, not a single demonstrated integrated device.

Everything below is derived from these four premises. If any premise drifts, the claim structure below must be re-evaluated.

---

## 1. Supportability Map

### Strongly supportable (claim territory)

- A **programmable optical-transfer-function control plane** as an architectural construct that spans two physically distinct stages: a DUV intracavity modulation stage and a driver-front-end conditioning stage that feeds an HHG stage.
- **Driver-front-end spectral and temporal conditioning** as the interface between the two repos. This is the load-bearing claim surface: it is enabled by well-established pulse-shaping art, it is where the vdW-cavity programmable-modulation analogy extends cleanly, and it is upstream of any EUV assertion.
- **Analytical relationships** already implemented and tested:
  - Cutoff relation E_cut = 3.17·U_p + I_p
  - Single-atom efficiency anti-scaling λ^−(5…6.5)
  - Phase-matching proxy via a critical ionization-fraction ceiling η_c
  - Beamline transmission as R^N · T^M (multilayers and foils)
- **Generated / transmitted / delivered** as a formal three-part reporting construct. The `FluxBudget` dataclass is the enabling implementation; the claim surface is the construct, not the numbers.
- The **wavelength-bridge representation** as an architectural narrative (driver bands, harmonic cascade, DUV/VUV/EUV/SXR regions, both repos on one axis).
- **Epistemic-tier labeling** as a reporting-discipline element of the control plane. The `TierLabel` construct is unusual, enabled, and claimable as a method element.

### Architecture-level only (non-enabling disclosure; include in spec, exclude from claims)

- Multi-head writer-array packaging concept.
- Fleet economics sensitivity.
- 11-DOF writer-head exploded view.
- The 3D pipeline rendering as a whole.
- The vdw-polaritonics-lab ↔ HHG-lab integration diagram, to the extent it could be read as a coupled physical assembly.

These are useful portfolio context — they show a consistent architectural worldview — but none of them is enabled to device-demonstration tier.

### Must be excluded from claims

- Any statement that the vdW cavity operates at or near EUV.
- Any numerical delivered flux, brightness, dose, or throughput as claim language. Those are `PARAMETERIZED` or illustrative, never measured.
- Any implication that gas-jet HHG can substitute for LPP in EUV HVM lithography.
- Any integrated-device claim that implies the two repos describe a single built apparatus.
- Any conflation of vdW intracavity DUV modulation with cavity-enhanced HHG (CE-HHG, JILA/MPQ lineage). Distinct prior art; conflation is a credibility and prior-art liability.
- Any PSF, resist, or aerial-image numerical result as a performance claim.

---

## 2. Claim Architecture

### Independent system-claim concept

A programmable-optical-transfer-function system comprising:

- a first optical control stage configured to apply a programmable spectral and temporal transfer function at a DUV wavelength through an intracavity modulation element;
- a second optical control stage configured to apply a programmable spectral and temporal transfer function to a driver pulse train at a near- or mid-infrared wavelength prior to entry of the driver pulse train into a high-harmonic-generation stage;
- a control-plane logic that expresses the transfer functions applied by the first and second stages in a common parameter space and selects them jointly;
- a reporting subsystem configured to emit, for a selected operating point, a tuple comprising a source-side estimate, a transmission-product estimate, and a delivered-side estimate, each accompanied by a tier label drawn from a predetermined tier set.

The load-bearing novelty is the **control plane plus tier-labeled reporting**, not the photon throughput. This is the structural choice that keeps the claim out of range of LPP-flux attacks and out of range of CE-HHG prior art.

### Independent method-claim concept

A method for operating a multi-stage laser-driven photon-source architecture, the method comprising:

- receiving a specification of a programmable optical transfer function expressed in a shared parameter space;
- decomposing the specification into a first parameter set governing an intracavity DUV modulation stage and a second parameter set governing a driver-front-end conditioning stage that feeds a downstream high-harmonic-generation stage;
- selecting the second parameter set such that a cutoff-energy relation and a phase-matching proxy associated with the harmonic-generation stage are driven to predetermined operating points;
- applying each parameter set through a shared control-plane interface to the respective stage;
- reporting the resulting operating point as a tier-labeled tuple of a generated-side estimate, a beamline-transmission product, and a delivered-side estimate.

### Dependent-claim buckets

- **Driver-conditioning modalities:** spectral-phase engineering; pulse-duration control; two-color synthesis; carrier-envelope-phase stabilization; chirped-pulse envelope engineering; MIR-OPCPA-driven conditioning.
- **Analytical-anchor dependents:** the cutoff estimate is computed from E_cut = 3.17·U_p + I_p using a driver intensity derived from the conditioned pulse; the single-atom yield is computed from a λ^−(5…6.5) anti-scaling anchored to a stated literature baseline.
- **Phase-matching dependents:** the second parameter set is selected such that an estimated ionization fraction remains below a critical value η_c.
- **Beamline-coupling dependents:** the delivered-side estimate is computed as R^N·T^M applied to a source-side literature anchor; the reflectivity R and transmission T are those of Mo/Si multilayer mirrors and metal foil filters respectively.
- **Reporting-discipline dependents:** each reported photon estimate is accompanied by a tier label drawn from a set comprising at least an analytical tier, a parameterized tier, an architectural tier, and a literature-quoted tier; the controller refuses to emit a delivered-side estimate in the absence of the corresponding source-side and transmission-side estimates.
- **DUV-stage dependents:** the intracavity modulation element comprises a two-dimensional-material heterostructure operating at a DUV wavelength below its EUV absorption edge; the element does not operate at EUV wavelengths; the element is not configured as an enhancement cavity for the driver of the HHG stage.
- **Wavelength-bridge dependents:** the control-plane logic presents the first and second stages on a common wavelength axis together with a representation of the harmonic cascade produced by the HHG stage.
- **Defensible use-case dependents:** coherent diffractive imaging; ptychography; actinic EUV mask inspection; angle-resolved photoemission. (High-volume EUV lithography is **not** listed.)

---

## 3. Specification-Paragraph Candidates

### System architecture

In one embodiment, a programmable optical-transfer-function system comprises two physically distinct optical control stages coupled only through a shared control-plane logic. The first stage operates at a deep-ultraviolet wavelength, for example 193 nanometers or 248 nanometers, and applies a programmable spectral and temporal modulation through an intracavity element within a DUV resonator. The second stage operates at a driver-laser wavelength in the near- or mid-infrared, for example approximately 800 nanometers, approximately 1030 nanometers, or a wavelength between approximately 1800 nanometers and 3000 nanometers, and applies a programmable spectral and temporal modulation to a pulse train that subsequently drives a high-harmonic-generation stage. The two stages are not required to share a common optical path and are not required to be physically co-located. What is shared is a parameterization of the applied transfer functions and a reporting convention for the controller's estimated output.

### Driver-conditioning interface

In the driver-conditioning stage, the programmable transfer function acts on the driver pulse prior to the pulse's entry into the gas-target chamber of the high-harmonic-generation stage. Conditioning operations include, in various embodiments, spectral-phase engineering, pulse-duration control, two-color synthesis, carrier-envelope-phase stabilization, and chirped-pulse-envelope adjustment. Each conditioning operation is expressed in a parameter space common to the DUV intracavity stage, so that the control-plane logic that selects an intracavity DUV waveform also selects the driver-side waveform that determines the subsequent harmonic response. The harmonic response is characterized analytically by a cutoff relation of the form E_cut = 3.17·U_p + I_p and by a phase-matching proxy expressed as a ceiling on an estimated ionization fraction, both of which are functions of the conditioned driver waveform.

### Wavelength-bridge narrative

The DUV intracavity stage and the driver-conditioned harmonic-generation stage occupy distinct regions of the optical spectrum. The DUV stage operates at approximately 193 nanometers to 248 nanometers. The driver wavelength of the harmonic-generation stage lies in the range of approximately 800 nanometers to 3000 nanometers, and the harmonic cascade produced by the stage populates orders spanning the vacuum-ultraviolet, extreme-ultraviolet, and soft-X-ray bands, for example down to a cutoff near 13.5 nanometers. In one representation, the two stages are displayed on a single wavelength axis together with the analytical cutoff relation of the harmonic-generation stage, thereby illustrating the span and the coupling of the two control planes. The representation is a control-plane narrative; it does not imply that the DUV stage operates at extreme-ultraviolet wavelengths, and it does not imply that a two-dimensional-material modulation element of the first stage operates beyond its native absorption edge.

### Epistemic-safe use of simulation outputs

Each quantitative output produced by the controller carries a tier label drawn from a predetermined set, for example a set comprising a closed-form analytical tier, a parameterized small-system tier, an architectural tier, and a literature-quoted tier. Photon-flux outputs are reported as a three-part tuple comprising a source-side estimate drawn from cited literature anchors, a beamline-transmission product of the form R^N·T^M computed analytically from stated optical-element properties, and a delivered-side estimate formed as the arithmetic product of the two. No output is reported as a delivered device-level photon flux in the absence of its corresponding source-side and transmission-side values and their respective tier labels. In certain embodiments, the reporting discipline is a condition on an export interface of the controller and is enforceable as an element of the system.

---

## 4. Claim-Risk Exclusions (language traps)

### EUV-source overclaim

- **Avoid:** "an EUV source comprising …"; "a system that produces EUV lithography-grade flux"; any language that positions the overall apparatus as a replacement or alternative to laser-produced-plasma EUV sources.
- **Safe:** "a harmonic-generation stage configured to produce harmonic orders within one or more of the vacuum-ultraviolet, extreme-ultraviolet, and soft-X-ray bands." Bounded; covers the defensible use cases (CDI, ptychography, actinic inspection, ARPES); does not cover HVM lithography.

### Integrated-device implication

- **Avoid:** "wherein the DUV stage and the HHG stage are integrated into a single optical assembly"; drawings that depict the vdW cavity and the HHG chamber sharing a resonator, a mirror, or an optical path.
- **Safe:** "the first stage and the second stage are coupled through the control-plane logic but are not required to share an optical path." This preserves portfolio coverage for physically decoupled architectures while preventing a non-enablement rejection for the integrated case the repo does not demonstrate.

### Flux / brightness implication from analytical models

- **Avoid:** "wherein the system delivers X photons per second" when X is derived only from parameterized or analytical scaling. Analytical outputs govern shape and scaling; they do not establish magnitude.
- **Safe:** "wherein the controller reports an estimated delivered photon count as the product of a literature-anchored source-side value and an analytically computed transmission product, each labeled with its epistemic tier." Claims the reporting construct, not the number.

### CE-HHG / vdW-cavity conflation

- **Avoid:** any language that could be read as equating the DUV intracavity modulation element with a femtosecond enhancement cavity at the NIR driver wavelength. Cavity-enhanced HHG is a distinct, demonstrated architecture with substantial prior art lineage (JILA, MPQ, since 2005).
- **Safe:** state explicitly that the DUV stage operates below the absorption edge of the two-dimensional material used in the modulation element, that the DUV stage does not function as an enhancement cavity for the driver of the HHG stage, and that the DUV stage is not in optical series with the HHG driver path.

### PSF / resist numerical performance implication

- **Avoid:** claiming specific resolution, line-edge roughness, dose latitude, or throughput values derived from the PSF-synthesis or resist modules.
- **Safe:** omit PSF and resist modules from the claim set entirely. Include them only as illustrative downstream consumers of the controller's output, and label any figures derived from them as architectural or parameterized.

---

## 5. Recommended Next Drafting Steps

1. **Provisional framing memo (internal, not filed).** One page that names the two claim pillars — (a) the shared control plane across two physically distinct stages and (b) the tier-labeled reporting discipline — and names everything else as background. Purpose: align drafting counsel on the claim-vs-background line before a word of claim language is drafted.

2. **Lock Figure 1 as the wavelength-bridge figure.** It is the one figure that performs the defensive work of placing both stages on a single axis without implying physical integration. 3D pipeline, multihead, fleet, PSF, and 11-DOF views drop to supporting or illustrative status.

3. **Draft an independent apparatus claim and an independent method claim at the control-plane level,** using the language in Section 2. Keep both silent on photon-flux magnitude and silent on lithography applicability. Accept a narrower independent claim in exchange for broad, stable dependent coverage.

4. **Layer dependent claims by modality, by analytical anchor, by phase-matching ceiling, by beamline-transmission product, and by tier-labeled reporting.** This is where portfolio breadth is built without re-introducing overclaim risk.

5. **Bound use-case dependents to the defensible set only** (CDI, ptychography, actinic mask inspection, ARPES). Do not add HVM-lithography dependents. Including them invites a written-description attack on the entire claim set and weakens the apparatus claims by implying they require LPP-class flux.

6. **Run a prior-art landscape pass** on (a) JILA / MPQ CE-HHG patents, (b) 2D-material intracavity modulator and saturable-absorber patents at DUV/NIR, and (c) pulse-shaping-for-HHG patents. Amend the spec to explicitly disclaim operation of the DUV element as a driver enhancement cavity and to explicitly disclaim any integrated single-cavity embodiment. Cheap insurance.

7. **Treat the tier-labeled reporting discipline as its own independent method-claim track,** not as a dependent of the apparatus claim. If the apparatus track is narrowed on prosecution, the reporting-discipline track remains standalone and novel. The `TierLabel` and `FluxBudget` constructs in the repo are the enabling implementation.

8. **Adopt a drafting rule for the specification:** every embodiment paragraph ends with one sentence stating what the embodiment does not demonstrate (for example, "this embodiment does not establish a delivered EUV-lithography-source flux"). This is the prose equivalent of the repo's epistemic banners and is the single most effective protection against the overclaim vectors identified in Section 4.

---

## Appendix A — Module ↔ Claim-Surface Mapping

| Module | Tier implemented | Claim-surface role |
| --- | --- | --- |
| `backend/epistemic.py` | n/a (infrastructure) | Enabling implementation of tier-labeled reporting (Claim Section 2, reporting-discipline dependents) |
| `backend/hhg_analytical.py` | `ANALYTICAL` | Analytical-anchor dependents (cutoff, efficiency anti-scaling, phase-matching proxy, beamline transmission) |
| `backend/wavelength_bridge.py` | `ARCHITECTURE` | Figure 1; wavelength-bridge narrative paragraph |
| `backend/optical_pipeline.py` (`FluxBudget`) | mixed | Generated/transmitted/delivered three-part reporting construct; enabling implementation for epistemic-safe-use paragraph |
| `backend/hhg_model.py` | compatibility shim | Not a claim surface |
| `backend/visualization_3d.py`, `visualization_multihead.py`, `visualization_fleet.py`, `visualization_11dof.py` | `ARCHITECTURE` | Supporting figures only; not claim surfaces |
| `backend/psf_synthesis.py`, `backend/lithography_model.py`, `backend/resist_model.py`, `backend/euv_psf.py`, `backend/dose_engine.py` | `PARAMETERIZED` | Excluded from claims (Section 4, PSF/resist trap) |
| `backend/citations.py`, `backend/references.py` | `LITERATURE` | Supports source-side anchors in reporting construct |

---

## Appendix B — Open drafting questions for counsel

1. Should the tier-labeled reporting discipline be drafted as a system claim (controller + export interface) or as a method claim (steps performed by a controller)? Method is likely safer against § 101 scrutiny; system is likely broader.
2. Should the defensible use-case dependents be drafted in the same application or in divisionals? Divisionals isolate prosecution risk but increase cost.
3. How explicitly should the spec disclaim CE-HHG? A hard disclaimer is defensive; a softer "in one embodiment, the DUV stage is not configured as an enhancement cavity for the driver" preserves design-around space.
4. Does the foreign filing strategy assume EPO-style "technical effect" support? If so, the tier-labeled reporting claim needs an EPO-friendly framing as a control-engineering feature, not a presentation-of-information feature.

*End of memo.*
