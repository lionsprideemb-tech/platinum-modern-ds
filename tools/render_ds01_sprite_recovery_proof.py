#!/usr/bin/env python3
"""Render side-by-side review of recovered/alternate DS01 custom-form candidates."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

GROUPS = [
    ("Darkrai recovery", ["darkrai_mega", "darkrai-mega"]),
    ("Heatran recovery", ["heatran_mega", "heatran-mega"]),
    ("Zeraora recovery", ["zeraora_mega", "zeraora-mega"]),
    ("Lapras alternatives", ["lapras_mega", "lapras-gmax", "lapras_mega_x"]),
    ("Toxtricity alternatives", ["toxtricity_mega", "toxtricity-amped-gmax", "toxtricity_redux_mega", "toxtricity_redux_fuzz_mega"]),
    ("Inteleon alternatives", ["inteleon_mega", "inteleon-gmax", "cpf_0357_inteleon_alternate_form_2"]),
    ("Machamp alternatives", ["machamp_mega", "machamp-gmax", "machamp_mega_redux"]),
    ("Snorlax alternatives", ["snorlax_mega", "snorlax-gmax", "snorlax_redux_mega", "snorlax_primal"]),
]


def member_for(zf: zipfile.ZipFile, slug: str) -> str:
    suffix=f"/hg_engine_ready/data/graphics/sprites/{slug}/male/front.png"
    matches=[n for n in zf.namelist() if n.replace("\\","/").endswith(suffix)]
    if not matches:
        raise KeyError(f"missing {slug}")
    return matches[0]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--json", dest="json_out", type=Path, required=True)
    args=ap.parse_args()

    font=ImageFont.load_default()
    rows=[]
    evidence=[]
    with zipfile.ZipFile(args.archive) as zf:
        for heading, slugs in GROUPS:
            items=[]
            for slug in slugs:
                member=member_for(zf,slug)
                raw=zf.read(member)
                with Image.open(io.BytesIO(raw)) as im:
                    rgba=im.convert("RGBA")
                pix=sha(f"{rgba.width}x{rgba.height}:RGBA:".encode("ascii")+rgba.tobytes())
                evidence.append({"group":heading,"slug":slug,"member":member,"pixel_sha256":pix,"byte_sha256":sha(raw),"size":[rgba.width,rgba.height]})
                items.append((slug,rgba,pix))
            rows.append((heading,items))

    scale=2
    pad=12
    cell_w=360
    cell_h=210
    heading_h=26
    max_cols=4
    total_h=pad+sum(heading_h+((len(items)+max_cols-1)//max_cols)*cell_h+pad for _,items in rows)
    canvas=Image.new("RGB",(pad*2+max_cols*cell_w,total_h),"white")
    draw=ImageDraw.Draw(canvas)
    y=pad
    for heading,items in rows:
        draw.text((pad,y),heading,fill="black",font=font)
        y+=heading_h
        for idx,(slug,im,pix) in enumerate(items):
            rr,cc=divmod(idx,max_cols)
            x=pad+cc*cell_w
            cy=y+rr*cell_h
            draw.text((x,cy+2),slug,fill="black",font=font)
            draw.text((x,cy+16),pix[:16],fill="black",font=font)
            bg=Image.new("RGBA",im.size,(255,255,255,255))
            bg.alpha_composite(im)
            disp=bg.convert("RGB").resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST)
            canvas.paste(disp,(x,cy+34))
        y+=((len(items)+max_cols-1)//max_cols)*cell_h+pad

    args.out.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(args.out)
    args.json_out.write_text(json.dumps({"groups":GROUPS,"evidence":evidence},indent=2)+"\n",encoding="utf-8")
    print(f"rendered {len(evidence)} candidates")


if __name__ == "__main__":
    main()
