import numpy as np
from scipy.ndimage import gaussian_filter


class VirtualLithoProcess:
    def __init__(self, nx=256, ny=256, dx=1.0):
        self.nx = nx
        self.ny = ny
        self.dx = dx

    def exposure_stochastic_euv(self, aerial_image, dose_mj_cm2):
        """Step 1: EUV Photon Stochastics"""
        photon_energy_j = 1.47e-17
        mean_photons_per_nm2 = (dose_mj_cm2 * 1e-9) / photon_energy_j
        local_mean = aerial_image * mean_photons_per_nm2 * (self.dx**2)

        # Stochastic sampling ensures High Dose != Low Dose
        photons = np.random.poisson(local_mean).astype(float)

        # Acid map calculation
        acid_map = 1 - np.exp(-1e-10 * photons / (self.dx**2))
        return acid_map

    def post_exposure_bake(
        self, acid_map, bake_time=60, k_amp=0.2, d_acid=5.0
    ):
        """Step 2: Reaction-Diffusion (PEB)"""
        diffusion_sigma_nm = np.sqrt(2 * d_acid * bake_time)
        sigma_val = diffusion_sigma_nm / self.dx
        diffused_acid = gaussian_filter(acid_map, sigma=sigma_val)
        m_latent_image = np.exp(-k_amp * diffused_acid * bake_time)
        return m_latent_image

    def mack_dissolution(self, m_map, r_max=100, r_min=0.1, n_mack=5):
        """Step 3: Mack's Dissolution Model"""
        deprotection_level = 1.0 - m_map
        rate = r_max * np.power(deprotection_level, n_mack) + r_min
        return rate

    def simulate_chain(self, aerial_image, params):
        """Full E2E process"""
        dose = params.get('dose', 20)

        # Step 1: Exposure
        acid = self.exposure_stochastic_euv(aerial_image, dose)

        # Step 2: PEB
        m_latent = self.post_exposure_bake(
            acid,
            bake_time=params.get('peb_time', 60),
            d_acid=params.get('diffusion_coef', 5.0),
            k_amp=params.get('k_amp', 0.2)
        )

        # Step 3: Dissolution
        return self.mack_dissolution(
            m_map=m_latent,
            r_max=params.get('r_max', 100),
            r_min=params.get('r_min', 0.1),
            n_mack=params.get('n_mack', 5)
        )

    def simulate_chain_detailed(self, aerial_image, params):
        """Full E2E process returning all intermediate maps."""
        dose = params.get('dose', 20)

        acid = self.exposure_stochastic_euv(aerial_image, dose)

        m_latent = self.post_exposure_bake(
            acid,
            bake_time=params.get('peb_time', 60),
            d_acid=params.get('diffusion_coef', 5.0),
            k_amp=params.get('k_amp', 0.2)
        )

        dissolution = self.mack_dissolution(
            m_map=m_latent,
            r_max=params.get('r_max', 100),
            r_min=params.get('r_min', 0.1),
            n_mack=params.get('n_mack', 5)
        )

        return {
            "aerial_image": aerial_image,
            "acid_map": acid,
            "deprotection": 1.0 - m_latent,
            "dissolution_rate": dissolution,
        }
