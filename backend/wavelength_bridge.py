"""Wavelength-bridge figure: driver -> harmonic cascade -> DUV/VUV/EUV.

This module renders the single most important architectural diagram in
the repo. It places, on one continuous wavelength axis from ~3 um down
to ~1 nm:

    * driver-laser bands (Ti:Sa 800 nm, Yb:YAG 1030 nm, MIR OPCPA 1800-3000 nm)
    * the HHG-conversion arrow that maps driver -> harmonic plateau
    * the DUV / VUV / EUV / SXR spectral regions
    * the operating point of the companion vdw-polaritonics-lab
      (193 / 248 nm DUV intracavity modulation)
    * the operating point of THIS repo (HHG generation chain, NIR/MIR
      driver -> 60-13.5 nm harmonics)
    * industrially relevant anchor wavelengths: ASML LPP @ 13.5 nm,
      actinic mask inspection @ ~30 nm, DUV @ 193/248 nm.

The figure is explicitly tier-tagged ARCHITECTURE: it is a system
diagram, not a parameterized output. It is paired with an analytical
overlay (cutoff vs driver wavelength) so that the figure cannot be
misread as device performance.
"""

from __future__ import annotations

from dataclasses import dataclass

import plotly.graph_objects as go

from backend.epistemic import (
    EPISTEMIC_CSS,
    EpistemicTier,
    SCOPE_BANNER_HTML,
    TierLabel,
    page_tier_panel,
)
from backend.hhg_analytical import (
    HC_EV_NM,
    cutoff_energy,
    harmonic_wavelength_nm,
)


# ---------------------------------------------------------------------------
# Spectral regions (wavelength bands, nm)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Band:
    name: str
    lambda_min_nm: float
    lambda_max_nm: float
    color: str
    text_color: str = "#ffffff"


SPECTRAL_REGIONS: tuple[Band, ...] = (
    Band("MIR / NIR driver", 1300.0, 3000.0, "#a16207"),
    Band("NIR driver (Ti:Sa, Yb)", 700.0, 1300.0, "#ca8a04"),
    Band("Visible", 400.0, 700.0, "#16a34a"),
    Band("DUV (vdW-cavity regime)", 150.0, 400.0, "#7c3aed"),
    Band("VUV", 100.0, 150.0, "#6d28d9"),
    Band("EUV", 10.0, 100.0, "#1d4ed8"),
    Band("Soft X-ray", 1.0, 10.0, "#0f172a"),
)


@dataclass(frozen=True)
class Anchor:
    name: str
    wavelength_nm: float
    note: str
    color: str = "#dc2626"


INDUSTRIAL_ANCHORS: tuple[Anchor, ...] = (
    Anchor("DUV 248 nm (KrF)", 248.0, "vdw-polaritonics-lab DUV regime", "#7c3aed"),
    Anchor("DUV 193 nm (ArF)", 193.0, "vdw-polaritonics-lab DUV regime", "#6d28d9"),
    Anchor("Actinic ~30 nm",  30.4, "EUV mask inspection (HHG-credible)", "#2563eb"),
    Anchor("EUV litho 13.5 nm", 13.5, "ASML LPP source - NOT this repo", "#dc2626"),
)


@dataclass(frozen=True)
class DriverSpec:
    name: str
    wavelength_nm: float
    color: str
    note: str


DRIVER_SPECS: tuple[DriverSpec, ...] = (
    DriverSpec("Ti:Sa  800 nm", 800.0,  "#ea580c",
               "best-characterized HHG driver; harmonics 17-51 -> 30-55 nm"),
    DriverSpec("Yb:YAG 1030 nm", 1030.0, "#d97706",
               "lower-cost industrial driver; harmonics into 25-40 nm"),
    DriverSpec("MIR OPCPA 1800 nm", 1800.0, "#a16207",
               "lower efficiency, higher cutoff; access to 13-15 nm in He"),
)


# ---------------------------------------------------------------------------
# Repo operating-region annotations
# ---------------------------------------------------------------------------

VDW_REPO_BAND = (193.0, 248.0)   # vdw-polaritonics-lab intracavity modulation
HHG_REPO_BAND = (13.5, 60.0)     # this repo: harmonic plateau / cutoff window


# ---------------------------------------------------------------------------
# Figure builder
# ---------------------------------------------------------------------------

def _add_region_bars(fig: go.Figure, y_center: float, bar_height: float) -> None:
    """Add the colored spectral-region bars across the wavelength axis."""
    for band in SPECTRAL_REGIONS:
        fig.add_shape(
            type="rect",
            x0=band.lambda_min_nm, x1=band.lambda_max_nm,
            y0=y_center - bar_height / 2, y1=y_center + bar_height / 2,
            fillcolor=band.color, opacity=0.35, line=dict(width=0),
            layer="below",
        )
        fig.add_annotation(
            x=(band.lambda_min_nm * band.lambda_max_nm) ** 0.5,
            y=y_center,
            text=band.name,
            showarrow=False,
            font=dict(size=10, color="#0f172a"),
        )


def _add_repo_bands(fig: go.Figure, y_top: float) -> None:
    """Annotate the operating regions of the two companion repos."""
    fig.add_shape(
        type="rect",
        x0=VDW_REPO_BAND[0], x1=VDW_REPO_BAND[1],
        y0=y_top - 0.1, y1=y_top + 0.1,
        fillcolor="#a855f7", opacity=0.55, line=dict(color="#7c3aed", width=2),
    )
    fig.add_annotation(
        x=(VDW_REPO_BAND[0] * VDW_REPO_BAND[1]) ** 0.5,
        y=y_top + 0.4,
        text="<b>vdw-polaritonics-lab</b><br>DUV intracavity modulation",
        showarrow=False, font=dict(size=11, color="#7c3aed"),
    )

    fig.add_shape(
        type="rect",
        x0=HHG_REPO_BAND[0], x1=HHG_REPO_BAND[1],
        y0=y_top - 0.1, y1=y_top + 0.1,
        fillcolor="#1d4ed8", opacity=0.55, line=dict(color="#1e3a8a", width=2),
    )
    fig.add_annotation(
        x=(HHG_REPO_BAND[0] * HHG_REPO_BAND[1]) ** 0.5,
        y=y_top + 0.4,
        text="<b>Laser-hhg-euv-lab (this repo)</b><br>HHG plateau \u2192 cutoff",
        showarrow=False, font=dict(size=11, color="#1e3a8a"),
    )


def _add_drivers(fig: go.Figure, y_drivers: float) -> None:
    """Annotate the three principal HHG driver wavelengths."""
    for d in DRIVER_SPECS:
        fig.add_trace(go.Scatter(
            x=[d.wavelength_nm], y=[y_drivers],
            mode="markers+text",
            marker=dict(size=14, color=d.color, line=dict(color="#1e293b", width=1.5),
                        symbol="diamond"),
            text=[f"<b>{d.name}</b>"],
            textposition="top center",
            textfont=dict(size=10, color="#1e293b"),
            hovertext=d.note,
            hoverinfo="text",
            name=d.name, showlegend=False,
        ))


def _add_anchors(fig: go.Figure, y_anchors: float) -> None:
    """Annotate industrially relevant anchor wavelengths."""
    for a in INDUSTRIAL_ANCHORS:
        fig.add_trace(go.Scatter(
            x=[a.wavelength_nm], y=[y_anchors],
            mode="markers+text",
            marker=dict(size=12, color=a.color, line=dict(color="#1e293b", width=1.2),
                        symbol="triangle-down"),
            text=[a.name],
            textposition="bottom center",
            textfont=dict(size=10, color="#1e293b"),
            hovertext=a.note,
            hoverinfo="text",
            name=a.name, showlegend=False,
        ))


def _add_conversion_arrows(fig: go.Figure, y_drivers: float, y_anchor: float) -> None:
    """Draw HHG-conversion arrows from each driver to its representative
    cutoff / plateau region (using the analytical cutoff at typical
    intensities)."""
    typical_intensity = 1.5e14  # W/cm^2 - representative HHG operating point
    typical_gas = "Ar"
    for d in DRIVER_SPECS:
        # If driver is very long-wavelength, prefer Ne/He which support
        # the higher cutoff energies actually used in MIR HHG.
        gas = "He" if d.wavelength_nm >= 1500 else typical_gas
        cut = cutoff_energy(typical_intensity, d.wavelength_nm, gas=gas)
        # Map cutoff energy back to wavelength for placement on the axis.
        landing_nm = HC_EV_NM / cut.cutoff_ev
        fig.add_annotation(
            x=landing_nm, y=y_anchor + 0.05,
            ax=d.wavelength_nm, ay=y_drivers - 0.05,
            xref="x", yref="y", axref="x", ayref="y",
            arrowhead=3, arrowsize=1.2, arrowwidth=1.4,
            arrowcolor=d.color, opacity=0.85,
            text=f"<i>HHG cutoff @ I=1.5\u00d710<sup>14</sup>, {gas}: ~{cut.cutoff_ev:.0f} eV</i>",
            font=dict(size=9, color=d.color),
            showarrow=True, standoff=4,
        )


def build_wavelength_bridge_figure() -> go.Figure:
    """Render the wavelength-bridge architecture figure."""
    fig = go.Figure()

    y_anchors = 0.0     # anchor wavelengths along the bottom
    y_regions = 1.0     # main spectral-region bar
    y_drivers = 2.2     # driver wavelengths above
    y_repos = 3.2       # repo operating-region overlays

    _add_region_bars(fig, y_center=y_regions, bar_height=0.7)
    _add_anchors(fig, y_anchors=y_anchors)
    _add_drivers(fig, y_drivers=y_drivers)
    _add_conversion_arrows(fig, y_drivers=y_drivers, y_anchor=y_anchors + 0.3)
    _add_repo_bands(fig, y_top=y_repos)

    fig.update_xaxes(
        type="log",
        range=[0.0, 3.6],   # 1 nm to ~4 um in log10
        title="Wavelength (nm) - log scale",
        showgrid=True, gridcolor="#e2e8f0",
        tickvals=[1, 3, 10, 30, 100, 300, 1000, 3000],
        ticktext=["1", "3", "10", "30", "100", "300", "1000", "3000"],
    )
    fig.update_yaxes(visible=False, range=[-0.6, 4.0])
    fig.update_layout(
        title=dict(
            text=(
                "<b>Wavelength bridge</b>: NIR/MIR drivers \u2192 HHG conversion \u2192 DUV/VUV/EUV<br>"
                "<sub>[ARCHITECTURE] System diagram - not a device-flux prediction. "
                "Cutoff arrows are analytical (3.17 U_p + I_p) at I=1.5\u00d710<sup>14</sup> W/cm<sup>2</sup>.</sub>"
            ),
            x=0.5, xanchor="center",
        ),
        height=520,
        margin=dict(l=60, r=40, t=110, b=60),
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#ffffff",
        showlegend=False,
    )
    return fig


# ---------------------------------------------------------------------------
# Tier annotation for the figure
# ---------------------------------------------------------------------------

WAVELENGTH_BRIDGE_TIER = TierLabel(
    tier=EpistemicTier.ARCHITECTURE,
    claim="Wavelength-bridge diagram",
    note=(
        "Driver bands and HHG cutoff arrows are analytical; repo "
        "operating-region overlays are architectural framing only."
    ),
)


def build_wavelength_bridge_html(*, embed_only: bool = False) -> str:
    """Return either an HTML fragment (embed_only=True) or a full page."""
    fig = build_wavelength_bridge_figure()
    plot_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    if embed_only:
        return plot_html

    bridge_panel = page_tier_panel(
        EpistemicTier.ARCHITECTURE,
        page_title="Wavelength Bridge (architectural diagram)",
        note=(
            "Driver bands and HHG-cutoff arrows are <b>analytical</b> "
            "(3.17 U_p + I_p); spectral regions and industrial anchors "
            "are <b>literature-derived</b>; repo operating-region "
            "overlays are <b>architecture-level</b> framing only. The "
            "vdW-cavity DUV regime and the HHG EUV regime are "
            "physically distinct and non-overlapping."
        ),
    )
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Wavelength bridge [ARCHITECTURE] - Laser-HHG-EUV Lab</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
               margin: 0; background: #f8fafc; color: #1e293b; }}
        .nav {{ background: #1a1a2e; padding: 8px 24px; display: flex; gap: 16px; align-items: center; }}
        .nav a {{ color: #aac; text-decoration: none; font-size: 14px; padding: 4px 12px; border-radius: 4px; }}
        .nav a:hover {{ background: #2a2a4e; }}
        .nav a.active {{ background: #2563eb; color: #fff; }}
        .section {{ padding: 18px 24px; }}
        .section p {{ font-size: 13px; line-height: 1.55; max-width: 900px; color: #334155; }}
    </style>
    <style>{EPISTEMIC_CSS}</style>
</head>
<body>
    <div class="nav">
        <a href="/">Dashboard</a>
        <a href="/api/visualize">2D Process Sim</a>
        <a href="/api/visualize-3d">3D Pipeline</a>
        <a href="/api/wavelength-bridge" class="active">Wavelength Bridge</a>
        <a href="/api/hhg-analytical">HHG Calculators</a>
        <a href="/api/fleet-dashboard">Platform Economics</a>
        <a href="/api/multihead">Multi-Head Array</a>
        <a href="/api/psf-synthesis">PSF Synthesis</a>
        <a href="/api/writer-head">11-DOF Head</a>
    </div>
    {SCOPE_BANNER_HTML}
    {bridge_panel}
    <div class="section">
        <h2>Wavelength bridge: driver \u2192 HHG \u2192 DUV/VUV/EUV</h2>
        <p>This figure positions the two companion repositories on a single
        wavelength axis. The vdw-polaritonics-lab operates intracavity in the
        DUV at 193/248 nm; this Laser-HHG-EUV lab models the generation-side
        chain that drives a near-infrared or mid-infrared pulse through a
        gas medium to produce odd harmonics in the DUV/VUV/EUV/SXR bands.
        The two systems share an architectural control-plane concept
        (programmable optical transfer function) but are physically
        distinct: vdW materials absorb at EUV, so the cavity does not
        operate at 13.5 nm[cite: 108].</p>
        <p>The HHG-cutoff arrows are <b>analytical</b> (E<sub>cut</sub> =
        3.17 U<sub>p</sub> + I<sub>p</sub>) evaluated at a representative
        operating point and grounded in the strong-field
        approximation[cite: 101] and the semi-classical three-step
        model[cite: 107]. The single-atom efficiency anti-scaling
        eta(lambda) ~ lambda<sup>-(5..6.5)</sup> is anchored to the
        Shiner et al. measurement[cite: 100]. The wavelength positions
        of the spectral regions and industrial anchors are
        <b>literature-derived</b>; source-side photon-flux anchors
        (KMLabs XUUS-4)[cite: 103] are quoted, not reproduced. The repo
        operating-region overlays are <b>architecture-level</b> framing
        only; they do not assert measured device flux, and gas-jet HHG
        is not represented as a replacement for ASML's LPP source[cite: 108].</p>
        {plot_html}
    </div>
</body>
</html>"""


__all__ = [
    "Band", "Anchor", "DriverSpec",
    "SPECTRAL_REGIONS", "INDUSTRIAL_ANCHORS", "DRIVER_SPECS",
    "VDW_REPO_BAND", "HHG_REPO_BAND",
    "WAVELENGTH_BRIDGE_TIER",
    "build_wavelength_bridge_figure",
    "build_wavelength_bridge_html",
]
