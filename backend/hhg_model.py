"""Compatibility shim over :mod:`backend.hhg_analytical`.

The legacy callers in this repository (notably
:mod:`backend.optical_pipeline` and the test suite) import these names
directly. The implementations here defer to the more rigorously
labelled functions in :mod:`backend.hhg_analytical`.

All values produced by this module carry the
:class:`backend.epistemic.EpistemicTier.ANALYTICAL` tier when computed
from the closed-form three-step law, and
:class:`backend.epistemic.EpistemicTier.LITERATURE` when they are
quoted from cited measurements (the conversion-efficiency anchors).

This module does NOT compute device flux. ``get_hhg_conversion_efficiency``
returns a *single-atom* response, not a delivered photon rate.
"""

from __future__ import annotations

from typing import Mapping

from backend.hhg_analytical import (
    EFFICIENCY_SCALING_EXPONENT_CENTRAL,
    HC_EV_NM,
    REFERENCE_DRIVER_WAVELENGTH_NM,
    cutoff_energy as _cutoff_energy,
    efficiency_scaling as _efficiency_scaling,
    get_ionization_potential_ev,
    harmonic_wavelength_nm as _harmonic_wavelength_nm,
)

# Backwards-compatible alias kept for legacy callers.
IONIZATION_POTENTIALS: Mapping[str, float] = {
    "He": 24.587,
    "Ne": 21.565,
    "Ar": 15.760,
    "Kr": 13.999,
    "Xe": 12.130,
}


# ---------------------------------------------------------------------------
# Single-atom anchor efficiencies at the reference 800 nm Ti:Sa driver.
# Source: tabulated single-atom plateau yields from Shiner et al. PRL 2009
# and the Coherent/KMLabs XUUS-4 white paper. These are LITERATURE anchors,
# not predictions. Use :func:`get_hhg_conversion_efficiency` to obtain a
# wavelength-scaled single-atom yield estimate.
# ---------------------------------------------------------------------------

_REF_SINGLE_ATOM_YIELD_AT_800NM: Mapping[str, float] = {
    "Ar": 1.0e-6,
    "Kr": 8.0e-7,
    "Xe": 2.0e-6,
    "Ne": 5.0e-7,
    "He": 2.0e-7,
}


def calculate_cutoff_energy(
    intensity_w_cm2: float,
    ionization_potential_ev: float,
    driver_wavelength_nm: float = REFERENCE_DRIVER_WAVELENGTH_NM,
) -> float:
    """Return E_cut = 3.17 U_p + I_p in eV.

    Tier: ANALYTICAL. Equivalent to
    ``backend.hhg_analytical.cutoff_energy(...).cutoff_ev`` but accepts
    a raw I_p value to preserve the legacy call signature.

    The legacy signature defaulted to a hard-coded 800 nm driver; the
    optional ``driver_wavelength_nm`` parameter now allows MIR/Yb drivers
    to be modelled correctly via the U_p \u221d lambda^2 scaling.
    """
    wavelength_um = driver_wavelength_nm / 1000.0
    up = 9.33e-14 * intensity_w_cm2 * (wavelength_um ** 2)
    return ionization_potential_ev + 3.17 * up


def get_harmonic_wavelength(q: int, fundamental_nm: float = REFERENCE_DRIVER_WAVELENGTH_NM) -> float:
    """lambda_q = lambda_drive / q. Tier: ANALYTICAL."""
    return _harmonic_wavelength_nm(q, fundamental_nm)


def get_ionization_potential(gas_type: str) -> float:
    """Lookup I_p (eV) from the NIST-anchored table. Tier: LITERATURE."""
    return get_ionization_potential_ev(gas_type)


def get_max_harmonic_order(cutoff_ev: float, fundamental_nm: float = REFERENCE_DRIVER_WAVELENGTH_NM) -> int:
    """Largest odd q satisfying q * h*nu_drive <= E_cut. Tier: ANALYTICAL."""
    fundamental_ev = HC_EV_NM / fundamental_nm
    q_max = int(cutoff_ev / fundamental_ev)
    if q_max % 2 == 0:
        q_max -= 1
    return max(q_max, 1)


def get_hhg_conversion_efficiency(
    gas_type: str,
    harmonic_order: int,
    driver_wavelength_nm: float = REFERENCE_DRIVER_WAVELENGTH_NM,
) -> float:
    """Single-atom HHG conversion efficiency estimate.

    Tier: PARAMETERIZED. Combines a literature-anchored 800 nm baseline
    yield with the lambda^-(5..6.5) anti-scaling law (Shiner et al. PRL
    2009). Provides an order-of-magnitude estimate of plateau yield;
    suppression in the cutoff region is modelled as a smooth roll-off
    rather than the legacy ``if q > 50: x0.5`` step.

    This is a SINGLE-ATOM yield. It does NOT include phase-matching
    macroscopic enhancement, plasma absorption, beamline transmission,
    or sample absorption. Callers must combine this with
    :func:`backend.hhg_analytical.beamline_transmission` and an explicit
    source-flux anchor to obtain a delivered-photon estimate.
    """
    base = _REF_SINGLE_ATOM_YIELD_AT_800NM.get(gas_type, 1.0e-6)

    # Wavelength scaling versus 800 nm baseline.
    wavelength_factor = _efficiency_scaling(
        driver_wavelength_nm,
        reference_wavelength_nm=REFERENCE_DRIVER_WAVELENGTH_NM,
        exponent_central=EFFICIENCY_SCALING_EXPONENT_CENTRAL,
    ).relative_yield_central

    # Smooth cutoff roll-off: Gaussian decay anchored at the analytical
    # cutoff harmonic for the given gas at typical 1.5e14 W/cm^2 intensity.
    typical_intensity = 1.5e14
    cut = _cutoff_energy(typical_intensity, driver_wavelength_nm, gas=gas_type)
    q_cut = max(cut.max_harmonic_order, 3)
    if harmonic_order >= q_cut:
        # Beyond cutoff: exponential suppression.
        rolloff = 0.1 ** ((harmonic_order - q_cut) / max(q_cut * 0.1, 1.0))
    else:
        # Inside plateau: gentle decline toward cutoff.
        x = (q_cut - harmonic_order) / max(q_cut, 1.0)
        rolloff = 0.4 + 0.6 * min(1.0, x)
    return float(max(base * wavelength_factor * rolloff, 1e-15))


__all__ = [
    "IONIZATION_POTENTIALS",
    "calculate_cutoff_energy",
    "get_harmonic_wavelength",
    "get_ionization_potential",
    "get_max_harmonic_order",
    "get_hhg_conversion_efficiency",
]
