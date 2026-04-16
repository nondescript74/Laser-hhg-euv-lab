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
