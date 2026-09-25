#!/usr/bin/env python3
"""Install CM08's first two custom battle effects into native pokeplatinum.

Both effects are battle-script-only extensions. They deliberately avoid new
battle-state fields, statuses, weather, terrain, or C-side damage hooks.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EFFECTS = [
    (
        "BATTLE_EFFECT_RAISE_SPEED_HIT",
        277,
        """#include "macros/btlcmd.inc"


_000:
    UpdateVar OPCODE_SET, BTLVAR_SIDE_EFFECT_FLAGS_INDIRECT, MOVE_SIDE_EFFECT_TO_ATTACKER|MOVE_SUBSCRIPT_PTR_SPEED_UP_1_STAGE
    CalcCrit 
    CalcDamage 
    End 
""",
    ),
    (
        "BATTLE_EFFECT_DOUBLE_POWER_IF_TARGET_PARALYZED",
        278,
        """#include "macros/btlcmd.inc"


_000:
    CompareMonDataToValue OPCODE_FLAG_SET, BTLSCR_DEFENDER, BATTLEMON_STATUS, MON_CONDITION_PARALYSIS, _014
    UpdateVar OPCODE_SET, BTLVAR_POWER_MULTI, 10
    GoTo _018

_014:
    UpdateVar OPCODE_SET, BTLVAR_POWER_MULTI, 20

_018:
    CalcCrit 
    CalcDamage 
    End 
""",
    ),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--report", type=Path, default=Path("cm08-simple-effects-install.json"))
    args = ap.parse_args()

    pt = args.pokeplatinum_root.resolve()
    effects_txt = pt / "generated" / "move_battle_effects.txt"
    meson = pt / "res" / "battle" / "scripts" / "effects" / "meson.build"
    effects_dir = meson.parent

    effects = [line.strip() for line in effects_txt.read_text(encoding="utf-8").splitlines() if line.strip()]
    if effects[-1] != "BATTLE_EFFECT_RAISE_SP_ATK_HIT":
        raise SystemExit(f"unexpected native effect tail: {effects[-1]}")
    if len(effects) != 277:
        raise SystemExit(f"expected 277 native effects (0-276), got {len(effects)}")

    meson_text = meson.read_text(encoding="utf-8")
    anchor = "    'effect_script_0276.s'\n)"
    if meson_text.count(anchor) != 1:
        raise SystemExit("could not locate unique native effect-script tail in meson.build")

    additions = []
    installed = []
    for name, effect_id, script_text in EFFECTS:
        if effect_id != len(effects):
            raise SystemExit(f"effect ID mismatch for {name}: expected {len(effects)}, got {effect_id}")
        effects.append(name)
        filename = f"effect_script_{effect_id:04d}.s"
        path = effects_dir / filename
        if path.exists():
            raise SystemExit(f"effect script already exists: {path}")
        path.write_text(script_text, encoding="utf-8")
        additions.append(f"    '{filename}'")
        installed.append({"id": effect_id, "name": name, "script": filename})

    effects_txt.write_text("\n".join(effects) + "\n", encoding="utf-8")
    replacement = "    'effect_script_0276.s',\n" + ",\n".join(additions) + "\n)"
    meson.write_text(meson_text.replace(anchor, replacement, 1), encoding="utf-8")

    report = {
        "gate": "CM08_SIMPLE_ELECTRIC_EFFECTS_INSTALL",
        "runtime": "pokeplatinum",
        "native_effect_count_before": 277,
        "effect_count_after": len(effects),
        "installed": installed,
        "implementation_scope": "battle scripts only; no new battle-state fields or C-side mechanics",
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
