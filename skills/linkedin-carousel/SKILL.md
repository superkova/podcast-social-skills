# LinkedIn Carousel Generator

Generate a beautifully designed LinkedIn carousel PDF from text content (up to 3000 characters).

## Trigger

TRIGGER when: the user asks to create a LinkedIn carousel, slide deck for LinkedIn, or swipeable post from text content.

## Instructions

You are a LinkedIn carousel designer. Given text content, you will:

### Step 1: Ask about branding (before analyzing content)

Before creating the carousel, ask the user these quick questions:

1. **"What's the name of your company or brand?"** — If provided, it will appear small and subtle on every slide (bottom-left, next to the logo if present). Pass via `--company`.

2. **"Do you have a website URL to include?"** — If provided, it will appear on the CTA (last) slide. Long URLs are auto-shortened to just the base domain for display, but the full URL is embedded as a clickable hyperlink. Pass via `--url`.

3. **"Do you have a logo you'd like on the slides?"** — If yes, ask for the file path. The logo will appear small and subtle on every slide (bottom-left corner). Pass via `--logo`.

4. **"Do you have brand colors or a design style?"** — The user can:
   - Provide hex colors (e.g. `#1B2838, #00E5A0, #FF6B35`)
   - Provide a path to a JSON config file (format: `{"colors": ["#hex1", "#hex2"]}`)
   - Say "no" — you'll use one of the built-in palettes instead

If the user provides colors, the script will auto-analyze them to pick the best background, accent, text, and highlight combinations. If they also provide a logo, the script extracts colors from the logo and blends them with the user's colors for a cohesive look.

If the user has neither custom colors nor a logo, choose the best built-in palette for their content tone.

### Step 2: Analyze and structure the content

1. **Analyze the content** and determine the best carousel type:
   - Step-by-step how-to guide (one step per slide)
   - Framework or numbered list (structured, memorable assets)
   - Myth-busting (each slide debunks a myth with truth + data)
   - Industry trends & predictions (thought leadership)
   - Case study & results (before/after, lessons learned)
   - Behind-the-scenes / human story (personal, trust-building)

2. **Structure the carousel** following this formula:
   - **Slide 1 (Hook):** Bold headline, high-contrast, clear promise of value. Pattern: "5 things I wish I knew about X" or "The truth about X nobody talks about"
   - **Slides 2-N (Body):** One idea per slide, max 2 bullet points, 25-50 words per slide
   - **Last Slide (CTA):** Question to spark comments + subtle call-to-action

3. **Optimal slide count:** 6-8 slides for the sweet spot. Min 3, max 10.

### Step 3: Generate the PDF using the generator script. Follow the design spec below.

## Design System

### Fonts (Google Fonts, auto-downloaded)
Each palette has its own headline font for a distinct visual identity:
- **Space Grotesk** - Bold geometric sans-serif (Professional palette)
- **Sora** - Punchy geometric sans (Bold palette)
- **Inter** - Clean contemporary sans (Modern palette)
- **Playfair Display** - Elegant serif (Warm palette)
- **DM Sans** - Body text and UI elements across all palettes

### Typography Hierarchy
The design uses hero-style typography with dramatic size contrast:
- Decorative slide numbers: 160pt, palette-specific opacity (background texture element)
- Hook title: 72pt headline font (scales down for long titles)
- Body slide title: 48pt headline font
- Body text: 30pt DM Sans Regular, 70% opacity
- Tag/category: 20pt DM Sans Medium, accent color, UPPERCASE with underline
- Slide counter: 16pt DM Sans Medium, 35% opacity, bottom-right

### Color Palettes

#### Option A: Custom colors (user-provided)
When the user provides their own colors, the script auto-analyzes them:
- Darkest color becomes the background (or lightest, if all colors are light)
- Most saturated/contrasting color becomes the accent
- Text, muted, and highlight colors are derived automatically
- Headline font is chosen to match the mood (serif for warm hues, geometric for high-saturation, etc.)
- If a logo is also provided, its dominant colors are extracted and blended in
- Defaults to a light theme when the colors are ambiguous

#### Option B: Built-in palettes (no custom colors)
Choose ONE palette based on content tone:

**Professional** (tech, B2B, leadership):
- Background: #0F1B2D (deep midnight) | Accent: #00E5A0 (electric green)
- Font: Space Grotesk | Highlight pills: green bg with dark text

**Bold** (startups, announcements, hot takes):
- Background: #1A0A2E (dark indigo) | Accent: #FF6B35 (vibrant orange)
- Font: Sora | Highlight pills: orange bg with white text

**Modern** (design, minimal, clean):
- Background: #FAFAFA (near white) | Accent: #FF3366 (hot pink)
- Font: Inter | Dark text on light bg, pink highlights

**Warm** (personal branding, coaching, culture):
- Background: #2D1B69 (rich purple) | Accent: #FFD93D (golden yellow)
- Font: Playfair Display | Highlight pills: yellow bg with purple text

### Visual Elements
- **Decorative circles:** Accent-colored circles at palette-specific opacity for depth (stronger on dark themes)
- **Accent stripe:** 8pt bar at bottom of every slide
- **Accent underlines:** Under tag text and CTA last line
- **Number badge:** Large "01", "02" etc as background design element on body slides (160pt, palette-specific opacity)
- **Highlight pills:** Words wrapped in `*asterisks*` get a rounded pill background in accent color, text vertically centered
- **Visual variety:** Body slides cycle through 3 layout variants (number position, decoration placement, accent line side)

### Slide-Specific Design
- **Hook:** Left-aligned massive title, optional uppercase tag with underline at top, decorative circles top-right
- **Body:** Three alternating layouts — number top-right/top-left/bottom-right, accent bars and decorative elements vary per slide for visual rhythm
- **CTA:** Concentric decorative circles behind centered text, accent underline on last line, subtitle in accent color

## Generation Process

1. Ask the user about logo and brand colors (see Step 1 above)
2. Parse the input text and break it into carousel slides
3. Select the color approach (custom colors, logo-derived, or built-in palette)
4. Write the slide data as a JSON file. Use `*asterisks*` around 1-2 key words per slide to highlight them:

```json
[
  {"type": "hook", "title": "5 Things That *Changed* How I Lead Remote Teams", "subtitle": "Leadership lessons"},
  {"type": "body", "title": "Async-first *communication*", "body": "Replace 80% of meetings with written updates. Your team gets focus time, you get better-documented decisions."},
  {"type": "cta", "title": "What's *your* biggest remote work challenge?", "subtitle": "Follow for more leadership insights"}
]
```

Each slide object has:
- `type`: `"hook"` (first slide), `"body"` (middle slides), or `"cta"` (last slide)
- `title`: main text (wrap 1-2 key words in `*asterisks*` for accent highlight pills)
- `body`: (optional) supporting text for body slides
- `subtitle`: (optional) tag/category for hook, or CTA instruction for last slide

5. Run the generator script located at `scripts/generate_carousel.py` (relative to this skill's directory):

```bash
# With a built-in palette (no custom branding):
python scripts/generate_carousel.py --slides slides.json --palette professional --output carousel-topic.pdf

# With company name and URL:
python scripts/generate_carousel.py --slides slides.json --palette professional --company "Acme Corp" --url "https://acme.com" --output carousel-topic.pdf

# Full branding (logo + company + URL + custom colors):
python scripts/generate_carousel.py --slides slides.json --colors "#1B2838,#00E5A0" --logo logo.png --company "Acme Corp" --url "https://acme.com/blog/post" --output carousel-topic.pdf

# With logo only (colors derived from logo, light theme fallback):
python scripts/generate_carousel.py --slides slides.json --logo logo.png --company "Acme Corp" --output carousel-topic.pdf

# With a built-in palette + logo:
python scripts/generate_carousel.py --slides slides.json --palette bold --logo logo.png --output carousel-topic.pdf
```

**Available flags:**
- `--palette`: `professional`, `bold`, `modern`, `warm`
- `--colors`: comma-separated hex codes (e.g. `"#1B2838,#00E5A0"`), or path to JSON file (`{"colors": ["#hex1", "#hex2"]}`)
- `--logo`: path to PNG, JPG, or other image file
- `--company`: company/brand name shown on every slide (bottom-left)
- `--url`: URL shown on CTA slide (auto-shortened for display, full link as hyperlink)

**Priority:** `--colors` overrides `--palette`. If both `--colors` and `--logo` are given, logo colors are blended in. If only `--logo` is given (no palette or colors), colors are derived from the logo with a light-theme fallback.

6. Clean up the temporary `slides.json` file
7. Confirm the output path to the user

## Output

- Save the PDF to the current working directory as `carousel-[topic-slug].pdf`
- Tell the user the file path and slide count
- Remind them: "Upload this PDF directly to LinkedIn as a document post for the carousel effect"

## Important Rules

- ALWAYS ask the user about logo and brand colors BEFORE generating the carousel
- NEVER exceed 50 words per slide body text
- ALWAYS include a hook slide first and CTA slide last
- ALWAYS check that reportlab, fonttools, and Pillow are installed (`pip install reportlab fonttools Pillow`) before generating
- If the user provides custom colors, use `--colors` instead of `--palette`
- If the user provides a logo path, pass it via `--logo`
- Choose the color palette that best matches the content tone (when no custom colors)
- If the input text is over 3000 characters, summarize it to fit within 6-8 slides
- Each slide must convey exactly ONE clear idea
- Use `*highlights*` sparingly - only 1-2 key words per slide for maximum impact
- Use action verbs and direct language
- Remove filler words ruthlessly
