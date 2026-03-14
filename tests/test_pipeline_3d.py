import numpy as np
from backend.hhg_model import (
    get_ionization_potential,
    get_max_harmonic_order,
    get_hhg_conversion_efficiency,
    calculate_cutoff_energy,
)
from backend.optical_pipeline import EUVOpticalPipeline
from backend.visualization_3d import build_3d_pipeline_figure


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
