# Growth Analytics

Analyze social media post performance and podcast subscriber growth. Pulls LinkedIn post metrics from the Late API and subscriber counts from Supabase.

## Trigger

TRIGGER when: the user asks to analyze post performance, check LinkedIn analytics, review social media metrics, see how posts are doing, check subscriber count, or get a growth report.

## Instructions

### Step 1: Determine What to Analyze

Ask the user what they want to review:

- **Post performance** — How individual posts or recent posts performed (impressions, likes, comments, shares, engagement rate)
- **Daily metrics** — Aggregated daily performance over a date range
- **Best posting times** — What days/hours get the most engagement
- **Content decay** — How quickly posts lose traction after publishing
- **Subscriber growth** — Podcast subscriber count and trend from Supabase
- **Full report** — All of the above combined

Default to a **full report for the last 30 days** if the user doesn't specify.

### Step 2: Pull LinkedIn Post Analytics

Use the analytics script to fetch data from the Late API.

#### Recent post performance

```bash
python skills/growth-analytics/scripts/growth_analytics.py posts \
  --days 30 \
  --sort engagement \
  --limit 20
```

Returns each post with: content preview, published date, impressions, reach, likes, comments, shares, clicks, engagement rate, and media type.

#### Single post deep dive

```bash
python skills/growth-analytics/scripts/growth_analytics.py posts \
  --post-id "late_post_id_or_external_id"
```

#### Daily aggregated metrics

```bash
python skills/growth-analytics/scripts/growth_analytics.py daily \
  --from-date 2026-02-15 \
  --to-date 2026-03-15
```

Returns daily totals: impressions, reach, likes, comments, shares, saves, clicks, views.

#### Best posting times

```bash
python skills/growth-analytics/scripts/growth_analytics.py best-time
```

Returns slots grouped by day of week and hour (UTC) with average engagement per slot.

#### Content decay

```bash
python skills/growth-analytics/scripts/growth_analytics.py content-decay
```

Shows how post performance drops off over time after publishing.

#### Posting frequency analysis

```bash
python skills/growth-analytics/scripts/growth_analytics.py posting-frequency
```

Shows correlation between posting frequency and engagement.

### Step 3: Pull Subscriber Data from Supabase

```bash
python skills/growth-analytics/scripts/growth_analytics.py subscribers
```

Queries the `subscribers` table in Supabase for:
- Current total subscriber count
- New subscribers in the last 7 / 30 / 90 days
- Subscriber growth trend (weekly buckets)
- Most recent subscribers

Also queries the `episodes` table to correlate episode releases with subscriber spikes.

### Step 4: Present the Analysis

After collecting data, present a clear analysis structured into three sections: **Key Insights**, **What's Not Working**, and **Recommendations**.

#### Goal hierarchy

The primary growth goals, in order of priority (most valuable first):

1. **Comments** — Most valuable. Comments signal genuine engagement, trigger algorithmic amplification, and build community. Optimize for conversation.
2. **Likes** — Second priority. Likes are low-effort social proof that boost reach. High like counts attract new followers.
3. **Reach** — Third priority. Reach is the top-of-funnel metric. More eyeballs create more opportunities for likes and comments. Reach without engagement is vanity.

When analyzing posts, **rank and evaluate against this hierarchy**. A post with 50 impressions and 3 comments is more successful than a post with 500 impressions and 0 comments.

#### Section 1: Key Insights

Identify 3-5 patterns from the data. Each insight should be:
- **Data-backed** — cite specific numbers, ratios, or comparisons
- **Scored against the goal hierarchy** — evaluate through the lens of comments > likes > reach
- **Comparative** — compare content types, posting times, formats, topics against each other

Examples of good insights:
- "Carousel posts generate 4x more comments per impression than text posts (2.8% vs 0.7%)"
- "Posts with a question in the caption get 3x more comments than those without"
- "Your best reach came from text-only posts, but carousels convert reach to engagement at a much higher rate"
- "Weekday morning posts (Mon-Thu before 10am UTC) get 60% more reach than afternoon posts"

#### Section 2: What's Not Working

Identify 2-3 specific things dragging down performance. Be direct and specific:
- Which content types or formats underperform?
- Which topics fell flat?
- Are there posting patterns that correlate with poor performance?
- Are there structural issues (e.g., links in captions suppressing reach)?

Always explain **why** something isn't working, not just that it isn't.

#### Section 3: Recommendations

Provide 3-5 specific, actionable recommendations. Split into two categories:

**Optimize what's working (2-3 recommendations):**
- Directly address a finding from Key Insights or What's Not Working
- Be concrete — not "post better content" but "lead every post with a question to drive comments"
- Prioritize the goal hierarchy — recommendations that drive comments rank above those that drive reach
- Include a suggested next action — what specifically to do for the next 1-2 posts

**Experiment with something new (1-2 recommendations):**
- Use `WebSearch` to research current LinkedIn best practices, trending content formats, or engagement tactics that the user hasn't tried yet
- Look for strategies that are working for similar accounts (AI/tech podcasts, research-focused creators, B2B thought leadership)
- Suggest one specific experiment the user hasn't done before — a new format, hook style, content type, engagement tactic, or posting strategy
- Frame it as a low-risk experiment: "Try this once and compare against your baseline"
- Examples: polls, "hot take" threads, storytelling posts, tagging relevant people, engaging in comments on others' posts before publishing, using a specific hook formula, posting a short video clip from the podcast, creating a "paper of the week" series format

The goal is to avoid tunnel vision — don't just optimize the same playbook forever. Actively seek out and suggest new approaches from what's working across LinkedIn right now.

#### For subscriber growth reports:
Include subscriber data as a separate section after the LinkedIn analysis:
- **Current count** and net change over period
- **Growth rate** — Weekly/monthly percentage change
- **Episode correlation** — Which episode releases drove the most new subscribers

#### For full reports:
Lead with a one-line headline summarizing the most important finding, then present all three sections plus subscriber data.

## Environment Variables

| Variable | Description |
|---|---|
| `LATE_API_KEY` | Late API key (same as linkedin-posting) |
| `LATE_LINKEDIN_ACCOUNT_ID` | Late LinkedIn account ID (same as linkedin-posting) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key |

The script loads these from its own `.env` file or inherits from the environment.

## Database Tables

**subscribers** — One row per subscriber event:
- `id`, `email`, `source` (where they signed up from)
- `subscribed_at` (timestamp)
- `unsubscribed_at` (nullable — null means still active)

**episodes** — Used for correlation (same table as publish-podcast):
- `episode_number`, `title`, `published_at`, `duration`

## Important Rules

- ALWAYS evaluate performance against the goal hierarchy: comments > likes > reach
- ALWAYS structure the analysis as: Key Insights → What's Not Working → Recommendations
- ALWAYS present data with context — raw numbers without comparison are meaningless
- ALWAYS include percentage changes, ratios, and comparisons between content types
- ALWAYS suggest actionable next steps based on the data
- NEVER make up metrics — if the API returns an error, tell the user
- NEVER treat engagement rate as a single number — break it down into comments, likes, and reach separately
- If the analytics add-on is not enabled (402 error), inform the user they need to enable it on getlate.dev
- Late API analytics data is cached and refreshed at most once per hour — mention this if the user asks about real-time data
- When comparing periods, use the same duration (e.g., this month vs last month, not this month vs last week)
- A post with high reach but zero comments is a failure by the goal hierarchy — flag it
