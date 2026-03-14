#!/usr/bin/env python3
"""Download all 20 meme templates from imgflip."""

import os
import requests
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

MEMES = {
    "drake": "https://i.imgflip.com/30b1gx.jpg",
    "distracted-boyfriend": "https://i.imgflip.com/1ur9b0.jpg",
    "this-is-fine": "https://i.imgflip.com/wxica.jpg",
    "expanding-brain": "https://i.imgflip.com/1jwhww.jpg",
    "surprised-pikachu": "https://i.imgflip.com/2kbn1e.jpg",
    "woman-yelling-at-cat": "https://i.imgflip.com/345v97.jpg",
    "grus-plan": "https://i.imgflip.com/26jxvz.jpg",
    "two-buttons": "https://i.imgflip.com/1g8my4.jpg",
    "nobody": "https://imgflip.com/s/meme/Nobody.jpg",
    "stonks": "https://imgflip.com/s/meme/stonks.jpg",
    "we-have-at-home": "https://imgflip.com/s/meme/Can-we-have.jpg",
    "one-does-not-simply": "https://i.imgflip.com/1bij.jpg",
    "success-kid": "https://i.imgflip.com/1bhk.jpg",
    "galaxy-brain": "https://imgflip.com/s/meme/Galaxy-Brain-3-brains.jpg",
    "same-picture": "https://i.imgflip.com/2za3u1.jpg",
    "free-real-estate": "https://imgflip.com/s/meme/Its-Free-Real-Estate.jpg",
    "disaster-girl": "https://i.imgflip.com/23ls.jpg",
    "change-my-mind": "https://i.imgflip.com/24y43o.jpg",
    "leonardo-pointing": "https://imgflip.com/s/meme/Leonardo-DiCaprio-Pointing.jpg",
    "roll-safe": "https://i.imgflip.com/1h7in3.jpg",
}

# Fallback URLs using imgflip template IDs
FALLBACK = {
    "nobody": "https://i.imgflip.com/2fm6x.jpg",
    "stonks": "https://i.imgflip.com/2yhw2a.jpg",
    "we-have-at-home": "https://i.imgflip.com/2x82g7.jpg",
    "galaxy-brain": "https://i.imgflip.com/2gnuqf.jpg",
    "free-real-estate": "https://i.imgflip.com/218s4a.jpg",
    "leonardo-pointing": "https://i.imgflip.com/3pnmg2.jpg",
}


def download(name, url):
    dest = TEMPLATES_DIR / f"{name}.jpg"
    if dest.exists():
        print(f"  [skip] {name} (already exists)")
        return True

    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
    if resp.status_code == 200 and len(resp.content) > 1000:
        dest.write_bytes(resp.content)
        print(f"  [ok]   {name} ({len(resp.content) // 1024}KB)")
        return True
    return False


def main():
    print(f"Downloading {len(MEMES)} meme templates to {TEMPLATES_DIR}\n")
    ok, fail = 0, 0
    for name, url in MEMES.items():
        if not download(name, url):
            # Try fallback
            fb = FALLBACK.get(name)
            if fb and download(name, fb):
                ok += 1
            else:
                print(f"  [FAIL] {name}")
                fail += 1
        else:
            ok += 1

    print(f"\nDone: {ok} downloaded, {fail} failed")


if __name__ == "__main__":
    main()
