#!/usr/bin/env python3
"""
Generate Mercury Redux title-screen assets while preserving Platinum's native
title-screen timing, layer behavior, intro, blinking prompt, and input logic.

Usage:
    python3 tools/generate_mercury_title.py vendor/pokeplatinum
"""

from __future__ import annotations

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance


def font_path(name: str) -> str:
    candidates = [
        f"/usr/share/fonts/truetype/dejavu/{name}.ttf",
        f"/usr/share/fonts/dejavu/{name}.ttf",
    ]
    for p in candidates:
        if Path(p).exists():
            return p
    raise FileNotFoundError(f"Required font not found: {name}")


def fit_font(draw, text: str, font_name: str, max_width: int, start_size: int):
    size = start_size
    while size > 8:
        font = ImageFont.truetype(font_path(font_name), size=size)
        box = draw.textbbox((0, 0), text, font=font, stroke_width=1)
        if box[2] - box[0] <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path(font_name), size=8)


def draw_metal_text(base: Image.Image, text: str, y: int, max_width: int, start_size: int, font_name: str, stroke: int = 2):
    draw = ImageDraw.Draw(base)
    font = fit_font(draw, text, font_name, max_width, start_size)
    box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke)
    w, h = box[2]-box[0], box[3]-box[1]
    x = (base.width - w) // 2

    # Slim shadow and restrained outline. The DS title screens use clean
    # anti-aliased artwork, not thick GBA-style pixel borders.
    shadow = Image.new("RGBA", base.size, (0,0,0,0))
    sd = ImageDraw.Draw(shadow)
    sd.text((x+1, y+2), text, font=font, fill=(10, 8, 24, 210),
            stroke_width=stroke+1, stroke_fill=(5, 4, 14, 225))
    shadow = shadow.filter(ImageFilter.GaussianBlur(0.45))
    base.alpha_composite(shadow)

    mask = Image.new("L", base.size, 0)
    md = ImageDraw.Draw(mask)
    md.text((x, y), text, font=font, fill=255, stroke_width=stroke, stroke_fill=255)

    # Silver/platinum vertical gradient.
    grad = Image.new("RGBA", base.size, (0,0,0,0))
    gp = grad.load()
    top = max(0, y)
    bottom = min(base.height, y+h+8)
    span = max(1, bottom-top)
    for yy in range(top, bottom):
        t=(yy-top)/span
        if t < .45:
            v=int(252 - 45*t)
        else:
            v=int(232 - 95*(t-.45))
        color=(v, v, min(255, v+12), 255)
        for xx in range(base.width):
            gp[xx,yy]=color
    base.alpha_composite(Image.composite(grad, Image.new("RGBA", base.size, (0,0,0,0)), mask))

    # Fine violet edge plus a bright top highlight gives the subtitle the
    # layered metallic/glass look common to DS-era title artwork.
    draw = ImageDraw.Draw(base)
    draw.text((x, y), text, font=font, fill=(0,0,0,0),
              stroke_width=1, stroke_fill=(104, 78, 188, 235))
    draw.line((x+3, y+2, x+w-3, y+2), fill=(242, 244, 255, 150), width=1)
    return y+h


def build_logo(path: Path):
    src = Image.open(path).convert("RGBA")

    # Preserve the authentic Pokémon wordmark from Platinum, remove the
    # Platinum-specific subtitle area, then rebuild that space as Mercury Redux.
    out = src.copy()
    clear_y = 65
    ImageDraw.Draw(out).rectangle((0, clear_y, out.width, out.height), fill=(0,0,0,0))

    # DS-era treatment: no chunky badge/plaque. Platinum's title art reads as
    # layered, anti-aliased 2D art with thin metallic edges and clean negative
    # space. Build Mercury the same way so it does not resemble a GBA ROM hack.
    accent = Image.new("RGBA", out.size, (0,0,0,0))
    ad = ImageDraw.Draw(accent)

    # Thin crystalline divider and restrained glow, matching the sharper DS look.
    ad.line((28, 116, 228, 116), fill=(42, 30, 82, 210), width=3)
    ad.line((34, 115, 222, 115), fill=(176, 158, 245, 235), width=1)
    ad.polygon([(21,116),(28,110),(35,116),(28,122)], fill=(98,70,184,230))
    ad.polygon([(221,116),(228,110),(235,116),(228,122)], fill=(98,70,184,230))
    accent = accent.filter(ImageFilter.GaussianBlur(0.35))
    out.alpha_composite(accent)

    # Wide, polished metallic subtitle with thin dark-violet depth instead of
    # heavy pixel outlines.
    end = draw_metal_text(out, "MERCURY", 66, 228, 35, "DejaVuSerifCondensed-Bold", 1)
    draw_metal_text(out, "R E D U X", min(101, end-1), 154, 14, "DejaVuSansCondensed-Bold", 1)

    # nitrogfx requires an indexed PNG with a palette. Reserve palette index 0
    # for transparency, then quantize the visible artwork into 255 colors.
    rgba = out.convert("RGBA")
    alpha = rgba.getchannel("A")
    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba.convert("RGB"), mask=alpha)
    q = rgb.quantize(colors=255, method=Image.Quantize.MEDIANCUT)

    old_palette = q.getpalette()[:255 * 3]
    pal = [0, 0, 0] + old_palette
    pal += [0] * (768 - len(pal))

    indexed = Image.new("P", rgba.size, 0)
    indexed.putpalette(pal)
    src_idx = q.load()
    dst_idx = indexed.load()
    a = alpha.load()
    for yy in range(rgba.height):
        for xx in range(rgba.width):
            dst_idx[xx, yy] = 0 if a[xx, yy] < 96 else min(255, src_idx[xx, yy] + 1)

    indexed.info["transparency"] = 0
    indexed.save(path, bits=8)


def tint_border(path: Path):
    # Keep the original 4bpp index map untouched and recolor only its first
    # 16 palette entries. This preserves Platinum's exact border tile layout.
    im = Image.open(path)
    if im.mode != "P":
        raise RuntimeError(f"{path} must remain a paletted PNG")

    pal = im.getpalette()
    if pal is None:
        raise RuntimeError(f"{path} does not contain a palette")

    new = pal[:]
    for i in range(16):
        r, g, b = pal[i*3:i*3+3]
        mx=max(r,g,b); mn=min(r,g,b)
        sat=mx-mn
        lum=(r+g+b)/3
        if lum < 235 and sat > 10:
            v=int(lum)
            nr=max(18,int(v*.66))
            ng=max(18,int(v*.58))
            nb=min(255,int(v*.92+35))
            new[i*3:i*3+3] = [nr, ng, nb]

    im.putpalette(new)
    im.save(path, bits=4)


def patch_prompt_color(source: Path):
    text=source.read_text()
    text=text.replace(
        "u16 letterColor = GX_RGB(21, 0, 0);\n    u16 shadowColor = GX_RGB(21, 0, 0);",
        "u16 letterColor = GX_RGB(26, 26, 31);\n    u16 shadowColor = GX_RGB(7, 4, 16);"
    )
    source.write_text(text)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_mercury_title.py <pokeplatinum-root>")
    root=Path(sys.argv[1]).resolve()
    gfx=root/"res/graphics/title_screen"
    logo=gfx/"logo.png"
    border=gfx/"top_screen_border.png"
    source=root/"src/applications/title_screen.c"

    for p in (logo,border,source):
        if not p.exists():
            raise SystemExit(f"missing required Platinum file: {p}")

    build_logo(logo)
    tint_border(border)
    patch_prompt_color(source)

    print("Mercury Redux title assets generated")
    print(f"logo: {logo}")
    print(f"border: {border}")
    print(f"source: {source}")


if __name__ == "__main__":
    main()
