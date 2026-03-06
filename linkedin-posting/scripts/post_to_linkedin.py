#!/usr/bin/env python3
"""Post content to LinkedIn via Late API, with Supabase storage for media hosting."""

import argparse
import json
import mimetypes
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote as url_quote

import requests

# ── Config ────────────────────────────────────────────────────────────────────

LATE_API_BASE = "https://getlate.dev/api/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR.parent / ".env"


def _load_env():
    """Load .env file from the linkedin-posting directory if it exists."""
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


# ── Supabase upload ──────────────────────────────────────────────────────────


def upload_to_supabase(file_path: str, bucket: str) -> str:
    """Upload a local file to Supabase storage and return the public URL."""
    supabase_url = _get_env("SUPABASE_URL")
    supabase_key = _get_env("SUPABASE_SERVICE_ROLE_KEY")

    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Generate unique storage path: content/YYYY-MM-DD/filename
    date_prefix = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    timestamp = datetime.now(timezone.utc).strftime("%H%M%S")
    storage_name = f"{timestamp}-{path.name}"
    storage_path = f"content/{date_prefix}/{storage_name}"

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


# ── Late API posting ─────────────────────────────────────────────────────────


def post_to_linkedin(
    content: str,
    media_items: list[dict] | None = None,
    first_comment: str | None = None,
    document_title: str | None = None,
    schedule: str | None = None,
    publish_now: bool = False,
) -> dict:
    """Create a LinkedIn post via Late API."""
    api_key = _get_env("LATE_API_KEY")
    account_id = _get_env("LATE_LINKEDIN_ACCOUNT_ID")

    if len(content) > 3000:
        print(f"Warning: Content is {len(content)} chars (max 3,000). Truncating.", file=sys.stderr)
        content = content[:3000]

    payload: dict = {
        "content": content,
        "platforms": [
            {
                "platform": "linkedin",
                "accountId": account_id,
            }
        ],
    }

    # Platform-specific data
    platform_data: dict = {}
    if first_comment:
        platform_data["firstComment"] = first_comment
    if document_title:
        platform_data["documentTitle"] = document_title
    if platform_data:
        payload["platforms"][0]["platformSpecificData"] = platform_data

    # Media
    if media_items:
        payload["mediaItems"] = media_items

    # Scheduling
    if publish_now:
        payload["publishNow"] = True
    elif schedule:
        payload["scheduledAt"] = schedule
    else:
        payload["publishNow"] = True  # default to now

    resp = requests.post(
        f"{LATE_API_BASE}/posts",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json=payload,
    )

    if resp.status_code not in (200, 201):
        print(f"Error from Late API: {resp.status_code}", file=sys.stderr)
        try:
            error_body = resp.json()
            print(json.dumps(error_body, indent=2), file=sys.stderr)
        except Exception:
            print(resp.text, file=sys.stderr)
        sys.exit(1)

    result = resp.json()
    post = result.get("post", result)
    post_id = post.get("_id", "unknown")

    if publish_now:
        print(f"Published to LinkedIn! Post ID: {post_id}")
    elif schedule:
        print(f"Scheduled for {schedule}. Post ID: {post_id}")
    else:
        print(f"Post created. Post ID: {post_id}")

    return result


# ── CLI ───────────────────────────────────────────────────────────────────────


def cmd_upload(args):
    url = upload_to_supabase(args.file, args.bucket)
    print(f"\nPublic URL:\n{url}")


def cmd_post(args):
    media_items = None
    if args.media:
        media_items = []
        for item in args.media:
            media_type, url = item.split(":", 1)
            if media_type not in ("image", "video", "document"):
                print(f"Error: Invalid media type '{media_type}'. Use image, video, or document.", file=sys.stderr)
                sys.exit(1)
            media_items.append({"type": media_type, "url": url})

        # Validate no mixed types
        types = {m["type"] for m in media_items}
        if len(types) > 1:
            print("Error: Cannot mix media types. Use only images, or one video, or one document.", file=sys.stderr)
            sys.exit(1)
        if "video" in types and len(media_items) > 1:
            print("Error: Only one video per post.", file=sys.stderr)
            sys.exit(1)
        if "document" in types and len(media_items) > 1:
            print("Error: Only one document per post.", file=sys.stderr)
            sys.exit(1)

    result = post_to_linkedin(
        content=args.content,
        media_items=media_items,
        first_comment=args.first_comment,
        document_title=args.document_title,
        schedule=args.schedule,
        publish_now=args.publish_now,
    )

    print(json.dumps(result, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(description="Post to LinkedIn via Late API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Upload command
    up = subparsers.add_parser("upload", help="Upload a file to Supabase storage")
    up.add_argument("--file", required=True, help="Local file path to upload")
    up.add_argument("--bucket", default="podcast", help="Supabase storage bucket (default: podcast)")

    # Post command
    p = subparsers.add_parser("post", help="Create a LinkedIn post")
    p.add_argument("--content", required=True, help="Post text (max 3,000 chars)")
    p.add_argument("--media", action="append", help="Media item as type:url (e.g. image:https://...)")
    p.add_argument("--first-comment", help="First comment text (put links here)")
    p.add_argument("--document-title", help="Title for document/carousel posts")
    p.add_argument("--schedule", help="Schedule time as ISO 8601 (e.g. 2026-03-10T09:00:00Z)")
    p.add_argument("--publish-now", action="store_true", help="Publish immediately")

    args = parser.parse_args()

    if args.command == "upload":
        cmd_upload(args)
    elif args.command == "post":
        cmd_post(args)


if __name__ == "__main__":
    main()
