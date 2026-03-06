# Thought-Provoking Visual

Generate abstract geometric animations and LinkedIn captions from a short text or idea. Every visual is designed from scratch — no templates, no presets.

## What it does

Give it a quote or insight. It produces:

- **Animated GIF** (1080x1080) — abstract geometric visual with GSAP-powered animation, ready to upload to LinkedIn
- **PNG** — static preview
- **LinkedIn caption** — thought-provoking text to pair with the visual

The visuals use only 2 colors, no text, no gradients — purely abstract geometry that creates cognitive tension. A project name watermark is rendered in the bottom-right corner.

## Setup

```bash
pip install Pillow playwright
playwright install chromium
```

## Usage

```bash
python scripts/generate_visual.py \
  --shapes path/to/shapes.json \
  --output path/to/output.png \
  --watermark "Your Project Name" \
  --quote "The quote text displayed at the top." \
  --caption "Your LinkedIn caption text."
```

### Arguments

| Flag | Required | Description |
|---|---|---|
| `--shapes` | Yes | Path to JSON shape spec file |
| `--output` | No | Output base path (default: `output.png`) |
| `--watermark` | No | Project name displayed bottom-right at 40% opacity (Courier New) |
| `--quote` | No | Quote text displayed centered at top of visual (max 2 lines, auto-sized) |
| `--caption` | No | LinkedIn caption text — saved to `.txt` file |

### Output files

From a single run with `--output path/to/name.png`:

| File | Description |
|---|---|
| `name.png` | 1080x1080 static image |
| `name.gif` | 1080x1080 animated GIF (if animation present, max 10MB) |
| `name.txt` | LinkedIn caption (if `--caption` provided) |

## Shape spec format

The renderer takes a JSON file describing shapes and animation. Canvas is 1080x1080.

```json
{
  "bg": "#0F1B2D",
  "shapes": [
    {"type": "circle", "cx": 540, "cy": 540, "r": 200, "stroke": "#00E5A0", "stroke_width": 3},
    {"type": "rect", "x": 200, "y": 200, "w": 300, "h": 300, "fill": "#00E5A0", "radius": 16},
    {"type": "line", "x1": 100, "y1": 540, "x2": 980, "y2": 540, "stroke": "#00E5A0", "stroke_width": 2.5},
    {"type": "polygon", "points": [[540,300],[700,700],[380,700]], "stroke": "#00E5A0", "stroke_width": 3, "radius": 8}
  ],
  "animation": {
    "tier": "gsap",
    "duration": 4,
    "repeat_delay": 2,
    "timeline": [
      {"target": 1, "to": {"y": 500, "rotate": 12}, "duration": 0.6, "ease": "power2.in"},
      {"target": 0, "to": {"scale": 1.2}, "duration": 0.8, "ease": "sine.inOut", "delay": -0.3}
    ]
  }
}
```

### Shape types

| Type | Required fields | Optional |
|---|---|---|
| `circle` | `cx`, `cy`, `r` | `fill`, `stroke`, `stroke_width`, `opacity` |
| `rect` | `x`, `y`, `w`, `h` | `fill`, `stroke`, `stroke_width`, `rotate`, `radius`, `opacity` |
| `line` | `x1`, `y1`, `x2`, `y2` | `stroke`, `stroke_width`, `cap` (`round`/`butt`), `opacity` |
| `polygon` | `points` (`[[x,y],...]`) | `fill`, `stroke`, `stroke_width`, `radius`, `opacity` |

### Animation (GSAP timeline)

Animation is defined at the top level with `"tier": "gsap"`. Each timeline step targets shapes by index.

**Timeline step:**

| Property | Type | Description |
|---|---|---|
| `target` | int, list, or `"all"` | Shape index(es) to animate |
| `to` | object | Target: `x`, `y`, `rotate`, `scale`, `opacity` |
| `duration` | number | Seconds |
| `ease` | string | `power2.out`, `power2.in`, `sine.inOut`, `expo.out`, `bounce.out`, `back.out(1.7)`, `elastic.out(1, 0.5)`, `none` |
| `delay` | number | Offset from previous step (negative = overlap) |
| `stagger` | number | Delay between elements when target is list/`"all"` |

**Top-level options:**

| Option | Default | Description |
|---|---|---|
| `duration` | 5 | Total GIF capture duration (seconds) |
| `repeat_delay` | 1 | Pause before loop restarts |

## How it works

1. **Claude** (the AI) analyzes the idea, designs a unique composition, and writes the JSON shape spec + GSAP animation
2. **The renderer** (`generate_visual.py`) is a pure renderer — it takes JSON in and produces PNG + GIF out
3. GIF frames are captured via **Playwright** (headless Chromium) running the GSAP animation, then assembled with **Pillow**

The creative decisions (what shapes, where, how they move, what it means) are made by Claude. The script just renders.

## Mood palettes

11 built-in 2-color palettes matched to emotional texture:

| Mood | Background | Foreground | Feel |
|---|---|---|---|
| `tension` | `#0F1B2D` | `#00E5A0` | Professional edge, sharp insight |
| `electric` | `#1A0A2E` | `#FF6B35` | Bold energy, disruption |
| `signal` | `#FAFAFA` | `#FF3366` | Modern urgency |
| `depth` | `#2D1B69` | `#FFD93D` | Philosophical, contemplative |
| `night` | `#0A0A0A` | `#F5F5F5` | Heavy, existential |
| `sand` | `#F5E6D3` | `#2C1810` | Warm, vulnerable |
| `steel` | `#E0E1DD` | `#0D1B2A` | Cold clarity |
| `ember` | `#1A0505` | `#FF4444` | Raw urgency |
| `forest` | `#0A1A0A` | `#4ADE80` | Growth, organic |
| `ocean` | `#0C1222` | `#38BDF8` | Depth, hidden complexity |
| `stark` | `#FFFFFF` | `#1A1A1A` | Clinical truth |

## Project structure

```
thought-provoking-visual/
├── README.md
├── SKILL.md              # Full instructions for Claude (the AI agent)
├── scripts/
│   └── generate_visual.py  # The renderer
├── output/                # Default output directory
└── tests/
    ├── generate_all.sh    # Render all test specs
    ├── test_gsap_collapse.json
    ├── test_defector.json
    ├── test_ember.json
    ├── test_erosion.json
    ├── test_gravity.json
    ├── test_stockade.json
    └── test_threshold.json
```
