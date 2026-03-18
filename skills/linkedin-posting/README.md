# LinkedIn Posting

Post content to LinkedIn via the [Zernio API](https://zernio.com), with Supabase storage for media hosting.

## What it does

Publish LinkedIn posts directly from the command line. Supports:

- **Text-only posts** — highest organic reach
- **Single image posts** — JPEG, PNG (max 8 MB)
- **Multi-image posts** — up to 20 images
- **Video posts** — MP4, MOV, AVI (max 5 GB)
- **Document/carousel posts** — PDF, PPT, PPTX, DOC, DOCX (swipeable carousel)

Media files are uploaded to Supabase storage first, then the public URL is passed to the Zernio API.

## Setup

```bash
pip install requests
```

### Environment variables

| Variable | Description |
|---|---|
| `ZERNIO_API_KEY` | Zernio API key ([zernio.com](https://zernio.com)) |
| `ZERNIO_LINKEDIN_ACCOUNT_ID` | Your LinkedIn account ID in Zernio |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key (for storage uploads) |

If env vars are not available locally, check the secret management system on the server called **broker**.

## Usage

### Upload media to Supabase

```bash
python scripts/post_to_linkedin.py upload \
  --file path/to/image.png
```

Files are uploaded to the `podcast` bucket under `content/YYYY-MM-DD/` with a timestamp prefix.

### Post to LinkedIn

```bash
# Text-only
python scripts/post_to_linkedin.py post \
  --content "Your post text here" \
  --publish-now

# With image
python scripts/post_to_linkedin.py post \
  --content "Caption text" \
  --media image:https://your-project.supabase.co/storage/v1/object/public/bucket/file.png \
  --publish-now

# With first comment (for links)
python scripts/post_to_linkedin.py post \
  --content "We just published our guide.\n\nLink in comments." \
  --first-comment "Read the full guide: https://example.com" \
  --publish-now

# Document/carousel
python scripts/post_to_linkedin.py post \
  --content "Check out our report" \
  --media document:https://your-project.supabase.co/storage/v1/object/public/bucket/report.pdf \
  --document-title "2024 Industry Report" \
  --publish-now

# Schedule for later
python scripts/post_to_linkedin.py post \
  --content "Scheduled post" \
  --schedule "2026-03-10T09:00:00Z"
```

### Arguments

**upload command:**

| Flag | Required | Description |
|---|---|---|
| `--file` | Yes | Local file path to upload |
| `--bucket` | No | Supabase storage bucket (default: `podcast`) |

**post command:**

| Flag | Required | Description |
|---|---|---|
| `--content` | Yes | Post text (max 3,000 characters) |
| `--media` | No | Media as `type:url` (repeatable for multi-image) |
| `--first-comment` | No | First comment text — put external links here |
| `--document-title` | No | Title for document/carousel posts |
| `--schedule` | No | ISO 8601 datetime to schedule (e.g. `2026-03-10T09:00:00Z`) |
| `--publish-now` | No | Publish immediately (default if no schedule) |

## Content types

| Type | Media flag | Limits |
|---|---|---|
| Text-only | None | 3,000 chars |
| Single image | `image:URL` | JPEG/PNG, 8 MB, recommended 1080x1080 |
| Multi-image | `image:URL` (repeat) | Up to 20 images |
| Video | `video:URL` | MP4/MOV/AVI, 5 GB, 10 min personal / 30 min company |
| Document | `document:URL` | PDF/PPT/PPTX/DOC/DOCX, 100 MB, 300 pages |

## LinkedIn tips

- **No links in caption** — LinkedIn suppresses posts with URLs by 40-50%. Use `--first-comment`.
- **First 210 chars matter** — Everything after is behind "see more".
- **No duplicate content** — LinkedIn rejects identical text (422 error).
- **Cannot mix media types** — Images OR video OR document, not combinations.
- **GIFs are video** — They get converted and count against the 1-video limit.

## Project structure

```
linkedin-posting/
├── README.md
├── SKILL.md              # Instructions for Claude (the AI agent)
└── scripts/
    └── post_to_linkedin.py  # Upload + posting CLI
```
