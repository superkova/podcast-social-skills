#!/usr/bin/env python3
"""Thought-Provoking Visual Renderer

Outputs:
  .png  — static 1080x1080 image (always)
  .gif  — animated GIF for LinkedIn upload (if animation present)
  .txt  — LinkedIn caption (if --caption provided)

Canvas: 1080x1080 pixels.

Animation spec (top-level):
  "animation": {
    "tier": "gsap",
    "duration": 5,
    "repeat_delay": 1,
    "timeline": [
      {"target": 0, "to": {"y": 900, "rotate": 15}, "duration": 0.8, "ease": "power2.in"},
      {"target": 1, "to": {"y": 900}, "duration": 0.6, "ease": "power2.in", "delay": 0.15}
    ]
  }
"""

import argparse
import json
import math
import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Error: Pillow is required. Install with: pip install Pillow", file=sys.stderr)
    sys.exit(1)

try:
    import cairosvg
except ImportError:
    cairosvg = None

W, H = 1080, 1080
SCALE = 3
GIF_SIZE = 1080
GIF_FPS = 20
QUOTE_AREA_TOP = 48       # top padding for quote text
QUOTE_AREA_BOTTOM = 180   # y where visual area begins (below quote)


# ──────────────────────────────────────────────
# SVG shape helpers
# ──────────────────────────────────────────────

def _svg_rounded_polygon_path(points, radius, fill='none', stroke='none', sw=0, opacity=1):
    """Generate SVG <path> for polygon with rounded corners."""
    n = len(points)
    if n < 3 or radius <= 0:
        pts_str = ' '.join(f'{p[0]:.2f},{p[1]:.2f}' for p in points)
        op = f' opacity="{opacity}"' if opacity < 1 else ''
        return (f'<polygon points="{pts_str}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{sw}"{op}/>')

    parts = []
    for i in range(n):
        p_prev = points[(i - 1) % n]
        p_curr = points[i]
        p_next = points[(i + 1) % n]
        dx1, dy1 = p_prev[0] - p_curr[0], p_prev[1] - p_curr[1]
        dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        len1 = math.hypot(dx1, dy1)
        len2 = math.hypot(dx2, dy2)
        if len1 == 0 or len2 == 0:
            parts.append(f'L {p_curr[0]:.2f} {p_curr[1]:.2f}')
            continue
        r = min(radius, len1 / 2, len2 / 2)
        start_x = p_curr[0] + dx1 / len1 * r
        start_y = p_curr[1] + dy1 / len1 * r
        end_x = p_curr[0] + dx2 / len2 * r
        end_y = p_curr[1] + dy2 / len2 * r
        cross = dx1 * dy2 - dy1 * dx2
        sweep = 0 if cross > 0 else 1
        if i == 0:
            parts.append(f'M {start_x:.2f} {start_y:.2f}')
        else:
            parts.append(f'L {start_x:.2f} {start_y:.2f}')
        parts.append(f'A {r:.2f} {r:.2f} 0 0 {sweep} {end_x:.2f} {end_y:.2f}')

    parts.append('Z')
    d = ' '.join(parts)
    op = f' opacity="{opacity}"' if opacity < 1 else ''
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{op}/>')


def _svg_shape_element(s):
    """Generate SVG element string for a single shape."""
    opacity = s.get('opacity', 1)
    op = f' opacity="{opacity}"' if opacity < 1 else ''

    if s['type'] == 'circle':
        fill = s.get('fill', 'none')
        stroke = s.get('stroke', 'none')
        sw = s.get('stroke_width', 0)
        return (f'<circle cx="{s["cx"]:.2f}" cy="{s["cy"]:.2f}" r="{s["r"]:.2f}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{op}/>')

    elif s['type'] == 'rect':
        fill = s.get('fill', 'none')
        stroke = s.get('stroke', 'none')
        sw = s.get('stroke_width', 0)
        rot = s.get('rotate', 0)
        radius = s.get('radius', 0)
        if rot:
            cx = s['x'] + s['w'] / 2
            cy = s['y'] + s['h'] / 2
            corners = [(s['x'], s['y']), (s['x'] + s['w'], s['y']),
                       (s['x'] + s['w'], s['y'] + s['h']), (s['x'], s['y'] + s['h'])]
            rad = math.radians(rot)
            rotated = []
            for px, py in corners:
                dx, dy = px - cx, py - cy
                rotated.append((dx * math.cos(rad) - dy * math.sin(rad) + cx,
                                dx * math.sin(rad) + dy * math.cos(rad) + cy))
            return _svg_rounded_polygon_path(rotated, radius, fill, stroke, sw, opacity)
        else:
            rx_attr = f' rx="{radius:.1f}" ry="{radius:.1f}"' if radius else ''
            return (f'<rect x="{s["x"]:.2f}" y="{s["y"]:.2f}" '
                    f'width="{s["w"]:.2f}" height="{s["h"]:.2f}" '
                    f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{rx_attr}{op}/>')

    elif s['type'] == 'line':
        stroke = s.get('stroke', '#000000')
        sw = s.get('stroke_width', 1)
        cap = s.get('cap', 'round')
        return (f'<line x1="{s["x1"]:.2f}" y1="{s["y1"]:.2f}" '
                f'x2="{s["x2"]:.2f}" y2="{s["y2"]:.2f}" '
                f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"{op}/>')

    elif s['type'] == 'polygon':
        fill = s.get('fill', 'none')
        stroke = s.get('stroke', 'none')
        sw = s.get('stroke_width', 0)
        radius = s.get('radius', 0)
        pts = [tuple(p) for p in s['points']]
        return _svg_rounded_polygon_path(pts, radius, fill, stroke, sw, opacity)

    return ''


def _shape_center(s):
    """Get visual center of a shape."""
    if s['type'] == 'circle':
        return s['cx'], s['cy']
    elif s['type'] == 'rect':
        return s['x'] + s['w'] / 2, s['y'] + s['h'] / 2
    elif s['type'] == 'line':
        return (s['x1'] + s['x2']) / 2, (s['y1'] + s['y2']) / 2
    elif s['type'] == 'polygon':
        pts = s['points']
        return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return W / 2, H / 2


# ──────────────────────────────────────────────
# PIL Renderer (shared by PNG and GIF)
# ──────────────────────────────────────────────

def _pil_rounded_polygon(draw, points, radius, fill=None, outline=None, width=0):
    n = len(points)
    if n < 3 or radius <= 0:
        if fill:
            draw.polygon(points, fill=fill)
        if outline and width > 0:
            draw.polygon(points, outline=outline, width=width)
        return

    arc_segments = []
    for i in range(n):
        p_prev = points[(i - 1) % n]
        p_curr = points[i]
        p_next = points[(i + 1) % n]
        dx1, dy1 = p_prev[0] - p_curr[0], p_prev[1] - p_curr[1]
        dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
        len1 = math.hypot(dx1, dy1)
        len2 = math.hypot(dx2, dy2)
        if len1 == 0 or len2 == 0:
            arc_segments.append(None)
            continue
        r = min(radius, len1 / 2, len2 / 2)
        arc_segments.append({
            'start': (p_curr[0] + dx1 / len1 * r, p_curr[1] + dy1 / len1 * r),
            'end': (p_curr[0] + dx2 / len2 * r, p_curr[1] + dy2 / len2 * r),
            'center': p_curr, 'r': r,
        })

    outline_points = []
    for i in range(n):
        seg = arc_segments[i]
        if seg is None:
            outline_points.append(points[i])
            continue
        sx, sy = seg['start']
        ex, ey = seg['end']
        cx, cy = seg['center']
        r = seg['r']
        angle_start = math.atan2(sy - cy, sx - cx)
        angle_end = math.atan2(ey - cy, ex - cx)
        p_prev = points[(i - 1) % n]
        p_next = points[(i + 1) % n]
        dx1, dy1 = p_prev[0] - cx, p_prev[1] - cy
        dx2, dy2 = p_next[0] - cx, p_next[1] - cy
        cross = dx1 * dy2 - dy1 * dx2
        if cross > 0:
            if angle_end > angle_start:
                angle_end -= 2 * math.pi
        else:
            if angle_end < angle_start:
                angle_end += 2 * math.pi
        n_arc = max(4, int(abs(angle_end - angle_start) / (math.pi / 8)))
        for j in range(n_arc + 1):
            t = j / n_arc
            a = angle_start + t * (angle_end - angle_start)
            outline_points.append((cx + r * math.cos(a), cy + r * math.sin(a)))

    if fill and outline_points:
        draw.polygon(outline_points, fill=fill)
    if outline and width > 0 and outline_points:
        for i in range(len(outline_points)):
            p1 = outline_points[i]
            p2 = outline_points[(i + 1) % len(outline_points)]
            draw.line([p1, p2], fill=outline, width=width)


def _render_pil(shapes, bg_color, supersample=SCALE):
    """Render shapes to a PIL Image at W×H. Returns the Image."""
    S = supersample
    img = Image.new('RGB', (W * S, H * S), bg_color)
    draw = ImageDraw.Draw(img)

    for s in shapes:
        if s['type'] == 'circle':
            cx, cy, r = s['cx'] * S, s['cy'] * S, s['r'] * S
            fill = s.get('fill') if s.get('fill', 'none') != 'none' else None
            stroke = s.get('stroke') if s.get('stroke', 'none') != 'none' else None
            sw = max(1, int(s.get('stroke_width', 0) * S)) if stroke else 0
            bbox = [cx - r, cy - r, cx + r, cy + r]
            if fill:
                draw.ellipse(bbox, fill=fill)
            if stroke and sw > 0:
                draw.ellipse(bbox, outline=stroke, width=sw)

        elif s['type'] == 'rect':
            x, y, w, h = s['x'] * S, s['y'] * S, s['w'] * S, s['h'] * S
            fill = s.get('fill') if s.get('fill', 'none') != 'none' else None
            stroke = s.get('stroke') if s.get('stroke', 'none') != 'none' else None
            sw = max(1, int(s.get('stroke_width', 0) * S)) if stroke else 0
            rot = s.get('rotate', 0)
            radius = s.get('radius', 0) * S
            if rot:
                cx_r, cy_r = x + w / 2, y + h / 2
                corners = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                rad = math.radians(rot)
                rotated = [(dx * math.cos(rad) - dy * math.sin(rad) + cx_r,
                            dx * math.sin(rad) + dy * math.cos(rad) + cy_r)
                           for px, py in corners for dx, dy in [(px - cx_r, py - cy_r)]]
                _pil_rounded_polygon(draw, rotated, radius, fill=fill, outline=stroke, width=sw)
            else:
                bbox = [x, y, x + w, y + h]
                if radius > 0:
                    if fill:
                        draw.rounded_rectangle(bbox, radius=radius, fill=fill)
                    if stroke and sw > 0:
                        draw.rounded_rectangle(bbox, radius=radius, outline=stroke, width=sw)
                else:
                    if fill:
                        draw.rectangle(bbox, fill=fill)
                    if stroke and sw > 0:
                        draw.rectangle(bbox, outline=stroke, width=sw)

        elif s['type'] == 'line':
            x1, y1 = s['x1'] * S, s['y1'] * S
            x2, y2 = s['x2'] * S, s['y2'] * S
            stroke = s.get('stroke', '#000000')
            sw = max(1, int(s.get('stroke_width', 1) * S))
            draw.line([(x1, y1), (x2, y2)], fill=stroke, width=sw)
            cap = s.get('cap', 'round')
            if cap == 'round' and sw > 2:
                cap_r = sw / 2
                draw.ellipse([x1 - cap_r, y1 - cap_r, x1 + cap_r, y1 + cap_r], fill=stroke)
                draw.ellipse([x2 - cap_r, y2 - cap_r, x2 + cap_r, y2 + cap_r], fill=stroke)

        elif s['type'] == 'polygon':
            pts = [(p[0] * S, p[1] * S) for p in s['points']]
            fill = s.get('fill') if s.get('fill', 'none') != 'none' else None
            stroke = s.get('stroke') if s.get('stroke', 'none') != 'none' else None
            sw = max(1, int(s.get('stroke_width', 0) * S)) if stroke else 0
            radius = s.get('radius', 0) * S
            _pil_rounded_polygon(draw, pts, radius, fill=fill, outline=stroke, width=sw)

    img = img.resize((W, H), Image.LANCZOS)
    return img


def _wrap_text(text, font, max_width, draw):
    """Wrap text to fit within max_width, return list of lines."""
    words = text.split()
    lines = []
    current = ''
    for word in words:
        test = f'{current} {word}'.strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _load_font(family, size):
    """Load a font by family name, with fallbacks."""
    from PIL import ImageFont
    paths = {
        'courier': ['/Library/Fonts/Courier New.ttf', '/System/Library/Fonts/Courier.dfont'],
        'helvetica': ['/System/Library/Fonts/Helvetica.ttc', '/Library/Fonts/Arial.ttf',
                      '/System/Library/Fonts/SFNSText.ttf'],
    }
    for path in paths.get(family, []):
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _render_quote(img, text, fg_color):
    """Draw quote text at the top of the image, max 2 lines."""
    if not text:
        return img
    draw = ImageDraw.Draw(img)
    max_width = W - 100  # 50px padding each side

    # Start with font size 36, shrink if needed to fit in 2 lines
    for font_size in (36, 32, 28, 24):
        font = _load_font('courier', font_size)
        lines = _wrap_text(text, font, max_width, draw)
        if len(lines) <= 2:
            break

    # Truncate to 2 lines if still too long
    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1][:len(lines[1])-3] + '...'

    c = fg_color.lstrip('#')
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)

    txt_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_layer)

    y = QUOTE_AREA_TOP
    line_height = font_size + 10
    for line in lines:
        bbox = txt_draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2  # center
        txt_draw.text((x, y), line, font=font, fill=(r, g, b, 180))
        y += line_height

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, txt_layer)
    img = img.convert('RGB')
    return img


def _render_watermark(img, text, fg_color):
    """Draw a small watermark in the bottom-right corner of a PIL image."""
    if not text:
        return img
    draw = ImageDraw.Draw(img)
    font_size = 24
    font = _load_font('courier', font_size)
    # Use foreground color at ~40% opacity by mixing with background
    # Since PIL doesn't support text opacity easily on RGB, use RGBA composite
    txt_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    txt_draw = ImageDraw.Draw(txt_layer)
    bbox = txt_draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = W - tw - 32
    y = H - th - 28
    # Parse fg_color hex to RGB
    c = fg_color.lstrip('#')
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    txt_draw.text((x, y), text, font=font, fill=(r, g, b, 100))
    img = img.convert('RGBA')
    img = Image.alpha_composite(img, txt_layer)
    img = img.convert('RGB')
    return img


def _render_png(shapes, bg_color, output_path, watermark=None, quote=None, fg_color='#FFFFFF'):
    img = _render_pil(shapes, bg_color)
    if quote:
        img = _render_quote(img, quote, fg_color)
    if watermark:
        img = _render_watermark(img, watermark, fg_color)
    img.save(output_path, 'PNG', quality=95)


# ──────────────────────────────────────────────
# GSAP timeline renderer
# ──────────────────────────────────────────────

def _svg_quote_text(quote, fg_color):
    """Generate SVG text elements for quote at top of canvas, max 2 lines."""
    if not quote:
        return ''
    # Estimate chars per line at font-size 36 in ~980px width
    # Average char width ~20px at 36px font → ~49 chars per line
    max_chars = 46
    words = quote.split()
    lines = []
    current = ''
    for word in words:
        test = f'{current} {word}'.strip()
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)

    # Cap at 2 lines
    font_size = 36
    if len(lines) > 2:
        # Try smaller estimate
        max_chars = 56
        lines = []
        current = ''
        for word in words:
            test = f'{current} {word}'.strip()
            if len(test) <= max_chars:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        font_size = 28

    if len(lines) > 2:
        lines = lines[:2]
        lines[1] = lines[1][:len(lines[1])-3] + '...'

    tspans = []
    y = QUOTE_AREA_TOP + font_size
    for line in lines:
        tspans.append(f'<tspan x="{W // 2}" y="{y}">{line}</tspan>')
        y += font_size + 10

    return (f'  <text font-family="Courier New, monospace" font-size="{font_size}" '
            f'fill="{fg_color}" opacity="0.7" text-anchor="middle">'
            f'{"".join(tspans)}</text>')


def _gsap_html(shapes, bg_color, anim_spec, watermark=None, quote=None, fg_color='#FFFFFF'):
    """Generate HTML with GSAP timeline animation."""
    duration = anim_spec.get('duration', 5)
    timeline = anim_spec.get('timeline', [])

    svg_elems = []
    for i, s in enumerate(shapes):
        elem = _svg_shape_element(s)
        svg_elems.append(f'      <g id="shape-{i}">{elem}</g>')

    tl_calls = []
    for step in timeline:
        idx = step['target']
        to_props = step.get('to', {})
        dur = step.get('duration', 1)
        ease = step.get('ease', 'power2.inOut')
        delay = step.get('delay', 0)
        stagger = step.get('stagger', 0)

        # Map shape properties to GSAP-compatible SVG transforms
        gsap_props = {}
        for k, v in to_props.items():
            if k in ('x', 'translateX'):
                gsap_props['x'] = v
            elif k in ('y', 'translateY'):
                gsap_props['y'] = v
            elif k == 'rotate':
                gsap_props['rotation'] = v
            elif k == 'scale':
                gsap_props['scale'] = v
            elif k == 'opacity':
                gsap_props['opacity'] = v

        gsap_props['duration'] = dur
        gsap_props['ease'] = ease

        # Target can be a single index or "all"
        if isinstance(idx, str) and idx == 'all':
            selector = '"[id^=shape-]"'
            if stagger:
                gsap_props['stagger'] = stagger
        elif isinstance(idx, list):
            selector = json.dumps([f'#shape-{i}' for i in idx])
            if stagger:
                gsap_props['stagger'] = stagger
        else:
            selector = f'"#shape-{idx}"'

        position = f', "-={abs(delay)}"' if delay < 0 else (f', "+={delay}"' if delay > 0 else '')
        tl_calls.append(f'    tl.to({selector}, {json.dumps(gsap_props)}{position});')

    # Add a repeat with delay to create a clean loop
    repeat_delay = anim_spec.get('repeat_delay', 1)

    html = f'''<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
  * {{ margin: 0; padding: 0; }}
  body {{ width: {W}px; height: {H}px; overflow: hidden; }}
  svg {{ width: {W}px; height: {H}px; display: block; }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
</head>
<body>
<svg id="canvas" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{W}" height="{H}" fill="{bg_color}"/>
{_svg_quote_text(quote, fg_color) if quote else ''}
{chr(10).join(svg_elems)}
  {'<text x="' + str(W - 32) + '" y="' + str(H - 28) + '" font-family="Courier New, monospace" font-size="24" fill="' + fg_color + '" opacity="0.4" text-anchor="end">' + watermark + '</text>' if watermark else ''}
</svg>
<script>
  // Set transform origins to shape centers
  document.querySelectorAll('[id^=shape-]').forEach(g => {{
    const bbox = g.getBBox();
    const cx = bbox.x + bbox.width / 2;
    const cy = bbox.y + bbox.height / 2;
    gsap.set(g, {{ transformOrigin: cx + 'px ' + cy + 'px' }});
  }});

  const tl = gsap.timeline({{ repeat: -1, repeatDelay: {repeat_delay} }});
{chr(10).join(tl_calls)}

  // Signal ready
  window.__ANIM_DURATION = {duration};
  window.__ANIM_READY = true;
</script>
</body></html>'''
    return html


# ──────────────────────────────────────────────
# Easing functions (GSAP-compatible)
# ──────────────────────────────────────────────

def _ease(t, name='power2.inOut'):
    """Apply easing to a 0→1 progress value. Matches GSAP easing names."""
    t = max(0.0, min(1.0, t))
    if name == 'none' or name == 'linear':
        return t

    parts = name.split('.')
    family = parts[0]
    variant = parts[1] if len(parts) > 1 else 'out'

    # Determine power
    powers = {'power1': 2, 'power2': 3, 'power3': 4, 'power4': 5, 'quad': 2, 'cubic': 3, 'quart': 4, 'quint': 5}
    p = powers.get(family, 3)

    if variant == 'in':
        return t ** p
    elif variant == 'out':
        return 1 - (1 - t) ** p
    else:  # inOut
        if t < 0.5:
            return (2 ** (p - 1)) * (t ** p)
        else:
            return 1 - ((-2 * t + 2) ** p) / 2


# ──────────────────────────────────────────────
# Timeline interpolator
# ──────────────────────────────────────────────

def _resolve_timeline(timeline):
    """Resolve timeline steps into absolute start times and return (start, duration, target, to, ease) tuples."""
    resolved = []
    cursor = 0.0  # current end-of-timeline position

    for step in timeline:
        dur = step.get('duration', 1)
        delay = step.get('delay', 0)

        if delay < 0:
            start = max(0, cursor + delay)
        elif delay > 0:
            start = cursor + delay
        else:
            start = cursor

        resolved.append({
            'start': start,
            'duration': dur,
            'target': step['target'],
            'to': step.get('to', {}),
            'ease': step.get('ease', 'power2.inOut'),
            'stagger': step.get('stagger', 0),
        })

        cursor = start + dur

    return resolved


def _interpolate_transforms(resolved_timeline, num_shapes, t):
    """Get per-shape transform dict at time t. Returns list of dicts with x, y, rotate, scale, opacity."""
    transforms = [{'x': 0, 'y': 0, 'rotate': 0, 'scale': 1, 'opacity': 1} for _ in range(num_shapes)]

    for step in resolved_timeline:
        targets = step['target']
        if isinstance(targets, str) and targets == 'all':
            targets = list(range(num_shapes))
        elif isinstance(targets, int):
            targets = [targets]

        stagger = step['stagger']
        for si, idx in enumerate(targets):
            if idx < 0 or idx >= num_shapes:
                continue
            step_start = step['start'] + si * stagger
            step_end = step_start + step['duration']

            if t <= step_start:
                progress = 0.0
            elif t >= step_end:
                progress = 1.0
            else:
                progress = (t - step_start) / step['duration']

            eased = _ease(progress, step['ease'])

            for prop, target_val in step['to'].items():
                prop_key = prop
                if prop in ('translateX',):
                    prop_key = 'x'
                elif prop in ('translateY',):
                    prop_key = 'y'

                if prop_key == 'scale':
                    start_val = 1
                elif prop_key == 'opacity':
                    start_val = 1
                else:
                    start_val = 0

                transforms[idx][prop_key] = start_val + (target_val - start_val) * eased

    return transforms


# ──────────────────────────────────────────────
# CairoSVG frame renderer → GIF
# ──────────────────────────────────────────────

def _build_frame_svg(shapes, bg_color, transforms, watermark=None, quote=None, fg_color='#FFFFFF'):
    """Build an SVG string for a single frame with transforms applied to each shape."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'  <rect width="{W}" height="{H}" fill="{bg_color}"/>',
    ]

    if quote:
        parts.append(_svg_quote_text(quote, fg_color))

    for i, s in enumerate(shapes):
        elem = _svg_shape_element(s)
        tr = transforms[i]
        cx, cy = _shape_center(s)

        # Build SVG transform: translate to center, apply scale+rotate, translate back, then apply x/y offset
        tx = tr.get('x', 0)
        ty = tr.get('y', 0)
        rot = tr.get('rotate', 0)
        sc = tr.get('scale', 1)
        op = tr.get('opacity', 1)

        transform_parts = []
        # Translate by x/y offset
        if tx != 0 or ty != 0:
            transform_parts.append(f'translate({tx:.2f},{ty:.2f})')
        # Rotate and scale around shape center
        if rot != 0:
            transform_parts.append(f'rotate({rot:.2f},{cx:.2f},{cy:.2f})')
        if sc != 1:
            transform_parts.append(f'translate({cx:.2f},{cy:.2f}) scale({sc:.4f}) translate({-cx:.2f},{-cy:.2f})')

        transform_str = f' transform="{" ".join(transform_parts)}"' if transform_parts else ''
        opacity_str = f' opacity="{op:.3f}"' if op < 1 else ''

        parts.append(f'  <g{transform_str}{opacity_str}>{elem}</g>')

    if watermark:
        parts.append(
            f'  <text x="{W - 32}" y="{H - 28}" font-family="Courier New, monospace" '
            f'font-size="24" fill="{fg_color}" opacity="0.4" text-anchor="end">{watermark}</text>'
        )

    parts.append('</svg>')
    return '\n'.join(parts)


def _render_gif_cairosvg(shapes, bg_color, anim_spec, output_path, watermark=None, quote=None, fg_color='#FFFFFF'):
    """Render animation to GIF using CairoSVG for frame rendering (no browser needed)."""
    if cairosvg is None:
        print("Error: cairosvg is required for GIF animation.", file=sys.stderr)
        print("Install with: pip install cairosvg", file=sys.stderr)
        return None

    import io

    duration = anim_spec.get('duration', 5)
    timeline = anim_spec.get('timeline', [])
    repeat_delay = anim_spec.get('repeat_delay', 1)
    total_duration = duration + repeat_delay
    fps = GIF_FPS

    n_frames = int(total_duration * fps)
    n_frames = max(n_frames, 2)

    print(f"  Rendering {n_frames} frames at {fps}fps ({total_duration:.1f}s)...", end=' ', flush=True)

    resolved = _resolve_timeline(timeline)
    frames = []

    for fi in range(n_frames):
        t = fi / fps
        # Clamp to animation duration (frames after duration show final state)
        anim_t = min(t, duration)
        transforms = _interpolate_transforms(resolved, len(shapes), anim_t)

        svg_str = _build_frame_svg(shapes, bg_color, transforms, watermark=watermark, quote=quote, fg_color=fg_color)
        png_data = cairosvg.svg2png(bytestring=svg_str.encode('utf-8'), output_width=GIF_SIZE, output_height=GIF_SIZE)

        img = Image.open(io.BytesIO(png_data)).convert('RGB')
        img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
        frames.append(img)

    if not frames:
        return None

    gif_frame_ms = int(1000 / fps)
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=gif_frame_ms,
        loop=0,
        optimize=True,
    )

    # Check file size — if over 10MB, downscale to 540px
    gif_size = Path(output_path).stat().st_size
    if gif_size > 10 * 1024 * 1024:
        print(f"  GIF too large ({gif_size / 1024 / 1024:.1f}MB), downscaling to 540px...", end=' ', flush=True)
        resized = []
        for frame in frames:
            img = frame.convert('RGB')
            img = img.resize((540, 540), Image.LANCZOS)
            img = img.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            resized.append(img)
        resized[0].save(
            output_path,
            save_all=True,
            append_images=resized[1:],
            duration=gif_frame_ms,
            loop=0,
            optimize=True,
        )

    gif_size = Path(output_path).stat().st_size
    print(f"done ({gif_size / 1024 / 1024:.1f}MB)")
    return output_path


def _get_fg_color(shapes):
    """Extract foreground color from shapes (first stroke or fill found)."""
    for s in shapes:
        for key in ('stroke', 'fill'):
            c = s.get(key)
            if c and c != 'none':
                return c
    return '#FFFFFF'


def _render_gif(shapes, bg_color, anim_spec, output_path, watermark=None, quote=None, fg_color='#FFFFFF'):
    """Render animation to GIF using CairoSVG (no browser needed)."""
    return _render_gif_cairosvg(shapes, bg_color, anim_spec, output_path,
                                watermark=watermark, quote=quote, fg_color=fg_color)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Render shape spec to PNG + animated GIF')
    parser.add_argument('--shapes', required=True, help='Path to JSON shape spec file')
    parser.add_argument('--output', default='output.png', help='Output base path')
    parser.add_argument('--watermark', help='Project name displayed as watermark')
    parser.add_argument('--quote', help='Quote text displayed at top of visual (max 2 lines)')
    parser.add_argument('--caption', help='LinkedIn caption text — saved to .txt')
    args = parser.parse_args()

    with open(args.shapes) as f:
        spec = json.load(f)

    bg = spec.get('bg', '#FFFFFF')
    shapes = spec.get('shapes', [])
    out = Path(args.output)
    fg = _get_fg_color(shapes)

    _render_png(shapes, bg, str(out.with_suffix('.png')),
                watermark=args.watermark, quote=args.quote, fg_color=fg)
    print(f"PNG: {out.with_suffix('.png')}")

    anim_spec = spec.get('animation', {})
    if anim_spec.get('timeline'):
        gif_path = _render_gif(shapes, bg, anim_spec, str(out.with_suffix('.gif')),
                               watermark=args.watermark, quote=args.quote, fg_color=fg)
        if gif_path:
            print(f"GIF: {gif_path}")

    if args.caption:
        txt_path = str(out.with_suffix('.txt'))
        with open(txt_path, 'w') as f:
            f.write(args.caption)
        print(f"Caption: {txt_path}")


if __name__ == '__main__':
    main()
