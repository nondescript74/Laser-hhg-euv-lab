import numpy as np
from backend.multihead_model import (
    ARCHITECTURES,
    build_multihead_array,
    compute_tile_exposure,
    simulate_dose_calibration,
    LAB91_PROCESS,
    LAB91_MODIFICATIONS,
    SHOT_NOISE_COMPARISON,
    compute_lab91_throughput,
)
from backend.visualization_multihead import build_multihead_html


def test_architectures_defined():
    assert "A" in ARCHITECTURES
    assert "B" in ARCHITECTURES
    assert "C" in ARCHITECTURES
    for key, arch in ARCHITECTURES.items():
        assert arch["wavelength_nm"] > 0
        assert arch["resolution_nm"] > 0
        assert arch["tile_um"] > 0


def test_build_array_default():
    array = build_multihead_array()
    assert array.arch_key == "A"
    assert len(array.heads) == 16  # 4x4
    assert array.n_rows == 4
    assert array.n_cols == 4


def test_build_array_custom():
    array = build_multihead_array("B", n_rows=2, n_cols=3)
    assert len(array.heads) == 6
    assert array.arch_key == "B"


def test_heads_have_calibration_maps():
    array = build_multihead_array(emitters_per_side=8)
    for head in array.heads:
        assert head.calibration_map is not None
        assert head.calibration_map.shape == (8, 8)


def test_tile_exposure_all_architectures():
    for key in ["A", "B", "C"]:
        result = compute_tile_exposure(key, source_power_mw=10.0, n_heads=16)
        assert result["wph"] > 0
        assert result["time_per_tile_ms"] > 0
        assert result["tiles_per_wafer"] > 0


def test_exposure_more_power_faster():
    e_low = compute_tile_exposure("A", source_power_mw=1.0, n_heads=16)
    e_high = compute_tile_exposure("A", source_power_mw=10.0, n_heads=16)
    assert e_high["wph"] > e_low["wph"]


def test_calibration_improves_uniformity():
    cal = simulate_dose_calibration(emitters_per_side=16)
    assert cal["raw_uniformity_pct"] > 1.0  # >1% raw variation
    assert cal["corrected_uniformity_pct"] < 0.01  # near-perfect after correction
    assert cal["raw_intensity"].shape == (16, 16)
    assert cal["final_dose"].shape == (16, 16)


def test_calibration_final_near_target():
    cal = simulate_dose_calibration(target_dose=2.0)
    # Final dose should be very close to target
    assert np.allclose(cal["final_dose"], 2.0, atol=1e-10)


def test_multihead_html_contains_all_sections():
    html = build_multihead_html()
    assert "Architecture Selection" in html
    assert "Writer Head Array" in html
    assert "Architecture Comparison" in html
    assert "Per-Tile Exposure Calculator" in html
    assert "Per-Site Dose Calibration" in html
    assert "Multi-Head Array" in html


def test_multihead_html_all_architectures():
    for key in ["A", "B", "C"]:
        html = build_multihead_html(arch_key=key)
        assert ARCHITECTURES[key]["name"] in html


def test_lab91_throughput_meets_target():
    result = compute_lab91_throughput(n_emitters=12_000)
    assert result["wph"] >= 60  # must meet 60 wph target
    assert result["total_time_s"] <= 60  # under 60 seconds per wafer
    assert result["pixel_dwell_ps"] > 0


def test_lab91_throughput_scales_with_emitters():
    r1 = compute_lab91_throughput(n_emitters=4_000)
    r2 = compute_lab91_throughput(n_emitters=12_000)
    assert r2["wph"] > r1["wph"]
    assert r2["total_time_s"] < r1["total_time_s"]


def test_lab91_resolution_sufficient_for_contacts():
    result = compute_lab91_throughput()
    # 405nm at NA=0.7 must resolve Lab 91's ≥300nm contacts
    assert result["practical_cd_nm"] <= LAB91_PROCESS["contact_cd_nm"]


def test_lab91_modifications_complete():
    assert len(LAB91_MODIFICATIONS) == 5
    for mod in LAB91_MODIFICATIONS:
        assert "title" in mod
        assert "current" in mod
        assert "proposed" in mod
        assert len(mod["key_numbers"]) >= 2


def test_shot_noise_vcsel_better_than_euv():
    snc = SHOT_NOISE_COMPARISON
    assert snc["vcsel_405"]["photons_per_voxel"] > snc["euv"]["photons_per_voxel"]
    assert snc["vcsel_405"]["shot_noise_pct"] < snc["euv"]["shot_noise_pct"]


def test_multihead_html_contains_lab91():
    html = build_multihead_html()
    assert "Lab 91" in html
    assert "MoS" in html
    assert "Shot Noise" in html
    assert "Process Modifications" in html
