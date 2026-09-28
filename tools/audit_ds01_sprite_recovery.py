#!/usr/bin/env python3
"""Search every staged DS01 source pack for replacement/recovery art for quarantined sprites."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from PIL import Image

IMAGE_EXTS = {".png", ".bmp", ".gif", ".jpg", ".jpeg", ".webp"}
TEXT_EXTS = {".csv", ".json", ".txt", ".md"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def target_aliases(slug: str) -> list[str]:
    raw = normalize(slug)
    words = raw.split()
    drop = {
        "mega", "gmax", "redux", "alternate", "form", "style", "male", "female",
        "front", "back", "icon", "single", "rapid", "strike", "amped", "low", "key",
        "z", "bond",
    }
    core = [w for w in words if w not in drop and not w.isdigit() and w != "cpf"]
    aliases = {raw}
    if core:
        aliases.add(" ".join(core))
        aliases.add(core[0])
    # Species-first alias is valuable for source packs named only by species.
    if words:
        for w in words:
            if w not in drop and not w.isdigit() and w != "cpf":
                aliases.add(w)
                break
    return sorted((a for a in aliases if len(a) >= 3), key=len, reverse=True)


def load_image_info(raw: bytes) -> dict | None:
    try:
        with Image.open(io.BytesIO(raw)) as im:
            im.seek(0)
            rgba = im.convert("RGBA")
    except Exception:
        return None
    return {
        "width": rgba.width,
        "height": rgba.height,
        "pixel_sha256": digest(f"{rgba.width}x{rgba.height}:RGBA:".encode("ascii") + rgba.tobytes()),
    }


def collect_targets(q: dict) -> list[str]:
    out = []
    for row in q.get("confirmed_blockers", []):
        out.extend(row.get("entries", []))
    for row in q.get("palette_review", []):
        out.extend(row.get("entries", []))
    for row in q.get("near_duplicate_review", []):
        out.extend(row)
    return sorted(set(out))


def find_ready_member(zf: zipfile.ZipFile, slug: str) -> str | None:
    suffix = f"/hg_engine_ready/data/graphics/sprites/{slug}/male/front.png"
    for name in zf.namelist():
        if name.replace("\\", "/").endswith(suffix):
            return name
    return None


def iter_nested_images(outer: zipfile.ZipFile):
    for info in outer.infolist():
        if info.is_dir():
            continue
        name = info.filename.replace("\\", "/")
        ext = Path(name).suffix.lower()
        if ext == ".zip":
            try:
                blob = outer.read(info)
                nested = zipfile.ZipFile(io.BytesIO(blob))
            except Exception:
                continue
            for ni in nested.infolist():
                if ni.is_dir():
                    continue
                nname = ni.filename.replace("\\", "/")
                if Path(nname).suffix.lower() not in IMAGE_EXTS:
                    continue
                try:
                    raw = nested.read(ni)
                except Exception:
                    continue
                yield f"{name}::{nname}", raw
        elif ext in IMAGE_EXTS and "/hg_engine_ready/" not in name:
            try:
                raw = outer.read(info)
            except Exception:
                continue
            yield name, raw


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("quarantine", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    q = json.loads(args.quarantine.read_text(encoding="utf-8"))
    targets = collect_targets(q)
    aliases = {t: target_aliases(t) for t in targets}

    report = {
        "gate": "MERCURY_DS01_SPRITE_RECOVERY_SEARCH",
        "status": "PASS",
        "analysis_only": True,
        "targets": {},
        "manifest_hits": {},
    }

    with zipfile.ZipFile(args.archive) as outer:
        ready = {}
        for t in targets:
            member = find_ready_member(outer, t)
            if member:
                raw = outer.read(member)
                info = load_image_info(raw)
                ready[t] = {
                    "member": member,
                    "byte_sha256": digest(raw),
                    **(info or {}),
                }

        candidates: dict[str, list[dict]] = defaultdict(list)
        seen_paths: dict[str, set[str]] = defaultdict(set)

        for logical, raw in iter_nested_images(outer):
            hay = normalize(logical)
            matched = []
            for t in targets:
                # Require the strongest available alias to appear as a token phrase.
                if any(a in hay for a in aliases[t]):
                    matched.append(t)
            if not matched:
                continue

            info = load_image_info(raw)
            if info is None:
                continue
            byte_hash = digest(raw)

            for t in matched:
                if logical in seen_paths[t]:
                    continue
                seen_paths[t].add(logical)
                base = ready.get(t, {})
                row = {
                    "path": logical,
                    "width": info["width"],
                    "height": info["height"],
                    "byte_sha256": byte_hash,
                    "pixel_sha256": info["pixel_sha256"],
                    "same_render_as_ready": (
                        bool(base.get("pixel_sha256"))
                        and base.get("pixel_sha256") == info["pixel_sha256"]
                    ),
                }
                candidates[t].append(row)

        # Search archive text manifests too; these often preserve source provenance
        # even when source-pack filenames are numeric or generic.
        manifest_hits: dict[str, list[dict]] = defaultdict(list)
        for info in outer.infolist():
            if info.is_dir():
                continue
            name = info.filename.replace("\\", "/")
            if Path(name).suffix.lower() not in TEXT_EXTS:
                continue
            if "/manifests/" not in name and not name.endswith("COMBINED_SPRITE_INDEX.csv") and not name.endswith("LIBRARY_SUMMARY.json"):
                continue
            try:
                text = outer.read(info).decode("utf-8", errors="replace")
            except Exception:
                continue
            for lineno, line in enumerate(text.splitlines(), 1):
                hay = normalize(line)
                for t in targets:
                    if any(a in hay for a in aliases[t]):
                        if len(manifest_hits[t]) < 100:
                            manifest_hits[t].append({
                                "file": name,
                                "line": lineno,
                                "text": line[:800],
                            })

        for t in targets:
            rows = candidates.get(t, [])
            rows.sort(key=lambda x: (x["same_render_as_ready"], x["path"]))
            different = sum(1 for x in rows if not x["same_render_as_ready"])
            report["targets"][t] = {
                "ready": ready.get(t),
                "aliases": aliases[t],
                "candidate_count": len(rows),
                "different_render_candidate_count": different,
                "candidates": rows[:250],
            }
            report["manifest_hits"][t] = manifest_hits.get(t, [])

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary = {
        t: {
            "candidate_count": v["candidate_count"],
            "different_render_candidate_count": v["different_render_candidate_count"],
            "manifest_hits": len(report["manifest_hits"].get(t, [])),
        }
        for t, v in report["targets"].items()
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
