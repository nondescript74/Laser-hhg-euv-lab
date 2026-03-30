import plotly.graph_objects as go
from plotly.subplots import make_subplots

STAGE_CONFIG = [
    ("aerial_image", "Aerial Image (Target Pattern)", "Viridis", "Intensity (a.u.)"),
    ("acid_map", "Acid Map (Post-Exposure)", "Hot", "Acid Conc. (a.u.)"),
    ("deprotection", "Deprotection Profile (Post-PEB)", "Plasma", "Deprotection (a.u.)"),
    ("dissolution_rate", "Dissolution Rate (Mack Model)", "Inferno", "Rate (nm/s)"),
]


def build_pipeline_figure(stages, title="EUV Lithography Simulation Pipeline"):
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[cfg[1] for cfg in STAGE_CONFIG],
        horizontal_spacing=0.22,
        vertical_spacing=0.16,
    )

    for idx, (key, label, colorscale, cbar_title) in enumerate(STAGE_CONFIG):
        row, col = divmod(idx, 2)
        fig.add_trace(
            go.Heatmap(
                z=stages[key],
                colorscale=colorscale,
                colorbar=dict(
                    title=dict(text=cbar_title, side="right"),
                    len=0.35,
                    y=0.82 - row * 0.60,
                    x=0.42 + col * 0.58,
                    thickness=15,
                ),
                hovertemplate="x: %{x} nm<br>y: %{y} nm<br>value: %{z:.4f}<extra></extra>",
            ),
            row=row + 1, col=col + 1,
        )

    # Add axis labels to all subplots
    for i in range(1, 5):
        fig.update_xaxes(title_text="X Position (nm)", row=(i - 1) // 2 + 1, col=(i - 1) % 2 + 1)
        fig.update_yaxes(title_text="Y Position (nm)", row=(i - 1) // 2 + 1, col=(i - 1) % 2 + 1)

    fig.update_layout(
        title_text=title,
        height=1000,
        width=1200,
    )
    return fig


def build_tunable_html(stages, params, title="EUV Lithography Simulation Pipeline"):
    """Build full HTML page with plotly figure and parameter controls."""
    fig = build_pipeline_figure(stages, title=title)
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False)

    dose = params.get("dose", 15.0)
    line_width = params.get("line_width", 20)
    peb_time = params.get("peb_time", 60.0)
    diffusion_coef = params.get("diffusion_coef", 5.0)
    k_amp = params.get("k_amp", 0.2)
    r_max = params.get("r_max", 100.0)
    n_mack = params.get("n_mack", 5)

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>EUV Litho Pipeline</title>
    <script src="plotly.min.js"></script>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #fafafa; }}
        .nav {{ background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }}
        .nav a {{ color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }}
        .nav a:hover {{ background: #2a2a4e; }}
        .nav a.active {{ background: #2563eb; color: #fff; }}
        .controls {{
            background: #fff; padding: 16px 24px; border-bottom: 1px solid #e0e0e0;
            display: flex; flex-wrap: wrap; gap: 16px; align-items: end;
        }}
        .control-group {{ display: flex; flex-direction: column; gap: 4px; }}
        .control-group label {{ font-size: 12px; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }}
        .control-group input {{ width: 90px; padding: 6px 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }}
        .control-group .value-display {{ font-size: 11px; color: #888; min-height: 16px; }}
        button {{
            padding: 8px 20px; background: #2563eb; color: #fff; border: none;
            border-radius: 4px; font-size: 14px; cursor: pointer; font-weight: 600;
            align-self: end;
        }}
        button:hover {{ background: #1d4ed8; }}
        .plot-container {{ padding: 8px; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/api/visualize" class="active">2D Process Sim</a>
        <a href="/api/visualize-3d">3D Pipeline</a>
        <a href="/api/fleet-dashboard">Platform Economics</a>
        <a href="/api/multihead">Multi-Head Array</a>
        <a href="/api/psf-synthesis">PSF Synthesis</a>
        <a href="/api/writer-head">11-DOF Head</a>
    </div>
    <form class="controls" method="get" action="/api/visualize">
        <div class="control-group">
            <label>Dose (mJ/cm&sup2;)</label>
            <input type="number" name="dose" value="{dose}" step="1" min="1" max="500">
        </div>
        <div class="control-group">
            <label>Line Width (nm)</label>
            <input type="number" name="line_width" value="{line_width}" step="1" min="1" max="128">
        </div>
        <div class="control-group">
            <label>PEB Time (s)</label>
            <input type="number" name="peb_time" value="{peb_time}" step="5" min="1" max="300">
        </div>
        <div class="control-group">
            <label>Diffusion (nm&sup2;/s)</label>
            <input type="number" name="diffusion_coef" value="{diffusion_coef}" step="0.5" min="0.1" max="50">
        </div>
        <div class="control-group">
            <label>k_amp</label>
            <input type="number" name="k_amp" value="{k_amp}" step="0.05" min="0.01" max="2">
        </div>
        <div class="control-group">
            <label>r_max (nm/s)</label>
            <input type="number" name="r_max" value="{r_max}" step="10" min="1" max="1000">
        </div>
        <div class="control-group">
            <label>Mack n</label>
            <input type="number" name="n_mack" value="{n_mack}" step="1" min="1" max="20">
        </div>
        <button type="submit">Simulate</button>
    </form>
    <div class="plot-container">
        {plot_html}
    </div>
    <div style="background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;padding:12px 20px;margin:12px 24px;font-size:13px;color:#1e40af;line-height:1.5;">
        <b>Connection to hardware:</b> This simulation models the resist response to a single exposure field.
        Each <a href="/api/writer-head" style="color:#2563eb;font-weight:700;">11-DOF writer head</a> delivers
        this PSF to one tile. The <a href="/api/multihead" style="color:#2563eb;">multi-head array</a> tiles
        many such heads across the wafer simultaneously.
    </div>
</body>
</html>"""
