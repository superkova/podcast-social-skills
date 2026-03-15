#!/usr/bin/env python3
"""Fetch growth analytics from Late API (LinkedIn) and Supabase (subscribers)."""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

# ── Config ────────────────────────────────────────────────────────────────────

LATE_API_BASE = "https://getlate.dev/api/v1"
SCRIPT_DIR = Path(__file__).resolve().parent
ENV_FILE = SCRIPT_DIR.parent / ".env"


def _load_env():
    """Load .env file from the growth-analytics directory if it exists."""
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


def _late_headers() -> dict:
    return {
        "Authorization": f"Bearer {_get_env('LATE_API_KEY')}",
        "Content-Type": "application/json",
    }


def _supabase_headers() -> dict:
    key = _get_env("SUPABASE_SERVICE_ROLE_KEY")
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


def _supabase_url() -> str:
    return _get_env("SUPABASE_URL")


# ── Late API: Post Analytics ─────────────────────────────────────────────────


def fetch_post_analytics(
    post_id: str | None = None,
    days: int = 30,
    sort_by: str = "date",
    limit: int = 50,
    page: int = 1,
) -> dict:
    """Fetch post analytics from Late API."""
    params: dict = {
        "platform": "linkedin",
        "source": "late",
        "sortBy": sort_by,
        "order": "desc",
        "limit": min(limit, 100),
        "page": page,
    }
    # profileId is optional — only include if LATE_LINKEDIN_PROFILE_ID is set
    profile_id = os.environ.get("LATE_LINKEDIN_PROFILE_ID")
    if profile_id:
        params["profileId"] = profile_id

    if post_id:
        params["postId"] = post_id
    else:
        to_date = datetime.now(timezone.utc)
        from_date = to_date - timedelta(days=days)
        params["fromDate"] = from_date.strftime("%Y-%m-%d")
        params["toDate"] = to_date.strftime("%Y-%m-%d")

    resp = requests.get(
        f"{LATE_API_BASE}/analytics",
        headers=_late_headers(),
        params=params,
    )

    if resp.status_code == 402:
        print("Error: Analytics add-on required. Enable it at https://getlate.dev", file=sys.stderr)
        sys.exit(1)
    if resp.status_code != 200:
        print(f"Error from Late API: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()


def fetch_daily_metrics(from_date: str, to_date: str) -> dict:
    """Fetch daily aggregated metrics."""
    params = {
        "platform": "linkedin",
        "profileId": _get_env("LATE_LINKEDIN_ACCOUNT_ID"),
        "fromDate": from_date,
        "toDate": to_date,
    }

    resp = requests.get(
        f"{LATE_API_BASE}/analytics/daily-metrics",
        headers=_late_headers(),
        params=params,
    )

    if resp.status_code != 200:
        print(f"Error fetching daily metrics: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()


def fetch_best_time() -> dict:
    """Fetch best posting times."""
    params = {
        "platform": "linkedin",
        "profileId": _get_env("LATE_LINKEDIN_ACCOUNT_ID"),
    }

    resp = requests.get(
        f"{LATE_API_BASE}/analytics/best-time",
        headers=_late_headers(),
        params=params,
    )

    if resp.status_code != 200:
        print(f"Error fetching best time: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()


def fetch_content_decay() -> dict:
    """Fetch content decay data."""
    params = {
        "platform": "linkedin",
        "profileId": _get_env("LATE_LINKEDIN_ACCOUNT_ID"),
    }

    resp = requests.get(
        f"{LATE_API_BASE}/analytics/content-decay",
        headers=_late_headers(),
        params=params,
    )

    if resp.status_code != 200:
        print(f"Error fetching content decay: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()


def fetch_posting_frequency() -> dict:
    """Fetch posting frequency vs engagement data."""
    params = {
        "platform": "linkedin",
        "profileId": _get_env("LATE_LINKEDIN_ACCOUNT_ID"),
    }

    resp = requests.get(
        f"{LATE_API_BASE}/analytics/posting-frequency",
        headers=_late_headers(),
        params=params,
    )

    if resp.status_code != 200:
        print(f"Error fetching posting frequency: {resp.status_code} {resp.text}", file=sys.stderr)
        sys.exit(1)

    return resp.json()


# ── Supabase: Subscribers ────────────────────────────────────────────────────


def fetch_subscribers() -> dict:
    """Fetch subscriber stats from Supabase."""
    base = _supabase_url()
    headers = _supabase_headers()
    now = datetime.now(timezone.utc)

    # Total active subscribers
    resp = requests.get(
        f"{base}/rest/v1/subscribers?select=id&unsubscribed_at=is.null",
        headers={**headers, "Prefer": "count=exact"},
    )
    total = 0
    if resp.status_code == 200:
        total = int(resp.headers.get("content-range", "*/0").split("/")[-1])

    # New subscribers in last 7 / 30 / 90 days
    counts = {}
    for label, days in [("7d", 7), ("30d", 30), ("90d", 90)]:
        since = (now - timedelta(days=days)).isoformat()
        resp = requests.get(
            f"{base}/rest/v1/subscribers?select=id&subscribed_at=gte.{since}&unsubscribed_at=is.null",
            headers={**headers, "Prefer": "count=exact"},
        )
        if resp.status_code == 200:
            counts[label] = int(resp.headers.get("content-range", "*/0").split("/")[-1])
        else:
            counts[label] = None

    # Weekly trend (last 12 weeks)
    twelve_weeks_ago = (now - timedelta(weeks=12)).isoformat()
    resp = requests.get(
        f"{base}/rest/v1/subscribers?select=subscribed_at&subscribed_at=gte.{twelve_weeks_ago}&order=subscribed_at.asc",
        headers=headers,
    )
    weekly_trend = []
    if resp.status_code == 200:
        rows = resp.json()
        # Bucket into weeks
        buckets: dict[str, int] = {}
        for row in rows:
            dt = datetime.fromisoformat(row["subscribed_at"].replace("Z", "+00:00"))
            week_start = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
            buckets[week_start] = buckets.get(week_start, 0) + 1
        weekly_trend = [{"week": k, "new_subscribers": v} for k, v in sorted(buckets.items())]

    # Most recent subscribers (last 10)
    resp = requests.get(
        f"{base}/rest/v1/subscribers?select=email,source,subscribed_at&order=subscribed_at.desc&limit=10",
        headers=headers,
    )
    recent = resp.json() if resp.status_code == 200 else []

    # Episode correlation — episodes published in last 90 days
    ninety_days_ago = (now - timedelta(days=90)).isoformat()
    resp = requests.get(
        f"{base}/rest/v1/episodes?select=episode_number,title,published_at&published_at=gte.{ninety_days_ago}&order=published_at.desc",
        headers=headers,
    )
    episodes = resp.json() if resp.status_code == 200 else []

    return {
        "total_active": total,
        "new": counts,
        "weekly_trend": weekly_trend,
        "recent": recent,
        "recent_episodes": episodes,
    }


# ── CLI ───────────────────────────────────────────────────────────────────────


def cmd_posts(args):
    data = fetch_post_analytics(
        post_id=args.post_id,
        days=args.days,
        sort_by=args.sort,
        limit=args.limit,
    )
    print(json.dumps(data, indent=2, default=str))


def cmd_daily(args):
    now = datetime.now(timezone.utc)
    from_date = args.from_date or (now - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date = args.to_date or now.strftime("%Y-%m-%d")
    data = fetch_daily_metrics(from_date, to_date)
    print(json.dumps(data, indent=2, default=str))


def cmd_best_time(args):
    data = fetch_best_time()
    print(json.dumps(data, indent=2, default=str))


def cmd_content_decay(args):
    data = fetch_content_decay()
    print(json.dumps(data, indent=2, default=str))


def cmd_posting_frequency(args):
    data = fetch_posting_frequency()
    print(json.dumps(data, indent=2, default=str))


def cmd_subscribers(args):
    data = fetch_subscribers()
    print(json.dumps(data, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(description="Growth analytics for LinkedIn and podcast subscribers")
    sub = parser.add_subparsers(dest="command", required=True)

    # posts
    p_posts = sub.add_parser("posts", help="Fetch LinkedIn post analytics")
    p_posts.add_argument("--post-id", help="Specific post ID to analyze")
    p_posts.add_argument("--days", type=int, default=30, help="Number of days to look back (default: 30)")
    p_posts.add_argument("--sort", choices=["date", "engagement"], default="date", help="Sort order")
    p_posts.add_argument("--limit", type=int, default=50, help="Max posts to return (default: 50)")
    p_posts.set_defaults(func=cmd_posts)

    # daily
    p_daily = sub.add_parser("daily", help="Fetch daily aggregated metrics")
    p_daily.add_argument("--from-date", help="Start date (YYYY-MM-DD)")
    p_daily.add_argument("--to-date", help="End date (YYYY-MM-DD)")
    p_daily.set_defaults(func=cmd_daily)

    # best-time
    p_best = sub.add_parser("best-time", help="Fetch best posting times")
    p_best.set_defaults(func=cmd_best_time)

    # content-decay
    p_decay = sub.add_parser("content-decay", help="Fetch content decay data")
    p_decay.set_defaults(func=cmd_content_decay)

    # posting-frequency
    p_freq = sub.add_parser("posting-frequency", help="Fetch posting frequency vs engagement")
    p_freq.set_defaults(func=cmd_posting_frequency)

    # subscribers
    p_subs = sub.add_parser("subscribers", help="Fetch subscriber stats from Supabase")
    p_subs.set_defaults(func=cmd_subscribers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
