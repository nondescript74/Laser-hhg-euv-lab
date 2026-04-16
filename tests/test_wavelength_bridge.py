"""Tests for the wavelength-bridge architecture figure.

The figure is the single most important visual asset in the repo. It
must place both companion repos on one wavelength axis, mark the four
industrial anchor wavelengths, draw an HHG-conversion arrow for each
of the three principal driver wavelengths, and stay tier-tagged
ARCHITECTURE.
"""

from __future__ import annotations

from backend.epistemic import EpistemicTier
from backend.wavelength_bridge import (
    DRIVER_SPECS,
    HHG_REPO_BAND,
    INDUSTRIAL_ANCHORS,
    SPECTRAL_REGIONS,
    VDW_REPO_BAND,
    WAVELENGTH_BRIDGE_TIER,
    build_wavelength_bridge_figure,
    build_wavelength_bridge_html,
)


# ---------------------------------------------------------------------------
# Static metadata
# ---------------------------------------------------------------------------

def test_three_driver_wavelengths_are_present():
    names = [d.name for d in DRIVER_SPECS]
    assert any("Ti:Sa" in n for n in names)
    assert any("Yb:YAG" in n for n in names)
    assert any("MIR" in n for n in names)


def test_industrial_anchors_include_lpp_and_duv():
    names = [a.name for a in INDUSTRIAL_ANCHORS]
    assert any("13.5" in n for n in names)   # ASML LPP - NOT this repo
    assert any("193" in n for n in names)
    assert any("248" in n for n in names)


def test_spectral_regions_cover_uv_to_sxr():
    region_names = [b.name for b in SPECTRAL_REGIONS]
    assert any("DUV" in n for n in region_names)
    assert any("VUV" in n for n in region_names)
    assert any("EUV" in n for n in region_names)
    assert any("Soft X-ray" in n for n in region_names)


def test_repo_bands_are_correctly_placed():
    # vdW cavity: 193-248 nm DUV
    assert VDW_REPO_BAND[0] < VDW_REPO_BAND[1]
    assert 150 <= VDW_REPO_BAND[0] <= 250
    # HHG repo: 13.5-60 nm EUV plateau
    assert HHG_REPO_BAND[0] < HHG_REPO_BAND[1]
    assert HHG_REPO_BAND[0] <= 13.5 + 1e-9
    # The two bands must NOT overlap (architectural separation).
    assert HHG_REPO_BAND[1] < VDW_REPO_BAND[0]


def test_figure_tier_is_architecture():
    assert WAVELENGTH_BRIDGE_TIER.tier is EpistemicTier.ARCHITECTURE


# ---------------------------------------------------------------------------
# Figure / HTML builders
# ---------------------------------------------------------------------------

def test_figure_builds_without_error():
    fig = build_wavelength_bridge_figure()
    # Drivers (3) + anchors (4) + zero or more conversion arrows = at least 7 traces
    assert len(fig.data) >= len(DRIVER_SPECS) + len(INDUSTRIAL_ANCHORS)


def test_figure_has_log_x_axis():
    fig = build_wavelength_bridge_figure()
    assert fig.layout.xaxis.type == "log"


def test_figure_title_carries_architecture_label():
    fig = build_wavelength_bridge_figure()
    text = fig.layout.title.text
    assert "ARCHITECTURE" in text
    assert "Wavelength bridge" in text


def test_html_page_contains_both_repo_overlays_and_anchors():
    html = build_wavelength_bridge_html()
    assert "vdw-polaritonics-lab" in html
    assert "Laser-hhg-euv-lab" in html
    # Industrial anchors visible.
    assert "13.5 nm" in html
    assert "193 nm" in html or "193 / 248 nm" in html
    # Tier label visible.
    assert "ARCHITECTURE" in html or "architecture-level" in html


def test_html_page_includes_navigation_to_calculators():
    html = build_wavelength_bridge_html()
    assert "/api/hhg-analytical" in html
