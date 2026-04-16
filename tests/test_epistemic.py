"""Discipline tests for the epistemic-tier taxonomy.

Every public visualization page must:
  * include the four-tier scope banner exactly once,
  * include the epistemic CSS so badges actually render, and
  * carry at least one explicit tier badge inline.

These tests fail fast if a future change accidentally strips the tier
labels off a user-facing page.
"""

from __future__ import annotations

import re

from fastapi.testclient import TestClient

from app import app
from backend.epistemic import (
    EPISTEMIC_CSS,
    EpistemicTier,
    SCOPE_BANNER_HTML,
    TierLabel,
    inject_epistemic_assets,
    render_badge,
    render_key,
    render_label,
)


# ---------------------------------------------------------------------------
# Enum + helpers
# ---------------------------------------------------------------------------

def test_all_four_tiers_exist():
    assert {t.value for t in EpistemicTier} == {
        "analytical", "parameterized", "architecture", "literature",
    }


def test_each_tier_has_label_and_color():
    for t in EpistemicTier:
        assert isinstance(t.short_label, str) and t.short_label
        assert isinstance(t.short_tag, str) and t.short_tag.isupper()
        assert isinstance(t.description, str) and t.description
        assert t.color.startswith("#")


def test_render_badge_emits_data_tier():
    html = render_badge(EpistemicTier.ANALYTICAL)
    assert 'data-tier="analytical"' in html
    assert "epi-badge" in html
    # Default text is the short tag.
    assert "ANALYTICAL" in html


def test_render_label_includes_claim_and_note():
    label = TierLabel(
        tier=EpistemicTier.PARAMETERIZED,
        claim="Single-atom yield",
        note="lambda^-(5..6.5)",
    )
    html = render_label(label)
    assert 'data-tier="parameterized"' in html
    assert "Single-atom yield" in html
    assert "lambda^-(5..6.5)" in html


def test_render_key_includes_all_tiers():
    html = render_key()
    for t in EpistemicTier:
        assert f'data-tier="{t.value}"' in html


def test_inject_epistemic_assets_adds_css_and_banner():
    page = "<html><head><title>x</title></head><body><div class='nav'>nav</div></body></html>"
    out = inject_epistemic_assets(page)
    assert "epi-badge" in out                # CSS injected
    assert "Scope &amp; epistemic tier" in out  # banner injected


def test_inject_epistemic_assets_can_skip_banner():
    page = "<html><head></head><body></body></html>"
    out = inject_epistemic_assets(page, banner=False)
    assert "epi-badge" in out
    assert "Scope &amp; epistemic tier" not in out


# ---------------------------------------------------------------------------
# Page-level discipline (FastAPI integration)
# ---------------------------------------------------------------------------

client = TestClient(app)


def _strip(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def test_dashboard_has_scope_card_and_tier_legend():
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.text
    assert "Parameterized HHG / EUV architectural modeling lab" in body
    # Tier legend
    for t in EpistemicTier:
        assert f'data-tier="{t.value}"' in body
    # The "Scope" callout on the dashboard
    assert "Scope." in body and "LPP" in body


def test_wavelength_bridge_page_is_architecture_tagged():
    resp = client.get("/api/wavelength-bridge")
    assert resp.status_code == 200
    body = resp.text
    assert "Wavelength bridge" in body
    assert "[ARCHITECTURE]" in body or "ARCHITECTURE" in body


def test_hhg_analytical_page_emits_all_four_tiers():
    resp = client.get("/api/hhg-analytical")
    assert resp.status_code == 200
    body = resp.text
    for t in EpistemicTier:
        assert f'data-tier="{t.value}"' in body, f"missing tier {t.value}"
    assert "Scope &amp; epistemic tier" in body


def test_hhg_analytical_returns_disciplined_metrics():
    resp = client.get(
        "/api/hhg-analytical",
        params={"driver_wavelength_nm": 1800, "intensity_w_cm2": 1e14, "gas": "He"},
    )
    assert resp.status_code == 200
    body = resp.text
    # Cutoff is reported in eV; for He at 1e14, 1800 nm cutoff is high
    assert "Cutoff energy" in body
    assert "Beamline transmission" in body
    assert "Generated vs. delivered" in body


def test_visualize_page_has_parameterized_badge():
    resp = client.get("/api/visualize")
    assert resp.status_code == 200
    body = resp.text
    assert "PARAMETERIZED" in body


def test_visualize_3d_page_has_architecture_label():
    resp = client.get("/api/visualize-3d")
    assert resp.status_code == 200
    body = resp.text
    assert "ARCHITECTURE" in body
    # Old "VCSEL" overclaim language should be gone from the headline.
    assert "VCSEL Source" not in body
    # Old "matches ASML throughput at 0.2% of the cost" claim must be removed.
    assert "0.2% of the cost" not in body


def test_fleet_economics_json_carries_tier_field():
    resp = client.get("/api/fleet-economics")
    assert resp.status_code == 200
    payload = resp.json()
    assert isinstance(payload, list) and payload
    for entry in payload:
        assert entry["epistemic_tier"] == "architecture"
        assert "tier_note" in entry


def test_simulate_post_carries_tier_field():
    resp = client.post("/api/simulate", json={"dose": 20})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["epistemic_tier"] == "parameterized"
    assert "tier_note" in payload


def test_system_state_carries_tier_field():
    resp = client.get("/api/v1/system-state")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["epistemic_tier"] == "architecture"
    assert "tier_note" in payload


# ---------------------------------------------------------------------------
# P1 page-tier-panel discipline
# Every visualization page that previously had no visible tier badge
# must now carry a per-page tier panel injected via page_tier_panel().
# ---------------------------------------------------------------------------

def test_psf_page_has_tier_panel_and_scope_banner():
    resp = client.get("/api/psf-synthesis")
    body = resp.text
    assert "epi-banner" in body
    assert "PSF Synthesis (parameterized)" in body
    assert 'data-tier="parameterized"' in body
    assert "Scope &amp; epistemic tier" in body


def test_multihead_page_has_tier_panel_and_scope_banner():
    resp = client.get("/api/multihead")
    body = resp.text
    assert "epi-banner" in body
    assert "Multi-Head Writer Array (architectural concept)" in body
    assert 'data-tier="architecture"' in body
    assert "Scope &amp; epistemic tier" in body
    # Old chip-scale-replaces-ASML phrasing must be gone from this page.
    assert "matches ASML throughput" not in body


def test_fleet_page_has_tier_panel_and_scope_banner():
    resp = client.get("/api/fleet-dashboard")
    body = resp.text
    assert "epi-banner" in body
    assert "Platform Economics" in body
    assert 'data-tier="architecture"' in body
    assert "Scope &amp; epistemic tier" in body
    # Hard-removed overclaim string.
    assert "replaces a room-sized $380M ASML tool" not in body


def test_writer_head_page_has_tier_panel_and_scope_banner():
    resp = client.get("/api/writer-head")
    body = resp.text
    assert "epi-banner" in body
    assert "11-DOF Writer Head (architectural concept)" in body
    assert 'data-tier="architecture"' in body
    assert "Scope &amp; epistemic tier" in body


# ---------------------------------------------------------------------------
# Citation discipline: HHG-facing pages must cite the new primary sources
# ---------------------------------------------------------------------------

# Distinctive substrings drawn from each reference's "full" text as
# rendered by build_references_footer(). If references.py is edited,
# these strings may need updating.
HHG_PRIMARY_REF_FULLTEXT = {
    "Shiner_2009":      "Shiner, A.D. et al.",
    "Lewenstein_1994":  "Lewenstein, M., Balcou",
    "Wikmark_2022":     "Wikmark, H. et al.",
    "KMLabs_XUUS4":     "Coherent / KMLabs XUUS-4 white paper",
    "Carstens_2024":    "Carstens, H. et al.",
    "ELI_ALPS_2025":    "ELI-ALPS / SYLOS team",
    "ASML_LPP":         "ASML laser-produced-plasma (LPP) EUV source",
    "Corkum_1993":      "Corkum, P.B.",
    "ArXiv_2509_02867": "Open-source C++ HHG simulation program",
}


def test_hhg_analytical_page_cites_primary_sources():
    body = client.get("/api/hhg-analytical").text
    for key in [
        "Shiner_2009",
        "Lewenstein_1994",
        "KMLabs_XUUS4",
        "Wikmark_2022",
        "ASML_LPP",
    ]:
        needle = HHG_PRIMARY_REF_FULLTEXT[key]
        assert needle in body, (
            f"Expected reference fragment '{needle}' ({key}) on HHG analytical page"
        )


def test_wavelength_bridge_page_cites_primary_sources():
    body = client.get("/api/wavelength-bridge").text
    for key in ["Shiner_2009", "Lewenstein_1994", "Wikmark_2022", "ASML_LPP"]:
        needle = HHG_PRIMARY_REF_FULLTEXT[key]
        assert needle in body, (
            f"Expected reference fragment '{needle}' ({key}) on wavelength-bridge page"
        )


def test_visualize_3d_page_cites_lpp_gap_and_kmlabs_anchor():
    body = client.get("/api/visualize-3d").text
    for key in ["ASML_LPP", "KMLabs_XUUS4", "Carstens_2024"]:
        needle = HHG_PRIMARY_REF_FULLTEXT[key]
        assert needle in body, f"Expected reference fragment '{needle}' ({key}) on /api/visualize-3d"


def test_fleet_dashboard_cites_lpp_gap_anchor():
    body = client.get("/api/fleet-dashboard").text
    for key in ["ASML_LPP", "Shiner_2009"]:
        needle = HHG_PRIMARY_REF_FULLTEXT[key]
        assert needle in body, f"Expected reference fragment '{needle}' ({key}) on /api/fleet-dashboard"


# ---------------------------------------------------------------------------
# P1.5 first-impression discipline
#
# For every priority page the SCOPE_BANNER and the per-page TIER PANEL
# must appear BEFORE the first quantitative content (hero stat, form,
# main figure). These tests pin the *order* of HTML markers so a future
# refactor cannot quietly demote the framing below the fold.
# ---------------------------------------------------------------------------

PRIORITY_PAGES_FIRST_IMPRESSION = {
    "/api/fleet-dashboard": {
        "tier_phrase": "Platform Economics &amp; ASML Comparison (architectural)",
        "first_content_marker": '<div class="hero">',
    },
    "/api/visualize-3d": {
        "tier_phrase": "3D Generation-Chain View (architectural diagram)",
        "first_content_marker": '<div class="hero">',
    },
    "/api/multihead": {
        "tier_phrase": "Multi-Head Writer Array (architectural concept)",
        "first_content_marker": '<form class="controls"',
    },
    "/api/psf-synthesis": {
        "tier_phrase": "PSF Synthesis (parameterized)",
        "first_content_marker": '<form class="controls"',
    },
    "/api/hhg-analytical": {
        "tier_phrase": "HHG Analytical Calculators (formula-based)",
        "first_content_marker": '<form class="controls"',
    },
    "/api/wavelength-bridge": {
        "tier_phrase": "Wavelength Bridge (architectural diagram)",
        "first_content_marker": "<h2>Wavelength bridge",
    },
}


def test_priority_pages_have_scope_banner_above_first_content():
    """Scope banner must appear before the first quantitative content."""
    for path, expected in PRIORITY_PAGES_FIRST_IMPRESSION.items():
        body = client.get(path).text
        i_scope = body.find("Scope &amp; epistemic tier")
        i_first = body.find(expected["first_content_marker"])
        assert i_scope != -1, f"{path}: scope banner missing"
        assert i_first != -1, (
            f"{path}: first content marker '{expected['first_content_marker']}' missing"
        )
        assert i_scope < i_first, (
            f"{path}: scope banner appears AFTER first content "
            f"(scope at {i_scope}, content at {i_first})"
        )


def test_priority_pages_have_tier_panel_above_first_content():
    """Per-page tier panel must appear before the first quantitative content."""
    for path, expected in PRIORITY_PAGES_FIRST_IMPRESSION.items():
        body = client.get(path).text
        i_panel = body.find(expected["tier_phrase"])
        i_first = body.find(expected["first_content_marker"])
        assert i_panel != -1, (
            f"{path}: tier panel phrase '{expected['tier_phrase']}' missing"
        )
        assert i_first != -1, (
            f"{path}: first content marker '{expected['first_content_marker']}' missing"
        )
        assert i_panel < i_first, (
            f"{path}: tier panel appears AFTER first content "
            f"(panel at {i_panel}, content at {i_first})"
        )


def test_fleet_hero_metrics_carry_architecture_tag_each():
    """Highest-risk page: every hero stat must carry an inline
    [ARCHITECTURE] chip so the strip cannot read as a deployable
    benchmark even when skimmed."""
    body = client.get("/api/fleet-dashboard").text
    # Each of the five hero-stat blocks should contain the .tag span.
    n_arch_tags = body.count('class="tag">ARCHITECTURE')
    assert n_arch_tags >= 5, (
        f"/api/fleet-dashboard hero must carry an ARCHITECTURE tag in "
        f"each of the 5 hero stats; found {n_arch_tags}"
    )


def test_fleet_hero_labels_no_longer_read_as_benchmarks():
    """The hero labels must read as sensitivity outputs, not as
    bare benchmark wins like 'Cost vs ASML' or 'Power Reduction'."""
    body = client.get("/api/fleet-dashboard").text
    # Old benchmark-style labels (now deprecated) must NOT appear in the
    # hero block.
    deprecated_labels = [
        ">Cost vs ASML<",
        ">Power Reduction<",
        ">Footprint<",
        ">Per-Head Failure<",
        ">Platform wph<",
    ]
    for bad in deprecated_labels:
        assert bad not in body, (
            f"/api/fleet-dashboard still uses deprecated benchmark "
            f"label '{bad}'; replace with sensitivity-style wording."
        )
    # New sensitivity-framed labels must be present.
    expected_labels = [
        "Sensitivity: cost-axis ratio",
        "Sensitivity: power-axis ratio",
        "Sensitivity: footprint ratio",
        "Architecture: per-head",
        "Sensitivity: throughput",
    ]
    for needle in expected_labels:
        assert needle in body, (
            f"/api/fleet-dashboard hero is missing the sensitivity-"
            f"framed label '{needle}'"
        )


def test_fleet_hero_value_demoted_to_neutral_color():
    """Hero values must use the demoted (neutral grey) styling, not
    the old large-blue benchmark-win styling."""
    body = client.get("/api/fleet-dashboard").text
    # The new demoted styling rule.
    assert ".hero-stat .value" in body
    assert "color: #cbd5e1" in body, (
        "/api/fleet-dashboard hero values must use the demoted "
        "neutral-grey colour (#cbd5e1), not the old #38bdf8 cyan."
    )
    assert "#38bdf8" not in body or "color: #38bdf8" not in body, (
        "/api/fleet-dashboard still applies the old cyan colour to "
        "the hero-stat values."
    )


def test_hhg_analytical_summary_strip_above_form():
    """The at-a-glance summary strip must appear before the form so a
    skim reader sees the four analytical numbers within the first
    viewport."""
    body = client.get("/api/hhg-analytical").text
    i_summary = body.find("At-a-glance")
    i_form = body.find('<form class="controls"')
    assert i_summary != -1, "/api/hhg-analytical missing 'At-a-glance' summary strip"
    assert i_form != -1
    assert i_summary < i_form, (
        "/api/hhg-analytical summary strip must precede the form "
        f"(summary at {i_summary}, form at {i_form})"
    )
