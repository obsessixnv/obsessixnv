#!/usr/bin/env python3
"""Render the header and footer banners in both themes.

The art lives here once, with {{SLOT}} placeholders where a colour goes; the
palette module supplies the values. That keeps the dark and light banners from
drifting apart, which is what happens when you hand-maintain two SVGs.

Usage:  python3 scripts/render_banners.py [--out assets]
Writes assets/{header,footer}.svg (dark) and assets/{header,footer}-light.svg.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette  # noqa: E402

HEADER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 300" width="1200" height="300" role="img" aria-label="Roman Yankovych — Forward Deployed Engineer at Elcano · Ostinato Rigore">
  <title>Roman Yankovych — Forward Deployed Engineer at Elcano · Ostinato Rigore</title>

  <defs>
    <radialGradient id="night" cx="30%" cy="34%" r="98%">
      <stop offset="0%"  stop-color="{{GROUND_0}}"/>
      <stop offset="42%" stop-color="{{GROUND_1}}"/>
      <stop offset="100%" stop-color="{{GROUND_2}}"/>
    </radialGradient>
    <radialGradient id="candle" cx="30%" cy="32%" r="72%">
      <stop offset="0%"  stop-color="{{GLOW_0}}" stop-opacity="{{GLOW_0_OP}}"/>
      <stop offset="55%" stop-color="{{GLOW_1}}" stop-opacity="{{GLOW_1_OP}}"/>
      <stop offset="100%" stop-color="{{GLOW_1}}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="frame" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%"  stop-color="{{FRAME_0}}"/>
      <stop offset="38%" stop-color="{{FRAME_1}}"/>
      <stop offset="72%" stop-color="{{FRAME_2}}"/>
      <stop offset="100%" stop-color="{{FRAME_3}}"/>
    </linearGradient>
    <linearGradient id="gilt" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="{{GILT_0}}"/>
      <stop offset="60%" stop-color="{{GILT_1}}"/>
      <stop offset="100%" stop-color="{{GILT_2}}"/>
    </linearGradient>
    <radialGradient id="vig" cx="50%" cy="46%" r="72%">
      <stop offset="40%" stop-color="{{VIGNETTE}}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{{VIGNETTE}}" stop-opacity="{{VIGNETTE_OP}}"/>
    </radialGradient>
    <linearGradient id="leafg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{{LEAF_0}}"/>
      <stop offset="55%" stop-color="{{LEAF_1}}"/>
      <stop offset="100%" stop-color="{{LEAF_2}}"/>
    </linearGradient>
    <linearGradient id="budg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{{BUD_0}}"/>
      <stop offset="100%" stop-color="{{BUD_1}}"/>
    </linearGradient>
    <radialGradient id="berryg" cx="38%" cy="34%" r="70%">
      <stop offset="0%" stop-color="{{BERRY_0}}"/>
      <stop offset="100%" stop-color="{{BERRY_1}}"/>
    </radialGradient>
    <filter id="grain">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" result="n"/>
      <feColorMatrix in="n" type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.05"/></feComponentTransfer>
    </filter>

    <!-- a single dried leaf, base at 0,0 pointing +x -->
    <g id="leaf">
      <path d="M0 0 C 13 -10 38 -8 47 0 C 38 8 13 10 0 0 Z" fill="url(#leafg)"/>
      <path d="M4 0 Q 26 1 45 0" fill="none" stroke="{{LEAF_VEIN}}" stroke-width="0.9"/>
      <path d="M14 -1 l 6 -5 M24 -1 l 7 -5 M14 1 l 6 5 M24 1 l 7 5" stroke="{{LEAF_VEIN}}" stroke-width="0.7" opacity="0.7"/>
      <path d="M0 0 C 13 -10 38 -8 47 0" fill="none" stroke="{{LEAF_EDGE}}" stroke-width="0.8" opacity="0.45"/>
    </g>
    <!-- nodding rosebud, base at 0,0 -->
    <g id="bud">
      <path d="M0 9 C -11 4 -10 -13 0 -17 C 10 -13 11 4 0 9 Z" fill="url(#budg)"/>
      <path d="M0 -15 C -5 -6 -4 3 0 7" fill="none" stroke="{{BUD_VEIN}}" stroke-width="0.9" opacity="0.8"/>
      <path d="M-6 -9 C -4 -2 -3 4 0 7" fill="none" stroke="{{BUD_VEIN}}" stroke-width="0.8" opacity="0.7"/>
      <path d="M6 -9 C 4 -2 3 4 0 7" fill="none" stroke="{{BUD_VEIN}}" stroke-width="0.8" opacity="0.7"/>
      <path d="M0 -17 C -4 -10 -3 -4 0 0" fill="none" stroke="{{LEAF_EDGE}}" stroke-width="0.8" opacity="0.4"/>
      <path d="M-2 8 C -9 14 -13 12 -15 6 M2 8 C 9 14 13 12 15 6" fill="none" stroke="{{BUD_STEM}}" stroke-width="1.4"/>
    </g>
    <g id="berry">
      <circle r="4.2" fill="url(#berryg)"/>
      <circle cx="-1.3" cy="-1.4" r="1.1" fill="{{BERRY_HI}}" opacity="0.55"/>
    </g>

    <!-- carved molding fleuron, right half: scroll sweeping outward, curling inward -->
    <g id="fleuronHalf">
      <path d="M5 0 C 20 -1 34 -4 44 0 C 52 4 50 12 43 12 C 37 12 35 5 41 4"
            fill="none" stroke="url(#gilt)" stroke-width="2.4" stroke-linecap="round"/>
      <use href="#leaf" transform="translate(15,-1) rotate(12) scale(0.5)"/>
      <circle cx="27" cy="4.4" r="1.5" fill="{{LEAF_EDGE}}" opacity="0.7"/>
      <path d="M56 0 L 132 0" stroke="{{RULE}}" stroke-width="1.4" opacity="0.75"/>
      <path d="M140 0 l 4.4 -3.4 l 4.4 3.4 l -4.4 3.4 Z" fill="{{DIAMOND}}" opacity="0.85"/>
    </g>
    <!-- full fleuron: mirrored scrolls about a central bud pointing inward (+y) -->
    <g id="fleuron">
      <use href="#fleuronHalf"/>
      <use href="#fleuronHalf" transform="scale(-1,1)"/>
      <path d="M0 -4 C -6.5 0 -6.5 9 0 14.5 C 6.5 9 6.5 0 0 -4 Z" fill="url(#budg)"/>
      <path d="M0 12.5 C -2 7 -2 2 0 -2.5" fill="none" stroke="{{BUD_VEIN}}" stroke-width="0.8" opacity="0.75"/>
      <path d="M0 -4 C 3.5 0.5 3.5 6 1.5 10" fill="none" stroke="{{LEAF_EDGE}}" stroke-width="0.7" opacity="0.45"/>
    </g>
  </defs>

  <style>
    .fade  { animation: fade 1.1s ease-out both; }
    .fade2 { animation: fade 1.1s ease-out 0.22s both; }
    .fade3 { animation: fade 1.1s ease-out 0.44s both; }
    @keyframes fade { from { opacity: 0 } to { opacity: 1 } }
    .flick { animation: flick 5.5s ease-in-out infinite; }
    @keyframes flick { 0%{opacity:.82} 22%{opacity:1} 38%{opacity:.78} 55%{opacity:.96} 74%{opacity:.8} 100%{opacity:.9} }
    @media (prefers-reduced-motion: reduce) {
      .fade, .fade2, .fade3, .flick { animation: none }
    }
  </style>

  <!-- ground -->
  <rect width="1200" height="300" fill="url(#night)"/>
  <rect class="flick" width="1200" height="300" fill="url(#candle)"/>
  <rect width="1200" height="300" filter="url(#grain)" opacity="{{GRAIN_OP}}"/>

  <!-- dried botanical: leaves seated on the stem, cascading down the left -->
  <g>
    <path d="M88 44 C 128 78 96 118 122 150 C 146 178 116 204 136 232"
          fill="none" stroke="{{STEM}}" stroke-width="2.4" stroke-linecap="round"/>
    <path d="M88 44 C 128 78 96 118 122 150 C 146 178 116 204 136 232"
          fill="none" stroke="{{STEM_HI}}" stroke-width="0.8" stroke-linecap="round" opacity="0.35"/>
    <path d="M122 150 C 104 168 94 196 92 220"
          fill="none" stroke="{{STEM}}" stroke-width="1.7" stroke-linecap="round"/>

    <use href="#leaf" transform="translate(88,44)   rotate(133) scale(0.82)"/>
    <use href="#leaf" transform="translate(106,70)  rotate(38)  scale(0.68)"/>
    <use href="#leaf" transform="translate(110,98)  rotate(154) scale(0.94)"/>
    <use href="#leaf" transform="translate(111,125) rotate(24)  scale(0.76)"/>
    <use href="#leaf" transform="translate(122,150) rotate(166) scale(0.88)"/>
    <use href="#leaf" transform="translate(131,171) rotate(46)  scale(0.72)"/>
    <use href="#leaf" transform="translate(129,211) rotate(158) scale(0.84)"/>
    <use href="#leaf" transform="translate(105,186) rotate(206) scale(0.66)"/>
    <use href="#leaf" transform="translate(92,220)  rotate(186) scale(0.6)"/>

    <use href="#bud"  transform="translate(136,232) rotate(22)  scale(1.05)"/>
    <use href="#bud"  transform="translate(130,191) rotate(-14) scale(0.62)"/>
    <use href="#berry" transform="translate(118,142)"/>
    <use href="#berry" transform="translate(126,158)"/>
    <use href="#berry" transform="translate(99,214)"/>
  </g>

  <!-- name — fills and fonts inlined so text survives without CSS -->
  <g text-anchor="middle" font-family="Georgia, 'Times New Roman', serif">
    <text class="fade"  x="690" y="104" font-size="14" font-weight="700" letter-spacing="7"   fill="{{TEXT_MOTTO}}">&#10022; &#160; OSTINATO RIGORE &#160; &#10022;</text>
    <text class="fade2" x="690" y="170" font-size="56" font-weight="700" letter-spacing="1"   fill="{{TEXT_NAME}}">Roman Yankovych</text>
    <text class="fade3" x="690" y="206" font-size="15" font-weight="700" letter-spacing="6.5" fill="{{TEXT_SUB}}">FORWARD DEPLOYED ENGINEER &#183; ELCANO</text>
  </g>

  <!-- shadowed corners -->
  <rect width="1200" height="300" fill="url(#vig)" pointer-events="none"/>

  <!-- gilt frame -->
  <rect x="3"  y="3"  width="1194" height="294" fill="none" stroke="{{FRAME_SHADOW}}" stroke-width="2" opacity="{{FRAME_SHADOW_OP}}"/>
  <rect x="9"  y="9"  width="1182" height="282" fill="none" stroke="url(#frame)" stroke-width="10"/>
  <rect x="9"  y="9"  width="1182" height="282" fill="none" stroke="{{FRAME_HI}}" stroke-width="1.1" opacity="{{FRAME_HI_OP}}"/>
  <rect x="17" y="17" width="1166" height="266" fill="none" stroke="{{FRAME_LINE}}" stroke-width="1.6"/>
  <rect x="22" y="22" width="1156" height="256" fill="none" stroke="{{RULE}}" stroke-width="1.6" stroke-dasharray="1.5 5" opacity="0.7"/>

  <!-- fleurons seated on the inner rule, top and bottom -->
  <use href="#fleuron" transform="translate(600,22)"/>
  <use href="#fleuron" transform="translate(600,278) rotate(180)"/>
</svg>
"""

FOOTER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 150" width="1200" height="150" role="img" aria-label="Festina lente — Ars longa, vita brevis">
  <title>Festina lente · Ars longa, vita brevis</title>
  <defs>
    <radialGradient id="nightf" cx="50%" cy="-10%" r="120%">
      <stop offset="0%"  stop-color="{{FGROUND_0}}"/>
      <stop offset="55%" stop-color="{{FGROUND_1}}"/>
      <stop offset="100%" stop-color="{{FGROUND_2}}"/>
    </radialGradient>
    <linearGradient id="framef" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="{{FRAME_2}}"/>
      <stop offset="50%" stop-color="{{FRAME_0}}"/>
      <stop offset="100%" stop-color="{{FRAME_2}}"/>
    </linearGradient>
    <linearGradient id="giltf" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%"  stop-color="{{GILT_0}}"/>
      <stop offset="60%" stop-color="{{GILT_1}}"/>
      <stop offset="100%" stop-color="{{GILT_2}}"/>
    </linearGradient>
    <linearGradient id="leafgf" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{{LEAF_0}}"/>
      <stop offset="55%" stop-color="{{LEAF_1}}"/>
      <stop offset="100%" stop-color="{{LEAF_2}}"/>
    </linearGradient>
    <linearGradient id="budgf" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{{BUD_0}}"/>
      <stop offset="100%" stop-color="{{BUD_1}}"/>
    </linearGradient>
    <radialGradient id="vigf" cx="50%" cy="40%" r="78%">
      <stop offset="45%" stop-color="{{VIGNETTE}}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{{VIGNETTE}}" stop-opacity="{{FVIGNETTE_OP}}"/>
    </radialGradient>
    <filter id="grainf">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" stitchTiles="stitch" result="n"/>
      <feColorMatrix in="n" type="saturate" values="0"/>
      <feComponentTransfer><feFuncA type="linear" slope="0.05"/></feComponentTransfer>
    </filter>

    <g id="leaff">
      <path d="M0 0 C 13 -10 38 -8 47 0 C 38 8 13 10 0 0 Z" fill="url(#leafgf)"/>
      <path d="M4 0 Q 26 1 45 0" fill="none" stroke="{{LEAF_VEIN}}" stroke-width="0.9"/>
      <path d="M0 0 C 13 -10 38 -8 47 0" fill="none" stroke="{{LEAF_EDGE}}" stroke-width="0.8" opacity="0.45"/>
    </g>

    <!-- the header's fleuron, so the frame reads as one set -->
    <g id="fleuronHalff">
      <path d="M5 0 C 20 -1 34 -4 44 0 C 52 4 50 12 43 12 C 37 12 35 5 41 4"
            fill="none" stroke="url(#giltf)" stroke-width="2.4" stroke-linecap="round"/>
      <use href="#leaff" transform="translate(15,-1) rotate(12) scale(0.5)"/>
      <circle cx="27" cy="4.4" r="1.5" fill="{{LEAF_EDGE}}" opacity="0.7"/>
      <path d="M56 0 L 132 0" stroke="{{RULE}}" stroke-width="1.4" opacity="0.75"/>
      <path d="M140 0 l 4.4 -3.4 l 4.4 3.4 l -4.4 3.4 Z" fill="{{DIAMOND}}" opacity="0.85"/>
    </g>
    <g id="fleuronf">
      <use href="#fleuronHalff"/>
      <use href="#fleuronHalff" transform="scale(-1,1)"/>
      <path d="M0 -4 C -6.5 0 -6.5 9 0 14.5 C 6.5 9 6.5 0 0 -4 Z" fill="url(#budgf)"/>
      <path d="M0 12.5 C -2 7 -2 2 0 -2.5" fill="none" stroke="{{BUD_VEIN}}" stroke-width="0.8" opacity="0.75"/>
      <path d="M0 -4 C 3.5 0.5 3.5 6 1.5 10" fill="none" stroke="{{LEAF_EDGE}}" stroke-width="0.7" opacity="0.45"/>
    </g>
  </defs>

  <rect width="1200" height="150" fill="url(#nightf)"/>
  <rect width="1200" height="150" filter="url(#grainf)" opacity="{{GRAIN_OP}}"/>

  <!-- gilded molding rail -->
  <rect x="34" y="20" width="1132" height="7" fill="url(#framef)"/>
  <rect x="34" y="20" width="1132" height="1.6" fill="{{FRAME_HI}}" opacity="{{RAIL_HI_OP}}"/>
  <line x1="42" y1="36" x2="1158" y2="36" stroke="{{RULE}}" stroke-width="1.6" stroke-dasharray="1.5 5" opacity="0.7"/>

  <use href="#fleuronf" transform="translate(600,36)"/>

  <!-- mottos — fills and fonts inlined so text survives without CSS -->
  <g text-anchor="middle" font-family="Georgia, 'Times New Roman', serif" font-weight="700">
    <text x="600" y="102" font-size="26" letter-spacing="7" fill="{{TEXT_MOTTO}}">FESTINA LENTE</text>
    <text x="600" y="126" font-size="12" letter-spacing="5" fill="{{TEXT_SUB}}">ARS &#183; LONGA &#183; VITA &#183; BREVIS</text>
  </g>

  <rect width="1200" height="150" fill="url(#vigf)" pointer-events="none"/>
</svg>
"""


def render(template: str, theme: str) -> str:
    values = palette.banners(theme)
    out = template
    for slot, value in values.items():
        out = out.replace("{{" + slot + "}}", value)
    leftover = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", out)))
    if leftover:
        raise SystemExit(f"error: template slot(s) with no palette entry: {leftover}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="assets")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    for name, template in (("header", HEADER), ("footer", FOOTER)):
        for theme in ("dark", "light"):
            suffix = "" if theme == "dark" else "-light"
            path = os.path.join(args.out, f"{name}{suffix}.svg")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(render(template, theme))
            print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
