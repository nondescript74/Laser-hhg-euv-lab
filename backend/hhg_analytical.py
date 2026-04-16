"""Analytical / formula-based HHG calculators.

This module is the lowest-rung, highest-credibility layer of the HHG
modeling stack. Every function here corresponds to a closed-form
expression from the standard three-step model literature, exposed with
explicit input units, an explicit return type, and an explicit
:class:`backend.epistemic.EpistemicTier` annotation.

No function in this module computes "device flux" or "delivered
photons-on-application". Source-side single-atom yield is strictly
separated from beamline transmission and delivered application-plane
flux; downstream callers are expected to multiply the three terms only
when they have explicitly opted into a delivered-flux estimate (and
labelled the result accordingly).

References (cited in module docstring per function for traceability):
    [Lewenstein 1994]   Lewenstein et al., Phys. Rev. A 49, 2117.
    [Corkum 1993]       Corkum, Phys. Rev. Lett. 71, 1994.
    [Shiner 2009]       Shiner et al., PRL 103, 073902 - lambda^-(5..6).
    [Wikmark 2022]      Wikmark et al., Nature Sci. Reports - PM window
                        with critical ionization fraction.
    [Coherent/KMLabs]   XUUS-4 white paper - tabletop EUV flux benchmarks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from backend.epistemic import EpistemicTier, TierLabel


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Photon-energy / wavelength conversion: E[eV] = HC_EV_NM / lambda[nm]
HC_EV_NM = 1239.84198  # eV * nm

# U_p[eV] = UP_PREFACTOR_EV * I[1e14 W/cm^2] * lambda[um]^2
# Equivalently U_p[eV] = 9.33e-14 * I[W/cm^2] * lambda[um]^2.
# We separate the two forms for input-unit clarity.
UP_PREFACTOR_PER_W_CM2_UM2 = 9.33e-14   # I in W/cm^2, lambda in um
UP_PREFACTOR_PER_1E14_UM2 = 9.33         # I in 1e14 W/cm^2, lambda in um

# Cutoff prefactor in the standard three-step law E_cut = 3.17 U_p + I_p
CUTOFF_UP_PREFACTOR = 3.17

# Ionization potentials I_p (eV). Source: NIST atomic database.
IONIZATION_POTENTIALS_EV: Mapping[str, float] = {
    "He": 24.587,
    "Ne": 21.565,
    "Ar": 15.760,
    "Kr": 13.999,
    "Xe": 12.130,
    "N2": 15.581,
    "H2": 15.426,
}

# Critical ionization fraction (eta_crit) below which classical phase
# matching is achievable. Practical range 3-9% depending on gas species
# and focusing geometry. We expose conservative defaults; callers can
# pass a per-gas value.
CRITICAL_IONIZATION_FRACTION_DEFAULT: Mapping[str, float] = {
    "He": 0.005,   # ~0.5%
    "Ne": 0.010,   # ~1.0%
    "Ar": 0.040,   # ~4.0%
    "Kr": 0.060,   # ~6.0%
    "Xe": 0.090,   # ~9.0%
}

# Single-atom yield scaling exponent: eta(lambda) propto lambda^-(5..6.5).
# Shiner et al. PRL 2009 measured -6.3 +/- 1.1 in Xe and -6.5 +/- 1.1 in Kr.
EFFICIENCY_SCALING_EXPONENT_CENTRAL = 6.0
EFFICIENCY_SCALING_EXPONENT_RANGE = (5.0, 6.5)

# Reference wavelength for relative single-atom yield (Ti:Sa baseline).
REFERENCE_DRIVER_WAVELENGTH_NM = 800.0


# ---------------------------------------------------------------------------
# Data classes for explicit-tier returns
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CutoffResult:
    """Result of an analytical cutoff-energy calculation.

    Tier: ANALYTICAL. The formula E_cut = 3.17 U_p + I_p is exact within
    the strong-field three-step model; absolute photon flux is NOT
    implied.
    """

    cutoff_ev: float
    ponderomotive_ev: float
    ionization_potential_ev: float
    max_harmonic_order: int
    cutoff_wavelength_nm: float
    driver_wavelength_nm: float
    intensity_w_cm2: float
    gas: str
    tier: TierLabel = field(
        default_factory=lambda: TierLabel(
            tier=EpistemicTier.ANALYTICAL,
            claim="Cutoff energy from three-step model",
            note="E_cut = 3.17 U_p + I_p; closed-form, single-atom",
        )
    )


@dataclass(frozen=True)
class EfficiencyScalingResult:
    """Relative single-atom HHG yield versus driver wavelength.

    Tier: ANALYTICAL (scaling law) with literature-anchored exponent.
    Returns *relative* yield versus a reference wavelength only.
    """

    driver_wavelength_nm: float
    reference_wavelength_nm: float
    relative_yield_central: float
    relative_yield_low: float
    relative_yield_high: float
    exponent_central: float
    exponent_range: tuple[float, float]
    tier: TierLabel = field(
        default_factory=lambda: TierLabel(
            tier=EpistemicTier.ANALYTICAL,
            claim="Single-atom efficiency anti-scaling",
            note="eta ~ lambda^-(5 to 6.5); Shiner et al. PRL 2009",
        )
    )


@dataclass(frozen=True)
class PhaseMatchingProxy:
    """Phase-matching window proxy.

    Tier: ANALYTICAL (proxy). Compares ionization fraction at the
    quoted intensity to a critical-ionization-fraction threshold drawn
    from published phase-matching theory. Does not compute coherence
    length L_coh; does not validate macroscopic build-up. It answers a
    binary-with-margin question: 'is this regime classically
    phase-matchable, or in the over-ionized regime?'.
    """

    gas: str
    ionization_fraction: float
    critical_fraction: float
    in_window: bool
    margin: float  # critical_fraction - ionization_fraction (positive => OK)
    medium_length_mm: float
    pressure_mbar: float
    tier: TierLabel = field(
        default_factory=lambda: TierLabel(
            tier=EpistemicTier.ANALYTICAL,
            claim="Phase-matching window proxy",
            note="Compares ionization fraction to eta_crit; not L_coh",
        )
    )


@dataclass(frozen=True)
class BeamlineTransmission:
    """Compound beamline transmission.

    Tier: ANALYTICAL. Product of mirror reflectivities (R^N) and filter
    transmissions (T^M). Caller provides reflectivity / transmission
    values from cited optics datasheets; defaults are representative for
    Mo/Si multilayer mirrors near 13.5 nm and Al/Zr filters in the
    soft-EUV / VUV window. This is generation-side photons -> in-vacuum
    delivered photons; it does NOT include sample absorption or
    detector quantum efficiency.
    """

    n_mirrors: int
    mirror_reflectivity: float
    n_filters: int
    filter_transmission: float
    transmission: float
    tier: TierLabel = field(
        default_factory=lambda: TierLabel(
            tier=EpistemicTier.ANALYTICAL,
            claim="Compound beamline transmission",
            note="R^N * T^M; source-side -> in-vacuum delivered, no sample",
        )
    )


@dataclass(frozen=True)
class FluxBudget:
    """Generated vs delivered photon flux split.

    The repo distinguishes three planes:
      * source_photons_per_second: at the gas-jet exit (single-atom yield
        times macroscopic density / interaction-volume scaling). LITERATURE
        anchor unless the caller explicitly provides a model.
      * beamline_transmission: ANALYTICAL product of optics throughputs.
      * delivered_photons_per_second: source * beamline; what reaches the
        application plane in vacuum.

    The default `delivered_photons_per_second` is conservatively rounded
    down because beamline losses are highly geometry-dependent.
    """

    source_photons_per_second: float
    beamline_transmission: float
    delivered_photons_per_second: float
    source_basis: TierLabel
    beamline_basis: TierLabel
    delivered_basis: TierLabel = field(
        default_factory=lambda: TierLabel(
            tier=EpistemicTier.PARAMETERIZED,
            claim="Delivered application-plane flux (vacuum)",
            note=(
                "source photons * beamline transmission; ignores sample "
                "absorption and detector QE"
            ),
        )
    )


# ---------------------------------------------------------------------------
# Core calculators
# ---------------------------------------------------------------------------

def ponderomotive_energy_ev(intensity_w_cm2: float, wavelength_nm: float) -> float:
    """Ponderomotive energy U_p in eV.

    U_p[eV] = 9.33e-14 * I[W/cm^2] * lambda[um]^2

    Tier: ANALYTICAL. Exact within the dipole approximation.
    """
    if intensity_w_cm2 <= 0:
        raise ValueError("intensity must be positive")
    if wavelength_nm <= 0:
        raise ValueError("wavelength must be positive")
    wavelength_um = wavelength_nm / 1000.0
    return UP_PREFACTOR_PER_W_CM2_UM2 * intensity_w_cm2 * (wavelength_um ** 2)


def get_ionization_potential_ev(gas: str) -> float:
    """Look up I_p in eV for a supported HHG gas (LITERATURE / NIST)."""
    try:
        return IONIZATION_POTENTIALS_EV[gas]
    except KeyError as exc:
        raise KeyError(
            f"unknown gas '{gas}'; supported: "
            f"{sorted(IONIZATION_POTENTIALS_EV)}"
        ) from exc


def cutoff_energy(
    intensity_w_cm2: float,
    driver_wavelength_nm: float = REFERENCE_DRIVER_WAVELENGTH_NM,
    gas: str = "Ar",
) -> CutoffResult:
    """Three-step-model cutoff energy E_cut = 3.17 U_p + I_p.

    Tier: ANALYTICAL. Exact within the strong-field three-step model
    (Lewenstein 1994; Corkum 1993). Cutoff energy is single-atom; it
    does not account for macroscopic phase matching, plasma blue-shift,
    or absorption.
    """
    ip_ev = get_ionization_potential_ev(gas)
    up_ev = ponderomotive_energy_ev(intensity_w_cm2, driver_wavelength_nm)
    e_cut = CUTOFF_UP_PREFACTOR * up_ev + ip_ev
    cutoff_wavelength_nm = HC_EV_NM / e_cut

    # Maximum odd harmonic order achievable.
    fundamental_ev = HC_EV_NM / driver_wavelength_nm
    q_max = int(e_cut / fundamental_ev)
    if q_max % 2 == 0:
        q_max -= 1
    q_max = max(q_max, 1)

    return CutoffResult(
        cutoff_ev=e_cut,
        ponderomotive_ev=up_ev,
        ionization_potential_ev=ip_ev,
        max_harmonic_order=q_max,
        cutoff_wavelength_nm=cutoff_wavelength_nm,
        driver_wavelength_nm=driver_wavelength_nm,
        intensity_w_cm2=intensity_w_cm2,
        gas=gas,
    )


def efficiency_scaling(
    driver_wavelength_nm: float,
    reference_wavelength_nm: float = REFERENCE_DRIVER_WAVELENGTH_NM,
    exponent_central: float = EFFICIENCY_SCALING_EXPONENT_CENTRAL,
    exponent_range: tuple[float, float] = EFFICIENCY_SCALING_EXPONENT_RANGE,
) -> EfficiencyScalingResult:
    """Single-atom HHG yield versus driver wavelength.

    eta(lambda) / eta(lambda_ref) = (lambda / lambda_ref)^-n

    where n in [5.0, 6.5] (Shiner et al. PRL 2009, 800-1850 nm in Xe/Kr).

    Returned values are *relative* and dimensionless. Absolute flux is
    not implied.
    """
    if driver_wavelength_nm <= 0 or reference_wavelength_nm <= 0:
        raise ValueError("wavelengths must be positive")
    ratio = driver_wavelength_nm / reference_wavelength_nm
    yield_central = ratio ** (-exponent_central)
    yield_low = ratio ** (-exponent_range[1])     # steeper exponent => lower yield at long lambda
    yield_high = ratio ** (-exponent_range[0])    # shallower exponent => higher yield at long lambda
    # Sort so low <= central <= high regardless of whether ratio > 1 or < 1.
    lo, hi = sorted([yield_low, yield_high])
    return EfficiencyScalingResult(
        driver_wavelength_nm=driver_wavelength_nm,
        reference_wavelength_nm=reference_wavelength_nm,
        relative_yield_central=yield_central,
        relative_yield_low=lo,
        relative_yield_high=hi,
        exponent_central=exponent_central,
        exponent_range=exponent_range,
    )


def phase_matching_window(
    gas: str,
    intensity_w_cm2: float,
    medium_length_mm: float,
    pressure_mbar: float,
    ionization_fraction: float | None = None,
    critical_fraction: float | None = None,
) -> PhaseMatchingProxy:
    """Classical phase-matching window proxy.

    Below the critical ionization fraction (gas-dependent, typically 3-9%
    for Ar/Kr/Xe and ~1% for Ne, ~0.5% for He), gas-dispersion and
    plasma-dispersion contributions can be balanced by tuning pressure
    and focusing geometry, allowing harmonic build-up over a coherence
    length L_coh > medium length L_med. Above eta_crit, plasma dispersion
    dominates and classical phase matching breaks down.

    The caller may pass an externally computed ionization fraction
    (e.g., from an ADK model). If not supplied, an order-of-magnitude
    proxy is used: eta ~ (I / I_sat)^2 with I_sat = 5e14 W/cm^2 for Ar
    and a corresponding scale for other gases. THIS IS A SCALAR PROXY,
    not an ADK calculation.

    Tier: ANALYTICAL (proxy).
    """
    if medium_length_mm <= 0 or pressure_mbar <= 0:
        raise ValueError("medium length and pressure must be positive")
    eta_crit = (
        critical_fraction
        if critical_fraction is not None
        else CRITICAL_IONIZATION_FRACTION_DEFAULT.get(gas, 0.03)
    )
    if ionization_fraction is None:
        # Crude scalar proxy: I_sat ~ 5e14 (Ar baseline).
        i_sat = {
            "He": 1.5e15,
            "Ne": 8.7e14,
            "Ar": 5.0e14,
            "Kr": 3.0e14,
            "Xe": 1.7e14,
        }.get(gas, 5.0e14)
        ionization_fraction = min(0.999, (intensity_w_cm2 / i_sat) ** 2)

    margin = eta_crit - ionization_fraction
    return PhaseMatchingProxy(
        gas=gas,
        ionization_fraction=float(ionization_fraction),
        critical_fraction=float(eta_crit),
        in_window=ionization_fraction <= eta_crit,
        margin=float(margin),
        medium_length_mm=medium_length_mm,
        pressure_mbar=pressure_mbar,
    )


def beamline_transmission(
    n_mirrors: int = 2,
    mirror_reflectivity: float = 0.65,
    n_filters: int = 1,
    filter_transmission: float = 0.50,
) -> BeamlineTransmission:
    """Compound beamline transmission T_total = R^N * T^M.

    Defaults are representative of a Mo/Si multilayer-mirror beamline
    near 13.5 nm with one Al or Zr metal filter. For other photon
    energies the caller must supply appropriate values from optics
    datasheets (e.g., CXRO).

    Tier: ANALYTICAL.
    """
    if n_mirrors < 0 or n_filters < 0:
        raise ValueError("counts must be non-negative")
    if not (0.0 <= mirror_reflectivity <= 1.0):
        raise ValueError("reflectivity must be in [0,1]")
    if not (0.0 <= filter_transmission <= 1.0):
        raise ValueError("filter transmission must be in [0,1]")
    t = (mirror_reflectivity ** n_mirrors) * (filter_transmission ** n_filters)
    return BeamlineTransmission(
        n_mirrors=n_mirrors,
        mirror_reflectivity=mirror_reflectivity,
        n_filters=n_filters,
        filter_transmission=filter_transmission,
        transmission=float(t),
    )


def split_generated_vs_delivered(
    source_photons_per_second: float,
    beamline: BeamlineTransmission,
    *,
    source_basis: TierLabel | None = None,
) -> FluxBudget:
    """Combine a source-side flux estimate with a beamline transmission.

    The source basis must be supplied with its own tier label. The repo
    does NOT compute source flux from first principles; typical numbers
    are quoted from published industrial HHG sources (e.g., KMLabs
    XUUS-4: ~1e11 photons/s/harmonic at 35 nm, ~1.5e7 photons/s/harmonic
    at 13.5 nm in He gas).
    """
    if source_basis is None:
        source_basis = TierLabel(
            tier=EpistemicTier.LITERATURE,
            claim="Source-side photon flux at gas-jet exit",
            note=(
                "Quoted from industrial datasheets (KMLabs XUUS-4, "
                "Coherent Astrella). Not reproduced in this repo."
            ),
        )
    delivered = source_photons_per_second * beamline.transmission
    return FluxBudget(
        source_photons_per_second=float(source_photons_per_second),
        beamline_transmission=beamline.transmission,
        delivered_photons_per_second=float(delivered),
        source_basis=source_basis,
        beamline_basis=beamline.tier,
    )


# ---------------------------------------------------------------------------
# Convenience: harmonic order to wavelength
# ---------------------------------------------------------------------------

def harmonic_wavelength_nm(harmonic_order: int, driver_wavelength_nm: float) -> float:
    """lambda_q = lambda_drive / q for odd harmonic order q."""
    if harmonic_order <= 0:
        raise ValueError("harmonic order must be positive")
    return driver_wavelength_nm / harmonic_order


def harmonic_photon_energy_ev(harmonic_order: int, driver_wavelength_nm: float) -> float:
    """Photon energy of the q-th harmonic, in eV."""
    return HC_EV_NM / harmonic_wavelength_nm(harmonic_order, driver_wavelength_nm)


__all__ = [
    "HC_EV_NM",
    "IONIZATION_POTENTIALS_EV",
    "CRITICAL_IONIZATION_FRACTION_DEFAULT",
    "EFFICIENCY_SCALING_EXPONENT_CENTRAL",
    "EFFICIENCY_SCALING_EXPONENT_RANGE",
    "REFERENCE_DRIVER_WAVELENGTH_NM",
    "CutoffResult",
    "EfficiencyScalingResult",
    "PhaseMatchingProxy",
    "BeamlineTransmission",
    "FluxBudget",
    "ponderomotive_energy_ev",
    "get_ionization_potential_ev",
    "cutoff_energy",
    "efficiency_scaling",
    "phase_matching_window",
    "beamline_transmission",
    "split_generated_vs_delivered",
    "harmonic_wavelength_nm",
    "harmonic_photon_energy_ev",
]
