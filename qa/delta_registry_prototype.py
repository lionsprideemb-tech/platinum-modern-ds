#!/usr/bin/env python3
"""Mercury Redux: isolated, non-ROM custom-species registry proof.

This is deliberately NOT a native registry patch. Custom identities are symbolic;
native save and icon use is fail-closed until reviewed engine integration.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
from dataclasses import asdict, dataclass
from pathlib import Path

CANONICAL_COUNT = 1025
SENTINELS = {"SPECIES_NONE": 0, "SPECIES_EGG": 1026, "SPECIES_BAD_EGG": 1027}
CUSTOM = (
    "CUSTOM_DELTA_TRAPINCH",
    "CUSTOM_DELTA_VIBRAVA",
    "CUSTOM_DELTA_FLYGON",
)
SITE_ONLY_IDS = (1581, 1751, 1761, 1816, 1817, 1638, 2081, 2082)
SOURCE_REFS = {
    "engine": "5525e961a1fb98c62bd53bc4a27b0276a39f6719",
    "dex_main": "faa7cb4016d8030fb4661b49114352d79cac7944",
    "dex_audit": "8ea34c7ad72c593b0f9f7845d03acff13fd2ecdd",
    "sprites": "f15c4671bf7afb15450fc7801bde17aefcdc4f7e",
    "pret": "c248fb3f8cc9934ded800e489567c5c0eeee92eb",
    "donor": "5157c501dc0e6f88ef1654ab121352a5cc9ed7de",
}


class PendingNativeIntegration(ValueError):
    """Fail closed instead of silently giving a provisional species an ID."""


@dataclass(frozen=True)
class DraftSpecies:
    key: str
    canonical_parent: str
    required_types: tuple[str, ...]
    unresolved_secondary_type: bool
    evolution_target: str | None
    evolution_method: None = None
    evolution_level: None = None
    native_id: None = None
    icon_archive_index: None = None
    palette_bank: None = None
    artwork_status: str = "unapproved"


DRAFT = (
    DraftSpecies(CUSTOM[0], "SPECIES_TRAPINCH", ("Bug",), True, CUSTOM[1]),
    DraftSpecies(CUSTOM[1], "SPECIES_VIBRAVA", ("Bug",), True, CUSTOM[2]),
    DraftSpecies(CUSTOM[2], "SPECIES_FLYGON", ("Bug", "Ground"), False, None),
)


def canonical_species(path: Path) -> list[str]:
    rows = [
        row.strip() for row in path.read_text().splitlines()
        if row.strip() and not row.lstrip().startswith("#")
    ]
    if len(rows) != CANONICAL_COUNT or len(set(rows)) != CANONICAL_COUNT:
        raise ValueError("Canonical 1025-row registry missing entries or contains duplicates")
    if any(row in SENTINELS or row in CUSTOM for row in rows):
        raise ValueError("Canonical IDs overlap sentinel or provisional custom names")
    if [rows[i - 1] for i in (328, 329, 330, 1025)] != [
        "SPECIES_TRAPINCH", "SPECIES_VIBRAVA", "SPECIES_FLYGON", "SPECIES_PECHARUNT"
    ]:
        raise ValueError("Protected canonical position has changed")
    return rows


def validate_draft(draft: tuple[DraftSpecies, ...] = DRAFT) -> None:
    if tuple(x.key for x in draft) != CUSTOM:
        raise ValueError("Delta lineage identity changed or lost")
    for entry in draft:
        if entry.native_id is not None or entry.icon_archive_index is not None:
            raise ValueError("Production ID/icon allocation is forbidden in QA prototype")
        if entry.palette_bank is not None:
            raise ValueError("Palette bank assignment is not authorized")
        if entry.evolution_level is not None or entry.evolution_method is not None:
            raise ValueError("Delta evolution method/level is not approved")
        if entry.artwork_status != "unapproved":
            raise ValueError("Delta art cannot be auto-approved")
        if "Bug" not in entry.required_types:
            raise ValueError("Delta early stages must be Bug-typed")
    if (draft[0].evolution_target, draft[1].evolution_target, draft[2].evolution_target) != (
        CUSTOM[1], CUSTOM[2], None
    ):
        raise ValueError("Evolution must follow all three Delta stages exactly")
    if draft[2].required_types != ("Bug", "Ground"):
        raise ValueError("Delta Flygon must be Bug/Ground")
    if not draft[0].unresolved_secondary_type or not draft[1].unresolved_secondary_type:
        raise ValueError("Do not invent earlier-stage secondary typings")


def id_for_canonical(species: str, rows: list[str]) -> int:
    if species in SENTINELS:
        return SENTINELS[species]
    if species in CUSTOM or species.startswith("CUSTOM_"):
        raise PendingNativeIntegration("Custom species have no assigned native IDs")
    try:
        return rows.index(species) + 1
    except ValueError as exc:
        raise PendingNativeIntegration("Unknown species cannot be serialized") from exc


def encode_legacy_species(species: str, rows: list[str]) -> bytes:
    """Only simulate legacy 16-bit species field; not a complete DS save format."""
    return struct.pack("<H", id_for_canonical(species, rows))


def decode_legacy_species(encoded: bytes, rows: list[str]) -> str:
    if len(encoded) != 2:
        raise ValueError("Expected exactly one legacy u16 field")
    (value,) = struct.unpack("<H", encoded)
    if 1 <= value <= CANONICAL_COUNT:
        return rows[value - 1]
    for name, ident in SENTINELS.items():
        if ident == value:
            return name
    raise PendingNativeIntegration("Unknown ID: refuse ambiguous native save migration")


def icon_routing(symbol: str, rows: list[str]) -> str:
    if symbol in CUSTOM or symbol.startswith("CUSTOM_"):
        raise PendingNativeIntegration("Native icon archive and routing not registered")
    if symbol in SENTINELS:
        return "egg-or-none: native conditions require runtime inspection"
    if symbol in rows:
        return "canonical: existing icon path (not an emulator proof)"
    raise PendingNativeIntegration("No verified icon route")


def palette_routing(symbol: str) -> str:
    if symbol in CUSTOM or symbol.startswith("CUSTOM_"):
        raise PendingNativeIntegration("No validated Delta palette slot; donor bank 3 != safe")
    return "existing canonical routing only"


def require_source(path: Path, tokens: tuple[str, ...]) -> dict:
    source = path.read_text()
    missing = [token for token in tokens if token not in source]
    if missing:
        raise ValueError(f"Pinned native source guard failed at {path}: {missing}")
    return {"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def self_tests(rows: list[str]) -> dict:
    checks = 0

    def check(condition: bool, label: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(label)

    def rejects(fn, label: str) -> None:
        nonlocal checks
        checks += 1
        try:
            fn()
        except (ValueError, PendingNativeIntegration):
            return
        raise AssertionError("Fail-closed condition did not reject: " + label)

    validate_draft()
    check(tuple(x.key for x in DRAFT) == CUSTOM, "independent symbolic namespace")
    check(len(set(CUSTOM)) == 3, "distinct custom identities")
    check(all(x.native_id is None for x in DRAFT), "no production IDs")
    check(all(x.artwork_status == "unapproved" for x in DRAFT), "unapproved art")
    check(DRAFT[0].evolution_target == CUSTOM[1], "delta first stage")
    check(DRAFT[1].evolution_target == CUSTOM[2], "delta second stage")
    check(DRAFT[2].evolution_target is None, "delta final stage")
    check([rows[i - 1] for i in (328, 329, 330)] ==
          ["SPECIES_TRAPINCH", "SPECIES_VIBRAVA", "SPECIES_FLYGON"],
          "vanilla identity")
    for symbol in (
        "SPECIES_NONE", "SPECIES_TRAPINCH", "SPECIES_VIBRAVA",
        "SPECIES_FLYGON", "SPECIES_PECHARUNT", "SPECIES_EGG", "SPECIES_BAD_EGG"
    ):
        check(decode_legacy_species(encode_legacy_species(symbol, rows), rows) == symbol,
              "legacy u16 roundtrip " + symbol)
    for symbolic in CUSTOM:
        rejects(lambda sym=symbolic: encode_legacy_species(sym, rows), "custom save " + symbolic)
        rejects(lambda sym=symbolic: icon_routing(sym, rows), "custom icon " + symbolic)
        rejects(lambda sym=symbolic: palette_routing(sym), "custom palette " + symbolic)
    for number in (1028, *SITE_ONLY_IDS, 65535):
        rejects(lambda n=number: decode_legacy_species(struct.pack("<H", n), rows),
                "unallocated integer " + str(number))
    rejects(lambda: decode_legacy_species(b"\0", rows), "truncated native field")
    rejects(lambda: id_for_canonical("SPECIES_NOT_REAL", rows), "unknown legacy species")
    rejects(lambda: validate_draft(DRAFT[:2]), "incomplete Delta family")
    rejects(lambda: validate_draft((
        DRAFT[0], DRAFT[1], DraftSpecies(CUSTOM[2], "SPECIES_FLYGON",
                                          ("Electric", "Dragon"), False, None)
    )), "wrong Delta Flygon typing")
    rejects(lambda: validate_draft((
        DraftSpecies(CUSTOM[0], "SPECIES_TRAPINCH", ("Bug",), True, CUSTOM[2]),
        DRAFT[1], DRAFT[2]
    )), "erroneous direct Trapinch-Flygon evolution")
    rejects(lambda: validate_draft((
        DraftSpecies(CUSTOM[0], "SPECIES_TRAPINCH", ("Bug",), True, CUSTOM[1],
                     native_id=1028), DRAFT[1], DRAFT[2]
    )), "forbidden guessed 1028 ID")
    rejects(lambda: validate_draft((
        DraftSpecies(CUSTOM[0], "SPECIES_TRAPINCH", ("Bug",), True, CUSTOM[1],
                     palette_bank=3), DRAFT[1], DRAFT[2]
    )), "unsafe bank 3 allocation")
    rejects(lambda: validate_draft((
        DraftSpecies(CUSTOM[0], "SPECIES_TRAPINCH", ("Bug",), True, CUSTOM[1],
                     evolution_level=35), DRAFT[1], DRAFT[2]
    )), "unapproved Delta level")
    return {"result": "PASS", "checks": checks, "scope": "symbolic model, not native ROM"}


def audit(args) -> dict:
    engine = Path(args.engine)
    sprites = Path(args.sprites)
    pret = Path(args.pret)
    donor = Path(args.donor)
    dex = Path(args.dex)

    rows = canonical_species(engine / "data/canonical_species_1025.txt")
    test_report = self_tests(rows)
    votes = json.loads((sprites / "review/user-iphone-decisions-2026-10-23.json").read_text())
    if not (votes["count"] == len(votes["entries"]) == 166
            and votes["keepCount"] == 154 and votes["cutCount"] == 12):
        raise ValueError("Historical vote ledger diverges from 166 / 154 KEEP / 12 CUT")
    roster = json.loads((sprites / "review/flygon-roster-plan-2026-11-09.json").read_text())
    if roster["acceptance"] != {
        "plannedFamilies": 2, "plannedTotalMegaForms": 1,
        "unresolvedDeltaArtworkMembers": 3, "electricLineMembersInRoster": 0,
        "newDeltaMembers": 3
    }:
        raise ValueError("Route 2 Flygon roster plan changed; manual review required")
    if roster["protections"]["romIntegrationAllowed"] or roster["protections"]["dexSpeciesEditsAllowed"]:
        raise ValueError("Unexpected promotion/integration permission")
    lock = json.loads((engine / "upstream/LOCK.json").read_text())["sources"]
    if lock["pokeplatinum"]["commit"] != SOURCE_REFS["pret"] or lock["hg-engine"]["commit"] != SOURCE_REFS["donor"]:
        raise ValueError("Pinned native source revision changed")

    source_guards = [
        require_source(pret / "include/constants/species.h", (
            "#define MAX_SPECIES        SPECIES_BAD_EGG",
            "#define NATIONAL_DEX_COUNT (MAX_SPECIES - 2)")),
        require_source(pret / "include/struct_defs/pokemon.h", ("u16 species;", "u8 form : 5;")),
        require_source(pret / "include/pokedex.h", ("DEX_SIZE_U32", "caughtPokemon[DEX_SIZE_U32]",
                                                    "seenPokemon[DEX_SIZE_U32]")),
        require_source(pret / "src/savedata/save_table.c", ("(SaveEntrySizeFunc)Pokedex_SaveSize",)),
        require_source(pret / "src/pokemon_icon.c", (
            "if (species > NATIONAL_DEX_COUNT)",
            "species = SPECIES_NONE;",
            "return IconTilesIndex(species);",
            "return sPokemonIconPaletteIndex[species];",
            "shared_pals_NCLR",
            "BoxPokemon_IconFormOffset")),
        require_source(pret / "src/evolution.c", ("evolutionData->targetSpecies = targetSpecies;",
                                                  "evolutionData->currentSpecies = ")),
        require_source(pret / "res/pokemon/meson.build", (
            "species_consts = fs.read(species_txt).splitlines()",
            "pl_poke_icon.narc", "shared_pals_NCLR", "evo.narc")),
    ]
    pal_src = (donor / "data/IconPaletteTable.c").read_text()
    palette_assignments = [
        int(x) for x in re.findall(r"\[\s*SPECIES_[A-Z0-9_]+\s*\]\s*=\s*([0-3])\s*,", pal_src)
    ]
    if not palette_assignments or 3 in palette_assignments:
        raise ValueError("Donor palette assignment assumptions invalidated")
    # Do not assert this is the full generated DS palette table.
    dex_audit = json.loads((dex / "qa/DELTA_FLYGON_ARCHITECTURE_EVIDENCE_2026-11-11.json").read_text())
    site_duplicate_ids = {
        x["id"] for x in dex_audit["audit"]["dex"]["duplicate_numeric_site_ids"]
    }
    if site_duplicate_ids != {1581, 1751, 1761}:
        raise ValueError("Site duplicate IDs changed; re-audit before continued work")

    # These results are NOT native code execution or save-migration tests.
    return {
        "schema": "mercury-delta-symbolic-registry-prototype-v1",
        "status": "QA_ONLY_NO_NATIVE_REGISTRATION",
        "snapshots": SOURCE_REFS,
        "protected": {
            "canonical_species": len(rows),
            "none": SENTINELS["SPECIES_NONE"],
            "egg": SENTINELS["SPECIES_EGG"],
            "bad_egg": SENTINELS["SPECIES_BAD_EGG"],
            "historical_votes": votes["count"],
            "keep": votes["keepCount"], "cut": votes["cutCount"],
            "site_duplicate_ids_not_native_collisions": sorted(site_duplicate_ids),
        },
        "draft": [asdict(x) for x in DRAFT],
        "static_native_guards": source_guards,
        "donor_palette_scan": {
            "explicit_matching_entries": len(palette_assignments),
            "bank_counts_matching_entries": {
                str(i): palette_assignments.count(i) for i in range(4)
            },
            "bank3_production_safety": "NOT_VERIFIED",
            "generated_NCLR_and_UI_lifetime": "NOT_VERIFIED",
        },
        "save_model": {
            "legacy_u16_roundtrip": "PASS_SIMULATED_ONLY",
            "custom_native_write": "REJECTED_UNTIL_VERSIONED_MIGRATION",
            "actual_party_pc_trade_save_reload": "NOT_TESTED",
            "pokedex_mapping_and_dynamic_save_resize": "NOT_TESTED",
        },
        "evolution": {
            "symbolic_delta_graph": "PASS",
            "delta_method_levels": "UNAPPROVED",
            "vanilla_family": "UNMODIFIED",
            "engine_evolution_execution": "NOT_TESTED",
        },
        "icons": {
            "legacy_overflow_falls_back_to_SPECIES_NONE": "SOURCE_VERIFIED",
            "custom_icons": "BLOCKED_NOT_REGISTERED",
            "native_icon_archive_palette_display": "NOT_TESTED",
        },
        "test_report": test_report,
        "runtime_build_or_emulator": "NOT_RUN",
        "artwork_approval": "UNCHANGED_UNAPPROVED",
        "native_IDs_allocated": 0,
        "files_in_main_or_rom_modified": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    for x in ("engine", "sprites", "pret", "donor", "dex"):
        parser.add_argument("--" + x, required=True)
    parser.add_argument("--out", default="qa-output/registry-prototype-evidence.json")
    args = parser.parse_args()
    report = audit(args)
    path = Path(args.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "result": report["test_report"], "votes": report["protected"]["historical_votes"],
        "native_IDs_allocated": report["native_IDs_allocated"],
        "runtime_build_or_emulator": report["runtime_build_or_emulator"],
    }, indent=2))


if __name__ == "__main__":
    main()
