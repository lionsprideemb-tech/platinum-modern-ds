#!/usr/bin/env python3
"""
Generate Mercury Redux title-screen assets while preserving Platinum's native
title-screen timing, layer behavior, intro, blinking prompt, and input logic.

Usage:
    python3 tools/generate_mercury_title.py vendor/pokeplatinum
"""

from __future__ import annotations

import struct
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


def recolor_nsbmd_palettes(path: Path, transforms: dict[str, str]):
    """Recolor named embedded TEX0 palettes without touching geometry/animation."""
    data = bytearray(path.read_bytes())
    if data[:4] != b"BMD0":
        raise RuntimeError(f"{path} is not an NSBMD/BMD0 file")
    if struct.unpack_from("<H", data, 4)[0] != 0xFEFF:
        raise RuntimeError(f"{path} has an unexpected Nitro byte order")

    section_count = struct.unpack_from("<H", data, 14)[0]
    tex0 = None
    for i in range(section_count):
        off = struct.unpack_from("<I", data, 16 + i * 4)[0]
        if data[off:off + 4] == b"TEX0":
            tex0 = off
            break
    if tex0 is None:
        raise RuntimeError(f"{path} has no embedded TEX0 section")

    palette_list_rel = struct.unpack_from("<I", data, tex0 + 0x34)[0]
    palette_data = tex0 + struct.unpack_from("<I", data, tex0 + 0x38)[0]
    palette_data_len = struct.unpack_from("<H", data, tex0 + 0x30)[0] << 3
    list_base = tex0 + palette_list_rel

    count = data[list_base + 1]
    sizes_off = list_base + 12 + count * 4
    elem_size = struct.unpack_from("<H", data, sizes_off)[0] or 4
    elem_data = sizes_off + 4
    names_off = elem_data + count * elem_size

    entries = []
    for i in range(count):
        raw_name = bytes(data[names_off + i * 16:names_off + (i + 1) * 16])
        name = raw_name.split(b"\x00", 1)[0].decode("ascii")
        off_shr3 = struct.unpack_from("<H", data, elem_data + i * elem_size)[0]
        entries.append((name, palette_data + (off_shr3 << 3)))

    entries.sort(key=lambda item: item[1])
    end_of_palettes = palette_data + palette_data_len

    def clamp5(value):
        return max(0, min(31, int(round(value))))

    def mercury_violet(r, g, b):
        # Keep truly neutral highlights silver; rotate red body/wing ramps into
        # saturated violet so Giratina remains high-contrast but no longer reads
        # like an untouched Platinum asset.
        if max(r, g, b) - min(r, g, b) <= 2 and max(r, g, b) >= 20:
            v = clamp5(max(r, g, b))
            return (v, v, min(31, v + 1))
        t = max(r, g, b) / 31.0
        return (
            clamp5(4 + 19 * t),
            clamp5(2 + 10 * t),
            clamp5(8 + 23 * t),
        )

    def mercury_platinum(r, g, b):
        # Giratina's vanilla yellow palette stores most of its useful shading
        # in the blue component. Remap that ramp to cool platinum/lavender.
        t = max(0.0, min(1.0, b / 23.0))
        return (
            clamp5(14 + 16 * t),
            clamp5(14 + 16 * t),
            clamp5(20 + 11 * t),
        )

    def mercury_cool_metal(r, g, b):
        t = max(r, g, b) / 31.0
        return (
            clamp5(9 + 21 * t),
            clamp5(10 + 21 * t),
            clamp5(16 + 15 * t),
        )

    palette_funcs = {
        "violet": mercury_violet,
        "platinum": mercury_platinum,
        "cool_metal": mercury_cool_metal,
    }

    found = set()
    for idx, (name, start) in enumerate(entries):
        mode = transforms.get(name)
        if mode is None:
            continue
        end = entries[idx + 1][1] if idx + 1 < len(entries) else end_of_palettes
        fn = palette_funcs[mode]
        for off in range(start, end, 2):
            color = struct.unpack_from("<H", data, off)[0]
            r = color & 0x1F
            g = (color >> 5) & 0x1F
            b = (color >> 10) & 0x1F
            nr, ng, nb = fn(r, g, b)
            struct.pack_into("<H", data, off, nr | (ng << 5) | (nb << 10))
        found.add(name)

    missing = set(transforms) - found
    if missing:
        raise RuntimeError(f"{path} is missing expected palettes: {sorted(missing)}")

    path.write_bytes(data)


def build_mercury_bottom_scene(path: Path):
    # Full 256x192 DS-native lower-screen composition. This remains a 4bpp
    # background behind Platinum's real animated 3D Giratina, so the original
    # model/animation pipeline stays intact while the surrounding presentation
    # becomes unmistakably Mercury Redux.
    palette = [
        (4, 3, 13),      # 0 near-black violet
        (8, 6, 24),      # 1
        (12, 8, 38),     # 2
        (17, 11, 54),    # 3
        (24, 16, 72),    # 4
        (34, 23, 94),    # 5
        (47, 32, 118),   # 6
        (63, 45, 143),   # 7
        (82, 63, 166),   # 8
        (105, 85, 190),  # 9
        (132, 113, 211), # 10
        (163, 148, 228), # 11
        (77, 114, 179),  # 12 cool-blue accent
        (113, 150, 207), # 13
        (163, 190, 230), # 14
        (231, 236, 250), # 15 silver-white
    ]

    im = Image.new("P", (256, 192), 0)
    flat = []
    for rgb in palette:
        flat.extend(rgb)
    flat += [0] * (768 - len(flat))
    im.putpalette(flat)
    px = im.load()

    # Vertical twilight gradient.
    for y in range(192):
        if y < 28:
            idx = 5
        elif y < 60:
            idx = 4
        elif y < 96:
            idx = 3
        elif y < 132:
            idx = 2
        elif y < 164:
            idx = 1
        else:
            idx = 0
        for x in range(256):
            px[x, y] = idx

    d = ImageDraw.Draw(im)

    # Distortion-space halo behind Giratina. These concentric broken arcs are
    # intentionally angular and sparse so they read clearly at 256x192.
    rings = [
        (28, 24, 228, 164, 6),
        (43, 36, 213, 154, 7),
        (59, 49, 197, 143, 8),
        (76, 62, 180, 132, 9),
    ]
    for box in rings:
        x0, y0, x1, y1, col = box
        d.arc((x0, y0, x1, y1), 196, 344, fill=col, width=2)
        d.arc((x0, y0, x1, y1), 16, 164, fill=max(5, col-1), width=1)

    # Subtle vertical rift glow in the center.
    for x, col in ((118, 6), (121, 7), (124, 8), (127, 9), (130, 8), (133, 7), (136, 6)):
        d.line((x, 42, x, 162), fill=col, width=1)

    # Crystalline/Distortion shards framing the model without covering it.
    left_shards = [
        [(0, 28), (28, 40), (5, 48)],
        [(0, 61), (35, 72), (7, 82)],
        [(0, 101), (31, 108), (3, 121)],
        [(12, 142), (42, 132), (31, 158)],
    ]
    right_shards = [
        [(255, 31), (226, 43), (252, 52)],
        [(255, 66), (221, 76), (250, 87)],
        [(255, 103), (224, 111), (252, 123)],
        [(244, 143), (214, 133), (225, 159)],
    ]
    shard_cols = [8, 7, 6, 5]
    for pts, col in zip(left_shards, shard_cols):
        d.polygon(pts, fill=col)
        d.line(pts + [pts[0]], fill=min(15, col + 3), width=1)
    for pts, col in zip(right_shards, shard_cols):
        d.polygon(pts, fill=col)
        d.line(pts + [pts[0]], fill=min(15, col + 3), width=1)

    # Small fixed star/glint pattern keeps the scene alive without looking
    # noisy or like a GBA-era tiled backdrop.
    stars = [
        (18, 18, 14), (47, 24, 12), (81, 16, 13), (174, 19, 13),
        (207, 27, 14), (236, 17, 12), (28, 91, 13), (228, 94, 13),
        (52, 154, 12), (202, 150, 12), (91, 173, 13), (165, 169, 13),
    ]
    for x, y, col in stars:
        d.point((x, y), fill=col)
        if col >= 13:
            d.point((x-1, y), fill=max(10, col-2))
            d.point((x+1, y), fill=max(10, col-2))
            d.point((x, y-1), fill=max(10, col-2))
            d.point((x, y+1), fill=max(10, col-2))

    # Thin lower crystalline horizon. Copyright text remains on its own
    # foreground layer above this.
    d.line((24, 173, 232, 173), fill=6, width=1)
    d.line((48, 176, 208, 176), fill=4, width=1)
    d.polygon([(20,173),(25,168),(30,173),(25,178)], fill=8)
    d.polygon([(226,173),(231,168),(236,173),(231,178)], fill=8)

    im.save(path, bits=4)


def install_binary_png(
    source_path: Path,
    output_path: Path,
    expected_size: tuple[int, int],
    expected_mode: str,
):
    output_path.write_bytes(source_path.read_bytes())

    # Validate the exact DS conversion inputs before nitrogfx sees them.
    with Image.open(output_path) as check:
        if check.size != expected_size:
            raise RuntimeError(f"{output_path} has wrong size: {check.size}, expected {expected_size}")
        if check.mode != expected_mode:
            raise RuntimeError(f"{output_path} has wrong mode: {check.mode}, expected {expected_mode}")


def write_jasc_palette_from_png(image_path: Path, palette_path: Path, color_count: int = 256):
    im = Image.open(image_path)
    if im.mode != "P":
        raise RuntimeError(f"{image_path} must remain a paletted PNG")
    pal = im.getpalette()
    if pal is None:
        raise RuntimeError(f"{image_path} does not contain a palette")

    colors = []
    for i in range(color_count):
        base = i * 3
        if base + 2 < len(pal):
            colors.append(tuple(pal[base:base + 3]))
        else:
            colors.append((0, 0, 0))

    lines = ["JASC-PAL", "0100", str(color_count)]
    lines.extend(f"{r} {g} {b}" for r, g, b in colors)
    # NitroGFX's JASC parser expects Windows CRLF endings.
    palette_path.write_bytes(("\r\n".join(lines) + "\r\n").encode("ascii"))


def pack_logo_with_blank_tile(path: Path):
    # Platinum's logo map uses tile 0 as the empty tile outside rows 3..18.
    # Preserve all 512 artwork tiles by packing them after a new blank tile 0.
    src = Image.open(path)
    if src.mode != "P" or src.size != (256, 128):
        raise RuntimeError(f"{path} must be a 256x128 paletted PNG")

    packed = Image.new("P", (256, 136), 0)
    packed.putpalette(src.getpalette())

    src_px = src.load()
    dst_px = packed.load()

    for tile in range(512):
        sx = (tile % 32) * 8
        sy = (tile // 32) * 8
        dst_tile = tile + 1
        dx = (dst_tile % 32) * 8
        dy = (dst_tile // 32) * 8
        for py in range(8):
            for px in range(8):
                dst_px[dx + px, dy + py] = src_px[sx + px, sy + py]

    packed.save(path)


def pack_border_with_blank_tile(path: Path):
    # The 4bpp footer also needs tile 0 reserved for transparent map cells.
    # Pack its 256 artwork tiles after a blank tile 0, exactly like the logo.
    src = Image.open(path)
    if src.mode != "P" or src.size != (256, 64):
        raise RuntimeError(f"{path} must be a 256x64 paletted PNG")

    packed = Image.new("P", (256, 72), 0)
    packed.putpalette(src.getpalette())

    src_px = src.load()
    dst_px = packed.load()

    for tile in range(256):
        sx = (tile % 32) * 8
        sy = (tile // 32) * 8
        dst_tile = tile + 1
        dx = (dst_tile % 32) * 8
        dy = (dst_tile // 32) * 8
        for py in range(8):
            for px in range(8):
                dst_px[dx + px, dy + py] = src_px[sx + px, sy + py]

    packed.save(path, bits=4)


def clear_last_tile(path: Path):
    # Reserve the final 8x8 tile as an empty tile for unused map cells while
    # preserving the artwork's natural tile 0 and row-major tile order.
    im = Image.open(path)
    if im.mode != "P":
        raise RuntimeError(f"{path} must remain a paletted PNG")
    px = im.load()
    x0 = im.width - 8
    y0 = im.height - 8
    for y in range(y0, im.height):
        for x in range(x0, im.width):
            px[x, y] = 0
    im.save(path)


def write_linear_nscr(path: Path, width_tiles: int, height_tiles: int, bitdepth: int, tile_for):
    data = bytearray()
    for y in range(height_tiles):
        for x in range(width_tiles):
            tile = tile_for(x, y)
            if tile < 0 or tile > 1023:
                raise RuntimeError(f"tile index {tile} out of range for {path}")
            data += struct.pack("<H", tile)

    section_size = len(data) + 0x14
    file_size = section_size + 0x10

    header = bytearray(b"RCSN")
    header += bytes((0xFF, 0xFE, 0x00, 0x01))
    header += struct.pack("<I", file_size)
    header += struct.pack("<H", 0x10)
    header += struct.pack("<H", 1)

    section = bytearray(b"NRCS")
    section += struct.pack("<I", section_size)
    section += struct.pack("<H", width_tiles * 8)
    section += struct.pack("<H", height_tiles * 8)
    section += bytes((0 if bitdepth == 4 else 1, 0, 0, 0))
    section += struct.pack("<I", len(data))

    path.write_bytes(header + section + data)


def build_mercury_tilemaps(gfx: Path):
    # Recreate Platinum's proven logo placement exactly, but point rows 3..18
    # at tiles 1..512. Tile 0 is now a true blank tile, so the top/bottom
    # areas no longer repeat the artwork's first 8x8 block.
    write_linear_nscr(
        gfx / "logo.NSCR",
        32,
        32,
        8,
        lambda x, y: ((y - 3) * 32 + x + 1) if 3 <= y < 19 else 0,
    )

    # Restore the Mercury footer into visible rows 16..23. Tile 0 remains
    # transparent everywhere else, while footer art occupies tiles 1..256.
    border_map = lambda x, y: ((y - 16) * 32 + x + 1) if 16 <= y < 24 else 0
    write_linear_nscr(gfx / "top_screen_border.NSCR", 32, 24, 4, border_map)
    write_linear_nscr(gfx / "top_screen_border_2.NSCR", 32, 32, 4, border_map)

    # Full-screen lower Mercury scene: one native DS tile per map cell.
    lower_map = lambda x, y: y * 32 + x
    write_linear_nscr(gfx / "bottom_screen_border.NSCR", 32, 24, 4, lower_map)
    write_linear_nscr(gfx / "bottom_screen_border_2.NSCR", 32, 24, 4, lower_map)


def patch_title_runtime(source: Path):
    text=source.read_text()

    prompt_old = (
        "u16 letterColor = GX_RGB(21, 0, 0);\n"
        "    u16 shadowColor = GX_RGB(21, 0, 0);"
    )
    prompt_new = (
        "u16 letterColor = GX_RGB(26, 26, 31);\n"
        "    u16 shadowColor = GX_RGB(7, 4, 16);"
    )
    if prompt_old not in text:
        raise RuntimeError("could not locate Platinum PRESS START palette code")
    text=text.replace(prompt_old, prompt_new, 1)

    # Mercury's logo keeps Platinum's restrained title-screen feel, but gets a
    # very small vertical 'breathing' motion. It is tied to the same 3-second
    # sine cycle already used by the title renderer, so there is no new timer
    # or timing path to destabilize the original application.
    motion_old = (
        "        titleScreen->blinkCounter++;\n"
        "        titleScreen->blinkCounter &= 31;\n\n"
        "        result = TRUE;"
    )
    motion_new = (
        "        titleScreen->blinkCounter++;\n"
        "        titleScreen->blinkCounter &= 31;\n\n"
        "        // Mercury Redux: subtle DS-native logo float (about +/-2 px).\n"
        "        Bg_SetOffset(bgConfig, TITLE_SCREEN_LAYER_LOGO, BG_OFFSET_UPDATE_SET_Y,\n"
        "            (CalcSineDegrees_Wraparound(titleScreen->giratinaHoverAngle) * 2) >> FX32_SHIFT);\n\n"
        "        result = TRUE;"
    )
    if motion_old not in text:
        raise RuntimeError("could not locate Platinum title idle loop")
    text=text.replace(motion_old, motion_new, 1)

    blend_old = "    G2S_SetBlendAlpha(GX_BLEND_PLANEMASK_BG0 | GX_BLEND_PLANEMASK_BG1, GX_BLEND_PLANEMASK_BG2 | GX_BLEND_PLANEMASK_BG3, 26, 10);"
    if blend_old not in text:
        raise RuntimeError("could not locate Platinum final title blend")
    text = text.replace(blend_old, "    G2S_BlendNone();", 1)

    # Mercury lower-screen color grade: preserve Platinum's animated 3D
    # Giratina, but cool the lighting toward silver/violet so it visually
    # belongs with the custom top screen instead of reading as a separate red/
    # yellow composition.
    light0_old = "    NNS_G3dGlbLightColor(GX_LIGHTID_0, COLOR_WHITE);"
    light0_new = "    NNS_G3dGlbLightColor(GX_LIGHTID_0, LIGHT_COLOR(26, 28, 31));"
    if light0_old not in text:
        raise RuntimeError("could not locate Platinum primary title light")
    text = text.replace(light0_old, light0_new, 1)

    dynamic_light_old = (
        "    NNS_G3dGlbLightColor(GX_LIGHTID_1, LIGHT_COLOR(titleScreen->light1Brightness, "
        "titleScreen->light1Brightness, titleScreen->light1Brightness));"
    )
    dynamic_light_new = (
        "    NNS_G3dGlbLightColor(GX_LIGHTID_1, "
        "LIGHT_COLOR((titleScreen->light1Brightness * 3) / 4, "
        "(titleScreen->light1Brightness * 2) / 3, titleScreen->light1Brightness));"
    )
    if dynamic_light_old not in text:
        raise RuntimeError("could not locate Platinum animated secondary light")
    text = text.replace(dynamic_light_old, dynamic_light_new, 1)

    main_light_old = "        NNS_G3dGlbLightColor(GX_LIGHTID_1, COLOR_WHITE);"
    main_light_new = "        NNS_G3dGlbLightColor(GX_LIGHTID_1, LIGHT_COLOR(23, 20, 31));"
    if main_light_old not in text:
        raise RuntimeError("could not locate Platinum main-state secondary light")
    text = text.replace(main_light_old, main_light_new, 1)

    # The redesigned lower screen uses a full 256x192 4bpp tile set
    # (24 KiB), far larger than Platinum's tiny vanilla border strip. Move
    # BG3's character data to 0x8000 so it cannot overlap the main-screen
    # tilemaps at 0x2000/0x3800 or the copyright tiles at 0x4000.
    giratina_bg_old = (
        "    BgTemplate bgMain3 = {\n"
        "        .x = 0,\n"
        "        .y = 0,\n"
        "        .bufferSize = 0x800,\n"
        "        .baseTile = 0,\n"
        "        .screenSize = BG_SCREEN_SIZE_256x256,\n"
        "        .colorMode = GX_BG_COLORMODE_16,\n"
        "        .screenBase = GX_BG_SCRBASE_0x2000,\n"
        "        .charBase = GX_BG_CHARBASE_0x00000,"
    )
    giratina_bg_new = (
        "    BgTemplate bgMain3 = {\n"
        "        .x = 0,\n"
        "        .y = 0,\n"
        "        .bufferSize = 0x800,\n"
        "        .baseTile = 0,\n"
        "        .screenSize = BG_SCREEN_SIZE_256x256,\n"
        "        .colorMode = GX_BG_COLORMODE_16,\n"
        "        .screenBase = GX_BG_SCRBASE_0x2000,\n"
        "        .charBase = GX_BG_CHARBASE_0x08000,"
    )
    if giratina_bg_old not in text:
        raise RuntimeError("could not locate Platinum Giratina background template")
    text = text.replace(giratina_bg_old, giratina_bg_new, 1)

    source.write_text(text)

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_mercury_title.py <pokeplatinum-root>")
    root=Path(sys.argv[1]).resolve()
    gfx=root/"res/graphics/title_screen"
    logo=gfx/"logo.png"
    border=gfx/"top_screen_border.png"
    bottom_border=gfx/"bottom_screen_border.png"
    giratina_model=gfx/"giratina.nsbmd"
    giratina_face_model=gfx/"giratina_face.nsbmd"
    giratina_portal_model=gfx/"giratina_portal.nsbmd"
    source=root/"src/applications/title_screen.c"

    project_root=Path(__file__).resolve().parent.parent
    asset_dir=project_root/"assets/title_screen"
    logo_asset=asset_dir/"mercury_logo_top_256x128.png"
    border_asset=asset_dir/"mercury_top_footer_256x64.png"

    for p in (logo,border,bottom_border,giratina_model,giratina_face_model,giratina_portal_model,source,logo_asset,border_asset):
        if not p.exists():
            raise SystemExit(f"missing required Mercury title file: {p}")

    # TIT02 visual pass: install the approved DS-scaled Mercury artwork rather
    # than approximating the title with runtime-generated text. The upper
    # 256x128 art contains the branded scene/logo; the lower 256x64 strip leaves
    # clean space for Platinum's live PRESS START layer.
    install_binary_png(
        logo_asset,
        logo,
        (256, 128),
        "P",
    )
    install_binary_png(
        border_asset,
        border,
        (256, 64),
        "P",
    )

    build_mercury_bottom_scene(bottom_border)

    # Title-screen-only Giratina color treatment. Geometry, skeletal animation,
    # texture animation, and portal motion stay vanilla; only embedded palettes
    # are shifted into Mercury's platinum/violet identity.
    recolor_nsbmd_palettes(
        giratina_model,
        {
            "gira01_pl": "violet",
            "gira02_pl": "platinum",
        },
    )
    recolor_nsbmd_palettes(
        giratina_face_model,
        {
            "op_ana07_pl": "violet",
        },
    )
    recolor_nsbmd_palettes(
        giratina_portal_model,
        {
            "op_ana02_pl": "cool_metal",
        },
    )

    pack_logo_with_blank_tile(logo)
    pack_border_with_blank_tile(border)
    write_jasc_palette_from_png(border, gfx/"top_screen_border.pal", 256)
    build_mercury_tilemaps(gfx)
    patch_title_runtime(source)

    print("Mercury Redux title assets generated")
    print(f"logo: {logo}")
    print(f"border: {border}")
    print(f"bottom border: {bottom_border}")
    print(f"Giratina model: {giratina_model}")
    print(f"Giratina face model: {giratina_face_model}")
    print(f"Giratina portal model: {giratina_portal_model}")
    print(f"source: {source}")


if __name__ == "__main__":
    main()
