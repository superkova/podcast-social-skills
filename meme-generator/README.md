# Meme Generator

Create AI-themed memes from a library of 16 classic templates. Pick a template, add text, render as PNG, and optionally upload to Supabase.

## Setup

```bash
pip install Pillow requests
```

For Supabase uploads, copy `.env` and fill in credentials:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sb_secret_your_key_here
```

## Usage

```bash
# List all available templates
python scripts/create_meme.py list

# Create a meme
python scripts/create_meme.py create \
  --meme drake \
  --texts "Reading the docs" "Asking ChatGPT to explain the docs"

# Upload to Supabase
python scripts/create_meme.py upload --file output/drake-20260306-143000.png
```

## Available Templates

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

## Text Zones

Each template has specific text zones. Provide `--texts` in order:

- **2-zone** (top/bottom): `drake`, `surprised-pikachu`, `woman-yelling-at-cat`, `nobody`, `one-does-not-simply`, `success-kid`, `disaster-girl`, `roll-safe`
- **3-zone**: `distracted-boyfriend` (new_thing, you, old_thing), `two-buttons` (button_1, button_2, caption), `same-picture` (left_pic, right_pic)
- **4-zone**: `expanding-brain`, `galaxy-brain`, `grus-plan` (4 levels/steps)
- **1-zone**: `this-is-fine` (caption), `change-my-mind` (sign)
