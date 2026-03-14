# LinkedIn Posting

Post content to LinkedIn via the Late API (getlate.dev), with Supabase storage for media hosting.

## Trigger

TRIGGER when: the user asks to post something to LinkedIn, publish a LinkedIn post, schedule a LinkedIn post, or upload content to LinkedIn.

## Instructions

You are a LinkedIn posting assistant. You help the user publish content to LinkedIn using the Late API, handling text posts, image posts, multi-image posts, video posts, and document/carousel posts.

### Step 1: Gather information

Before posting, collect from the user:

1. **Content type** — What are we posting?
   - **Text-only** — highest organic reach, up to 3,000 characters
   - **Single image** — one image attached (JPEG, PNG; max 8 MB; recommended 1080x1080 or 1200x627)
   - **Multi-image** — up to 20 images (cannot mix with video/document)
   - **Video** — one video (MP4, MOV, AVI; max 5 GB; max 10 min personal / 30 min company)
   - **Document/Carousel** — one PDF, PPT, PPTX, DOC, DOCX (max 100 MB, 300 pages; displays as swipeable carousel)

2. **Caption/text** — The post text (max 3,000 characters). First ~210 characters appear before the "see more" fold — lead with the hook.

3. **Media files** (if applicable) — Local file paths for images, video, or document to upload.

4. **First comment** (optional) — External links should go here, NOT in the caption. LinkedIn suppresses posts with links by 40-50%.

5. **Scheduling** (optional) — Post now or schedule for a specific date/time.

6. **Document title** (if document post) — Required by LinkedIn for document/carousel posts. Falls back to filename if omitted.

### Step 2: Check credentials

The posting script needs two sets of credentials:

- **Late API key** — env var `LATE_API_KEY`
- **Late LinkedIn account ID** — env var `LATE_LINKEDIN_ACCOUNT_ID`
- **Supabase URL** — env var `SUPABASE_URL`
- **Supabase service role key** — env var `SUPABASE_SERVICE_ROLE_KEY`

If env vars are not set, check the secret management system on the server called **broker** for the values.

### Step 3: Upload media to Supabase (if applicable)

For any post with media (images, video, document), upload the file to Supabase storage first to get a public URL. The Late API requires publicly accessible media URLs.

Use the posting script's `upload` command:

```bash
python scripts/post_to_linkedin.py upload \
  --file path/to/image.png
```

This uploads to the `podcast` bucket under the `content/` folder (with date-based subfolders) and returns a public URL. For multi-image posts, upload each file separately.

**Supabase storage notes:**
- Storage bucket: `podcast`, folder: `content/` (files go to `content/YYYY-MM-DD/HHMMSS-filename`)
- Late auto-proxies Supabase storage URLs, so they work without additional configuration
- Supported: any file type LinkedIn accepts (JPEG, PNG, GIF, MP4, MOV, AVI, PDF, PPT, etc.)

### Step 4: Post to LinkedIn

Use the posting script to publish:

```bash
# Text-only post
python scripts/post_to_linkedin.py post \
  --content "Your post text here" \
  --publish-now

# Image post (after uploading to Supabase)
python scripts/post_to_linkedin.py post \
  --content "Caption text" \
  --media image:https://your-supabase-url.supabase.co/storage/v1/object/public/bucket/file.png \
  --publish-now

# Multi-image post
python scripts/post_to_linkedin.py post \
  --content "Caption text" \
  --media image:https://url1.png \
  --media image:https://url2.png \
  --media image:https://url3.png \
  --publish-now

# Video post
python scripts/post_to_linkedin.py post \
  --content "Caption text" \
  --media video:https://your-supabase-url.supabase.co/storage/v1/object/public/bucket/demo.mp4 \
  --publish-now

# Document/carousel post
python scripts/post_to_linkedin.py post \
  --content "Caption text" \
  --media document:https://your-supabase-url.supabase.co/storage/v1/object/public/bucket/report.pdf \
  --document-title "Report Title" \
  --publish-now

# With first comment (for links)
python scripts/post_to_linkedin.py post \
  --content "We just published our guide.\n\nLink in comments." \
  --first-comment "Read the full guide: https://example.com/guide" \
  --publish-now

# Schedule for later
python scripts/post_to_linkedin.py post \
  --content "Scheduled post text" \
  --schedule "2026-03-10T09:00:00Z"
```

### Step 5: Confirm to user

After posting, confirm:
- Post ID returned by Late API
- Whether it was published immediately or scheduled
- Remind them: first ~210 characters are visible before "see more"

## Content Types Reference

| Type | Media | Limits | Notes |
|---|---|---|---|
| Text-only | None | 3,000 chars | Highest organic reach |
| Single image | 1 image | JPEG/PNG, 8 MB, recommended 1080x1080 or 1200x627 | Good engagement |
| Multi-image | 2-20 images | Same per image | Cannot mix with video/doc |
| Video | 1 video | MP4/MOV/AVI, 5 GB, 10 min personal / 30 min company | GIFs count as video |
| Document | 1 document | PDF/PPT/PPTX/DOC/DOCX, 100 MB, 300 pages | Displays as swipeable carousel |

## LinkedIn Best Practices

- **No links in caption** — LinkedIn suppresses posts with URLs by 40-50%. Put links in `--first-comment`.
- **Hook in first 210 chars** — Everything after is hidden behind "see more".
- **No duplicate content** — LinkedIn rejects identical text with a 422 error. Every post must be meaningfully different.
- **Cannot mix media types** — A post can have images OR a video OR a document, not combinations.
- **GIFs are video** — GIF uploads are converted to video and count against the 1-video limit.
- **Document first page is the cover** — Design it to grab attention in the feed.

## Media URL Requirements

Media URLs passed to Late must be:
- Publicly accessible (no auth required)
- Returning actual media bytes with correct Content-Type header
- Not behind redirects that resolve to HTML pages

**Do NOT use** Google Drive, Dropbox, OneDrive, or iCloud links — they return HTML pages, not raw files. Use Supabase storage.

## Script Location

The posting script is at `skills/linkedin-posting/scripts/post_to_linkedin.py` (relative to the project root).

## Important Rules

- ALWAYS check that env vars are set before attempting to post
- ALWAYS upload media to Supabase first — never pass local file paths to the Late API
- ALWAYS put external links in `--first-comment`, not in `--content`
- NEVER post duplicate content (LinkedIn returns 422)
- NEVER mix media types in a single post
- For document posts, ALWAYS provide `--document-title`
- If a post fails, check the error against the common errors table and advise the user
