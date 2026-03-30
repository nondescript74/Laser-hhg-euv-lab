"""Visualization for PSF Synthesis via Spatiotemporal Exposure Compositing.

Generates an interactive HTML dashboard showing:
1. Native vs. Composite PSF heatmaps (incoherent)
2. Coupled vs. Sequential optimization comparison
3. Coherent PSF sharpening demo
4. Thermal relaxation curves
5. Sub-exposure dither map
6. Cross-section line profiles
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from backend.psf_synthesis import (
    run_psf_synthesis_comparison,
    gaussian_psf,
    measure_fwhm,
    SynthesisComparison,
)


# ── Shared nav + style ──────────────────────────────────────────────

_NAV = """
<div class="nav">
    <a href="/api/visualize">2D Process Sim</a>
    <a href="/api/visualize-3d">3D Pipeline</a>
    <a href="/api/fleet-dashboard">Platform Economics</a>
    <a href="/api/multihead">Multi-Head Array</a>
    <a href="/api/psf-synthesis" class="active">PSF Synthesis</a>
    <a href="/api/writer-head">11-DOF Head</a>
</div>"""

_CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }
.nav { background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }
.nav a { color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }
.nav a:hover { background: #2a2a4e; }
.nav a.active { background: #2563eb; color: #fff; }
.controls {
    background: #fff; padding: 12px 24px; border-bottom: 1px solid #e2e8f0;
    display: flex; flex-wrap: wrap; gap: 14px; align-items: end;
}
.control-group { display: flex; flex-direction: column; gap: 3px; }
.control-group label { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
.control-group input, .control-group select { padding: 5px 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 13px; }
.control-group input { width: 90px; }
.control-group select { width: 130px; }
button {
    padding: 7px 18px; background: #2563eb; color: #fff; border: none;
    border-radius: 4px; font-size: 13px; cursor: pointer; font-weight: 600;
}
button:hover { background: #1d4ed8; }
.section { padding: 20px 24px; }
.section h2 { font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0; border-bottom: 2px solid #2563eb; padding-bottom: 6px; display: inline-block; }
.plot-container { padding: 0 8px; }
.callout {
    background: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px;
    padding: 14px 20px; margin: 16px 0; font-size: 13px; color: #1e40af; line-height: 1.5;
}
.callout b { color: #1e3a8a; }
.callout.success { background: #f0fdf4; border-color: #86efac; color: #166534; }
.callout.success b { color: #14532d; }
.callout.warning { background: #fffbeb; border-color: #fcd34d; color: #92400e; }
.callout.warning b { color: #78350f; }
.metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin: 16px 0; }
.metric-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 16px; text-align: center;
}
.metric-card .value { font-size: 28px; font-weight: 800; color: #0f172a; }
.metric-card .label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 4px; }
.metric-card .delta { font-size: 13px; font-weight: 600; margin-top: 4px; }
.delta-good { color: #16a34a; }
.delta-bad { color: #dc2626; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
.data-table th { background: #f1f5f9; padding: 10px 12px; text-align: left; font-weight: 700; color: #475569; border-bottom: 2px solid #e2e8f0; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }
.data-table tr:hover { background: #f8fafc; }
.two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 900px) { .two-col { grid-template-columns: 1fr; } }
"""


# ── 1. PSF heatmaps: native, target, sequential, coupled ─────────

def _build_psf_heatmaps(comp: SynthesisComparison, dx_nm: float) -> go.Figure:
    """4-panel heatmap: native, target, sequential result, coupled result."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"Native Gaussian (FWHM={comp.native_fwhm_nm:.1f} nm)",
            f"Target ({comp.target_type.replace('_', ' ').title()})",
            f"Sequential (FWHM={comp.sequential.fwhm_nm:.1f} nm)",
            f"Coupled (FWHM={comp.coupled.fwhm_nm:.1f} nm)",
        ],
        horizontal_spacing=0.12,
        vertical_spacing=0.12,
    )

    panels = [
        (comp.native_psf, "Hot"),
        (comp.target_psf, "Viridis"),
        (comp.sequential.composite_psf, "Plasma"),
        (comp.coupled.composite_psf, "Plasma"),
    ]

    n = comp.native_psf.shape[0]
    half = n // 2
    crop = 20  # show central region only
    sl = slice(half - crop, half + crop)

    for idx, (data, colorscale) in enumerate(panels):
        row, col = divmod(idx, 2)
        cropped = data[sl, sl]
        fig.add_trace(go.Heatmap(
            z=cropped,
            colorscale=colorscale,
            showscale=idx == 0,
            hovertemplate="(%{x}, %{y})<br>Intensity: %{z:.6f}<extra></extra>",
        ), row=row + 1, col=col + 1)

    fig.update_layout(
        height=700, width=900,
        title_text="PSF Compositing: Incoherent Regime",
        margin=dict(t=60, b=40),
    )
    return fig


# ── 2. Cross-section profiles ────────────────────────────────────

def _build_profile_figure(comp: SynthesisComparison, dx_nm: float) -> go.Figure:
    """Line profiles through center of each PSF."""
    n = comp.native_psf.shape[0]
    center = n // 2
    half = 25
    sl = slice(center - half, center + half)
    x_nm = (np.arange(-half, half)) * dx_nm

    fig = go.Figure()

    profiles = [
        (comp.native_psf[center, sl], "Native Gaussian", "#6366f1", "solid"),
        (comp.target_psf[center, sl], "Target Shape", "#10b981", "dash"),
        (comp.sequential.composite_psf[center, sl], "Sequential Opt.", "#f59e0b", "solid"),
        (comp.coupled.composite_psf[center, sl], "Coupled Opt.", "#ef4444", "solid"),
    ]

    if comp.coherent_psf is not None:
        profiles.append(
            (comp.coherent_psf[center, sl], "Coherent Sharpened", "#8b5cf6", "dot")
        )

    for profile, name, color, dash in profiles:
        # Normalize to peak
        p = profile / profile.max() if profile.max() > 0 else profile
        fig.add_trace(go.Scatter(
            x=x_nm, y=p, mode="lines",
            name=name,
            line=dict(color=color, width=2.5, dash=dash),
            hovertemplate=f"{name}<br>x=%{{x:.1f}} nm<br>I=%{{y:.4f}}<extra></extra>",
        ))

    # Half-max line
    fig.add_hline(y=0.5, line_dash="dot", line_color="#94a3b8", line_width=1,
                  annotation_text="FWHM level", annotation_position="top right")

    fig.update_layout(
        title="Cross-Section Profiles (through PSF center)",
        xaxis_title="Position (nm)",
        yaxis_title="Normalized Intensity",
        height=450, width=900,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(t=50, b=60),
    )
    return fig


# ── 3. Coupled vs Sequential comparison bar chart ────────────────

def _build_comparison_figure(comp: SynthesisComparison) -> go.Figure:
    """Side-by-side bars comparing sequential vs coupled metrics."""
    fig = make_subplots(
        rows=1, cols=4,
        subplot_titles=[
            "Fidelity Error (×10⁶)",
            "Resist Damage",
            "Dose Containment %",
            "Uniformity RMS",
        ],
        horizontal_spacing=0.08,
    )

    methods = ["Sequential", "Coupled"]
    colors = ["#f59e0b", "#ef4444"]

    metrics = [
        (comp.sequential.fidelity_cost * 1e6, comp.coupled.fidelity_cost * 1e6),
        (comp.sequential.damage_cost, comp.coupled.damage_cost),
        (comp.sequential.dose_containment * 100, comp.coupled.dose_containment * 100),
        (comp.sequential.uniformity_rms, comp.coupled.uniformity_rms),
    ]

    for col, (seq_val, coup_val) in enumerate(metrics, 1):
        fig.add_trace(go.Bar(
            x=methods, y=[seq_val, coup_val],
            marker_color=colors,
            text=[f"{seq_val:.3f}", f"{coup_val:.3f}"],
            textposition="outside",
            showlegend=False,
        ), row=1, col=col)

    fig.update_layout(
        height=350, width=1100,
        title_text="Sequential vs. Coupled Optimization — Claim 4 Evidence",
        margin=dict(t=60, b=40),
    )
    return fig


# ── 4. Sub-exposure dither map ───────────────────────────────────

def _build_dither_figure(comp: SynthesisComparison) -> go.Figure:
    """Scatter plot of sub-exposure positions, sized by weight."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Sequential Sub-Exposures", "Coupled Sub-Exposures"],
        horizontal_spacing=0.12,
    )

    for col, (result, color) in enumerate([
        (comp.sequential, "#f59e0b"),
        (comp.coupled, "#ef4444"),
    ], 1):
        dx_vals = [s.dx_nm for s in result.sub_exposures]
        dy_vals = [s.dy_nm for s in result.sub_exposures]
        weights = [s.weight for s in result.sub_exposures]
        dwells = [s.dwell_ns for s in result.sub_exposures]

        max_w = max(weights) if weights else 1.0
        sizes = [max(6, w / max_w * 40) for w in weights]

        fig.add_trace(go.Scatter(
            x=dx_vals, y=dy_vals,
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=[d for d in dwells],
                colorscale="Viridis",
                showscale=(col == 2),
                colorbar=dict(title="Dwell (ns)", x=1.02) if col == 2 else None,
                line=dict(width=1, color="#333"),
            ),
            text=[f"{w:.2f}" for w in weights],
            textposition="top center",
            textfont=dict(size=9),
            hovertemplate=(
                "Δx=%{x:.1f} nm<br>Δy=%{y:.1f} nm<br>"
                "Weight: %{text}<br>Dwell: %{marker.color:.1f} ns<extra></extra>"
            ),
            showlegend=False,
        ), row=1, col=col)

        # Add crosshair at origin
        fig.add_hline(y=0, line_dash="dot", line_color="#ccc", row=1, col=col)
        fig.add_vline(x=0, line_dash="dot", line_color="#ccc", row=1, col=col)

    for col in [1, 2]:
        fig.update_xaxes(title_text="Δx (nm)", row=1, col=col)
        fig.update_yaxes(title_text="Δy (nm)", scaleanchor=f"x{col if col > 1 else ''}", row=1, col=col)

    fig.update_layout(
        height=450, width=900,
        title_text="Sub-Exposure Dither Positions (size=weight, color=dwell)",
        margin=dict(t=60, b=60),
    )
    return fig


# ── 5. Thermal relaxation curve ──────────────────────────────────

def _build_thermal_figure(comp: SynthesisComparison) -> go.Figure:
    """Thermal relaxation fraction vs inter-exposure interval."""
    thermal = comp.thermal

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=thermal.intervals_ns,
        y=thermal.relaxation_fractions * 100,
        mode="lines+markers",
        name="Thermal Relaxation",
        line=dict(color="#ef4444", width=2.5),
        marker=dict(size=8),
        hovertemplate="Δt=%{x:.1f} ns<br>Relaxation=%{y:.1f}%<extra></extra>",
    ))

    # Mark key thresholds
    fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8",
                  annotation_text="50% relaxation", annotation_position="top right")
    fig.add_hline(y=90, line_dash="dash", line_color="#94a3b8",
                  annotation_text="90% relaxation", annotation_position="top right")
    fig.add_hline(y=99, line_dash="dash", line_color="#94a3b8",
                  annotation_text="99% relaxation", annotation_position="top right")

    # Mark τ_thermal
    fig.add_vline(x=thermal.tau_thermal_ns, line_dash="dot", line_color="#6366f1",
                  annotation_text=f"τ={thermal.tau_thermal_ns:.2f} ns",
                  annotation_position="top left")

    fig.update_layout(
        title=f"Thermal Relaxation (d={thermal.resist_thickness_nm:.0f} nm resist, τ={thermal.tau_thermal_ns:.2f} ns)",
        xaxis_title="Inter-Sub-Exposure Interval (ns)",
        yaxis_title="Thermal Relaxation (%)",
        xaxis_type="log",
        height=400, width=800,
        margin=dict(t=50, b=60),
    )
    return fig


# ── 6. Coherent sharpening figure ────────────────────────────────

def _build_coherent_figure(comp: SynthesisComparison, dx_nm: float) -> go.Figure:
    """Show coherent PSF sharpening heatmap and profile."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"Coherent Composite (FWHM={comp.coherent_fwhm_nm:.1f} nm)",
            "Coherent vs Native Profile",
        ],
        horizontal_spacing=0.15,
        column_widths=[0.45, 0.55],
        specs=[[{"type": "heatmap"}, {"type": "xy"}]],
    )

    n = comp.native_psf.shape[0]
    center = n // 2
    crop = 20
    sl = slice(center - crop, center + crop)

    # Heatmap
    fig.add_trace(go.Heatmap(
        z=comp.coherent_psf[sl, sl] if comp.coherent_psf is not None else np.zeros((40, 40)),
        colorscale="Magma",
        showscale=True,
        colorbar=dict(title="Intensity", x=0.42, len=0.8),
        hovertemplate="(%{x}, %{y})<br>Intensity: %{z:.6f}<extra></extra>",
    ), row=1, col=1)

    # Profile comparison
    x_nm = (np.arange(-crop, crop)) * dx_nm
    native_p = comp.native_psf[center, sl]
    native_p = native_p / native_p.max()

    if comp.coherent_psf is not None:
        coh_p = comp.coherent_psf[center, sl]
        coh_p = coh_p / coh_p.max() if coh_p.max() > 0 else coh_p
    else:
        coh_p = np.zeros_like(native_p)

    fig.add_trace(go.Scatter(
        x=x_nm, y=native_p, mode="lines",
        name="Native", line=dict(color="#6366f1", width=2, dash="dash"),
    ), row=1, col=2)

    fig.add_trace(go.Scatter(
        x=x_nm, y=coh_p, mode="lines",
        name="Coherent", line=dict(color="#8b5cf6", width=2.5),
    ), row=1, col=2)

    fig.add_hline(y=0.5, line_dash="dot", line_color="#94a3b8", row=1, col=2)

    sharpening = 0.0
    if comp.native_fwhm_nm > 0 and comp.coherent_fwhm_nm > 0:
        sharpening = (1.0 - comp.coherent_fwhm_nm / comp.native_fwhm_nm) * 100

    fig.update_xaxes(title_text="Position (nm)", row=1, col=2)
    fig.update_yaxes(title_text="Normalized Intensity", row=1, col=2)

    fig.update_layout(
        height=400, width=900,
        title_text=f"Coherent PSF Sharpening — {sharpening:.0f}% FWHM reduction via destructive interference",
        margin=dict(t=60, b=60),
        legend=dict(x=0.65, y=0.95),
    )
    return fig


# ── Metrics cards HTML ────────────────────────────────────────────

def _metrics_html(comp: SynthesisComparison) -> str:
    """Build metric cards showing improvement from coupled optimization."""
    def _delta(val, good_if_positive=True):
        if abs(val) < 0.1:
            return f'<div class="delta" style="color:#64748b;">≈ 0%</div>'
        cls = "delta-good" if (val > 0) == good_if_positive else "delta-bad"
        sign = "+" if val > 0 else ""
        return f'<div class="delta {cls}">{sign}{val:.1f}%</div>'

    sharpening = 0.0
    if comp.native_fwhm_nm > 0 and comp.coherent_fwhm_nm > 0:
        sharpening = (1.0 - comp.coherent_fwhm_nm / comp.native_fwhm_nm) * 100

    return f"""<div class="metrics-grid">
        <div class="metric-card">
            <div class="value">{comp.native_fwhm_nm:.1f} nm</div>
            <div class="label">Native PSF FWHM</div>
        </div>
        <div class="metric-card">
            <div class="value">{comp.coupled.fwhm_nm:.1f} nm</div>
            <div class="label">Coupled Composite FWHM</div>
        </div>
        <div class="metric-card">
            <div class="value">{comp.coherent_fwhm_nm:.1f} nm</div>
            <div class="label">Coherent FWHM</div>
            {_delta(sharpening, True)}
        </div>
        <div class="metric-card">
            <div class="value">{comp.fidelity_improvement_pct:.1f}%</div>
            <div class="label">Fidelity Improvement</div>
            {_delta(comp.fidelity_improvement_pct, True)}
        </div>
        <div class="metric-card">
            <div class="value">{comp.damage_reduction_pct:.1f}%</div>
            <div class="label">Damage Reduction</div>
            {_delta(comp.damage_reduction_pct, True)}
        </div>
        <div class="metric-card">
            <div class="value">{comp.coupled.dose_containment * 100:.1f}%</div>
            <div class="label">Dose Containment (Coupled)</div>
            {_delta(comp.containment_improvement_pct, True)}
        </div>
        <div class="metric-card">
            <div class="value">{len(comp.coupled.sub_exposures)}</div>
            <div class="label">Active Sub-Exposures</div>
        </div>
        <div class="metric-card">
            <div class="value">{comp.thermal.tau_thermal_ns:.2f} ns</div>
            <div class="label">Thermal τ ({comp.thermal.resist_thickness_nm:.0f} nm resist)</div>
        </div>
    </div>"""


# ── Sub-exposure table ────────────────────────────────────────────

def _sub_exposure_table(comp: SynthesisComparison) -> str:
    """Table comparing sub-exposure parameters: sequential vs coupled."""
    rows = ""
    max_n = max(len(comp.sequential.sub_exposures), len(comp.coupled.sub_exposures))

    for i in range(max_n):
        seq = comp.sequential.sub_exposures[i] if i < len(comp.sequential.sub_exposures) else None
        coup = comp.coupled.sub_exposures[i] if i < len(comp.coupled.sub_exposures) else None

        seq_cells = (
            f"<td>{seq.dx_nm:.1f}, {seq.dy_nm:.1f}</td>"
            f"<td>{seq.weight:.3f}</td>"
            f"<td>{seq.dwell_ns:.1f}</td>"
        ) if seq else "<td>—</td><td>—</td><td>—</td>"

        coup_cells = (
            f"<td>{coup.dx_nm:.1f}, {coup.dy_nm:.1f}</td>"
            f"<td>{coup.weight:.3f}</td>"
            f"<td>{coup.dwell_ns:.1f}</td>"
        ) if coup else "<td>—</td><td>—</td><td>—</td>"

        rows += f"<tr><td>{i + 1}</td>{seq_cells}{coup_cells}</tr>"

    return f"""<table class="data-table">
        <thead><tr>
            <th>#</th>
            <th colspan="3" style="text-align:center; background:#fef3c7;">Sequential</th>
            <th colspan="3" style="text-align:center; background:#fee2e2;">Coupled</th>
        </tr>
        <tr>
            <th></th>
            <th>Offset (nm)</th><th>Weight</th><th>Dwell (ns)</th>
            <th>Offset (nm)</th><th>Weight</th><th>Dwell (ns)</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


# ── Master HTML builder ──────────────────────────────────────────

def build_psf_synthesis_html(
    sigma_nm: float = 10.0,
    target_type: str = "flat_top",
    target_radius_nm: float = 15.0,
    n_sub: int = 9,
    dx_nm: float = 1.0,
    grid_size: int = 128,
    resist_thickness_nm: float = 20.0,
) -> str:
    """Build the full PSF synthesis dashboard HTML."""
    # Run the comparison
    comp = run_psf_synthesis_comparison(
        sigma_nm=sigma_nm,
        target_type=target_type,
        target_radius_nm=target_radius_nm,
        n_sub=n_sub,
        dx_nm=dx_nm,
        grid_size=grid_size,
        resist_thickness_nm=resist_thickness_nm,
    )

    # Build all figures
    heatmap_fig = _build_psf_heatmaps(comp, dx_nm)
    heatmap_html = heatmap_fig.to_html(full_html=False, include_plotlyjs=False)

    profile_fig = _build_profile_figure(comp, dx_nm)
    profile_html = profile_fig.to_html(full_html=False, include_plotlyjs=False)

    comparison_fig = _build_comparison_figure(comp)
    comparison_html = comparison_fig.to_html(full_html=False, include_plotlyjs=False)

    dither_fig = _build_dither_figure(comp)
    dither_html = dither_fig.to_html(full_html=False, include_plotlyjs=False)

    thermal_fig = _build_thermal_figure(comp)
    thermal_html = thermal_fig.to_html(full_html=False, include_plotlyjs=False)

    coherent_fig = _build_coherent_figure(comp, dx_nm)
    coherent_html = coherent_fig.to_html(full_html=False, include_plotlyjs=False)

    metrics = _metrics_html(comp)
    sub_table = _sub_exposure_table(comp)

    sharpening = 0.0
    if comp.native_fwhm_nm > 0 and comp.coherent_fwhm_nm > 0:
        sharpening = (1.0 - comp.coherent_fwhm_nm / comp.native_fwhm_nm) * 100

    def _sel(val, opt):
        return "selected" if str(val) == str(opt) else ""

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>PSF Synthesis — Spatiotemporal Compositing</title>
    <script src="plotly.min.js"></script>
    <style>{_CSS}</style>
</head>
<body>
    {_NAV}

    <form class="controls" method="get" action="/api/psf-synthesis">
        <div class="control-group">
            <label>Native σ (nm)</label>
            <input type="number" name="sigma_nm" value="{sigma_nm}" min="2" max="50" step="1">
        </div>
        <div class="control-group">
            <label>Target Shape</label>
            <select name="target_type">
                <option value="flat_top" {_sel(target_type, 'flat_top')}>Flat-Top</option>
                <option value="annular" {_sel(target_type, 'annular')}>Annular</option>
            </select>
        </div>
        <div class="control-group">
            <label>Target Radius (nm)</label>
            <input type="number" name="target_radius_nm" value="{target_radius_nm}" min="5" max="100" step="1">
        </div>
        <div class="control-group">
            <label>Sub-Exposures</label>
            <input type="number" name="n_sub" value="{n_sub}" min="3" max="25" step="1">
        </div>
        <div class="control-group">
            <label>Resist (nm)</label>
            <input type="number" name="resist_thickness_nm" value="{resist_thickness_nm}" min="5" max="100" step="1">
        </div>
        <div class="control-group">
            <label>Grid Res (nm/px)</label>
            <input type="number" name="dx_nm" value="{dx_nm}" min="0.5" max="5" step="0.5">
        </div>
        <button type="submit">Synthesize</button>
    </form>

    <div class="section">
        <h2>PSF Synthesis Overview</h2>
        <div class="callout">
            <b>Invention Core:</b> Build an arbitrary effective PSF from rapidly dithered sub-exposures:
            PSF<sub>eff</sub>(x,y) = &Sigma; w<sub>i</sub> &middot; PSF<sub>native</sub>(x&minus;&Delta;x<sub>i</sub>, y&minus;&Delta;y<sub>i</sub>).
            The coupled optimizer jointly tunes spatial offsets (&Delta;x, &Delta;y, w) and temporal
            intervals (&Delta;t, dwell) in a single cost function with pattern-fidelity, resist-damage,
            and dose-rate reciprocity cross-terms[cite: 21]. This synergistic coupling is the key novelty (Claim 4).
            Spatial decomposition uses NNLS[cite: 50]; coherent case uses Gerchberg-Saxton phase retrieval[cite: 51].
        </div>
        {metrics}
    </div>

    <div class="section">
        <h2>Incoherent PSF Compositing</h2>
        <div class="callout warning">
            <b>Physics constraint:</b> In the incoherent regime (intensities add)[cite: 25], the composite PSF
            is always broader than or equal to the native PSF &mdash; you <em>cannot</em> sharpen below
            the native resolution. The value is in <em>reshaping</em>: creating flat-top, annular, or
            asymmetric dose profiles with superior dose containment and uniformity within the target region.
            This is structurally distinct from prior overlapping-exposure methods[cite: 1][cite: 2].
        </div>
        <div class="plot-container">{heatmap_html}</div>
    </div>

    <div class="section">
        <h2>Cross-Section Profiles</h2>
        <div class="plot-container">{profile_html}</div>
    </div>

    <div class="section">
        <h2>Coupled vs. Sequential Optimization &mdash; Claim 4 Evidence</h2>
        <div class="callout success">
            <b>Key finding:</b> Coupled (joint) optimization of spatial offsets and temporal intervals
            achieves <b>{comp.fidelity_improvement_pct:.1f}% better fidelity</b> and
            <b>{comp.damage_reduction_pct:.1f}% lower resist damage</b> than sequential (independent) optimization.
            The cross-coupling term L<sub>reciprocity</sub> penalizes spatial configurations that demand
            temporally aggressive scheduling, creating synergistic benefit impossible with independent tuning.
        </div>
        <div class="plot-container">{comparison_html}</div>
    </div>

    <div class="section">
        <h2>Sub-Exposure Dither Positions</h2>
        <div class="plot-container">{dither_html}</div>
    </div>

    <div class="section">
        <h2>Sub-Exposure Parameters</h2>
        {sub_table}
    </div>

    <div class="section">
        <h2>Thermal Relaxation Model</h2>
        <div class="callout">
            <b>Resist fragility:</b> For {resist_thickness_nm:.0f} nm resist,
            &tau;<sub>thermal</sub> = d&sup2;/(4&alpha;) = {comp.thermal.tau_thermal_ns:.2f} ns.
            Inter-sub-exposure intervals of 10&ndash;100 ns provide 50&ndash;99%+ thermal relaxation,
            preventing pattern collapse[cite: 52] and dose-rate reciprocity failure[cite: 21] in thin films.
        </div>
        <div class="plot-container">{thermal_html}</div>
    </div>

    <div class="section">
        <h2>Coherent PSF Sharpening</h2>
        <div class="callout">
            <b>Coherent regime:</b> With phase-controlled illumination (FEG e-beam or laser)[cite: 25][cite: 27],
            destructive interference at the wings can sharpen the effective PSF below the native FWHM &mdash;
            analogous to synthetic aperture techniques[cite: 23].
            Achieved <b>{sharpening:.0f}% FWHM reduction</b> ({comp.native_fwhm_nm:.1f} &rarr; {comp.coherent_fwhm_nm:.1f} nm)
            using anti-phase satellite beamlets. Requires Claim 7 phase modulation capability.
        </div>
        <div class="plot-container">{coherent_html}</div>
    </div>

    <div style="text-align: center; padding: 32px; font-size: 12px; color: #94a3b8;">
        Laser-HHG-EUV Lab &middot; PSF Synthesis Patent Demo &middot; buildzmarter-ai
    </div>
</body>
</html>"""
