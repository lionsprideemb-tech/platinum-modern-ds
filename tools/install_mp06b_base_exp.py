#!/usr/bin/env python3
"""MP06B: preserve full modern base EXP values through the Platinum species layer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_pt04d_species_batch import load_registry, parse_base_exp


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one {label} match, found {count}")
    path.write_text(text.replace(old, new, 1))


def dirname(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--start-dex", type=int, default=494)
    ap.add_argument("--end-dex", type=int, default=1025)
    ap.add_argument("--report", type=Path, default=Path("mp06b-base-exp.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    donor = parse_base_exp(hg / "data/BaseExperienceTable.c")

    replace_once(
        pt / "include/struct_defs/species.h",
        "    u8 baseExpReward;\n",
        "    u16 baseExpReward;\n",
        "SpeciesData base EXP width",
    )
    replace_once(
        pt / "tools/dataproc/src/speciesproc.c",
        '        .baseExpReward  = u8(".base_exp_reward"),\n',
        '        .baseExpReward  = u16(".base_exp_reward"),\n',
        "speciesproc base EXP parser",
    )

    changed = []
    missing = []
    over_255 = []

    for dex in range(args.start_dex, args.end_dex + 1):
        species = registry[dex - 1]
        value = donor.get(species)
        if value is None:
            missing.append({"dex": dex, "species": species})
            continue

        data_path = pt / "res/pokemon" / dirname(species) / "data.json"
        if not data_path.is_file():
            raise SystemExit(f"{species}: missing generated data file {data_path}")

        data = json.loads(data_path.read_text(encoding="utf-8"))
        old = int(data["base_exp_reward"])
        data["base_exp_reward"] = int(value)
        data_path.write_text(
            json.dumps(data, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        changed.append({"dex": dex, "species": species, "old": old, "modern": value})
        if value > 255:
            over_255.append({"dex": dex, "species": species, "modern": value})

    if missing:
        raise SystemExit(f"missing donor base EXP for {len(missing)} species: {missing[:10]}")

    report = {
        "gate": "MP06B_FULL_MODERN_BASE_EXP",
        "dex_range": [args.start_dex, args.end_dex],
        "species_updated": len(changed),
        "values_over_255_preserved": len(over_255),
        "max_base_exp": max(x["modern"] for x in changed),
        "storage": "u16",
        "missing": missing,
        "over_255": over_255,
        "result": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
