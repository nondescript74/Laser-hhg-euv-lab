from dataclasses import dataclass, field
import numpy as np
from backend.hhg_model import (
    calculate_cutoff_energy,
    get_ionization_potential,
    get_max_harmonic_order,
    get_harmonic_wavelength,
    get_hhg_conversion_efficiency,
)


@dataclass
class OpticalComponent:
    name: str
    z_start: float          # mm along optical axis
    z_end: float            # mm
    radius: float           # mm (exaggerated for visual clarity)
    component_type: str     # source, lens, gas_cell, filter, mirror, wafer
    transmission: float     # fraction 0-1
    color: str
    properties: dict = field(default_factory=dict)


class EUVOpticalPipeline:
    def __init__(self):
        self.components: list[OpticalComponent] = []
        self.params: dict = {}

    def build_default_pipeline(
        self,
        gas_type="Ar",
        pressure_mbar=30.0,
        intensity_w_cm2=1e14,
        n_mirrors=2,
        filter_material="Al",
        filter_thickness_nm=200.0,
    ):
        self.components = []
        self.params = {
            "gas_type": gas_type,
            "pressure_mbar": pressure_mbar,
            "intensity_w_cm2": intensity_w_cm2,
            "n_mirrors": n_mirrors,
            "filter_material": filter_material,
            "filter_thickness_nm": filter_thickness_nm,
        }

        # Compute HHG physics
        ip_ev = get_ionization_potential(gas_type)
        cutoff_ev = calculate_cutoff_energy(intensity_w_cm2, ip_ev)
        max_q = get_max_harmonic_order(cutoff_ev)
        target_q = min(max_q, 59)  # Target H59 for 13.5nm
        if target_q % 2 == 0:
            target_q -= 1
        euv_wavelength_nm = get_harmonic_wavelength(target_q)
        conversion_eff = get_hhg_conversion_efficiency(gas_type, target_q)

        # Filter transmission estimate
        filter_trans = {"Al": 0.35, "Zr": 0.45}.get(filter_material, 0.35)

        # 1. VCSEL Source
        self.components.append(OpticalComponent(
            name="VCSEL Source",
            z_start=0, z_end=2, radius=3,
            component_type="source",
            transmission=1.0,
            color="#cc3333",
            properties={"wavelength_nm": 800, "power_w": 1.0},
        ))

        # 2. Focusing Optic
        self.components.append(OpticalComponent(
            name="Focusing Optic",
            z_start=10, z_end=12, radius=8,
            component_type="lens",
            transmission=0.98,
            color="#6699cc",
            properties={"focal_length_mm": 50},
        ))

        # 3. HHG Gas Cell
        gas_cell_z_start = 30
        gas_cell_z_end = 60
        gas_cell_z_mid = (gas_cell_z_start + gas_cell_z_end) / 2
        self.components.append(OpticalComponent(
            name=f"HHG Gas Cell ({gas_type})",
            z_start=gas_cell_z_start, z_end=gas_cell_z_end, radius=5,
            component_type="gas_cell",
            transmission=conversion_eff,
            color="#66cc99",
            properties={
                "gas_type": gas_type,
                "pressure_mbar": pressure_mbar,
                "flow_rate_sccm": pressure_mbar * 0.5,
                "ionization_potential_ev": ip_ev,
                "cutoff_energy_ev": cutoff_ev,
                "max_harmonic_order": max_q,
                "target_harmonic": target_q,
                "euv_wavelength_nm": euv_wavelength_nm,
                "conversion_efficiency": conversion_eff,
                "interaction_length_mm": gas_cell_z_end - gas_cell_z_start,
                "supply_lines": [
                    {"label": "Gas In", "x": 0, "y": 12, "z": gas_cell_z_mid - 5},
                    {"label": "Gas Out", "x": 0, "y": -12, "z": gas_cell_z_mid + 5},
                    {"label": "Pressure\nGauge", "x": 12, "y": 0, "z": gas_cell_z_mid},
                ],
            },
        ))

        # 4. Metal Filter
        self.components.append(OpticalComponent(
            name=f"{filter_material} Filter",
            z_start=70, z_end=70.2, radius=6,
            component_type="filter",
            transmission=filter_trans,
            color="#cccc33",
            properties={
                "material": filter_material,
                "thickness_nm": filter_thickness_nm,
            },
        ))

        # 5-6. Collection Mirrors
        mirror_z_positions = [90, 110]
        for i in range(n_mirrors):
            if i >= len(mirror_z_positions):
                break
            z = mirror_z_positions[i]
            self.components.append(OpticalComponent(
                name=f"Mo/Si Mirror {i+1}",
                z_start=z, z_end=z + 1, radius=10,
                component_type="mirror",
                transmission=0.70,
                color="#aaaadd",
                properties={"reflectivity": 0.70, "material": "Mo/Si"},
            ))

        # 7. Wafer
        self.components.append(OpticalComponent(
            name="Wafer",
            z_start=130, z_end=130, radius=15,
            component_type="wafer",
            transmission=1.0,
            color="#33aa55",
            properties={},
        ))

        return self

    def compute_power_budget(self, initial_power_w=1.0):
        """Compute power at each stage through the pipeline."""
        budget = []
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
            })
            power = power_out
        return budget

    def get_beam_path(self, n_points=300):
        """Generate beam centerline and envelope for 3D rendering."""
        z_vals = np.linspace(-2, 135, n_points)
        x_center = np.zeros(n_points)
        y_center = np.zeros(n_points)

        # Beam radius envelope (exaggerated for visibility)
        r_envelope = np.ones(n_points) * 2.0  # default radius

        # Find key z positions
        gas_cell = next((c for c in self.components if c.component_type == "gas_cell"), None)
        focus_z = gas_cell.z_start + 5 if gas_cell else 35  # focus near start of gas cell

        for i, z in enumerate(z_vals):
            if z < 0:
                r_envelope[i] = 2.5
            elif z < focus_z:
                # Converging: linear taper from 2.5 to 0.5
                t = z / focus_z
                r_envelope[i] = 2.5 * (1 - t) + 0.5 * t
            elif gas_cell and z <= gas_cell.z_end:
                # Inside gas cell: tight waist with slight expansion
                t = (z - focus_z) / (gas_cell.z_end - focus_z)
                r_envelope[i] = 0.5 + 0.3 * t
            else:
                # After gas cell: diverging EUV
                z_after = z - (gas_cell.z_end if gas_cell else 60)
                r_envelope[i] = 0.8 + z_after * 0.04

        # Determine beam color transition (IR → EUV at gas cell exit)
        color_transition_z = gas_cell.z_end if gas_cell else 60

        return z_vals, x_center, y_center, r_envelope, color_transition_z
