import numpy as np
from backend.hhg_model import (
    get_ionization_potential,
    get_max_harmonic_order,
    get_hhg_conversion_efficiency,
    calculate_cutoff_energy,
)
from backend.optical_pipeline import EUVOpticalPipeline
from backend.visualization_3d import (
    build_3d_pipeline_figure,
    build_3d_pipeline_html,
    _get_platform_geometry,
)


def test_ionization_potentials():
    assert get_ionization_potential("Ar") == 15.76
    assert get_ionization_potential("Ne") == 21.56
    assert get_ionization_potential("Xe") == 12.13


def test_max_harmonic_order():
    cutoff = calculate_cutoff_energy(1e14, 15.76)
    q = get_max_harmonic_order(cutoff)
    assert q > 0
    assert q % 2 == 1  # must be odd


def test_hhg_conversion_efficiency():
    eff = get_hhg_conversion_efficiency("Ar", 59)
    assert 0 < eff < 1


def test_pipeline_default_components():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    # 7 components: source, lens, gas_cell, filter, mirror1, mirror2, wafer
    assert len(pipeline.components) == 7
    types = [c.component_type for c in pipeline.components]
    assert "source" in types
    assert "gas_cell" in types
    assert "wafer" in types


def test_pipeline_power_budget_decreasing():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    budget = pipeline.compute_power_budget(1.0)
    powers = [b["power_out"] for b in budget]
    # Power should decrease monotonically
    for i in range(1, len(powers)):
        assert powers[i] <= powers[i - 1]
    # Final power should be much less than initial
    assert powers[-1] < 1e-3


def test_pipeline_beam_path():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    z, x, y, r, color_z = pipeline.get_beam_path()
    assert len(z) == 300
    assert len(r) == 300
    assert np.all(r > 0)
    assert color_z > 0


def test_3d_figure_has_traces():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    fig = build_3d_pipeline_figure(pipeline)
    # Should have multiple traces (components + beam + annotations)
    assert len(fig.data) >= 10


def test_pipeline_variable_mirrors():
    for n in [1, 2, 3]:
        pipeline = EUVOpticalPipeline()
        pipeline.build_default_pipeline(n_mirrors=n)
        mirror_count = sum(1 for c in pipeline.components if c.component_type == "mirror")
        assert mirror_count == min(n, 2)  # max 2 mirror positions defined


def test_platform_geometry_has_expected_keys():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    geom = _get_platform_geometry(pipeline, {"gas_type": "Ar"})
    assert "platform" in geom
    assert "hhg" in geom
    assert "power_budget" in geom
    assert "grouped_layers" in geom
    assert "full_layers" in geom
    assert geom["platform"]["total_heads"] == 160
    assert geom["platform"]["heads_per_package"] == 16
    assert len(geom["grouped_layers"]) == 4
    assert len(geom["full_layers"]) == 11


def test_3d_html_has_zoom_control():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    params = {"gas_type": "Ar", "pressure_mbar": 30, "intensity_w_cm2": 1e14,
              "n_mirrors": 2, "filter_material": "Al", "filter_thickness_nm": 200}
    html = build_3d_pipeline_html(pipeline, params)
    assert "zoomSlider" in html
    assert "buildPlatform" in html
    assert "buildPackage" in html
    assert "buildHead" in html
    assert "Integrated Multi-Head Writer Platform" in html


def test_3d_html_has_full_nav():
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline()
    params = {"gas_type": "Ar", "pressure_mbar": 30, "intensity_w_cm2": 1e14,
              "n_mirrors": 2, "filter_material": "Al", "filter_thickness_nm": 200}
    html = build_3d_pipeline_html(pipeline, params)
    assert "2D Process Sim" in html
    assert "3D Pipeline" in html
    assert "Platform Economics" in html
    assert "Multi-Head Array" in html
    assert "PSF Synthesis" in html
    assert "11-DOF Head" in html
