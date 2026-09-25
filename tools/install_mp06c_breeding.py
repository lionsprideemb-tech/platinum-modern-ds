#!/usr/bin/env python3
"""MP06C: import canonical breeding offspring/baby-species mappings."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from audit_pt04d_species_batch import load_registry


BABY_RE = re.compile(
    r"^\s*\[(SPECIES_[A-Z0-9_]+)\]\s*=\s*(SPECIES_[A-Z0-9_]+)\s*,\s*$",
    re.M,
)


def dirname(species_const: str) -> str:
    return species_const.removeprefix("SPECIES_").lower()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--registry", type=Path, default=Path("data/canonical_species_1025.txt"))
    ap.add_argument("--start-dex", type=int, default=494)
    ap.add_argument("--end-dex", type=int, default=1025)
    ap.add_argument("--report", type=Path, default=Path("mp06c-breeding.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    hg = args.hg_engine_root.resolve()
    registry = load_registry(args.registry)
    canonical = set(registry)

    baby_text = (hg / "data/BabyMons.c").read_text(encoding="utf-8")
    baby_map = dict(BABY_RE.findall(baby_text))

    updated = []
    missing = []
    noncanonical_targets = []

    for dex in range(args.start_dex, args.end_dex + 1):
        species = registry[dex - 1]
        baby = baby_map.get(species)
        if baby is None:
            missing.append({"dex": dex, "species": species})
            continue
        if baby not in canonical:
            noncanonical_targets.append(
                {"dex": dex, "species": species, "donor_offspring": baby}
            )
            continue

        path = pt / "res/pokemon" / dirname(species) / "data.json"
        if not path.is_file():
            raise SystemExit(f"{species}: missing generated data file {path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        old = data.get("offspring")
        data["offspring"] = baby
        path.write_text(
            json.dumps(data, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        updated.append(
            {
                "dex": dex,
                "species": species,
                "old": old,
                "offspring": baby,
                "changed_from_self": baby != species,
            }
        )

    if missing:
        raise SystemExit(f"missing baby mapping for {len(missing)} species: {missing[:10]}")
    if noncanonical_targets:
        raise SystemExit(
            "noncanonical offspring targets in base-species pass: "
            + str(noncanonical_targets[:10])
        )

    report = {
        "gate": "MP06C_CANONICAL_BREEDING_OFFSPRING",
        "dex_range": [args.start_dex, args.end_dex],
        "species_updated": len(updated),
        "evolved_species_redirected_to_baby": sum(
            1 for x in updated if x["changed_from_self"]
        ),
        "missing": missing,
        "noncanonical_targets": noncanonical_targets,
        "result": "PASS",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
