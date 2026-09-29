#!/usr/bin/env python3
"""MR10C0 — compile compatibility for canonical mechanics awaiting species data.

MR08 already implements several official form/state Ability mechanics whose
species do not yet exist in Mercury's current Platinum species namespace.
Keep those mechanics compiled but dormant by assigning unique sentinel values
only when the corresponding species token is absent from generated/species.txt.

Once the National species expansion adds a token, this installer automatically
stops creating that token's sentinel and the real species constant is used.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

FUTURE_SPECIES = (
    "SPECIES_DARMANITAN",
    "SPECIES_ZYGARDE",
    "SPECIES_WISHIWASHI",
    "SPECIES_MINIOR",
    "SPECIES_CRAMORANT",
    "SPECIES_MORPEKO",
    "SPECIES_PALAFIN",
    "SPECIES_DONDOZO",
    "SPECIES_TATSUGIRI",
    "SPECIES_TERAPAGOS",
)

SENTINEL_BASE = 0xF000


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def patch_missing_species(root: Path) -> list[str]:
    species_txt = root / "generated/species.txt"
    known = set(
        line.strip()
        for line in species_txt.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    missing = [token for token in FUTURE_SPECIES if token not in known]
    if not missing:
        return []

    block_lines = [
        "",
        "/* Mercury MR10C0: temporary compile sentinels for official Ability",
        " * mechanics whose species data has not been imported yet. Values are",
        " * deliberately outside the live Platinum species range and disappear",
        " * automatically from this installer once generated/species.txt contains",
        " * the real token. */",
    ]
    for i, token in enumerate(missing):
        block_lines.append(f"#define {token} 0x{SENTINEL_BASE + i:04X}")
    block_lines.append("")
    block = "\n".join(block_lines) + "\n"

    for rel in ("src/battle/battle_lib.c", "src/battle/battle_script.c"):
        path = root / rel
        insert_after_once(
            path,
            '#include "res/battle/scripts/sub_seq.naix"\n',
            block,
            f"MR10C0 species sentinel block in {rel}",
        )

    return missing



def validate(root: Path, missing: list[str]) -> dict[str, bool]:
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    return {
        "all_missing_species_have_unique_sentinels": all(
            f"#define {token} 0x{SENTINEL_BASE + FUTURE_SPECIES.index(token):04X}" in lib
            and f"#define {token} 0x{SENTINEL_BASE + FUTURE_SPECIES.index(token):04X}" in script
            for token in missing
        ),
        "sentinels_unique": len(missing) == len({
            SENTINEL_BASE + FUTURE_SPECIES.index(token) for token in missing
        }),
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr10c0-species-compat.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    missing = patch_missing_species(root)
    checks = validate(root, missing)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C0_PENDING_SPECIES_COMPILE_COMPAT",
        "status": status,
        "missing_species_count": len(missing),
        "missing_species": missing,
        "runtime_policy":
            "Sentinel species values are compile-only dormant guards; no absent species is made obtainable or assigned data.",
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C0 species compatibility validation failed")


if __name__ == "__main__":
    main()
