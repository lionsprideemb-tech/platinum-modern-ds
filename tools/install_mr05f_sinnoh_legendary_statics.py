#!/usr/bin/env python3
"""MR05F — Sinnoh legendary static encounter progression/safety pass.

This pass follows the sealed Mercury special-area policy without changing
ordinary random encounters:

- Turnback Cave fallback Giratina is Lv60.
- Uxie and Azelf are Lv60.
- Cynthia's grandmother can unlock the Dialga/Palkia rifts after the
  Distortion World story, before the League.
- Dialga/Palkia remain Lv70 but no longer consume their rift when the player
  wins without capturing them; leaving/re-entering with the matching Orb lets
  the player retry.

Mesprit's guided pursuit remains a separate pass because it is a roaming/
tracking-system change rather than a simple static-script edit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(text: str, old: str, new: str, where: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{where}: expected exactly one anchor, found {count}")
    return text.replace(old, new, 1)


def patch_level(path: Path, species: str, old_level: int, new_level: int) -> None:
    text = path.read_text()
    old = f"StartLegendaryBattle {species}, {old_level}"
    new = f"StartLegendaryBattle {species}, {new_level}"
    text = replace_once(text, old, new, str(path))
    path.write_text(text)


def patch_celestic_unlock(root: Path) -> None:
    path = root / "res/field/scripts/scripts_celestic_town_north_house.s"
    text = path.read_text()
    text = replace_once(
        text,
        "    GoToIfSet FLAG_GAME_COMPLETED, CelesticTownNorthHouse_IDidSomeResearch\n",
        "    GoToIfGe VAR_EXITED_DISTORTION_WORLD_STATE, 2, CelesticTownNorthHouse_IDidSomeResearch\n",
        str(path),
    )
    path.write_text(text)


def patch_portal_retry(path: Path, prefix: str, species: str, state_var: str, caught_flag: str) -> None:
    text = path.read_text()
    old = f"""    StartLegendaryBattle {species}, 70
    CheckWonBattle VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, {prefix}_BlackOut
    SetVar {state_var}, 1
    CheckDidNotCapture VAR_RESULT
    CallIfEq VAR_RESULT, FALSE, {prefix}_SetFlagCaught{species.removeprefix('SPECIES_').title()}
    ReleaseAll
    End
"""
    # Existing labels use Dialga/Palkia title casing exactly.
    label_suffix = "Dialga" if species == "SPECIES_DIALGA" else "Palkia"
    new = f"""    StartLegendaryBattle {species}, 70
    CheckWonBattle VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, {prefix}_BlackOut
    CheckDidNotCapture VAR_RESULT
    CallIfEq VAR_RESULT, FALSE, {prefix}_SetFlagCaught{label_suffix}
    ReleaseAll
    End
"""
    # Build the exact old anchor with the actual label suffix as well.
    old = f"""    StartLegendaryBattle {species}, 70
    CheckWonBattle VAR_RESULT
    GoToIfEq VAR_RESULT, FALSE, {prefix}_BlackOut
    SetVar {state_var}, 1
    CheckDidNotCapture VAR_RESULT
    CallIfEq VAR_RESULT, FALSE, {prefix}_SetFlagCaught{label_suffix}
    ReleaseAll
    End
"""
    text = replace_once(text, old, new, str(path) + " battle result")

    old_sub = f"""{prefix}_SetFlagCaught{label_suffix}:
    SetFlag {caught_flag}
    Return
"""
    new_sub = f"""{prefix}_SetFlagCaught{label_suffix}:
    SetVar {state_var}, 1
    SetFlag {caught_flag}
    Return
"""
    text = replace_once(text, old_sub, new_sub, str(path) + " capture state")
    path.write_text(text)


def validate(root: Path) -> dict[str, object]:
    turnback = (root / "res/field/scripts/scripts_turnback_cave_giratina_room.s").read_text()
    acuity = (root / "res/field/scripts/scripts_acuity_cavern.s").read_text()
    valor = (root / "res/field/scripts/scripts_valor_cavern.s").read_text()
    celestic = (root / "res/field/scripts/scripts_celestic_town_north_house.s").read_text()
    dialga = (root / "res/field/scripts/scripts_spear_pillar_dialga.s").read_text()
    palkia = (root / "res/field/scripts/scripts_spear_pillar_palkia.s").read_text()
    coronet6 = (root / "res/field/scripts/scripts_mt_coronet_6f.s").read_text()

    checks = {
        "turnback_giratina_level_60": "StartLegendaryBattle SPECIES_GIRATINA, 60" in turnback,
        "uxie_level_60": "StartLegendaryBattle SPECIES_UXIE, 60" in acuity,
        "azelf_level_60": "StartLegendaryBattle SPECIES_AZELF, 60" in valor,
        "celestic_unlock_post_distortion": (
            "GoToIfGe VAR_EXITED_DISTORTION_WORLD_STATE, 2, CelesticTownNorthHouse_IDidSomeResearch" in celestic
            and "GoToIfSet FLAG_GAME_COMPLETED, CelesticTownNorthHouse_IDidSomeResearch" not in celestic
        ),
        "dialga_level_70": "StartLegendaryBattle SPECIES_DIALGA, 70" in dialga,
        "palkia_level_70": "StartLegendaryBattle SPECIES_PALKIA, 70" in palkia,
        "dialga_state_only_on_capture": (
            "SpearPillarDialga_SetFlagCaughtDialga:\n    SetVar VAR_SPEAR_PILLAR_DIALGA_STATE, 1\n    SetFlag FLAG_CAUGHT_DIALGA" in dialga
            and "GoToIfEq VAR_RESULT, FALSE, SpearPillarDialga_BlackOut\n    SetVar VAR_SPEAR_PILLAR_DIALGA_STATE, 1\n    CheckDidNotCapture" not in dialga
        ),
        "palkia_state_only_on_capture": (
            "SpearPillarPalkia_SetFlagCaughtPalkia:\n    SetVar VAR_SPEAR_PILLAR_PALKIA_STATE, 1\n    SetFlag FLAG_CAUGHT_PALKIA" in palkia
            and "GoToIfEq VAR_RESULT, FALSE, SpearPillarPalkia_BlackOut\n    SetVar VAR_SPEAR_PILLAR_PALKIA_STATE, 1\n    CheckDidNotCapture" not in palkia
        ),
        "adamant_orb_gate_preserved": "CheckItem ITEM_ADAMANT_ORB, 1" in coronet6,
        "lustrous_orb_gate_preserved": "CheckItem ITEM_LUSTROUS_ORB, 1" in coronet6,
    }

    failed = [name for name, value in checks.items() if not value]
    if failed:
        raise SystemExit("MR05F validation failed: " + ", ".join(failed))

    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("mr05f-legendary-statics.json"))
    args = ap.parse_args()
    root = args.pokeplatinum_root.resolve()

    patch_level(
        root / "res/field/scripts/scripts_turnback_cave_giratina_room.s",
        "SPECIES_GIRATINA",
        47,
        60,
    )
    patch_level(
        root / "res/field/scripts/scripts_acuity_cavern.s",
        "SPECIES_UXIE",
        50,
        60,
    )
    patch_level(
        root / "res/field/scripts/scripts_valor_cavern.s",
        "SPECIES_AZELF",
        50,
        60,
    )
    patch_celestic_unlock(root)
    patch_portal_retry(
        root / "res/field/scripts/scripts_spear_pillar_dialga.s",
        "SpearPillarDialga",
        "SPECIES_DIALGA",
        "VAR_SPEAR_PILLAR_DIALGA_STATE",
        "FLAG_CAUGHT_DIALGA",
    )
    patch_portal_retry(
        root / "res/field/scripts/scripts_spear_pillar_palkia.s",
        "SpearPillarPalkia",
        "SPECIES_PALKIA",
        "VAR_SPEAR_PILLAR_PALKIA_STATE",
        "FLAG_CAUGHT_PALKIA",
    )

    checks = validate(root)
    report = {
        "gate": "MERCURY_MR05F_SINNOH_LEGENDARY_STATICS",
        "status": "PASS",
        **checks,
        "mesprit_guided_pursuit_deferred": True,
        "fullmoon_newmoon_static_pass_deferred": True,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
