#!/usr/bin/env python3
"""Turn a podcast script into audio via ElevenLabs, upload to Supabase, and publish episode metadata."""

import argparse
import json
import mimetypes
import os
import re
import struct
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote as url_quote

import requests

# ── Config ────────────────────────────────────────────────────────────────────

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR.parent / ".env"

ELEVENLABS_API = "https://api.elevenlabs.io/v1"
ELEVENLABS_MODEL = "eleven_multilingual_v2"


def _load_env():
    """Load .env file from the publish-podcast directory if it exists."""
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


def _get_env(name: str) -> str:
    val = os.environ.get(name)
    if not val:
        print(f"Error: {name} environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return val


# ── Script parsing ────────────────────────────────────────────────────────────


def parse_script(script_path: str) -> dict:
    """Parse a podcast script markdown file into structured data.

    Returns:
        {
            "title": str,
            "metadata": {header lines},
            "chapters": [
                {"title": str, "lines": [{"speaker": str, "text": str}, ...]}
            ]
        }
    """
    text = Path(script_path).read_text(encoding="utf-8")
    lines = text.split("\n")

    title = ""
    metadata = {}
    chapters = []
    current_chapter = None
    current_speaker = None
    current_text_parts = []

    def _flush_speaker():
        nonlocal current_speaker, current_text_parts
        if current_speaker and current_text_parts:
            full_text = " ".join(current_text_parts).strip()
            if full_text and current_chapter is not None:
                current_chapter["lines"].append(
                    {"speaker": current_speaker, "text": full_text}
                )
        current_speaker = None
        current_text_parts = []

    for line in lines:
        stripped = line.strip()

        # Top-level title
        if stripped.startswith("# ") and not title:
            title = stripped[2:].strip()
            continue

        # Metadata lines like **Paper:** ...
        meta_match = re.match(r"\*\*(.+?):\*\*\s*(.+)", stripped)
        if meta_match and not chapters:
            metadata[meta_match.group(1).strip()] = meta_match.group(2).strip()
            continue

        # Chapter headings (## or # within body)
        chapter_match = re.match(r"^#{1,2}\s+(?:Chapter\s+\d+:\s*)?(.+)", stripped)
        if chapter_match and (
            stripped.startswith("## ")
            or (stripped.startswith("# ") and title)
        ):
            _flush_speaker()
            current_chapter = {"title": chapter_match.group(1).strip(), "lines": []}
            chapters.append(current_chapter)
            continue

        # Speaker lines: **Alex:** or **Thuy:**
        speaker_match = re.match(r"^\*\*(\w+):\*\*\s*(.*)", stripped)
        if speaker_match:
            _flush_speaker()
            current_speaker = speaker_match.group(1)
            remainder = speaker_match.group(2).strip()
            if remainder:
                current_text_parts.append(remainder)
            continue

        # Continuation of current speaker's dialogue
        if current_speaker and stripped:
            current_text_parts.append(stripped)

        # Blank line — could be paragraph break within speaker
        if not stripped and current_speaker:
            current_text_parts.append("")

    _flush_speaker()

    return {"title": title, "metadata": metadata, "chapters": chapters}


# ── ElevenLabs TTS ────────────────────────────────────────────────────────────


def _tts_segment(text: str, voice_id: str, api_key: str) -> bytes:
    """Generate audio for a text segment using ElevenLabs API. Returns MP3 bytes."""
    resp = requests.post(
        f"{ELEVENLABS_API}/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "text": text,
            "model_id": ELEVENLABS_MODEL,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True,
            },
        },
        stream=True,
    )

    if resp.status_code != 200:
        print(f"ElevenLabs error: {resp.status_code} {resp.text[:500]}", file=sys.stderr)
        sys.exit(1)

    audio = b""
    for chunk in resp.iter_content(chunk_size=8192):
        audio += chunk
    return audio


def _get_mp3_duration_ms(data: bytes) -> int:
    """Estimate MP3 duration in milliseconds from raw bytes.

    Uses file size and assumed bitrate (128kbps) as fallback.
    """
    # Try to find bitrate from first MP3 frame header
    bitrate_kbps = 128  # default assumption
    for i in range(min(len(data) - 4, 4096)):
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            # Found sync word
            version_bits = (data[i + 1] >> 3) & 0x03
            bitrate_idx = (data[i + 2] >> 4) & 0x0F
            # MPEG1 Layer 3 bitrate table
            mpeg1_l3 = [0, 32, 40, 48, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0, 0]
            if version_bits == 3 and 1 <= bitrate_idx <= 14:
                bitrate_kbps = mpeg1_l3[bitrate_idx]
            break

    duration_s = (len(data) * 8) / (bitrate_kbps * 1000)
    return int(duration_s * 1000)


def generate_audio(parsed: dict, output_dir: str) -> tuple[str, list[dict]]:
    """Generate audio for each chapter and concatenate into a single MP3.

    Returns (output_path, chapter_markers) where chapter_markers is
    [{"title": str, "start_time_ms": int, "end_time_ms": int}, ...]
    """
    api_key = _get_env("ELEVENLABS_API_KEY")
    voice_alex = _get_env("ELEVENLABS_VOICE_ID_ALEX")
    voice_thuy = _get_env("ELEVENLABS_VOICE_ID_THUY")

    voice_map = {"Alex": voice_alex, "Thuy": voice_thuy}

    all_audio = b""
    chapter_markers = []
    current_ms = 0

    for ch_idx, chapter in enumerate(parsed["chapters"]):
        chapter_start_ms = current_ms
        print(f"Generating audio for: {chapter['title']}")

        for line in chapter["lines"]:
            speaker = line["speaker"]
            text = line["text"].strip()
            if not text:
                continue

            voice_id = voice_map.get(speaker)
            if not voice_id:
                print(f"Warning: Unknown speaker '{speaker}', skipping.", file=sys.stderr)
                continue

            # ElevenLabs has a ~5000 char limit per request, split if needed
            chunks = _split_text(text, max_chars=4500)
            for chunk in chunks:
                audio_bytes = _tts_segment(chunk, voice_id, api_key)
                duration = _get_mp3_duration_ms(audio_bytes)
                all_audio += audio_bytes
                current_ms += duration

        chapter_markers.append(
            {
                "title": chapter["title"],
                "start_time_ms": chapter_start_ms,
                "end_time_ms": current_ms,
                "sort_order": ch_idx,
            }
        )
        print(f"  Chapter {ch_idx + 1} done: {(current_ms - chapter_start_ms) / 1000:.1f}s")

    # Write combined audio
    slug = _slugify(parsed["title"])
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    filename = f"{slug}-{date_str}.mp3"
    output_path = str(Path(output_dir) / filename)

    with open(output_path, "wb") as f:
        f.write(all_audio)

    total_s = current_ms / 1000
    print(f"\nTotal audio: {total_s:.0f}s ({total_s / 60:.1f} min), {len(all_audio) / 1024 / 1024:.1f} MB")
    print(f"Saved to: {output_path}")

    return output_path, chapter_markers


def _split_text(text: str, max_chars: int = 4500) -> list[str]:
    """Split text into chunks at sentence boundaries."""
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""
    sentences = re.split(r"(?<=[.!?])\s+", text)

    for sentence in sentences:
        if len(current) + len(sentence) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sentence
        else:
            current = f"{current} {sentence}" if current else sentence

    if current.strip():
        chunks.append(current.strip())

    return chunks


# ── Supabase upload ───────────────────────────────────────────────────────────


def upload_to_supabase(file_path: str, bucket: str, folder: str) -> str:
    """Upload a local file to Supabase storage and return the public URL."""
    supabase_url = _get_env("SUPABASE_URL")
    supabase_key = _get_env("SUPABASE_SERVICE_ROLE_KEY")

    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    storage_name = f"{timestamp}-{path.name}"
    storage_path = f"{folder}/{date_prefix}/{storage_name}"

    content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
    upload_url = f"{supabase_url}/storage/v1/object/{bucket}/{storage_path}"

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
        print(f"Error uploading to Supabase: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{url_quote(storage_path, safe='/')}"
    print(f"Uploaded: {public_url}")
    return public_url


# ── Supabase database publish ─────────────────────────────────────────────────


def _supabase_rest(method: str, table: str, data: dict | list, returning: bool = True) -> dict:
    """Make a request to Supabase PostgREST API."""
    supabase_url = _get_env("SUPABASE_URL")
    supabase_key = _get_env("SUPABASE_SERVICE_ROLE_KEY")

    url = f"{supabase_url}/rest/v1/{table}"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }
    if returning:
        headers["Prefer"] = "return=representation"

    resp = getattr(requests, method)(url, headers=headers, json=data)

    if resp.status_code not in (200, 201):
        print(f"Supabase DB error ({table}): {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()


def _next_episode_number() -> int:
    """Query the episodes table and return the next episode number."""
    supabase_url = _get_env("SUPABASE_URL")
    supabase_key = _get_env("SUPABASE_SERVICE_ROLE_KEY")

    resp = requests.get(
        f"{supabase_url}/rest/v1/episodes?select=episode_number&order=episode_number.desc&limit=1",
        headers={
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
        },
    )

    if resp.status_code != 200:
        print(f"Warning: Could not query episodes table: {resp.status_code}", file=sys.stderr)
        return 1

    rows = resp.json()
    if not rows or rows[0].get("episode_number") is None:
        return 1

    return rows[0]["episode_number"] + 1


def publish_episode(
    title: str,
    slug: str,
    description: str,
    audio_url: str,
    duration_ms: int,
    file_size: int,
    episode_number: int | None = None,
    season_number: int | None = None,
    image_url: str | None = None,
) -> dict:
    """Insert an episode record into the episodes table."""
    data = {
        "title": title,
        "slug": slug,
        "description": description,
        "audio_url": audio_url,
        "duration": duration_ms // 1000,  # table stores seconds
        "file_size": file_size,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "episode_type": "full",
        "explicit": False,
    }
    if episode_number is not None:
        data["episode_number"] = episode_number
    if season_number is not None:
        data["season_number"] = season_number
    if image_url:
        data["image_url"] = image_url

    result = _supabase_rest("post", "episodes", data)
    episode = result[0] if isinstance(result, list) else result
    print(f"Episode published: {episode.get('id')}")
    return episode


def publish_chapters(episode_id: str, chapter_markers: list[dict], paper_url: str | None = None) -> list:
    """Insert chapter records into the chapters table."""
    rows = []
    for ch in chapter_markers:
        row = {
            "episode_id": episode_id,
            "title": ch["title"],
            "start_time_ms": ch["start_time_ms"],
            "end_time_ms": ch["end_time_ms"],
            "sort_order": ch["sort_order"],
        }
        if paper_url:
            row["url"] = paper_url
        rows.append(row)

    result = _supabase_rest("post", "chapters", rows)
    print(f"Published {len(rows)} chapters")
    return result


# ── SEO metadata generation ───────────────────────────────────────────────────


def generate_seo_description(parsed: dict, paper_url: str | None = None) -> str:
    """Generate an SEO-optimized episode description from the parsed script."""
    chapter_titles = [ch["title"] for ch in parsed["chapters"]]
    metadata = parsed.get("metadata", {})
    paper_title = metadata.get("Paper", "")
    authors = metadata.get("Authors", "")

    parts = []

    # Opening hook — first 2 sentences max
    if paper_title:
        parts.append(f"In this episode, we break down \"{paper_title}\"")
        if authors:
            parts[-1] += f" by {authors}."
        else:
            parts[-1] += "."

    # Chapter list
    if chapter_titles:
        parts.append("\nWhat we cover:")
        for i, title in enumerate(chapter_titles, 1):
            parts.append(f"  ({i}) {title}")

    # Paper link
    if paper_url:
        parts.append(f"\nRead the original paper: {paper_url}")

    parts.append("\nHosts: Alex & Thuy | Artificial Peer Review")
    parts.append("Website: artificialpeerreview.com")

    return "\n".join(parts)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug."""
    text = text.lower()
    text = re.sub(r"[—–]", "-", text)
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:80]


# ── CLI ───────────────────────────────────────────────────────────────────────


def cmd_generate(args):
    """Generate audio from script."""
    parsed = parse_script(args.script)
    print(f"Parsed: {parsed['title']}")
    print(f"Chapters: {len(parsed['chapters'])}")
    for ch in parsed["chapters"]:
        print(f"  - {ch['title']} ({len(ch['lines'])} dialogue lines)")

    output_dir = args.output_dir or str(SCRIPT_DIR.parent / "output")
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    audio_path, chapter_markers = generate_audio(parsed, output_dir)

    # Save chapter markers for later use
    markers_path = audio_path.replace(".mp3", "-chapters.json")
    with open(markers_path, "w") as f:
        json.dump(
            {"title": parsed["title"], "metadata": parsed["metadata"],
             "chapters": chapter_markers},
            f, indent=2,
        )
    print(f"Chapter markers saved: {markers_path}")


def cmd_publish(args):
    """Upload audio and publish episode to Supabase."""
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"Error: Audio file not found: {args.audio}", file=sys.stderr)
        sys.exit(1)

    # Load chapter markers
    markers_path = args.chapters or str(audio_path).replace(".mp3", "-chapters.json")
    if not Path(markers_path).exists():
        print(f"Error: Chapter markers not found: {markers_path}", file=sys.stderr)
        sys.exit(1)

    with open(markers_path) as f:
        markers_data = json.load(f)

    # Upload audio to Supabase storage
    print("Uploading audio to Supabase...")
    audio_url = upload_to_supabase(args.audio, bucket="podcast", folder="audio")

    # Determine metadata
    title = args.title or markers_data.get("title", audio_path.stem)
    slug = _slugify(title)
    file_size = audio_path.stat().st_size
    chapter_markers = markers_data["chapters"]
    duration_ms = chapter_markers[-1]["end_time_ms"] if chapter_markers else 0

    # Generate SEO description
    description = args.description
    if not description:
        description = generate_seo_description(
            {"title": title, "metadata": markers_data.get("metadata", {}), "chapters": chapter_markers},
            paper_url=args.paper_url,
        )

    print(f"\nTitle: {title}")
    print(f"Slug: {slug}")
    print(f"Duration: {duration_ms / 1000:.0f}s ({duration_ms / 60000:.1f} min)")
    print(f"File size: {file_size / 1024 / 1024:.1f} MB")
    print(f"Description:\n{description}\n")

    # Auto-detect episode number if not provided
    episode_number = args.episode_number
    if episode_number is None:
        episode_number = _next_episode_number()
        print(f"Auto-detected episode number: {episode_number}")

    # Publish episode
    episode = publish_episode(
        title=title,
        slug=slug,
        description=description,
        audio_url=audio_url,
        duration_ms=duration_ms,
        file_size=file_size,
        episode_number=episode_number,
        season_number=args.season_number,
        image_url=args.image_url,
    )

    episode_id = episode["id"]

    # Publish chapters
    publish_chapters(episode_id, chapter_markers, paper_url=args.paper_url)

    print(f"\nEpisode published successfully!")
    print(f"  ID: {episode_id}")
    print(f"  Slug: {slug}")
    print(f"  Audio: {audio_url}")
    print(json.dumps(episode, indent=2, default=str))


def cmd_parse(args):
    """Parse and preview a script without generating audio."""
    parsed = parse_script(args.script)
    print(f"Title: {parsed['title']}")
    print(f"Metadata: {json.dumps(parsed['metadata'], indent=2)}")
    print(f"Chapters: {len(parsed['chapters'])}")
    for ch in parsed["chapters"]:
        print(f"\n  ## {ch['title']}")
        print(f"  Lines: {len(ch['lines'])}")
        for line in ch["lines"][:3]:
            preview = line["text"][:80] + "..." if len(line["text"]) > 80 else line["text"]
            print(f"    {line['speaker']}: {preview}")
        if len(ch["lines"]) > 3:
            print(f"    ... and {len(ch['lines']) - 3} more lines")

    if args.paper_url:
        desc = generate_seo_description(parsed, paper_url=args.paper_url)
        print(f"\n--- SEO Description ---\n{desc}")


def main():
    parser = argparse.ArgumentParser(description="Publish podcast episodes")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Parse command — preview script structure
    p_parse = subparsers.add_parser("parse", help="Parse and preview a podcast script")
    p_parse.add_argument("--script", required=True, help="Path to podcast script markdown file")
    p_parse.add_argument("--paper-url", help="URL to original paper (for SEO description)")

    # Generate command — script → audio
    p_gen = subparsers.add_parser("generate", help="Generate audio from a podcast script")
    p_gen.add_argument("--script", required=True, help="Path to podcast script markdown file")
    p_gen.add_argument("--output-dir", help="Output directory (default: publish-podcast/output)")

    # Publish command — upload audio + publish metadata
    p_pub = subparsers.add_parser("publish", help="Upload audio and publish episode to Supabase")
    p_pub.add_argument("--audio", required=True, help="Path to generated MP3 file")
    p_pub.add_argument("--chapters", help="Path to chapter markers JSON (auto-detected from audio path)")
    p_pub.add_argument("--title", help="Episode title (default: from script metadata)")
    p_pub.add_argument("--description", help="Episode description (default: auto-generated SEO)")
    p_pub.add_argument("--paper-url", help="URL to original research paper")
    p_pub.add_argument("--episode-number", type=int, help="Episode number")
    p_pub.add_argument("--season-number", type=int, help="Season number")
    p_pub.add_argument("--image-url", help="Episode cover image URL")

    args = parser.parse_args()

    if args.command == "parse":
        cmd_parse(args)
    elif args.command == "generate":
        cmd_generate(args)
    elif args.command == "publish":
        cmd_publish(args)


if __name__ == "__main__":
    main()
