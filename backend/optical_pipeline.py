"""Architectural model of the HHG generation chain.

This module assembles a sequence of :class:`OpticalComponent` objects
representing the chain: NIR/MIR driver laser -> focusing optic ->
HHG gas cell (single-atom + literature-anchored source flux) ->
metal filter -> Mo/Si multilayer mirror(s) -> application plane.

Tier discipline (see :mod:`backend.epistemic`):

* The cutoff energy and maximum harmonic order are ANALYTICAL.
* The single-atom conversion efficiency is PARAMETERIZED.
* The mirror reflectivity and filter transmission anchors are
  LITERATURE-derived from optics datasheets (CXRO).
* The pipeline as a whole is ARCHITECTURE-level: it is a system diagram
  used for visualisation, not a delivered-flux measurement.

The :meth:`EUVOpticalPipeline.compute_flux_budget` method explicitly
splits *generated* (source-side single-atom) photon flux from
*delivered* (after-beamline, in-vacuum) photon flux, with an
:class:`backend.hhg_analytical.FluxBudget` describing the source
basis and beamline transmission separately.

The driver-laser stage is labelled "NIR/MIR Driver Laser"; the legacy
"VCSEL Source" label was incorrect (a VCSEL is not an HHG driver) and
has been removed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
import numpy as np

from backend.epistemic import EpistemicTier, TierLabel
from backend.hhg_analytical import (
    HC_EV_NM,
    BeamlineTransmission,
    FluxBudget,
    beamline_transmission as analytical_beamline_transmission,
    cutoff_energy,
    get_ionization_potential_ev,
    harmonic_wavelength_nm,
    phase_matching_window,
    split_generated_vs_delivered,
)
from backend.hhg_model import get_hhg_conversion_efficiency


# Mo/Si multilayer reflectivity near 13.5 nm: 65-70% per mirror is the
# typical published value; we use 0.65 as a conservative anchor.
DEFAULT_MOSI_REFLECTIVITY_AT_13P5NM = 0.65

# Metal filter transmissions in the soft-EUV / VUV band (representative,
# not wavelength-resolved). Source: CXRO X-ray attenuation tables.
DEFAULT_FILTER_TRANSMISSIONS = {
    "Al": 0.50,   # Al filter near 17-50 nm
    "Zr": 0.45,   # Zr filter near 8-20 nm
    "Sn": 0.20,
}


# Literature-anchored source-side flux at the gas-jet exit.
# Source: Coherent / KMLabs XUUS-4 white paper.
#   ~1e11 photons/s/harmonic at 35 nm (Ar)
#   ~1.5e7 photons/s/harmonic at 13.5 nm (He)
# These are used as anchors for the FluxBudget; the values are NOT
# computed by this repository.
SOURCE_SIDE_LITERATURE_ANCHORS = {
    "Ar_35nm": 1.0e11,
    "He_13p5nm": 1.5e7,
    "Kr_50nm": 5.0e10,
    "Ne_30nm": 5.0e9,
    "Xe_70nm": 5.0e11,
}


@dataclass
class OpticalComponent:
    """A single component on the optical axis.

    Attributes:
        name: human-readable component label
        z_start, z_end: extent along the optical axis (mm; exaggerated for
            visualisation only)
        radius: visual radius for 3D rendering (mm)
        component_type: "driver", "lens", "gas_cell", "filter", "mirror",
            "application"
        transmission: fractional throughput at the operating wavelength
            (0 to 1). For the gas cell this carries the *source-side
            single-atom* HHG conversion efficiency, NOT a delivered flux.
        color: visual color
        properties: extra metadata; carries a "tier" key documenting the
            epistemic basis of any quantitative attributes.
    """
    name: str
    z_start: float
    z_end: float
    radius: float
    component_type: str
    transmission: float
    color: str
    properties: dict = field(default_factory=dict)


class EUVOpticalPipeline:
    """Architectural model of the HHG generation chain.

    Tier: ARCHITECTURE for the chain as a whole.
    Component-level quantitative attributes are individually tier-tagged
    in their ``properties`` dict.
    """

    def __init__(self):
        self.components: list[OpticalComponent] = []
        self.params: dict = {}
        self.tier_label: TierLabel = TierLabel(
            tier=EpistemicTier.ARCHITECTURE,
            claim="HHG generation-chain system diagram",
            note=(
                "Driver \u2192 focusing \u2192 gas cell \u2192 filter \u2192 mirror(s)"
                " \u2192 application; not a built device."
            ),
        )

    # ------------------------------------------------------------------ build
    def build_default_pipeline(
        self,
        gas_type: str = "Ar",
        pressure_mbar: float = 30.0,
        intensity_w_cm2: float = 1.5e14,
        n_mirrors: int = 2,
        filter_material: str = "Al",
        filter_thickness_nm: float = 200.0,
        driver_wavelength_nm: float = 800.0,
    ) -> "EUVOpticalPipeline":
        self.components = []
        self.params = {
            "gas_type": gas_type,
            "pressure_mbar": pressure_mbar,
            "intensity_w_cm2": intensity_w_cm2,
            "n_mirrors": n_mirrors,
            "filter_material": filter_material,
            "filter_thickness_nm": filter_thickness_nm,
            "driver_wavelength_nm": driver_wavelength_nm,
        }

        # ---- Analytical HHG physics (tier: ANALYTICAL) -----------------
        ip_ev = get_ionization_potential_ev(gas_type)
        cut = cutoff_energy(intensity_w_cm2, driver_wavelength_nm, gas=gas_type)
        max_q = cut.max_harmonic_order
        target_q = min(max_q, 59)
        if target_q % 2 == 0:
            target_q -= 1
        target_q = max(target_q, 3)
        target_wavelength_nm = harmonic_wavelength_nm(target_q, driver_wavelength_nm)
        # Single-atom yield is PARAMETERIZED.
        single_atom_eff = get_hhg_conversion_efficiency(
            gas_type, target_q, driver_wavelength_nm
        )

        # Phase-matching proxy (tier: ANALYTICAL).
        pm = phase_matching_window(
            gas=gas_type,
            intensity_w_cm2=intensity_w_cm2,
            medium_length_mm=30.0,
            pressure_mbar=pressure_mbar,
        )

        # Filter transmission anchor (tier: LITERATURE).
        filter_trans = DEFAULT_FILTER_TRANSMISSIONS.get(filter_material, 0.35)

        # ---- Components ------------------------------------------------
        # 1. Driver laser
        # NB: component_type kept as "source" for backward compat with
        # visualization_3d.py and the legacy test suite. The display
        # label is the authoritative term.
        self.components.append(OpticalComponent(
            name=f"NIR/MIR Driver Laser ({driver_wavelength_nm:.0f} nm)",
            z_start=0, z_end=2, radius=3,
            component_type="source",
            transmission=1.0,
            color="#cc3333",
            properties={
                "wavelength_nm": driver_wavelength_nm,
                "tier": EpistemicTier.ARCHITECTURE.value,
                "label": (
                    "Driver laser stage (Ti:Sa, Yb:YAG, or MIR OPCPA in practice). "
                    "Label is architectural; this repo does not model the laser cavity."
                ),
            },
        ))

        # 2. Focusing optic
        self.components.append(OpticalComponent(
            name="Focusing Optic",
            z_start=10, z_end=12, radius=8,
            component_type="lens",
            transmission=0.98,
            color="#6699cc",
            properties={
                "focal_length_mm": 50,
                "tier": EpistemicTier.ARCHITECTURE.value,
            },
        ))

        # 3. HHG gas cell - the source-side conversion stage.
        gas_cell_z_start = 30
        gas_cell_z_end = 60
        gas_cell_z_mid = (gas_cell_z_start + gas_cell_z_end) / 2
        self.components.append(OpticalComponent(
            name=f"HHG Gas Cell ({gas_type})",
            z_start=gas_cell_z_start, z_end=gas_cell_z_end, radius=5,
            component_type="gas_cell",
            transmission=single_atom_eff,
            color="#66cc99",
            properties={
                "gas_type": gas_type,
                "pressure_mbar": pressure_mbar,
                "flow_rate_sccm": pressure_mbar * 0.5,
                "ionization_potential_ev": ip_ev,
                "cutoff_energy_ev": cut.cutoff_ev,
                "max_harmonic_order": max_q,
                "target_harmonic": target_q,
                "harmonic_wavelength_nm": target_wavelength_nm,
                # Legacy key kept for backward compat with visualization_3d.py.
                "euv_wavelength_nm": target_wavelength_nm,
                # Legacy key kept for backward compat with visualization_3d.py.
                "conversion_efficiency": single_atom_eff,
                "single_atom_efficiency": single_atom_eff,
                "interaction_length_mm": gas_cell_z_end - gas_cell_z_start,
                "phase_matching_in_window": pm.in_window,
                "phase_matching_margin": pm.margin,
                "phase_matching_eta_crit": pm.critical_fraction,
                "phase_matching_ionization_fraction": pm.ionization_fraction,
                "supply_lines": [
                    {"label": "Gas In", "x": 0, "y": 12, "z": gas_cell_z_mid - 5},
                    {"label": "Gas Out", "x": 0, "y": -12, "z": gas_cell_z_mid + 5},
                    {"label": "Pressure\nGauge", "x": 12, "y": 0, "z": gas_cell_z_mid},
                ],
                "tier_cutoff": EpistemicTier.ANALYTICAL.value,
                "tier_efficiency": EpistemicTier.PARAMETERIZED.value,
                "tier_phase_matching": EpistemicTier.ANALYTICAL.value,
                "label": (
                    "Source-side HHG conversion. The 'transmission' field is "
                    "the SINGLE-ATOM conversion efficiency, not delivered "
                    "flux. Macroscopic build-up requires phase matching."
                ),
            },
        ))

        # 4. Metal filter
        self.components.append(OpticalComponent(
            name=f"{filter_material} Filter",
            z_start=70, z_end=70.2, radius=6,
            component_type="filter",
            transmission=filter_trans,
            color="#cccc33",
            properties={
                "material": filter_material,
                "thickness_nm": filter_thickness_nm,
                "tier_transmission": EpistemicTier.LITERATURE.value,
                "label": (
                    "Metal foil filter blocks residual driver light and out-of-band "
                    "harmonics. Transmission anchored to CXRO datasheets."
                ),
            },
        ))

        # 5-6. Collection mirror(s)
        mirror_z_positions = [90, 110]
        for i in range(min(n_mirrors, len(mirror_z_positions))):
            z = mirror_z_positions[i]
            self.components.append(OpticalComponent(
                name=f"Mo/Si Mirror {i+1}",
                z_start=z, z_end=z + 1, radius=10,
                component_type="mirror",
                transmission=DEFAULT_MOSI_REFLECTIVITY_AT_13P5NM,
                color="#aaaadd",
                properties={
                    "reflectivity": DEFAULT_MOSI_REFLECTIVITY_AT_13P5NM,
                    "material": "Mo/Si multilayer",
                    "tier_reflectivity": EpistemicTier.LITERATURE.value,
                    "label": (
                        "Mo/Si multilayer mirror near 13.5 nm. Reflectivity "
                        "is per-mirror; total beamline throughput is R^N."
                    ),
                },
            ))

        # 7. Application plane. Display label is the authoritative term
        # ("Application Plane (CDI / metrology / actinic inspection)").
        # component_type is kept as "wafer" only for backward compatibility
        # with the legacy 3D renderer; the repo's defensible use cases are
        # CDI, ptychography, actinic mask inspection, and ARPES, NOT
        # lithography exposure (see ASML LPP sources).
        self.components.append(OpticalComponent(
            name="Application Plane (CDI / metrology / actinic inspection)",
            z_start=130, z_end=130, radius=15,
            component_type="wafer",
            transmission=1.0,
            color="#33aa55",
            properties={
                "tier": EpistemicTier.ARCHITECTURE.value,
                "label": (
                    "Defensible HHG use cases: coherent diffractive imaging, "
                    "ptychography, actinic EUV mask inspection, ARPES. "
                    "NOT EUV lithography \u2014 see ASML LPP sources."
                ),
            },
        ))

        return self

    # ------------------------------------------------------------------ budgets
    def compute_power_budget(self, initial_power_w: float = 1.0) -> list[dict]:
        """Compute power at each stage, scaled by component transmission.

        Tier: PARAMETERIZED. The 'power_out' values trace the product of
        all upstream transmissions, not a measured power. The gas cell
        contribution is the SINGLE-ATOM conversion efficiency; this is a
        worst-case proxy, not a macroscopic flux.
        """
        budget: list[dict] = []
        power = initial_power_w
        for comp in self.components:
            power_in = power
            power_out = power * comp.transmission
            budget.append({
                "name": comp.name,
                "z_mid": (comp.z_start + comp.z_end) / 2,
                "power_in": power_in,
                "power_out": power_out,
                "transmission": comp.transmission,
                "tier": EpistemicTier.PARAMETERIZED.value,
            })
            power = power_out
        return budget

    def compute_flux_budget(
        self,
        source_photons_per_second: float | None = None,
    ) -> FluxBudget:
        """Split source-side flux from beamline-attenuated delivered flux.

        Returns a :class:`backend.hhg_analytical.FluxBudget` that
        explicitly distinguishes:

          * source_photons_per_second: at the gas-jet exit (LITERATURE
            anchor unless overridden)
          * beamline_transmission: ANALYTICAL product of mirror
            reflectivities and filter transmissions
          * delivered_photons_per_second: source * beamline (vacuum;
            ignores sample absorption and detector QE)

        If the caller does not supply a source flux, the literature
        anchor matching the operating gas is used as a conservative
        order-of-magnitude estimate.
        """
        if source_photons_per_second is None:
            gas = self.params.get("gas_type", "Ar")
            # Choose the closest literature anchor.
            anchor_key = {
                "Ar": "Ar_35nm", "Kr": "Kr_50nm", "Ne": "Ne_30nm",
                "Xe": "Xe_70nm", "He": "He_13p5nm",
            }.get(gas, "Ar_35nm")
            source_photons_per_second = SOURCE_SIDE_LITERATURE_ANCHORS[anchor_key]

        n_mirrors = sum(1 for c in self.components if c.component_type == "mirror")
        n_filters = sum(1 for c in self.components if c.component_type == "filter")
        # Use the actual filter transmission from the pipeline if present.
        filt = next(
            (c for c in self.components if c.component_type == "filter"), None
        )
        filt_t = filt.transmission if filt else 0.5

        beamline = analytical_beamline_transmission(
            n_mirrors=n_mirrors,
            mirror_reflectivity=DEFAULT_MOSI_REFLECTIVITY_AT_13P5NM,
            n_filters=n_filters,
            filter_transmission=filt_t,
        )
        return split_generated_vs_delivered(source_photons_per_second, beamline)

    # ------------------------------------------------------------------ render
    def get_beam_path(self, n_points: int = 300):
        """Generate the optical-axis envelope used by the 3D renderer.

        Tier: ARCHITECTURE. The envelope is a visual proxy; it is not
        ABCD-matrix Gaussian-beam propagation.
        """
        z_vals = np.linspace(-2, 135, n_points)
        x_center = np.zeros(n_points)
        y_center = np.zeros(n_points)

        r_envelope = np.ones(n_points) * 2.0

        gas_cell = next(
            (c for c in self.components if c.component_type == "gas_cell"),
            None,
        )
        focus_z = gas_cell.z_start + 5 if gas_cell else 35

        for i, z in enumerate(z_vals):
            if z < 0:
                r_envelope[i] = 2.5
            elif z < focus_z:
                t = z / focus_z
                r_envelope[i] = 2.5 * (1 - t) + 0.5 * t
            elif gas_cell and z <= gas_cell.z_end:
                t = (z - focus_z) / (gas_cell.z_end - focus_z)
                r_envelope[i] = 0.5 + 0.3 * t
            else:
                z_after = z - (gas_cell.z_end if gas_cell else 60)
                r_envelope[i] = 0.8 + z_after * 0.04

        color_transition_z = gas_cell.z_end if gas_cell else 60
        return z_vals, x_center, y_center, r_envelope, color_transition_z


__all__ = [
    "OpticalComponent",
    "EUVOpticalPipeline",
    "DEFAULT_MOSI_REFLECTIVITY_AT_13P5NM",
    "DEFAULT_FILTER_TRANSMISSIONS",
    "SOURCE_SIDE_LITERATURE_ANCHORS",
]
