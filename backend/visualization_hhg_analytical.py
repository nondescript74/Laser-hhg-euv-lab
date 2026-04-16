"""HTML page exposing the analytical HHG calculators with explicit tier
labels.

This page is the ANALYTICAL counterpart to
:mod:`backend.wavelength_bridge` (ARCHITECTURE). For a given driver
wavelength, intensity, gas, medium length, and pressure, it shows:

    * cutoff energy and maximum harmonic order      (ANALYTICAL)
    * relative single-atom yield vs. wavelength      (ANALYTICAL)
    * phase-matching window proxy                    (ANALYTICAL)
    * compound beamline transmission                 (ANALYTICAL)
    * generated vs delivered photon flux             (LITERATURE + ANALYTICAL)

Every numeric output is rendered with the tier badge produced by
:func:`backend.epistemic.render_badge`.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from backend.epistemic import (
    EpistemicTier,
    SCOPE_BANNER_HTML,
    EPISTEMIC_CSS,
    page_tier_panel,
    render_badge,
    render_key,
)
from backend.hhg_analytical import (
    HC_EV_NM,
    cutoff_energy,
    efficiency_scaling,
    phase_matching_window,
    beamline_transmission,
    split_generated_vs_delivered,
)
from backend.optical_pipeline import SOURCE_SIDE_LITERATURE_ANCHORS


_NAV = """
<div class="nav">
    <a href="/api/visualize">2D Process Sim</a>
    <a href="/api/visualize-3d">3D Pipeline</a>
    <a href="/api/wavelength-bridge">Wavelength Bridge</a>
    <a href="/api/hhg-analytical" class="active">HHG Calculators</a>
    <a href="/api/fleet-dashboard">Platform Economics</a>
    <a href="/api/multihead">Multi-Head Array</a>
    <a href="/api/psf-synthesis">PSF Synthesis</a>
    <a href="/api/writer-head">11-DOF Head</a>
</div>
"""

_PAGE_CSS = """
* { box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
       margin: 0; background: #f8fafc; color: #1e293b; }
.nav { background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }
.nav a { color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }
.nav a:hover { background: #2a2a4e; }
.nav a.active { background: #2563eb; color: #fff; }
.controls { background: #fff; padding: 12px 24px; border-bottom: 1px solid #e2e8f0;
            display: flex; flex-wrap: wrap; gap: 14px; align-items: end; }
.control-group { display: flex; flex-direction: column; gap: 3px; }
.control-group label { font-size: 11px; font-weight: 600; color: #475569;
                       text-transform: uppercase; letter-spacing: 0.5px; }
.control-group input, .control-group select { padding: 6px 8px; border: 1px solid #cbd5e1;
            border-radius: 4px; font-size: 13px; }
.control-group input { width: 110px; }
.control-group select { width: 90px; }
button { padding: 7px 18px; background: #2563eb; color: #fff; border: none;
         border-radius: 4px; font-size: 13px; cursor: pointer; font-weight: 600; }
button:hover { background: #1d4ed8; }
.section { padding: 18px 24px; }
.section h2 { font-size: 18px; font-weight: 700; color: #0f172a; margin: 0 0 10px 0;
              border-bottom: 2px solid #2563eb; padding-bottom: 6px; display: inline-block; }
.metrics { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; margin-top: 12px; }
.metric { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; }
.metric .value { font-size: 22px; font-weight: 800; color: #0f172a; margin-top: 4px; }
.metric .label { font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px; }
.metric .basis { font-size: 11px; color: #475569; margin-top: 6px; line-height: 1.4; }
table.budget { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
table.budget th { background: #f1f5f9; padding: 8px 10px; text-align: left; color: #475569; font-weight: 700; border-bottom: 2px solid #e2e8f0; }
table.budget td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; }
"""


def _metric(label: str, value: str, basis_html: str) -> str:
    return (
        '<div class="metric">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>'
        f'<div class="basis">{basis_html}</div>'
        '</div>'
    )


def _build_efficiency_figure(reference_nm: float = 800.0) -> go.Figure:
    lambdas = np.linspace(400, 3000, 80)
    cent = []
    lo = []
    hi = []
    for ln in lambdas:
        r = efficiency_scaling(float(ln), reference_wavelength_nm=reference_nm)
        cent.append(r.relative_yield_central)
        lo.append(r.relative_yield_low)
        hi.append(r.relative_yield_high)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(lambdas) + list(lambdas[::-1]),
        y=hi + lo[::-1],
        fill="toself", fillcolor="rgba(37,99,235,0.18)",
        line=dict(color="rgba(37,99,235,0)"),
        name="lambda^-(5..6.5) band", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=lambdas, y=cent, mode="lines",
        line=dict(color="#1d4ed8", width=2),
        name="lambda^-6 (central)",
    ))
    fig.add_vline(x=800, line_dash="dot", line_color="#ea580c",
                  annotation_text="Ti:Sa 800 nm", annotation_position="top left")
    fig.add_vline(x=1030, line_dash="dot", line_color="#d97706",
                  annotation_text="Yb:YAG 1030", annotation_position="top right")
    fig.add_vline(x=1800, line_dash="dot", line_color="#a16207",
                  annotation_text="MIR 1800", annotation_position="top")
    fig.update_yaxes(type="log", title="Relative single-atom yield (vs 800 nm)")
    fig.update_xaxes(title="Driver wavelength (nm)")
    fig.update_layout(
        title="Single-atom efficiency anti-scaling [ANALYTICAL]",
        height=380, margin=dict(l=60, r=40, t=60, b=40),
        plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
    )
    return fig


def _build_cutoff_vs_intensity_figure(driver_wavelength_nm: float, gas: str) -> go.Figure:
    intensities = np.logspace(13.5, 15.5, 60)
    cutoffs = [cutoff_energy(float(I), driver_wavelength_nm, gas).cutoff_ev for I in intensities]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=intensities, y=cutoffs, mode="lines",
                             line=dict(color="#16a34a", width=2.5),
                             name=f"{gas} @ {driver_wavelength_nm:.0f} nm"))
    fig.add_hline(y=92.0, line_dash="dot", line_color="#dc2626",
                  annotation_text="EUV litho 13.5 nm = 92 eV (NOT this repo)",
                  annotation_position="top right")
    fig.update_xaxes(type="log", title="Driver intensity (W/cm^2)")
    fig.update_yaxes(title="HHG cutoff energy (eV)")
    fig.update_layout(
        title=f"Cutoff energy vs intensity [ANALYTICAL] - {gas}, {driver_wavelength_nm:.0f} nm",
        height=380, margin=dict(l=60, r=40, t=60, b=40),
        plot_bgcolor="#f8fafc", paper_bgcolor="#ffffff",
    )
    return fig


def build_hhg_analytical_html(
    driver_wavelength_nm: float = 800.0,
    intensity_w_cm2: float = 1.5e14,
    gas: str = "Ar",
    medium_length_mm: float = 30.0,
    pressure_mbar: float = 30.0,
    n_mirrors: int = 2,
    n_filters: int = 1,
    mirror_reflectivity: float = 0.65,
    filter_transmission: float = 0.50,
) -> str:
    """Build the HHG analytical-calculator HTML page."""
    cut = cutoff_energy(intensity_w_cm2, driver_wavelength_nm, gas=gas)
    eff = efficiency_scaling(driver_wavelength_nm)
    pm = phase_matching_window(
        gas=gas, intensity_w_cm2=intensity_w_cm2,
        medium_length_mm=medium_length_mm, pressure_mbar=pressure_mbar,
    )
    bl = beamline_transmission(
        n_mirrors=n_mirrors, mirror_reflectivity=mirror_reflectivity,
        n_filters=n_filters, filter_transmission=filter_transmission,
    )

    # Pick a literature anchor for the chosen gas, for the FluxBudget.
    anchor_key = {
        "Ar": "Ar_35nm", "Kr": "Kr_50nm", "Ne": "Ne_30nm",
        "Xe": "Xe_70nm", "He": "He_13p5nm",
    }.get(gas, "Ar_35nm")
    anchor_value = SOURCE_SIDE_LITERATURE_ANCHORS[anchor_key]
    flux = split_generated_vs_delivered(anchor_value, bl)

    # Figures.
    fig_eff = _build_efficiency_figure()
    fig_cut = _build_cutoff_vs_intensity_figure(driver_wavelength_nm, gas)
    plot_eff = fig_eff.to_html(full_html=False, include_plotlyjs="cdn")
    plot_cut = fig_cut.to_html(full_html=False, include_plotlyjs=False)

    badge_a = render_badge(EpistemicTier.ANALYTICAL)
    badge_p = render_badge(EpistemicTier.PARAMETERIZED)
    badge_l = render_badge(EpistemicTier.LITERATURE)

    cut_metric = _metric(
        "Cutoff energy E_cut",
        f"{cut.cutoff_ev:.1f} eV",
        f"{badge_a} 3.17 U_p + I_p; U_p = {cut.ponderomotive_ev:.2f} eV; "
        f"I_p({cut.gas}) = {cut.ionization_potential_ev:.2f} eV",
    )
    qmax_metric = _metric(
        "Max harmonic order q_max",
        f"H{cut.max_harmonic_order} ({cut.cutoff_wavelength_nm:.1f} nm)",
        f"{badge_a} q_max odd; lambda_q = lambda_drive / q",
    )
    eff_metric = _metric(
        "Relative single-atom yield",
        f"{eff.relative_yield_central:.2e}",
        f"{badge_a} (lambda / 800 nm)^-6; band [{eff.relative_yield_low:.1e}, "
        f"{eff.relative_yield_high:.1e}] for n in [5.0, 6.5]",
    )
    pm_status = "in phase-matching window" if pm.in_window else "OVER-IONIZED (no classical PM)"
    pm_metric = _metric(
        "Phase-matching proxy",
        pm_status,
        f"{badge_a} ionization fraction {pm.ionization_fraction*100:.2f}% vs "
        f"eta_crit({gas}) = {pm.critical_fraction*100:.2f}%; margin {pm.margin*100:+.2f}%",
    )
    bl_metric = _metric(
        "Beamline transmission",
        f"{bl.transmission*100:.2f}%",
        f"{badge_a} R^N * T^M; R={mirror_reflectivity:.2f}^{n_mirrors} * "
        f"T={filter_transmission:.2f}^{n_filters}",
    )

    flux_table = (
        '<table class="budget">'
        '<tr><th>Plane</th><th>Photons / s / harmonic</th><th>Tier</th><th>Basis</th></tr>'
        f'<tr><td>Source-side (gas-jet exit)</td>'
        f'<td>{flux.source_photons_per_second:.2e}</td>'
        f'<td>{badge_l}</td>'
        f'<td>{flux.source_basis.note}</td></tr>'
        f'<tr><td>Beamline transmission factor</td>'
        f'<td>{flux.beamline_transmission*100:.2f}%</td>'
        f'<td>{badge_a}</td>'
        f'<td>{flux.beamline_basis.note}</td></tr>'
        f'<tr><td><b>Delivered (application plane, vacuum)</b></td>'
        f'<td><b>{flux.delivered_photons_per_second:.2e}</b></td>'
        f'<td>{badge_p}</td>'
        f'<td>{flux.delivered_basis.note}</td></tr>'
        '</table>'
    )

    analytical_panel = page_tier_panel(
        EpistemicTier.ANALYTICAL,
        page_title="HHG Analytical Calculators (formula-based)",
        note=(
            "Every metric on this page is a closed-form expression "
            "evaluated with stated assumptions, plus one literature-"
            "anchored source-flux number on the budget table. <b>Nothing "
            "here measures device flux.</b> Cutoff energy uses E_cut = "
            "3.17 U_p + I_p[cite: 101][cite: 107]; single-atom yield "
            "uses lambda^-(5..6.5)[cite: 100]; phase-matching window "
            "uses eta_crit thresholds[cite: 102]; source-side flux is "
            "quoted from the KMLabs XUUS-4 white paper[cite: 103]."
        ),
    )
    # Top-of-page summary strip so an expert sees the key numbers within
    # the first viewport without having to scroll past a bare form.
    summary_strip = (
        f'<div style="display:flex;flex-wrap:wrap;gap:8px;background:#f1f5f9;'
        f'padding:10px 16px;border-bottom:1px solid #e2e8f0;font-size:12px;">'
        f'<span style="color:#475569;"><b>At-a-glance</b> (current inputs):</span>'
        f'<span>{badge_a} cutoff <b>{cut.cutoff_ev:.1f} eV</b> '
        f'(H{cut.max_harmonic_order}, &lambda;_cut={cut.cutoff_wavelength_nm:.1f} nm)</span>'
        f'<span>&middot;</span>'
        f'<span>{badge_a} relative single-atom yield '
        f'<b>{eff.relative_yield_central:.2e}</b> vs 800 nm</span>'
        f'<span>&middot;</span>'
        f'<span>{badge_a} beamline T '
        f'<b>{bl.transmission*100:.2f}%</b></span>'
        f'<span>&middot;</span>'
        f'<span>{badge_a} phase-matching: '
        f'<b>{"in window" if pm.in_window else "OVER-IONIZED"}</b></span>'
        f'<span>&middot;</span>'
        f'<span>{badge_l} source-flux anchor: KMLabs XUUS-4</span>'
        f'</div>'
    )

    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>HHG Analytical Calculators [ANALYTICAL] - Laser-HHG-EUV Lab</title>
    <style>{_PAGE_CSS}</style>
    <style>{EPISTEMIC_CSS}</style>
</head>
<body>
    {_NAV}
    {SCOPE_BANNER_HTML}
    {analytical_panel}
    {summary_strip}
    <form class="controls" method="get" action="/api/hhg-analytical">
        <div class="control-group">
            <label>Driver lambda (nm)</label>
            <input type="number" name="driver_wavelength_nm" value="{driver_wavelength_nm}" step="50" min="200" max="3000">
        </div>
        <div class="control-group">
            <label>Intensity (W/cm^2)</label>
            <input type="number" name="intensity_w_cm2" value="{intensity_w_cm2:.2e}" step="1e13" min="1e13" max="1e16">
        </div>
        <div class="control-group">
            <label>Gas</label>
            <select name="gas">
                <option value="Ar" {"selected" if gas=="Ar" else ""}>Ar</option>
                <option value="Kr" {"selected" if gas=="Kr" else ""}>Kr</option>
                <option value="Xe" {"selected" if gas=="Xe" else ""}>Xe</option>
                <option value="Ne" {"selected" if gas=="Ne" else ""}>Ne</option>
                <option value="He" {"selected" if gas=="He" else ""}>He</option>
            </select>
        </div>
        <div class="control-group">
            <label>Medium L (mm)</label>
            <input type="number" name="medium_length_mm" value="{medium_length_mm}" step="1" min="1" max="100">
        </div>
        <div class="control-group">
            <label>Pressure (mbar)</label>
            <input type="number" name="pressure_mbar" value="{pressure_mbar}" step="5" min="1" max="500">
        </div>
        <div class="control-group">
            <label>N mirrors</label>
            <input type="number" name="n_mirrors" value="{n_mirrors}" step="1" min="0" max="10">
        </div>
        <div class="control-group">
            <label>Mirror R</label>
            <input type="number" name="mirror_reflectivity" value="{mirror_reflectivity}" step="0.05" min="0" max="1">
        </div>
        <div class="control-group">
            <label>N filters</label>
            <input type="number" name="n_filters" value="{n_filters}" step="1" min="0" max="5">
        </div>
        <div class="control-group">
            <label>Filter T</label>
            <input type="number" name="filter_transmission" value="{filter_transmission}" step="0.05" min="0" max="1">
        </div>
        <button type="submit">Recompute</button>
    </form>

    <div class="section">
        <h2>Analytical results</h2>
        {render_key()}
        <div class="metrics">
            {cut_metric}
            {qmax_metric}
            {eff_metric}
            {pm_metric}
            {bl_metric}
        </div>
    </div>

    <div class="section">
        <h2>Generated vs. delivered photon flux</h2>
        <p style="font-size:13px;color:#475569;line-height:1.5;max-width:900px;">
            The repo strictly separates source-side flux (LITERATURE
            anchor at the gas-jet exit)[cite: 103], beamline transmission
            (ANALYTICAL R^N * T^M), and delivered application-plane
            flux (PARAMETERIZED, source x beamline; ignores sample
            absorption and detector QE). The default source value is
            quoted from the Coherent / KMLabs XUUS-4 white paper[cite: 103]
            and is NOT computed by this repository. ASML's industrial
            LPP source operates at 250 W intermediate focus[cite: 108];
            tabletop HHG delivers nanowatts to microwatts at 13.5 nm,
            and the gap is physical, not engineering.
        </p>
        {flux_table}
    </div>

    <div class="section">
        <h2>Single-atom efficiency anti-scaling</h2>
        <p style="font-size:13px;color:#475569;line-height:1.5;max-width:900px;">
            Single-atom HHG yield falls steeply with driver wavelength:
            eta(lambda) ~ lambda<sup>-(5..6.5)</sup>. The central
            curve uses the lambda<sup>-6</sup> exponent; the shaded
            band brackets the experimental uncertainty measured by
            Shiner et al.[cite: 100] in Xe and Kr over 800-1850 nm.
            This is the reason MIR HHG (which extends the cutoff via
            U<sub>p</sub> ~ lambda<sup>2</sup>) has dramatically lower
            single-atom yield than Ti:Sa.
        </p>
        {plot_eff}
    </div>

    <div class="section">
        <h2>Cutoff energy vs intensity</h2>
        <p style="font-size:13px;color:#475569;line-height:1.5;max-width:900px;">
            Cutoff energy follows the strong-field three-step
            law[cite: 101][cite: 107]: E<sub>cut</sub> = 3.17
            U<sub>p</sub> + I<sub>p</sub>, with U<sub>p</sub> = 9.33
            &times; 10<sup>-14</sup> &middot; I[W/cm<sup>2</sup>]
            &middot; lambda[&micro;m]<sup>2</sup>. The dashed line at
            92 eV marks the EUV-litho 13.5 nm photon energy &mdash;
            this is shown for reference only; this repo does not
            represent gas-jet HHG as a 13.5 nm lithography source[cite: 108].
        </p>
        {plot_cut}
    </div>
</body>
</html>"""


__all__ = ["build_hhg_analytical_html"]
