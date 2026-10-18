"""Checks on the design tokens and the self-hosted font."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = ROOT / "site"
STATIC_DIR = SITE_DIR / "static"
TOKENS_PATH = STATIC_DIR / "tokens.css"
FONT_DIR = STATIC_DIR / "fonts"
FONT_FILES = ("SiteSans-subset.woff2", "SiteSerif-subset.woff2")
LICENCE_FILES = ("OFL-SourceSans3.txt", "OFL-SourceSerif4.txt")

FONT_BUDGET_BYTES = 25 * 1024
BASE_FONT_SIZE_PX = 16
VIEWPORT_SMALL_PX = 390
VIEWPORT_LARGE_PX = 1440

# Raw colour syntax. A hex value must not follow a word character, slash or ampersand, so
# page anchors such as href="#main" and character references are not read as colours.
HEX_COLOUR = re.compile(r"(?<![\w/&])#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3,4})\b")
COLOUR_FUNCTION = re.compile(r"\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch)\(", re.IGNORECASE)
COLOUR_SUFFIXES = {".css", ".svg", ".html", ".j2", ".jinja"}


def tokens_css() -> str:
    return TOKENS_PATH.read_text(encoding="utf-8")


def token_hex(name: str) -> str:
    """The first hex value declared for a custom property, which is the fallback value."""
    match = re.search(rf"--{re.escape(name)}:\s*(#[0-9a-fA-F]{{6}})\b", tokens_css())
    assert match, f"--{name} has no hex value in tokens.css"
    return match.group(1)


def rgb(hex_colour: str) -> tuple[int, int, int]:
    return (
        int(hex_colour[1:3], 16),
        int(hex_colour[3:5], 16),
        int(hex_colour[5:7], 16),
    )


def relative_luminance(hex_colour: str) -> float:
    def linear(channel: int) -> float:
        value = channel / 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in rgb(hex_colour))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def srgb_mix(accent: str, surface: str, accent_share: float) -> str:
    mixed = (
        round(accent_share * a + (1 - accent_share) * s)
        for a, s in zip(rgb(accent), rgb(surface), strict=True)
    )
    return "#" + "".join(f"{channel:02x}" for channel in mixed)


def clamp_pixels(name: str, viewport_px: float) -> float:
    """Evaluate a `clamp(min, intercept + slope vw, max)` token at a viewport width."""
    match = re.search(
        rf"--{re.escape(name)}:\s*clamp\(([\d.]+)rem,\s*([\d.]+)rem \+ ([\d.]+)vw,\s*([\d.]+)rem\)",
        tokens_css(),
    )
    assert match, f"--{name} is not a clamp() of rem plus vw"
    minimum, intercept, slope_vw, maximum = (float(group) for group in match.groups())
    preferred = intercept * BASE_FONT_SIZE_PX + slope_vw * viewport_px / 100
    return min(max(preferred, minimum * BASE_FONT_SIZE_PX), maximum * BASE_FONT_SIZE_PX)


def test_no_raw_colour_outside_the_tokens_file() -> None:
    offenders: list[str] = []
    for path in sorted(SITE_DIR.rglob("*")):
        if path == TOKENS_PATH or path.suffix not in COLOUR_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in (HEX_COLOUR, COLOUR_FUNCTION):
            offenders.extend(
                f"{path.relative_to(ROOT)}: {m.group(0)}" for m in pattern.finditer(text)
            )
    assert not offenders, offenders


def test_the_raw_colour_check_catches_a_planted_colour() -> None:
    assert HEX_COLOUR.search("a { color: #1b4fbf; }")
    assert HEX_COLOUR.search('<rect fill="#fff"/>')
    assert COLOUR_FUNCTION.search("a { color: rgb(0 0 0); }")
    assert not HEX_COLOUR.search('<a href="#main">Skip to content</a>')


@pytest.mark.parametrize("name", FONT_FILES)
def test_each_font_subset_is_a_woff2_file_under_the_budget(name: str) -> None:
    data = (FONT_DIR / name).read_bytes()
    assert data[:4] == b"wOF2"
    assert len(data) < FONT_BUDGET_BYTES


@pytest.mark.parametrize("name", LICENCE_FILES)
def test_each_font_licence_ships_beside_the_fonts(name: str) -> None:
    licence = (FONT_DIR / name).read_text(encoding="utf-8")
    assert "SIL Open Font License, Version 1.1" in licence


def test_the_only_fonts_shipped_are_the_two_subsets() -> None:
    assert sorted(path.name for path in FONT_DIR.iterdir()) == sorted(FONT_FILES + LICENCE_FILES)


@pytest.mark.parametrize(
    ("foreground", "minimum"),
    [
        ("ink", 4.5),
        ("ink-muted", 4.5),
        ("accent", 4.5),
        ("positive-variance", 4.5),
        ("negative-variance", 4.5),
        ("rule-strong", 3.0),
    ],
)
def test_token_contrast_against_the_surface(foreground: str, minimum: float) -> None:
    assert contrast_ratio(token_hex(foreground), token_hex("surface")) >= minimum


def test_ink_and_accent_stay_readable_on_the_accent_tints() -> None:
    for tint in ("accent-wash", "accent-tint"):
        assert contrast_ratio(token_hex("ink"), token_hex(tint)) >= 4.5
        assert contrast_ratio(token_hex("accent"), token_hex(tint)) >= 4.5


def test_tint_fallbacks_are_the_srgb_mix_of_accent_and_surface() -> None:
    accent, surface = token_hex("accent"), token_hex("surface")
    assert token_hex("accent-wash") == srgb_mix(accent, surface, 0.06)
    assert token_hex("accent-tint") == srgb_mix(accent, surface, 0.12)


@pytest.mark.parametrize(
    ("name", "small_px", "large_px"),
    [("text-heading", 20, 25), ("text-verdict", 25, 31), ("text-title", 31, 39)],
)
def test_large_type_steps_span_one_step_between_390_and_1440_px(
    name: str, small_px: float, large_px: float
) -> None:
    assert clamp_pixels(name, VIEWPORT_SMALL_PX) == pytest.approx(small_px, abs=0.05)
    assert clamp_pixels(name, VIEWPORT_LARGE_PX) == pytest.approx(large_px, abs=0.05)


def test_fixed_type_steps_are_13_16_and_20_px() -> None:
    sizes = {
        name: float(value) * BASE_FONT_SIZE_PX
        for name, value in re.findall(r"--(text-\w+):\s*([\d.]+)rem;", tokens_css())
    }
    assert sizes == {"text-note": 13, "text-body": 16, "text-subheading": 20}


def test_spacing_steps_are_on_the_4_px_scale() -> None:
    pixels = [
        float(value) * BASE_FONT_SIZE_PX
        for value in re.findall(r"--space-\d:\s*([\d.]+)rem;", tokens_css())
    ]
    assert pixels == [4, 8, 12, 16, 24, 32, 48, 64]
