"""Physical-sanity tests for the analytical HHG calculators.

These tests are intentionally conservative. They check that each
calculator produces values in the expected sign/scale, that monotonic
trends predicted by the closed-form theory hold, and that the
generated-vs-delivered split actually decreases (a beamline never
*adds* photons).
"""

from __future__ import annotations

import math
import pytest

from backend.epistemic import EpistemicTier
from backend.hhg_analytical import (
    HC_EV_NM,
    REFERENCE_DRIVER_WAVELENGTH_NM,
    beamline_transmission,
    cutoff_energy,
    efficiency_scaling,
    get_ionization_potential_ev,
    harmonic_photon_energy_ev,
    harmonic_wavelength_nm,
    phase_matching_window,
    ponderomotive_energy_ev,
    split_generated_vs_delivered,
)


# ---------------------------------------------------------------------------
# Ponderomotive / cutoff
# ---------------------------------------------------------------------------

def test_ponderomotive_at_reference_point():
    # Up = 9.33e-14 * 1e14 * (0.8)^2 = 5.97 eV
    up = ponderomotive_energy_ev(1.0e14, 800.0)
    assert math.isclose(up, 9.33 * 0.64, rel_tol=1e-3)


def test_ponderomotive_scales_with_lambda_squared():
    up_800 = ponderomotive_energy_ev(1.0e14, 800.0)
    up_1600 = ponderomotive_energy_ev(1.0e14, 1600.0)
    assert math.isclose(up_1600 / up_800, 4.0, rel_tol=1e-6)


def test_ponderomotive_scales_with_intensity():
    up_low = ponderomotive_energy_ev(1.0e14, 800.0)
    up_high = ponderomotive_energy_ev(2.0e14, 800.0)
    assert math.isclose(up_high / up_low, 2.0, rel_tol=1e-6)


def test_ponderomotive_rejects_bad_inputs():
    with pytest.raises(ValueError):
        ponderomotive_energy_ev(0.0, 800.0)
    with pytest.raises(ValueError):
        ponderomotive_energy_ev(1e14, 0.0)


def test_cutoff_energy_matches_three_step_model():
    # E_cut = 3.17 U_p + I_p; for Ar at 1e14 W/cm^2, 800 nm:
    #   U_p ~ 5.97 eV; 3.17 * U_p ~ 18.93 eV; I_p(Ar) = 15.76 eV
    #   E_cut ~ 34.7 eV
    cut = cutoff_energy(1.0e14, 800.0, gas="Ar")
    expected = 3.17 * (9.33e-14 * 1.0e14 * 0.64) + 15.760
    assert math.isclose(cut.cutoff_ev, expected, rel_tol=1e-3)
    assert cut.tier.tier is EpistemicTier.ANALYTICAL


def test_cutoff_increases_with_intensity_and_wavelength():
    base = cutoff_energy(1.0e14, 800.0, gas="Ar").cutoff_ev
    higher_I = cutoff_energy(2.0e14, 800.0, gas="Ar").cutoff_ev
    longer_lambda = cutoff_energy(1.0e14, 1600.0, gas="Ar").cutoff_ev
    assert higher_I > base
    assert longer_lambda > base


def test_cutoff_max_harmonic_is_odd():
    cut = cutoff_energy(1.5e14, 800.0, gas="Ar")
    assert cut.max_harmonic_order >= 1
    assert cut.max_harmonic_order % 2 == 1


def test_get_ionization_potential():
    assert math.isclose(get_ionization_potential_ev("Ar"), 15.760, rel_tol=1e-3)
    assert math.isclose(get_ionization_potential_ev("Ne"), 21.565, rel_tol=1e-3)
    with pytest.raises(KeyError):
        get_ionization_potential_ev("Pb")


# ---------------------------------------------------------------------------
# Efficiency scaling
# ---------------------------------------------------------------------------

def test_efficiency_at_reference_is_unity():
    r = efficiency_scaling(REFERENCE_DRIVER_WAVELENGTH_NM)
    assert math.isclose(r.relative_yield_central, 1.0, rel_tol=1e-9)
    assert math.isclose(r.relative_yield_low, 1.0, rel_tol=1e-9)
    assert math.isclose(r.relative_yield_high, 1.0, rel_tol=1e-9)


def test_efficiency_falls_for_longer_drivers():
    """eta(lambda) ~ lambda^-(5..6.5): MIR is suppressed vs Ti:Sa."""
    r = efficiency_scaling(1800.0)
    # 1800/800 = 2.25; 2.25^-6 ~ 0.0077
    assert r.relative_yield_central < 0.05
    assert r.relative_yield_central > 1e-4
    assert r.relative_yield_low <= r.relative_yield_central <= r.relative_yield_high


def test_efficiency_band_brackets_central():
    for lam in [500.0, 800.0, 1030.0, 1800.0, 3000.0]:
        r = efficiency_scaling(lam)
        assert r.relative_yield_low <= r.relative_yield_central + 1e-12
        assert r.relative_yield_central <= r.relative_yield_high + 1e-12


def test_efficiency_tier_is_analytical():
    assert efficiency_scaling(1030.0).tier.tier is EpistemicTier.ANALYTICAL


# ---------------------------------------------------------------------------
# Phase-matching window proxy
# ---------------------------------------------------------------------------

def test_phase_matching_low_intensity_in_window():
    # At 5e13 W/cm^2 in Ar the proxy should report we are in the window.
    pm = phase_matching_window("Ar", 5.0e13, medium_length_mm=10.0,
                               pressure_mbar=20.0)
    assert pm.in_window
    assert pm.margin > 0


def test_phase_matching_overionized_at_high_intensity():
    # 5e15 W/cm^2 is well over the saturation regime for Ar.
    pm = phase_matching_window("Ar", 5.0e15, medium_length_mm=10.0,
                               pressure_mbar=20.0)
    assert not pm.in_window
    assert pm.margin < 0


def test_phase_matching_critical_fraction_can_be_overridden():
    pm = phase_matching_window("Ar", 1.0e14, 5.0, 20.0,
                               critical_fraction=0.99)
    assert pm.critical_fraction == 0.99
    assert pm.in_window


def test_phase_matching_rejects_bad_inputs():
    with pytest.raises(ValueError):
        phase_matching_window("Ar", 1e14, medium_length_mm=0, pressure_mbar=20)
    with pytest.raises(ValueError):
        phase_matching_window("Ar", 1e14, medium_length_mm=10, pressure_mbar=0)


# ---------------------------------------------------------------------------
# Beamline transmission
# ---------------------------------------------------------------------------

def test_beamline_transmission_is_product_of_factors():
    bl = beamline_transmission(n_mirrors=2, mirror_reflectivity=0.5,
                               n_filters=1, filter_transmission=0.4)
    assert math.isclose(bl.transmission, 0.5 ** 2 * 0.4, rel_tol=1e-12)


def test_beamline_transmission_monotone_in_count():
    bl_2 = beamline_transmission(n_mirrors=2, mirror_reflectivity=0.7).transmission
    bl_3 = beamline_transmission(n_mirrors=3, mirror_reflectivity=0.7).transmission
    bl_4 = beamline_transmission(n_mirrors=4, mirror_reflectivity=0.7).transmission
    assert bl_2 > bl_3 > bl_4


def test_beamline_transmission_zero_when_any_factor_zero():
    bl = beamline_transmission(n_mirrors=2, mirror_reflectivity=0.0)
    assert bl.transmission == 0.0


def test_beamline_transmission_validates_inputs():
    with pytest.raises(ValueError):
        beamline_transmission(n_mirrors=-1)
    with pytest.raises(ValueError):
        beamline_transmission(mirror_reflectivity=1.1)
    with pytest.raises(ValueError):
        beamline_transmission(filter_transmission=-0.1)


# ---------------------------------------------------------------------------
# Generated vs delivered flux split
# ---------------------------------------------------------------------------

def test_split_delivered_never_exceeds_source():
    bl = beamline_transmission(n_mirrors=2, mirror_reflectivity=0.7,
                               n_filters=1, filter_transmission=0.4)
    fb = split_generated_vs_delivered(1.0e10, bl)
    assert fb.delivered_photons_per_second < fb.source_photons_per_second
    assert fb.delivered_photons_per_second == pytest.approx(1.0e10 * bl.transmission)


def test_split_carries_three_distinct_tiers():
    bl = beamline_transmission()
    fb = split_generated_vs_delivered(1.0e10, bl)
    assert fb.source_basis.tier is EpistemicTier.LITERATURE
    assert fb.beamline_basis.tier is EpistemicTier.ANALYTICAL
    assert fb.delivered_basis.tier is EpistemicTier.PARAMETERIZED


# ---------------------------------------------------------------------------
# Harmonic geometry
# ---------------------------------------------------------------------------

def test_harmonic_wavelength_inverse_q():
    assert math.isclose(harmonic_wavelength_nm(2, 800.0), 400.0, rel_tol=1e-12)
    assert math.isclose(harmonic_wavelength_nm(59, 800.0), 800.0 / 59, rel_tol=1e-12)


def test_harmonic_photon_energy_matches_hc_over_lambda():
    e = harmonic_photon_energy_ev(59, 800.0)
    assert math.isclose(e, HC_EV_NM / (800.0 / 59), rel_tol=1e-12)


def test_harmonic_wavelength_rejects_bad_q():
    with pytest.raises(ValueError):
        harmonic_wavelength_nm(0, 800.0)
