from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
import numpy as np
from backend.euv_psf import generate_elliptical_source, propagate_asm
from backend.resist_model import calculate_3d_resist_profile
from backend.lithography_model import VirtualLithoProcess
from backend.dose_engine import PhoenixEngine
from backend.visualization import build_pipeline_figure

app = FastAPI(title="Laser-HHG-EUV Lab")

model = VirtualLithoProcess()
phoenix = PhoenixEngine()


@app.get("/api/fleet-economics")
async def get_economics():
    return {
        "unit_cost_savings": "99.2%",
        "power_draw_reduction": "99.9%",
        "redundancy_impact_per_unit": "1.1%"
    }


@app.post("/api/simulate")
async def simulate(payload: dict = Body(...)):
    ai = np.zeros((256, 256))
    ai[:, 118:138] = 1.0

    dev_rate = model.simulate_chain(ai, {
        "dose": payload.get("dose", 20),
        "peb_time": payload.get("peb_time", 60),
        "diffusion_coef": payload.get("diffusion_coef", 5.0),
        "k_amp": payload.get("k_amp", 0.2),
        "r_max": payload.get("r_max", 100),
        "r_min": payload.get("r_min", 0.1),
        "n_mack": payload.get("n_mack", 5)
    })

    return {
        "status": "success",
        "visual_data": dev_rate.tolist(),
        "metrics": {
            "max_rate": float(np.max(dev_rate)),
            "mean_rate": float(np.mean(dev_rate))
        }
    }


@app.get("/api/visualize", response_class=HTMLResponse)
async def visualize(
    dose: float = 20.0,
    peb_time: float = 60.0,
    diffusion_coef: float = 5.0,
    k_amp: float = 0.2,
    r_max: float = 100.0,
    r_min: float = 0.1,
    n_mack: int = 5,
):
    ai = np.zeros((256, 256))
    ai[:, 118:138] = 1.0

    params = {
        "dose": dose, "peb_time": peb_time,
        "diffusion_coef": diffusion_coef, "k_amp": k_amp,
        "r_max": r_max, "r_min": r_min, "n_mack": n_mack,
    }

    stages = model.simulate_chain_detailed(ai, params)
    fig = build_pipeline_figure(stages, title=f"EUV Litho Pipeline (dose={dose} mJ/cm\u00b2)")
    return fig.to_html(full_html=True, include_plotlyjs="cdn")


@app.get("/api/v1/system-state")
async def get_system_state():
    return {
        "active_hypotheses": phoenix.hypotheses,
        "correction_factor": phoenix.get_correction_factor(),
        "dose_tolerance": f"{phoenix.dose_tolerance * 100}%",
        "status": "Adaptive Gating Active"
    }
