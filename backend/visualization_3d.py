"""3D interactive visualization of the integrated multi-head writer platform.

Three zoom levels let the viewer drill from desk-sized platform down to a
single 11-DOF writer head:

  Platform  -- enclosure + modules + packages + wafer + beam shower
  Package   -- one 33x33 mm package with 4x4 head grid + individual beams
  Head      -- single ~2x2 mm writer head with simplified layer stack + beam

The zoom slider drives Plotly.react() client-side so the camera is preserved
between level transitions.  HHG physics controls (gas, pressure, mirrors,
filter) still require a server round-trip via the form.
"""

import json
import numpy as np
import plotly.graph_objects as go

from backend.visualization_11dof import STACK_LAYERS


# -- Helpers for the static Plotly figure (keeps tests working) --------

def _cylinder_mesh(z_start, z_end, radius, color, name, opacity=0.6, n_seg=24):
    """Generate a cylinder as a Mesh3d trace along the z-axis."""
    theta = np.linspace(0, 2 * np.pi, n_seg, endpoint=False)
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)

    x = np.concatenate([radius * cos_t, radius * cos_t, [0, 0]])
    y = np.concatenate([radius * sin_t, radius * sin_t, [0, 0]])
    z = np.concatenate([np.full(n_seg, z_start), np.full(n_seg, z_end),
                        [z_start, z_end]])

    center_bot = 2 * n_seg
    center_top = 2 * n_seg + 1

    ii, jj, kk = [], [], []
    for s in range(n_seg):
        s_next = (s + 1) % n_seg
        ii += [s, s, s + n_seg]
        jj += [s_next, s + n_seg, s_next + n_seg]
        kk += [s + n_seg, s_next, s_next]
        ii.append(center_bot); jj.append(s); kk.append(s_next)
        ii.append(center_top); jj.append(s_next + n_seg); kk.append(s + n_seg)

    return go.Mesh3d(
        x=x, y=y, z=z, i=ii, j=jj, k=kk,
        color=color, opacity=opacity,
        name=name, hoverinfo="name", flatshading=True,
    )


def _disc_mesh(z_pos, radius, color, name, opacity=0.8, n_seg=24):
    return _cylinder_mesh(z_pos, z_pos + 0.3, radius, color, name, opacity, n_seg)


def _beam_surface(z_vals, r_envelope, color_transition_z, n_ang=16):
    theta = np.linspace(0, 2 * np.pi, n_ang)
    traces = []
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
            x=X, y=Y, z=Z, surfacecolor=np.ones_like(Z),
            colorscale=[[0, color], [1, color]], showscale=False,
            name=beam_name, hoverinfo="name", opacity=0.35,
        ))
    traces.append(go.Scatter3d(
        x=np.zeros_like(z_vals), y=np.zeros_like(z_vals), z=z_vals,
        mode="lines", line=dict(color="white", width=2),
        name="Optical Axis", hoverinfo="name",
    ))
    return traces


def _render_gas_supply_lines(gas_cell):
    traces = []
    supply_lines = gas_cell.properties.get("supply_lines", [])
    pressure = gas_cell.properties.get("pressure_mbar", 30)
    gas_type = gas_cell.properties.get("gas_type", "Ar")
    for line_info in supply_lines:
        lx, ly, lz = line_info["x"], line_info["y"], line_info["z"]
        label = line_info["label"]
        traces.append(go.Scatter3d(
            x=[0, lx], y=[0, ly], z=[lz, lz],
            mode="lines+markers",
            line=dict(color="#888888", width=6),
            marker=dict(size=[0, 5], color=["#888888", "#dd6633"]),
            name=label,
            hovertext=f"{label}<br>{gas_type} @ {pressure:.0f} mbar",
            hoverinfo="text",
        ))
        traces.append(go.Scatter3d(
            x=[lx * 1.3], y=[ly * 1.3], z=[lz],
            mode="text", text=[label],
            textfont=dict(size=10, color="#555555"),
            hoverinfo="skip", showlegend=False,
        ))
    return traces


def _render_power_annotations(power_budget):
    traces = []
    x_vals, y_vals, z_vals, texts = [], [], [], []
    for entry in power_budget:
        z_vals.append(entry["z_mid"])
        x_vals.append(-85)
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
        mode="text", text=texts,
        textfont=dict(size=10, color="#222222"),
        hoverinfo="text", showlegend=False,
    ))
    return traces


def build_3d_pipeline_figure(pipeline, params=None):
    """Build complete 3D optical pipeline figure (static, for tests)."""
    fig = go.Figure()

    for comp in pipeline.components:
        if comp.component_type in ("wafer", "filter"):
            fig.add_trace(_disc_mesh(
                comp.z_start, comp.radius, comp.color, comp.name, opacity=0.7))
        elif comp.component_type == "gas_cell":
            fig.add_trace(_cylinder_mesh(
                comp.z_start, comp.z_end, comp.radius,
                comp.color, comp.name, opacity=0.3))
            for trace in _render_gas_supply_lines(comp):
                fig.add_trace(trace)
        elif comp.component_type == "mirror":
            fig.add_trace(_disc_mesh(
                comp.z_start, comp.radius, comp.color, comp.name, opacity=0.8))
        else:
            fig.add_trace(_cylinder_mesh(
                comp.z_start, comp.z_end, comp.radius,
                comp.color, comp.name, opacity=0.6))

    z_vals, x_c, y_c, r_env, color_z = pipeline.get_beam_path()
    for trace in _beam_surface(z_vals, r_env, color_z):
        fig.add_trace(trace)

    budget = pipeline.compute_power_budget()
    for trace in _render_power_annotations(budget):
        fig.add_trace(trace)

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
            hoverinfo="skip", showlegend=False,
        ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title="X (mm)", range=[-100, 100], showgrid=True, gridcolor="#eee"),
            yaxis=dict(title="Y (mm)", range=[-30, 30], showgrid=True, gridcolor="#eee"),
            zaxis=dict(title="Z \u2014 Optical Axis (mm)", range=[-5, 140], showgrid=True, gridcolor="#eee"),
            aspectmode="manual",
            aspectratio=dict(x=1.8, y=0.5, z=1.2),
            camera=dict(eye=dict(x=2.0, y=0.6, z=0.3), up=dict(x=0, y=0, z=1)),
            bgcolor="#fafafa",
        ),
        title=dict(text=(
            "HHG Generation Chain (Driver \u2192 Gas Cell \u2192 Filter \u2192 Mirror \u2192 Application)"
            "  \u2014  [ARCHITECTURE]"
        )),
        height=900, width=1500,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(255,255,255,0.8)"),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


# -- Platform hierarchy data for client-side JS -----------------------

def _get_platform_geometry(pipeline, params):
    """Compute all geometry data for the three-level 3D JS visualization."""
    gas_cell = next((c for c in pipeline.components if c.component_type == "gas_cell"), None)
    hhg_info = {}
    if gas_cell:
        p = gas_cell.properties
        hhg_info = {
            "gas_type": p.get("gas_type", "Ar"),
            "pressure_mbar": p.get("pressure_mbar", 30),
            "ip_ev": round(p.get("ionization_potential_ev", 0), 1),
            "cutoff_ev": round(p.get("cutoff_energy_ev", 0), 0),
            "target_harmonic": p.get("target_harmonic", 59),
            "euv_wavelength_nm": round(p.get("euv_wavelength_nm", 13.5), 1),
        }

    budget = pipeline.compute_power_budget()
    power_data = [
        {"name": b["name"], "z_mid": b["z_mid"], "power_out": b["power_out"]}
        for b in budget
    ]

    grouped_layers = [
        {"name": "CMOS + Waveguide", "thickness": 65, "color": "#64748b",
         "desc": "Si substrate, CMOS drivers, SiN waveguides, optical routing"},
        {"name": "Optical Core", "thickness": 22, "color": "#8b5cf6",
         "desc": "Polarizers, phase modulators, Bragg diffractors, emitter array"},
        {"name": "MEMS + Vacuum", "thickness": 35, "color": "#f97316",
         "desc": "Micromirror steering array, hermetic vacuum containment shell"},
        {"name": "Output Optics", "thickness": 15, "color": "#22c55e",
         "desc": "Immersion coupling interface, final micro-objective"},
    ]

    full_layers = [
        {"name": l["name"], "thickness": l["thickness_um"], "color": l["color"], "desc": l["desc"]}
        for l in STACK_LAYERS
    ]

    return {
        "platform": {
            "width_mm": 1400, "depth_mm": 700, "height_mm": 400,
            "modules": 1, "packages_per_module": 10,
            "heads_per_package": 16, "head_rows": 4, "head_cols": 4,
            "package_mm": 33, "head_mm": 2,
            "total_heads": 160,
        },
        "hhg": hhg_info,
        "power_budget": power_data,
        "grouped_layers": grouped_layers,
        "full_layers": full_layers,
    }


def _build_platform_js(geometry_json):
    """Return JS that drives the three-level 3D interactive visualization."""
    return (
        '<div id="platform3d" style="width:100%;height:780px;"></div>\n'
        '<div style="display:flex;align-items:center;gap:16px;padding:10px 24px;'
        'background:#fff;border:1px solid #e2e8f0;border-radius:8px;margin:8px 24px;">\n'
        '    <label style="font-size:13px;font-weight:700;color:#475569;white-space:nowrap;">Zoom Level:</label>\n'
        '    <span id="zoomLabel" style="font-size:12px;color:#6366f1;font-weight:600;min-width:90px;">Platform</span>\n'
        '    <input id="zoomSlider" type="range" min="0" max="2" value="0" step="1"'
        ' style="flex:1;accent-color:#6366f1;">\n'
        '    <div style="display:flex;gap:16px;font-size:11px;color:#94a3b8;">\n'
        '        <span>0 = Platform</span><span>1 = Package</span><span>2 = Writer Head</span>\n'
        '    </div>\n'
        '</div>\n'
        '<script>\n'
        '(function() {\n'
        'var G = ' + geometry_json + ';\n'
        'var P = G.platform;\n'
        'var triI = [0,0,4,4,0,0,1,1,0,0,3,3];\n'
        'var triJ = [1,2,5,6,1,4,2,5,3,4,2,6];\n'
        'var triK = [2,3,6,7,4,5,5,6,4,7,6,7];\n'
        '\n'
        'function box(cx,cy,cz, sx,sy,sz, color, name, desc, opacity) {\n'
        '    var hx=sx/2, hy=sy/2;\n'
        '    return {\n'
        '        type:"mesh3d",\n'
        '        x:[cx-hx,cx+hx,cx+hx,cx-hx,cx-hx,cx+hx,cx+hx,cx-hx],\n'
        '        y:[cy-hy,cy-hy,cy+hy,cy+hy,cy-hy,cy-hy,cy+hy,cy+hy],\n'
        '        z:[cz,cz,cz,cz,cz+sz,cz+sz,cz+sz,cz+sz],\n'
        '        i:triI,j:triJ,k:triK,\n'
        '        color:color,opacity:opacity||0.6,\n'
        '        name:name,\n'
        '        hovertext:"<b>"+name+"</b>"+(desc?"<br>"+desc:""),\n'
        '        hoverinfo:"text",flatshading:true,showlegend:true\n'
        '    };\n'
        '}\n'
        '\n'
        'function wireBox(cx,cy,cz,sx,sy,sz,color,name) {\n'
        '    var hx=sx/2,hy=sy/2;\n'
        '    var c=[[cx-hx,cy-hy,cz],[cx+hx,cy-hy,cz],[cx+hx,cy+hy,cz],[cx-hx,cy+hy,cz],\n'
        '           [cx-hx,cy-hy,cz+sz],[cx+hx,cy-hy,cz+sz],[cx+hx,cy+hy,cz+sz],[cx-hx,cy+hy,cz+sz]];\n'
        '    var edges=[[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]];\n'
        '    var x=[],y=[],z=[];\n'
        '    edges.forEach(function(e){\n'
        '        x.push(c[e[0]][0],c[e[1]][0],null);\n'
        '        y.push(c[e[0]][1],c[e[1]][1],null);\n'
        '        z.push(c[e[0]][2],c[e[1]][2],null);\n'
        '    });\n'
        '    return {type:"scatter3d",x:x,y:y,z:z,mode:"lines",\n'
        '             line:{color:color,width:2},name:name,hoverinfo:"name",showlegend:true};\n'
        '}\n'
        '\n'
        'function disc(cx,cy,cz,radius,color,name,n) {\n'
        '    n=n||32;\n'
        '    var x=[cx],y=[cy],z=[cz],ii=[],jj=[],kk=[];\n'
        '    for(var a=0;a<n;a++){\n'
        '        var th=2*Math.PI*a/n;\n'
        '        x.push(cx+radius*Math.cos(th));\n'
        '        y.push(cy+radius*Math.sin(th));\n'
        '        z.push(cz);\n'
        '        ii.push(0);jj.push(a+1);kk.push(a<n-1?a+2:1);\n'
        '    }\n'
        '    return {type:"mesh3d",x:x,y:y,z:z,i:ii,j:jj,k:kk,\n'
        '             color:color,opacity:0.5,name:name,hoverinfo:"name",flatshading:true,showlegend:true};\n'
        '}\n'
        '\n'
        '// --- LEVEL 0: Platform ---\n'
        'function buildPlatform() {\n'
        '    var t = [];\n'
        '    var pw=P.width_mm, pd=P.depth_mm, ph=P.height_mm;\n'
        '    t.push(wireBox(0,0,0,pw,pd,ph,"#475569","Platform Enclosure"));\n'
        '    var mz=ph*0.55, mw=pw*0.85, md=pd*0.7;\n'
        '    t.push(box(0,0,mz,mw,md,8,"#16a34a","Module Board",\n'
        '        P.packages_per_module+" packages, cooling + control",0.35));\n'
        '    var nPkg=P.packages_per_module;\n'
        '    var pkgSize=P.package_mm;\n'
        '    var pkgSpacing=pkgSize*2.8;\n'
        '    var cols=5,rows=2;\n'
        '    var startX=-(cols-1)*pkgSpacing/2;\n'
        '    var startY=-(rows-1)*pkgSpacing/2;\n'
        '    for(var r=0;r<rows;r++){\n'
        '        for(var c=0;c<cols;c++){\n'
        '            var idx=r*cols+c;\n'
        '            if(idx>=nPkg) break;\n'
        '            var px=startX+c*pkgSpacing;\n'
        '            var py=startY+r*pkgSpacing;\n'
        '            t.push(box(px,py,mz+8,pkgSize,pkgSize,5,"#f97316",\n'
        '                "Package "+(idx+1),"4\\u00d74 = 16 writer heads, 33\\u00d733mm",0.7));\n'
        '            t.push({type:"scatter3d",\n'
        '                x:[px,px],y:[py,py],z:[mz+8,-60],\n'
        '                mode:"lines",line:{color:"rgba(139,92,246,0.4)",width:3},\n'
        '                hoverinfo:"skip",showlegend:false});\n'
        '        }\n'
        '    }\n'
        '    t.push(disc(0,0,-80,150,"#22c55e","Application Plane (concept)"));\n'
        '    t.push(box(0,0,-95,340,340,10,"#64748b","XY Stage (concept)","Architectural illustration only",0.25));\n'
        '    t.push({type:"scatter3d",x:[pw/2+40],y:[0],z:[ph/2],mode:"text",\n'
        '        text:["<b>Integrated Platform [ARCHITECTURE]</b><br>"+P.total_heads+" writer-head concept slots<br>"+\n'
        '              nPkg+" packages<br>Desk-sized: "+(pw/10).toFixed(0)+"\\u00d7"+(pd/10).toFixed(0)+" cm"],\n'
        '        textfont:{size:11,color:"#1e40af"},hoverinfo:"skip",showlegend:false});\n'
        '    t.push({type:"scatter3d",x:[0],y:[0],z:[-110],mode:"text",\n'
        '        text:["<b>Application Plane (concept)</b><br>Architectural illustration; no wafer-exposure claim"],\n'
        '        textfont:{size:11,color:"#16a34a"},hoverinfo:"skip",showlegend:false});\n'
        '    return t;\n'
        '}\n'
        '\n'
        '// --- LEVEL 1: Package ---\n'
        'function buildPackage() {\n'
        '    var t = [];\n'
        '    var pkgSize=P.package_mm;\n'
        '    // Package substrate\n'
        '    t.push(box(0,0,0,pkgSize,pkgSize,2,"#ea580c","Package Substrate",\n'
        '        "Silicon interposer + flip-chip bonding",0.4));\n'
        '    var headSize=P.head_mm;\n'
        '    var spacing=pkgSize/(P.head_rows+1);\n'
        '    // Head 1 position (top-left) — will show exploded cutaway\n'
        '    var h1x=-pkgSize/2+spacing, h1y=-pkgSize/2+spacing;\n'
        '    // All heads except Head 1\n'
        '    for(var r=0;r<P.head_rows;r++){\n'
        '        for(var c=0;c<P.head_cols;c++){\n'
        '            var hx=-pkgSize/2+spacing*(c+1);\n'
        '            var hy=-pkgSize/2+spacing*(r+1);\n'
        '            var idx=r*P.head_cols+c;\n'
        '            if(idx===0) continue; // skip Head 1, drawn as exploded\n'
        '            t.push(box(hx,hy,2,headSize,headSize,1.5,"#6366f1",\n'
        '                "Head "+(idx+1),"11-DOF writer head, ~2\\u00d72mm die",0.8));\n'
        '            t.push({type:"scatter3d",\n'
        '                x:[hx,hx],y:[hy,hy],z:[2,-25],\n'
        '                mode:"lines",line:{color:"rgba(139,92,246,0.3)",width:1.5},\n'
        '                hoverinfo:"skip",showlegend:false});\n'
        '            t.push({type:"scatter3d",\n'
        '                x:[hx],y:[hy],z:[-25],mode:"markers",\n'
        '                marker:{size:3,color:"#22c55e",symbol:"circle"},\n'
        '                hovertext:"Exposure field, Head "+(idx+1),hoverinfo:"text",showlegend:false});\n'
        '        }\n'
        '    }\n'
        '    // --- Head 1: exploded 11-DOF cutaway ---\n'
        '    var eX=h1x, eY=h1y, eZ=3; // start above package\n'
        '    var layers = G.grouped_layers;\n'
        '    var scale=0.6; // scale down to fit on package\n'
        '    var lw=headSize*1.8, lh=headSize*1.8;\n'
        '    var gap=0.8;\n'
        '    var dofLabels = [\n'
        '        {color:"#64748b",dofs:"DOF 11: Thermal sensors\\nDOF 6-7: Waveguide routing"},\n'
        '        {color:"#8b5cf6",dofs:"DOF 6: Polarization\\nDOF 7: Phase modulation\\nDOF 9: Wavelength (Bragg)"},\n'
        '        {color:"#f97316",dofs:"DOF 1-2: XY beam steering (MEMS)\\nDOF 5: Focus drilling (piston)"},\n'
        '        {color:"#22c55e",dofs:"DOF 10: Dose integration\\nDOF 3: Z structure\\nDOF 4: Temporal dithering\\nDOF 8: Coherent combination"}\n'
        '    ];\n'
        '    var ez=eZ;\n'
        '    for(var i=0;i<layers.length;i++){\n'
        '        var lt=layers[i].thickness*scale*0.03; // compressed thickness\n'
        '        t.push(box(eX,eY,ez,lw,lh,lt,layers[i].color,layers[i].name,\n'
        '            layers[i].desc+"\\n"+dofLabels[i].dofs,0.75));\n'
        '        // Leader line from layer to DOF label on the right\n'
        '        var labelX=pkgSize/2+6;\n'
        '        t.push({type:"scatter3d",\n'
        '            x:[eX+lw/2,labelX-1],y:[eY,eY],z:[ez+lt/2,ez+lt/2],\n'
        '            mode:"lines",line:{color:layers[i].color,width:1.5,dash:"dot"},\n'
        '            hoverinfo:"skip",showlegend:false});\n'
        '        t.push({type:"scatter3d",x:[labelX],y:[eY],z:[ez+lt/2],mode:"text",\n'
        '            text:["<b>"+layers[i].name+"</b><br>"+dofLabels[i].dofs.replace(/\\n/g,"<br>")],\n'
        '            textfont:{size:8,color:layers[i].color},textposition:"middle right",\n'
        '            hoverinfo:"skip",showlegend:false});\n'
        '        ez+=lt+gap;\n'
        '    }\n'
        '    // Beam from Head 1 exploded stack\n'
        '    t.push({type:"scatter3d",x:[eX,eX],y:[eY,eY],z:[ez+2,-25],\n'
        '        mode:"lines",line:{color:"#ef4444",width:3},\n'
        '        name:"Head 1 beam",hoverinfo:"name"});\n'
        '    t.push({type:"scatter3d",x:[eX],y:[eY],z:[-25],mode:"markers",\n'
        '        marker:{size:5,color:"#22c55e",symbol:"circle"},\n'
        '        hovertext:"Exposure field, Head 1",hoverinfo:"text",showlegend:false});\n'
        '    // "Head 1" label\n'
        '    t.push({type:"scatter3d",x:[eX],y:[eY-3],z:[ez+3],mode:"text",\n'
        '        text:["<b>Head 1 (exploded)</b><br>~2\\u00d72 mm die<br>11 DOF per head"],\n'
        '        textfont:{size:9,color:"#6366f1"},hoverinfo:"skip",showlegend:false});\n'
        '    // Application plane (illustrative; no wafer-exposure claim)\n'
        '    t.push(disc(0,0,-26,pkgSize*0.6,"#22c55e","Application Plane (concept)"));\n'
        '    // Signal routing\n'
        '    var routeX=[],routeY=[],routeZ=[];\n'
        '    for(var r=0;r<P.head_rows;r++){\n'
        '        var hy2=-pkgSize/2+spacing*(r+1);\n'
        '        routeX.push(-pkgSize/2-2,pkgSize/2+2,null);\n'
        '        routeY.push(hy2,hy2,null);\n'
        '        routeZ.push(1.8,1.8,null);\n'
        '    }\n'
        '    t.push({type:"scatter3d",x:routeX,y:routeY,z:routeZ,mode:"lines",\n'
        '        line:{color:"#fbbf24",width:1.5},name:"Signal routing",hoverinfo:"name"});\n'
        '    // Package label\n'
        '    t.push({type:"scatter3d",x:[-pkgSize/2-6],y:[0],z:[5],mode:"text",\n'
        '        text:["<b>33\\u00d733 mm Package</b><br>4\\u00d74 = 16 writer heads<br>"+\n'
        '              "Flip-chip on Si interposer<br>~1,000 heads per fab run"],\n'
        '        textfont:{size:10,color:"#ea580c"},hoverinfo:"skip",showlegend:false});\n'
        '    // 11-DOF summary\n'
        '    t.push({type:"scatter3d",x:[0],y:[0],z:[-32],mode:"text",\n'
        '        text:["<b>16 parallel beams \\u2022 16 \\u00d7 11 = 176 DOF per package</b><br>"+\n'
        '              "XY steering \\u2022 Focus \\u2022 Polarization \\u2022 Phase \\u2022 Wavelength \\u2022 Dose \\u2022 Thermal"],\n'
        '        textfont:{size:9,color:"#6366f1"},hoverinfo:"skip",showlegend:false});\n'
        '    return t;\n'
        '}\n'
        '\n'
        '// --- LEVEL 2: Writer Head ---\n'
        'function buildHead() {\n'
        '    var t = [];\n'
        '    var layers = G.grouped_layers;\n'
        '    var xSize=30, ySize=30;\n'
        '    var z = 0;\n'
        '    for(var i=0;i<layers.length;i++) {\n'
        '        var th=layers[i].thickness;\n'
        '        var z0=z, z1=z+th;\n'
        '        t.push(box(0,0,z0,xSize,ySize,th,layers[i].color,layers[i].name,\n'
        '            layers[i].desc,0.7));\n'
        '        t.push({type:"scatter3d",x:[xSize/2+8],y:[0],z:[(z0+z1)/2],mode:"text",\n'
        '            text:[layers[i].name+" ("+th+"\\u00b5m)"],\n'
        '            textfont:{size:10,color:layers[i].color},textposition:"middle right",\n'
        '            hoverinfo:"skip",showlegend:false});\n'
        '        z = z1 + 3;\n'
        '    }\n'
        '    var beamZ=[],beamX=[],beamY=[];\n'
        '    for(var bz=z+20;bz>=-20;bz-=1){\n'
        '        beamZ.push(bz);beamX.push(0);beamY.push(0);\n'
        '    }\n'
        '    t.push({type:"scatter3d",x:beamX,y:beamY,z:beamZ,mode:"lines",\n'
        '        line:{color:"#ef4444",width:5},name:"Beam Path",hoverinfo:"skip",showlegend:true});\n'
        '    var coneZ=-20, coneR=12;\n'
        '    var cx=[],cy=[],cz=[];\n'
        '    for(var a=0;a<=2*Math.PI;a+=0.2){\n'
        '        cx.push(coneR*Math.cos(a));cy.push(coneR*Math.sin(a));cz.push(coneZ);\n'
        '    }\n'
        '    t.push({type:"scatter3d",x:cx,y:cy,z:cz,mode:"lines",\n'
        '        line:{color:"#22c55e",width:3,dash:"dash"},\n'
        '        name:"PSF Output",hoverinfo:"skip",showlegend:true});\n'
        '    for(var ca=0;ca<4;ca++){\n'
        '        var ang=ca*Math.PI/2;\n'
        '        t.push({type:"scatter3d",\n'
        '            x:[0,coneR*Math.cos(ang)],y:[0,coneR*Math.sin(ang)],z:[0,coneZ],\n'
        '            mode:"lines",line:{color:"#22c55e",width:1,dash:"dash"},\n'
        '            hoverinfo:"skip",showlegend:false});\n'
        '    }\n'
        '    var h = G.hhg;\n'
        '    if(h.gas_type) {\n'
        '        t.push({type:"scatter3d",x:[-xSize/2-25],y:[0],z:[z/2],mode:"text",\n'
        '            text:["<b>"+h.gas_type+" HHG</b><br>P="+h.pressure_mbar+" mbar<br>"+\n'
        '                  "IP="+h.ip_ev+" eV<br>Cutoff="+h.cutoff_ev+" eV<br>"+\n'
        '                  "H"+h.target_harmonic+" \\u2192 "+h.euv_wavelength_nm+" nm"],\n'
        '            textfont:{size:10,color:"#006644"},hoverinfo:"skip",showlegend:false});\n'
        '    }\n'
        '    var pb = G.power_budget;\n'
        '    var pbText = "<b>Power Budget</b>";\n'
        '    for(var pi=0;pi<pb.length;pi++){\n'
        '        var pw2=pb[pi].power_out;\n'
        '        var pStr = pw2>=1e-3 ? pw2.toFixed(3)+" W" :\n'
        '                   pw2>=1e-6 ? (pw2*1e6).toFixed(1)+" \\u00b5W" :\n'
        '                   pw2>=1e-9 ? (pw2*1e9).toFixed(1)+" nW" : pw2.toExponential(1)+" W";\n'
        '        pbText += "<br>"+pb[pi].name+": "+pStr;\n'
        '    }\n'
        '    t.push({type:"scatter3d",x:[xSize/2+25],y:[0],z:[z*0.7],mode:"text",\n'
        '        text:[pbText],textfont:{size:9,color:"#1e40af"},\n'
        '        hoverinfo:"skip",showlegend:false});\n'
        '    t.push({type:"scatter3d",x:[0],y:[ySize/2+12],z:[z/2],mode:"text",\n'
        '        text:["<b>11 Degrees of Freedom</b><br>"+\n'
        '              "XY steering \\u2022 Focus \\u2022 Polarization<br>"+\n'
        '              "Phase \\u2022 Wavelength \\u2022 Dose \\u2022 Thermal"],\n'
        '        textfont:{size:10,color:"#6366f1"},hoverinfo:"skip",showlegend:false});\n'
        '    return t;\n'
        '}\n'
        '\n'
        '// --- Camera presets and layouts ---\n'
        'var cameras = [\n'
        '    {eye:{x:1.8,y:1.2,z:0.8},up:{x:0,y:0,z:1}},\n'
        '    {eye:{x:1.6,y:1.0,z:0.6},up:{x:0,y:0,z:1}},\n'
        '    {eye:{x:1.5,y:-1.0,z:0.7},up:{x:0,y:0,z:1}}\n'
        '];\n'
        'var layouts = [\n'
        '    {scene:{xaxis:{title:"X (mm)",range:[-900,900],showgrid:true,gridcolor:"#eee"},\n'
        '            yaxis:{title:"Y (mm)",range:[-500,500],showgrid:true,gridcolor:"#eee"},\n'
        '            zaxis:{title:"Z (mm)",range:[-150,500],showgrid:true,gridcolor:"#eee"},\n'
        '            aspectmode:"manual",aspectratio:{x:1.8,y:1.0,z:0.8},\n'
        '            camera:cameras[0],bgcolor:"#fafafa"},\n'
        '     height:780,width:1400,showlegend:true,\n'
        '     legend:{x:0.01,y:0.99,bgcolor:"rgba(255,255,255,0.8)"},\n'
        '     title:"Integrated Multi-Head Writer Platform [ARCHITECTURE concept] (160 head slots)",\n'
        '     margin:{t:50,b:20,l:0,r:0}},\n'
        '    {scene:{xaxis:{title:"X (mm)",range:[-30,50],showgrid:true,gridcolor:"#eee"},\n'
        '            yaxis:{title:"Y (mm)",range:[-25,25],showgrid:true,gridcolor:"#eee"},\n'
        '            zaxis:{title:"Z (mm)",range:[-35,18],showgrid:true,gridcolor:"#eee"},\n'
        '            aspectmode:"manual",aspectratio:{x:1.5,y:1.0,z:1.1},\n'
        '            camera:cameras[1],bgcolor:"#fafafa"},\n'
        '     height:780,width:1400,showlegend:true,\n'
        '     legend:{x:0.01,y:0.99,bgcolor:"rgba(255,255,255,0.8)"},\n'
        '     title:"33\\u00d733 mm Package \\u2014 4\\u00d74 Writer Head Array (Head 1 exploded to show 11-DOF stack)",\n'
        '     margin:{t:50,b:20,l:0,r:0}},\n'
        '    {scene:{xaxis:{title:"X (\\u00b5m)",range:[-50,80],showgrid:true,gridcolor:"#eee"},\n'
        '            yaxis:{title:"Y (\\u00b5m)",range:[-40,40],showgrid:true,gridcolor:"#eee"},\n'
        '            zaxis:{title:"Z stack (\\u00b5m)",range:[-30,170],showgrid:true,gridcolor:"#eee"},\n'
        '            aspectmode:"manual",aspectratio:{x:1.3,y:0.8,z:1.5},\n'
        '            camera:cameras[2],bgcolor:"#fafafa"},\n'
        '     height:780,width:1400,showlegend:true,\n'
        '     legend:{x:0.01,y:0.99,bgcolor:"rgba(255,255,255,0.8)"},\n'
        '     title:"Single 11-DOF Writer Head \\u2014 3D Semiconductor Stack (~2\\u00d72 mm die)",\n'
        '     margin:{t:50,b:20,l:0,r:0}}\n'
        '];\n'
        'var builders = [buildPlatform, buildPackage, buildHead];\n'
        'var labels = ["Platform (160 heads)","Package (4\\u00d74 = 16 heads)","Writer Head (11-DOF)"];\n'
        '\n'
        'function render(level) {\n'
        '    Plotly.react("platform3d", builders[level](), layouts[level]);\n'
        '}\n'
        'render(0);\n'
        'var slider = document.getElementById("zoomSlider");\n'
        'var label = document.getElementById("zoomLabel");\n'
        'slider.addEventListener("input", function() {\n'
        '    var v = parseInt(this.value);\n'
        '    label.textContent = labels[v];\n'
        '    render(v);\n'
        '});\n'
        '})();\n'
        '</script>'
    )


# -- HTML page builder -------------------------------------------------

def build_3d_pipeline_html(pipeline, params, title="Integrated Multi-Head Writer Platform [ARCHITECTURE]"):
    """Build full HTML page with 3D platform hierarchy and tunable controls."""
    geometry = _get_platform_geometry(pipeline, params)
    geometry_json = json.dumps(geometry)

    gas_type = params.get("gas_type", "Ar")
    pressure = params.get("pressure_mbar", 30.0)
    intensity = params.get("intensity_w_cm2", 1e14)
    n_mirrors = params.get("n_mirrors", 2)
    filter_material = params.get("filter_material", "Al")
    filter_thickness = params.get("filter_thickness_nm", 200.0)

    def _selected(val, option):
        return "selected" if str(val) == str(option) else ""

    platform_js = _build_platform_js(geometry_json)

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="plotly.min.js"></script>
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
        .hero {{ background: linear-gradient(135deg, #0f172a, #1e3a5f); color: #fff; padding: 20px 24px; }}
        .hero h2 {{ margin: 0 0 6px 0; font-size: 20px; }}
        .hero p {{ margin: 0; font-size: 13px; color: #94a3b8; line-height: 1.5; max-width: 900px; }}
        .callout {{ background:#eff6ff;border:1px solid #93c5fd;border-radius:8px;padding:12px 20px;margin:12px 24px;font-size:13px;color:#1e40af;line-height:1.5; }}
    </style>
</head>
<body>
    <div class="nav">
        <a href="/api/visualize">2D Process Sim</a>
        <a href="/api/visualize-3d" class="active">3D Pipeline</a>
        <a href="/api/wavelength-bridge">Wavelength Bridge</a>
        <a href="/api/hhg-analytical">HHG Calculators</a>
        <a href="/api/fleet-dashboard">Platform Economics</a>
        <a href="/api/multihead">Multi-Head Array</a>
        <a href="/api/psf-synthesis">PSF Synthesis</a>
        <a href="/api/writer-head">11-DOF Head</a>
    </div>

    <div class="hero">
        <h2>Integrated Multi-Head Writer Platform <span style="background:#a855f7;color:#fff;font-size:11px;padding:2px 8px;border-radius:3px;letter-spacing:0.5px;vertical-align:middle;">ARCHITECTURE</span></h2>
        <p>
            <b>Architectural concept only.</b> This 3D view is an
            <i>architecture-level</i> system diagram that places an HHG
            generation chain (NIR/MIR driver \u2192 focusing optic \u2192 gas
            cell \u2192 metal filter \u2192 Mo/Si mirror \u2192 application plane)
            inside a multi-head packaging concept. It is not a built
            device, and not a claim that gas-jet HHG is competitive with
            laser-produced-plasma (LPP) EUV sources for high-volume
            manufacturing. The HHG cutoff, single-atom efficiency, and
            beamline transmission shown alongside this view are computed
            from the analytical / parameterized models in
            <code>backend/hhg_analytical.py</code>; see the
            <a href="/api/wavelength-bridge" style="color:#93c5fd;">wavelength-bridge</a>
            page for the spectral-region context.
        </p>
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
        <button type="submit">Update HHG Physics</button>
    </form>

    {platform_js}

    <div class="callout">
        <b>Scope.</b> This visualisation is an <i>architecture-level</i>
        system diagram. The HHG cutoff, single-atom efficiency, and
        beamline transmission shown above are computed analytically; the
        platform-level packaging shown below is illustrative only and
        carries no device-flux claim. Tabletop HHG sources deliver
        coherent EUV photon flux that is many orders of magnitude below
        ASML's laser-produced-plasma (LPP) source (250 W at intermediate
        focus, 13.5 nm); the gap is physical (conversion efficiency,
        duty cycle), not engineering. Defensible HHG use cases are
        coherent diffractive imaging (CDI), ptychography, actinic EUV
        mask inspection, and angle-resolved photoemission (ARPES) - see
        the <a href="/api/wavelength-bridge" style="color:#2563eb;">wavelength-bridge</a>
        figure for spectral context.
    </div>
</body>
</html>"""
