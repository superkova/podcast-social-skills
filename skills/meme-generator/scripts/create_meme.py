#!/usr/bin/env python3
"""Create memes by overlaying text on template images."""

import argparse
import json
import mimetypes
import os
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote as url_quote

import requests
from PIL import Image, ImageDraw, ImageFont

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
ENV_FILE = SKILL_DIR / ".env"

# Try to find a good font — Impact is the classic meme font
FONT_PATHS = [
    "/System/Library/Fonts/Supplemental/Impact.ttf",
    "/System/Library/Fonts/Impact.ttf",
    "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _find_font():
    for p in FONT_PATHS:
        if Path(p).exists():
            return p
    return None


def _load_env():
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip()
                if key and value and key not in os.environ:
                    os.environ[key] = value


_load_env()


# ── Meme catalog ─────────────────────────────────────────────────────────────

MEMES = {
    "drake": {
        "name": "Drake",
        "template": "drake.jpg",
        "best_for": "Any X vs Y comparison",
        "text_zones": [
            {"label": "reject", "x": 0.5, "y": 0.0, "w": 0.5, "h": 0.5},
            {"label": "prefer", "x": 0.5, "y": 0.5, "w": 0.5, "h": 0.5},
        ],
    },
    "distracted-boyfriend": {
        "name": "Distracted Boyfriend",
        "template": "distracted-boyfriend.jpg",
        "best_for": "Abandoning old thing for new trend",
        "text_zones": [
            {"label": "new_thing", "x": 0.08, "y": 0.6, "w": 0.28, "h": 0.4},
            {"label": "you", "x": 0.42, "y": 0.6, "w": 0.28, "h": 0.4},
            {"label": "old_thing", "x": 0.70, "y": 0.6, "w": 0.28, "h": 0.4},
        ],
    },
    "this-is-fine": {
        "name": "This Is Fine",
        "template": "this-is-fine.jpg",
        "best_for": "Ignoring obvious AI problems/risks",
        "text_zones": [
            {"label": "caption", "x": 0.0, "y": 0.78, "w": 1.0, "h": 0.22},
        ],
    },
    "expanding-brain": {
        "name": "Expanding Brain",
        "template": "expanding-brain.jpg",
        "best_for": "Levels of takes, from basic to unhinged",
        "text_zones": [
            {"label": "level_1", "x": 0.0, "y": 0.0, "w": 0.5, "h": 0.25},
            {"label": "level_2", "x": 0.0, "y": 0.25, "w": 0.5, "h": 0.25},
            {"label": "level_3", "x": 0.0, "y": 0.5, "w": 0.5, "h": 0.25},
            {"label": "level_4", "x": 0.0, "y": 0.75, "w": 0.5, "h": 0.25},
        ],
    },
    "surprised-pikachu": {
        "name": "Surprised Pikachu",
        "template": "surprised-pikachu.jpg",
        "best_for": "Predictable consequences nobody prepared for",
        "text_zones": [
            {"label": "top", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.45, "max_font": 120},
            {"label": "bottom", "x": 0.0, "y": 0.70, "w": 1.0, "h": 0.30, "max_font": 100},
        ],
    },
    "woman-yelling-at-cat": {
        "name": "Woman Yelling at Cat",
        "template": "woman-yelling-at-cat.jpg",
        "best_for": "Two opposing camps arguing",
        "text_zones": [
            {"label": "woman", "x": 0.0, "y": 0.0, "w": 0.5, "h": 0.25},
            {"label": "cat", "x": 0.5, "y": 0.0, "w": 0.5, "h": 0.25},
        ],
    },
    "grus-plan": {
        "name": "Gru's Plan",
        "template": "grus-plan.jpg",
        "best_for": "Strategy that backfires in the last step",
        "text_zones": [
            {"label": "step_1", "x": 0.27, "y": 0.04, "w": 0.22, "h": 0.44},
            {"label": "step_2", "x": 0.77, "y": 0.04, "w": 0.22, "h": 0.44},
            {"label": "step_3", "x": 0.27, "y": 0.53, "w": 0.22, "h": 0.44},
            {"label": "step_4", "x": 0.77, "y": 0.53, "w": 0.22, "h": 0.44},
        ],
    },
    "two-buttons": {
        "name": "Two Buttons",
        "template": "two-buttons.jpg",
        "best_for": "Impossible choices / decision paralysis",
        "text_zones": [
            {"label": "button_1", "x": 0.08, "y": 0.02, "w": 0.38, "h": 0.18, "max_font": 28},
            {"label": "button_2", "x": 0.50, "y": 0.02, "w": 0.38, "h": 0.18, "max_font": 28},
            {"label": "caption", "x": 0.0, "y": 0.82, "w": 1.0, "h": 0.18, "max_font": 36},
        ],
    },
    "nobody": {
        "name": "Nobody / AI",
        "template": "nobody.jpg",
        "best_for": "Unsolicited, unhinged AI outputs",
        "text_zones": [
            {"label": "top", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.15, "max_font": 28},
            {"label": "bottom", "x": 0.0, "y": 0.78, "w": 1.0, "h": 0.22, "max_font": 32},
        ],
    },
    "one-does-not-simply": {
        "name": "One Does Not Simply",
        "template": "one-does-not-simply.jpg",
        "best_for": "\"You can't just automate X...\"",
        "text_zones": [
            {"label": "top", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.25},
            {"label": "bottom", "x": 0.0, "y": 0.75, "w": 1.0, "h": 0.25},
        ],
    },
    "success-kid": {
        "name": "Success Kid",
        "template": "success-kid.jpg",
        "best_for": "Small but real wins with AI",
        "text_zones": [
            {"label": "top", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.25},
            {"label": "bottom", "x": 0.0, "y": 0.75, "w": 1.0, "h": 0.25},
        ],
    },
    "galaxy-brain": {
        "name": "Galaxy Brain",
        "template": "galaxy-brain.jpg",
        "best_for": "Reasoning that sounds smart but is absurd",
        "text_zones": [
            {"label": "level_1", "x": 0.0, "y": 0.0, "w": 0.5, "h": 0.25},
            {"label": "level_2", "x": 0.0, "y": 0.25, "w": 0.5, "h": 0.25},
            {"label": "level_3", "x": 0.0, "y": 0.5, "w": 0.5, "h": 0.25},
            {"label": "level_4", "x": 0.0, "y": 0.75, "w": 0.5, "h": 0.25},
        ],
    },
    "same-picture": {
        "name": "They're The Same Picture",
        "template": "same-picture.jpg",
        "best_for": "False equivalences in AI debates",
        "text_zones": [
            {"label": "left_pic", "x": 0.10, "y": 0.04, "w": 0.32, "h": 0.32, "rotate": -15},
            {"label": "right_pic", "x": 0.58, "y": 0.04, "w": 0.32, "h": 0.32, "rotate": -15},
        ],
    },
    "disaster-girl": {
        "name": "Disaster Girl",
        "template": "disaster-girl.jpg",
        "best_for": "Watching AI chaos unfold, unbothered",
        "text_zones": [
            {"label": "top", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.25},
            {"label": "bottom", "x": 0.0, "y": 0.75, "w": 1.0, "h": 0.25},
        ],
    },
    "change-my-mind": {
        "name": "Change My Mind",
        "template": "change-my-mind.jpg",
        "best_for": "Hot takes about AI/LLMs",
        "text_zones": [
            {"label": "sign", "x": 0.37, "y": 0.55, "w": 0.55, "h": 0.28, "rotate": 7, "max_font": 40},
        ],
    },
    "roll-safe": {
        "name": "Roll Safe",
        "template": "roll-safe.jpg",
        "best_for": "Flawed but confident logic",
        "text_zones": [
            {"label": "top", "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.25},
            {"label": "bottom", "x": 0.0, "y": 0.75, "w": 1.0, "h": 0.25},
        ],
    },
}


# ── Text rendering ───────────────────────────────────────────────────────────


def _fit_text(draw, text, font_path, max_width, max_height, min_size=16, max_size=60):
    """Find the largest font size that fits the text in the given box, and return wrapped lines + font."""
    for size in range(max_size, min_size - 1, -2):
        try:
            font = ImageFont.truetype(font_path, size)
        except Exception:
            font = ImageFont.load_default()

        # Estimate chars per line
        avg_char_w = font.getbbox("A")[2]
        chars_per_line = max(int(max_width / avg_char_w), 1)
        lines = textwrap.wrap(text, width=chars_per_line, break_long_words=False, break_on_hyphens=False)
        if not lines:
            lines = [text]

        # Measure total height
        line_height = font.getbbox("Ay")[3] + 4
        total_height = line_height * len(lines)

        if total_height <= max_height:
            # Check no line exceeds width
            fits = True
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                if bbox[2] - bbox[0] > max_width:
                    fits = False
                    break
            if fits:
                return lines, font, line_height

    # Fallback: smallest size
    try:
        font = ImageFont.truetype(font_path, min_size)
    except Exception:
        font = ImageFont.load_default()
    avg_char_w = font.getbbox("A")[2]
    chars_per_line = max(int(max_width / avg_char_w), 1)
    lines = textwrap.wrap(text, width=chars_per_line, break_long_words=False, break_on_hyphens=False)
    if not lines:
        lines = [text]
    line_height = font.getbbox("Ay")[3] + 4
    return lines, font, line_height


def _render_text_block(text, font_path, max_w, max_h, min_size=16, max_size=60):
    """Render text into a transparent RGBA image that fits within max_w x max_h."""
    # Create a temporary draw for measurement
    tmp = Image.new("RGBA", (1, 1))
    tmp_draw = ImageDraw.Draw(tmp)

    lines, font, line_height = _fit_text(tmp_draw, text, font_path, max_w, max_h, min_size, max_size)

    total_h = line_height * len(lines)
    # Measure widest line
    widest = 0
    for line in lines:
        bbox = tmp_draw.textbbox((0, 0), line, font=font)
        widest = max(widest, bbox[2] - bbox[0])

    # Create text image with padding for outline
    pad = max(3, font.size // 15)
    txt_img = Image.new("RGBA", (widest + pad * 2, total_h + pad * 2), (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_img)

    for i, line in enumerate(lines):
        bbox = txt_draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        lx = pad + (widest - line_w) // 2
        ly = pad + i * line_height

        outline_range = max(2, font.size // 20)
        for dx in range(-outline_range, outline_range + 1):
            for dy in range(-outline_range, outline_range + 1):
                if dx != 0 or dy != 0:
                    txt_draw.text((lx + dx, ly + dy), line, font=font, fill="black")
        txt_draw.text((lx, ly), line, font=font, fill="white")

    return txt_img


def _draw_text_zone(img, text, zone, font_path):
    """Draw text in a zone with white text and black outline. Supports rotation."""
    img_width, img_height = img.size
    x = int(zone["x"] * img_width)
    y = int(zone["y"] * img_height)
    w = int(zone["w"] * img_width)
    h = int(zone["h"] * img_height)
    rotate = zone.get("rotate", 0)

    padding = 10
    max_w = w - padding * 2
    max_h = h - padding * 2

    if max_w < 20 or max_h < 20:
        return

    max_font = zone.get("max_font", 60)
    txt_img = _render_text_block(text, font_path, max_w, max_h, max_size=max_font)

    if rotate:
        txt_img = txt_img.rotate(rotate, expand=True, resample=Image.BICUBIC)

    # Center the text image in the zone
    paste_x = x + (w - txt_img.width) // 2
    paste_y = y + (h - txt_img.height) // 2

    img.paste(txt_img, (paste_x, paste_y), txt_img)


# ── Meme creation ────────────────────────────────────────────────────────────


def create_meme(meme_id: str, texts: list[str], output_path: str) -> str:
    """Create a meme image by overlaying texts on a template.

    Args:
        meme_id: Key from MEMES catalog
        texts: List of text strings, one per text zone
        output_path: Where to save the PNG

    Returns:
        Path to the created image
    """
    if meme_id not in MEMES:
        print(f"Error: Unknown meme '{meme_id}'", file=sys.stderr)
        print(f"Available: {', '.join(sorted(MEMES.keys()))}", file=sys.stderr)
        sys.exit(1)

    meme = MEMES[meme_id]
    template_path = TEMPLATES_DIR / meme["template"]

    if not template_path.exists():
        print(f"Error: Template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    font_path = _find_font()
    if not font_path:
        print("Warning: No Impact/bold font found, using default", file=sys.stderr)

    img = Image.open(template_path).convert("RGBA")

    zones = meme["text_zones"]
    for i, zone in enumerate(zones):
        if i < len(texts) and texts[i].strip():
            _draw_text_zone(img, texts[i].upper(), zone, font_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG")
    print(f"Meme saved: {output_path} ({img.width}x{img.height})")
    return output_path


# ── Supabase upload ──────────────────────────────────────────────────────────


def upload_to_supabase(file_path: str) -> str:
    """Upload meme to Supabase storage and return the public URL."""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set.", file=sys.stderr)
        sys.exit(1)

    path = Path(file_path)
    date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    storage_path = f"content/{date_prefix}/{timestamp}-{path.name}"

    content_type = mimetypes.guess_type(file_path)[0] or "image/png"
    upload_url = f"{supabase_url}/storage/v1/object/podcast/{storage_path}"

    with open(file_path, "rb") as f:
        resp = requests.post(
            upload_url,
            headers={
                "apikey": supabase_key,
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=f,
        )

    if resp.status_code not in (200, 201):
        print(f"Upload error: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    public_url = f"{supabase_url}/storage/v1/object/public/podcast/{url_quote(storage_path, safe='/')}"
    print(f"Uploaded: {public_url}")
    return public_url


# ── CLI ──────────────────────────────────────────────────────────────────────


def cmd_list(args):
    """List all available meme templates."""
    print(f"{'ID':<28} {'Name':<30} Best For")
    print("-" * 90)
    for mid, m in MEMES.items():
        print(f"{mid:<28} {m['name']:<30} {m['best_for']}")


def cmd_create(args):
    """Create a meme from template + texts."""
    texts = args.texts
    output = args.output or f"meme-generator/output/{args.meme}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    create_meme(args.meme, texts, output)


def cmd_upload(args):
    """Upload a meme image to Supabase."""
    upload_to_supabase(args.file)


def main():
    parser = argparse.ArgumentParser(description="AI Meme Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List templates
    subparsers.add_parser("list", help="List available meme templates")

    # Create meme
    p_create = subparsers.add_parser("create", help="Create a meme")
    p_create.add_argument("--meme", required=True, help="Meme template ID (use 'list' to see options)")
    p_create.add_argument("--texts", nargs="+", required=True, help="Text for each zone (in order)")
    p_create.add_argument("--output", help="Output file path (default: auto-generated)")

    # Upload to Supabase
    p_upload = subparsers.add_parser("upload", help="Upload meme to Supabase")
    p_upload.add_argument("--file", required=True, help="Path to meme image")

    args = parser.parse_args()

    if args.command == "list":
        cmd_list(args)
    elif args.command == "create":
        cmd_create(args)
    elif args.command == "upload":
        cmd_upload(args)


if __name__ == "__main__":
    main()
