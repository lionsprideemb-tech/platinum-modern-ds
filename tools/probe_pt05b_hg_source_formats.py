#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROBES = [
    "SPECIES_VICTINI",
    "SPECIES_SNIVY",
    "SPECIES_GENESECT",
    "Victini",
    "Snivy",
    "Genesect",
    "victini",
    "snivy",
    "genesect",
]

FILES = {
    "species_data": "data/Species.c",
    "learnsets": "data/learnsets/learnsets.json",
    "sprite_offsets": "data/SpriteOffsets.c",
}


def context(text: str, needle: str, radius: int = 1000) -> str | None:
    pos = text.find(needle)
    if pos < 0:
        return None
    start = max(0, pos - radius)
    end = min(len(text), pos + len(needle) + radius)
    return text[start:end]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("hg_engine_root", type=Path)
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("pt05b-hg-source-format-probe.json"),
    )
    args = parser.parse_args()

    root = args.hg_engine_root.resolve()
    report = {
        "gate": "PT05B_HG_SOURCE_FORMAT_PROBE",
        "files": {},
    }

    for label, rel in FILES.items():
        path = root / rel
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing donor source: {path}")

        text = path.read_text(errors="replace")
        matches = {}
        for needle in PROBES:
            hit = context(text, needle)
            if hit is not None:
                matches[needle] = hit

        report["files"][label] = {
            "path": rel,
            "bytes": path.stat().st_size,
            "line_count": text.count("\n") + 1,
            "head": "\n".join(text.splitlines()[:40]),
            "matches": matches,
        }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "gate": report["gate"],
        "summary": {
            label: {
                "bytes": data["bytes"],
                "line_count": data["line_count"],
                "matched_probe_terms": list(data["matches"]),
            }
            for label, data in report["files"].items()
        },
    }, indent=2))


if __name__ == "__main__":
    main()
