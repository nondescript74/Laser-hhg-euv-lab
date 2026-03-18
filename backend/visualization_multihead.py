"""Visualization for multi-head writer array, architecture comparison,
tile exposure calculator, and dose calibration."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
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


def _hex_to_rgba(hex_color, alpha=1.0):
    """Convert #RRGGBB to rgba() string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# ── Shared nav + style ──────────────────────────────────────────────

_NAV = """
<div class="nav">
    <a href="/api/visualize">2D Process Sim</a>
    <a href="/api/visualize-3d">3D Pipeline</a>
    <a href="/api/fleet-dashboard">Platform Economics</a>
    <a href="/api/multihead" class="active">Multi-Head Array</a>
    <a href="/api/psf-synthesis">PSF Synthesis</a>
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
.control-group select { width: 110px; }
button {
    padding: 7px 18px; background: #2563eb; color: #fff; border: none;
    border-radius: 4px; font-size: 13px; cursor: pointer; font-weight: 600;
}
button:hover { background: #1d4ed8; }
.section { padding: 20px 24px; }
.section h2 { font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0; border-bottom: 2px solid #2563eb; padding-bottom: 6px; display: inline-block; }
.plot-container { padding: 0 8px; }
.tab-bar { display: flex; gap: 0; border-bottom: 2px solid #e2e8f0; padding: 0 24px; background: #fff; }
.tab-bar a {
    padding: 10px 20px; font-size: 14px; font-weight: 600; color: #64748b;
    text-decoration: none; border-bottom: 3px solid transparent; margin-bottom: -2px;
}
.tab-bar a:hover { color: #1e293b; }
.tab-bar a.active { color: #2563eb; border-bottom-color: #2563eb; }
.arch-cards { display: flex; gap: 16px; flex-wrap: wrap; margin: 16px 0; }
.arch-card {
    flex: 1; min-width: 260px; background: #fff; border: 2px solid #e2e8f0;
    border-radius: 10px; padding: 20px; transition: transform 0.15s, box-shadow 0.15s;
}
.arch-card:hover { transform: translateY(-3px); box-shadow: 0 4px 20px rgba(0,0,0,0.08); }
.arch-card.selected { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.15); }
.arch-card h3 { margin: 0 0 6px 0; font-size: 15px; }
.arch-card p { font-size: 12px; color: #64748b; margin: 0 0 10px 0; line-height: 1.4; }
.arch-specs { font-size: 12px; color: #475569; }
.arch-specs span { display: inline-block; background: #f1f5f9; padding: 2px 8px; border-radius: 10px; margin: 2px 4px 2px 0; }
.trl-badge { display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: 700; }
.data-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
.data-table th { background: #f1f5f9; padding: 10px 12px; text-align: left; font-weight: 700; color: #475569; border-bottom: 2px solid #e2e8f0; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }
.data-table tr:hover { background: #f8fafc; }
.callout {
    background: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px;
    padding: 14px 20px; margin: 16px 0; font-size: 13px; color: #1e40af; line-height: 1.5;
}
.callout b { color: #1e3a8a; }
"""


def _trl_color(trl):
    if trl >= 5:
        return "#16a34a", "#dcfce7"
    if trl >= 3:
        return "#ca8a04", "#fef9c3"
    return "#dc2626", "#fee2e2"


# ── 1. Multi-head array top-down view ────────────────────────────────

def _build_array_figure(array):
    """Build top-down view of writer head tiles on wafer."""
    arch = ARCHITECTURES[array.arch_key]
    fig = go.Figure()

    # Draw wafer outline (300mm = 300,000 µm, but we show just the tiled region)
    region_x = array.wafer_region_x_um
    region_y = array.wafer_region_y_um

    # Draw each tile
    for head in array.heads:
        half = head.tile_size_um / 2
        x0 = head.tile_x_um - half
        y0 = head.tile_y_um - half
        x1 = head.tile_x_um + half
        y1 = head.tile_y_um + half

        # Tile fill
        fig.add_trace(go.Scatter(
            x=[x0, x1, x1, x0, x0],
            y=[y0, y0, y1, y1, y0],
            fill="toself",
            fillcolor=_hex_to_rgba(arch["color"], 0.13),
            line=dict(color=arch["color"], width=2),
            name=f"Head {head.head_id}",
            hovertext=(
                f"<b>Head {head.head_id}</b> (row {head.row}, col {head.col})<br>"
                f"Tile: {head.tile_size_um}\u00d7{head.tile_size_um} \u00b5m<br>"
                f"Emitters: {head.n_emitters} ({int(head.n_emitters**0.5)}\u00d7{int(head.n_emitters**0.5)})<br>"
                f"Power: {head.power_mw:.1f} mW"
            ),
            hoverinfo="text",
            showlegend=False,
        ))

        # Head ID label
        fig.add_trace(go.Scatter(
            x=[head.tile_x_um], y=[head.tile_y_um],
            mode="text",
            text=[f"H{head.head_id}"],
            textfont=dict(size=10, color=arch["color"]),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Draw overlap zones
    overlap = array.overlap_um
    if overlap > 0:
        for head in array.heads:
            half = head.tile_size_um / 2
            # Right overlap
            if head.col < array.n_cols - 1:
                ox0 = head.tile_x_um + half - overlap
                ox1 = head.tile_x_um + half
                oy0 = head.tile_y_um - half
                oy1 = head.tile_y_um + half
                fig.add_trace(go.Scatter(
                    x=[ox0, ox1, ox1, ox0, ox0],
                    y=[oy0, oy0, oy1, oy1, oy0],
                    fill="toself",
                    fillcolor="rgba(255,200,0,0.25)",
                    line=dict(color="rgba(255,180,0,0.5)", width=1),
                    hovertext=f"Stitch zone ({overlap:.0f} \u00b5m overlap)",
                    hoverinfo="text",
                    showlegend=False,
                ))
            # Bottom overlap
            if head.row < array.n_rows - 1:
                ox0 = head.tile_x_um - half
                ox1 = head.tile_x_um + half
                oy0 = head.tile_y_um + half - overlap
                oy1 = head.tile_y_um + half
                fig.add_trace(go.Scatter(
                    x=[ox0, ox1, ox1, ox0, ox0],
                    y=[oy0, oy0, oy1, oy1, oy0],
                    fill="toself",
                    fillcolor="rgba(255,200,0,0.25)",
                    line=dict(color="rgba(255,180,0,0.5)", width=1),
                    hovertext=f"Stitch zone ({overlap:.0f} \u00b5m overlap)",
                    hoverinfo="text",
                    showlegend=False,
                ))

    fig.update_layout(
        title=f"Multi-Head Writer Array \u2014 {arch['name']}",
        xaxis=dict(title="Wafer X (\u00b5m)", scaleanchor="y", scaleratio=1,
                   range=[-20, region_x + 20]),
        yaxis=dict(title="Wafer Y (\u00b5m)",
                   range=[-20, region_y + 20]),
        height=600, width=700,
        plot_bgcolor="#fafafa",
        margin=dict(l=60, r=20, t=50, b=60),
    )
    return fig


# ── 2. Architecture comparison ──────────────────────────────────────

def _build_arch_comparison_figure():
    """Bar charts comparing the three architectures."""
    keys = ["A", "B", "C"]
    names = [ARCHITECTURES[k]["short"] for k in keys]
    colors = [ARCHITECTURES[k]["color"] for k in keys]

    fig = make_subplots(
        rows=1, cols=4,
        subplot_titles=["Wavelength (nm)", "Resolution (nm)", "Tile Size (\u00b5m)", "TRL"],
        horizontal_spacing=0.08,
    )

    metrics = [
        ("wavelength_nm", "Wavelength"),
        ("resolution_nm", "Resolution"),
        ("tile_um", "Tile Size"),
        ("trl", "TRL"),
    ]

    for col, (metric, label) in enumerate(metrics, 1):
        vals = [ARCHITECTURES[k][metric] for k in keys]
        fig.add_trace(go.Bar(
            x=names, y=vals,
            marker_color=colors,
            text=[f"{v}" for v in vals],
            textposition="outside",
            hovertemplate=f"{label}: %{{y}}<extra></extra>",
            showlegend=False,
        ), row=1, col=col)

    # Log scale for wavelength
    fig.update_yaxes(type="log", row=1, col=1)
    fig.update_yaxes(type="log", row=1, col=2)

    fig.update_layout(
        height=350, width=1100,
        title_text="Architecture Comparison: A (NIR) vs B (DUV) vs C (EUV)",
        margin=dict(t=60, b=40),
    )
    return fig


# ── 3. Tile exposure calculator ─────────────────────────────────────

def _build_exposure_table_html(exposures):
    """Build HTML table for per-architecture tile exposure data."""
    rows = ""
    for e in exposures:
        color = ARCHITECTURES[e["arch_key"]]["color"]
        rows += f"""<tr>
            <td style="color:{color}; font-weight:700;">{e['arch_name']}</td>
            <td>{e['tile_um']}\u00d7{e['tile_um']} \u00b5m</td>
            <td>{e['energy_per_tile_mj']:.4e} mJ</td>
            <td>{e['power_per_head_mw']:.3f} mW</td>
            <td>{e['time_per_tile_ms']:.2f} ms</td>
            <td>{e['tiles_per_wafer']:,}</td>
            <td>{e['n_heads']}</td>
            <td>{e['total_time_s']:.1f} s</td>
            <td>{e['wph']:.2f}</td>
        </tr>"""

    return f"""<table class="data-table">
        <thead><tr>
            <th>Architecture</th>
            <th>Tile Size</th>
            <th>Energy / Tile</th>
            <th>Power / Head</th>
            <th>Time / Tile</th>
            <th>Tiles / Wafer</th>
            <th>Heads</th>
            <th>Total Time</th>
            <th>Wafers / Hr</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def _build_exposure_figure(exposures):
    """Bar chart of exposure time and throughput per architecture."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Time per Tile (ms)", "Wafer Throughput (wph)"],
        horizontal_spacing=0.14,
    )

    names = [e["arch_name"].split(" \u2014 ")[1] for e in exposures]
    colors = [ARCHITECTURES[e["arch_key"]]["color"] for e in exposures]

    fig.add_trace(go.Bar(
        x=names,
        y=[e["time_per_tile_ms"] for e in exposures],
        marker_color=colors,
        text=[f"{e['time_per_tile_ms']:.2f}" for e in exposures],
        textposition="outside",
        showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=names,
        y=[e["wph"] for e in exposures],
        marker_color=colors,
        text=[f"{e['wph']:.2f}" for e in exposures],
        textposition="outside",
        showlegend=False,
    ), row=1, col=2)

    fig.update_yaxes(type="log", title_text="ms (log)", row=1, col=1)
    fig.update_yaxes(title_text="wph", row=1, col=2)

    fig.update_layout(
        height=350, width=900,
        margin=dict(t=50, b=40),
    )
    return fig


# ── 4. Dose calibration visualization ───────────────────────────────

def _build_calibration_figure(cal):
    """Build 2x2 heatmap showing raw→corrected dose uniformity."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            f"Raw Emitter Intensity (\u03c3={cal['raw_uniformity_pct']:.1f}%)",
            "Static Calibration Correction",
            "After Drift (thermal \u00b13%)",
            f"Final Dose (corrected, \u03c3={cal['corrected_uniformity_pct']:.2e}%)",
        ],
        horizontal_spacing=0.18,
        vertical_spacing=0.16,
    )

    panels = [
        (cal["raw_intensity"], "RdYlGn_r", "Intensity"),
        (cal["static_correction"], "Blues", "Correction Factor"),
        (cal["after_drift"], "RdYlGn_r", "Intensity"),
        (cal["final_dose"], "Greens", "Dose"),
    ]

    for idx, (data, colorscale, cbar_title) in enumerate(panels):
        row, col = divmod(idx, 2)
        fig.add_trace(go.Heatmap(
            z=data,
            colorscale=colorscale,
            colorbar=dict(
                title=dict(text=cbar_title, side="right"),
                len=0.35,
                y=0.82 - row * 0.58,
                x=0.44 + col * 0.56,
                thickness=12,
            ),
            hovertemplate="Emitter (%{x}, %{y})<br>Value: %{z:.4f}<extra></extra>",
        ), row=row + 1, col=col + 1)

    for i in range(1, 5):
        r, c = divmod(i - 1, 2)
        fig.update_xaxes(title_text="Emitter Column", row=r + 1, col=c + 1)
        fig.update_yaxes(title_text="Emitter Row", row=r + 1, col=c + 1)

    fig.update_layout(
        height=800, width=1000,
        title_text="Per-Site Dose Calibration: Raw \u2192 Static Correction \u2192 Drift \u2192 Final",
        margin=dict(t=60, b=40),
    )
    return fig


# ── 5. Lab 91 Use Case ──────────────────────────────────────────────

def _build_shot_noise_figure():
    """Bar chart comparing EUV vs 405nm shot noise at 2nm voxel."""
    snc = SHOT_NOISE_COMPARISON

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Photons per 2×2 nm² Voxel", "Shot Noise (%)"],
        horizontal_spacing=0.15,
    )

    labels = ["EUV (13.5 nm)", "VCSEL (405 nm)"]
    colors = ["#6a0dad", "#e63946"]
    photons = [snc["euv"]["photons_per_voxel"], snc["vcsel_405"]["photons_per_voxel"]]
    noise = [snc["euv"]["shot_noise_pct"], snc["vcsel_405"]["shot_noise_pct"]]

    fig.add_trace(go.Bar(
        x=labels, y=photons, marker_color=colors,
        text=[str(p) for p in photons], textposition="outside",
        showlegend=False,
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=labels, y=noise, marker_color=colors,
        text=[f"{n}%" for n in noise], textposition="outside",
        showlegend=False,
    ), row=1, col=2)

    fig.update_yaxes(title_text="Photons", row=1, col=1)
    fig.update_yaxes(title_text="Shot Noise %", row=1, col=2)

    fig.update_layout(
        height=350, width=800,
        margin=dict(t=50, b=40),
    )
    return fig


def _build_lab91_throughput_figure():
    """Throughput sensitivity: emitter count vs wafer time for Lab 91."""
    emitter_counts = [1000, 2000, 4000, 8000, 12000, 16000, 24000]
    times = []
    wphs = []
    for n in emitter_counts:
        result = compute_lab91_throughput(n_emitters=n)
        times.append(result["total_time_s"])
        wphs.append(result["wph"])

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Wafer Time vs Emitter Count", "Throughput (wph) vs Emitter Count"],
        horizontal_spacing=0.15,
    )

    fig.add_trace(go.Scatter(
        x=emitter_counts, y=times,
        mode="lines+markers",
        line=dict(color="#e63946", width=3),
        marker=dict(size=8),
        name="Wafer Time",
        hovertemplate="Emitters: %{x:,}<br>Time: %{y:.1f} s<extra></extra>",
    ), row=1, col=1)

    # Add 60 wph reference line
    fig.add_hline(y=60, line_dash="dash", line_color="#64748b",
                  annotation_text="60 s target", row=1, col=1)

    fig.add_trace(go.Scatter(
        x=emitter_counts, y=wphs,
        mode="lines+markers",
        line=dict(color="#2a9d8f", width=3),
        marker=dict(size=8),
        name="Throughput",
        hovertemplate="Emitters: %{x:,}<br>WPH: %{y:.1f}<extra></extra>",
    ), row=1, col=2)

    # Add 60 wph reference line
    fig.add_hline(y=60, line_dash="dash", line_color="#64748b",
                  annotation_text="60 wph target", row=1, col=2)

    fig.update_xaxes(title_text="Emitter Count", row=1, col=1)
    fig.update_xaxes(title_text="Emitter Count", row=1, col=2)
    fig.update_yaxes(title_text="Seconds per Wafer", row=1, col=1)
    fig.update_yaxes(title_text="Wafers per Hour", row=1, col=2)

    fig.update_layout(
        height=400, width=1000,
        margin=dict(t=50, b=40),
        showlegend=False,
    )
    return fig


def _build_lab91_modifications_html():
    """Build HTML cards for the 5 Lab 91 process modifications."""
    cards = ""
    for mod in LAB91_MODIFICATIONS:
        numbers_html = "".join(
            f'<li style="margin:3px 0;">{n}</li>' for n in mod["key_numbers"]
        )
        cards += f"""
        <div style="background:#fff; border:2px solid {mod['color']}22; border-left:4px solid {mod['color']};
                    border-radius:10px; padding:20px; margin-bottom:14px;
                    transition: transform 0.15s, box-shadow 0.15s;"
             onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 16px rgba(0,0,0,0.08)';"
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none';">
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:10px;">
                <span style="font-size:24px;">{mod['icon']}</span>
                <h3 style="margin:0; font-size:15px; color:#0f172a;">{mod['title']}</h3>
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:10px;">
                <div>
                    <div style="font-size:10px; font-weight:700; color:#dc2626; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">Current (EBL)</div>
                    <div style="font-size:12px; color:#64748b; line-height:1.4;">{mod['current']}</div>
                </div>
                <div>
                    <div style="font-size:10px; font-weight:700; color:#16a34a; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:4px;">VCSEL Multiwriter</div>
                    <div style="font-size:12px; color:#64748b; line-height:1.4;">{mod['proposed']}</div>
                </div>
            </div>
            <ul style="font-size:12px; color:#475569; margin:0; padding-left:18px; line-height:1.5;">
                {numbers_html}
            </ul>
        </div>"""
    return cards


def _build_lab91_section_html():
    """Build the full Lab 91 use case section."""
    throughput = compute_lab91_throughput()

    # Shot noise chart
    shot_fig = _build_shot_noise_figure()
    shot_html = shot_fig.to_html(full_html=False, include_plotlyjs=False)

    # Throughput chart
    tp_fig = _build_lab91_throughput_figure()
    tp_html = tp_fig.to_html(full_html=False, include_plotlyjs=False)

    # Modification cards
    mods_html = _build_lab91_modifications_html()

    proc = LAB91_PROCESS

    return f"""
    <div style="background:linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%); color:#fff; padding:32px 40px; margin-top:24px;">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
            <span style="font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px;
                         background:#1e5f3a; color:#5be6a3; letter-spacing:0.5px;">USE CASE</span>
            <span style="font-size:11px; font-weight:700; padding:3px 10px; border-radius:20px;
                         background:#5f4b1e; color:#e6c45b; letter-spacing:0.5px;">2D MATERIALS</span>
        </div>
        <h2 style="margin:0 0 6px 0; font-size:26px; font-weight:800;">Lab 91 — MoS\u2082 RF Switch Fabrication</h2>
        <p style="margin:0; font-size:15px; color:#94a3b8; max-width:800px; line-height:1.6;">
            {proc['mission']}. Beachhead market: <b style="color:#fff;">{proc['beachhead']}</b>,
            scaling to {proc['future']}. Current process uses {proc['current_process']['patterning']}
            with {proc['current_process']['growth']} — core challenge:
            <b style="color:#fbbf24;">{proc['current_process']['challenge']}</b>.
        </p>
    </div>

    <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:0 0 8px 8px;
                padding:16px 24px; margin:0 0 4px 0;">
        <div style="display:flex; gap:32px; flex-wrap:wrap;">
            <div style="text-align:center; min-width:140px;">
                <div style="font-size:28px; font-weight:800; color:#16a34a;">{throughput['wph']:.0f}</div>
                <div style="font-size:11px; color:#64748b; text-transform:uppercase;">Wafers/Hour</div>
            </div>
            <div style="text-align:center; min-width:140px;">
                <div style="font-size:28px; font-weight:800; color:#16a34a;">{throughput['total_time_s']:.0f}s</div>
                <div style="font-size:11px; color:#64748b; text-transform:uppercase;">Per 300mm Wafer</div>
            </div>
            <div style="text-align:center; min-width:140px;">
                <div style="font-size:28px; font-weight:800; color:#16a34a;">{throughput['n_emitters']:,}</div>
                <div style="font-size:11px; color:#64748b; text-transform:uppercase;">Parallel Emitters</div>
            </div>
            <div style="text-align:center; min-width:140px;">
                <div style="font-size:28px; font-weight:800; color:#16a34a;">{throughput['pixel_dwell_ps']:.0f} ps</div>
                <div style="font-size:11px; color:#64748b; text-transform:uppercase;">Pixel Dwell Time</div>
            </div>
            <div style="text-align:center; min-width:140px;">
                <div style="font-size:28px; font-weight:800; color:#16a34a;">{throughput['practical_cd_nm']:.0f} nm</div>
                <div style="font-size:11px; color:#64748b; text-transform:uppercase;">CD at NA={throughput['na']}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Five Process Modifications for Lab 91</h2>
        <p style="font-size:13px; color:#64748b; margin:0 0 14px 0; line-height:1.5;">
            Each modification replaces a step in Lab 91's current EBL-based MoS\u2082 RF switch
            fabrication with a VCSEL multiwriter equivalent, addressing the core yield problem:
            polymer residue and electron damage at the MoS\u2082 contact interface.
        </p>
        {mods_html}
    </div>

    <div class="section">
        <h2>Shot Noise Advantage: 405 nm vs EUV</h2>
        <div class="callout">
            <b>At a 2\u00d72 nm\u00b2 voxel:</b> EUV at 60 mJ/cm\u00b2 delivers only 163 photons (8% shot noise).
            The VCSEL at 405 nm and 20 mJ/cm\u00b2 delivers 1,630 photons (2.5% shot noise) — a
            <b>10\u00d7 photon count</b> and <b>3\u00d7 noise reduction</b> per pixel.
            This directly improves contact edge roughness and atomristor switching reproducibility.
        </div>
        <div class="plot-container">{shot_html}</div>
    </div>

    <div class="section">
        <h2>Lab 91 Throughput: Emitter Scaling</h2>
        <div class="callout">
            <b>Target:</b> 60+ wafers per hour on 300 mm wafers.
            At {throughput['n_emitters']:,} emitters running at {throughput['pixel_clock_ghz']:.0f} GHz each,
            total pixel rate is {throughput['pixel_rate_label']} px/s.
            A full 300 mm wafer completes in <b>{throughput['total_time_s']:.0f} seconds</b>
            ({throughput['wph']:.0f} wph) including 20% stepping overhead.
        </div>
        <div class="plot-container">{tp_html}</div>
    </div>

    <div class="section">
        <div class="callout" style="background:#fef3c7; border-color:#f59e0b; color:#92400e;">
            <b>Transfer Integration:</b> The VCSEL write head mounts in-situ in Lab 91's transfer tool.
            MoS\u2082 monolayer placement \u2192 immediate resist exposure \u2192 no vacuum break,
            no atmospheric contamination, no resist spin, no EBL chamber.
            Per-zone VCSEL dose feedback compensates for MoS\u2082 thickness variation across
            grain boundaries in real time.
        </div>
    </div>
    """


# ── Architecture cards HTML ──────────────────────────────────────────

def _arch_cards_html(selected_key):
    """Render architecture selection cards."""
    cards = ""
    for key, arch in ARCHITECTURES.items():
        sel = "selected" if key == selected_key else ""
        tc, bg = _trl_color(arch["trl"])
        cards += f"""<a href="/api/multihead?arch={key}" class="arch-card {sel}" style="border-color: {arch['color'] if sel else '#e2e8f0'}; text-decoration: none; color: inherit;">
            <h3 style="color:{arch['color']}">{arch['name']}</h3>
            <p>{arch['description']}</p>
            <div class="arch-specs">
                <span>{arch['wavelength_label']}</span>
                <span>Res: {arch['resolution_nm']} nm</span>
                <span>Tile: {arch['tile_um']} \u00b5m</span>
                <span>NA: {arch['na']}</span>
                <span>{arch['emitter_type']}</span>
                <span class="trl-badge" style="color:{tc}; background:{bg}">TRL {arch['trl']}</span>
            </div>
        </a>"""
    return f'<div class="arch-cards">{cards}</div>'


# ── Master HTML builder ──────────────────────────────────────────────

def build_multihead_html(
    arch_key: str = "A",
    n_rows: int = 4,
    n_cols: int = 4,
    overlap_pct: float = 5.0,
    emitters_per_side: int = 16,
    source_power_mw: float = 10.0,
    dose_mj_cm2: float = 15.0,
):
    """Build the full multi-head writer array dashboard."""
    # Build array
    array = build_multihead_array(arch_key, n_rows, n_cols, overlap_pct, emitters_per_side)

    # Array figure
    array_fig = _build_array_figure(array)
    array_html = array_fig.to_html(full_html=False, include_plotlyjs="cdn")

    # Architecture comparison
    arch_fig = _build_arch_comparison_figure()
    arch_html = arch_fig.to_html(full_html=False, include_plotlyjs=False)

    # Tile exposure for all architectures
    n_heads = n_rows * n_cols
    exposures = [
        compute_tile_exposure(k, source_power_mw, dose_mj_cm2, n_heads)
        for k in ["A", "B", "C"]
    ]
    exposure_table = _build_exposure_table_html(exposures)
    exposure_fig = _build_exposure_figure(exposures)
    exposure_chart_html = exposure_fig.to_html(full_html=False, include_plotlyjs=False)

    # Dose calibration
    cal = simulate_dose_calibration(emitters_per_side)
    cal_fig = _build_calibration_figure(cal)
    cal_html = cal_fig.to_html(full_html=False, include_plotlyjs=False)

    # Architecture cards
    cards = _arch_cards_html(arch_key)

    arch = ARCHITECTURES[arch_key]

    def _sel(val, opt):
        return "selected" if str(val) == str(opt) else ""

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Multi-Head Writer Array</title>
    <style>{_CSS}</style>
</head>
<body>
    {_NAV}

    <form class="controls" method="get" action="/api/multihead">
        <div class="control-group">
            <label>Architecture</label>
            <select name="arch">
                <option value="A" {_sel(arch_key, 'A')}>A: NIR/Visible</option>
                <option value="B" {_sel(arch_key, 'B')}>B: Deep UV</option>
                <option value="C" {_sel(arch_key, 'C')}>C: EUV</option>
            </select>
        </div>
        <div class="control-group">
            <label>Array Rows</label>
            <input type="number" name="n_rows" value="{n_rows}" min="1" max="16" step="1">
        </div>
        <div class="control-group">
            <label>Array Cols</label>
            <input type="number" name="n_cols" value="{n_cols}" min="1" max="16" step="1">
        </div>
        <div class="control-group">
            <label>Overlap %</label>
            <input type="number" name="overlap_pct" value="{overlap_pct}" min="0" max="20" step="1">
        </div>
        <div class="control-group">
            <label>Emitters/Side</label>
            <input type="number" name="emitters_per_side" value="{emitters_per_side}" min="4" max="256" step="4">
        </div>
        <div class="control-group">
            <label>Source Power (mW)</label>
            <input type="number" name="source_power_mw" value="{source_power_mw}" min="0.001" max="1000" step="0.1">
        </div>
        <div class="control-group">
            <label>Dose (mJ/cm\u00b2)</label>
            <input type="number" name="dose_mj_cm2" value="{dose_mj_cm2}" min="1" max="100" step="1">
        </div>
        <button type="submit">Update</button>
    </form>

    <div class="callout" style="background:#eff6ff; border-color:#93c5fd; color:#1e40af; margin:16px 24px;">
        <b>Each writer head is an 11-DOF optical engine</b> built from 2D planar semiconductor
        layers: emitters, MEMS steering, waveguides, polarizers, Bragg diffractor mirrors,
        phase modulators, and vacuum containment. Batch-fabricated ~1,000 per wafer run.
        <a href="/api/writer-head" style="color:#2563eb; font-weight:700;">Explore the 3D structure \u2192</a>
    </div>

    <div class="section">
        <h2>Architecture Selection</h2>
        <p style="font-size:13px; color:#64748b; margin:0 0 4px 0;">
            Three wavelength regimes sharing a common tiled multi-head platform.
            Click a card or use the dropdown above to switch.
        </p>
        {cards}
    </div>

    <div class="section">
        <h2>Writer Head Array \u2014 Top-Down View</h2>
        <div class="callout">
            <b>{arch['name']}:</b> {n_rows}\u00d7{n_cols} = {n_heads} writer heads,
            each covering a {arch['tile_um']}\u00d7{arch['tile_um']} \u00b5m tile
            with {overlap_pct:.0f}% overlap stitch zones (yellow).
            Total tiled region: {array.wafer_region_x_um:.0f}\u00d7{array.wafer_region_y_um:.0f} \u00b5m.
        </div>
        <div class="plot-container">{array_html}</div>
    </div>

    <div class="section">
        <h2>Architecture Comparison</h2>
        <div class="plot-container">{arch_html}</div>
    </div>

    <div class="section">
        <h2>Per-Tile Exposure Calculator</h2>
        <div class="callout">
            <b>Source power:</b> {source_power_mw} mW total, split across {n_heads} heads
            = {source_power_mw/n_heads:.3f} mW/head.
            <b>Resist dose:</b> {dose_mj_cm2} mJ/cm\u00b2.
            Exposure times include 20% stepping overhead.
        </div>
        {exposure_table}
        <div class="plot-container">{exposure_chart_html}</div>
    </div>

    <div class="section">
        <h2>Per-Site Dose Calibration</h2>
        <div class="callout">
            <b>Patent claim:</b> Each emitter site has a static correction parameter (factory-measured)
            plus dynamic in-situ feedback from optical sensors[cite: 59] and temperature monitors.
            Raw fabrication variation (\u00b115%) is corrected to near-perfect uniformity via adaptive dose control[cite: 60].
            Shown for a {emitters_per_side}\u00d7{emitters_per_side} emitter array within one writer head.
        </div>
        <div class="plot-container">{cal_html}</div>
    </div>

    {_build_lab91_section_html()}
</body>
</html>"""
