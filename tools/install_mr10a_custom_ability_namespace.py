#!/usr/bin/env python3
"""MR10A — install the complete Mercury custom Ability namespace.

This pass only materializes stable IDs/text for non-canonical identities.
Canonical names keep official IDs 0..310. Mechanics are installed by later
MR10 runtime batches; this script never marks an Ability implemented by itself.
"""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from pathlib import Path

CANONICAL_MAX = 310
CUSTOM_FIRST = 311
SAVE_CAPACITY = 1023


def read_bank(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_bank(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


DS_TEXT_REPLACEMENTS = str.maketrans({
    # These generated Ability banks are fed through pokeplatinum msgenc.
    # Keep their punctuation conservative: current native builds reject
    # apostrophe/quote glyphs in the JSON message payload even when a related
    # glyph appears in the charmap. Exact source prose stays in the partition.
    "'": "",
    '"': "",
    "\u2018": "",
    "\u2019": "",
    "\u201c": "",
    "\u201d": "",
    "\u2013": "-",
    "\u2014": "-",
    "\u2026": "...",
    "\u00a0": " ",
    "\u00d7": "x",
}


def ds_text(text: str) -> str:
    """Normalize prose to characters present in Platinum's message charmap."""
    text = text.translate(DS_TEXT_REPLACEMENTS)
    # Platinum has no ASCII/Unicode greater-than glyph in its English charmap.
    # This only affects the custom Ability name "3 > 1"; preserve the meaning
    # rather than substituting an unrelated symbol.
    text = text.replace("3 > 1", "3 Beats 1")
    return text


def sanitize_tree(value):
    if isinstance(value, str):
        return ds_text(value)
    if isinstance(value, list):
        return [sanitize_tree(x) for x in value]
    if isinstance(value, dict):
        return {k: sanitize_tree(v) for k, v in value.items()}
    return value


def load_supported_chars(root: Path) -> set[str]:
    supported: set[str] = set()
    path = root / "tools/msgenc/charmap.txt"
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip("\n")
        if not line or line.lstrip().startswith("//") or "=" not in line:
            continue
        value = line.split("=", 1)[1]
        if len(value) == 1:
            supported.add(value)
    return supported


def bank_uses_only_supported_chars(bank: dict, supported: set[str]) -> bool:
    def valid(value) -> bool:
        if isinstance(value, str):
            return all(ch in supported or ch in "\n\r\t" for ch in value)
        if isinstance(value, list):
            return all(valid(x) for x in value)
        if isinstance(value, dict):
            return all(valid(v) for k, v in value.items() if k != "id")
        return True

    return all(valid(message.get("en_US")) for message in bank["messages"])


def short_description(effect: str) -> list[str]:
    clean = re.sub(r"\s+", " ", ds_text(effect).strip())
    # Prefer the first complete sentence/major clause for the two-line Summary
    # view. The full exact wording remains in mr10_safe_ability_partition.json.
    first = re.split(r"(?<=[.!?])\s+", clean, maxsplit=1)[0]
    lines = textwrap.wrap(first, width=31, break_long_words=False, break_on_hyphens=False)
    if len(lines) > 2:
        lines = lines[:2]
        if len(lines[1]) > 28:
            lines[1] = lines[1][:28].rstrip()
        lines[1] = lines[1].rstrip(" .") + "..."
    if not lines:
        lines = ["Custom Ability."]
    return [line + ("\n" if i < len(lines) - 1 else "") for i, line in enumerate(lines)]


def ensure_message(bank: dict, prefix: str, idx: int, value) -> None:
    msg_id = f"{prefix}_{idx:05d}"
    for message in bank["messages"]:
        if message["id"] == msg_id:
            message["en_US"] = value
            return
    bank["messages"].append({"id": msg_id, "en_US": value})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_safe_ability_partition.json"))
    ap.add_argument("--report", type=Path, default=Path("mr10a-custom-ability-namespace.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    plan = json.loads(args.partition.read_text(encoding="utf-8"))
    custom = sorted(
        (x for x in plan["abilities"] if x["runtime_kind"] == "custom_id"),
        key=lambda x: x["id"],
    )

    expected = list(range(CUSTOM_FIRST, custom[-1]["id"] + 1))
    actual = [x["id"] for x in custom]
    if actual != expected:
        raise SystemExit(f"custom Ability IDs must be contiguous; expected {expected[:3]}..{expected[-3:]}, got gap")
    if custom[-1]["id"] > SAVE_CAPACITY:
        raise SystemExit(f"custom Ability tail {custom[-1]['id']} exceeds 10-bit save capacity {SAVE_CAPACITY}")

    ability_path = root / "generated/abilities.txt"
    abilities = [x.strip() for x in ability_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(abilities) < CANONICAL_MAX + 1:
        raise SystemExit(f"canonical Ability namespace is short: {len(abilities)}")
    abilities = abilities[: CANONICAL_MAX + 1]

    tokens = [x["token"] for x in custom]
    if len(tokens) != len(set(tokens)):
        raise SystemExit("custom Ability token collision")
    abilities.extend(tokens)
    ability_path.write_text("\n".join(abilities) + "\n", encoding="utf-8")

    names = read_bank(root / "res/text/ability_names.json")
    uppercase = read_bank(root / "res/text/ability_names_uppercase.json")
    descriptions = read_bank(root / "res/text/ability_descriptions.json")

    # Strip any experimental custom tail so reruns are deterministic.
    for bank in (names, uppercase, descriptions):
        bank["messages"] = bank["messages"][: CANONICAL_MAX + 1]

    for entry in custom:
        idx = entry["id"]
        name = ds_text(entry["display_name"])
        ensure_message(names, "pl_msg_00000610", idx, name)
        ensure_message(uppercase, "pl_msg_00000611", idx, name.upper())
        ensure_message(
            descriptions,
            "pl_msg_00000612",
            idx,
            short_description(entry["exact_effect"]),
        )

    # Canonical override batches also write descriptions from the partition.
    # Normalize the complete Ability text banks here so every resulting string,
    # not only newly appended custom rows, is safe for Platinum's msgenc.
    names = sanitize_tree(names)
    uppercase = sanitize_tree(uppercase)
    descriptions = sanitize_tree(descriptions)

    write_bank(root / "res/text/ability_names.json", names)
    write_bank(root / "res/text/ability_names_uppercase.json", uppercase)
    write_bank(root / "res/text/ability_descriptions.json", descriptions)

    supported = load_supported_chars(root)

    checks = {
        "custom_ids_contiguous": actual == expected,
        "custom_tokens_unique": len(tokens) == len(set(tokens)),
        "fits_10bit_save_storage": custom[-1]["id"] <= SAVE_CAPACITY,
        "registry_tail_matches": abilities[-1] == custom[-1]["token"],
        "registry_size_matches": len(abilities) == custom[-1]["id"] + 1,
        "name_bank_size_matches": len(names["messages"]) == custom[-1]["id"] + 1,
        "uppercase_bank_size_matches": len(uppercase["messages"]) == custom[-1]["id"] + 1,
        "description_bank_size_matches": len(descriptions["messages"]) == custom[-1]["id"] + 1,
        "all_ability_text_uses_ds_charmap": all(
            bank_uses_only_supported_chars(bank, supported)
            for bank in (names, uppercase, descriptions)
        ),
        "msgenc_sensitive_quotes_removed": all(
            ch not in json.dumps(bank["messages"], ensure_ascii=False)
            for bank in (names, uppercase, descriptions)
            for ch in ("'", '"', "\u2018", "\u2019", "\u201c", "\u201d")
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR10A_COMPLETE_CUSTOM_ABILITY_NAMESPACE",
        "status": status,
        "canonical_range": [0, CANONICAL_MAX],
        "custom_range": [CUSTOM_FIRST, custom[-1]["id"]],
        "custom_identity_count": len(custom),
        "safe_custom_count": sum(1 for x in custom if not x["review_blocked"]),
        "review_blocked_custom_count": sum(1 for x in custom if x["review_blocked"]),
        "runtime_enabled_custom_count": sum(1 for x in custom if x.get("runtime_enabled", True)),
        "runtime_disabled_reserved_count": sum(1 for x in custom if not x.get("runtime_enabled", True)),
        "implemented_mechanics_in_this_gate": 0,
        "implemented_registry_changed": False,
        "locked_mr07_visuals_touched": False,
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR10A custom Ability namespace validation failed")


if __name__ == "__main__":
    main()
