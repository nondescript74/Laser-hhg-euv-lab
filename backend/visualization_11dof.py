"""11 Degrees of Freedom writer head visualization.

Shows the physical structure of a single writer head: a 3D optical stack
built from 2D planar semiconductor layers, with Bragg diffractor mirrors,
vacuum containment, waveguides, polarizers, and optical switches.

The 11 DOF:
  1. X beam position (MEMS lateral steering)
  2. Y beam position (MEMS lateral steering)
  3. Z structure (3D optical stack from 2D planar layers)
  4. Time / dithering (temporal modulation and sub-pixel dither)
  5. Focus drilling (depth-of-focus control through focal stack)
  6. Polarization (integrated waveguide polarizer state)
  7. Phase modulation (across multiple emitter elements)
  8. Coherent temporal combination (coherent combination in time domain)
  9. Wavelength selection (Bragg grating tuning / architecture A/B/C)
  10. Dose integration (dwell time and pulse energy control)
  11. Thermal compensation (on-die sensor feedback loop)

Output PSF coupled via index-matching immersion fluid (matched NA for DUV/EUV).
"""

import plotly.graph_objects as go
import numpy as np

from backend.epistemic import (
    EPISTEMIC_CSS,
    EpistemicTier,
    SCOPE_BANNER_HTML,
    page_tier_panel,
)


_11DOF_TIER_PANEL = page_tier_panel(
    EpistemicTier.ARCHITECTURE,
    page_title="11-DOF Writer Head (architectural concept)",
    note=(
        "An <b>architecture-level</b> exploded-view of an integrated "
        "writer-head concept. Layer counts, thicknesses, and "
        "manufacturing claims are diagram-level; <b>nothing on this "
        "page measures a built device.</b> The HHG source that would "
        "feed such a head is modelled separately on the "
        "<a href='/api/hhg-analytical' style='color:#2563eb;'>HHG "
        "Calculators</a> page."
    ),
)


# ── DOF definitions ──────────────────────────────────────────────────

DEGREES_OF_FREEDOM = [
    {
        "id": 1, "name": "X Beam Position",
        "category": "Spatial",
        "component": "MEMS Tip/Tilt Mirror",
        "description": "Lateral beam steering in X via MEMS micromirror actuation",
        "range": "\u00b150 \u00b5m",
        "color": "#ef4444",
    },
    {
        "id": 2, "name": "Y Beam Position",
        "category": "Spatial",
        "component": "MEMS Tip/Tilt Mirror",
        "description": "Lateral beam steering in Y via MEMS micromirror actuation",
        "range": "\u00b150 \u00b5m",
        "color": "#f97316",
    },
    {
        "id": 3, "name": "Z Structure (3D Stack)",
        "category": "Spatial",
        "component": "Planar Layer Stack",
        "description": "3D optical structure built from 2D planar semiconductor layers",
        "range": "10\u2013200 \u00b5m stack height",
        "color": "#eab308",
    },
    {
        "id": 4, "name": "Time / Dithering",
        "category": "Temporal",
        "component": "Modulation Driver",
        "description": "Temporal modulation and sub-pixel dither patterns for resolution enhancement",
        "range": "1\u2013100 MHz modulation",
        "color": "#22c55e",
    },
    {
        "id": 5, "name": "Focus Drilling",
        "category": "Spatial",
        "component": "MEMS Piston + Varifocal",
        "description": "Depth-of-focus control through focal stack adjustment",
        "range": "\u00b12 \u00b5m DOF",
        "color": "#06b6d4",
    },
    {
        "id": 6, "name": "Polarization",
        "category": "Optical",
        "component": "Integrated Waveguide Polarizer",
        "description": "Polarization state control for resist interaction optimization",
        "range": "Linear / Circular / Elliptical",
        "color": "#3b82f6",
    },
    {
        "id": 7, "name": "Phase Modulation",
        "category": "Coherent",
        "component": "Phase Modulators (multi-element)",
        "description": "Phase control across multiple emitter elements for coherent PSF shaping",
        "range": "0\u20132\u03c0 per element",
        "color": "#6366f1",
    },
    {
        "id": 8, "name": "Coherent Temporal Combination",
        "category": "Coherent",
        "component": "Temporal Coherence Engine",
        "description": "Coherent combination of multiple exposures in time domain",
        "range": "1\u2013N pulse stacking",
        "color": "#8b5cf6",
    },
    {
        "id": 9, "name": "Wavelength Selection",
        "category": "Optical",
        "component": "Bragg Diffractor Grating",
        "description": "Wavelength selection via Bragg grating tuning (Arch A: 405nm, B: 248nm, C: 13.5nm)",
        "range": "13.5\u2013405 nm",
        "color": "#a855f7",
    },
    {
        "id": 10, "name": "Dose Integration",
        "category": "Temporal",
        "component": "Dwell Controller",
        "description": "Dwell time and pulse energy control for precise dose delivery",
        "range": "0.1\u2013100 mJ/cm\u00b2",
        "color": "#ec4899",
    },
    {
        "id": 11, "name": "Thermal Compensation",
        "category": "Feedback",
        "component": "On-Die Thermal Sensor + Loop",
        "description": "Real-time thermal feedback for drift compensation and stability",
        "range": "\u00b10.01\u00b0C stability",
        "color": "#f43f5e",
    },
]

# Physical layers in the writer head stack (bottom to top)
STACK_LAYERS = [
    {"name": "Silicon Substrate", "thickness_um": 50, "color": "#475569",
     "desc": "Foundation: standard 200/300mm Si wafer"},
    {"name": "CMOS Driver Layer", "thickness_um": 10, "color": "#64748b",
     "desc": "Modulation drivers, thermal sensors, control logic"},
    {"name": "Waveguide Layer", "thickness_um": 5, "color": "#3b82f6",
     "desc": "SiN/SiO\u2082 waveguides, optical routing, switches"},
    {"name": "Polarizer Layer", "thickness_um": 3, "color": "#6366f1",
     "desc": "Integrated wire-grid or metasurface polarizers"},
    {"name": "Phase Modulator Array", "thickness_um": 5, "color": "#8b5cf6",
     "desc": "Electro-optic phase shifters for coherent combination"},
    {"name": "Bragg Diffractor Mirrors", "thickness_um": 8, "color": "#a855f7",
     "desc": "Distributed Bragg reflectors for wavelength selection"},
    {"name": "Emitter Array (VCSEL/DUV/EUV)", "thickness_um": 6, "color": "#ef4444",
     "desc": "Surface-emitting source array (architecture-dependent)"},
    {"name": "MEMS Steering Layer", "thickness_um": 15, "color": "#f97316",
     "desc": "Micromirror/microlens array: tip, tilt, piston (XY + focus)"},
    {"name": "Vacuum Containment Shell", "thickness_um": 20, "color": "#1e293b",
     "desc": "Hermetic seal for EUV operation; optional for DUV/NIR"},
    {"name": "Immersion Coupling Interface", "thickness_um": 5, "color": "#06b6d4",
     "desc": "Index-matching fluid interface for NA optimization (DUV/EUV)"},
    {"name": "Output Micro-Objective", "thickness_um": 10, "color": "#22c55e",
     "desc": "Final focusing optic; delivers PSF to resist surface"},
]


def _build_stack_js():
    """Return JS + HTML for an interactive 3D exploded stack with explosion slider.

    The slider controls the gap between layers from 0 (collapsed physical)
    to 30 µm (fully exploded for inspection).  Plotly is driven client-side
    so the camera position is preserved when the slider moves.
    """
    import json

    # Pre-compute layer data for the JS side
    layers_json = json.dumps([
        {
            "name": l["name"],
            "thickness": l["thickness_um"],
            "color": l["color"],
            "desc": l["desc"],
        }
        for l in STACK_LAYERS
    ])

    return f"""
<div id="stack3d" style="width:100%;height:750px;"></div>
<div style="display:flex;align-items:center;gap:16px;padding:8px 24px;background:#fff;border:1px solid #e2e8f0;border-radius:8px;margin:8px 0;">
    <label style="font-size:13px;font-weight:700;color:#475569;white-space:nowrap;">Explode Z Gap:</label>
    <input id="gapSlider" type="range" min="0" max="40" value="15" step="1"
           style="flex:1;accent-color:#6366f1;">
    <span id="gapVal" style="font-size:13px;font-weight:600;color:#6366f1;min-width:55px;">15 \u00b5m</span>
</div>
<script>
(function() {{
    var layers = {layers_json};
    var xSize = 70, ySize = 70;
    var triI = [0,0,4,4,0,0,1,1,0,0,3,3];
    var triJ = [1,2,5,6,1,4,2,5,3,4,2,6];
    var triK = [2,3,6,7,4,5,5,6,4,7,6,7];

    function buildTraces(gap) {{
        var traces = [];
        var z = 0;
        var layerCenters = [];

        for (var i = 0; i < layers.length; i++) {{
            var t = layers[i].thickness;
            var z0 = z, z1 = z + t;
            var cx = (z0 + z1) / 2;
            layerCenters.push(cx);

            // Box mesh
            traces.push({{
                type: 'mesh3d',
                x: [-xSize/2, xSize/2, xSize/2, -xSize/2, -xSize/2, xSize/2, xSize/2, -xSize/2],
                y: [-ySize/2, -ySize/2, ySize/2, ySize/2, -ySize/2, -ySize/2, ySize/2, ySize/2],
                z: [z0, z0, z0, z0, z1, z1, z1, z1],
                i: triI, j: triJ, k: triK,
                color: layers[i].color,
                opacity: 0.75,
                name: layers[i].name,
                hovertext: '<b>' + layers[i].name + '</b><br>' + layers[i].desc +
                           '<br>Thickness: ' + t + ' \u00b5m<br>Z: ' + z0.toFixed(0) + '\u2013' + z1.toFixed(0) + ' \u00b5m',
                hoverinfo: 'text',
                flatshading: true,
                showlegend: true,
            }});

            // Label
            traces.push({{
                type: 'scatter3d',
                x: [xSize/2 + 12], y: [0], z: [cx],
                mode: 'text',
                text: [layers[i].name + ' (' + t + '\u00b5m)'],
                textfont: {{size: 10, color: layers[i].color}},
                textposition: 'middle right',
                hoverinfo: 'skip',
                showlegend: false,
            }});

            z = z1 + gap;
        }}

        // Beam path
        var beamZ = [], beamX = [], beamY = [];
        for (var bz = z + 25; bz >= -15; bz -= 2) {{
            beamZ.push(bz); beamX.push(0); beamY.push(0);
        }}
        traces.push({{
            type: 'scatter3d', x: beamX, y: beamY, z: beamZ,
            mode: 'lines', line: {{color: '#ef4444', width: 5}},
            name: 'Beam Path', hoverinfo: 'skip', showlegend: false,
        }});

        // PSF cone at bottom
        var coneZ = -15, coneR = 18;
        var cx2 = [], cy2 = [], cz2 = [];
        for (var a = 0; a <= 2*Math.PI; a += 0.22) {{
            cx2.push(coneR * Math.cos(a));
            cy2.push(coneR * Math.sin(a));
            cz2.push(coneZ);
        }}
        traces.push({{
            type: 'scatter3d', x: cx2, y: cy2, z: cz2,
            mode: 'lines', line: {{color: '#22c55e', width: 3, dash: 'dash'}},
            name: 'PSF Output', hoverinfo: 'skip', showlegend: false,
        }});
        for (var ca = 0; ca < 4; ca++) {{
            var ang = ca * Math.PI / 2;
            traces.push({{
                type: 'scatter3d',
                x: [0, coneR * Math.cos(ang)],
                y: [0, coneR * Math.sin(ang)],
                z: [0, coneZ],
                mode: 'lines', line: {{color: '#22c55e', width: 1, dash: 'dash'}},
                hoverinfo: 'skip', showlegend: false,
            }});
        }}

        return {{traces: traces, maxZ: z + 30}};
    }}

    function render(gap) {{
        var result = buildTraces(gap);
        Plotly.react('stack3d', result.traces, {{
            scene: {{
                xaxis: {{title: 'X (\u00b5m)', range: [-90, 140]}},
                yaxis: {{title: 'Y (\u00b5m)', range: [-60, 60]}},
                zaxis: {{title: 'Z stack (\u00b5m)', range: [-25, result.maxZ]}},
                aspectmode: 'manual',
                aspectratio: {{x: 1.5, y: 0.8, z: 1.6}},
                camera: {{eye: {{x: 1.5, y: -1.0, z: 0.7}}}},
            }},
            height: 750, width: 1100,
            title: 'Writer Head: 3D Optical Stack (' + (gap === 0 ? 'Physical' : 'Exploded ' + gap + '\u00b5m gap') + ')',
            margin: {{t: 50, b: 20}},
        }});
    }}

    // Initial render at default gap
    render(15);

    // Slider interaction
    var slider = document.getElementById('gapSlider');
    var valLabel = document.getElementById('gapVal');
    slider.addEventListener('input', function() {{
        var g = parseInt(this.value);
        valLabel.textContent = g + ' \u00b5m';
        render(g);
    }});
}})();
</script>"""


def _build_dof_radar_figure():
    """Build radar/spider chart of the 11 DOF categories."""
    categories = [d["name"] for d in DEGREES_OF_FREEDOM]
    # Normalize "capability" as a visualization aid (all at max for now)
    values = [1.0] * 11
    values.append(values[0])  # close the polygon
    cats = categories + [categories[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=cats,
        fill="toself",
        fillcolor="rgba(99, 102, 241, 0.15)",
        line=dict(color="#6366f1", width=2),
        name="11 DOF System",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False, range=[0, 1.3]),
            angularaxis=dict(tickfont=dict(size=10)),
        ),
        height=500, width=600,
        title="11 Degrees of Freedom",
        showlegend=False,
        margin=dict(t=60, b=20),
    )
    return fig


def _dof_cards_html():
    """Build HTML cards for each DOF."""
    cards = ""
    cat_icons = {
        "Spatial": "\U0001F4CD",
        "Temporal": "\u23F1\uFE0F",
        "Optical": "\U0001F4A0",
        "Coherent": "\U0001F300",
        "Feedback": "\U0001F504",
    }
    for d in DEGREES_OF_FREEDOM:
        icon = cat_icons.get(d["category"], "")
        cards += f"""<div class="dof-card" style="border-left: 4px solid {d['color']};">
            <div class="dof-header">
                <span class="dof-id" style="background:{d['color']};">DOF {d['id']}</span>
                <span class="dof-cat">{icon} {d['category']}</span>
            </div>
            <h3>{d['name']}</h3>
            <p class="dof-desc">{d['description']}</p>
            <div class="dof-meta">
                <span class="dof-component">{d['component']}</span>
                <span class="dof-range">{d['range']}</span>
            </div>
        </div>"""
    return f'<div class="dof-grid">{cards}</div>'


def _stack_table_html():
    """Build HTML table of the physical layer stack."""
    rows = ""
    z = 0
    for layer in STACK_LAYERS:
        rows += f"""<tr>
            <td><span class="layer-dot" style="background:{layer['color']};"></span>{layer['name']}</td>
            <td>{layer['thickness_um']} \u00b5m</td>
            <td>{z}\u2013{z + layer['thickness_um']} \u00b5m</td>
            <td>{layer['desc']}</td>
        </tr>"""
        z += layer["thickness_um"]
    total = sum(l["thickness_um"] for l in STACK_LAYERS)
    rows += f"""<tr style="font-weight:700; background:#f1f5f9;">
        <td>Total Stack</td><td>{total} \u00b5m</td><td>0\u2013{total} \u00b5m</td>
        <td>Complete writer head: 2D planar fab \u2192 3D optical structure</td>
    </tr>"""
    return f"""<table class="data-table">
        <thead><tr><th>Layer</th><th>Thickness</th><th>Z Position</th><th>Function</th></tr></thead>
        <tbody>{rows}</tbody>
    </table>"""


# ── Master HTML builder ──────────────────────────────────────────────

_NAV = """
<div class="nav">
    <a href="/api/visualize">2D Process Sim</a>
    <a href="/api/visualize-3d">3D Pipeline</a>
    <a href="/api/wavelength-bridge">Wavelength Bridge</a>
    <a href="/api/hhg-analytical">HHG Calculators</a>
    <a href="/api/fleet-dashboard">Platform Economics</a>
    <a href="/api/multihead">Multi-Head Array</a>
    <a href="/api/psf-synthesis">PSF Synthesis</a>
    <a href="/api/writer-head" class="active">11-DOF Writer Head</a>
</div>"""

_CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f8fafc; color: #1e293b; }
.nav { background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }
.nav a { color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }
.nav a:hover { background: #2a2a4e; }
.nav a.active { background: #2563eb; color: #fff; }
.section { padding: 20px 24px; }
.section h2 { font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 12px 0; border-bottom: 2px solid #2563eb; padding-bottom: 6px; display: inline-block; }
.plot-container { padding: 0 8px; }
.two-col { display: flex; gap: 24px; flex-wrap: wrap; }
.two-col > * { flex: 1; min-width: 400px; }

.dof-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; margin-top: 12px; }
.dof-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px 16px;
    transition: transform 0.15s, box-shadow 0.15s;
}
.dof-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.06); }
.dof-header { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.dof-id { color: #fff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 10px; }
.dof-cat { font-size: 11px; color: #64748b; }
.dof-card h3 { margin: 0 0 4px 0; font-size: 14px; color: #0f172a; }
.dof-desc { font-size: 12px; color: #64748b; margin: 0 0 8px 0; line-height: 1.4; }
.dof-meta { display: flex; gap: 8px; flex-wrap: wrap; }
.dof-meta span { font-size: 11px; background: #f1f5f9; padding: 2px 8px; border-radius: 10px; color: #475569; }
.dof-component { font-weight: 600; }

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 8px; }
.data-table th { background: #f1f5f9; padding: 10px 12px; text-align: left; font-weight: 700; color: #475569; border-bottom: 2px solid #e2e8f0; }
.data-table td { padding: 10px 12px; border-bottom: 1px solid #e2e8f0; }
.data-table tr:hover { background: #f8fafc; }
.layer-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }

.callout-blue {
    background: #eff6ff; border: 1px solid #93c5fd; border-radius: 8px;
    padding: 14px 20px; margin: 16px 0; font-size: 13px; color: #1e40af; line-height: 1.5;
}
.callout-blue b { color: #1e3a8a; }

.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    color: #fff; padding: 32px 40px; text-align: center;
}
.hero-banner h1 { font-size: 28px; margin: 0 0 8px 0; font-weight: 800; }
.hero-banner p { font-size: 14px; color: #c7d2fe; margin: 0; max-width: 800px; margin: 0 auto; line-height: 1.5; }
.hero-stats { display: flex; justify-content: center; gap: 40px; margin-top: 20px; flex-wrap: wrap; }
.hero-stat { text-align: center; }
.hero-stat .value { font-size: 32px; font-weight: 800; color: #a5b4fc; }
.hero-stat .label { font-size: 11px; color: #818cf8; text-transform: uppercase; letter-spacing: 1px; }
"""


def build_11dof_html():
    """Build the complete 11-DOF writer head visualization page."""
    stack_js_html = _build_stack_js()

    radar_fig = _build_dof_radar_figure()
    radar_html = radar_fig.to_html(full_html=False, include_plotlyjs=False)

    dof_cards = _dof_cards_html()
    stack_table = _stack_table_html()

    total_thickness = sum(l["thickness_um"] for l in STACK_LAYERS)

    return f"""<!DOCTYPE html>
<html>
<head>
    <title>11-DOF Writer Head Architecture [ARCHITECTURE]</title>
    <script src="plotly.min.js"></script>
    <style>{_CSS}</style>
    <style>{EPISTEMIC_CSS}</style>
</head>
<body>
    {_NAV}
    {SCOPE_BANNER_HTML}
    {_11DOF_TIER_PANEL}

    <div class="hero-banner">
        <h1>11 Degrees of Freedom Writer Head</h1>
        <p>
            3D optical structure built from 2D planar semiconductor processes.
            Each writer head integrates beam propagation, optical switches, waveguides,
            polarizers, Bragg diffractor mirrors, and vacuum containment into a single
            ~2\u00d72mm die. Output PSF coupled via index-matching immersion fluid.
        </p>
        <div class="hero-stats">
            <div class="hero-stat">
                <div class="value">11</div>
                <div class="label">Degrees of Freedom</div>
            </div>
            <div class="hero-stat">
                <div class="value">{len(STACK_LAYERS)}</div>
                <div class="label">Functional Layers</div>
            </div>
            <div class="hero-stat">
                <div class="value">{total_thickness} \u00b5m</div>
                <div class="label">Total Stack Height</div>
            </div>
            <div class="hero-stat">
                <div class="value">1,000+</div>
                <div class="label">Heads per Fab Run</div>
            </div>
        </div>
    </div>

    <div class="callout-blue">
        <b>Architectural manufacturing concept.</b> Layer choices and
        process notes are illustrative; the page asserts no built
        prototype. Vacuum containment is an architectural requirement
        for EUV operation, not a demonstrated subsystem of this repo.
        For the upstream HHG source physics that would feed such a
        head, see the <a href="/api/hhg-analytical" style="color:#2563eb;">HHG
        Calculators</a> and <a href="/api/wavelength-bridge" style="color:#2563eb;">Wavelength
        Bridge</a> pages.
    </div>

    <div class="section">
        <h2>11 Degrees of Freedom</h2>
        <div class="two-col">
            <div class="plot-container">{radar_html}</div>
            <div>
                <p style="font-size:13px; color:#64748b; line-height:1.6; margin-top:0;">
                    The writer head is an <b>11-dimensional control system</b>. Spatial DOF (XY beam, Z stack, focus)
                    define where the beam goes. Temporal DOF (dithering, dose integration, coherent combination)
                    define when and how energy is delivered. Optical DOF (polarization, phase, wavelength)
                    shape the PSF. Feedback (thermal) closes the loop for stability.
                    <br><br>
                    This multi-dimensional control enables <b>PSF synthesis</b> \u2014 the ability to compose
                    arbitrary point-spread functions from the combined action of all 11 DOF, far beyond
                    what a fixed-optics single-pass system can achieve.
                </p>
            </div>
        </div>
        {dof_cards}
    </div>

    <div class="section">
        <h2>Physical Layer Stack (3D from 2D Planar)</h2>
        <p style="font-size:13px; color:#64748b; margin:0 0 8px 0;">
            Each layer is deposited/bonded using standard semiconductor processes.
            The complete stack forms a self-contained optical engine with integrated
            emitters, steering, waveguides, polarizers, Bragg mirrors, and vacuum shell.
        </p>
        <div class="plot-container">{stack_js_html}</div>
        {stack_table}
    </div>
</body>
</html>"""
