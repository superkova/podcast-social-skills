# Publish Podcast

Turn a podcast script (markdown) into a published episode on [artificialpeerreview.com](https://artificialpeerreview.com).

## Pipeline

1. **Parse** — Validate script structure, preview chapters and SEO description
2. **Generate** — Convert dialogue to audio via ElevenLabs TTS, concatenate into a single MP3 with chapter timestamps
3. **Publish** — Upload MP3 to Supabase storage, insert episode + chapter records into the database

## Setup

1. Copy `.env` and fill in your credentials:

```
ELEVENLABS_API_KEY=         # ElevenLabs API key
ELEVENLABS_VOICE_ID_ALEX=   # Voice ID for Alex
ELEVENLABS_VOICE_ID_THUY=   # Voice ID for Thuy
SUPABASE_URL=               # Supabase project URL
SUPABASE_SERVICE_ROLE_KEY=  # Supabase secret key (sb_secret_...)
```

2. Install dependencies:

```bash
pip install requests python-dotenv
```

## Usage

```bash
# Step 1: Parse and preview
python scripts/publish_podcast.py parse \
  --script path/to/podcast-script.md \
  --paper-url "https://example.com/paper"

# Step 2: Generate audio
python scripts/publish_podcast.py generate \
  --script path/to/podcast-script.md \
  --output-dir publish-podcast/output

# Step 3: Publish
python scripts/publish_podcast.py publish \
  --audio path/to/episode.mp3 \
  --paper-url "https://example.com/paper" \
  --episode-number 1 \
  --season-number 1
```

## Script Format

Scripts must be markdown with `##` chapter headings and `**Alex:**` / `**Thuy:**` speaker lines. See `SKILL.md` for the full format spec.

## Database

- **episodes** — Episode metadata (title, slug, description, audio URL, duration)
- **chapters** — Chapter markers with timestamps for Spotify chapter support

Both tables live in the same Supabase project used by `linkedin-posting`.
