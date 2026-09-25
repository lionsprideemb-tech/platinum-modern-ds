#!/usr/bin/env python3
"""Fast, reusable preflight gate for Mercury Redux community moves.

This is deliberately cheaper than a full ROM build. It catches structural,
namespace, text-encoding, effect-registration, and animation-donor mistakes
before GitHub spends minutes compiling the entire game.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CANONICAL_TYPES = {
    "TYPE_NORMAL", "TYPE_FIRE", "TYPE_WATER", "TYPE_ELECTRIC", "TYPE_GRASS",
    "TYPE_ICE", "TYPE_FIGHTING", "TYPE_POISON", "TYPE_GROUND", "TYPE_FLYING",
    "TYPE_PSYCHIC", "TYPE_BUG", "TYPE_ROCK", "TYPE_GHOST", "TYPE_DRAGON",
    "TYPE_DARK", "TYPE_STEEL", "TYPE_FAIRY",
}
MOVE_CLASSES = {"CLASS_PHYSICAL", "CLASS_SPECIAL", "CLASS_STATUS"}
TOKEN_RE = re.compile(r"MOVE_[A-Z0-9_]+$")
COMMUNITY_MIN = 1024
COMMUNITY_MAX = 1599


class PreflightError(Exception):
    pass


def fail(message: str) -> None:
    raise PreflightError(message)


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path}: invalid JSON: {exc}")


def constants(path: Path) -> list[str]:
    if not path.is_file():
        fail(f"missing required Platinum file: {path}")
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def charmap_characters(path: Path) -> set[str]:
    if not path.is_file():
        fail(f"missing Platinum charmap: {path}")
    supported: set[str] = {"\n", "\r"}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.lstrip()
        if not line or line.startswith("//") or "=" not in line:
            continue
        _, rhs = line.split("=", 1)
        # Command tokens and escaped control codes are not literal display text.
        if rhs.startswith("{") or rhs.startswith(r"\x"):
            continue
        supported.update(rhs)
    return supported


def validate_text(label: str, value: str, supported: set[str]) -> None:
    bad = []
    for ch in value:
        if ch not in supported:
            bad.append(f"{ch!r} (U+{ord(ch):04X})")
    if bad:
        unique = list(dict.fromkeys(bad))
        fail(f"{label}: unsupported Platinum text character(s): {', '.join(unique)}")


def batch_number(path: Path) -> int:
    match = re.search(r"community_moves_cm(\d+)\.json$", path.name)
    if not match:
        fail(f"cannot determine community batch number from {path}")
    return int(match.group(1))


def validate_batch_shape(path: Path, payload: dict) -> list[dict]:
    moves = payload.get("moves")
    if not isinstance(moves, list) or not moves:
        fail(f"{path}: moves must be a non-empty list")

    ids = [m.get("id") for m in moves]
    if any(not isinstance(x, int) for x in ids):
        fail(f"{path}: every move requires an integer id")
    if ids != list(range(ids[0], ids[0] + len(ids))):
        fail(f"{path}: move IDs are not contiguous: {ids[0]}..{ids[-1]}")
    if payload.get("start_id") != ids[0]:
        fail(f"{path}: start_id {payload.get('start_id')} does not match first move ID {ids[0]}")
    if ids[0] < COMMUNITY_MIN or ids[-1] > COMMUNITY_MAX:
        fail(f"{path}: IDs {ids[0]}..{ids[-1]} leave community lane {COMMUNITY_MIN}..{COMMUNITY_MAX}")

    for move in moves:
        token = move.get("token", "")
        if not TOKEN_RE.fullmatch(token):
            fail(f"{path}: invalid move token {token!r}")
    return moves


def all_static_batches(root: Path) -> list[tuple[Path, dict, list[dict]]]:
    out = []
    for path in sorted((root / "data").glob("community_moves_cm*.json"), key=batch_number):
        payload = read_json(path)
        moves = validate_batch_shape(path, payload)
        out.append((path, payload, moves))
    if not out:
        fail("no static community move batches found")
    return out


def load_extensions(root: Path) -> list[dict]:
    path = root / "data" / "community_move_effect_extensions.json"
    payload = read_json(path)
    rows = payload.get("effects")
    if not isinstance(rows, list):
        fail(f"{path}: effects must be a list")

    ids: set[int] = set()
    names: set[str] = set()
    for row in rows:
        effect_id = row.get("id")
        name = row.get("name")
        installer = row.get("installer")
        if not isinstance(effect_id, int) or effect_id < 0:
            fail(f"{path}: invalid effect ID {effect_id!r}")
        if not isinstance(name, str) or not name.startswith("BATTLE_EFFECT_"):
            fail(f"{path}: invalid effect name {name!r}")
        if effect_id in ids:
            fail(f"{path}: duplicate custom effect ID {effect_id}")
        if name in names:
            fail(f"{path}: duplicate custom effect name {name}")
        ids.add(effect_id)
        names.add(name)

        installer_path = root / str(installer)
        if not installer_path.is_file():
            fail(f"{path}: installer does not exist for {name}: {installer}")
        installer_text = installer_path.read_text(encoding="utf-8")
        if name not in installer_text:
            fail(f"{path}: installer {installer} does not mention {name}")
    return rows


def current_batch(
    batches: list[tuple[Path, dict, list[dict]]],
    requested: Path | None,
) -> tuple[Path, dict, list[dict]]:
    if requested is None:
        return batches[-1]
    requested = requested.resolve()
    for entry in batches:
        if entry[0].resolve() == requested:
            return entry
    fail(f"requested batch is not part of the static community stack: {requested}")


def validate_global_namespace(
    batches: list[tuple[Path, dict, list[dict]]],
    supported: set[str],
) -> tuple[int, int]:
    ids: dict[int, str] = {}
    tokens: dict[str, str] = {}
    total = 0

    for path, _, moves in batches:
        for move in moves:
            total += 1
            move_id = move["id"]
            token = move["token"]
            if move_id in ids:
                fail(f"community ID collision {move_id}: {ids[move_id]} and {path}")
            if token in tokens:
                fail(f"community token collision {token}: {tokens[token]} and {path}")
            ids[move_id] = str(path)
            tokens[token] = str(path)

            name = move.get("name")
            if not isinstance(name, str) or not name:
                fail(f"{path}: {token} has no display name")
            validate_text(f"{path}:{token}:name", name, supported)

            desc = move.get("description")
            if not isinstance(desc, list) or not desc or not all(isinstance(x, str) for x in desc):
                fail(f"{path}: {token} description must be a non-empty list of strings")
            for i, line in enumerate(desc):
                validate_text(f"{path}:{token}:description[{i}]", line, supported)

    return total, len(ids)


def validate_move_metadata(
    path: Path,
    moves: list[dict],
    pt: Path,
    extension_names: set[str],
    installed: bool,
) -> None:
    ranges = set(constants(pt / "generated" / "move_ranges.txt"))
    live_effects = set(constants(pt / "generated" / "move_battle_effects.txt"))

    for move in moves:
        token = move["token"]
        move_type = move.get("type")
        move_class = move.get("class")
        move_range = move.get("range")
        effect = move.get("effect")

        if move_type not in CANONICAL_TYPES:
            fail(f"{path}: {token} uses non-canonical type {move_type!r}")
        if move_class not in MOVE_CLASSES:
            fail(f"{path}: {token} has invalid class {move_class!r}")
        if move_range not in ranges:
            fail(f"{path}: {token} has unknown Platinum range {move_range!r}")
        if not isinstance(effect, dict) or not isinstance(effect.get("type"), str):
            fail(f"{path}: {token} has invalid effect block")

        effect_name = effect["type"]
        allowed = live_effects if installed else (live_effects | extension_names)
        if effect_name not in allowed:
            stage = "installed Platinum effect registry" if installed else "native/custom extension registry"
            fail(f"{path}: {token} effect {effect_name} is absent from {stage}")

        for field in ("power", "accuracy", "pp", "priority"):
            if not isinstance(move.get(field), int):
                fail(f"{path}: {token} field {field} must be an integer")
        if move["pp"] <= 0:
            fail(f"{path}: {token} must have positive PP")
        chance = effect.get("chance")
        if not isinstance(chance, int) or not 0 <= chance <= 100:
            fail(f"{path}: {token} has invalid effect chance {chance!r}")

        animation = move.get("animation")
        if not isinstance(animation, dict) or animation.get("mode") != "copy_native_platinum":
            fail(f"{path}: {token} must use a declared copy_native_platinum animation donor")
        donor = animation.get("donor_move")
        if not isinstance(donor, str) or not donor:
            fail(f"{path}: {token} has no animation donor")


def validate_installed_batch(path: Path, moves: list[dict], pt: Path) -> None:
    registry = constants(pt / "generated" / "moves.txt")
    if registry[-1] != "MAX_MOVES":
        fail("installed move registry no longer ends in MAX_MOVES")

    for move in moves:
        move_id = move["id"]
        token = move["token"]
        if move_id >= len(registry) or registry[move_id] != token:
            got = registry[move_id] if move_id < len(registry) else "<out of range>"
            fail(f"{path}: registry mismatch at ID {move_id}: expected {token}, got {got}")

        stem = token.removeprefix("MOVE_").lower()
        move_dir = pt / "res" / "moves" / stem
        data_path = move_dir / "data.json"
        anim_path = move_dir / "anim.s"
        if not data_path.is_file() or not anim_path.is_file():
            fail(f"{path}: installed resources missing for {token}")

        actual = read_json(data_path)
        expected_fields = {
            "name": move["name"],
            "description": move["description"],
            "class": move["class"],
            "type": move["type"],
            "power": move["power"],
            "accuracy": move["accuracy"],
            "pp": move["pp"],
            "effect": move["effect"],
            "range": move["range"],
            "priority": move["priority"],
            "flags": move["flags"],
            "contest": move["contest"],
        }
        for key, expected in expected_fields.items():
            if actual.get(key) != expected:
                fail(f"{path}: installed {token} field {key} differs from batch metadata")

        donor = move["animation"]["donor_move"]
        donor_anim = pt / "res" / "moves" / donor / "anim.s"
        if not donor_anim.is_file():
            fail(f"{path}: {token} animation donor is missing: {donor_anim}")
        if anim_path.read_bytes() != donor_anim.read_bytes():
            fail(f"{path}: {token} animation does not match donor {donor}")

    expected_max = moves[-1]["id"] + 1
    if expected_max >= len(registry) or registry[expected_max] != "MAX_MOVES":
        fail(f"{path}: expected MAX_MOVES immediately after ID {moves[-1]['id']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("mercury_root", type=Path)
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--batch", type=Path)
    ap.add_argument("--installed", action="store_true")
    ap.add_argument("--report", type=Path, default=Path("mercury-move-preflight.json"))
    args = ap.parse_args()

    root = args.mercury_root.resolve()
    pt = args.pokeplatinum_root.resolve()

    try:
        supported = charmap_characters(pt / "tools" / "msgenc" / "charmap.txt")
        batches = all_static_batches(root)
        extensions = load_extensions(root)
        extension_names = {row["name"] for row in extensions}

        total_static, unique_ids = validate_global_namespace(batches, supported)
        batch_path, batch_payload, moves = current_batch(batches, args.batch)
        validate_move_metadata(batch_path, moves, pt, extension_names, args.installed)

        native_effect_count = len(constants(pt / "generated" / "move_battle_effects.txt"))
        if not args.installed:
            extension_ids = sorted(row["id"] for row in extensions)
            if extension_ids:
                expected = list(range(native_effect_count, native_effect_count + len(extension_ids)))
                if extension_ids != expected:
                    fail(
                        "custom effect IDs must append contiguously after native Platinum: "
                        f"expected {expected}, got {extension_ids}"
                    )
        else:
            live_effects = constants(pt / "generated" / "move_battle_effects.txt")
            for row in extensions:
                effect_id = row["id"]
                if effect_id >= len(live_effects) or live_effects[effect_id] != row["name"]:
                    fail(
                        f"installed custom effect mismatch at {effect_id}: "
                        f"expected {row['name']}"
                    )
            validate_installed_batch(batch_path, moves, pt)

        report = {
            "gate": "MERCURY_MOVE_PREFLIGHT",
            "stage": "installed" if args.installed else "metadata",
            "batch": batch_payload.get("batch", batch_path.stem),
            "batch_file": str(batch_path.relative_to(root)),
            "batch_move_count": len(moves),
            "batch_id_range": [moves[0]["id"], moves[-1]["id"]],
            "static_batches_checked": len(batches),
            "static_moves_checked": total_static,
            "unique_static_ids": unique_ids,
            "custom_effect_extensions": len(extensions),
            "platinum_charmap_characters_checked": True,
            "canonical_type_gate": True,
            "namespace_gate": True,
            "effect_gate": True,
            "animation_gate": bool(args.installed),
            "installed_resource_gate": bool(args.installed),
            "result": "PASS",
        }
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0

    except PreflightError as exc:
        report = {
            "gate": "MERCURY_MOVE_PREFLIGHT",
            "stage": "installed" if args.installed else "metadata",
            "result": "FAIL",
            "error": str(exc),
        }
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
