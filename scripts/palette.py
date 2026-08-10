"""Both themes, in one place.

Dark is the Baroque original: a tenebrist ground lit by candlelight.
Light is its historical counterpart rather than an inversion -- the illuminated
manuscript. Parchment ground, sepia ink, the same gilt and the same oxblood
botanicals, which is what they were painted on to begin with.

Every colour the banners and cards use is a named slot here. Nothing downstream
hardcodes a hex, so a theme is a palette swap and not a second copy of the art.
"""

# --- cards -------------------------------------------------------------------

CARD_DARK = {
    "INK_BRIGHT": "#f0e4c8",   # hero numbers
    "INK":        "#bda06e",   # labels
    "INK_DIM":    "#8a7350",   # axis ticks
    "GOLD":       "#b8860b",   # titles
    "GOLD_HI":    "#e7c469",   # gilt highlight, plot line
    "OXBLOOD":    "#a8412a",   # peak marker
    "GROUND_0":   "#2a1e11",   # card ground, radial centre
    "GROUND_1":   "#14100a",
    "GROUND_2":   "#0b0807",
    "BORDER_0":   "#e7c469",
    "BORDER_1":   "#8a6a1e",
    "BORDER_2":   "#3d2b09",
    "GRID":       "#3a2c18",
    "AREA_OP":    "0.13",
}

CARD_LIGHT = {
    "INK_BRIGHT": "#2b1e08",
    "INK":        "#6b5320",
    "INK_DIM":    "#8d7b52",
    "GOLD":       "#8a6a1e",
    "GOLD_HI":    "#a87c1c",
    "OXBLOOD":    "#8f3323",
    "GROUND_0":   "#fdf8ea",
    "GROUND_1":   "#f3e9d2",
    "GROUND_2":   "#e6d8b8",
    "BORDER_0":   "#c9992a",
    "BORDER_1":   "#9a7a26",
    "BORDER_2":   "#5c4109",
    "GRID":       "#d9c9a2",
    "AREA_OP":    "0.20",
}

# Sequential ramps for language share. Both validated: lightness strictly
# monotonic and every step >= 3:1 against that theme's card ground. Adjacent
# steps sit close within one hue family, so each segment always carries a direct
# label and a 2px gap -- identity never rests on colour alone.
RAMP_DARK = ["#f5e0a0", "#e2c076", "#d0a154", "#be833f", "#ad6538", "#9c4a33"]
RAMP_DARK_OTHER = "#6f6555"

RAMP_LIGHT = ["#ad7020", "#9c5f22", "#8b4b25", "#7a3927", "#682a26", "#551d1f"]
RAMP_LIGHT_OTHER = "#8a8170"


def cards(theme: str) -> tuple[dict, list[str], str]:
    if theme == "light":
        return CARD_LIGHT, RAMP_LIGHT, RAMP_LIGHT_OTHER
    return CARD_DARK, RAMP_DARK, RAMP_DARK_OTHER


# --- banners -----------------------------------------------------------------
# Slot names are shared; the banner templates reference {{SLOT}} placeholders.

BANNER_DARK = {
    "GROUND_0": "#3a2716", "GROUND_1": "#1b130c", "GROUND_2": "#0b0807",
    "FGROUND_0": "#34230f", "FGROUND_1": "#160f09", "FGROUND_2": "#0b0807",
    "GLOW_0": "#7a5228", "GLOW_0_OP": "0.58",
    "GLOW_1": "#3a2613", "GLOW_1_OP": "0.20",
    "VIGNETTE": "#000000", "VIGNETTE_OP": "0.62", "FVIGNETTE_OP": "0.55",
    "FRAME_0": "#e7c469", "FRAME_1": "#9a7320", "FRAME_2": "#5a3f0e", "FRAME_3": "#2c1f06",
    "FRAME_HI": "#f3e3a6", "FRAME_HI_OP": "0.4", "RAIL_HI_OP": "0.5",
    "FRAME_LINE": "#1a1206",
    "FRAME_SHADOW": "#000000", "FRAME_SHADOW_OP": "0.6",
    "RULE": "#8a6a1e",
    "GILT_0": "#e7c469", "GILT_1": "#9a7320", "GILT_2": "#4a340b",
    "LEAF_0": "#a8412a", "LEAF_1": "#79271a", "LEAF_2": "#401410",
    "LEAF_VEIN": "#360f0b", "LEAF_EDGE": "#d6a24e",
    "BUD_0": "#a23c28", "BUD_1": "#5c1c14",
    "BUD_VEIN": "#3a120d", "BUD_STEM": "#5a2a16",
    "BERRY_0": "#7a241a", "BERRY_1": "#250a08", "BERRY_HI": "#caa05a",
    "STEM": "#6b4423", "STEM_HI": "#a8823f",
    "TEXT_NAME": "#f0e4c8", "TEXT_SUB": "#bda06e", "TEXT_MOTTO": "#c0704c",
    "DIAMOND": "#b8912f",
    "GRAIN_OP": "0.42",
}

BANNER_LIGHT = dict(BANNER_DARK, **{
    "GROUND_0": "#fdf8ea", "GROUND_1": "#f3e9d2", "GROUND_2": "#e2d3b0",
    "FGROUND_0": "#fdf8ea", "FGROUND_1": "#f3e9d2", "FGROUND_2": "#e2d3b0",
    # on parchment the candle becomes a warm bloom rather than a pool of light
    "GLOW_0": "#fff3cf", "GLOW_0_OP": "0.55",
    "GLOW_1": "#f8ecd0", "GLOW_1_OP": "0.25",
    # a burnt-umber edge reads as an aged page; black would read as a bruise
    "VIGNETTE": "#8a6a3a", "VIGNETTE_OP": "0.26", "FVIGNETTE_OP": "0.22",
    "FRAME_0": "#d9a72f", "FRAME_1": "#a8781c", "FRAME_2": "#7a5610", "FRAME_3": "#4a3408",
    "FRAME_HI": "#fff6d0", "FRAME_HI_OP": "0.55", "RAIL_HI_OP": "0.6",
    "FRAME_LINE": "#6b5220",
    "FRAME_SHADOW": "#8a6f3a", "FRAME_SHADOW_OP": "0.5",
    "RULE": "#8a6a1e",
    "GILT_0": "#c9992a", "GILT_1": "#96701c", "GILT_2": "#5c4109",
    # the oxblood botanicals are left alone: red lead and vermilion on vellum is
    # exactly what these motifs were painted with
    "LEAF_EDGE": "#8a5a1e",
    "BERRY_HI": "#e8c98a",
    "STEM": "#5c3a1c", "STEM_HI": "#8a6524",
    "TEXT_NAME": "#2b1e08", "TEXT_SUB": "#6b5320", "TEXT_MOTTO": "#8f3323",
    "DIAMOND": "#9a7520",
    "GRAIN_OP": "0.30",
})


def banners(theme: str) -> dict:
    return BANNER_LIGHT if theme == "light" else BANNER_DARK
