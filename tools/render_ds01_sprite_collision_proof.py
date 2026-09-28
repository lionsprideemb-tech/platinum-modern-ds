#!/usr/bin/env python3
"""Render an analysis-only contact sheet for DS01 sprite collision quarantine entries."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GROUPS = [
    ("Unrelated exact-byte collision", ["darkrai_mega", "heatran_mega", "slate", "zeraora_mega"]),
    ("Custom Mega vs G-Max", ["charizard_mega_z", "charizard-gmax"]),
    ("Custom Mega vs G-Max", ["coalossal_mega", "coalossal-gmax"]),
    ("Custom Mega vs G-Max", ["drednaw_mega", "drednaw-gmax"]),
    ("Custom Mega vs G-Max", ["hatterene_mega", "hatterene-gmax"]),
    ("Custom Mega vs G-Max", ["inteleon_mega", "inteleon-gmax"]),
    ("Custom Mega vs G-Max", ["machamp_mega", "machamp-gmax"]),
    ("Custom Mega vs G-Max", ["snorlax_mega", "snorlax-gmax"]),
    ("Custom Mega vs G-Max", ["toxtricity_mega", "toxtricity-amped-gmax", "toxtricity-low-key-gmax"]),
    ("Custom Mega vs G-Max", ["urshifu_mega", "urshifu-single-strike-gmax"]),
    ("Custom Mega vs G-Max", ["urshifu_rapid_strike_style_mega", "urshifu-rapid-strike-gmax"]),
    ("Palette/recolor review", ["lapras_mega", "lapras-gmax"]),
    ("Near-duplicate review", ["butterfree_mega", "butterfree-gmax"]),
    ("Near-duplicate review", ["kingler_mega", "kingler-gmax"]),
    ("Near-duplicate review", ["tinkaton_mega", "tinkaton"]),
]


def find_member(zf: zipfile.ZipFile, slug: str) -> str:
    suffix = f"/hg_engine_ready/data/graphics/sprites/{slug}/male/front.png"
    matches = [n for n in zf.namelist() if n.replace("\\", "/").endswith(suffix)]
    if not matches:
        raise KeyError(f"missing male/front for {slug}")
    return matches[0]


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--json", dest="json_out", type=Path, required=True)
    args = ap.parse_args()

    cards = []
    evidence = []
    with zipfile.ZipFile(args.archive) as zf:
        for heading, slugs in GROUPS:
            group = []
            for slug in slugs:
                member = find_member(zf, slug)
                raw = zf.read(member)
                with Image.open(io.BytesIO(raw)) as im:
                    image = im.convert("RGBA")
                group.append((slug, image))
                evidence.append({
                    "heading": heading,
                    "slug": slug,
                    "member": member,
                    "byte_sha256": digest(raw),
                    "pixel_sha256": digest(image.tobytes()),
                    "size": [image.width, image.height],
                })
            cards.append((heading, group))

    font = ImageFont.load_default()
    scale = 2
    pad = 12
    label_h = 34
    heading_h = 24
    cell_w = 360
    cell_h = 210
    cols = 4
    rows = sum((len(group) + cols - 1) // cols for _, group in cards)
    total_h = pad + sum(heading_h + ((len(group) + cols - 1) // cols) * cell_h + pad for _, group in cards)
    canvas = Image.new("RGB", (pad * 2 + cols * cell_w, total_h), "white")
    draw = ImageDraw.Draw(canvas)

    y = pad
    for heading, group in cards:
        draw.text((pad, y), heading, fill="black", font=font)
        y += heading_h
        for idx, (slug, im) in enumerate(group):
            row, col = divmod(idx, cols)
            x = pad + col * cell_w
            cy = y + row * cell_h
            # checker-free neutral presentation; preserve transparency on white.
            display = Image.new("RGBA", im.size, (255, 255, 255, 255))
            display.alpha_composite(im)
            display = display.convert("RGB").resize((im.width * scale, im.height * scale), Image.Resampling.NEAREST)
            canvas.paste(display, (x, cy + label_h))
            draw.text((x, cy + 2), slug, fill="black", font=font)
            # Short digest makes exact identity visible without trusting labels.
            row_e = next(e for e in evidence if e["slug"] == slug and e["heading"] == heading)
            draw.text((x, cy + 16), row_e["pixel_sha256"][:16], fill="black", font=font)
        y += ((len(group) + cols - 1) // cols) * cell_h + pad

    args.out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(args.out)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps({"groups": GROUPS, "evidence": evidence}, indent=2) + "\n", encoding="utf-8")
    print(f"rendered {len(evidence)} sprite proofs to {args.out}")


if __name__ == "__main__":
    main()
