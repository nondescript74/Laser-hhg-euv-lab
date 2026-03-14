import numpy as np
import plotly.graph_objects as go


def _cylinder_mesh(z_start, z_end, radius, color, name, opacity=0.6, n_seg=24):
    """Generate a cylinder as a Mesh3d trace along the z-axis."""
    theta = np.linspace(0, 2 * np.pi, n_seg, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    # Bottom ring (z_start) + top ring (z_end) + 2 center points for caps
    x = np.concatenate([radius * cos_t, radius * cos_t, [0, 0]])
    y = np.concatenate([radius * sin_t, radius * sin_t, [0, 0]])
    z = np.concatenate([np.full(n_seg, z_start), np.full(n_seg, z_end),
                        [z_start, z_end]])

    center_bot = 2 * n_seg
    center_top = 2 * n_seg + 1

    ii, jj, kk = [], [], []

    for s in range(n_seg):
        s_next = (s + 1) % n_seg
        # Side faces (two triangles per quad)
        ii += [s, s, s + n_seg]
        jj += [s_next, s + n_seg, s_next + n_seg]
        kk += [s + n_seg, s_next, s_next]
        # Bottom cap
        ii.append(center_bot)
        jj.append(s)
        kk.append(s_next)
        # Top cap
        ii.append(center_top)
        jj.append(s_next + n_seg)
        kk.append(s + n_seg)

    return go.Mesh3d(
        x=x, y=y, z=z,
        i=ii, j=jj, k=kk,
        color=color, opacity=opacity,
        name=name, hoverinfo="name",
        flatshading=True,
    )


def _disc_mesh(z_pos, radius, color, name, opacity=0.8, n_seg=24):
    """Generate a thin disc as a Mesh3d trace."""
    return _cylinder_mesh(z_pos, z_pos + 0.3, radius, color, name, opacity, n_seg)


def _beam_surface(z_vals, r_envelope, color_transition_z, n_ang=16):
    """Generate beam envelope as a surface of revolution."""
    theta = np.linspace(0, 2 * np.pi, n_ang)
    traces = []

    # Split into IR and EUV segments
    ir_mask = z_vals <= color_transition_z
    euv_mask = z_vals >= color_transition_z

    for mask, color, beam_name in [
        (ir_mask, "rgba(255,80,40,0.25)", "IR Beam (800nm)"),
        (euv_mask, "rgba(130,60,255,0.25)", "EUV Beam (13.5nm)"),
    ]:
        z_seg = z_vals[mask]
        r_seg = r_envelope[mask]
        if len(z_seg) < 2:
            continue

        Z, T = np.meshgrid(z_seg, theta)
        R = np.tile(r_seg, (n_ang, 1))
        X = R * np.cos(T)
        Y = R * np.sin(T)

        traces.append(go.Surface(
            x=X, y=Y, z=Z,
            surfacecolor=np.ones_like(Z),
            colorscale=[[0, color], [1, color]],
            showscale=False,
            name=beam_name,
            hoverinfo="name",
            opacity=0.35,
        ))

    # Beam centerline
    traces.append(go.Scatter3d(
        x=np.zeros_like(z_vals), y=np.zeros_like(z_vals), z=z_vals,
        mode="lines",
        line=dict(color="white", width=2),
        name="Optical Axis",
        hoverinfo="name",
    ))

    return traces


def _render_gas_supply_lines(gas_cell):
    """Render gas inlet/outlet pipes and pressure gauge."""
    traces = []
    supply_lines = gas_cell.properties.get("supply_lines", [])
    pressure = gas_cell.properties.get("pressure_mbar", 30)
    gas_type = gas_cell.properties.get("gas_type", "Ar")

    for line_info in supply_lines:
        lx, ly, lz = line_info["x"], line_info["y"], line_info["z"]
        label = line_info["label"]

        # Pipe from gas cell surface to external point
        traces.append(go.Scatter3d(
            x=[0, lx], y=[0, ly], z=[lz, lz],
            mode="lines+markers",
            line=dict(color="#888888", width=6),
            marker=dict(size=[0, 5], color=["#888888", "#dd6633"]),
            name=label,
            hovertext=f"{label}<br>{gas_type} @ {pressure:.0f} mbar",
            hoverinfo="text",
        ))

        # Label
        traces.append(go.Scatter3d(
            x=[lx * 1.3], y=[ly * 1.3], z=[lz],
            mode="text",
            text=[label],
            textfont=dict(size=10, color="#555555"),
            hoverinfo="skip",
            showlegend=False,
        ))

    return traces


def _render_power_annotations(power_budget):
    """Add power level labels at each component, offset far to the left."""
    traces = []
    x_vals, y_vals, z_vals, texts = [], [], [], []

    for entry in power_budget:
        z_vals.append(entry["z_mid"])
        x_vals.append(-85)  # far left of beam axis
        y_vals.append(0)
        power = entry["power_out"]
        if power >= 1e-3:
            txt = f"{power:.3f} W"
        elif power >= 1e-6:
            txt = f"{power*1e6:.2f} \u00b5W"
        elif power >= 1e-9:
            txt = f"{power*1e9:.2f} nW"
        else:
            txt = f"{power:.2e} W"
        texts.append(f"<b>{entry['name']}</b><br>{txt}")

    traces.append(go.Scatter3d(
        x=x_vals, y=y_vals, z=z_vals,
        mode="text",
        text=texts,
        textfont=dict(size=10, color="#222222"),
        hoverinfo="text",
        showlegend=False,
    ))
    return traces


def build_3d_pipeline_figure(pipeline, params=None):
    """Build complete 3D optical pipeline figure."""
    fig = go.Figure()

    # Render each component
    for comp in pipeline.components:
        if comp.component_type == "wafer":
            # Flat disc for wafer
            fig.add_trace(_disc_mesh(
                comp.z_start, comp.radius, comp.color, comp.name, opacity=0.7))
        elif comp.component_type == "filter":
            fig.add_trace(_disc_mesh(
                comp.z_start, comp.radius, comp.color, comp.name, opacity=0.7))
        elif comp.component_type == "gas_cell":
            fig.add_trace(_cylinder_mesh(
                comp.z_start, comp.z_end, comp.radius,
                comp.color, comp.name, opacity=0.3))
            # Gas supply lines
            for trace in _render_gas_supply_lines(comp):
                fig.add_trace(trace)
        elif comp.component_type == "mirror":
            fig.add_trace(_disc_mesh(
                comp.z_start, comp.radius, comp.color, comp.name, opacity=0.8))
        else:
            # source, lens, etc.
            fig.add_trace(_cylinder_mesh(
                comp.z_start, comp.z_end, comp.radius,
                comp.color, comp.name, opacity=0.6))

    # Beam path
    z_vals, x_c, y_c, r_env, color_z = pipeline.get_beam_path()
    for trace in _beam_surface(z_vals, r_env, color_z):
        fig.add_trace(trace)

    # Power budget annotations
    budget = pipeline.compute_power_budget()
    for trace in _render_power_annotations(budget):
        fig.add_trace(trace)

    # HHG info annotation — placed far to the right so it doesn't overlap
    gas_cell = next((c for c in pipeline.components if c.component_type == "gas_cell"), None)
    if gas_cell:
        props = gas_cell.properties
        fig.add_trace(go.Scatter3d(
            x=[85], y=[0], z=[(gas_cell.z_start + gas_cell.z_end) / 2],
            mode="text",
            text=[
                f"<b>{props.get('gas_type', 'Ar')} HHG</b><br>"
                f"P={props.get('pressure_mbar', 30):.0f} mbar<br>"
                f"IP={props.get('ionization_potential_ev', 0):.1f} eV<br>"
                f"Cutoff={props.get('cutoff_energy_ev', 0):.0f} eV<br>"
                f"H{props.get('target_harmonic', 59)} \u2192 "
                f"{props.get('euv_wavelength_nm', 13.5):.1f} nm"
            ],
            textfont=dict(size=11, color="#006644"),
            hoverinfo="skip",
            showlegend=False,
        ))

    # Layout — wide scene with text pushed to sides
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (mm)", range=[-100, 100], showgrid=True, gridcolor="#eee"),
            yaxis=dict(title="Y (mm)", range=[-30, 30], showgrid=True, gridcolor="#eee"),
            zaxis=dict(title="Z — Optical Axis (mm)", range=[-5, 140], showgrid=True, gridcolor="#eee"),
            aspectmode="manual",
            aspectratio=dict(x=1.8, y=0.5, z=1.2),
            camera=dict(
                eye=dict(x=2.0, y=0.6, z=0.3),
                up=dict(x=0, y=0, z=1),
            ),
            bgcolor="#fafafa",
        ),
        title=dict(text="EUV Lithography Optical Pipeline (VCSEL \u2192 HHG \u2192 Wafer)"),
        height=900,
        width=1500,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(l=0, r=0, t=40, b=0),
    )

    return fig


def build_3d_pipeline_html(pipeline, params, title="EUV Optical Pipeline"):
    """Build full HTML page with 3D figure and tunable controls."""
    fig = build_3d_pipeline_figure(pipeline, params)
    plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    gas_type = params.get("gas_type", "Ar")
    pressure = params.get("pressure_mbar", 30.0)
    intensity = params.get("intensity_w_cm2", 1e14)
    n_mirrors = params.get("n_mirrors", 2)
    filter_material = params.get("filter_material", "Al")
    filter_thickness = params.get("filter_thickness_nm", 200.0)

    def _selected(val, option):
        return "selected" if str(val) == str(option) else ""

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #fafafa; }}
        .nav {{ background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }}
        .nav a {{ color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }}
        .nav a:hover {{ background: #2a2a4e; }}
        .nav a.active {{ background: #2563eb; color: #fff; }}
        .controls {{
            background: #fff; padding: 12px 24px; border-bottom: 1px solid #e0e0e0;
            display: flex; flex-wrap: wrap; gap: 14px; align-items: end;
        }}
        .control-group {{ display: flex; flex-direction: column; gap: 3px; }}
        .control-group label {{ font-size: 11px; font-weight: 600; color: #555; text-transform: uppercase; letter-spacing: 0.5px; }}
        .control-group input, .control-group select {{ padding: 5px 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px; }}
        .control-group input {{ width: 100px; }}
        .control-group select {{ width: 80px; }}
        button {{
            padding: 7px 18px; background: #2563eb; color: #fff; border: none;
            border-radius: 4px; font-size: 13px; cursor: pointer; font-weight: 600;
        }}
        button:hover {{ background: #1d4ed8; }}
        .plot-container {{ padding: 0; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/api/visualize">2D Process Simulation</a>
        <a href="/api/visualize-3d" class="active">3D Optical Pipeline</a>
    </div>
    <form class="controls" method="get" action="/api/visualize-3d">
        <div class="control-group">
            <label>Gas Type</label>
            <select name="gas_type">
                <option value="Ar" {_selected(gas_type, "Ar")}>Argon</option>
                <option value="Ne" {_selected(gas_type, "Ne")}>Neon</option>
                <option value="Xe" {_selected(gas_type, "Xe")}>Xenon</option>
                <option value="Kr" {_selected(gas_type, "Kr")}>Krypton</option>
            </select>
        </div>
        <div class="control-group">
            <label>Pressure (mbar)</label>
            <input type="number" name="pressure_mbar" value="{pressure}" step="5" min="1" max="200">
        </div>
        <div class="control-group">
            <label>Intensity (W/cm&sup2;)</label>
            <input type="number" name="intensity_w_cm2" value="{intensity:.0e}" step="1e13" min="1e13" max="1e16">
        </div>
        <div class="control-group">
            <label>Mirrors</label>
            <select name="n_mirrors">
                <option value="1" {_selected(n_mirrors, 1)}>1</option>
                <option value="2" {_selected(n_mirrors, 2)}>2</option>
                <option value="3" {_selected(n_mirrors, 3)}>3</option>
            </select>
        </div>
        <div class="control-group">
            <label>Filter</label>
            <select name="filter_material">
                <option value="Al" {_selected(filter_material, "Al")}>Aluminum</option>
                <option value="Zr" {_selected(filter_material, "Zr")}>Zirconium</option>
            </select>
        </div>
        <div class="control-group">
            <label>Filter (nm)</label>
            <input type="number" name="filter_thickness_nm" value="{filter_thickness}" step="50" min="50" max="500">
        </div>
        <button type="submit">Update Pipeline</button>
    </form>
    <div class="plot-container">
        {plot_html}
    </div>
</body>
</html>"""
