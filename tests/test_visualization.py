import numpy as np
from backend.lithography_model import VirtualLithoProcess
from backend.visualization import build_pipeline_figure


def test_pipeline_figure_has_four_traces():
    model = VirtualLithoProcess(nx=64, ny=64)
    ai = np.zeros((64, 64))
    ai[:, 24:40] = 1.0
    stages = model.simulate_chain_detailed(ai, {"dose": 20})
    fig = build_pipeline_figure(stages)
    assert len(fig.data) == 4
    assert set(stages.keys()) == {"aerial_image", "acid_map", "deprotection", "dissolution_rate"}


def test_detailed_matches_original():
    """simulate_chain_detailed dissolution must match simulate_chain output."""
    model = VirtualLithoProcess(nx=64, ny=64)
    ai = np.zeros((64, 64))
    ai[:, 24:40] = 1.0
    params = {"dose": 20}
    np.random.seed(42)
    original = model.simulate_chain(ai, params)
    np.random.seed(42)
    detailed = model.simulate_chain_detailed(ai, params)
    np.testing.assert_array_equal(original, detailed["dissolution_rate"])
