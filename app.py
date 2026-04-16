"""FastAPI entry point for the Laser-HHG-EUV Lab.

This application is a *parameterized HHG / EUV architectural modeling
lab*. It is not a device demonstration and not an industrial EUV source
claim. Every route returns a page that carries an explicit epistemic
tier badge (analytical / parameterized / architecture / literature),
and the dashboard's top banner reminds the user of that scope.
"""

from fastapi import FastAPI, Body
from fastapi.responses import HTMLResponse
import numpy as np

from backend.euv_psf import generate_elliptical_source, propagate_asm  # noqa: F401
from backend.resist_model import calculate_3d_resist_profile  # noqa: F401
from backend.lithography_model import VirtualLithoProcess
from backend.dose_engine import PhoenixEngine
from backend.visualization import build_pipeline_figure, build_tunable_html  # noqa: F401
from backend.optical_pipeline import EUVOpticalPipeline
from backend.visualization_3d import build_3d_pipeline_html
from backend.fleet_economics import compute_sensitivity_table
from backend.visualization_fleet import build_fleet_dashboard_html
from backend.visualization_multihead import build_multihead_html
from backend.visualization_psf import build_psf_synthesis_html
from backend.visualization_11dof import build_11dof_html
from backend.visualization_hhg_analytical import build_hhg_analytical_html
from backend.wavelength_bridge import build_wavelength_bridge_html
from backend.citations import inject_citations
from backend.epistemic import (
    SCOPE_BANNER_HTML,
    EPISTEMIC_CSS,
    EpistemicTier,
    render_badge,
)

app = FastAPI(title="Laser-HHG-EUV Lab")

model = VirtualLithoProcess()
phoenix = PhoenixEngine()


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    badge_arch = render_badge(EpistemicTier.ARCHITECTURE)
    badge_anal = render_badge(EpistemicTier.ANALYTICAL)
    badge_param = render_badge(EpistemicTier.PARAMETERIZED)
    badge_lit = render_badge(EpistemicTier.LITERATURE)
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Laser-HHG-EUV Lab</title>
    <style>{EPISTEMIC_CSS}</style>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; }}
        .header {{ text-align: center; padding: 36px 24px 18px; }}
        .header h1 {{ font-size: 28px; font-weight: 700; color: #fff; letter-spacing: 1px; }}
        .header p {{ font-size: 14px; color: #888; margin-top: 8px; max-width: 760px; margin-left: auto; margin-right: auto; line-height: 1.5; }}
        .tier-key {{ display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; padding: 8px 24px 24px; }}
        .tier-key > div {{ background: #1a1a2e; padding: 6px 12px; border-radius: 6px; border: 1px solid #2a2a4e; font-size: 12px; color: #cbd5e1; }}
        .cards {{ display: flex; justify-content: center; gap: 22px; padding: 24px 24px; flex-wrap: wrap; }}
        .card {{
            background: #1a1a2e; border: 1px solid #2a2a4e; border-radius: 12px;
            width: 320px; padding: 24px; text-decoration: none; color: #e0e0e0;
            transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
            display: flex; flex-direction: column;
        }}
        .card:hover {{ transform: translateY(-4px); border-color: #4a6cf7; box-shadow: 0 8px 30px rgba(74,108,247,0.15); }}
        .card .icon {{ font-size: 30px; margin-bottom: 10px; }}
        .card h2 {{ font-size: 17px; font-weight: 600; color: #fff; margin-bottom: 6px; }}
        .card p {{ font-size: 13px; color: #94a3b8; line-height: 1.5; flex: 1; }}
        .card .badges {{ margin-top: 12px; }}
        .footer {{ text-align: center; padding: 24px; font-size: 12px; color: #555; max-width: 800px; margin: 0 auto; line-height: 1.5; }}
        .scope-card {{
            background: #0f172a; border-left: 4px solid #f59e0b; padding: 14px 22px;
            margin: 0 24px 18px; font-size: 13px; color: #e2e8f0; line-height: 1.55;
        }}
        .scope-card b {{ color: #fbbf24; }}
        .scope-card code {{ background: #1e293b; padding: 1px 6px; border-radius: 3px; font-family: ui-monospace, Menlo, monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Laser-HHG-EUV Lab</h1>
        <p>Parameterized HHG / EUV architectural modeling lab.
        Generation-side chain (driver \u2192 gas cell \u2192 beamline) with
        explicit epistemic-tier labels on every output.</p>
    </div>

    <div class="scope-card">
        <b>Scope.</b> This repository is an architectural / parameterized
        modeling lab, not a device demonstration and not an industrial
        EUV source claim. High-volume manufacturing EUV lithography uses
        laser-produced-plasma (LPP) sources at power levels not
        accessible to gas-jet HHG; the gap is physical (conversion
        efficiency, duty cycle, repetition rate), not engineering.
        Defensible HHG use cases: <code>CDI</code>, <code>ptychography</code>,
        <code>actinic EUV mask inspection</code>, <code>ARPES</code>.
    </div>

    <div class="tier-key">
        <div>{badge_anal} Analytical / formula-based</div>
        <div>{badge_param} Parameterized model</div>
        <div>{badge_arch} Architecture-level</div>
        <div>{badge_lit} Literature-derived</div>
    </div>

    <div class="cards">
        <a class="card" href="/api/wavelength-bridge">
            <div class="icon">&#x1F308;</div>
            <h2>Wavelength Bridge</h2>
            <p>NIR/MIR drivers \u2192 HHG conversion \u2192 DUV / VUV / EUV / SXR.
            Places this repo and the companion vdW-cavity repo on one
            wavelength axis with industrial anchors.</p>
            <div class="badges">{badge_arch}</div>
        </a>
        <a class="card" href="/api/hhg-analytical">
            <div class="icon">&#x1F4D0;</div>
            <h2>HHG Analytical Calculators</h2>
            <p>Cutoff energy (3.17 U_p + I_p), single-atom efficiency
            anti-scaling, phase-matching-window proxy, compound beamline
            transmission, and generated-vs-delivered flux split.</p>
            <div class="badges">{badge_anal}</div>
        </a>
        <a class="card" href="/api/visualize-3d">
            <div class="icon">&#x1F52C;</div>
            <h2>3D Generation-Chain View</h2>
            <p>Driver \u2192 focusing optic \u2192 gas cell \u2192 metal filter
            \u2192 Mo/Si mirror \u2192 application plane. Architectural diagram
            with HHG physics annotations.</p>
            <div class="badges">{badge_arch}</div>
        </a>
        <a class="card" href="/api/visualize">
            <div class="icon">&#x1F4CA;</div>
            <h2>2D Resist Process</h2>
            <p>Aerial image \u2192 acid map \u2192 PEB \u2192 Mack dissolution.
            Parameterized trade-off explorer; resist parameters not
            calibrated to a specific commercial chemistry.</p>
            <div class="badges">{badge_param}</div>
        </a>
        <a class="card" href="/api/psf-synthesis">
            <div class="icon">&#x1F9EC;</div>
            <h2>PSF Synthesis</h2>
            <p>Spatiotemporal exposure compositing. Incoherent broadening,
            coherent sharpening, coupled spatial-temporal optimization on
            Gaussian sub-exposures.</p>
            <div class="badges">{badge_param}</div>
        </a>
        <a class="card" href="/api/multihead">
            <div class="icon">&#x1F4A0;</div>
            <h2>Multi-Head Packaging</h2>
            <p>Tiled writer-array packaging concept (A/B/C variants),
            stitching zones, per-site dose calibration. Architectural
            illustration only.</p>
            <div class="badges">{badge_arch}</div>
        </a>
        <a class="card" href="/api/fleet-dashboard">
            <div class="icon">&#x1F4B0;</div>
            <h2>Fleet Sensitivity</h2>
            <p>Cost / power / throughput sensitivity table. Architectural
            framing; not a delivered-flux comparison with ASML LPP.</p>
            <div class="badges">{badge_arch}</div>
        </a>
        <a class="card" href="/api/writer-head">
            <div class="icon">&#x1F9F1;</div>
            <h2>11-DOF Writer Head</h2>
            <p>Exploded view of the 11-DOF writer head concept. 3D
            stack from 2D planar layers; architecture diagram only.</p>
            <div class="badges">{badge_arch}</div>
        </a>
    </div>
    <div class="footer">
        Laser-HHG-EUV Lab. Companion to vdw-polaritonics-lab (DUV
        intracavity modulation). All outputs labelled with their
        epistemic tier. See <code>README.md</code> for the full
        evidence-architecture and claim taxonomy.
    </div>
</body>
</html>"""


@app.get("/api/wavelength-bridge", response_class=HTMLResponse)
async def wavelength_bridge():
    """Driver -> harmonic cascade -> DUV/VUV/EUV figure (ARCHITECTURE).

    Cited primary sources: 100 Shiner 2009, 101 Lewenstein 1994,
    102 Wikmark 2022, 103 Coherent/KMLabs XUUS-4, 108 ASML LPP.
    """
    html = build_wavelength_bridge_html()
    return inject_citations(html, extra_refs=[100, 101, 102, 103, 107, 108])


@app.get("/api/hhg-analytical", response_class=HTMLResponse)
async def hhg_analytical(
    driver_wavelength_nm: float = 800.0,
    intensity_w_cm2: float = 1.5e14,
    gas: str = "Ar",
    medium_length_mm: float = 30.0,
    pressure_mbar: float = 30.0,
    n_mirrors: int = 2,
    n_filters: int = 1,
    mirror_reflectivity: float = 0.65,
    filter_transmission: float = 0.50,
):
    """HHG analytical calculator dashboard (ANALYTICAL).

    Cited primary sources: 100 Shiner 2009 (efficiency anti-scaling),
    101 Lewenstein 1994 (SFA cutoff), 102 Wikmark 2022 (PM window),
    103 Coherent/KMLabs (source-side flux anchor), 105 ELI-ALPS pulse
    duration, 106 open-source HHG sim, 107 Corkum 1993, 108 ASML LPP.
    """
    html = build_hhg_analytical_html(
        driver_wavelength_nm=driver_wavelength_nm,
        intensity_w_cm2=intensity_w_cm2,
        gas=gas,
        medium_length_mm=medium_length_mm,
        pressure_mbar=pressure_mbar,
        n_mirrors=n_mirrors,
        n_filters=n_filters,
        mirror_reflectivity=mirror_reflectivity,
        filter_transmission=filter_transmission,
    )
    return inject_citations(
        html, extra_refs=[100, 101, 102, 103, 105, 106, 107, 108]
    )


@app.get("/api/fleet-dashboard", response_class=HTMLResponse)
async def fleet_dashboard(
    dose_mj_cm2: float = 15.0,
    config_name: str = "Specialty / Defense",
):
    from backend.fleet_economics import PLATFORM_CONFIGS
    config = PLATFORM_CONFIGS.get(config_name, list(PLATFORM_CONFIGS.values())[1])
    scenarios = compute_sensitivity_table(
        power_levels_mw=[0.1, 1.0, 5.0, 10.0, 50.0],
        config=config,
        dose_mj_cm2=dose_mj_cm2,
    )
    params = {
        "dose_mj_cm2": dose_mj_cm2,
        "config_name": config_name,
    }
    html = build_fleet_dashboard_html(scenarios, params)
    # 43 ASML NXE platform reference, 100 Shiner efficiency anti-scaling
    # (why HHG can't scale to ASML power levels), 103 KMLabs source-flux
    # anchor, 108 ASML LPP gap statement.
    return inject_citations(html, extra_refs=[43, 44, 45, 100, 103, 108])


@app.get("/api/multihead", response_class=HTMLResponse)
async def multihead(
    arch: str = "A",
    n_rows: int = 4,
    n_cols: int = 4,
    overlap_pct: float = 5.0,
    emitters_per_side: int = 16,
    source_power_mw: float = 10.0,
    dose_mj_cm2: float = 15.0,
):
    html = build_multihead_html(
        arch_key=arch,
        n_rows=n_rows,
        n_cols=n_cols,
        overlap_pct=overlap_pct,
        emitters_per_side=emitters_per_side,
        source_power_mw=source_power_mw,
        dose_mj_cm2=dose_mj_cm2,
    )
    # 40 IMS MBMW-101, 46 Multibeam Corp MEBL (multi-beam packaging
    # precedents), 100 Shiner, 103 KMLabs anchor (the "source power"
    # this packaging concept assumes), 108 ASML LPP gap.
    return inject_citations(
        html, extra_refs=[40, 46, 100, 103, 108]
    )


@app.get("/api/writer-head", response_class=HTMLResponse)
async def writer_head():
    return build_11dof_html()


@app.get("/api/fleet-economics")
async def get_economics():
    scenarios = compute_sensitivity_table()
    return [
        {
            "euv_power_mw": s.euv_power_mw,
            "total_heads": s.total_heads,
            "platform_wph": round(s.wph, 2),
            "platform_cost_m": round(s.platform_cost_m, 1),
            "platform_power_kw": round(s.platform_power_kw, 1),
            "capex_savings_pct": round(s.capex_savings_pct, 1),
            "power_savings_pct": round(s.power_savings_pct, 1),
            "single_head_failure_pct": round(s.single_head_failure_pct, 3),
            # Tier label is part of the JSON payload so downstream
            # consumers (dashboards, exports) cannot strip it.
            "epistemic_tier": "architecture",
            "tier_note": (
                "Architecture-level sensitivity. NOT a delivered-flux "
                "claim vs. ASML LPP."
            ),
        }
        for s in scenarios
    ]


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
        },
        "epistemic_tier": "parameterized",
        "tier_note": (
            "Resist response from parameterized Mack-dissolution + "
            "reaction-diffusion PEB model. Not calibrated to a specific "
            "commercial chemistry."
        ),
    }


@app.get("/api/visualize", response_class=HTMLResponse)
async def visualize(
    dose: float = 15.0,
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
    title = f"EUV Litho Pipeline (dose={dose} mJ/cm\u00b2, line={line_width} nm) [PARAMETERIZED]"
    html = build_tunable_html(stages, params, title=title)
    return inject_citations(html, extra_refs=[42, 52, 53, 54])


@app.get("/api/visualize-3d", response_class=HTMLResponse)
async def visualize_3d(
    gas_type: str = "Ar",
    pressure_mbar: float = 30.0,
    intensity_w_cm2: float = 1.5e14,
    n_mirrors: int = 2,
    filter_material: str = "Al",
    filter_thickness_nm: float = 200.0,
    driver_wavelength_nm: float = 800.0,
):
    pipeline = EUVOpticalPipeline()
    pipeline.build_default_pipeline(
        gas_type=gas_type,
        pressure_mbar=pressure_mbar,
        intensity_w_cm2=intensity_w_cm2,
        n_mirrors=n_mirrors,
        filter_material=filter_material,
        filter_thickness_nm=filter_thickness_nm,
        driver_wavelength_nm=driver_wavelength_nm,
    )
    params = {
        "gas_type": gas_type, "pressure_mbar": pressure_mbar,
        "intensity_w_cm2": intensity_w_cm2, "n_mirrors": n_mirrors,
        "filter_material": filter_material, "filter_thickness_nm": filter_thickness_nm,
        "driver_wavelength_nm": driver_wavelength_nm,
    }
    html = build_3d_pipeline_html(pipeline, params)
    # 100 Shiner, 101 Lewenstein, 102 Wikmark PM, 103 KMLabs source-flux
    # anchor, 104 Carstens CE-HHG, 107 Corkum, 108 ASML LPP gap.
    # Legacy refs 44/45 retained for the SFA/Corkum citations already
    # in-place on the 3D page text.
    return inject_citations(
        html, extra_refs=[44, 45, 100, 101, 102, 103, 104, 107, 108]
    )


@app.get("/api/psf-synthesis", response_class=HTMLResponse)
async def psf_synthesis(
    sigma_nm: float = 10.0,
    target_type: str = "flat_top",
    target_radius_nm: float = 15.0,
    n_sub: int = 9,
    dx_nm: float = 1.0,
    grid_size: int = 128,
    resist_thickness_nm: float = 20.0,
):
    html = build_psf_synthesis_html(
        sigma_nm=sigma_nm,
        target_type=target_type,
        target_radius_nm=target_radius_nm,
        n_sub=n_sub,
        dx_nm=dx_nm,
        grid_size=grid_size,
        resist_thickness_nm=resist_thickness_nm,
    )
    return inject_citations(html, extra_refs=[1, 21, 24, 40, 50, 51])


@app.get("/api/v1/system-state")
async def get_system_state():
    return {
        "active_hypotheses": phoenix.hypotheses,
        "correction_factor": phoenix.get_correction_factor(),
        "dose_tolerance": f"{phoenix.dose_tolerance * 100}%",
        "status": "Adaptive Gating Active",
        "epistemic_tier": "architecture",
        "tier_note": (
            "Phoenix engine state is an architectural placeholder for an "
            "adaptive-dose control loop. No live sensor fusion is "
            "implemented in this repo."
        ),
    }
