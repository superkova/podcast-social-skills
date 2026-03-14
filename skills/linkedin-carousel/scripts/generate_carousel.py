#!/usr/bin/env python3
"""
LinkedIn Carousel PDF Generator

Generates a beautifully designed 1080x1080 square PDF carousel
optimized for LinkedIn document posts.

Usage:
    python generate_carousel.py --slides slides.json --palette professional --output carousel.pdf
    python generate_carousel.py --slides slides.json --colors "#1B2838,#00E5A0,#FF6B35" --output carousel.pdf
    python generate_carousel.py --slides slides.json --palette bold --logo logo.png --output carousel.pdf
"""

import argparse
import colorsys
import json
import math
import os
import urllib.request

from reportlab.lib.colors import HexColor, Color
from reportlab.lib.utils import simpleSplit, ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")

GITHUB_FONTS_RAW = "https://raw.githubusercontent.com/google/fonts/main/ofl"

VARIABLE_FONT_URLS = {
    "SpaceGrotesk": f"{GITHUB_FONTS_RAW}/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf",
    "DMSans": f"{GITHUB_FONTS_RAW}/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf",
    "DMSans-Italic": f"{GITHUB_FONTS_RAW}/dmsans/DMSans-Italic%5Bopsz%2Cwght%5D.ttf",
    "Sora": f"{GITHUB_FONTS_RAW}/sora/Sora%5Bwght%5D.ttf",
    "Inter": f"{GITHUB_FONTS_RAW}/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "PlayfairDisplay": f"{GITHUB_FONTS_RAW}/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
}

FONT_INSTANCES = {
    # Space Grotesk - geometric sans (professional)
    "SpaceGrotesk-Bold": ("SpaceGrotesk", {"wght": 700}),
    "SpaceGrotesk-Medium": ("SpaceGrotesk", {"wght": 500}),
    "SpaceGrotesk-Regular": ("SpaceGrotesk", {"wght": 400}),
    "SpaceGrotesk-Light": ("SpaceGrotesk", {"wght": 300}),
    # DM Sans - body text for all palettes
    "DMSans-Regular": ("DMSans", {"wght": 400, "opsz": 14}),
    "DMSans-Medium": ("DMSans", {"wght": 500, "opsz": 14}),
    "DMSans-Bold": ("DMSans", {"wght": 700, "opsz": 14}),
    "DMSans-Italic": ("DMSans-Italic", {"wght": 400, "opsz": 14}),
    # Sora - punchy geometric (bold)
    "Sora-Bold": ("Sora", {"wght": 700}),
    "Sora-SemiBold": ("Sora", {"wght": 600}),
    # Inter - clean modern (modern)
    "Inter-Bold": ("Inter", {"wght": 700, "opsz": 28}),
    "Inter-SemiBold": ("Inter", {"wght": 600, "opsz": 28}),
    # Playfair Display - elegant serif (warm)
    "PlayfairDisplay-Bold": ("PlayfairDisplay", {"wght": 700}),
    "PlayfairDisplay-SemiBold": ("PlayfairDisplay", {"wght": 600}),
}

# Shared body fonts
F_BODY = "DMSans-Regular"
F_BODY_MED = "DMSans-Medium"
F_BODY_BOLD = "DMSans-Bold"
F_BODY_ITALIC = "DMSans-Italic"

PALETTES = {
    "professional": {
        "primary": "#0F1B2D",
        "accent": "#00E5A0",
        "text": "#FFFFFF",
        "muted": "#7B8FA1",
        "highlight_bg": "#00E5A0",
        "highlight_text": "#0F1B2D",
        "headline_font": "SpaceGrotesk-Bold",
        "headline_font_med": "SpaceGrotesk-Medium",
        "decor_num_alpha": 0.15,
        "decor_circle_alpha": 0.10,
    },
    "bold": {
        "primary": "#1A0A2E",
        "accent": "#FF6B35",
        "text": "#FFFFFF",
        "muted": "#9B8FB0",
        "highlight_bg": "#FF6B35",
        "highlight_text": "#FFFFFF",
        "headline_font": "Sora-Bold",
        "headline_font_med": "Sora-SemiBold",
        "decor_num_alpha": 0.18,
        "decor_circle_alpha": 0.12,
    },
    "modern": {
        "primary": "#FAFAFA",
        "accent": "#FF3366",
        "text": "#1A1A1A",
        "muted": "#999999",
        "highlight_bg": "#FF3366",
        "highlight_text": "#FFFFFF",
        "headline_font": "Inter-Bold",
        "headline_font_med": "Inter-SemiBold",
        "decor_num_alpha": 0.08,
        "decor_circle_alpha": 0.06,
    },
    "warm": {
        "primary": "#2D1B69",
        "accent": "#FFD93D",
        "text": "#FFFFFF",
        "muted": "#9B8FC2",
        "highlight_bg": "#FFD93D",
        "highlight_text": "#2D1B69",
        "headline_font": "PlayfairDisplay-Bold",
        "headline_font_med": "PlayfairDisplay-SemiBold",
        "decor_num_alpha": 0.18,
        "decor_circle_alpha": 0.12,
    },
}


# ---------------------------------------------------------------------------
# Color analysis utilities
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_str):
    """Convert '#RRGGBB' to (r, g, b) floats 0-1."""
    h = hex_str.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _rgb_to_hex(r, g, b):
    """Convert (r, g, b) floats 0-1 to '#RRGGBB'."""
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))


def _luminance(hex_str):
    """Relative luminance of a hex color (0=black, 1=white)."""
    r, g, b = _hex_to_rgb(hex_str)
    def lin(c):
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _saturation(hex_str):
    """HSL saturation of a hex color (0-1)."""
    r, g, b = _hex_to_rgb(hex_str)
    _, _, s = colorsys.rgb_to_hls(r, g, b)
    return s


def _contrast_ratio(hex1, hex2):
    """WCAG contrast ratio between two hex colors."""
    l1 = _luminance(hex1) + 0.05
    l2 = _luminance(hex2) + 0.05
    return max(l1, l2) / min(l1, l2)


def _pick_text_color(bg_hex):
    """Return white or near-black text depending on background luminance."""
    return "#FFFFFF" if _luminance(bg_hex) < 0.4 else "#1A1A1A"


def _pick_muted_color(bg_hex, text_hex):
    """Return a muted version of text color for secondary elements."""
    if _luminance(bg_hex) < 0.4:
        # Dark bg: light muted
        r, g, b = _hex_to_rgb(bg_hex)
        return _rgb_to_hex(
            min(1, r + 0.3), min(1, g + 0.3), min(1, b + 0.3)
        )
    else:
        return "#999999"


def _adjust_for_contrast(accent_hex, bg_hex, min_ratio=3.0):
    """Lighten or darken accent color until it has enough contrast with bg."""
    r, g, b = _hex_to_rgb(accent_hex)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    bg_light = _luminance(bg_hex) > 0.4

    for _ in range(20):
        test = _rgb_to_hex(*colorsys.hls_to_rgb(h, l, s))
        if _contrast_ratio(test, bg_hex) >= min_ratio:
            return test
        # Move lightness away from background
        l = max(0, l - 0.05) if bg_light else min(1, l + 0.05)

    return accent_hex


def _pick_highlight_colors(accent_hex, bg_hex):
    """Return (highlight_bg, highlight_text) for pill backgrounds."""
    accent_lum = _luminance(accent_hex)
    # Pill bg is the accent color; text should contrast well against it
    pill_text = "#FFFFFF" if accent_lum < 0.45 else "#1A1A1A"
    # If accent is too close to bg, darken/lighten the pill text further
    if _contrast_ratio(accent_hex, pill_text) < 3.0:
        pill_text = bg_hex
    return accent_hex, pill_text


def _choose_headline_font(bg_hex, accent_hex):
    """Pick a headline font that matches the palette mood."""
    bg_lum = _luminance(bg_hex)
    accent_sat = _saturation(accent_hex)
    _, _, accent_hue_s = colorsys.rgb_to_hls(*_hex_to_rgb(accent_hex))
    accent_h, _, _ = colorsys.rgb_to_hls(*_hex_to_rgb(accent_hex))

    # Light bg -> modern Inter
    if bg_lum > 0.7:
        return "Inter-Bold", "Inter-SemiBold"
    # Warm hues (red/orange/yellow, hue 0-0.15 or 0.8-1.0) + dark bg -> Playfair
    if accent_h < 0.15 or accent_h > 0.8:
        if accent_sat > 0.5:
            return "PlayfairDisplay-Bold", "PlayfairDisplay-SemiBold"
    # High saturation accent -> punchy Sora
    if accent_sat > 0.6:
        return "Sora-Bold", "Sora-SemiBold"
    # Default -> Space Grotesk
    return "SpaceGrotesk-Bold", "SpaceGrotesk-Medium"


def _build_palette_from_colors(colors):
    """
    Build a complete palette dict from a list of hex color strings.

    Strategy:
    - Sort by luminance
    - Darkest color -> background (unless all are light, then lightest -> bg)
    - Most saturated remaining color -> accent
    - Derive text, muted, highlights from those
    - Default to light theme if colors are ambiguous
    """
    if not colors:
        return PALETTES["professional"]

    # Normalize
    colors = [c if c.startswith("#") else f"#{c}" for c in colors]

    # Sort by luminance
    by_lum = sorted(colors, key=_luminance)

    # Decide dark or light theme
    darkest = by_lum[0]
    lightest = by_lum[-1]

    # If darkest color is actually quite light, go light theme
    if _luminance(darkest) > 0.35:
        bg = lightest
    else:
        bg = darkest

    # Pick accent: most saturated color that isn't the background
    remaining = [c for c in colors if c != bg]
    if not remaining:
        remaining = [colors[0]]

    accent = max(remaining, key=lambda c: _saturation(c) + abs(_luminance(c) - _luminance(bg)) * 0.5)

    # Ensure accent has enough contrast against bg
    accent = _adjust_for_contrast(accent, bg, min_ratio=2.5)

    text = _pick_text_color(bg)
    muted = _pick_muted_color(bg, text)
    highlight_bg, highlight_text = _pick_highlight_colors(accent, bg)
    h_font, h_font_med = _choose_headline_font(bg, accent)

    # Decoration alpha: stronger on dark themes
    is_dark = _luminance(bg) < 0.4
    num_alpha = 0.18 if is_dark else 0.08
    circle_alpha = 0.12 if is_dark else 0.06

    return {
        "primary": bg,
        "accent": accent,
        "text": text,
        "muted": muted,
        "highlight_bg": highlight_bg,
        "highlight_text": highlight_text,
        "headline_font": h_font,
        "headline_font_med": h_font_med,
        "decor_num_alpha": num_alpha,
        "decor_circle_alpha": circle_alpha,
    }


def _extract_logo_colors(logo_path, sample_count=5):
    """
    Extract dominant colors from a logo image.
    Returns a list of hex color strings.
    """
    try:
        from PIL import Image
    except ImportError:
        return []

    img = Image.open(logo_path).convert("RGBA")
    # Resize for speed
    img = img.resize((80, 80), Image.LANCZOS)

    # Collect non-transparent, non-white, non-black pixels
    pixels = []
    for r, g, b, a in img.getdata():
        if a < 128:
            continue
        # Skip near-white and near-black
        lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        if 0.08 < lum < 0.92:
            pixels.append((r / 255, g / 255, b / 255))

    if not pixels:
        return []

    # Simple k-means-ish: bucket by hue
    buckets = {}
    for r, g, b in pixels:
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        bucket = int(h * 12)  # 12 hue buckets
        if bucket not in buckets:
            buckets[bucket] = []
        buckets[bucket].append((r, g, b))

    # Take the largest buckets
    sorted_buckets = sorted(buckets.values(), key=len, reverse=True)
    result = []
    for bucket in sorted_buckets[:sample_count]:
        avg_r = sum(p[0] for p in bucket) / len(bucket)
        avg_g = sum(p[1] for p in bucket) / len(bucket)
        avg_b = sum(p[2] for p in bucket) / len(bucket)
        result.append(_rgb_to_hex(avg_r, avg_g, avg_b))

    return result


def _parse_colors_input(colors_arg):
    """
    Parse --colors argument: either comma-separated hex codes or a JSON config file path.
    Config file format: {"colors": ["#hex1", "#hex2", ...]}
    """
    if not colors_arg:
        return []

    # Check if it's a file path
    if os.path.isfile(colors_arg):
        with open(colors_arg) as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("colors", [])
        return []

    # Comma-separated hex codes
    return [c.strip() for c in colors_arg.split(",") if c.strip()]


# ---------------------------------------------------------------------------
# Logo utilities
# ---------------------------------------------------------------------------

def _load_logo(logo_path):
    """Load and return a logo ImageReader, or None if unavailable."""
    if not logo_path or not os.path.isfile(logo_path):
        return None
    try:
        return ImageReader(logo_path)
    except Exception:
        return None


def _get_logo_dimensions(logo_path, max_h=36):
    """Get scaled (width, height) for logo, fitting within max_h."""
    try:
        from PIL import Image
        img = Image.open(logo_path)
        w, h = img.size
        scale = max_h / h
        return int(w * scale), max_h
    except Exception:
        return max_h, max_h


def _draw_logo(c, logo, logo_dims, W, H):
    """Draw logo small in bottom-left, above accent stripe."""
    if not logo:
        return
    lw, lh = logo_dims
    x = 60
    y = 28  # just above the 8pt accent stripe
    c.drawImage(logo, x, y, width=lw, height=lh, mask="auto",
                preserveAspectRatio=True, anchor="sw")


def _ensure_fonts():
    """Download variable Google Fonts and create static weight instances."""
    import io
    from fontTools.ttLib import TTFont as FTFont
    from fontTools.varLib.mutator import instantiateVariableFont

    os.makedirs(FONTS_DIR, exist_ok=True)

    # Check if all instances already exist
    all_present = all(
        os.path.exists(os.path.join(FONTS_DIR, f"{name}.ttf"))
        for name in FONT_INSTANCES
    )
    if all_present:
        return

    # Download variable fonts
    var_fonts = {}
    for family, url in VARIABLE_FONT_URLS.items():
        cache_path = os.path.join(FONTS_DIR, f"_var_{family}.ttf")
        if not os.path.exists(cache_path):
            print(f"Downloading {family} variable font...")
            urllib.request.urlretrieve(url, cache_path)
        var_fonts[family] = cache_path

    # Create static instances
    for name, (family, axes) in FONT_INSTANCES.items():
        target = os.path.join(FONTS_DIR, f"{name}.ttf")
        if not os.path.exists(target):
            print(f"Creating {name}...")
            font = FTFont(var_fonts[family])
            instance = instantiateVariableFont(font, axes)
            instance.save(target)


def _register_fonts():
    """Register all fonts with reportlab."""
    _ensure_fonts()
    for name in FONT_INSTANCES:
        path = os.path.join(FONTS_DIR, f"{name}.ttf")
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
            except Exception:
                pass


def _hex_alpha(hex_color, alpha):
    """Create a Color from hex with alpha."""
    c = HexColor(hex_color)
    return Color(c.red, c.green, c.blue, alpha)


def _draw_text_with_highlights(c, text, highlights, font, size, x, y, max_width, color, accent_bg, accent_text):
    """
    Draw text with highlighted words. Words wrapped in *asterisks* get
    a colored background pill.
    """
    import re

    parts = re.split(r'(\*[^*]+\*)', text)
    lines = []
    current_line = []
    current_width = 0

    for part in parts:
        is_highlight = part.startswith('*') and part.endswith('*')
        word_text = part.strip('*') if is_highlight else part
        words = word_text.split(' ')

        for wi, word in enumerate(words):
            if not word:
                continue
            word_w = pdfmetrics.stringWidth(word + ' ', font, size)
            if current_width + word_w > max_width and current_line:
                lines.append(list(current_line))
                current_line = []
                current_width = 0
            current_line.append({'text': word, 'highlight': is_highlight})
            current_width += word_w

    if current_line:
        lines.append(current_line)

    line_height = size * 1.5
    pill_pad_x = size * 0.3
    pill_pad_y = size * 0.15
    space_w = pdfmetrics.stringWidth(' ', font, size)

    for li, line in enumerate(lines):
        cx = x
        for ti, token in enumerate(line):
            word = token['text']
            word_w = pdfmetrics.stringWidth(word, font, size)

            # Add extra space before highlighted word so pill doesn't overlap previous word
            if token['highlight'] and ti > 0:
                cx += pill_pad_x

            if token['highlight']:
                # Draw highlight pill centered on text
                pill_h = size + pill_pad_y * 2
                # Center pill on text visual center (baseline + 30% of size)
                text_center_y = y - li * line_height + size * 0.3
                pill_bottom = text_center_y - pill_h / 2
                c.setFillColor(HexColor(accent_bg))
                c.roundRect(
                    cx - pill_pad_x,
                    pill_bottom,
                    word_w + pill_pad_x * 2,
                    pill_h,
                    pill_h / 2,
                    fill=1, stroke=0,
                )
                c.setFillColor(HexColor(accent_text))
            else:
                c.setFillColor(HexColor(color))

            c.setFont(font, size)
            c.drawString(cx, y - li * line_height, word)
            cx += word_w + space_w

            # Add extra space after highlighted word so pill doesn't overlap next word
            if token['highlight'] and ti < len(line) - 1:
                cx += pill_pad_x

    return len(lines) * line_height


def _draw_text_centered_with_highlights(c, text, font, size, canvas_w, y_start, max_width, line_height, color, accent_bg, accent_text):
    """
    Draw centered text with highlighted words (for CTA slides).
    Words wrapped in *asterisks* get a colored background pill.
    """
    import re

    parts = re.split(r'(\*[^*]+\*)', text)
    # Build word tokens
    tokens = []
    for part in parts:
        is_highlight = part.startswith('*') and part.endswith('*')
        word_text = part.strip('*') if is_highlight else part
        for word in word_text.split(' '):
            if word:
                tokens.append({'text': word, 'highlight': is_highlight})

    # Word-wrap into lines
    lines = []
    current_line = []
    current_width = 0
    for token in tokens:
        word_w = pdfmetrics.stringWidth(token['text'] + ' ', font, size)
        if current_width + word_w > max_width and current_line:
            lines.append(list(current_line))
            current_line = []
            current_width = 0
        current_line.append(token)
        current_width += word_w
    if current_line:
        lines.append(current_line)

    pill_pad_x = size * 0.3
    pill_pad_y = size * 0.15
    space_w = pdfmetrics.stringWidth(' ', font, size)

    for li, line in enumerate(lines):
        # Measure total line width for centering (including pill spacing)
        line_w = 0
        for ti, token in enumerate(line):
            line_w += pdfmetrics.stringWidth(token['text'], font, size) + space_w
            # Account for extra space around highlighted words
            if token['highlight'] and ti > 0:
                line_w += pill_pad_x
            if token['highlight'] and ti < len(line) - 1:
                line_w += pill_pad_x
        line_w -= space_w  # remove trailing space

        cx = (canvas_w - line_w) / 2
        ly = y_start - li * line_height

        for ti, token in enumerate(line):
            word = token['text']
            word_w = pdfmetrics.stringWidth(word, font, size)

            # Extra space before highlighted word
            if token['highlight'] and ti > 0:
                cx += pill_pad_x

            if token['highlight']:
                pill_h = size + pill_pad_y * 2
                # Center pill on text visual center (baseline + 30% of size)
                text_center_y = ly + size * 0.3
                pill_bottom = text_center_y - pill_h / 2
                c.setFillColor(HexColor(accent_bg))
                c.roundRect(
                    cx - pill_pad_x, pill_bottom,
                    word_w + pill_pad_x * 2, pill_h,
                    pill_h / 2, fill=1, stroke=0,
                )
                c.setFillColor(HexColor(accent_text))
            else:
                c.setFillColor(HexColor(color))
            c.setFont(font, size)
            c.drawString(cx, ly, word)
            cx += word_w + space_w

            # Extra space after highlighted word
            if token['highlight'] and ti < len(line) - 1:
                cx += pill_pad_x


def _draw_underline(c, x, y, width, color, thickness=3):
    """Draw a stylish underline."""
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(thickness)
    c.line(x, y, x + width, y)


def _shorten_url(url):
    """Shorten a long URL to just the base domain for display."""
    from urllib.parse import urlparse
    if not url:
        return "", url
    parsed = urlparse(url if "://" in url else f"https://{url}")
    domain = parsed.netloc or parsed.path.split("/")[0]
    # Remove www. prefix
    if domain.startswith("www."):
        domain = domain[4:]
    # If URL is short enough, show it as-is (without protocol)
    display = url.replace("https://", "").replace("http://", "").rstrip("/")
    if len(display) > 35:
        display = domain
    # Ensure full URL has protocol for hyperlink
    full = url if "://" in url else f"https://{url}"
    return display, full


def _draw_common_elements(c, slide_num, total, W, H, palette,
                          logo=None, logo_dims=None, company=None):
    """Draw elements shared across all slides."""
    # Background
    c.setFillColor(HexColor(palette["primary"]))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Accent stripe at bottom
    c.setFillColor(HexColor(palette["accent"]))
    c.rect(0, 0, W, 8, fill=1, stroke=0)

    # Logo and company name - bottom left, small and subtle
    brand_x = 60
    if logo:
        _draw_logo(c, logo, logo_dims or (36, 36), W, H)
        lw = (logo_dims or (36, 36))[0]
        brand_x = 60 + lw + 12  # position company name after logo

    if company:
        c.setFont(F_BODY_MED, 14)
        c.setFillColor(_hex_alpha(palette["text"], 0.35))
        c.drawString(brand_x, 34, company)

    # Slide counter - bottom right, modern style
    c.setFont(F_BODY_MED, 16)
    c.setFillColor(_hex_alpha(palette["text"], 0.35))
    counter = f"{slide_num}  /  {total}"
    c.drawRightString(W - 60, 36, counter)


def _draw_hook(c, slide, W, H, palette, total):
    """
    Hook slide - dramatic hero typography.
    Big title with highlighted keywords, small subtitle above.
    """
    margin = 80
    h_font = palette["headline_font"]
    circle_a = palette["decor_circle_alpha"]

    # Optional category/tag at top
    if slide.get("subtitle"):
        c.setFont(F_BODY_MED, 20)
        c.setFillColor(HexColor(palette["accent"]))
        tag = slide["subtitle"].upper()
        c.drawString(margin, H - margin - 10, tag)
        # Underline the tag
        tag_w = pdfmetrics.stringWidth(tag, F_BODY_MED, 20)
        _draw_underline(c, margin, H - margin - 18, tag_w, palette["accent"], 2)

    # Main title - massive, left-aligned for impact
    content_w = W - margin * 2
    title_size = 72

    # Adjust size down if title is very long
    title = slide["title"]
    test_lines = simpleSplit(title.replace('*', ''), h_font, title_size, content_w)
    while len(test_lines) > 4 and title_size > 48:
        title_size -= 4
        test_lines = simpleSplit(title.replace('*', ''), h_font, title_size, content_w)

    # Vertically center title, shifted slightly down for visual weight
    line_height = title_size * 1.5
    block_height = len(test_lines) * line_height
    y_start = (H + block_height) / 2 - title_size * 0.15

    _draw_text_with_highlights(
        c, title, [], h_font, title_size,
        margin, y_start, content_w,
        palette["text"], palette["highlight_bg"], palette["highlight_text"],
    )

    # Swipe hint at bottom left
    c.setFont(F_BODY, 20)
    c.setFillColor(_hex_alpha(palette["text"], 0.25))
    c.drawString(margin, 80, "Swipe to read more")
    # Arrow line
    hint_w = pdfmetrics.stringWidth("Swipe to read more  ", F_BODY, 20)
    c.setStrokeColor(_hex_alpha(palette["accent"], 0.4))
    c.setLineWidth(2)
    arrow_x = margin + hint_w
    c.line(arrow_x, 88, arrow_x + 60, 88)
    c.line(arrow_x + 50, 94, arrow_x + 60, 88)
    c.line(arrow_x + 50, 82, arrow_x + 60, 88)

    # Decorative accent dot cluster - top right
    c.setFillColor(_hex_alpha(palette["accent"], circle_a * 1.5))
    c.circle(W - 100, H - 100, 80, fill=1, stroke=0)
    c.setFillColor(_hex_alpha(palette["accent"], circle_a * 0.8))
    c.circle(W - 40, H - 180, 50, fill=1, stroke=0)


def _draw_body(c, slide, slide_num, W, H, palette, total):
    """
    Body slide - alternating layouts for visual variety.
    Even slides: number top-right, content left-aligned
    Odd slides: number top-left, content left-aligned with different decor
    """
    margin = 80
    content_w = W - margin * 2
    variant = slide_num % 3  # 0, 1, 2 for three layout variants
    h_font = palette["headline_font"]
    num_alpha = palette["decor_num_alpha"]
    circle_a = palette["decor_circle_alpha"]

    # --- Draw decorative number ---
    num_str = f"{slide_num:02d}"
    num_size = 160
    c.setFont(h_font, num_size)
    c.setFillColor(_hex_alpha(palette["accent"], num_alpha))

    if variant == 0:
        # Top-right number
        num_w = pdfmetrics.stringWidth(num_str, h_font, num_size)
        c.drawString(W - margin - num_w + 10, H - margin - num_size + 30, num_str)
    elif variant == 1:
        # Top-left number (original position)
        c.drawString(margin - 10, H - margin - num_size + 30, num_str)
    else:
        # Bottom-right, slightly more faded
        num_w = pdfmetrics.stringWidth(num_str, h_font, num_size)
        c.setFillColor(_hex_alpha(palette["accent"], num_alpha * 0.7))
        c.drawString(W - margin - num_w + 10, 60, num_str)

    # --- Accent bar - wider and more visible ---
    c.setFillColor(HexColor(palette["accent"]))
    if variant == 0:
        # Horizontal bar top-left
        c.rect(margin, H - margin - 8, 80, 6, fill=1, stroke=0)
    elif variant == 1:
        # Horizontal bar below number
        c.rect(margin, H - margin - num_size - 10, 80, 6, fill=1, stroke=0)
    else:
        # Horizontal bar at top spanning wider
        c.rect(margin, H - margin - 8, 120, 6, fill=1, stroke=0)

    # --- Measure text content ---
    title_size = 48
    title = slide["title"]
    title_clean = title.replace('*', '')
    title_lines = simpleSplit(title_clean, h_font, title_size, content_w)
    while len(title_lines) > 3 and title_size > 36:
        title_size -= 2
        title_lines = simpleSplit(title_clean, h_font, title_size, content_w)
    title_line_h = title_size * 1.5
    title_block_h = len(title_lines) * title_line_h

    body_size = 30
    body_lines = []
    body_line_h = body_size * 1.65
    body_block_h = 0
    gap_title_body = 40
    if slide.get("body"):
        body_lines = simpleSplit(slide["body"], F_BODY, body_size, content_w)
        body_block_h = len(body_lines) * body_line_h

    # Total height of title + body content
    content_h = title_block_h + (gap_title_body + body_block_h if body_lines else 0)

    # Vertically center content in the slide
    zone_top = H - margin - 80  # leave room for accent bar / number at top
    zone_bottom = 80
    zone_center = (zone_top + zone_bottom) / 2
    # Slight upward bias for optical balance
    title_y = zone_center + content_h / 2 + 20

    # --- Draw content ---

    # Vertical accent line - varies by layout
    c.setStrokeColor(_hex_alpha(palette["accent"], 0.25))
    c.setLineWidth(4)
    line_top = title_y + 8
    line_bottom = title_y - content_h + 8
    if variant == 2:
        # Right-side accent line
        c.line(W - margin + 20, line_top, W - margin + 20, line_bottom)
    else:
        # Left-side accent line
        c.line(margin - 20, line_top, margin - 20, line_bottom)

    # Title
    _draw_text_with_highlights(
        c, title, [], h_font, title_size,
        margin, title_y, content_w,
        palette["text"], palette["highlight_bg"], palette["highlight_text"],
    )

    # Body text
    if body_lines:
        body_y = title_y - title_block_h - gap_title_body + body_size
        c.setFont(F_BODY, body_size)
        c.setFillColor(_hex_alpha(palette["text"], 0.70))
        for j, line in enumerate(body_lines):
            c.drawString(margin, body_y - j * body_line_h, line)

    # --- Decorative elements - vary by slide ---
    if variant == 0:
        # Circle cluster bottom-left
        c.setFillColor(_hex_alpha(palette["accent"], circle_a))
        c.circle(120, 120, 70, fill=1, stroke=0)
        c.setFillColor(_hex_alpha(palette["accent"], circle_a * 0.6))
        c.circle(60, 80, 40, fill=1, stroke=0)
    elif variant == 1:
        # Single circle bottom-right
        c.setFillColor(_hex_alpha(palette["accent"], circle_a))
        c.circle(W - 70, 90, 50, fill=1, stroke=0)
    else:
        # Dot grid top-right
        c.setFillColor(_hex_alpha(palette["accent"], circle_a * 1.5))
        for row in range(3):
            for col in range(3):
                c.circle(W - margin - col * 24, H - margin - row * 24, 4, fill=1, stroke=0)


def _draw_cta(c, slide, W, H, palette, total, url=None):
    """
    CTA slide - centered, impactful question with accent styling.
    Optionally displays a clickable URL.
    """
    margin = 100
    content_w = W - margin * 2
    h_font = palette["headline_font"]
    circle_a = palette["decor_circle_alpha"]

    # Decorative elements - larger, bolder
    c.setFillColor(_hex_alpha(palette["accent"], circle_a * 1.2))
    c.circle(W / 2, H / 2, 300, fill=1, stroke=0)
    c.setFillColor(_hex_alpha(palette["accent"], circle_a * 0.7))
    c.circle(W / 2, H / 2, 400, fill=1, stroke=0)

    # Main CTA text - big and centered, with highlight pills
    title = slide["title"]
    title_size = 56
    title_clean = title.replace('*', '')
    test_lines = simpleSplit(title_clean, h_font, title_size, content_w)
    while len(test_lines) > 3 and title_size > 40:
        title_size -= 2
        test_lines = simpleSplit(title_clean, h_font, title_size, content_w)

    line_height = title_size * 1.5
    block_height = len(test_lines) * line_height
    y_start = (H + block_height) / 2

    # If URL present, shift content up slightly to make room
    if url:
        y_start += 30

    # Use centered highlight rendering
    _draw_text_centered_with_highlights(
        c, title, h_font, title_size,
        W, y_start, content_w, line_height,
        palette["text"], palette["highlight_bg"], palette["highlight_text"],
    )

    # Underline the last line for emphasis
    if test_lines:
        last_line = test_lines[-1]
        last_w = pdfmetrics.stringWidth(last_line, h_font, title_size)
        last_x = (W - last_w) / 2
        last_y = y_start - (len(test_lines) - 1) * line_height
        _draw_underline(c, last_x, last_y - 8, last_w, palette["accent"], 4)

    # Subtitle / CTA instruction
    bottom_y = y_start - len(test_lines) * line_height - 40
    if slide.get("subtitle"):
        c.setFont(F_BODY_MED, 24)
        c.setFillColor(HexColor(palette["accent"]))
        sub_lines = simpleSplit(slide["subtitle"], F_BODY_MED, 24, content_w)
        for j, line in enumerate(sub_lines):
            sw = pdfmetrics.stringWidth(line, F_BODY_MED, 24)
            c.drawString((W - sw) / 2, bottom_y - j * 34, line)
        bottom_y -= len(sub_lines) * 34

    # URL - displayed below subtitle, clickable hyperlink
    if url:
        display_url, full_url = _shorten_url(url)
        url_size = 20
        c.setFont(F_BODY_MED, url_size)
        url_w = pdfmetrics.stringWidth(display_url, F_BODY_MED, url_size)
        url_x = (W - url_w) / 2
        url_y = bottom_y - 30

        # Draw URL text in accent color
        c.setFillColor(_hex_alpha(palette["accent"], 0.7))
        c.drawString(url_x, url_y, display_url)

        # Subtle underline
        _draw_underline(c, url_x, url_y - 4, url_w, palette["accent"], 1.5)

        # Add clickable hyperlink area
        c.linkURL(full_url, (url_x, url_y - 6, url_x + url_w, url_y + url_size + 4))


def create_carousel(slides, palette, output_path, logo_path=None,
                    company=None, url=None):
    """
    Generate a LinkedIn carousel PDF.

    Args:
        slides: list of dicts with keys:
            - type: 'hook' | 'body' | 'cta'
            - title: str (wrap words in *asterisks* to highlight them)
            - body: str (optional, for body slides)
            - subtitle: str (optional, for hook/cta slides)
        palette: dict with palette color keys
        output_path: path to save the PDF
        logo_path: optional path to a logo image
        company: optional company name to display on each slide
        url: optional URL to display on the CTA slide
    """
    _register_fonts()

    # Load logo if provided
    logo = _load_logo(logo_path)
    logo_dims = _get_logo_dimensions(logo_path) if logo else None

    W, H = 1080, 1080
    c = canvas.Canvas(output_path, pagesize=(W, H))
    total = len(slides)

    for i, slide in enumerate(slides):
        _draw_common_elements(c, i + 1, total, W, H, palette,
                              logo, logo_dims, company)

        if slide["type"] == "hook":
            _draw_hook(c, slide, W, H, palette, total)
        elif slide["type"] == "body":
            _draw_body(c, slide, i + 1, W, H, palette, total)
        elif slide["type"] == "cta":
            _draw_cta(c, slide, W, H, palette, total, url=url)

        c.showPage()

    c.save()
    print(f"Carousel saved to: {output_path}")
    print(f"Total slides: {total}")


def main():
    parser = argparse.ArgumentParser(description="Generate a LinkedIn carousel PDF")
    parser.add_argument(
        "--slides", required=True, help="Path to JSON file containing slide data",
    )
    parser.add_argument(
        "--palette", choices=PALETTES.keys(), default=None,
        help="Built-in color palette (professional, bold, modern, warm)",
    )
    parser.add_argument(
        "--colors",
        help='Custom colors: comma-separated hex codes (e.g. "#1B2838,#00E5A0") '
             "or path to a JSON config file",
    )
    parser.add_argument(
        "--logo", help="Path to a logo image (PNG, JPG, SVG) to display on each slide",
    )
    parser.add_argument(
        "--company", help="Company name to display on each slide (small, bottom-left)",
    )
    parser.add_argument(
        "--url", help="URL to display on the CTA slide (auto-shortened if long, full link as hyperlink)",
    )
    parser.add_argument(
        "--output", default="carousel.pdf", help="Output PDF path (default: carousel.pdf)",
    )
    args = parser.parse_args()

    with open(args.slides) as f:
        slides = json.load(f)

    # Build palette
    if args.colors:
        # Custom colors provided
        user_colors = _parse_colors_input(args.colors)
        # If logo provided, extract its colors and merge
        if args.logo:
            logo_colors = _extract_logo_colors(args.logo)
            # User colors take priority, logo colors fill in
            all_colors = user_colors + [c for c in logo_colors if c not in user_colors]
        else:
            all_colors = user_colors
        palette = _build_palette_from_colors(all_colors)
        print(f"Custom palette: bg={palette['primary']}, accent={palette['accent']}, font={palette['headline_font']}")
    elif args.logo and not args.palette:
        # Logo only, no palette or colors - derive from logo
        logo_colors = _extract_logo_colors(args.logo)
        if logo_colors:
            palette = _build_palette_from_colors(logo_colors)
            print(f"Logo-derived palette: bg={palette['primary']}, accent={palette['accent']}, font={palette['headline_font']}")
        else:
            palette = PALETTES["modern"]  # light theme default when unsure
            print("Could not extract logo colors, using modern (light) palette")
    else:
        palette = PALETTES[args.palette or "professional"]

    create_carousel(slides, palette, args.output,
                    logo_path=args.logo, company=args.company, url=args.url)


if __name__ == "__main__":
    main()
