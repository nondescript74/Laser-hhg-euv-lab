"""Epistemic tier taxonomy for the Laser-HHG-EUV Lab.

Every quantitative or qualitative output in this repository must carry
an explicit tier label so that expert readers can immediately separate
formula-based predictions from architectural framing.

Tiers (from strongest to weakest physical commitment):

    ANALYTICAL   - Formula-based, exact within stated assumptions.
                   Examples: cutoff energy E_cut = 3.17 U_p + I_p,
                   beamline transmission product, photon-energy-to-wavelength
                   conversion.

    PARAMETERIZED- Single-atom or small-system response computed from a
                   physically motivated model with stated assumptions and
                   known limits of validity. Output shape (e.g., HHG
                   plateau + cutoff) is meaningful; absolute device flux
                   is NOT.

    ARCHITECTURE - System-level diagram, control-plane narrative, or
                   "consistent with published experimental feasibility"
                   claim. Carries no quantitative device-performance
                   assertion.

    LITERATURE   - Quoted measured value or scaling from a cited
                   experimental paper or industrial datasheet. The repo
                   does not reproduce the measurement; it reports what
                   has been published.

These four labels mirror the taxonomy in the HHG/EUV technical
repositioning brief (Apr 2026, Section D / Part E "Four Epistemic Tiers").
A fifth tier - "demonstrated subsystem behaviour" - is intentionally
excluded because no module in this repo physically builds or measures a
device; that tier is the province of cited references only.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class EpistemicTier(str, Enum):
    """Four-level claim taxonomy."""

    ANALYTICAL = "analytical"
    PARAMETERIZED = "parameterized"
    ARCHITECTURE = "architecture"
    LITERATURE = "literature"

    @property
    def short_label(self) -> str:
        return {
            EpistemicTier.ANALYTICAL: "Analytical / formula-based",
            EpistemicTier.PARAMETERIZED: "Parameterized model",
            EpistemicTier.ARCHITECTURE: "Architecture-level",
            EpistemicTier.LITERATURE: "Literature-derived",
        }[self]

    @property
    def short_tag(self) -> str:
        return {
            EpistemicTier.ANALYTICAL: "ANALYTICAL",
            EpistemicTier.PARAMETERIZED: "PARAMETERIZED",
            EpistemicTier.ARCHITECTURE: "ARCHITECTURE",
            EpistemicTier.LITERATURE: "LITERATURE",
        }[self]

    @property
    def description(self) -> str:
        return {
            EpistemicTier.ANALYTICAL: (
                "Closed-form expression evaluated with stated assumptions. "
                "Exact within the model; not a device-flux prediction."
            ),
            EpistemicTier.PARAMETERIZED: (
                "Single-atom or small-system response computed from a "
                "parameterized model (e.g., SFA, Gaussian PSF). Output "
                "shape is physically meaningful; absolute device flux is not."
            ),
            EpistemicTier.ARCHITECTURE: (
                "System diagram or control-plane narrative. Asserts "
                "architectural consistency with published experimental "
                "feasibility, not a built device."
            ),
            EpistemicTier.LITERATURE: (
                "Value quoted from a cited experimental paper or "
                "industrial datasheet. Not reproduced in this repo."
            ),
        }[self]

    @property
    def color(self) -> str:
        return {
            EpistemicTier.ANALYTICAL: "#16a34a",      # green
            EpistemicTier.PARAMETERIZED: "#2563eb",   # blue
            EpistemicTier.ARCHITECTURE: "#a855f7",    # purple
            EpistemicTier.LITERATURE: "#f59e0b",      # amber
        }[self]


@dataclass(frozen=True)
class TierLabel:
    """An epistemic tier plus the specific claim it applies to."""

    tier: EpistemicTier
    claim: str
    note: str = ""

    def to_text(self) -> str:
        prefix = f"[{self.tier.short_tag}]"
        body = self.claim if not self.note else f"{self.claim} \u2014 {self.note}"
        return f"{prefix} {body}"


# ---------------------------------------------------------------------------
# HTML rendering helpers
# ---------------------------------------------------------------------------

EPISTEMIC_CSS = """
.epi-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.6px;
    padding: 2px 7px;
    border-radius: 3px;
    text-transform: uppercase;
    vertical-align: middle;
    color: #fff;
    margin-right: 6px;
}
.epi-badge[data-tier="analytical"]    { background: #16a34a; }
.epi-badge[data-tier="parameterized"] { background: #2563eb; }
.epi-badge[data-tier="architecture"]  { background: #a855f7; }
.epi-badge[data-tier="literature"]    { background: #f59e0b; }
.epi-banner {
    background: #0f172a;
    color: #e2e8f0;
    padding: 10px 18px;
    border-left: 4px solid #f59e0b;
    font-size: 12px;
    line-height: 1.5;
}
.epi-banner b { color: #fbbf24; }
.epi-banner code { background: #1e293b; padding: 1px 5px; border-radius: 3px; }
.epi-key {
    display: flex; flex-wrap: wrap; gap: 8px;
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px;
    padding: 8px 12px; font-size: 11px; color: #475569; margin: 8px 0;
}
.epi-key .epi-badge { font-size: 9px; }
"""


def render_badge(tier: EpistemicTier, text: str | None = None) -> str:
    """Render an inline tier badge for use inside HTML prose."""
    label = text or tier.short_tag
    return (
        f'<span class="epi-badge" data-tier="{tier.value}" '
        f'title="{tier.description}">{label}</span>'
    )


def render_label(label: TierLabel) -> str:
    """Render a TierLabel as `<badge> claim - note` HTML."""
    badge = render_badge(label.tier)
    body = label.claim
    if label.note:
        body = f"{body} <span style='color:#64748b;'>&mdash; {label.note}</span>"
    return f"{badge}{body}"


def render_key(tiers: Iterable[EpistemicTier] | None = None) -> str:
    """Render the four-tier legend used at the top/bottom of pages."""
    if tiers is None:
        tiers = list(EpistemicTier)
    items = []
    for t in tiers:
        items.append(
            f'<div>{render_badge(t)}<span>{t.short_label}</span></div>'
        )
    return f'<div class="epi-key">{"".join(items)}</div>'


SCOPE_BANNER_HTML = """
<div class="epi-banner">
<b>Scope &amp; epistemic tier.</b> This repository is a <b>parameterized
HHG/EUV architectural modeling lab</b>, not a device demonstration and not
an industrial EUV source claim. All quantitative outputs carry an
explicit tier badge: <code>ANALYTICAL</code> (formula-based),
<code>PARAMETERIZED</code> (single-atom / small-system model),
<code>ARCHITECTURE</code> (system diagram / control-plane narrative),
or <code>LITERATURE</code> (value quoted from a cited source).
High-volume manufacturing EUV lithography uses laser-produced-plasma
(LPP) sources at power levels not accessible to gas-jet HHG; the gap
is physical (conversion efficiency, duty cycle, repetition rate), not
engineering, and this repo does not assert otherwise.
</div>
"""


def inject_epistemic_assets(html: str, *, banner: bool = True) -> str:
    """Inject epistemic CSS and (optionally) the scope banner into a page."""
    css_block = f"<style>{EPISTEMIC_CSS}</style>"
    if "<head>" in html:
        html = html.replace("<head>", f"<head>\n{css_block}", 1)
    elif "</head>" in html:
        html = html.replace("</head>", f"{css_block}\n</head>", 1)
    else:
        html = css_block + html

    if banner:
        # Insert banner directly after the first nav block if present, else
        # immediately after <body>.
        if 'class="nav"' in html:
            # Insert after the closing of the nav div (best-effort: after first
            # </div> following 'class="nav"').
            idx = html.find('class="nav"')
            close_idx = html.find("</div>", idx)
            if close_idx != -1:
                close_idx += len("</div>")
                html = html[:close_idx] + "\n" + SCOPE_BANNER_HTML + html[close_idx:]
            else:
                html = html.replace("<body>", f"<body>\n{SCOPE_BANNER_HTML}", 1)
        elif "<body>" in html:
            html = html.replace("<body>", f"<body>\n{SCOPE_BANNER_HTML}", 1)

    return html


def page_tier_panel(
    primary_tier: EpistemicTier,
    page_title: str,
    note: str,
) -> str:
    """Render a per-page header strip showing the primary tier of the page.

    This is the standard P1 visible badge for every visualization page.
    It is meant to sit immediately under the navigation, before any
    content callouts, so an expert reader sees the page's epistemic
    commitment before they read any numbers.
    """
    badge = render_badge(primary_tier)
    return (
        f'<div class="epi-banner" style="border-left-color:{primary_tier.color};">'
        f'{badge}<b>{page_title}</b> &mdash; {note}'
        f'</div>'
    )


__all__ = [
    "EpistemicTier",
    "TierLabel",
    "EPISTEMIC_CSS",
    "SCOPE_BANNER_HTML",
    "render_badge",
    "render_label",
    "render_key",
    "page_tier_panel",
    "inject_epistemic_assets",
]
