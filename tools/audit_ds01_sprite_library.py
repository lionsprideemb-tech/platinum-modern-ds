#!/usr/bin/env python3
"""Audit staged DS01 community sprites for duplicates, recolors, near-duplicates, and concept collisions.

This is an analysis-only tool. It never installs or rewrites sprite assets.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable

from PIL import Image

IMAGE_EXTS = {".png", ".bmp", ".gif", ".jpg", ".jpeg", ".webp"}
ARCHIVE_EXTS = {".zip"}
DROP_TOKENS = {
    "front", "back", "male", "female", "m", "f", "normal", "regular",
    "shiny", "icon", "icons", "sprite", "sprites", "battle", "battler",
    "idle", "anim", "animation", "frame", "palette", "pal", "sheet",
    "converted", "conversion", "reference", "ref", "ds", "gba",
}


@dataclass
class Entry:
    path: str
    source_archive: str
    species_label: str
    width: int
    height: int
    mode: str
    byte_sha256: str
    pixel_sha256: str
    canonical_palette_sha256: str
    dhash64: int
    color_count: int
    is_sprite_candidate: bool
    is_visual_candidate: bool
    concept_key: str
    top_bucket: str


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def species_label(path: str) -> str:
    parts = [p for p in path.replace("\\", "/").split("/") if p]
    for i, part in enumerate(parts):
        if part.lower() == "sprites" and i + 1 < len(parts):
            return parts[i + 1].lower()
    return Path(path).stem.lower()


def concept_key(path: str) -> str:
    """Normalize a logical sprite identity without collapsing legitimate roles."""
    clean = path.replace("\\", "/").lower()
    # HG-Engine-ready layout: .../sprites/<species>/<gender>/<front|back>.png
    m = re.search(r"/sprites/([^/]+)/(male|female)/(front|back)\.[a-z0-9]+$", clean)
    if m:
        species, gender, view = m.groups()
        return f"{species} {gender} {view}"

    # Icon identity: .../sprites/<species>/icon.png
    m = re.search(r"/sprites/([^/]+)/icon\.[a-z0-9]+$", clean)
    if m:
        return f"{m.group(1)} icon"

    # Generic source-pack fallback: retain meaningful filename tokens and the
    # nearest parent directory so alternate forms with generic front/back names
    # do not all collapse into one bucket.
    p = Path(clean.split("::")[-1])
    stem = p.stem
    parent = p.parent.name
    tokens = [t for t in re.split(r"[^a-z0-9]+", f"{parent} {stem}") if t]
    tokens = [t for t in tokens if t not in {"sprite", "sprites", "battle", "battler", "idle", "anim", "animation", "frame", "sheet", "converted", "conversion", "reference", "ref", "ds", "gba"}]
    return " ".join(tokens)


def top_bucket(path: str) -> str:
    """Return a useful source/origin bucket rather than the common archive root."""
    clean = path.replace("\\", "/")
    if "::" in clean:
        outer, inner = clean.split("::", 1)
        return f"nested:{Path(outer).stem}"
    parts = [p for p in clean.split("/") if p]
    for marker in ("hg_engine_ready", "partial_assets", "raw_source_packs", "previews", "source_metadata", "manifests"):
        if marker in parts:
            idx = parts.index(marker)
            if idx + 1 < len(parts) and marker in {"partial_assets", "raw_source_packs", "source_metadata", "manifests"}:
                return f"{marker}:{parts[idx + 1]}"
            return marker
    return parts[0] if parts else ""


def canonical_palette_hash(img: Image.Image) -> str:
    rgba = img.convert("RGBA")
    mapping: dict[tuple[int, int, int, int], int] = {}
    next_id = 1
    ids = bytearray()
    for px in rgba.getdata():
        if px[3] == 0:
            idx = 0
        else:
            if px not in mapping:
                mapping[px] = next_id
                next_id += 1
            idx = mapping[px]
        # DS-style sprites should stay tiny-palette, but two bytes keeps this generic.
        ids += int(idx).to_bytes(4, "little", signed=False)
    header = f"{rgba.width}x{rgba.height}:".encode("ascii")
    return sha256(header + bytes(ids))


def dhash64(img: Image.Image) -> int:
    rgba = img.convert("RGBA")
    base = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    base.alpha_composite(rgba)
    gray = base.convert("L").resize((9, 8), Image.Resampling.BILINEAR)
    px = list(gray.getdata())
    out = 0
    bit = 0
    for y in range(8):
        row = y * 9
        for x in range(8):
            if px[row + x] > px[row + x + 1]:
                out |= 1 << bit
            bit += 1
    return out


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


class BKNode:
    __slots__ = ("value", "indices", "children")

    def __init__(self, value: int, index: int):
        self.value = value
        self.indices = [index]
        self.children: dict[int, "BKNode"] = {}


class BKTree:
    def __init__(self):
        self.root: BKNode | None = None

    def add(self, value: int, index: int) -> None:
        if self.root is None:
            self.root = BKNode(value, index)
            return
        node = self.root
        while True:
            d = hamming(value, node.value)
            if d == 0:
                node.indices.append(index)
                return
            nxt = node.children.get(d)
            if nxt is None:
                node.children[d] = BKNode(value, index)
                return
            node = nxt

    def query(self, value: int, radius: int) -> Iterable[tuple[int, int]]:
        if self.root is None:
            return []
        found: list[tuple[int, int]] = []
        stack = [self.root]
        while stack:
            node = stack.pop()
            d = hamming(value, node.value)
            if d <= radius:
                for idx in node.indices:
                    found.append((idx, d))
            lo, hi = d - radius, d + radius
            for edge, child in node.children.items():
                if lo <= edge <= hi:
                    stack.append(child)
        return found


class DSU:
    def __init__(self, n: int):
        self.p = list(range(n))
        self.sz = [1] * n

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if self.sz[ra] < self.sz[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.sz[ra] += self.sz[rb]


def load_entry(raw: bytes, logical_path: str, archive_name: str) -> Entry | None:
    try:
        with Image.open(io.BytesIO(raw)) as im:
            im.seek(0)
            rgba = im.convert("RGBA")
    except Exception:
        return None

    colors = rgba.getcolors(maxcolors=257)
    color_count = len(colors) if colors is not None else 257
    candidate = (
        8 <= rgba.width <= 256
        and 8 <= rgba.height <= 256
        and color_count <= 256
    )

    pixel_blob = f"{rgba.width}x{rgba.height}:RGBA:".encode("ascii") + rgba.tobytes()
    if candidate:
        palette_hash = canonical_palette_hash(rgba)
        perceptual = dhash64(rgba)
    else:
        palette_hash = ""
        perceptual = 0

    clean = logical_path.replace("\\", "/").lower()
    visual_candidate = bool(
        candidate
        and (
            clean.endswith("/male/front.png")
            or (
                "/male/front.png" not in clean
                and clean.endswith("/female/front.png")
            )
        )
    )

    return Entry(
        path=logical_path,
        source_archive=archive_name,
        species_label=species_label(logical_path),
        width=rgba.width,
        height=rgba.height,
        mode="RGBA",
        byte_sha256=sha256(raw),
        pixel_sha256=sha256(pixel_blob),
        canonical_palette_sha256=palette_hash,
        dhash64=perceptual,
        color_count=color_count,
        is_sprite_candidate=candidate,
        is_visual_candidate=visual_candidate,
        concept_key=concept_key(logical_path),
        top_bucket=top_bucket(logical_path),
    )

def scan_zip_bytes(
    blob: bytes,
    archive_name: str,
    prefix: str = "",
    path_contains: str | None = None,
) -> list[Entry]:
    out: list[Entry] = []
    try:
        zf = zipfile.ZipFile(io.BytesIO(blob))
    except zipfile.BadZipFile:
        return out

    for info in zf.infolist():
        if info.is_dir():
            continue
        name = info.filename.replace("\\", "/")
        logical = f"{prefix}{name}" if prefix else name
        ext = Path(name).suffix.lower()

        if ext in IMAGE_EXTS:
            if path_contains and path_contains not in logical:
                continue
            try:
                raw = zf.read(info)
            except Exception:
                continue
            e = load_entry(raw, logical, archive_name)
            if e is not None:
                out.append(e)
        elif ext in ARCHIVE_EXTS and path_contains is None:
            try:
                raw = zf.read(info)
            except Exception:
                continue
            nested_prefix = logical + "::"
            out.extend(scan_zip_bytes(raw, archive_name, nested_prefix, path_contains=None))
    return out


def grouped(
    entries: list[Entry],
    attr: str,
    candidate_only: bool = True,
    visual_only: bool = False,
) -> list[list[int]]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for i, e in enumerate(entries):
        if candidate_only and not e.is_sprite_candidate:
            continue
        if visual_only and not e.is_visual_candidate:
            continue
        buckets[str(getattr(e, attr))].append(i)
    groups = [g for g in buckets.values() if len(g) > 1]
    groups.sort(key=lambda g: (-len(g), entries[g[0]].path))
    return groups


def near_groups(entries: list[Entry], radius: int = 4) -> list[list[int]]:
    """Cluster perceptually close sprite candidates without quadratic duplicate-hash blowups."""
    candidates = [i for i, e in enumerate(entries) if e.is_visual_candidate]
    by_dim_hash: dict[tuple[int, int], dict[int, list[int]]] = defaultdict(lambda: defaultdict(list))
    for i in candidates:
        e = entries[i]
        by_dim_hash[(e.width, e.height)][e.dhash64].append(i)

    dsu = DSU(len(entries))

    for _, hash_map in by_dim_hash.items():
        # Same dHash value is already a distance-0 perceptual match. Union once per member.
        for ids in hash_map.values():
            anchor = ids[0]
            for i in ids[1:]:
                dsu.union(anchor, i)

        # Compare unique dHash values only. This avoids O(n^2) behavior when many
        # sprites share a common silhouette/hash (blank frames, icons, palettes, etc.).
        tree = BKTree()
        representative_for_hash: dict[int, int] = {}
        for dh, ids in hash_map.items():
            rep = ids[0]
            for other_rep, dist in tree.query(dh, radius):
                if dist <= radius:
                    dsu.union(rep, other_rep)
            tree.add(dh, rep)
            representative_for_hash[dh] = rep

    buckets: dict[int, list[int]] = defaultdict(list)
    for i in candidates:
        root = dsu.find(i)
        if dsu.sz[root] > 1:
            buckets[root].append(i)

    groups: list[list[int]] = []
    for g in buckets.values():
        if len(g) < 2:
            continue
        # Pure exact-pixel and pure palette-recolor groups are already reported
        # in cleaner categories; keep only groups that add genuine near-visual signal.
        if len({entries[i].pixel_sha256 for i in g}) == 1:
            continue
        if len({entries[i].canonical_palette_sha256 for i in g}) == 1:
            continue
        groups.append(g)

    groups.sort(key=lambda g: (-len(g), entries[g[0]].path))
    return groups


def concept_groups(entries: list[Entry]) -> list[list[int]]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for i, e in enumerate(entries):
        if not e.is_visual_candidate or not e.concept_key:
            continue
        buckets[e.concept_key].append(i)

    groups = []
    for _, ids in buckets.items():
        labels = {entries[i].species_label for i in ids}
        if len(labels) < 2:
            continue
        pixels = {entries[i].pixel_sha256 for i in ids}
        if len(pixels) > 1:
            groups.append(ids)
    groups.sort(key=lambda g: (-len(g), entries[g[0]].concept_key, entries[g[0]].path))
    return groups


def summarize_group(entries: list[Entry], ids: list[int], kind: str) -> dict:
    sample = [entries[i] for i in ids]
    return {
        "kind": kind,
        "count": len(ids),
        "dimensions": sorted({f"{e.width}x{e.height}" for e in sample}),
        "concept_keys": sorted({e.concept_key for e in sample if e.concept_key}),
        "species_labels": sorted({e.species_label for e in sample if e.species_label}),
        "source_buckets": sorted({e.top_bucket for e in sample if e.top_bucket}),
        "paths": [e.path for e in sample],
    }


def write_markdown(report: dict, path: Path) -> None:
    lines = [
        "# DS01 Sprite Library Duplicate Audit",
        "",
        "Status: ANALYSIS ONLY — no sprite assets were installed, replaced, recolored, or deleted.",
        "",
        "## Summary",
        "",
        f"- Images scanned: **{report['summary']['images_scanned']}**",
        f"- Sprite candidates: **{report['summary']['sprite_candidates']}**",
        f"- Male/front visual representatives: **{report['summary']['visual_representatives']}**",
        f"- Exact byte-duplicate groups: **{report['summary']['exact_byte_groups']}**",
        f"- Exact rendered-pixel duplicate groups: **{report['summary']['exact_pixel_groups']}**",
        f"- Palette/recolor candidate groups: **{report['summary']['palette_recolor_groups']}**",
        f"- Near-visual duplicate groups (dHash <= {report['near_duplicate_radius']}): **{report['summary']['near_visual_groups']}**",
        f"- Concept-name collision groups: **{report['summary']['concept_collision_groups']}**",
        "",
        "### Classification",
        "",
        "- **Exact byte duplicate**: identical encoded image bytes.",
        "- **Exact pixel duplicate**: different files/encodings that render identically.",
        "- **Palette/recolor candidate**: identical per-pixel color-pattern topology after palette labels are normalized, but different rendered RGB values.",
        "- **Near visual duplicate**: same dimensions and perceptual dHash distance within the configured threshold, excluding exact/palette matches.",
        "- **Concept collision**: normalized sprite naming points at the same concept across multiple distinct visuals or source buckets.",
        "",
    ]

    sections = [
        ("Exact byte duplicates", report["groups"]["exact_bytes"]),
        ("Exact rendered-pixel duplicates", report["groups"]["exact_pixels"]),
        ("Palette / recolor candidates", report["groups"]["palette_recolors"]),
        ("Near visual duplicates", report["groups"]["near_visual"]),
        ("Duplicated concept candidates", report["groups"]["concept_collisions"]),
    ]
    for title, groups in sections:
        lines += [f"## {title}", ""]
        if not groups:
            lines += ["None detected.", ""]
            continue
        for n, g in enumerate(groups[:100], 1):
            label = ", ".join(g.get("concept_keys") or []) or "(unnamed)"
            lines += [
                f"### {n}. {label} — {g['count']} files",
                "",
                f"Dimensions: {', '.join(g['dimensions'])}",
                "",
                f"Source buckets: {', '.join(g['source_buckets']) or '(none)'}",
                "",
            ]
            for p in g["paths"][:30]:
                lines.append(f"- `{p}`")
            if len(g["paths"]) > 30:
                lines.append(f"- … {len(g['paths']) - 30} more")
            lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("--json", dest="json_path", type=Path, required=True)
    ap.add_argument("--markdown", dest="md_path", type=Path, required=True)
    ap.add_argument("--near-radius", type=int, default=4)
    ap.add_argument("--path-contains", default=None)
    args = ap.parse_args()

    blob = args.archive.read_bytes()
    entries = scan_zip_bytes(blob, args.archive.name, path_contains=args.path_contains)

    exact_bytes = grouped(entries, "byte_sha256")
    exact_pixels_all = grouped(entries, "pixel_sha256")
    # Keep pixel duplicate groups that are not merely the same exact byte hash.
    exact_pixels = [
        g for g in exact_pixels_all
        if len({entries[i].byte_sha256 for i in g}) > 1
    ]
    palette_all = grouped(entries, "canonical_palette_sha256", visual_only=True)
    palette_recolors = [
        g for g in palette_all
        if len({entries[i].pixel_sha256 for i in g}) > 1
    ]
    near = near_groups(entries, radius=args.near_radius)
    concepts = concept_groups(entries)

    report = {
        "gate": "MERCURY_DS01_SPRITE_LIBRARY_DUPLICATE_AUDIT",
        "status": "PASS",
        "analysis_only": True,
        "archive": str(args.archive),
        "archive_sha256": sha256(blob),
        "near_duplicate_radius": args.near_radius,
        "path_filter": args.path_contains,
        "summary": {
            "images_scanned": len(entries),
            "sprite_candidates": sum(1 for e in entries if e.is_sprite_candidate),
            "visual_representatives": sum(1 for e in entries if e.is_visual_candidate),
            "exact_byte_groups": len(exact_bytes),
            "exact_pixel_groups": len(exact_pixels),
            "palette_recolor_groups": len(palette_recolors),
            "near_visual_groups": len(near),
            "concept_collision_groups": len(concepts),
        },
        "groups": {
            "exact_bytes": [summarize_group(entries, g, "exact_bytes") for g in exact_bytes],
            "exact_pixels": [summarize_group(entries, g, "exact_pixels") for g in exact_pixels],
            "palette_recolors": [summarize_group(entries, g, "palette_recolor") for g in palette_recolors],
            "near_visual": [summarize_group(entries, g, "near_visual") for g in near],
            "concept_collisions": [summarize_group(entries, g, "concept_collision") for g in concepts],
        },
        "entries": [asdict(e) for e in entries],
    }

    args.json_path.parent.mkdir(parents=True, exist_ok=True)
    args.json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown(report, args.md_path)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
