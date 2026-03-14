import numpy as np

# Ionization potentials in eV for common HHG gases
IONIZATION_POTENTIALS = {
    "Ar": 15.76,
    "Ne": 21.56,
    "Xe": 12.13,
    "Kr": 14.00,
}


def calculate_cutoff_energy(intensity_w_cm2, ionization_potential_ev):
    # Up (Ponderomotive energy) = 9.33e-14 * I * lambda^2
    wavelength_um = 0.8
    up = 9.33e-14 * intensity_w_cm2 * (wavelength_um**2)
    return ionization_potential_ev + 3.17 * up


def get_harmonic_wavelength(q, fundamental_nm=800):
    return fundamental_nm / q


def get_ionization_potential(gas_type):
    """Return ionization potential in eV for the given gas."""
    return IONIZATION_POTENTIALS[gas_type]


def get_max_harmonic_order(cutoff_ev, fundamental_nm=800):
    """Return the maximum odd harmonic order achievable at the given cutoff energy."""
    fundamental_ev = 1239.8 / fundamental_nm  # photon energy from wavelength
    q_max = int(cutoff_ev / fundamental_ev)
    if q_max % 2 == 0:
        q_max -= 1  # HHG only produces odd harmonics
    return max(q_max, 1)


def get_hhg_conversion_efficiency(gas_type, harmonic_order):
    """Rough conversion efficiency estimate for HHG plateau harmonics."""
    # Typical values: ~10^-6 for plateau, drops near cutoff
    base = {"Ar": 1e-6, "Ne": 5e-7, "Xe": 2e-6, "Kr": 8e-7}
    eff = base.get(gas_type, 1e-6)
    # Efficiency drops for higher harmonics (near cutoff)
    if harmonic_order > 50:
        eff *= 0.5
    if harmonic_order > 70:
        eff *= 0.3
    return eff
