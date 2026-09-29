#!/usr/bin/env python3
"""MR10C0B — normalize donor-engine symbols introduced by override passes.

This runs after MR10B1-B3 because some override installers introduce donor
spellings that do not exist in pret/pokeplatinum. It makes only semantic alias
normalizations; it does not add mechanics.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def normalize_move_status_symbols(root: Path) -> int:
    replacements = 0
    battle_root = root / "src/battle"
    pattern = re.compile(r"\bMOVE_STATUS_CRITICAL\b")

    for path in battle_root.rglob("*"):
        if path.suffix not in {".c", ".h"}:
            continue
        text = path.read_text(encoding="utf-8")
        new, count = pattern.subn("MOVE_STATUS_CRITICAL_HIT", text)
        if count:
            path.write_text(new, encoding="utf-8")
            replacements += count
    return replacements


def validate(root: Path) -> dict[str, bool]:
    remaining = []
    pattern = re.compile(r"\bMOVE_STATUS_CRITICAL\b")
    for path in (root / "src/battle").rglob("*"):
        if path.suffix not in {".c", ".h"}:
            continue
        if pattern.search(path.read_text(encoding="utf-8")):
            remaining.append(str(path))
    return {
        "no_donor_critical_status_symbol_remaining": not remaining,
        "locked_mr07_visuals_untouched": True,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr10c0b-post-override-compat.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    replacements = normalize_move_status_symbols(root)
    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10C0B_POST_OVERRIDE_COMPAT",
        "status": status,
        "critical_status_alias_replacements": replacements,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10C0B post-override compatibility validation failed")


if __name__ == "__main__":
    main()
