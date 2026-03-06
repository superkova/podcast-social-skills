# LinkedIn Carousel Generator

A Claude skill that transforms text content into beautifully designed PDF carousels optimized for LinkedIn.

## What It Does

Give Claude any text content (up to 3000 characters) and it will:

1. Analyze your content and pick the best carousel format (how-to guide, framework, myth-busting, trends, case study, or human story)
2. Break it into 6-8 slides following LinkedIn best practices
3. Generate a polished 1080x1080 square PDF with professional design elements

## Setup

### Prerequisites

Install the Python PDF library:

```bash
pip install reportlab
```

### Add the Skill to Claude

Add the skill path to your Claude project settings or `.claude/settings.json`:

```json
{
  "skills": [
    "/path/to/linkedin-carousel/SKILL.md"
  ]
}
```

## Usage

Provide your text content and ask Claude to create a carousel:

```
Create a LinkedIn carousel from this:

Remote work isn't just a trend - it's reshaping how companies hire, retain talent,
and build culture. Here are 5 shifts every leader should prepare for in 2026...
```

Claude will:
- Structure the content into hook, body, and CTA slides
- Choose a fitting color palette (Professional, Bold, Modern, or Warm)
- Generate a PDF saved as `carousel-[topic-slug].pdf` in your working directory

Upload the resulting PDF directly to LinkedIn as a document post — LinkedIn renders it as a swipeable carousel in the feed.

## Carousel Design

- **Format:** 1080x1080px square slides (optimal for LinkedIn feed)
- **Slide 1 (Hook):** Bold headline with a clear promise of value
- **Slides 2-N (Body):** One idea per slide, max 50 words, accent bar design
- **Last Slide (CTA):** Question to spark comments + follow prompt
- **Visual elements:** Decorative circles, accent bars, slide counters, bottom stripes

## Color Palettes

| Palette | Best For | Primary Color |
|---------|----------|---------------|
| Professional | Corporate, B2B, leadership | Deep navy |
| Bold | Marketing, startups, announcements | Vibrant orange |
| Modern | Tech, design, innovation | Charcoal + mint |
| Warm | Personal branding, coaching, culture | Purple + yellow |

## Tips for Best Results

- Keep input text focused on a single topic
- Content with clear structure (numbered lists, steps, contrasts) converts best
- Aim for content that fits 6-8 slides — that's the LinkedIn sweet spot
- The skill auto-summarizes if your content is too long for the slide count
