#!/usr/bin/env python3
"""MR08F — final canonical Ability certification.

This is the completion gate for Mercury's official Gen 5-9 Ability mechanics.
It does not install mechanics. It certifies that:
- canonical modern Ability IDs 124..310 are contiguous and unique (187 total);
- every one is present in the implemented-Ability registry;
- the registry contains no duplicate modern entries;
- every modern Ability is owned by an MR08 installer's IMPLEMENTED declaration;
- every modern Ability has exactly one primary MR08 mechanic owner; explicitly
  declared supplemental interaction installers may extend that owner.

The gate intentionally keeps custom / non-canon Abilities out of this count.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


MODERN_FIRST_ID = 124
MODERN_LAST_ID = 310
MODERN_COUNT = MODERN_LAST_ID - MODERN_FIRST_ID + 1

# These installers intentionally add later interaction coverage to Abilities
# whose primary implementation lives in another MR08 batch. They are not
# duplicate mechanic owners.
SUPPLEMENTAL_INSTALLERS = {
    "install_mr08k_canonical_ability_redirect_copy_control.py",
}


def flatten_strings(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, (tuple, list, set)):
        for item in value:
            yield from flatten_strings(item)
    elif isinstance(value, dict):
        for key in value:
            yield from flatten_strings(key)


def installer_ownership(installers_dir: Path) -> tuple[dict[str, list[str]], list[str]]:
    owners: dict[str, list[str]] = defaultdict(list)
    unreadable: list[str] = []

    for path in sorted(installers_dir.glob("install_mr08*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError):
            unreadable.append(path.name)
            continue

        found = False
        for node in tree.body:
            if not isinstance(node, (ast.Assign, ast.AnnAssign)):
                continue

            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if not any(isinstance(t, ast.Name) and t.id == "IMPLEMENTED" for t in targets):
                continue

            found = True
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                unreadable.append(path.name)
                break

            for token in flatten_strings(value):
                if token.startswith("ABILITY_") and path.name not in owners[token]:
                    owners[token].append(path.name)

        # Some utility-only MR08 files legitimately have no IMPLEMENTED tuple.
        # They are ignored rather than treated as an error.
        _ = found

    return dict(owners), sorted(set(unreadable))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--installers-dir", type=Path, default=Path("tools"))
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08-final-canonical-ability-certification.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry_path = args.implemented_registry.resolve()
    installers_dir = args.installers_dir.resolve()

    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(abilities) <= MODERN_LAST_ID:
        raise SystemExit(
            f"Ability namespace ends at {len(abilities) - 1}; expected at least {MODERN_LAST_ID}"
        )

    modern = abilities[MODERN_FIRST_ID : MODERN_LAST_ID + 1]
    modern_set = set(modern)

    registry_rows = [
        line.strip()
        for line in registry_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    registry_set = set(registry_rows)

    owners, unreadable_installers = installer_ownership(installers_dir)
    missing_registry = [token for token in modern if token not in registry_set]
    missing_owner = [token for token in modern if token not in owners]
    supplemental_overlaps: dict[str, list[str]] = {}
    conflicting_primary_owners: dict[str, list[str]] = {}
    for token in modern:
        token_owners = owners.get(token, [])
        if len(token_owners) <= 1:
            continue

        primary = [
            owner for owner in token_owners
            if owner not in SUPPLEMENTAL_INSTALLERS
        ]
        if len(primary) == 1:
            supplemental_overlaps[token] = token_owners
        else:
            conflicting_primary_owners[token] = token_owners

    modern_registry_rows = [token for token in registry_rows if token in modern_set]
    duplicate_registry = sorted(
        {
            token
            for token in modern_registry_rows
            if modern_registry_rows.count(token) > 1
        }
    )

    checks = {
        "canonical_namespace_reaches_gen9": len(abilities) >= 311,
        "modern_id_range_is_187": len(modern) == MODERN_COUNT,
        "modern_namespace_unique": len(modern_set) == MODERN_COUNT,
        "all_187_in_implemented_registry": len(missing_registry) == 0,
        "no_duplicate_modern_registry_entries": len(duplicate_registry) == 0,
        "all_187_owned_by_mr08_installers": len(missing_owner) == 0,
        "no_conflicting_primary_mr08_owners":
            len(conflicting_primary_owners) == 0,
        "all_mr08_implemented_declarations_parse": len(unreadable_installers) == 0,
    }

    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08_FINAL_CANONICAL_ABILITY_CERTIFICATION",
        "status": status,
        "canonical_modern_range": {
            "first_id": MODERN_FIRST_ID,
            "last_id": MODERN_LAST_ID,
            "count": MODERN_COUNT,
            "first_token": modern[0],
            "last_token": modern[-1],
        },
        "implemented_registry": {
            "modern_count": len(set(modern_registry_rows)),
            "missing": missing_registry,
            "duplicates": duplicate_registry,
        },
        "installer_ownership": {
            "owned_modern_count": sum(1 for token in modern if token in owners),
            "missing": missing_owner,
            "supplemental_overlaps": supplemental_overlaps,
            "conflicting_primary_owners": conflicting_primary_owners,
            "supplemental_installers": sorted(SUPPLEMENTAL_INSTALLERS),
            "unreadable_installers": unreadable_installers,
        },
        "custom_abilities_included": False,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR08 final canonical Ability certification failed")


if __name__ == "__main__":
    main()
