"""Visualization for integrated platform economics and ASML power comparison."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from backend.fleet_economics import (
    compute_sensitivity_table,
    compute_scaling_table,
    ASML_POWER_CHAIN,
    COHERENT_POWER_CHAIN,
    ASML_REFERENCE,
    MARKET_SEGMENTS,
    PLATFORM_CONFIGS,
)
import math


def _format_power(w):
    """Format watts for display."""
    if w >= 1_000_000:
        return f"{w / 1_000_000:.1f} MW"
    if w >= 1_000:
        return f"{w / 1_000:.0f} kW"
    if w >= 1:
        return f"{w:.1f} W"
    if w >= 0.001:
        return f"{w * 1_000:.1f} mW"
    return f"{w * 1e6:.1f} \u00b5W"


def build_sensitivity_figure(scenarios):
    """Build multi-panel sensitivity dashboard figure."""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            "Platform Throughput (wph)",
            "Head Count on Platform",
            "Platform Cost ($M)",
            "Platform Power (kW)",
        ],
        horizontal_spacing=0.14,
        vertical_spacing=0.18,
    )

    powers = [s.euv_power_mw for s in scenarios]
    labels = [f"{p} mW" for p in powers]
    colors = ["#ef4444", "#f97316", "#eab308", "#22c55e", "#3b82f6"]

    # 1. Platform throughput
    fig.add_trace(go.Bar(
        x=labels, y=[s.wph for s in scenarios],
        marker_color=colors, name="wph",
        text=[f"{s.wph:.1f}" for s in scenarios],
        textposition="outside",
        hovertemplate="EUV Power: %{x}<br>Throughput: %{y:.2f} wph<extra></extra>",
    ), row=1, col=1)
    fig.add_hline(y=ASML_REFERENCE["wph"], line_dash="dash", line_color="#888",
                  annotation_text=f"ASML NXE ({ASML_REFERENCE['wph']} wph)",
                  annotation_position="top right", row=1, col=1)

    # 2. Head count
    fig.add_trace(go.Bar(
        x=labels, y=[s.total_heads for s in scenarios],
        marker_color=colors, name="Heads",
        text=[f"{s.total_heads:,}" for s in scenarios],
        textposition="outside",
        hovertemplate="EUV Power: %{x}<br>Writer heads: %{y:,}<extra></extra>",
    ), row=1, col=2)

    # 3. Platform cost with ASML reference
    cost_vals = [s.platform_cost_m for s in scenarios]
    fig.add_trace(go.Bar(
        x=labels, y=cost_vals,
        marker_color=colors, name="Platform Cost",
        text=[f"${v:.1f}M" for v in cost_vals],
        textposition="outside",
        hovertemplate="EUV Power: %{x}<br>Cost: $%{y:.1f}M<extra></extra>",
    ), row=2, col=1)
    fig.add_hline(y=ASML_REFERENCE["unit_cost_m"], line_dash="dash", line_color="#dc2626",
                  annotation_text=f"ASML NXE (${ASML_REFERENCE['unit_cost_m']}M)",
                  annotation_position="top right", row=2, col=1)

    # 4. Platform power with ASML reference
    power_vals = [s.platform_power_kw for s in scenarios]
    fig.add_trace(go.Bar(
        x=labels, y=power_vals,
        marker_color=colors, name="Platform Power",
        text=[f"{v:.1f} kW" for v in power_vals],
        textposition="outside",
        hovertemplate="EUV Power: %{x}<br>Power: %{y:.1f} kW<extra></extra>",
    ), row=2, col=2)
    fig.add_hline(y=ASML_REFERENCE["power_draw_kw"], line_dash="dash", line_color="#dc2626",
                  annotation_text=f"ASML NXE ({ASML_REFERENCE['power_draw_kw']} kW)",
                  annotation_position="top right", row=2, col=2)

    fig.update_layout(
        height=800,
        width=1300,
        showlegend=False,
        title_text="Integrated Platform Economics: Performance vs. EUV Source Power",
        margin=dict(t=60, b=40),
    )

    fig.update_yaxes(title_text="Wafers / Hour", row=1, col=1)
    fig.update_yaxes(title_text="Writer Heads", row=1, col=2)
    fig.update_yaxes(title_text="$M USD", row=2, col=1)
    fig.update_yaxes(title_text="kW", row=2, col=2)
    for r in range(1, 3):
        for c in range(1, 3):
            fig.update_xaxes(title_text="EUV Source Power per Head", row=r, col=c)

    return fig


def build_scaling_figure(scaling_scenarios):
    """Build chart showing throughput and cost across platform configurations."""
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=[
            "Throughput by Config (wph)",
            "Platform Cost ($M)",
            "Single-Head Failure Impact (%)",
        ],
        horizontal_spacing=0.10,
    )

    names = [s.config_name for s in scaling_scenarios]
    heads = [s.total_heads for s in scaling_scenarios]
    colors = ["#3b82f6", "#22c55e", "#f97316", "#ef4444"]

    # Throughput
    fig.add_trace(go.Bar(
        x=[f"{n}<br>({h:,} heads)" for n, h in zip(names, heads)],
        y=[s.wph for s in scaling_scenarios],
        marker_color=colors,
        text=[f"{s.wph:.1f}" for s in scaling_scenarios],
        textposition="outside",
        showlegend=False,
    ), row=1, col=1)
    fig.add_hline(y=ASML_REFERENCE["wph"], line_dash="dash", line_color="#888",
                  annotation_text="ASML 220 wph", annotation_position="top right",
                  row=1, col=1)

    # Cost
    fig.add_trace(go.Bar(
        x=[f"{n}<br>({h:,} heads)" for n, h in zip(names, heads)],
        y=[s.platform_cost_m for s in scaling_scenarios],
        marker_color=colors,
        text=[f"${s.platform_cost_m:.1f}M" for s in scaling_scenarios],
        textposition="outside",
        showlegend=False,
    ), row=1, col=2)
    fig.add_hline(y=ASML_REFERENCE["unit_cost_m"], line_dash="dash", line_color="#dc2626",
                  annotation_text="ASML $380M", annotation_position="top right",
                  row=1, col=2)

    # Redundancy
    fig.add_trace(go.Bar(
        x=[f"{n}<br>({h:,} heads)" for n, h in zip(names, heads)],
        y=[s.single_head_failure_pct for s in scaling_scenarios],
        marker_color=colors,
        text=[f"{s.single_head_failure_pct:.2f}%" for s in scaling_scenarios],
        textposition="outside",
        showlegend=False,
    ), row=1, col=3)
    fig.add_hline(y=100, line_dash="dash", line_color="#dc2626",
                  annotation_text="ASML: 100% (single point of failure)",
                  annotation_position="bottom right", row=1, col=3)

    fig.update_yaxes(title_text="wph", row=1, col=1)
    fig.update_yaxes(title_text="$M USD", row=1, col=2)
    fig.update_yaxes(title_text="% throughput lost", row=1, col=3)

    fig.update_layout(
        height=450, width=1300, showlegend=False,
        title_text="Platform Scaling: More Heads = More Throughput, Lower Risk",
        margin=dict(t=60, b=80),
    )
    return fig


def build_waterfall_figure():
    """Build side-by-side ASML vs Coherent Source power loss waterfall."""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            "ASML LPP: 1.5 MW \u2192 1 W at Wafer",
            "Integrated Platform: 500 W \u2192 0.9 mW at Wafer",
        ],
        horizontal_spacing=0.12,
    )

    asml_stages = [s["stage"] for s in ASML_POWER_CHAIN]
    asml_powers = [s["power_w"] for s in ASML_POWER_CHAIN]
    asml_notes = [s["note"] for s in ASML_POWER_CHAIN]
    asml_log = [math.log10(max(p, 1e-6)) for p in asml_powers]

    fig.add_trace(go.Bar(
        x=asml_stages, y=asml_log,
        marker_color=_gradient_colors(len(asml_stages), "#dc2626", "#fee2e2"),
        text=[_format_power(p) for p in asml_powers],
        textposition="outside",
        hovertext=[f"{s}<br>{_format_power(p)}<br>{n}"
                   for s, p, n in zip(asml_stages, asml_powers, asml_notes)],
        hoverinfo="text", name="ASML LPP",
    ), row=1, col=1)

    coh_stages = [s["stage"] for s in COHERENT_POWER_CHAIN]
    coh_powers = [s["power_w"] for s in COHERENT_POWER_CHAIN]
    coh_notes = [s["note"] for s in COHERENT_POWER_CHAIN]
    coh_log = [math.log10(max(p, 1e-6)) for p in coh_powers]

    fig.add_trace(go.Bar(
        x=coh_stages, y=coh_log,
        marker_color=_gradient_colors(len(coh_stages), "#2563eb", "#dbeafe"),
        text=[_format_power(p) for p in coh_powers],
        textposition="outside",
        hovertext=[f"{s}<br>{_format_power(p)}<br>{n}"
                   for s, p, n in zip(coh_stages, coh_powers, coh_notes)],
        hoverinfo="text", name="Integrated Platform",
    ), row=1, col=2)

    for col in [1, 2]:
        fig.update_yaxes(
            title_text="Power (log\u2081\u2080 W)", range=[-4, 7],
            tickvals=[-3, -2, -1, 0, 1, 2, 3, 4, 5, 6],
            ticktext=["1 mW", "10 mW", "100 mW", "1 W", "10 W", "100 W",
                       "1 kW", "10 kW", "100 kW", "1 MW"],
            row=1, col=col,
        )
        fig.update_xaxes(tickangle=-35, row=1, col=col)

    fig.update_layout(
        height=600, width=1300, showlegend=False,
        title_text="Power Loss Chain: ASML Tin-Plasma vs. Coherent Chip-Scale Source",
        margin=dict(t=60, b=120),
    )
    return fig


def _gradient_colors(n, start_hex, end_hex):
    """Generate a gradient of n colors between two hex colors."""
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    s = hex_to_rgb(start_hex)
    e = hex_to_rgb(end_hex)
    colors = []
    for i in range(n):
        t = i / max(n - 1, 1)
        r = int(s[0] + (e[0] - s[0]) * t)
        g = int(s[1] + (e[1] - s[1]) * t)
        b = int(s[2] + (e[2] - s[2]) * t)
        colors.append(f"rgb({r},{g},{b})")
    return colors


def build_comparison_table_html(scenarios):
    """Build HTML comparison table for platform scenarios."""
    rows = ""
    for s in scenarios:
        savings_class = "positive" if s.capex_savings_pct > 0 else "negative"
        power_class = "positive" if s.power_savings_pct > 0 else "negative"
        rows += f"""<tr>
            <td><b>{s.euv_power_mw} mW</b></td>
            <td>{s.total_heads:,}</td>
            <td>{s.wph:.2f}</td>
            <td>{s.seconds_per_field:.1f}s</td>
            <td>${s.platform_cost_m:.1f}M</td>
            <td class="{savings_class}">{s.capex_savings_pct:+.0f}%</td>
            <td>{s.platform_power_kw:.1f} kW</td>
            <td class="{power_class}">{s.power_savings_pct:+.1f}%</td>
            <td>{s.single_head_failure_pct:.2f}%</td>
        </tr>"""

    return f"""<table class="data-table">
        <thead><tr>
            <th>EUV Power<br>per Head</th>
            <th>Writer<br>Heads</th>
            <th>Platform<br>wph</th>
            <th>Time /<br>Field</th>
            <th>Platform<br>Cost</th>
            <th>vs ASML<br>$380M</th>
            <th>Platform<br>Power</th>
            <th>vs ASML<br>1.5 MW</th>
            <th>Single-Head<br>Failure</th>
        </tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


def build_market_segments_html():
    """Build market segment cards showing platform configurations."""
    cards = ""
    icons = {
        "R&D / Prototyping": "\U0001F52C",
        "Specialty / Defense": "\U0001F6E1\uFE0F",
        "Mid-Volume": "\U0001F3ED",
        "HVM Parity": "\U0001F680",
    }
    for name, info in MARKET_SEGMENTS.items():
        icon = icons.get(name, "")
        cfg = info["config"]
        cards += f"""<div class="segment-card">
            <div class="segment-icon">{icon}</div>
            <h3>{name}</h3>
            <p>{info['description']}</p>
            <div class="segment-stats">
                <span>{cfg.total_heads:,} heads</span>
                <span>{cfg.total_packages} pkgs</span>
                <span>{cfg.modules} module{'s' if cfg.modules > 1 else ''}</span>
                <span>{info['capex_range']}</span>
                <span>{info['power_range']}</span>
                <span>{cfg.footprint_m2} m\u00b2</span>
            </div>
        </div>"""
    return f'<div class="segments">{cards}</div>'


def _build_hierarchy_html(config_name):
    """Build visual hierarchy diagram showing platform → module → package → head."""
    cfg = PLATFORM_CONFIGS.get(config_name, list(PLATFORM_CONFIGS.values())[1])
    return f"""<div class="hierarchy">
        <div class="hier-level platform">
            <div class="hier-label">Platform</div>
            <div class="hier-detail">{cfg.footprint_m2} m\u00b2 \u00b7 ${cfg.total_cost_m:.1f}M \u00b7 {cfg.total_power_kw:.1f} kW</div>
            <div class="hier-children">
                <div class="hier-level module">
                    <div class="hier-label">{cfg.modules} Module{'s' if cfg.modules > 1 else ''}</div>
                    <div class="hier-detail">~200\u00d7200mm board \u00b7 ${cfg.module_cost_usd/1000:.0f}k ea \u00b7 robotic cleanroom assembly</div>
                    <div class="hier-children">
                        <div class="hier-level package">
                            <div class="hier-label">{cfg.packages_per_module} Package{'s' if cfg.packages_per_module > 1 else ''} / module</div>
                            <div class="hier-detail">33\u00d733mm \u00b7 ${cfg.package_cost_usd/1000:.0f}k ea \u00b7 flip-chip optical coupling</div>
                            <div class="hier-children">
                                <div class="hier-level head">
                                    <div class="hier-label">{cfg.heads_per_package} Writer Heads / package</div>
                                    <div class="hier-detail">~2\u00d72mm die \u00b7 ${cfg.head_cost_usd} ea \u00b7 <a href="/api/writer-head" style="color:#8b5cf6;font-weight:700;">11 DOF</a> \u00b7 batch fab 1,000/run</div>
                                    <div class="hier-components">Emitters + MEMS + waveguides + polarizers + Bragg mirrors + vacuum shell + immersion coupling &nbsp; <a href="/api/writer-head" style="color:#8b5cf6;font-size:11px;">[explore 3D stack]</a></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="hier-total">\u2192 <b>{cfg.total_heads:,} writer heads</b> on one desk-sized platform</div>
        </div>
    </div>"""


def build_fleet_dashboard_html(scenarios, params, title="Platform Economics & ASML Comparison"):
    """Build full HTML page with platform economics dashboard."""
    sensitivity_fig = build_sensitivity_figure(scenarios)
    waterfall_fig = build_waterfall_figure()

    # Scaling across configurations at 10 mW
    scaling_scenarios = compute_scaling_table(euv_power_mw=10.0)
    scaling_fig = build_scaling_figure(scaling_scenarios)

    sensitivity_html = sensitivity_fig.to_html(full_html=False, include_plotlyjs=False)
    waterfall_html = waterfall_fig.to_html(full_html=False, include_plotlyjs=False)
    scaling_html = scaling_fig.to_html(full_html=False, include_plotlyjs=False)

    table_html = build_comparison_table_html(scenarios)
    segments_html = build_market_segments_html()
    hierarchy_html = _build_hierarchy_html("Specialty / Defense")

    dose = params.get("dose_mj_cm2", 15.0)
    config_name = params.get("config_name", "Specialty / Defense")

    # Headline numbers from the 10 mW scenario
    scenario_10 = next((s for s in scenarios if s.euv_power_mw == 10.0), scenarios[-1])

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="plotly.min.js"></script>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }}
        .nav {{ background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }}
        .nav a {{ color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }}
        .nav a:hover {{ background: #2a2a4e; }}
        .nav a.active {{ background: #2563eb; color: #fff; }}

        .controls {{
            background: #fff; padding: 12px 24px; border-bottom: 1px solid #e2e8f0;
            display: flex; flex-wrap: wrap; gap: 14px; align-items: end;
        }}
        .control-group {{ display: flex; flex-direction: column; gap: 3px; }}
        .control-group label {{ font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }}
        .control-group input, .control-group select {{ padding: 5px 8px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 13px; width: 110px; }}
        button {{
            padding: 7px 18px; background: #2563eb; color: #fff; border: none;
            border-radius: 4px; font-size: 13px; cursor: pointer; font-weight: 600;
        }}
        button:hover {{ background: #1d4ed8; }}

        .hero {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #fff; padding: 32px 40px; display: flex; gap: 32px; flex-wrap: wrap;
        }}
        .hero-stat {{
            text-align: center; min-width: 160px; flex: 1;
        }}
        .hero-stat .value {{ font-size: 36px; font-weight: 800; color: #38bdf8; }}
        .hero-stat .label {{ font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
        .hero-stat .sub {{ font-size: 13px; color: #64748b; margin-top: 2px; }}

        .section {{ padding: 16px 24px; }}
        .section h2 {{ font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0; border-bottom: 2px solid #2563eb; padding-bottom: 6px; display: inline-block; }}

        .data-table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }}
        .data-table th {{ background: #f1f5f9; padding: 10px 12px; text-align: left; font-weight: 700; color: #475569; border-bottom: 2px solid #e2e8f0; }}
        .data-table td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }}
        .data-table tr:hover {{ background: #f8fafc; }}
        .positive {{ color: #16a34a; font-weight: 700; }}
        .negative {{ color: #dc2626; font-weight: 700; }}

        .segments {{ display: flex; gap: 16px; flex-wrap: wrap; margin-top: 12px; }}
        .segment-card {{
            flex: 1; min-width: 200px; background: #fff; border: 1px solid #e2e8f0;
            border-radius: 10px; padding: 20px; transition: transform 0.15s, box-shadow 0.15s;
        }}
        .segment-card:hover {{ transform: translateY(-3px); box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
        .segment-icon {{ font-size: 28px; margin-bottom: 8px; }}
        .segment-card h3 {{ margin: 0 0 6px 0; font-size: 15px; color: #0f172a; }}
        .segment-card p {{ font-size: 12px; color: #64748b; margin: 0 0 10px 0; line-height: 1.4; }}
        .segment-stats {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .segment-stats span {{
            font-size: 11px; background: #f1f5f9; padding: 3px 8px; border-radius: 12px;
            color: #475569; font-weight: 600;
        }}

        .callout {{
            background: #fffbeb; border: 1px solid #fbbf24; border-radius: 8px;
            padding: 14px 20px; margin: 16px 0; font-size: 13px; color: #92400e; line-height: 1.5;
        }}
        .callout b {{ color: #78350f; }}

        .callout-blue {{
            background: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px;
            padding: 14px 20px; margin: 16px 0; font-size: 13px; color: #1e40af; line-height: 1.5;
        }}
        .callout-blue b {{ color: #1e3a8a; }}

        .plot-container {{ padding: 0 8px; }}

        .hierarchy {{
            background: #fff; border: 2px solid #e2e8f0; border-radius: 12px;
            padding: 24px; margin: 16px 0;
        }}
        .hier-level {{
            border-left: 3px solid #cbd5e1; padding: 8px 0 8px 16px; margin: 4px 0;
        }}
        .hier-level.platform {{ border-left-color: #2563eb; }}
        .hier-level.module {{ border-left-color: #22c55e; }}
        .hier-level.package {{ border-left-color: #f97316; }}
        .hier-level.head {{ border-left-color: #8b5cf6; }}
        .hier-label {{ font-weight: 700; font-size: 15px; color: #0f172a; }}
        .hier-detail {{ font-size: 12px; color: #64748b; margin-top: 2px; }}
        .hier-components {{ font-size: 11px; color: #8b5cf6; font-style: italic; margin-top: 3px; }}
        .hier-children {{ margin-left: 8px; }}
        .hier-total {{ margin-top: 10px; font-size: 14px; color: #2563eb; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/api/visualize">2D Process Sim</a>
        <a href="/api/visualize-3d">3D Pipeline</a>
        <a href="/api/fleet-dashboard" class="active">Platform Economics</a>
        <a href="/api/multihead">Multi-Head Array</a>
        <a href="/api/psf-synthesis">PSF Synthesis</a>
        <a href="/api/writer-head">11-DOF Head</a>
    </div>

    <div class="hero">
        <div class="hero-stat">
            <div class="value">{scenario_10.capex_savings_pct:+.0f}%</div>
            <div class="label">Cost vs ASML</div>
            <div class="sub">${scenario_10.platform_cost_m:.1f}M platform vs $380M monolith</div>
        </div>
        <div class="hero-stat">
            <div class="value">{scenario_10.power_savings_pct:+.1f}%</div>
            <div class="label">Power Reduction</div>
            <div class="sub">{scenario_10.platform_power_kw:.1f} kW vs 1,500 kW</div>
        </div>
        <div class="hero-stat">
            <div class="value">{scenario_10.footprint_savings_pct:+.0f}%</div>
            <div class="label">Footprint</div>
            <div class="sub">{scenario_10.footprint_m2} m\u00b2 desk vs 120 m\u00b2 cleanroom</div>
        </div>
        <div class="hero-stat">
            <div class="value">{scenario_10.single_head_failure_pct:.2f}%</div>
            <div class="label">Per-Head Failure</div>
            <div class="sub">{scenario_10.total_heads:,} heads \u2192 graceful degradation</div>
        </div>
        <div class="hero-stat">
            <div class="value">{scenario_10.wph:.1f}</div>
            <div class="label">Platform wph</div>
            <div class="sub">@ {scenario_10.euv_power_mw} mW, {dose} mJ/cm\u00b2 dose</div>
        </div>
    </div>

    <form class="controls" method="get" action="/api/fleet-dashboard">
        <div class="control-group">
            <label>Resist Dose (mJ/cm\u00b2)</label>
            <input type="number" name="dose_mj_cm2" value="{dose}" step="1" min="1" max="100">
        </div>
        <div class="control-group">
            <label>Platform Config</label>
            <select name="config_name">
                {"".join(f'<option value="{n}" {"selected" if n == config_name else ""}>{n}</option>' for n in PLATFORM_CONFIGS)}
            </select>
        </div>
        <button type="submit">Recalculate</button>
    </form>

    <div class="callout-blue">
        <b>Integrated Platform Architecture:</b> Each writer head is a 3D optical structure built from 2D planar
        semiconductor processes with 11 degrees of freedom (beam XY, focus, intensity, polarization, waveguide routing,
        optical switching, wavelength, pulse timing, dose dwell, thermal compensation). Heads are batch-fabricated
        ~1,000 per wafer run and robotically assembled in cleanrooms. One desk-sized platform replaces
        a room-sized $380M ASML tool.
    </div>

    <div class="section">
        <h2>Platform Hierarchy</h2>
        <p style="font-size: 13px; color: #64748b; margin: 0 0 4px 0;">
            3D optical structures from 2D planar semiconductor fab \u2192 batch manufacturing at scale.
        </p>
        {hierarchy_html}
    </div>

    <div class="section">
        <h2>Performance Sensitivity vs. EUV Source Power</h2>
        <div class="callout">
            <b>Sensitivity Analysis:</b> Shows how platform economics change across EUV source power levels
            from 0.1 mW (worst-case) to 50 mW (optimistic). Even at 1 mW, the platform delivers viable R&amp;D
            capability at a fraction of ASML&rsquo;s cost and power. Dashed lines show ASML NXE:3800E reference.
        </div>
        <div class="plot-container">{sensitivity_html}</div>
    </div>

    <div class="section">
        <h2>Platform Scaling: Head Count vs. Performance</h2>
        <p style="font-size: 13px; color: #64748b; margin: 0 0 8px 0;">
            Semiconductor replication: add packages and modules to scale throughput linearly.
            Single-head failure impact approaches zero as head count grows \u2014 graceful degradation
            vs. ASML\u2019s catastrophic single point of failure.
        </p>
        <div class="plot-container">{scaling_html}</div>
    </div>

    <div class="section">
        <h2>Power Loss Chain Comparison</h2>
        <p style="font-size: 13px; color: #64748b; margin: 0 0 8px 0;">
            ASML\u2019s incoherent tin-plasma source loses 99.99993% of input power before reaching the wafer.
            A coherent chip-scale HHG source eliminates the collection problem entirely.
        </p>
        <div class="plot-container">{waterfall_html}</div>
    </div>

    <div class="section">
        <h2>Detailed Comparison Table</h2>
        {table_html}
    </div>

    <div class="section">
        <h2>Platform Configurations by Market</h2>
        <p style="font-size: 13px; color: #64748b; margin: 0 0 4px 0;">
            Same semiconductor-manufactured writer heads, different platform scale. Entry at R&amp;D tier
            (${list(PLATFORM_CONFIGS.values())[0].total_cost_m:.1f}M vs $380M minimum), then scale up by adding packages and modules.
        </p>
        {segments_html}
    </div>
</body>
</html>"""
