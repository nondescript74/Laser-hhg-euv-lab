# Patent Counsel Handoff Packet

**Matter:** Laser-HHG-EUV Lab ↔ vdw-polaritonics-lab — programmable optical-transfer-function control plane.
**Date:** 2026-04-16
**Audience:** drafting counsel.
**Repository:** `Laser-hhg-euv-lab` (main branch).
**Source documents in same repo:** `patent_positioning_2026-04-16.md` (architecture memo); `patent_claim_priority_brief_2026-04-16.md` (drafting brief); `hhg-euv-lab-complete.pdf` (technical background).

This packet is self-contained. The three source documents are the depth record; this packet is what counsel works from.

---

## 1. Executive Summary (one page)

**What this is.** A patent package derived from an epistemically tiered architectural modeling lab. The repository models the HHG / EUV generation chain as a simulation-and-control-plane study; it does not demonstrate a device, does not assert an industrial EUV source, and separates generated / transmitted / delivered photon flux into three reportable planes.

**What is claimed.** A programmable optical-transfer-function control plane operating across two physically distinct optical stages — a DUV intracavity modulation stage at 193/248 nm and a driver-front-end conditioning stage at 800 / 1030 / 1800–3000 nm upstream of an HHG gas target — coupled only through shared parameter space and controller logic, together with controller-enforced tier-labeled three-part flux export with emission-inhibit gating.

**What is not claimed.** Photon-flux magnitude; lithography applicability; EUV-source-level device operation; integrated single-cavity / single-optical-path embodiments; 2D-material modulator operation beyond a native absorption edge; any conflation with cavity-enhanced HHG (CE-HHG).

**Claim architecture at a glance.** Two independent tracks, each with a backup rung. System track: Rung 1 is the two-stage controller with joint selection under cutoff-target and η_c constraints plus gated tier-labeled export; Rung 2 drops the DUV stage and lives on driver conditioning plus gated export. Method track: Rung 3 mirrors Rung 1 as a method; Rung 4 mirrors Rung 2.

**Survivability.** Load-bearing surfaces are (a) controller-enforced tier-labeled export with emission-inhibit gating and (b) joint parameter-set selection under an analytical cutoff and an η_c phase-matching proxy. Pulse-shaping modalities live only as dependents tightly coupled to those constraints. PSF / resist / multihead / fleet material is spec-only.

**Prior-art pressure.** Four clusters: CE-HHG (disclaim in claim and spec with not-in-optical-series language); pulse-shaping for HHG (dependents only, tied to constraints); vdW / 2D-material intracavity optical control (claim role only, DUV-below-absorption-edge restriction); simulation / provenance reporting (§101 pressure managed by controller-enforced gating and photon-source-flux-bookkeeping domain specificity).

**Immediate drafting actions.** (i) Lock the wavelength-bridge figure as Figure 1. (ii) Commission a targeted landscape pull on the four prior-art clusters. (iii) Draft the independent apparatus claim and the independent method claim at the control-plane level using the Rung 1 and Rung 3 skeletons in Section 2. (iv) Draft the tier-labeled reporting method claim as its own independent track, not as a dependent of the apparatus track.

**Drafting rule.** Every embodiment paragraph ends with one sentence naming what the embodiment does not demonstrate. Every figure caption ends with one sentence naming what the figure does not represent. These are the prose and caption analogs of the repo's epistemic-tier banners and constitute the single most effective written-description defense.

---

## 2. Claim-Priority Brief

### 2.1 Survivability ranking

**Strongest — independent claim territory:**
- Controller-enforced tier-labeled three-part flux export with emission-inhibit gating.
- Joint DUV-stage / driver-stage parameter selection under an analytical-cutoff constraint and an η_c phase-matching-proxy constraint.

**Medium — dependents, tightly coupled to the strongest surfaces:**
- Two-stage architecture with explicit "not in optical series" phrasing carried into the claim body.
- Driver-conditioning modalities (SLM, AOPDF, CEP lock, two-color, chirped envelope, MIR-OPCPA band) each tied to a specific controller-side constraint.
- R^N · T^M transmission-product composition as a computed component of the export tuple.

**Weak — specification only, never in claims:**
- Wavelength-bridge figure as a claim anchor (kept as Figure 1, narrative only).
- Single-atom λ^−(5…6.5) exponent range as a numerical claim element.
- Standalone statement of E_cut = 3.17 · U_p + I_p (present only inside a constraint-computation step).
- 3D pipeline, multihead packaging, fleet economics, 11-DOF writer-head view, PSF synthesis, resist process.

### 2.2 Fallback ladder (element skeletons)

**Rung 1 — primary independent system claim.** (i) memory storing shared parameter space and predetermined tier set; (ii) first-stage interface to DUV intracavity modulation stage operating at a DUV wavelength; (iii) second-stage interface to driver-front-end conditioning stage upstream of an HHG gas target; (iv) selection logic computing both parameter sets jointly from the shared parameter space subject to ≥1 cutoff-target constraint and ≥1 phase-matching-proxy (η_c) constraint; (v) export interface emitting a three-part tier-labeled tuple (literature-anchor source-side; analytical transmission-product; parameterized delivered-side); (vi) emission-inhibit gate on missing components; (vii) first and second stages not in optical series.

**Rung 2 — backup independent system claim.** Drops the DUV stage. Elements: memory; driver-stage interface; selection logic under both constraints; three-part tier-labeled export; emission-inhibit gate. Survives if Rung 1 is narrowed on CE-HHG or intracavity-modulator art.

**Rung 3 — primary independent method claim.** Steps: (a) receive specification expressed in shared parameter space stored in controller memory; (b) compute DUV-stage and driver-stage parameter sets jointly under both constraints; (c) transmit each parameter set to its respective stage via a controller interface; (d) compute three-part photon-estimate tuple; (e) associate each part with a tier label drawn from a predetermined tier set in controller memory; (f) emit tuple through an export interface; wherein delivered-side emission is gated on presence of source-side, transmission-product, and their tier labels.

**Rung 4 — backup independent method claim.** Reduced steps: driver-stage selection under both constraints; three-part tier-labeled tuple computation; gated export emission. Survives if Rung 3 is narrowed.

### 2.3 Tier-labeled reporting as machine-governed

The label is a field on a controller data object, assigned at construction time, enforced at an export interface, and gated by an emission-inhibit rule tied to missing components. Claim verbs: `emit`, `transmit`, `store`, `associate`, `inhibit emission of`, `gate on`, `refuse to emit`. Never: `display`, `show`, `present`, `render`, `annotate`, `user interface`. This framing manages §101 pressure in the US and supports a technical-effect framing in the EPO anchored to the controller export gate and the photon-source operational domain.

### 2.4 Prior-art pressure table

| Cluster | Likely attack | Best narrowing distinction | Posture |
| --- | --- | --- | --- |
| CE-HHG / NIR enhancement cavity (JILA, MPQ, 2005→) | §102/§103 on any claim reading on a cavity upstream of or enclosing the HHG target; obviousness bridge to swap the NIR cavity element for a DUV intracavity stage | DUV-only operation; DUV stage not in optical series with the HHG driver path; DUV stage does not enhance, build up, or recirculate the driver pulse at the HHG target | Disclaim in spec; carry decoupling phrase into the independent claim and key dependents |
| Pulse-shaping for HHG (SLM phase shaping; AOPDF / Dazzler; two-color ω + 2ω; CEP-stabilized driver; feedback-optimized HHG) | §103 on each modality individually; "shaped driver + reporting overlay is obvious" bridge | Require the shaping to be a product of joint selection with the DUV-stage parameter set from a shared parameter space under an explicit cutoff-target value and an explicit η_c ceiling | Claim modalities only as dependents; never as an independent element |
| vdW / 2D-material intracavity optical control (graphene / MoS₂ / hBN / BP saturable absorbers, modulators, polariton-cavity devices) | §102/§103 on the modulator element broadly | Claim only the role of the DUV stage in the shared control plane, not the modulator element; restrict to DUV operation below the EUV absorption edge; disclaim enhancement-cavity function | Claim role as dependent; disclose element detail in spec; disclaim enhancement-cavity function everywhere |
| Simulation / provenance / uncertainty-label reporting (lineage frameworks; provenance systems; uncertainty-propagating scientific software) | §101 abstract-idea / presentation-of-information; §102 generic provenance labeling | Predetermined tier set in controller memory; controller-enforced emission-inhibit gate on missing components; specific technical domain (photon-source flux bookkeeping) with the three-part construction rule (literature anchor; analytical transmission; parameterized product) | Claim as independent method track with controller-enforced gating; frame every instance as controller operation with a refusal state |

### 2.5 Dependents to keep on narrowing

Keep (survive when the independent claim narrows):

- Emission-inhibit gating.
- η_c phase-matching-proxy ceiling.
- Cutoff-target constraint.
- Literature-anchor source-side tier.
- Analytically computed R^N · T^M transmission-product with named materials (Mo/Si multilayer count N; metal-foil count M).
- Defensible application endpoints: CDI, ptychography, actinic EUV mask inspection, ARPES. (HVM lithography is never listed.)
- Physical-decoupling phrase ("first and second stages not in optical series") as a dependent in addition to the independent claim body.
- DUV-below-absorption-edge restriction.
- Enumerated four-tier set (analytical, parameterized, architectural, literature-quoted).
- Controller refusal on non-compliant specification input.

Drop first on narrowing: individual pulse-shaping modality dependents (SLM, AOPDF, CEP, two-color, chirped envelope, MIR-OPCPA band). These live in spec as background if pulse-shaping prior-art pressure appears.

---

## 3. Exclusions / Language Traps Appendix

### 3.1 Hard exclusions — never in any claim or dependent

- Photon-flux magnitudes, brightness, dose, throughput.
- EUV-source apparatus naming: "EUV source", "programmable EUV source", "tabletop EUV source", "coherent EUV source".
- Lithography applicability: "lithography", "wafer", "HVM", "patterning".
- Integrated-device phrasing: "integrated into a single optical assembly", "single cavity containing both stages", "co-located stages".
- "Cavity-enhanced" in any form for the DUV stage.
- 2D-material modulation element operation beyond its native absorption edge.
- Numerical resolution, LER, dose latitude, or throughput derived from PSF or resist modules.
- λ^−(5…6.5) exponent range as a numerical claim element.
- E_cut = 3.17 · U_p + I_p as a standalone claim element (appears only inside a constraint-computation step).

### 3.2 Prohibited verbs and phrases when referring to tier labels

Never: `display`, `show`, `present`, `render`, `visualize`, `flag`, `annotate`, `indicate to a user`, `user interface`.
Always: `emit`, `transmit`, `store`, `associate`, `inhibit emission of`, `gate on`, `refuse to emit`.

### 3.3 Prohibited competitive-positioning phrases

Never: `replaces`, `alternative to`, `comparable to`, `equivalent to`, `on par with`, whenever placed near `LPP`, `ASML`, `EUV source`, `lithography`, `HVM`, `intermediate focus`.

### 3.4 Six language traps with safe substitutes

1. **EUV-source overclaim.** Trap: "an EUV source comprising …" / "a system that produces EUV lithography-grade flux". Safe: "a harmonic-generation stage configured to produce harmonic orders within one or more of the VUV, EUV, and soft-X-ray bands".

2. **Integrated-device implication.** Trap: "integrated into a single optical assembly"; drawings of a shared cavity, mirror, or optical path between the stages. Safe: "the first stage and the second stage are coupled through the selection logic and are not in optical series".

3. **Flux / brightness implication from analytical models.** Trap: "wherein the system delivers X photons per second" where X is derived from PARAMETERIZED or ANALYTICAL math. Safe: "the controller reports an estimated delivered photon count as the product of a literature-anchored source-side value and an analytically computed transmission product, each labeled with its epistemic tier".

4. **CE-HHG / vdW-cavity conflation.** Trap: language that could be read as equating the DUV intracavity element with a femtosecond enhancement cavity at the NIR driver wavelength. Safe: explicit disclaimer in claim and spec that the DUV stage does not enhance, build up, or recirculate the HHG driver pulse, and that the DUV stage is not in optical series with the driver path.

5. **PSF / resist numerical performance implication.** Trap: claiming specific resolution, LER, dose latitude, or throughput from PSF-synthesis or resist modules. Safe: omit PSF and resist entirely from the claim set; include only as architectural illustrations of downstream consumers of controller output.

6. **§101 presentation-of-information framing for tier labels.** Trap: describing tier labels as displayed, shown, or user-facing. Safe: frame as a controller-enforced export-interface gate with emission inhibit on missing components; tie to a stored predetermined tier set; tie to the photon-source flux-bookkeeping domain.

### 3.5 Per-paragraph and per-caption drafting rule

Every embodiment paragraph ends with one sentence naming what the embodiment does not demonstrate. Every figure caption ends with one sentence naming what the figure does not represent. Representative closers:

- Embodiment closer: "This embodiment does not establish a delivered EUV-lithography-source flux and does not demonstrate operation of a two-dimensional-material modulation element beyond its native absorption edge."
- Figure 1 caption closer: "This figure places both stages on a common wavelength axis as a control-plane narrative; it does not represent a physical optical path between the stages and does not assert operation of a two-dimensional-material modulation element beyond its native absorption edge."

These closers are the prose analog of the repository's epistemic-tier banners. They are the single most effective defense against written-description and overclaim attacks.

---

## 4. Figure List — anchored by the wavelength bridge

### Figure 1 — Wavelength bridge (keystone)

- **Role.** Defensive keystone. The single figure on which the claim set depends for narrative coherence. Places the two stages on one wavelength axis with the HHG cascade.
- **Content.** Driver bands (Ti:Sa 800 nm; Yb:YAG 1030 nm; MIR OPCPA 1800–3000 nm); DUV / VUV / EUV / SXR regions; operating region of `vdw-polaritonics-lab` (193 / 248 nm); operating region of this repo (HHG plateau ~60 → ~13.5 nm); industrial anchors (DUV 193/248; actinic 30 nm; ASML LPP 13.5 nm).
- **Must not imply.** That the DUV stage operates at EUV. That the two stages share an optical path. That any 2D-material modulation element operates beyond its native absorption edge.
- **Tier.** ARCHITECTURE.
- **Source.** `backend/wavelength_bridge.py`.

### Figure 2 — Controller architecture (supporting; new)

- **Role.** Schematic of the controller apparatus: stored shared parameter space; first-stage and second-stage interfaces; joint selection logic with labeled cutoff-target and η_c constraints; export interface with emission-inhibit gate.
- **Content.** Data-flow diagram only; no physical optics.
- **Must not imply.** Any physical coupling between the two stages beyond the controller. Any specific photon-flux value.
- **Tier.** ARCHITECTURE.
- **Source.** New figure; to be drafted from the Rung 1 claim skeleton in Section 2.2.

### Figure 3 — Three-part flux-budget reporting construct (supporting)

- **Role.** Tier-labeled tuple rendered as a controller data-object diagram with the emission-inhibit gate depicted as a controller state.
- **Content.** Three fields (source-side / transmission-product / delivered-side) with tier labels (literature-anchor / analytical / parameterized); the emission-inhibit gate on missing components.
- **Must not imply.** Any specific photon-flux value. Any user-facing display semantics.
- **Tier.** ARCHITECTURE for the mechanism; LITERATURE as origin label on source-side; ANALYTICAL as origin label on transmission-product.
- **Source.** `backend/optical_pipeline.py` (`FluxBudget`, `compute_flux_budget()`); `backend/epistemic.py` (`TierLabel`).

### Figure 4 — Constraint surfaces (supporting; optional)

- **Role.** Illustrative plot of the two constraint surfaces used by the joint selection logic: cutoff-energy relation E_cut = 3.17 · U_p + I_p as a function of driver intensity; η_c ceiling as a function of ionization-fraction estimate.
- **Content.** Constraint geometry; representative operating points; no device-level numbers.
- **Must not imply.** Any device-level flux value; any specific driver-pulse achievement.
- **Tier.** ANALYTICAL.
- **Source.** `backend/hhg_analytical.py`.
- **Keep/drop rule.** Keep if counsel wants an analytical anchor figure; drop if the independent claim recites both constraints adequately in prose.

### Figures demoted to background or omitted from the application

- 3D pipeline rendering (`backend/visualization_3d.py`) — background only.
- Multihead packaging view (`backend/visualization_multihead.py`) — background only.
- 11-DOF writer-head exploded view (`backend/visualization_11dof.py`) — background only.
- Fleet economics sensitivity (`backend/visualization_fleet.py`) — omit from the patent-application figure set; economics do not belong in this claim structure's spec.
- PSF synthesis example (`backend/visualization_psf.py`) — demote to background; never a claim anchor.
- Resist-process pipeline (`backend/visualization.py`) — demote to background; never a claim anchor.

### Figure-caption discipline (enforced per Section 3.5)

Every figure caption ends with one sentence naming what the figure does not represent. See representative closers in Section 3.5.

---

*End of handoff packet.*
