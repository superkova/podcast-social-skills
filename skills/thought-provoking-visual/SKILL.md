# Thought-Provoking Visual — LinkedIn Post Generator

Generate a completely unique abstract geometric visual and LinkedIn caption from a short text or idea. Every visual is designed from scratch — no templates, no presets.

## When to use

When the user wants to create a thought-provoking LinkedIn post with an abstract visual — not an infographic, not a quote card, but a genuinely abstract geometric image that creates cognitive tension.

## Dependencies

```bash
pip install Pillow playwright
playwright install chromium
```

## Step 1: Gather input

Ask the user:

1. **What's the idea?** — A short text, quote, or insight (up to 500 characters)
2. **Project name?** — A short name displayed as a watermark on the visual (e.g. "The Growth Lab", "QT Insights"). This brands the visual.
3. **Output folder?** (optional) — Where to save the files. Default: `skills/thought-provoking-visual/output`
4. **Color preference?** (optional) — A mood keyword, or two hex codes. Default: auto-selected based on the quote's emotional texture.

## Step 2: Analyze the idea

Read the text carefully. Before designing anything, identify:

1. **The core tension** — What makes this thought-provoking? Name the two forces, the paradox, the unsettling truth.
2. **The emotional texture** — Is this sharp or soft? Claustrophobic or expansive? Chaotic or precise? Heavy or weightless?
3. **The visual metaphor** — How does the tension map to spatial relationships? Think in terms of: proximity, scale contrast, density, alignment, rhythm, absence, overflow, balance, repetition, interruption.

## Step 3: Choose colors by mood

Pick the mood palette that best matches the emotional texture of the quote. If the user provided colors, use those instead.

| Mood | Background | Foreground | When to use |
|---|---|---|---|
| `stark` | `#FFFFFF` | `#1A1A1A` | Maximum clarity, clinical truth, simple but cutting ideas |
| `night` | `#0A0A0A` | `#F5F5F5` | Heavy, dramatic, existential weight |
| `tension` | `#0F1B2D` | `#00E5A0` | Professional edge, ambition, sharp insight |
| `electric` | `#1A0A2E` | `#FF6B35` | Bold energy, disruption, challenge to norms |
| `signal` | `#FAFAFA` | `#FF3366` | Modern urgency, clean disruption, standing out |
| `depth` | `#2D1B69` | `#FFD93D` | Philosophical, rich, contemplative wisdom |
| `sand` | `#F5E6D3` | `#2C1810` | Warmth, humanity, personal truth, vulnerability |
| `steel` | `#E0E1DD` | `#0D1B2A` | Cold clarity, systems thinking, distance |
| `ember` | `#1A0505` | `#FF4444` | Raw urgency, alarm, uncomfortable truth |
| `forest` | `#0A1A0A` | `#4ADE80` | Growth, organic, natural tension |
| `ocean` | `#0C1222` | `#38BDF8` | Depth, calm but vast, hidden complexity |

### Mood selection guidelines

- Ideas about **conflict, power, ambition** → `tension`, `electric`, or `ember`
- Ideas about **identity, vulnerability, self** → `sand`, `depth`, or `night`
- Ideas about **clarity, truth, simplicity** → `steel`, `signal`, or `tension`
- Ideas about **growth, change, potential** → `forest`, `ocean`, or `electric`
- Ideas about **weight, mortality, existence** → `night`, `depth`, or `ember`
- **Avoid `stark` unless the user specifically requests black and white** — it's too plain for LinkedIn. Prefer palettes with color.
- When in doubt → `tension` (dark blue + green is professional, eye-catching, and works for most ideas)

## Step 4: Design the composition

This is the creative heart. You are designing a unique composition from scratch every single time. There are NO templates. You decide:

- **Which shapes** to use (circles, lines, rectangles, polygons, or combinations)
- **How many** (could be 2 shapes or 200 — whatever the idea demands)
- **What size** each shape is
- **Where** each shape sits on the canvas — **the top 180px is reserved for the quote text**, so design shapes in the y range 180–1040
- **Fill vs stroke** and at what weight
- **Corner rounding** — use `radius` on rects and polygons for softer, more refined shapes
- **The spatial relationships** between shapes — this is where meaning lives

### Translation strategy

Map the idea to geometry through these lenses:

**Duality / Conflict** — Two systems that almost touch but don't, or that overlap and corrupt each other. Could be: ordered grid vs scattered points, circles vs angular shapes, dense region vs sparse region, ascending vs descending patterns.

**Paradox** — Geometry that contradicts itself. Heavy centers that should be light. Expansion that feels like contraction. Properties used in ways that invert expectations.

**Scale / Insignificance** — Absurd size ratios. A massive form held up by something tiny. Infinite repetition shrinking toward nothing. One dot in a vast field.

**Interrupted Pattern** — Build a perfect system, then break it. One rotated element in a grid. A missing line. A shifted row. Almost-symmetry.

**Threshold / Imminence** — Two forms about to collide with a hair's gap. A shape at the tipping point of balance. Something about to happen.

**Containment / Escape** — Something too large for its container. Shapes pressing against walls. A form that has almost escaped but not quite.

**Recursion / Self-reference** — Nested forms. A boundary that is also the bounded thing. Shapes made of smaller versions of themselves.

**Transformation / Morphing** — The idea lives in the *transition between two states*, not in either state alone. Use animation to show one form becoming another. Examples:
- 30+ dots arranged as a perfect square that migrate to form a circle (order → organic, rigid → fluid)
- A tight grid that explodes outward into scattered chaos (structure → disruption)
- Scattered random dots that coalesce into a recognizable geometric form (chaos → pattern)
- A single large shape that fragments into many small pieces (unity → fragmentation)
- Many small shapes that converge into one mass (individuals → collective)

This is one of the most powerful strategies because **the meaning is the motion itself**. The before-state and after-state each tell half the story. "Reshape" = show the reshaping. "Transform" = show the transformation. Don't just illustrate the end result.

**Particle Swarm** — Use 20–80+ identical small shapes (dots, tiny squares) whose *collective arrangement* creates meaning. Each particle is a separate shape with its own animation target. The power comes from:
- **Formation shift**: particles arranged as Shape A animate to positions forming Shape B
- **Density gradients**: tight clusters that thin out, or sparse fields that condense
- **Flow and migration**: particles streaming from one region to another like a current
- **Emergent pattern**: random-looking placement that reveals structure when animated
- **Flocking/swarming**: groups moving together with slight stagger creates organic, living motion

When computing particle positions, use math: place N points along a circle with `(cx + r*cos(2*pi*i/N), cy + r*sin(2*pi*i/N))`, along a grid with row/column math, or along any parametric curve. Animate each particle's `x` and `y` from its start position to its end position. Use stagger (0.02–0.08s per particle) to create wave-like motion rather than everything moving at once.

### Composition rules

These are listed in order of importance. When rules conflict, higher-ranked rules win.

#### 1. Reduction (most important)

Remove everything that doesn't carry meaning. If a shape can be taken out and the idea still reads — take it out. Complexity should come from the idea, never from filling space. The goal is the **minimum number of elements that create maximum tension**. Picasso's bull drawings are the reference: 11 reductions to a single line that is still unmistakably a bull.

**Exception: particle/swarm compositions.** When the idea is about collective behavior, transformation, or emergence, using 30–80+ identical small shapes is not clutter — it's the point. The individual particle is meaningless; the collective pattern carries the idea. In these compositions, reduction means: every particle must contribute to the overall form or motion. Remove any that don't serve the formation.

#### 2. Visual hierarchy

The eye needs an entry point, a journey, and somewhere to rest. **One dominant element, one secondary, everything else subordinate.** Size, contrast, and position create hierarchy — not colour alone. A composition where everything competes equally is exhausting and says nothing.

#### 3. Purposeful negative space

Empty space is not absence — it's an active ingredient. Negative space can be the subject (the gap between two shapes *is* the idea). Crowding destroys tension; breathing room creates it. Think *ma* (間) — the meaningful pause.

#### 4. Contrast creates meaning

Without contrast there is no signal. At least one strong contrast axis should be present in every piece:
- **Scale contrast**: tiny vs vast
- **Density contrast**: packed vs sparse
- **Motion contrast**: still vs moving
- **Geometric contrast**: hard edges vs curves, regular vs irregular

#### 5. The viewer completes the work

Great visuals are slightly unfinished on purpose. Leave a gap the brain wants to close. Imply rather than state — a line pointing toward something off-canvas is more powerful than showing the destination. The moment of completion happens in the viewer's mind, which is why it feels personal.

#### 6. Consistency of visual language

All elements should feel like they belong to the same world. Don't mix sharp geometric precision with loose organic shapes unless the contrast *is* the idea. Stroke weights, proportions, and spacing should feel like they came from the same system. Visual noise comes from inconsistency, not from complexity.

#### 7. One idea per piece

A piece that says three things says nothing. Identify the single core tension and let everything serve it. If two good ideas emerge, that's two pieces. The discipline of one idea is what gives the visual its punch.

#### 8. Composition grammar (know when to break it)

- **Rule of thirds** — tension lives off-centre
- **Golden ratio** — proportions that feel inevitable rather than arbitrary
- **Symmetry is comfort; asymmetry is unease** — choose deliberately
- **Odd numbers** of elements feel more dynamic than even numbers
- **Edge relationships** — shapes near canvas edges create tension with the frame
- **Use rounded corners deliberately** — softer shapes feel human and approachable; sharp corners feel rigid and confrontational. Mix both for contrast.
- Break these rules only when the violation is the point (e.g. rigid perfect symmetry to express suffocation)

### Hard constraints

- Maximum 2 colors (foreground + background from mood palette)
- No text in the visual
- No gradients or shadows
- No recognizable objects — purely abstract geometry
- No decorative elements — every shape must serve the concept
- The visual should create friction or tension, not just be pretty

## Step 5: Add animation

**Every visual MUST be animated.** Animation makes posts stand out on LinkedIn and adds a layer of meaning.

Ask yourself: **"What kind of motion deepens this idea?"** Even ideas that seem static have an implicit time dimension — tension implies something about to move, weight implies gravity, clarity implies something that just resolved.

**Animation-first design:** For many ideas, the animation IS the composition. Don't design a static image and then add movement — design the *transition* as the core concept. The most compelling visuals often have a clear before-state and after-state, with the animation being the meaning. Examples:
- "Reshape" → 40 dots in a square formation animate to circle positions (the reshaping IS the visual)
- "Disruption" → an ordered grid where elements scatter one by one
- "Convergence" → scattered particles flowing into a single point
- "Evolution" → a simple form that progressively gains complexity through animated additions

When the idea is about change, transformation, or process — **the animation should carry 80% of the meaning**. The static frame should look incomplete or ambiguous. Only in motion does the full idea land.

### Animation as meaning, not decoration

Every motion must say something. If you removed the animation and the meaning didn't change, the animation is wrong.

| Motion | What it communicates |
|---|---|
| Slow pulse | Breathing, persistence, something alive beneath stillness |
| Pulse that speeds up and stops | Anxiety, escalation, burnout |
| Two shapes drifting toward each other, forever | Longing, asymptotic closeness |
| Continuous rotation | Restlessness, the inability to be still |
| Slow rotation that reverses | Indecision, oscillation |
| A form expanding then resetting | Dissolution, Sisyphean effort |
| Counter-rotating nested shapes | Internal conflict, opposing forces |
| Slight vibration / jitter | Instability, something about to fail |
| Staggered collapse / domino fall | Systemic failure, cascading consequences |
| Objects falling and bouncing | Entropy, loss of control, fragility |
| Slow stack then sudden scatter | Careful construction undone by chaos |
| Particles migrating from formation A to B | Transformation, identity shift, reshaping |
| Grid dissolving into organic scatter | Loss of structure, freedom, or chaos |
| Scattered dots coalescing into a form | Emergence, convergence, finding order |
| Shape fragmenting into many pieces | Breakdown, deconstruction, analysis |

### GSAP animation spec

Add a top-level `animation` object with `"tier": "gsap"`. Define a `timeline` array where each step targets a shape by index.

```json
{
  "bg": "#0F1B2D",
  "shapes": [
    {"type": "rect", "x": 140, "y": 200, "w": 80, "h": 300, "fill": "#00E5A0", "radius": 8},
    {"type": "rect", "x": 300, "y": 200, "w": 80, "h": 300, "fill": "#00E5A0", "radius": 8},
    {"type": "rect", "x": 460, "y": 200, "w": 80, "h": 300, "fill": "#00E5A0", "radius": 8}
  ],
  "animation": {
    "tier": "gsap",
    "duration": 4,
    "repeat_delay": 2,
    "timeline": [
      {"target": 2, "to": {"y": 500, "rotate": 12}, "duration": 0.6, "ease": "power2.in"},
      {"target": 1, "to": {"y": 480, "rotate": -8}, "duration": 0.5, "ease": "power2.in", "delay": -0.3},
      {"target": 0, "to": {"y": 460, "rotate": 15}, "duration": 0.5, "ease": "power2.in", "delay": -0.3}
    ]
  }
}
```

**Particle swarm example** — 36 dots migrating from a square grid to a circle:

To compute positions, use math in your head or describe the algorithm. For a 6x6 grid centered on (540, 540) with 80px spacing, the positions are `(540 + (col - 2.5)*80, 540 + (row - 2.5)*80)` for row, col in 0–5. For a circle of radius 250, the positions are `(540 + 250*cos(2*pi*i/36), 540 + 250*sin(2*pi*i/36))` for i in 0–35. Each dot's animation `to` is the delta between its grid position and its circle position: `{"x": circle_x - grid_x, "y": circle_y - grid_y}`.

Use a single timeline step targeting all 36 shapes with stagger 0.04s for a wave effect:
```json
{"target": [0,1,2,...,35], "to": {}, "duration": 2, "ease": "power2.inOut", "stagger": 0.04}
```
Since each dot needs different x/y offsets, define separate timeline steps per dot (or per row/group), overlapping with negative delay. For cleaner specs, group dots by row and give each row a staggered step.

**Timeline step properties:**

| Property | Type | Description |
|---|---|---|
| `target` | int, list, or `"all"` | Shape index(es) to animate |
| `to` | object | Target properties: `x`, `y`, `rotate`, `scale`, `opacity` |
| `duration` | seconds | How long this step takes |
| `ease` | string | See easing reference below |
| `delay` | seconds | Offset from previous step. Negative = overlap with previous step. |
| `stagger` | seconds | Delay between each element when target is a list or `"all"` |

**Top-level animation options:**

| Option | Default | Description |
|---|---|---|
| `duration` | 5 | Total animation duration for GIF capture |
| `repeat_delay` | 1 | Pause before looping |

### GSAP best practices

**1. Easing is everything.** The single biggest difference between amateur and professional motion.

| Ease | Feel | When to use |
|---|---|---|
| `power2.out` | Natural, confident, the workhorse | Most motion — elements arriving, settling |
| `power3.out` | Snappier, more decisive | Quick reveals, UI-like precision |
| `power2.in` | Accelerating — feels like falling | Elements leaving, collapse, gravity |
| `sine.inOut` | Gentle, breathing, organic | Pulses, oscillation, anything that needs to feel alive |
| `expo.out` | Dramatic fast-then-slow, cinematic | Big reveals, sudden arrivals |
| `elastic.out(1, 0.5)` | Playful overshoot and settle | Use very sparingly — adds bounce/spring |
| `bounce.out` | Literal bouncing | Physical impact, landing |
| `back.out(1.7)` | Slight overshoot past target | Elements arriving with momentum |
| `none` / `linear` | Mechanical, cold, robotic | Rotation, continuous motion — use intentionally |

Never use the default ease blindly. The wrong ease makes correct timing feel wrong.

**2. Timing ratios matter more than absolute duration.** Secondary elements should take 1.4–1.6× longer than primary ones. Everything the same duration feels robotic.

**3. Stagger with intention.** The stagger amount changes everything:
- **Tight (0.04–0.1s)** — feels like a wave, a system, fabric
- **Medium (0.1–0.2s)** — each element is distinct but connected
- **Loose (0.3–0.5s)** — each element has its own deliberate moment

**4. Use negative delay for overlap.** The offset between timeline steps is where musicality lives:
- `"delay": -0.2` — next step starts 0.2s before previous ends (overlap = flow)
- `"delay": 0.1` — small pause between steps (= breath, separation)
- `"delay": 0` — starts immediately after previous (= mechanical sequence)

**5. The golden rules of motion:**
- **Anticipation** — a tiny move opposite before the main action (pull back before launch)
- **Follow-through** — slight overshoot past the target, settle back
- **Slowest part = most emotional weight** — where you slow down is where the eye lingers
- **Never animate more than 3 things simultaneously** — the eye can't follow

### Animation design principles

- **Keep at least one element static** — the still shape anchors the composition and makes the motion meaningful by contrast
- **Speed**: slow (4–8s) is heavy, meditative, inevitable. Fast (1–2s) is anxious, urgent
- **Synchrony**: shapes moving in sync feel like systems. Slight delay offset creates unease. Full desync creates chaos
- **Stagger**: tight (0.04–0.1s) feels like a wave. Loose (0.3–0.5s) feels deliberate, sequential
- **Overlap**: negative delay between steps creates flow; zero delay feels mechanical; small positive delay creates breath
- **Layer independent rhythms** for complexity: e.g. slow rotation on one element + faster pulse on another + stillness on a third. Phase drift between them creates organic unpredictability

## Step 6: Write the shape spec JSON

Create a JSON file with the exact composition you designed. Canvas is **1080x1080**.

```json
{
  "bg": "#0F1B2D",
  "shapes": [
    {"type": "circle", "cx": 540, "cy": 540, "r": 400, "stroke": "#00E5A0", "stroke_width": 3},
    {"type": "rect", "x": 200, "y": 200, "w": 660, "h": 660, "stroke": "#00E5A0", "stroke_width": 3, "radius": 16},
    {"type": "line", "x1": 540, "y1": 140, "x2": 540, "y2": 940, "stroke": "#00E5A0", "stroke_width": 2.5},
    {"type": "polygon", "points": [[540,300],[700,700],[380,700]], "stroke": "#00E5A0", "stroke_width": 3, "radius": 8}
  ]
}
```

### Shape types

| Type | Required fields | Optional |
|---|---|---|
| `circle` | `cx`, `cy`, `r` | `fill`, `stroke`, `stroke_width`, `opacity` |
| `rect` | `x`, `y`, `w`, `h` | `fill`, `stroke`, `stroke_width`, `rotate` (degrees), `radius` (corner rounding), `opacity` |
| `line` | `x1`, `y1`, `x2`, `y2` | `stroke`, `stroke_width`, `cap` (`round`/`butt`, default: `round`), `opacity` |
| `polygon` | `points` (list of `[x, y]`) | `fill`, `stroke`, `stroke_width`, `radius` (corner rounding), `opacity` |

### Style guidance

- **Stroke widths**: Use **2.5–4** as your baseline. Thinner (1–2) for delicate accents; thicker (5–10) for heavy, dominant elements. Avoid hairline strokes (< 1.5) — they disappear at screen size.
- **Corner rounding** (`radius`): Use **8–20** for subtle softness, **30–60** for clearly rounded shapes. Works on both `rect` and `polygon`. Omit for sharp corners when you want rigid tension.
- **Lines** default to round caps — the ends will be softly capped. Use `"cap": "butt"` for hard-cut line endings.
- **Filled vs stroked shapes** have very different visual weight. A filled circle at r=200 dominates; a stroked one at the same size feels hollow. Mix deliberately.
- **Opacity** (0–1): Use for layered depth — shapes at 0.3–0.5 opacity feel like shadows or echoes.
- Canvas is 1080x1080. (0,0) is top-left. **The quote occupies the top 180px**, so the visual area is y: 180–1040. Center of the visual area is approximately (540, 610).

## Step 6: Write the LinkedIn caption

Write a caption that:
- **Opens with friction** — a provocative statement, counterintuitive claim, or uncomfortable question
- **Expands the tension** — 2-3 sentences that develop the idea without resolving it
- **Doesn't resolve** — leave the reader unsettled, thinking
- Under 200 words
- No hashtags (or 1-2 max at the end)
- No emojis
- Tone: confident, spare, slightly confrontational

## Step 7: Generate 3 options and present

Design **3 distinct compositions** for the same idea. Each should use a different visual metaphor, translation strategy, or spatial approach. Vary the mood palette across the 3 options when it makes sense (not all 3 need different palettes, but avoid making all 3 identical).

### File naming

Generate a unique prefix from the idea to avoid overwriting previous runs:
- Take 2-3 key words from the idea, lowercase, joined by hyphens
- Append a date stamp: `YYYYMMDD`
- Example: idea "Success comes to those too busy to look" → `success-busy-20260305`

All files for one run share the same prefix. The output folder is whatever the user specified (default `skills/thought-provoking-visual/output`).

### Generation steps

1. Create the output folder if it doesn't exist
2. Write 3 shape spec JSON files in the output folder:

```bash
# Example with prefix "success-busy-20260305", watermark "The Growth Lab"
OUT=skills/thought-provoking-visual/output

python skills/thought-provoking-visual/scripts/generate_visual.py \
  --shapes $OUT/success-busy-20260305_option1.json \
  --output $OUT/success-busy-20260305_option1.png \
  --watermark "The Growth Lab" \
  --quote "Success usually comes to those who are too busy to be looking for it."

python skills/thought-provoking-visual/scripts/generate_visual.py \
  --shapes $OUT/success-busy-20260305_option2.json \
  --output $OUT/success-busy-20260305_option2.png \
  --watermark "The Growth Lab" \
  --quote "Success usually comes to those who are too busy to be looking for it."

python skills/thought-provoking-visual/scripts/generate_visual.py \
  --shapes $OUT/success-busy-20260305_option3.json \
  --output $OUT/success-busy-20260305_option3.png \
  --watermark "The Growth Lab" \
  --quote "Success usually comes to those who are too busy to be looking for it."
```

This generates for each option:
- `<prefix>_optionN.png` — 1080x1080 static preview (with watermark)
- `<prefix>_optionN.gif` — 1080x1080 animated GIF for LinkedIn upload (with watermark, max 10MB)

3. Read all 3 generated GIFs to verify they look correct
4. Present to the user:
   - **All 3 GIF visuals** labelled Option 1, 2, 3
   - A one-sentence explanation of each visual metaphor
   - Ask the user to **pick one**
5. Once the user picks, run the renderer again with the caption on the chosen option:

```bash
python skills/thought-provoking-visual/scripts/generate_visual.py \
  --shapes $OUT/success-busy-20260305_optionN.json \
  --output $OUT/success-busy-20260305_final.png \
  --watermark "The Growth Lab" \
  --quote "Success usually comes to those who are too busy to be looking for it." \
  --caption "Your LinkedIn caption text here.

Second paragraph of the caption.

Final line."
```

This produces the final deliverables:
- `<prefix>_final.gif` — the GIF to upload to LinkedIn
- `<prefix>_final.txt` — the caption text for easy copying

6. Present the final output:
   - The **GIF visual**
   - The **LinkedIn caption** in a code block for copying
   - "Upload the .gif to LinkedIn"

## Example thought process

**Input:** "We spend our whole lives building walls, then wonder why we feel alone."

**Analysis:**
- Core tension: protection vs isolation — the thing that saves you traps you
- Emotional texture: claustrophobic, heavy, ironic, personal
- Visual metaphor: containment built by the contained

**Mood:** `sand` — warm, personal, vulnerable

**Design:** A ring of tall, narrow rounded rectangles arranged like a stockade. In the exact center, a single tiny filled circle. The rectangles press inward — the dot is both protected and imprisoned. A narrow gap in the ring: visible but too narrow to pass through. The rounded corners on the bars make them feel almost gentle — walls built with care, which makes the imprisonment more poignant.

**Caption:**
"The first wall is reasonable. Someone hurts you, you build something small. Sensible. Protective.

The second wall is strategic. The third is habitual. By the twentieth, you've built something magnificent — a fortress of lessons learned, boundaries maintained, trust carefully rationed.

And then one Tuesday evening you look around and realize: the architect, the builder, and the prisoner are all the same person.

The walls aren't keeping anything out anymore. They haven't been for years."

**This is NOT a template** — next time, for a different quote about walls, the composition could be completely different. Every quote gets a fresh design. Every time.
