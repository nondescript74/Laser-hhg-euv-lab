# Patent Claim-Priority Drafting Brief

**Companion to:** `patent_positioning_2026-04-16.md`
**Date:** 2026-04-16
**Audience:** drafting counsel; internal technical review
**Purpose:** convert the architecture memo into a drafting brief optimized for claim survivability, fallback structure, and exclusion discipline

---

## Locked premises (verbatim)

1. The load-bearing claim surface is the programmable optical-transfer-function control plane across two physically distinct stages plus tier-labeled three-part flux reporting.
2. The two stages are a DUV intracavity modulation stage at 193/248 nm and a driver-front-end conditioning stage at 800 / 1030 / 1800–3000 nm, upstream of an HHG gas target.
3. The stages are coupled through shared parameter space and control logic, not through a shared optical path.
4. Claims must stay silent on photon-flux magnitude and silent on lithography applicability.
5. The tier-labeled reporting track must be framed as a machine-governed control / export constraint, not merely presentation of information.

---

## 1. Claim-priority ranking (by survivability)

### Strongest (draft independent claims here)

- **Controller-enforced, tier-labeled, three-part flux export with emission-inhibit gating.** Frames the `TierLabel` + `FluxBudget` implementation as a controller export-interface gate: the controller refuses to emit a delivered-side estimate in the absence of a literature-anchored source-side estimate and an analytically computed transmission-product estimate, each carrying its own tier label from a predetermined tier set stored in controller memory. This reads as machine operation, not presentation; the gating logic is the novel technical feature; §101 pressure is manageable because the gate is controller-enforced on an export interface, not a labeling step.
- **Joint selection of a DUV-stage parameter set and a driver-stage parameter set from a shared parameter space, subject to at least one analytical-cutoff constraint and at least one phase-matching-proxy constraint on the downstream HHG target.** Narrow, enabled, and specific. The two constraints (cutoff-target and η_c ceiling) are the survival anchors that distinguish this from generic pulse shaping.

### Medium (survive only with tight coupling to the strongest surfaces)

- **Two-stage control-plane architecture with explicit physical-decoupling language** ("coupled through shared parameter space; not required to share an optical path; the DUV stage is not in optical series with the HHG driver path"). Novel as posed, but adjacent to CE-HHG and intracavity-modulator art. Must be drafted with the decoupling language in the claim, not just the spec, to survive §103.
- **Driver-conditioning modalities (SLM spectral phase, AOPDF, two-color, CEP lock, chirped envelope, MIR-OPCPA driver band).** Densely covered art at the modality level. Survivable only as dependents that require the specific controller-side constraint (cutoff-target or η_c ceiling) to be applied through the shaping operation.
- **Analytical transmission product R^N·T^M as the computed transmission component of the export tuple.** Textbook math; survives only as an implementation detail of the gated-export claim, not as a standalone element.

### Weak / background only (spec, not claims)

- Wavelength-bridge figure. Presentation; Figure 1 of the spec; not a claim surface.
- Single-atom λ^−(5…6.5) anti-scaling. Numerical exponent range sourced from literature parameterization; §112(a) written-description risk if claimed.
- Analytical cutoff E_cut = 3.17·U_p + I_p as a standalone relation. Textbook; appears only as a constraint-computation step inside the independent claims, never as a claim surface in itself.
- 3D pipeline rendering, multihead packaging, fleet economics, 11-DOF writer-head view.
- PSF synthesis and resist process modules. Spec background only; actively excluded from claims per Section 4 of the prior memo.

---

## 2. Fallback ladder

### Reframing of tier-labeled reporting as machine-governed (applied to every rung)

The tier label is **not** a display; it is a field on a controller data object stored in memory, associated with the computed estimate at construction time (per `FluxBudget` / `TierLabel`), and enforced by the controller's export interface. The export interface has a **gate** that inhibits emission of the delivered-side estimate in the absence of the source-side estimate, the transmission-product estimate, and their respective tier labels. The gate is a machine-actionable refusal condition — an operational state of the controller — not a user-facing warning. Downstream consumers of the controller output consume the tuple, not the scalar. All claim language uses `emit`, `transmit`, `inhibit`, `refuse`, and `gate`; never `display` or `show`.

### Rung 1 — Primary independent SYSTEM claim

A controller for a two-stage laser photon-source architecture, comprising:

- a memory storing a shared parameter space and a predetermined tier set;
- a first-stage interface configured to transmit a DUV-stage parameter set to an intracavity modulation stage operating at a DUV wavelength;
- a second-stage interface configured to transmit a driver-stage parameter set to a driver-front-end conditioning stage upstream of a high-harmonic-generation gas target;
- selection logic configured to compute the first-stage parameter set and the second-stage parameter set jointly from the shared parameter space subject to at least one cutoff-target constraint derived from an analytical cutoff relation and at least one phase-matching-proxy constraint on an estimated ionization fraction of the gas target;
- an export interface configured to emit, for a selected operating point, an output tuple comprising a source-side estimate carrying a tier label of a literature-anchor tier, a transmission-product estimate carrying a tier label of an analytical tier, and a delivered-side estimate carrying a tier label of a parameterized tier;
- wherein the export interface is configured to inhibit emission of the delivered-side estimate in the absence of the source-side estimate, the transmission-product estimate, and their respective tier labels; and
- wherein the first stage and the second stage are coupled through the selection logic and are not in optical series with one another.

### Rung 2 — Backup independent SYSTEM claim (drops the two-stage coupling)

A controller for a laser photon-source driver stage upstream of a high-harmonic-generation gas target, comprising:

- a memory storing a parameter space and a predetermined tier set;
- a driver-stage interface configured to transmit a driver-stage parameter set to a driver-front-end conditioning stage;
- selection logic configured to compute the driver-stage parameter set from the parameter space subject to at least one cutoff-target constraint derived from an analytical cutoff relation and at least one phase-matching-proxy constraint on an estimated ionization fraction of the gas target;
- an export interface configured to emit a three-part tier-labeled tuple comprising a literature-anchor-tier source-side estimate, an analytical-tier transmission-product estimate, and a parameterized-tier delivered-side estimate;
- wherein the export interface is configured to inhibit emission of the delivered-side estimate in the absence of the other two components and their tier labels.

This rung survives if the two-stage coupling language is attacked on CE-HHG / intracavity prior art. It lives entirely on driver conditioning + gated tier-labeled reporting.

### Rung 3 — Primary independent METHOD claim

A method performed by a controller of a two-stage laser photon-source architecture, comprising:

- (a) receiving, at the controller, a specification expressed in a shared parameter space stored in controller memory;
- (b) computing, by selection logic of the controller, a DUV-stage parameter set and a driver-stage parameter set jointly from the specification subject to at least one analytical-cutoff constraint and at least one phase-matching-proxy constraint on a downstream HHG gas target;
- (c) transmitting each parameter set to its respective stage via a controller interface;
- (d) computing a three-part photon-estimate tuple comprising a source-side estimate drawn from a literature anchor stored in controller memory, an analytically computed transmission-product estimate, and a delivered-side estimate formed as the product of the two;
- (e) associating each part of the tuple with a tier label drawn from a predetermined tier set stored in controller memory;
- (f) emitting the tuple through an export interface of the controller, wherein emission of the delivered-side estimate is inhibited in the absence of the source-side estimate, the transmission-product estimate, and their respective tier labels.

### Rung 4 — Backup independent METHOD claim

A method performed by a controller for a laser photon-source driver stage, comprising:

- selecting a driver-stage parameter set from a stored parameter space subject to an analytical-cutoff constraint and a phase-matching-proxy constraint on a downstream HHG gas target;
- computing a three-part tier-labeled photon-estimate tuple;
- emitting the tuple through an export interface of the controller, wherein emission of the delivered-side component is gated on presence of the source-side and transmission-product components and their associated tier labels.

Same role as Rung 2: survives narrowing of the two-stage claim.

---

## 3. Prior-art pressure table

| Prior-art cluster | Likely overlap | Likely attack vector | Best narrowing distinction | Posture |
| --- | --- | --- | --- | --- |
| **CE-HHG / femtosecond enhancement cavity** (JILA, MPQ, 2005→; Mills, Eikema, Ye group) | Enhancement cavity at the HHG driver wavelength providing the pulses that drive the HHG target; cavity-based driver buildup; intra-cavity HHG at NIR | §102/§103: any claim that reads on a cavity upstream of or enclosing the HHG target; obviousness bridge to replace the NIR cavity element with a DUV intracavity stage; inherency arguments on "control plane across stages" | Explicit structural disclaimer in the independent claim preamble and body: (i) the DUV intracavity stage operates at a DUV wavelength; (ii) the DUV stage is not in optical series with the driver path of the HHG target; (iii) the DUV stage is not configured to enhance, build up, or recirculate the driver pulse at the HHG target | **Disclaim** in spec; carry the decoupling phrase into the independent claim; maintain disclaim in every relevant dependent |
| **Pulse-shaping for HHG** (SLM-based phase shaping; AOPDF / Dazzler; two-color ω + 2ω; CEP-stabilized driver; GA- / evolutionary-driven feedback HHG optimization) | Driver-front-end spectral and temporal shaping to control HHG output; closed-loop optimization of HHG spectra; two-color-driven HHG | §103 on every driver-conditioning modality individually; bridging arguments that a shaped driver with a reporting overlay is obvious | Require, in the independent claim, that the shaping be a product of **joint** selection with the DUV-stage parameter set from a shared parameter space, under an explicit cutoff-target value and an explicit η_c ceiling; do not claim a shaping operation alone | **Claim** only as dependents; never as an independent element in its own right |
| **vdW / 2D-material intracavity optical control** (graphene / MoS₂ / hBN / BP saturable absorbers; polariton cavities; DUV modulators) | Intracavity 2D-material modulation at NIR or DUV | §102/§103 on the "intracavity 2D-material modulator" element broadly | Claim only the **role** of the DUV stage in the shared control plane, not the modulator element itself; restrict to DUV operation below the EUV absorption edge; disclaim enhancement-cavity function | **Claim role** as dependent; **disclose** element detail in spec; **disclaim** enhancement-cavity function everywhere |
| **Simulation / controller reporting with provenance or uncertainty labels** (data-provenance frameworks; units libraries; uncertainty-propagating scientific software; lineage trackers) | Tagged output fields; labels on computed quantities | §101 "abstract idea / mental process / presentation of information"; §102 on generic provenance labeling | Tie the tier label to (a) a **predetermined tier set** stored in controller memory; (b) **controller-enforced export-inhibit gating** on absence of required components; (c) the **specific technical domain** of photon-source flux bookkeeping with the three computational construction rules (literature anchor; analytical transmission product; parameterized product); (d) **emit / transmit / inhibit** verbs, never display / show / present | **Claim** as an independent method track and as a system-claim element; frame every instance as a controller operation with a refusal state, never a labeling operation |

---

## 4. Dependent buckets worth keeping on narrowing

**Keep (survive even when the two-stage independent claim narrows):**

- Controller-enforced export-inhibit gating dependents (this is the survival anchor; it rides on both the primary and the backup method tracks).
- η_c phase-matching-proxy ceiling dependent (survival anchor for driver-side claims).
- Cutoff-target constraint dependent (same; parallel survival anchor to η_c).
- Literature-anchor source-side tier dependent (ties the tier-label claim to a specific data-origin rule, which helps against §101).
- Analytically computed transmission-product dependent using R^N·T^M with named optical elements (multilayer mirror count N, foil count M, stated materials).
- Defensible application-endpoint dependents: CDI, ptychography, actinic EUV mask inspection, ARPES. (HVM lithography is never listed.)
- Physical-decoupling dependent ("first stage and second stage are not in optical series" — do not rely on this living only in the spec; dependent-claim form is stronger).
- DUV-below-absorption-edge dependent (narrows the vdW element and disclaims EUV operation in the same breath).
- Predetermined-tier-set dependent enumerating the four tiers.

**Drop on narrowing (keep in spec only):**

- Individual pulse-shaping modality dependents (SLM, AOPDF, CEP, two-color, chirped envelope, MIR-OPCPA band). Under §103 pressure from pulse-shaping-for-HHG art these will be first to fall; do not anchor portfolio value here.
- Wavelength-bridge figure as a dependent (never belonged in claims; Figure 1 only).
- Multihead, fleet, 11-DOF, PSF, resist dependents (already spec-only per prior memo; restate here to prevent drift).

---

## 5. Revised drafting guidance for counsel

### What must appear in the independent claims

- Controller memory storing a shared parameter space and a predetermined tier set.
- Joint selection logic operating across a DUV-stage parameter set and a driver-stage parameter set (Rung 1 / Rung 3) or a driver-stage parameter set alone (Rung 2 / Rung 4).
- At least one analytical-cutoff constraint and at least one phase-matching-proxy constraint on the HHG target.
- Export interface that emits a three-part tier-labeled tuple.
- Emission-inhibit / gating rule on missing components.
- Physical-decoupling phrase ("not in optical series") in Rung 1 / Rung 3.

### What should be pushed to dependents

- Driver-conditioning modalities (SLM, AOPDF, CEP, two-color, chirped, MIR-OPCPA).
- DUV-element specifics (2D-material heterostructure classes at DUV).
- Transmission-product decomposition with R^N · T^M and named materials.
- Defensible use-case endpoints (CDI, ptychography, actinic mask inspection, ARPES).
- Enumeration of the four tiers.
- DUV-below-absorption-edge restriction.
- Refusal / non-compliant-input rejection dependents (strengthens the gating narrative).

### What must stay specification-only

- Wavelength-bridge figure (Figure 1, narrative).
- 3D pipeline rendering, multihead packaging, fleet economics, 11-DOF writer-head.
- PSF synthesis, resist process, aerial-image examples.
- Any illustrative photon-count numbers.
- Single-atom λ^−(5…6.5) anti-scaling as a numerical range.
- Analytical cutoff relation E_cut = 3.17·U_p + I_p as a standalone statement (appears only inside a constraint-computation step in the claims).

### Language to avoid in any claim or dependent

- "EUV source", "programmable EUV source", or any apparatus-level EUV-source naming.
- "Lithography", "wafer", "HVM", "throughput".
- "Delivers X photons", "brightness", any scalar flux.
- "Integrated into a single optical assembly", "single cavity containing both stages".
- "Cavity-enhanced" in any form.
- "Display", "show", "present", "user interface" when referring to tier labels — use "emit", "transmit", "inhibit emission of", "gate on".
- "Equivalent to ASML", "comparable to LPP", or any competitive-positioning phrase.
- "Replaces" or "alternative to" when placed near "LPP", "EUV source", or "lithography".

### Per-paragraph drafting rule (carried from the prior memo)

Every embodiment paragraph in the specification ends with one sentence naming what the embodiment does not demonstrate — e.g., "this embodiment does not establish a delivered EUV-lithography-source flux and does not demonstrate operation of a two-dimensional-material modulation element beyond its native absorption edge." This is the prose analog of the repo's epistemic-tier banners and is the single most effective written-description defense.

### Procedural recommendations

- File the reporting-discipline method claim as its own independent track (Rung 3 / Rung 4), not as a dependent of the two-stage apparatus claim. Independent standing preserves survivability if the apparatus track is narrowed on prosecution.
- Commission a targeted landscape pull before filing on the four clusters in Section 3 — CE-HHG, pulse-shaping-for-HHG, vdW intracavity optical control, simulation-and-provenance controller reporting — and incorporate the results into the disclaim / dependent structure before drafting the independent claims. A landscape hit on one cluster changes the order and language of the disclaimers, not the overall structure.
- For foreign strategy (EPO in particular), draft the tier-labeled reporting track with "technical effect" framing anchored to the controller's export gate and the photon-source operational domain, not to the label itself. The European technical-character analysis is the pressure point.

*End of brief.*
