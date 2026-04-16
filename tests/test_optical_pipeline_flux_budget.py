"""Tests for the generated-vs-delivered flux split in EUVOpticalPipeline.

These tests are the core enforcement that the repo never collapses
source-side single-atom yield, beamline transmission, and delivered
application-plane flux into one number.
"""

from __future__ import annotations

from backend.epistemic import EpistemicTier
from backend.optical_pipeline import (
    EUVOpticalPipeline,
    SOURCE_SIDE_LITERATURE_ANCHORS,
)


def test_default_pipeline_returns_three_distinct_planes():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    fb = pipeline.compute_flux_budget()

    # Strict ordering: source > delivered.
    assert fb.delivered_photons_per_second < fb.source_photons_per_second
    # Beamline transmission is between 0 and 1.
    assert 0.0 < fb.beamline_transmission < 1.0
    # Tiers are correctly tagged on the three legs of the budget.
    assert fb.source_basis.tier is EpistemicTier.LITERATURE
    assert fb.beamline_basis.tier is EpistemicTier.ANALYTICAL
    assert fb.delivered_basis.tier is EpistemicTier.PARAMETERIZED


def test_more_mirrors_lowers_delivered_flux():
    p1 = EUVOpticalPipeline().build_default_pipeline(n_mirrors=1)
    p2 = EUVOpticalPipeline().build_default_pipeline(n_mirrors=2)
    fb1 = p1.compute_flux_budget(source_photons_per_second=1.0e10)
    fb2 = p2.compute_flux_budget(source_photons_per_second=1.0e10)
    assert fb2.delivered_photons_per_second < fb1.delivered_photons_per_second


def test_caller_can_override_source_flux():
    pipeline = EUVOpticalPipeline().build_default_pipeline()
    fb = pipeline.compute_flux_budget(source_photons_per_second=42.0)
    assert fb.source_photons_per_second == 42.0


def test_default_source_anchor_matches_lit_table():
    """Default source pick uses a published industrial anchor."""
    pipeline = EUVOpticalPipeline().build_default_pipeline(gas_type="Ar")
    fb = pipeline.compute_flux_budget()
    assert fb.source_photons_per_second == SOURCE_SIDE_LITERATURE_ANCHORS["Ar_35nm"]


def test_pipeline_tier_label_is_architecture():
    pipeline = EUVOpticalPipeline().build_default_pipeline()
    assert pipeline.tier_label.tier is EpistemicTier.ARCHITECTURE


def test_gas_cell_properties_include_phase_matching_proxy():
    pipeline = EUVOpticalPipeline().build_default_pipeline()
    gas_cell = next(c for c in pipeline.components if c.component_type == "gas_cell")
    p = gas_cell.properties
    assert "phase_matching_in_window" in p
    assert "phase_matching_eta_crit" in p
    assert "phase_matching_ionization_fraction" in p
    # Tier annotations are present.
    assert p.get("tier_efficiency") == "parameterized"
    assert p.get("tier_phase_matching") == "analytical"
    assert p.get("tier_cutoff") == "analytical"


def test_driver_label_no_longer_says_vcsel():
    pipeline = EUVOpticalPipeline().build_default_pipeline()
    driver = next(c for c in pipeline.components if c.component_type == "source")
    assert "VCSEL" not in driver.name
    assert "Driver" in driver.name


def test_application_plane_label_is_use_case_neutral():
    pipeline = EUVOpticalPipeline().build_default_pipeline()
    apl = next(c for c in pipeline.components if c.component_type == "wafer")
    assert "Application Plane" in apl.name


def test_mir_driver_extends_cutoff():
    """U_p ~ lambda^2 - longer driver -> larger cutoff energy."""
    p_800 = EUVOpticalPipeline().build_default_pipeline(driver_wavelength_nm=800)
    p_1800 = EUVOpticalPipeline().build_default_pipeline(driver_wavelength_nm=1800)
    cell_800 = next(c for c in p_800.components if c.component_type == "gas_cell")
    cell_1800 = next(c for c in p_1800.components if c.component_type == "gas_cell")
    assert (cell_1800.properties["cutoff_energy_ev"]
            > cell_800.properties["cutoff_energy_ev"])
