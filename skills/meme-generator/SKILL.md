# Meme Generator

Create AI-themed memes from a library of 16 classic templates. Given a topic or text, choose the right meme format, generate the text, render the image, and optionally upload to Supabase.

## Trigger

TRIGGER when: the user asks to create a meme, make a meme, generate a meme image, or wants meme content for LinkedIn/social media.

## Instructions

### Step 1: Understand the Topic

The user provides a topic, idea, or text they want to turn into a meme. Understand the core message, humor angle, and target audience (typically AI/tech LinkedIn).

### Step 2: Choose the Right Meme

Pick the best template based on the message type:

| ID | Name | Best For |
|---|---|---|
| `drake` | Drake | Any X vs Y comparison |
| `distracted-boyfriend` | Distracted Boyfriend | Abandoning old thing for new trend |
| `this-is-fine` | This Is Fine | Ignoring obvious AI problems/risks |
| `expanding-brain` | Expanding Brain | Levels of takes, from basic to unhinged |
| `surprised-pikachu` | Surprised Pikachu | Predictable consequences nobody prepared for |
| `woman-yelling-at-cat` | Woman Yelling at Cat | Two opposing camps arguing |
| `grus-plan` | Gru's Plan | Strategy that backfires in the last step |
| `two-buttons` | Two Buttons | Impossible choices / decision paralysis |
| `nobody` | Nobody / AI | Unsolicited, unhinged AI outputs |
| `one-does-not-simply` | One Does Not Simply | "You can't just automate X..." |
| `success-kid` | Success Kid | Small but real wins with AI |
| `galaxy-brain` | Galaxy Brain | Reasoning that sounds smart but is absurd |
| `same-picture` | They're The Same Picture | False equivalences in AI debates |
| `disaster-girl` | Disaster Girl | Watching AI chaos unfold, unbothered |
| `change-my-mind` | Change My Mind | Hot takes about AI/LLMs |
| `roll-safe` | Roll Safe | Flawed but confident logic |

Present your meme choice and the text to the user for approval before generating.

### Step 3: Generate the Meme

```bash
python skills/meme-generator/scripts/create_meme.py create \
  --meme drake \
  --texts "Using ChatGPT to write your emails" "Using ChatGPT to write prompts for ChatGPT to write your emails"
```

Each `--texts` argument maps to a text zone in the template (in order). See the text zones section below for how many texts each meme needs.

### Step 4: Upload to Supabase (Optional)

```bash
python skills/meme-generator/scripts/create_meme.py upload \
  --file skills/meme-generator/output/drake-20260306-143000.png
```

Uploads to Supabase storage (`podcast` bucket, `content/` folder) and returns the public URL.

### Step 5: Confirm to User

Show the user:
- The meme template used and why
- The generated text
- The output file path
- The Supabase URL (if uploaded)

## Text Zones Per Meme

Each meme has specific text zones. Provide texts in this order:

| Meme | Zones (in order) |
|---|---|
| `drake` | reject, prefer |
| `distracted-boyfriend` | new_thing, you, old_thing |
| `this-is-fine` | caption |
| `expanding-brain` | level_1, level_2, level_3, level_4 |
| `surprised-pikachu` | top, bottom |
| `woman-yelling-at-cat` | woman, cat |
| `grus-plan` | step_1, step_2, step_3, step_4 |
| `two-buttons` | button_1, button_2, caption |
| `nobody` | top, bottom |
| `one-does-not-simply` | top, bottom |
| `success-kid` | top, bottom |
| `galaxy-brain` | level_1, level_2, level_3, level_4 |
| `same-picture` | left_pic, right_pic, bottom |
| `disaster-girl` | top, bottom |
| `change-my-mind` | sign |
| `roll-safe` | top, bottom |

## Meme Text Best Practices

- **Keep it short** — meme text should be punchy, not paragraphs
- **Use ALL CAPS** — the script auto-uppercases, but write in the meme voice
- **Be specific** — "GPT-4" is funnier than "AI"; "Kubernetes" is funnier than "infrastructure"
- **Match the format** — Drake memes need a clear bad/good contrast; Gru's Plan needs a twist in step 3-4
- **Know your audience** — these are for AI/tech LinkedIn, so reference real tools, trends, and pain points

## Environment Variables

| Variable | Description |
|---|---|
| `SUPABASE_URL` | Supabase project URL (for upload) |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key (for upload) |

## Important Rules

- ALWAYS present the meme choice and text to the user before generating
- ALWAYS pick the meme format that best matches the message type — don't force a topic into the wrong format
- NEVER use more than ~10 words per text zone — brevity is key
- If the user's topic doesn't fit any template well, suggest the closest match and explain why
