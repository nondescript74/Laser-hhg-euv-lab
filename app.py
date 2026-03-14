from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse, RedirectResponse
import numpy as np
from backend.euv_psf import generate_elliptical_source, propagate_asm
from backend.resist_model import calculate_3d_resist_profile
from backend.lithography_model import VirtualLithoProcess
from backend.dose_engine import PhoenixEngine
from backend.visualization import build_pipeline_figure, build_tunable_html
from backend.optical_pipeline import EUVOpticalPipeline
from backend.visualization_3d import build_3d_pipeline_html

app = FastAPI(title="Laser-HHG-EUV Lab")

model = VirtualLithoProcess()
phoenix = PhoenixEngine()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """<!DOCTYPE html>
<html>
<head>
    <title>Laser-HHG-EUV Lab</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }
        .header { text-align: center; padding: 48px 24px 24px; }
        .header h1 { font-size: 28px; font-weight: 700; color: #fff; letter-spacing: 1px; }
        .header p { font-size: 14px; color: #888; margin-top: 8px; }
        .cards { display: flex; justify-content: center; gap: 28px; padding: 32px 24px; flex-wrap: wrap; }
        .card {
            background: #1a1a2e; border: 1px solid #2a2a4e; border-radius: 12px;
            width: 320px; padding: 28px 24px; text-decoration: none; color: #e0e0e0;
            transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
        }
        .card:hover { transform: translateY(-4px); border-color: #4a6cf7; box-shadow: 0 8px 30px rgba(74,108,247,0.15); }
        .card .icon { font-size: 36px; margin-bottom: 14px; }
        .card h2 { font-size: 18px; font-weight: 600; color: #fff; margin-bottom: 8px; }
        .card p { font-size: 13px; color: #999; line-height: 1.5; }
        .card .tag { display: inline-block; margin-top: 14px; font-size: 11px; padding: 3px 10px; border-radius: 20px; font-weight: 600; }
        .tag-2d { background: #1e3a5f; color: #5ba3e6; }
        .tag-3d { background: #2d1e5f; color: #a37be6; }
        .tag-api { background: #1e5f3a; color: #5be6a3; }
        .footer { text-align: center; padding: 32px; font-size: 12px; color: #555; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Laser-HHG-EUV Lab</h1>
        <p>Chip-Scale Coherent EUV Source Simulation Platform</p>
    </div>
    <div class="cards">
        <a class="card" href="/api/visualize">
            <div class="icon">&#x1F4CA;</div>
            <h2>2D Process Simulation</h2>
            <p>Interactive lithography pipeline: aerial image, acid map, PEB deprotection, and Mack dissolution rate. Tune dose, line width, and process parameters.</p>
            <span class="tag tag-2d">HEATMAPS</span>
        </a>
        <a class="card" href="/api/visualize-3d">
            <div class="icon">&#x1F52C;</div>
            <h2>3D Optical Pipeline</h2>
            <p>Full beam path from VCSEL source through HHG gas cell to wafer. Visualize gas supply, pressures, power budget, and harmonic generation physics.</p>
            <span class="tag tag-3d">3D INTERACTIVE</span>
        </a>
        <a class="card" href="/api/v1/system-state">
            <div class="icon">&#x2699;</div>
            <h2>Phoenix Engine State</h2>
            <p>Adaptive dose correction system status. View active hypotheses, correction factors, and dose tolerance for the Phoenix gating engine.</p>
            <span class="tag tag-api">API JSON</span>
        </a>
    </div>
    <div class="footer">Laser-HHG-EUV Lab &middot; buildzmarter-ai</div>
</body>
</html>"""


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
    line_width: int = 20,
    peb_time: float = 60.0,
    diffusion_coef: float = 5.0,
    k_amp: float = 0.2,
    r_max: float = 100.0,
    r_min: float = 0.1,
    n_mack: int = 5,
):
    ai = np.zeros((256, 256))
    center = 256 // 2
    half = max(1, line_width // 2)
    ai[:, center - half:center + half] = 1.0

    params = {
        "dose": dose, "line_width": line_width, "peb_time": peb_time,
        "diffusion_coef": diffusion_coef, "k_amp": k_amp,
        "r_max": r_max, "r_min": r_min, "n_mack": n_mack,
    }

    stages = model.simulate_chain_detailed(ai, params)
    title = f"EUV Litho Pipeline (dose={dose} mJ/cm\u00b2, line={line_width} nm)"
    return build_tunable_html(stages, params, title=title)


@app.get("/api/visualize-3d", response_class=HTMLResponse)
async def visualize_3d(
    gas_type: str = "Ar",
    pressure_mbar: float = 30.0,
    intensity_w_cm2: float = 1e14,
    n_mirrors: int = 2,
    filter_material: str = "Al",
    filter_thickness_nm: float = 200.0,
):
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline(
        gas_type=gas_type,
        pressure_mbar=pressure_mbar,
        intensity_w_cm2=intensity_w_cm2,
        n_mirrors=n_mirrors,
        filter_material=filter_material,
        filter_thickness_nm=filter_thickness_nm,
    )
    params = {
        "gas_type": gas_type, "pressure_mbar": pressure_mbar,
        "intensity_w_cm2": intensity_w_cm2, "n_mirrors": n_mirrors,
        "filter_material": filter_material, "filter_thickness_nm": filter_thickness_nm,
    }
    return build_3d_pipeline_html(pipeline, params)


@app.get("/api/v1/system-state")
async def get_system_state():
    return {
        "active_hypotheses": phoenix.hypotheses,
        "correction_factor": phoenix.get_correction_factor(),
        "dose_tolerance": f"{phoenix.dose_tolerance * 100}%",
        "status": "Adaptive Gating Active"
    }
