# Publish Podcast

Turn a podcast script into audio using ElevenLabs TTS, upload to Supabase storage, and publish the episode with chapter markers to the artificialpeerreview.com website.

## Trigger

TRIGGER when: the user asks to publish a podcast, generate podcast audio, convert a script to audio, or upload a podcast episode.

## Instructions

You help the user turn a podcast script (markdown) into a published episode. The pipeline has three stages: parse, generate, publish.

### Step 1: Parse and Preview

Before generating audio, parse the script to verify structure:

```bash
python scripts/publish_podcast.py parse \
  --script path/to/podcast-script.md \
  --paper-url "https://example.com/paper"
```

This shows:
- Title and metadata
- Chapter breakdown with dialogue line counts
- Auto-generated SEO description preview

Confirm the structure looks correct before proceeding.

### Step 2: Generate Audio

Convert the script to audio via ElevenLabs:

```bash
python scripts/publish_podcast.py generate \
  --script path/to/podcast-script.md \
  --output-dir publish-podcast/output
```

This:
- Parses the script into chapters and speaker turns
- Sends each dialogue line to ElevenLabs TTS with the correct voice ID (Alex or Thuy)
- Concatenates all audio into a single MP3
- Saves chapter markers (timestamps) to a companion JSON file

**Voice mapping:**
- `**Alex:**` lines → `ELEVENLABS_VOICE_ID_ALEX`
- `**Thuy:**` lines → `ELEVENLABS_VOICE_ID_THUY`

**Output files:**
- `{slug}-{date}.mp3` — full episode audio
- `{slug}-{date}-chapters.json` — chapter timestamps for Spotify/publishing

### Step 3: Publish to Supabase

Upload audio and publish episode metadata:

```bash
python scripts/publish_podcast.py publish \
  --audio path/to/episode.mp3 \
  --paper-url "https://example.com/paper"
```

The episode number is **auto-detected** — it queries the `episodes` table and uses the next number after the highest existing episode. You can override with `--episode-number N` if needed.

This:
1. **Queries** the database for the next episode number
2. **Uploads** the MP3 to Supabase storage (`podcast` bucket, `audio/` folder)
3. **Inserts** an episode record into the `episodes` table with SEO-optimized metadata
4. **Inserts** chapter records into the `chapters` table with timestamps (for Spotify chapter support)
5. Links each chapter to the original paper URL

### Step 4: Confirm to User

After publishing, confirm:
- Episode ID and slug
- Audio URL on Supabase
- Chapter count and total duration
- Link to the live page on artificialpeerreview.com

## Environment Variables

| Variable | Description |
|---|---|
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID_ALEX` | Voice ID for Alex |
| `ELEVENLABS_VOICE_ID_THUY` | Voice ID for Thuy |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key (for storage + DB) |

## Script Format

The script must be a markdown file with this structure:

```markdown
# Episode Title

**Paper:** Paper title
**Authors:** Author names
**Published:** Date

---

## Chapter 1: Chapter Title

**Alex:** Dialogue text...

**Thuy:** Dialogue text...

---

## Chapter 2: Chapter Title

...
```

Key rules:
- Chapter headings use `##` (or `# Chapter N:`)
- Speaker lines start with `**Alex:**` or `**Thuy:**`
- Multi-line dialogue is supported (continuation lines under a speaker)
- The `---` separators between chapters are optional

## Database Tables

**episodes** — One row per published episode:
- `title`, `slug` (unique, URL-safe), `description` (SEO-optimized)
- `audio_url` (Supabase public URL), `duration` (seconds), `file_size` (bytes)
- `published_at`, `episode_number`, `season_number`
- `episode_type` (full/trailer/bonus), `guid` (auto-generated for RSS)

**chapters** — Chapter markers for Spotify/podcast players:
- `episode_id` (FK to episodes), `title`, `start_time_ms`, `end_time_ms`
- `url` (link to original paper), `sort_order`

## SEO Best Practices

### Episode Titles

**Structure:** `[Hook / Benefit] + [Topic]` — make the value obvious in under 60 characters.

- **Make value obvious** — listeners should know what they'll learn immediately
  - Good: `"Why AI Assistants Behave Like Humans: The Persona Selection Model"`
  - Weak: `"Episode 14"` or `"A Conversation About AI"`
- **Use searchable keywords** — include words people actually search for on Spotify, Apple Podcasts, YouTube
  - Good: `"AI Alignment Explained: Personas, Safety, and Deceptive Models"`
  - Weak: `"Masks and Shoggoths"` (clever but unsearchable)
- **Keep under 60 characters** — long titles get truncated on podcast apps
- **Use numbers and clear formats** — numbers signal structure and perform well
  - `"3 Ways AI Models Learn Character (and Why It Matters)"`
- **Highlight paper authors when notable** — lead with them if recognizable
  - `"Anthropic's New Framework for Understanding AI Behavior"`
- **Never lead with episode numbers** — put them at the end if included
  - Bad: `"Episode 32 – AI Safety"`
  - Good: `"AI Safety Through Character Design (Ep. 32)"`

### Episode Descriptions

The auto-generated description includes:
- Paper title and authors (keyword-rich opening)
- Numbered chapter list (scannable, keyword-rich)
- Link to original paper
- Host names and show name
- Website URL

## Important Rules

- ALWAYS parse the script first to verify structure before generating audio
- ALWAYS confirm the audio sounds correct before publishing
- NEVER publish without chapter markers — they're essential for Spotify
- NEVER skip the paper URL — it's included in every chapter record and the description
- If ElevenLabs rate-limits, the script handles retries automatically
- Audio generation can take several minutes for a full episode — set expectations
