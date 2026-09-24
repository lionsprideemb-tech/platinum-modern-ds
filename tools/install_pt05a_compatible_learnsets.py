#!/usr/bin/env python3
"""Install compatible modern level-up and egg learnsets into Mercury DS.

This is a production build step, not a runtime QA harness.

The PT04 bulk species importer intentionally gave post-Gen-IV species a
Tackle-only compatibility learnset while the 1025-species architecture was
being proven. This tool replaces that placeholder data in bulk using the
pinned HG-Engine learnset source while filtering out moves that the current
Platinum move table does not yet implement.

Unsupported modern moves are reported, never silently substituted.
TM/HM compatibility is intentionally left for the dedicated machine-move
import pass because Platinum stores TM compatibility by machine ID rather
than move name.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_registry(path: Path) -> list[str]:
    rows = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        rows.append(line)
    if len(rows) < 1025:
        raise SystemExit(f"registry is too short: {len(rows)} entries")
    return rows


def load_constants(path: Path) -> set[str]:
    return {
        line.strip()
        for line in path.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }


def species_dir(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def dedupe_pairs(rows: list[list[object]]) -> list[list[object]]:
    seen = set()
    out = []
    for level, move in rows:
        key = (int(level), str(move))
        if key in seen:
            continue
        seen.add(key)
        out.append([int(level), str(move)])
    return out


def dedupe_strings(rows: list[str]) -> list[str]:
    seen = set()
    out = []
    for row in rows:
        if row in seen:
            continue
        seen.add(row)
        out.append(row)
    return out


def cap_level_learnset(rows: list[list[object]], limit: int = 20) -> tuple[list[list[object]], int]:
    """Fit a modern learnset into Platinum's fixed 20-entry level-up table.

    Keep the first and last moves, then sample the middle evenly so the
    resulting progression still spans the species' full level curve.
    """
    if len(rows) <= limit:
        return rows, 0
    if limit < 2:
        return rows[:limit], len(rows) - limit

    keep = {0, len(rows) - 1}
    slots = limit - 2
    if slots:
        for i in range(1, slots + 1):
            idx = round(i * (len(rows) - 1) / (slots + 1))
            keep.add(idx)

    # Rounding can collide on very small ranges; fill from the front if needed.
    if len(keep) < limit:
        for idx in range(len(rows)):
            keep.add(idx)
            if len(keep) == limit:
                break

    selected = [row for idx, row in enumerate(rows) if idx in sorted(keep)][:limit]
    return selected, len(rows) - len(selected)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--start-dex", type=int, default=494)
    ap.add_argument("--end-dex", type=int, default=1025)
    ap.add_argument("--report", type=Path, default=Path("pt05a-compatible-learnsets.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)

    available_moves = load_constants(pt / "generated/moves.txt")
    donor_path = hg / "data/learnsets/learnsets.json"
    if not donor_path.is_file():
        donor_path = hg / "data/learnsets/base/21_sv.json"
    donor = json.loads(donor_path.read_text())

    imported = []
    missing_donor = []
    fallback_tackle = []
    unsupported_by_species = {}
    total_supported_level = 0
    total_unsupported_level = 0
    total_supported_egg = 0
    total_supported_tutor = 0

    for dex in range(args.start_dex, args.end_dex + 1):
        species_const = registry[dex - 1]
        path = pt / "res/pokemon" / species_dir(species_const) / "data.json"
        if not path.is_file():
            raise SystemExit(f"missing target species data: {path}")

        source = donor.get(species_const)
        if not source:
            missing_donor.append({"dex": dex, "species": species_const})
            continue

        data = json.loads(path.read_text())
        learnset = data.setdefault("learnset", {})

        supported_level = []
        unsupported = []
        for row in source.get("LevelMoves", []) or []:
            move = row.get("Move")
            level = int(row.get("Level", 1))
            if move in available_moves:
                # Level 0 in modern data means "on evolution". Until the
                # dedicated evolution-move mechanic pass, expose it at Lv1.
                supported_level.append([max(1, level), move])
            else:
                unsupported.append(move)

        supported_level = dedupe_pairs(supported_level)
        if not supported_level:
            supported_level = [[1, "MOVE_TACKLE"]]
            fallback_tackle.append({"dex": dex, "species": species_const})

        supported_level, trimmed = cap_level_learnset(supported_level, 20)
        if trimmed:
            trimmed_by_species[species_const] = trimmed
            total_trimmed_level += trimmed

        egg = dedupe_strings([
            move for move in (source.get("EggMoves", []) or [])
            if move in available_moves
        ])

        learnset["by_level"] = supported_level
        # Keep TM/HM and tutor compatibility empty until their dedicated
        # importers translate modern move names into Platinum's actual tables.
        learnset["by_tm"] = []
        learnset["by_tutor"] = []
        learnset["egg_moves"] = egg

        path.write_text(json.dumps(data, indent=4, ensure_ascii=False) + "\n")

        total_supported_level += len(supported_level)
        total_unsupported_level += len(unsupported)
        total_supported_egg += len(egg)
        total_supported_tutor += 0
        if unsupported:
            unsupported_by_species[species_const] = sorted(set(unsupported))

        imported.append({
            "dex": dex,
            "species": species_const,
            "level_moves": len(supported_level),
            "egg_moves": len(egg),
            "tutor_moves": 0,
            "unsupported_level_moves": len(set(unsupported)),
        })

    report = {
        "gate": "PT05A_COMPATIBLE_MODERN_LEARNSETS",
        "range": [args.start_dex, args.end_dex],
        "donor_source": str(donor_path),
        "species_requested": args.end_dex - args.start_dex + 1,
        "species_imported": len(imported),
        "species_missing_donor": missing_donor,
        "species_using_tackle_fallback": fallback_tackle,
        "totals": {
            "supported_level_moves": total_supported_level,
            "unsupported_level_moves": total_unsupported_level,
            "supported_egg_moves": total_supported_egg,
            "supported_tutor_moves": total_supported_tutor,
            "trimmed_level_moves_to_fit_platinum_limit": total_trimmed_level,
        },
        "unsupported_level_moves_by_species": unsupported_by_species,
        "trimmed_level_moves_by_species": trimmed_by_species,
        "species": imported,
        "deferred": {
            "tm_hm_compatibility": "separate machine-ID import pass",
            "tutor_compatibility": "separate Platinum tutor-table import pass",
            "unsupported_modern_moves": "requires PT05 move-table expansion",
            "evolution_methods": "next build-forward pass",
        },
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")

    if len(imported) < 500:
        raise SystemExit(
            f"learnset donor coverage unexpectedly low: {len(imported)} / "
            f"{report['species_requested']}"
        )

    print(json.dumps({
        "gate": report["gate"],
        "species_imported": len(imported),
        "fallback_tackle": len(fallback_tackle),
        "supported_level_moves": total_supported_level,
        "unsupported_level_moves": total_unsupported_level,
    }, indent=2))


if __name__ == "__main__":
    main()
