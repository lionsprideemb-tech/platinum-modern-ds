#!/usr/bin/env python3
"""Install the first curated community-move batch into native pokeplatinum.

Community moves use Mercury's locked 2048-2559 lane. IDs 920-2047 remain
reserved for future official moves, so this build materializes inert placeholders
for those IDs before appending the curated community records. The placeholders
are build-time resources only; they are not teachable and have no gameplay use.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

COMMUNITY_START = 2048
OFFICIAL_RESERVED_END = 2047


def write_move_dir(root: Path, stem: str, data: dict, anim_text: str) -> None:
    move_dir = root / "res" / "moves" / stem
    if move_dir.exists():
        raise SystemExit(f"move directory already exists: {move_dir}")
    move_dir.mkdir(parents=True)
    (move_dir / "data.json").write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (move_dir / "script.s").write_text(
        '#include "macros/btlcmd.inc"\n\n\n_000:\n    GoToEffectScript \n',
        encoding="utf-8",
    )
    (move_dir / "anim.s").write_text(anim_text, encoding="utf-8")


def reserved_data() -> dict:
    return {
        "name": "Reserved",
        "description": ["Reserved move slot."],
        "class": "CLASS_STATUS",
        "type": "TYPE_NORMAL",
        "power": 0,
        "accuracy": 0,
        "pp": 1,
        "effect": {"type": "BATTLE_EFFECT_DO_NOTHING", "chance": 0},
        "range": "RANGE_USER",
        "priority": 0,
        "flags": [],
        "contest": {
            "effect": "CONTEST_EFFECT_BASIC",
            "type": "CONTEST_TYPE_COOL",
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--batch",
        type=Path,
        default=Path("data/community_moves_cm01.json"),
    )
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("cm01-community-moves-install.json"),
    )
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    batch = json.loads(args.batch.read_text(encoding="utf-8"))
    records = sorted(batch["moves"], key=lambda x: x["id"])

    if not records:
        raise SystemExit("community batch is empty")
    for previous, record in zip(records, records[1:]):
        if record["id"] != previous["id"] + 1:
            raise SystemExit(
                f"community batch must be contiguous: {previous['id']} -> {record['id']}"
            )

    moves_txt = pt / "generated" / "moves.txt"
    registry = [x.strip() for x in moves_txt.read_text(encoding="utf-8").splitlines() if x.strip()]
    if not registry or registry[-1] != "MAX_MOVES":
        raise SystemExit("move registry does not end in MAX_MOVES")

    existing = registry[:-1]
    if len(existing) < 920 or existing[919] != "MOVE_MALIGNANT_CHAIN":
        raise SystemExit(
            "community imports require the certified PT05C1 namespace through canonical ID 919"
        )

    tokens = set(existing)
    reserved_tokens: list[str] = []
    noop_anim = '#include "macros/btlanimcmd.inc"\n\nL_0:\n    End\n'

    # The first community-import pass materializes the protected official-ID
    # lane once. Later batches append directly after already-installed community
    # moves, avoiding a rebuild of duplicate placeholders.
    if len(existing) == 920:
        for move_id in range(len(existing), COMMUNITY_START):
            token = f"MOVE_RESERVED_OFFICIAL_{move_id:04d}"
            if token in tokens:
                raise SystemExit(f"reserved token collision: {token}")
            stem = token.removeprefix("MOVE_").lower()
            write_move_dir(pt, stem, reserved_data(), noop_anim)
            existing.append(token)
            tokens.add(token)
            reserved_tokens.append(token)
    elif len(existing) < COMMUNITY_START:
        raise SystemExit(
            f"partial reserved lane detected: registry stops at {len(existing) - 1}"
        )

    expected_first_id = len(existing)
    if records[0]["id"] != expected_first_id:
        raise SystemExit(
            f"next community ID must be {expected_first_id}, got {records[0]['id']}"
        )
    if records[-1]["id"] > 2559:
        raise SystemExit("community batch exceeds the locked 2048-2559 lane")

    installed = []
    for record in records:
        token = record["token"]
        if token in tokens:
            raise SystemExit(f"community move token collision: {token}")
        if len(existing) != record["id"]:
            raise SystemExit(
                f"registry position mismatch for {token}: "
                f"expected {record['id']}, next index is {len(existing)}"
            )

        donor = record["animation"]
        if donor.get("mode") != "copy_native_platinum":
            raise SystemExit(f"{token}: unsupported animation mode {donor!r}")
        donor_stem = donor["donor_move"]
        donor_anim = pt / "res" / "moves" / donor_stem / "anim.s"
        if not donor_anim.is_file():
            raise SystemExit(f"{token}: missing native animation donor {donor_anim}")

        data = {
            "name": record["name"],
            "description": record["description"],
            "class": record["class"],
            "type": record["type"],
            "power": record["power"],
            "accuracy": record["accuracy"],
            "pp": record["pp"],
            "effect": record["effect"],
            "range": record["range"],
            "priority": record["priority"],
            "flags": record["flags"],
            "contest": record["contest"],
        }

        stem = token.removeprefix("MOVE_").lower()
        write_move_dir(pt, stem, data, donor_anim.read_text(encoding="utf-8"))
        existing.append(token)
        tokens.add(token)
        installed.append(
            {
                "id": record["id"],
                "token": token,
                "name": record["name"],
                "effect": record["effect"],
                "animation_donor": donor_stem,
                "traits": record.get("traits", []),
                "provenance": record.get("provenance"),
            }
        )

    moves_txt.write_text("\n".join(existing + ["MAX_MOVES", ""]), encoding="utf-8")

    report = {
        "gate": "CM01_NATIVE_PLATINUM_COMMUNITY_MOVE_IMPORT",
        "runtime": "pokeplatinum",
        "official_canonical_end": 919,
        "reserved_official_materialized": [920, OFFICIAL_RESERVED_END],
        "reserved_placeholder_count_added_this_pass": len(reserved_tokens),
        "community_lane": [2048, 2559],
        "community_moves_installed_this_pass": len(installed),
        "first_community_id_this_pass": installed[0]["id"],
        "last_community_id_this_pass": installed[-1]["id"],
        "total_materialized_move_count": len(existing),
        "total_community_moves_materialized": max(0, len(existing) - COMMUNITY_START),
        "moves": installed,
        "policy": (
            "reserved 920-2047 entries are inert build-time placeholders; "
            "community moves begin at the locked ID 2048 lane"
        ),
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
