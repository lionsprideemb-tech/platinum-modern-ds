#!/usr/bin/env python3
"""Fast inventory of the staged DS01 community sprite archive."""

from __future__ import annotations

import argparse
import json
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    top = Counter()
    depth2 = Counter()
    depth3 = Counter()
    exts = Counter()
    files_by_top: dict[str, list[str]] = defaultdict(list)
    nested = []
    total_uncompressed = 0
    total_compressed = 0

    with zipfile.ZipFile(args.archive) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        for info in infos:
            name = info.filename.replace("\\", "/")
            parts = [p for p in name.split("/") if p]
            bucket = parts[0] if parts else "(root)"
            ext = Path(name).suffix.lower() or "(none)"
            top[bucket] += 1
            if len(parts) >= 2:
                depth2["/".join(parts[:2])] += 1
            if len(parts) >= 3:
                depth3["/".join(parts[:3])] += 1
            exts[ext] += 1
            total_uncompressed += info.file_size
            total_compressed += info.compress_size
            if len(files_by_top[bucket]) < 80:
                files_by_top[bucket].append(name)
            if ext == ".zip":
                nested.append({
                    "path": name,
                    "compressed_size": info.compress_size,
                    "uncompressed_size": info.file_size,
                })

    report = {
        "archive": str(args.archive),
        "file_count": sum(top.values()),
        "total_uncompressed_bytes": total_uncompressed,
        "total_compressed_bytes": total_compressed,
        "top_level_counts": dict(top.most_common()),
        "depth2_counts": dict(depth2.most_common()),
        "depth3_counts": dict(depth3.most_common()),
        "extension_counts": dict(exts.most_common()),
        "nested_zip_count": len(nested),
        "nested_zips": nested,
        "sample_paths_by_top_level": dict(files_by_top),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
