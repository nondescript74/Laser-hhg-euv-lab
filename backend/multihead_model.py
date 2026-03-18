"""Multi-head writer array model for tiled maskless lithography.

Models the patent's core architecture: a 2D array of writer heads,
each exposing a local tile on the wafer, with stitching overlap zones
and per-site calibration.
"""

from dataclasses import dataclass, field
import numpy as np


# --- Architecture definitions ---
ARCHITECTURES = {
    "A": {
        "name": "Architecture A — NIR/Visible",
        "short": "A: NIR/Vis",
        "wavelength_nm": 405,
        "wavelength_label": "405 nm (GaN VCSEL)",
        "emitter_type": "GaN VCSEL array",
        "optics_material": "BK7 / fused silica",
        "tile_um": 200,
        "na": 0.3,
        "resolution_nm": 500,
        "emitter_pitch_um": 10,
        "power_per_emitter_mw": 2.0,
        "color": "#e63946",
        "description": "Proof-of-concept platform. NIR/visible VCSELs with standard MEMS "
                       "steering. Validates tiling, stitching, and calibration subsystems.",
        "trl": 5,
    },
    "B": {
        "name": "Architecture B — Deep UV",
        "short": "B: DUV",
        "wavelength_nm": 248,
        "wavelength_label": "248 nm (AlGaN DUV)",
        "emitter_type": "AlGaN DUV VCSEL array",
        "optics_material": "Fused silica / CaF\u2082 / MgF\u2082",
        "tile_um": 100,
        "na": 0.6,
        "resolution_nm": 80,
        "emitter_pitch_um": 5,
        "power_per_emitter_mw": 0.5,
        "color": "#457b9d",
        "description": "Production-class DUV writer. AlGaN deep-UV emitters at 193\u2013300 nm "
                       "with UV-compatible MEMS optics and high-NA micro-objectives.",
        "trl": 3,
    },
    "C": {
        "name": "Architecture C — EUV (Rydberg HHG)",
        "short": "C: EUV",
        "wavelength_nm": 13.5,
        "wavelength_label": "13.5 nm (Rydberg HHG)",
        "emitter_type": "Mo/Si MEMS mirror modulator",
        "optics_material": "Mo/Si multilayer reflectors",
        "tile_um": 100,
        "na": 0.33,
        "resolution_nm": 7,
        "emitter_pitch_um": 2,
        "power_per_emitter_mw": 0.001,
        "color": "#6a0dad",
        "description": "EUV prototype. Rydberg-enhanced HHG source feeds MEMS mirror "
                       "modulator heads with Mo/Si multilayer coatings at 13.5 nm.",
        "trl": 2,
    },
}


@dataclass
class WriterHead:
    """A single writer head in the multi-head array."""
    head_id: int
    row: int
    col: int
    tile_x_um: float        # tile center x on wafer
    tile_y_um: float        # tile center y on wafer
    tile_size_um: float     # side length of square tile
    n_emitters: int         # emitters per head (n x n)
    emitter_pitch_um: float
    power_mw: float         # total optical power from this head
    # Per-site calibration: correction factors for each emitter
    calibration_map: np.ndarray = field(default=None, repr=False)


@dataclass
class MultiHeadArray:
    """A 2D array of writer heads tiling a wafer region."""
    arch_key: str
    n_rows: int
    n_cols: int
    tile_size_um: float
    overlap_um: float       # overlap between adjacent tiles
    heads: list = field(default_factory=list)
    wafer_region_x_um: float = 0.0
    wafer_region_y_um: float = 0.0


def build_multihead_array(
    arch_key: str = "A",
    n_rows: int = 4,
    n_cols: int = 4,
    overlap_pct: float = 5.0,
    emitters_per_side: int = 16,
) -> MultiHeadArray:
    """Build a multi-head writer array for the given architecture."""
    arch = ARCHITECTURES[arch_key]
    tile_size = arch["tile_um"]
    overlap_um = tile_size * overlap_pct / 100.0
    pitch = tile_size - overlap_um  # center-to-center spacing

    heads = []
    for r in range(n_rows):
        for c in range(n_cols):
            head_id = r * n_cols + c
            cx = c * pitch + tile_size / 2
            cy = r * pitch + tile_size / 2
            n_emitters = emitters_per_side ** 2
            power = n_emitters * arch["power_per_emitter_mw"]

            # Simulate fabrication-induced intensity variation (±15%)
            rng = np.random.RandomState(42 + head_id)
            cal_map = 1.0 + 0.15 * (rng.rand(emitters_per_side, emitters_per_side) - 0.5)

            heads.append(WriterHead(
                head_id=head_id,
                row=r, col=c,
                tile_x_um=cx, tile_y_um=cy,
                tile_size_um=tile_size,
                n_emitters=n_emitters,
                emitter_pitch_um=arch["emitter_pitch_um"],
                power_mw=power,
                calibration_map=cal_map,
            ))

    region_x = n_cols * pitch + overlap_um
    region_y = n_rows * pitch + overlap_um

    return MultiHeadArray(
        arch_key=arch_key,
        n_rows=n_rows, n_cols=n_cols,
        tile_size_um=tile_size,
        overlap_um=overlap_um,
        heads=heads,
        wafer_region_x_um=region_x,
        wafer_region_y_um=region_y,
    )


def compute_tile_exposure(
    arch_key: str,
    source_power_mw: float,
    dose_mj_cm2: float = 15.0,
    n_heads: int = 16,
) -> dict:
    """Compute exposure time per tile and total wafer time."""
    arch = ARCHITECTURES[arch_key]
    tile_um = arch["tile_um"]
    tile_area_cm2 = (tile_um * 1e-4) ** 2
    energy_per_tile_mj = dose_mj_cm2 * tile_area_cm2
    power_per_head_mw = source_power_mw / n_heads if n_heads > 0 else source_power_mw

    time_per_tile_s = energy_per_tile_mj / power_per_head_mw if power_per_head_mw > 0 else float("inf")

    # 300mm wafer: ~707 mm² active area
    wafer_area_um2 = 707e6  # µm²
    tile_area_um2 = tile_um ** 2
    tiles_per_wafer = int(wafer_area_um2 / tile_area_um2)

    # With n_heads in parallel, each head covers tiles_per_wafer / n_heads tiles
    tiles_per_head = tiles_per_wafer / n_heads if n_heads > 0 else tiles_per_wafer
    total_exposure_s = tiles_per_head * time_per_tile_s
    # Add 20% overhead for stepping/settling
    total_time_s = total_exposure_s * 1.2

    return {
        "arch_key": arch_key,
        "arch_name": arch["name"],
        "tile_um": tile_um,
        "tile_area_cm2": tile_area_cm2,
        "energy_per_tile_mj": energy_per_tile_mj,
        "power_per_head_mw": power_per_head_mw,
        "time_per_tile_ms": time_per_tile_s * 1000,
        "tiles_per_wafer": tiles_per_wafer,
        "tiles_per_head": tiles_per_head,
        "n_heads": n_heads,
        "total_exposure_s": total_exposure_s,
        "total_time_s": total_time_s,
        "wph": 3600 / total_time_s if total_time_s > 0 else 0,
        "dose_mj_cm2": dose_mj_cm2,
        "source_power_mw": source_power_mw,
    }



# --- Lab 91 Use Case: MoS₂ 2D Material RF Switches ---

LAB91_PROCESS = {
    "company": "Lab 91",
    "location": "Austin, TX",
    "mission": "Automating transfer of 2D materials (MoS₂) from growth wafers to target wafers",
    "beachhead": "RF switches for 6G",
    "future": "Transistors at sub-2nm nodes",
    "current_process": {
        "patterning": "EBL (electron beam lithography)",
        "growth": "CVD MoS₂ on sapphire or glass",
        "transfer": "Wet/dry transfer onto device substrates",
        "resist": "PMMA (Protocol II) / AZ1512HS (Protocol I)",
        "challenge": "Clean contact formation — polymer residue degrades MoS₂ contacts",
    },
    "switch_area_um2": 0.5 * 0.5,  # 0.5×0.5 µm² switch area
    "contact_cd_nm": 300,  # minimum contact width
}

# Shot noise comparison at 2×2 nm² voxel
SHOT_NOISE_COMPARISON = {
    "voxel_nm": 2,
    "euv": {
        "wavelength_nm": 13.5,
        "dose_mj_cm2": 60,
        "photon_energy_ev": 91.8,  # 13.5 nm
        "photons_per_voxel": 163,
        "shot_noise_pct": 7.8,
    },
    "vcsel_405": {
        "wavelength_nm": 405,
        "dose_mj_cm2": 20,
        "photon_energy_ev": 3.06,  # 405 nm
        "photons_per_voxel": 1630,
        "shot_noise_pct": 2.5,
    },
}


def compute_lab91_throughput(
    n_emitters: int = 12_000,
    pixel_clock_ghz: float = 30.0,
    wafer_diameter_mm: float = 300.0,
    pixel_size_nm: float = 2.0,
    overhead_pct: float = 20.0,
) -> dict:
    """Compute Lab 91 specific throughput for MoS₂ RF switch patterning."""
    # Total pixel rate
    pixel_rate_hz = n_emitters * pixel_clock_ghz * 1e9  # px/s

    # Wafer area in pixels
    wafer_area_mm2 = 3.14159 * (wafer_diameter_mm / 2) ** 2
    wafer_area_nm2 = wafer_area_mm2 * 1e12  # mm² → nm²
    pixel_area_nm2 = pixel_size_nm ** 2
    total_pixels = wafer_area_nm2 / pixel_area_nm2

    # Exposure time
    exposure_time_s = total_pixels / pixel_rate_hz
    total_time_s = exposure_time_s * (1 + overhead_pct / 100)
    wph = 3600 / total_time_s if total_time_s > 0 else 0

    # Resolution at 405nm
    na = 0.7
    rayleigh_nm = 0.61 * 405 / na  # ~353 nm (k1=0.61)
    practical_cd_nm = 0.5 * 405 / na  # ~289 nm (k1=0.5)

    return {
        "n_emitters": n_emitters,
        "pixel_clock_ghz": pixel_clock_ghz,
        "pixel_rate_ps": pixel_rate_hz,
        "pixel_rate_label": f"{pixel_rate_hz:.1e}",
        "wafer_diameter_mm": wafer_diameter_mm,
        "total_pixels": total_pixels,
        "exposure_time_s": exposure_time_s,
        "total_time_s": total_time_s,
        "wph": wph,
        "na": na,
        "rayleigh_cd_nm": rayleigh_nm,
        "practical_cd_nm": practical_cd_nm,
        "pixel_dwell_ps": 1e12 / (pixel_clock_ghz * 1e9),  # ps per pixel
    }


# Five modifications to Lab 91's process
LAB91_MODIFICATIONS = [
    {
        "id": 1,
        "title": "Contact Patterning: Replace EBL with VCSEL Direct Optical Write",
        "icon": "🔬",
        "current": "EBL — serial, slow, electron dose (100–1000 µC/cm²) damages MoS₂ via charging and radiolysis",
        "proposed": "405 nm optical exposure avoids electron-induced damage mechanisms (charging, radiolysis, S-vacancy creation), shifting interaction into a controllable photochemical/photothermal regime",
        "key_numbers": [
            "405 nm at NA=0.7 → 290 nm resolution (sufficient for ≥300 nm contacts in far-field)",
            "No electron-induced charging or radiolysis — categorically gentler than EBL",
            "Future scaling path: near-field apertures (50–100 nm) for sub-diffraction contacts below 100 nm",
        ],
        "color": "#e63946",
    },
    {
        "id": 2,
        "title": "Dose Control: Shot-Noise Advantage of 405 nm Over EUV",
        "icon": "📊",
        "current": "EUV at 60 mJ/cm²: 163 photons per 2nm pixel → 8% shot noise",
        "proposed": "VCSEL 405nm at 20 mJ/cm²: 1,630 photons per 2nm pixel → 2.5% shot noise (3× improvement)",
        "key_numbers": [
            "3× better dose uniformity per pixel vs EUV",
            "Lower contact edge roughness (LER/LWR) floor",
            "Tighter filament formation zone → better ON/OFF ratio reproducibility",
        ],
        "color": "#457b9d",
    },
    {
        "id": 3,
        "title": "Resist Chemistry: Metal-Oxide or t-SPL Resists",
        "icon": "🧪",
        "current": "PMMA leaves residue degrading MoS₂ contacts; AZ1512HS requires DUV + IBE cleaning",
        "proposed": "Metal-oxide resists (HfO₂/ZrO₂) — zero organic residue, 5–10× etch resistance; or gold mask lithography for contamination-free contacts",
        "key_numbers": [
            "Zero organic residue after development",
            "5–10× higher etch resistance than PMMA",
            "Gold mask lift-off protects MoS₂ surface throughout",
            "Exposure calibrated against resist contrast curve (Hurter-Driffield) for stable CD control under local dose variation",
        ],
        "color": "#2a9d8f",
    },
    {
        "id": 4,
        "title": "Control Architecture: Local Analog Power Stabilization",
        "icon": "⚡",
        "current": "FPGA loop latency 5–10 ns → 150–300× too slow for 33 ps pixel dwell",
        "proposed": "Per-VCSEL analog power stabilization (monitor photodiode + TIA) at the emitter level, plus slower zone-level compensation for transfer-induced thickness nonuniformity",
        "key_numbers": [
            "33 ps pixel dwell at 30 GHz per emitter — requires emitter-local analog control",
            "Per-VCSEL monitor photodiode samples ~1% of output for real-time power stabilization",
            "Zone-level dose correction compensates MoS₂ thickness variation across grain boundaries",
            "Emitter-level power stabilization and scan strategies limit thermal accumulation and cross-talk during exposure",
        ],
        "color": "#e9c46a",
    },
    {
        "id": 5,
        "title": "Transfer Process Integration: In-Situ Write in Transfer Chamber",
        "icon": "🔧",
        "current": "Separate EBL patterning step with vacuum break, atmospheric contamination at contacts",
        "proposed": "VCSEL write head mounted in-situ in transfer tool — expose immediately after MoS₂ placement, before contamination",
        "key_numbers": [
            "Zero vacuum break between transfer and patterning",
            "No resist spin, no EBL chamber needed",
            "Real-time compensation for MoS₂ thickness variation via per-zone dose feedback",
            "Global alignment inherited from Lab 91's transfer tool; local exposure in continuous scan avoids stitching artifacts",
        ],
        "color": "#264653",
    },
]


def simulate_dose_calibration(
    emitters_per_side: int = 16,
    target_dose: float = 1.0,
    seed: int = 42,
) -> dict:
    """Simulate per-site calibration: raw variation, correction, and corrected output."""
    rng = np.random.RandomState(seed)

    # Raw emitter intensity (fabrication variation ±15%)
    raw_intensity = target_dose * (1.0 + 0.15 * (2 * rng.rand(emitters_per_side, emitters_per_side) - 1))

    # Static calibration correction (factory-measured)
    static_correction = target_dose / raw_intensity

    # Apply static correction
    after_static = raw_intensity * static_correction  # should be ~target_dose

    # Simulate thermal drift (±3% temporal variation)
    thermal_drift = 1.0 + 0.03 * (2 * rng.rand(emitters_per_side, emitters_per_side) - 1)
    after_drift = after_static * thermal_drift

    # Dynamic in-situ correction (sensor feedback)
    dynamic_correction = target_dose / after_drift
    final_dose = after_drift * dynamic_correction

    return {
        "raw_intensity": raw_intensity,
        "static_correction": static_correction,
        "after_static": after_static,
        "thermal_drift": thermal_drift,
        "after_drift": after_drift,
        "dynamic_correction": dynamic_correction,
        "final_dose": final_dose,
        "target_dose": target_dose,
        "raw_uniformity_pct": float(np.std(raw_intensity) / np.mean(raw_intensity) * 100),
        "corrected_uniformity_pct": float(np.std(final_dose) / np.mean(final_dose) * 100),
    }
