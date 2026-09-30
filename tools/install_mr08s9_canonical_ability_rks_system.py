#!/usr/bin/env python3
"""MR08S9 — canonical RKS System + Memory / Multi-Attack pass.

Implements the mechanics-side Gen VII RKS System package:
- adds all 17 Silvally Memory held items to the Platinum item namespace;
- Silvally with RKS System becomes the type of its held Memory in party,
  Summary, AI and battle data paths (Normal with no Memory);
- Multi-Attack is promoted from the modern-move stub lane to the existing
  Judgment-style variable-type damage lane, including Fairy Memory;
- Memories cannot be removed from Silvally by Knock Off, Thief/Covet,
  Trick/Switcheroo, Fling, Magician, Pickpocket, or Symbiosis;
- RKS System cannot be suppressed, traced, copied, swapped, overwritten by
  Worry Seed/Gastro Acid, or inherited by Receiver/Power of Alchemy.

Type-specific Silvally battle sprite/model presentation remains deferred to the
later form-asset pass. Locked MR07 Summary/editor visuals are not changed.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IMPLEMENTED = ("ABILITY_RKS_SYSTEM",)
EXPECTED_IDS = {"ABILITY_RKS_SYSTEM": 225}

MEMORIES = (
    ("BUG", "Bug"),
    ("DARK", "Dark"),
    ("DRAGON", "Dragon"),
    ("ELECTRIC", "Electric"),
    ("FAIRY", "Fairy"),
    ("FIGHTING", "Fighting"),
    ("FIRE", "Fire"),
    ("FLYING", "Flying"),
    ("GHOST", "Ghost"),
    ("GRASS", "Grass"),
    ("GROUND", "Ground"),
    ("ICE", "Ice"),
    ("POISON", "Poison"),
    ("PSYCHIC", "Psychic"),
    ("ROCK", "Rock"),
    ("STEEL", "Steel"),
    ("WATER", "Water"),
)


def insert_before_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, insertion + anchor, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor in {path}, found {count}")
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match in {path}, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def replace_in_function(
    path: Path,
    signature: str,
    old: str,
    new: str,
    label: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    definition = signature + "\n{"
    start = text.find(definition)
    if start < 0:
        raise SystemExit(f"{label}: function definition not found in {path}")

    open_brace = start + len(signature) + 1
    depth = 0
    end = -1
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end < 0:
        raise SystemExit(f"{label}: closing brace not found in {path}")

    segment = text[start:end]
    count = segment.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one scoped match in {path}, found {count}"
        )
    segment = segment.replace(old, new, 1)
    path.write_text(text[:start] + segment + text[end:], encoding="utf-8")


def validate_ids(root: Path) -> dict[str, bool]:
    abilities = [
        line.strip()
        for line in (root / "generated/abilities.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {
        f"{token.lower()}_id": len(abilities) > expected and abilities[expected] == token
        for token, expected in EXPECTED_IDS.items()
    }


def memory_c_switch(indent: str = "    ") -> str:
    rows = []
    for token, _name in MEMORIES:
        rows.append(f"{indent}case ITEM_{token}_MEMORY:\n{indent}    return TYPE_{token};")
    return "\n".join(rows)


def patch_memory_items(root: Path) -> None:
    generated = root / "generated/items.txt"
    lines = [line.rstrip() for line in generated.read_text(encoding="utf-8").splitlines()]
    try:
        max_idx = lines.index("MAX_ITEMS")
    except ValueError as exc:
        raise SystemExit("RKS System: MAX_ITEMS anchor missing") from exc

    additions = [f"ITEM_{token}_MEMORY" for token, _name in MEMORIES]
    for item in additions:
        if item not in lines:
            lines.insert(max_idx, item)
            max_idx += 1
    generated.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    item_dir = root / "res/items/data"
    item_dir.mkdir(parents=True, exist_ok=True)
    for token, name in MEMORIES:
        path = item_dir / f"{token.lower()}_memory.json"
        data = {
            "name": f"{name} Memory",
            "plural": f"{name} Memories",
            "article": "a",
            "description": [
                f"A Memory disc holding {name}-type data.\n",
                "It changes Silvally’s type with RKS System.",
            ],
            "icon": {
                "sprite": "choice_specs_NCGR",
                "palette": "choice_specs_NCLR",
            },
            "gbaID": "GBA_ITEM_NONE",
            "price": 0,
            "effectParam": 0,
            "holdEffect": "HOLD_EFFECT_NONE",
            "pluckEffect": "PLUCK_EFFECT_NONE",
            "flingEffect": "FLING_EFFECT_NONE",
            "flingPower": 50,
            "naturalGiftPower": 0,
            "naturalGiftType": None,
            "preventToss": False,
            "canRegister": False,
            "fieldPocket": "POCKET_ITEMS",
            "battlePocket": "BATTLE_POCKET_MASK_NONE",
            "fieldUseFunc": "ITEM_USE_FUNC_NONE",
            "battleUseCategory": "BATTLE_USE_CATEGORY_NONE",
            "itemUseParams": None,
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def patch_party_and_summary_typing(root: Path) -> None:
    path = root / "src/pokemon.c"

    helper = f"""static int Mercury_MemoryTypeFromItem(int item)
{{
    switch (item) {{
{memory_c_switch("    ")}
    default:
        return TYPE_NORMAL;
    }}
}}

"""
    insert_before_once(
        path,
        """static u32 BoxPokemon_GetDataInternal(BoxPokemon *boxMon, enum PokemonDataParam param, void *dest)
{
""",
        helper,
        "RKS party/summary Memory type helper",
    )

    replace_once(
        path,
        """    case MON_DATA_TYPE_1:
    case MON_DATA_TYPE_2:
        if (monDataBlockA->species == SPECIES_ARCEUS && monDataBlockA->ability == ABILITY_MULTITYPE) {
            result = Pokemon_GetArceusTypeOf(Item_LoadParam(monDataBlockA->heldItem, ITEM_PARAM_HOLD_EFFECT, HEAP_ID_SYSTEM));
        } else {
            result = SpeciesData_GetFormValue(monDataBlockA->species, monDataBlockB->form, SPECIES_DATA_TYPE_1 + (param - MON_DATA_TYPE_1));
        }
        break;
""",
        """    case MON_DATA_TYPE_1:
    case MON_DATA_TYPE_2:
        if (monDataBlockA->species == SPECIES_ARCEUS && monDataBlockA->ability == ABILITY_MULTITYPE) {
            result = Pokemon_GetArceusTypeOf(Item_LoadParam(monDataBlockA->heldItem, ITEM_PARAM_HOLD_EFFECT, HEAP_ID_SYSTEM));
        } else if (monDataBlockA->ability == ABILITY_RKS_SYSTEM) {
            result = Mercury_MemoryTypeFromItem(monDataBlockA->heldItem);
        } else {
            result = SpeciesData_GetFormValue(monDataBlockA->species, monDataBlockB->form, SPECIES_DATA_TYPE_1 + (param - MON_DATA_TYPE_1));
        }
        break;
""",
        "RKS party/summary typing",
    )


def patch_battle_type_helpers(root: Path) -> None:
    path = root / "src/battle/battle_lib.c"

    helper = f"""static int Mercury_MemoryTypeFromItem(int item)
{{
    switch (item) {{
{memory_c_switch("    ")}
    default:
        return TYPE_NORMAL;
    }}
}}

static BOOL Mercury_IsMemoryItem(int item)
{{
    return Mercury_MemoryTypeFromItem(item) != TYPE_NORMAL;
}}

static BOOL Mercury_IsSilvallyMemoryLocked(
    BattleContext *battleCtx,
    int battler)
{{
    return Battler_Ability(battleCtx, battler) == ABILITY_RKS_SYSTEM
        && Mercury_IsMemoryItem(battleCtx->battleMons[battler].heldItem);
}}

"""
    insert_before_once(
        path,
        """static int CalcMoveType(BattleSystem *battleSys, BattleContext *battleCtx, int item, int move)
{
""",
        helper,
        "RKS battle Memory helpers",
    )

    replace_in_function(
        path,
        "static int CalcMoveType(BattleSystem *battleSys, BattleContext *battleCtx, int item, int move)",
        """    case MOVE_JUDGMENT:
""",
        """    case MOVE_MULTI_ATTACK:
        type = Mercury_MemoryTypeFromItem(
            Battler_HeldItem(battleCtx, item));
        break;

    case MOVE_JUDGMENT:
""",
        "Multi-Attack battle type",
    )

    replace_in_function(
        path,
        "int Move_CalcVariableType(BattleSystem *battleSys, BattleContext *battleCtx, Pokemon *mon, int move)",
        """    case MOVE_JUDGMENT:
""",
        """    case MOVE_MULTI_ATTACK:
        type = Mercury_MemoryTypeFromItem(
            Pokemon_GetValue(mon, MON_DATA_HELD_ITEM, NULL));
        break;

    case MOVE_JUDGMENT:
""",
        "Multi-Attack AI type",
    )

    replace_in_function(
        path,
        "BOOL BattleSystem_CanStealItem(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """    if (battleCtx->battleMons[battler].heldItem
        && (battleCtx->sideConditions[side].knockedOffItemsMask & FlagIndex(battleCtx->selectedPartySlot[battler])) == FALSE
        && Item_IsMail(battleCtx->battleMons[battler].heldItem) == FALSE) {
""",
        """    if (battleCtx->battleMons[battler].heldItem
        && Mercury_IsSilvallyMemoryLocked(battleCtx, battler) == FALSE
        && (battleCtx->sideConditions[side].knockedOffItemsMask & FlagIndex(battleCtx->selectedPartySlot[battler])) == FALSE
        && Item_IsMail(battleCtx->battleMons[battler].heldItem) == FALSE) {
""",
        "Memory theft lock",
    )

    replace_in_function(
        path,
        "BOOL BattleSystem_FlingItem(BattleSystem *battleSys, BattleContext *battleCtx, int battler)",
        """{
    int effect = Battler_ItemFlingEffect(battleCtx, battler);
""",
        """{
    if (Mercury_IsSilvallyMemoryLocked(battleCtx, battler)) {
        return FALSE;
    }

    int effect = Battler_ItemFlingEffect(battleCtx, battler);
""",
        "Memory Fling lock",
    )

    # MR08K Magician and Pickpocket directly transfer items; include the same
    # Memory lock in those modern Ability paths.
    replace_once(
        path,
        """        && ATTACKING_MON.heldItem == ITEM_NONE
        && DEFENDING_MON.heldItem != ITEM_NONE
        && Battler_Ability(battleCtx, battleCtx->defender) != ABILITY_STICKY_HOLD
""",
        """        && ATTACKING_MON.heldItem == ITEM_NONE
        && DEFENDING_MON.heldItem != ITEM_NONE
        && Mercury_IsSilvallyMemoryLocked(
            battleCtx, battleCtx->defender) == FALSE
        && Battler_Ability(battleCtx, battleCtx->defender) != ABILITY_STICKY_HOLD
""",
        "Memory Magician lock",
    )

    replace_once(
        path,
        """            && DEFENDING_MON.heldItem == ITEM_NONE
            && ATTACKING_MON.heldItem != ITEM_NONE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
""",
        """            && DEFENDING_MON.heldItem == ITEM_NONE
            && ATTACKING_MON.heldItem != ITEM_NONE
            && Mercury_IsSilvallyMemoryLocked(
                battleCtx, battleCtx->attacker) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
""",
        "Memory Pickpocket lock",
    )


def patch_multi_attack(root: Path, move_registry: Path | None) -> None:
    move_data = root / "res/moves/multi_attack/data.json"
    if not move_data.is_file():
        # A clean pokeplatinum checkout has no post-Gen-IV Multi-Attack data.
        # Seed the modern move in the same JSON schema as the native move
        # resources so the canonical Ability stack can rebuild from scratch.
        move_data.parent.mkdir(parents=True, exist_ok=True)
        move_data.write_text(
            json.dumps(
                {
                    "name": "Multi-Attack",
                    "description": [
                        "The user cloaks itself in\\n",
                        "high energy and attacks.\\n",
                        "The move's type matches\\n",
                        "the Memory it is holding.",
                    ],
                    "class": "CLASS_PHYSICAL",
                    "type": "TYPE_NORMAL",
                    "power": 120,
                    "accuracy": 100,
                    "pp": 10,
                    "effect": {
                        "type": "BATTLE_EFFECT_JUDGEMENT",
                        "chance": 0,
                    },
                    "range": "RANGE_SINGLE_TARGET",
                    "priority": 0,
                    "flags": [
                        "MOVE_FLAG_CAN_PROTECT",
                        "MOVE_FLAG_CAN_MIRROR_MOVE",
                        "MOVE_FLAG_TRIGGERS_KINGS_ROCK",
                    ],
                    "contest": {
                        "effect": "CONTEST_EFFECT_RANDOM_ORDER",
                        "type": "CONTEST_TYPE_COOL",
                    },
                },
                indent=4,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        script_path = move_data.parent / "script.s"
        script_path.write_text(
            '#include "macros/btlcmd.inc"\n\n\n_000:\n    GoToEffectScript\n',
            encoding="utf-8",
        )

        donor_anim = root / "res/moves/judgment/anim.s"
        if not donor_anim.is_file():
            raise SystemExit("Multi-Attack: Judgment animation donor missing")
        (move_data.parent / "anim.s").write_text(
            donor_anim.read_text(encoding="utf-8"),
            encoding="utf-8",
        )

    data = json.loads(move_data.read_text(encoding="utf-8"))
    data["effect"]["type"] = "BATTLE_EFFECT_JUDGEMENT"
    data["effect"]["chance"] = 0
    data["class"] = "CLASS_PHYSICAL"
    data["type"] = "TYPE_NORMAL"
    data["power"] = 120
    data["accuracy"] = 100
    data["pp"] = 10
    move_data.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    effect = root / "res/battle/scripts/effects/effect_script_0268.s"
    original = effect.read_text(encoding="utf-8")
    if "_MercuryMultiAttack:" not in original:
        anchor = """_000:
"""
        if original.count(anchor) != 1:
            raise SystemExit("Multi-Attack: Judgment script entry anchor missing")

        checks = []
        labels = []
        for idx, (token, _name) in enumerate(MEMORIES):
            label = f"_MercuryMemory{idx}"
            checks.append(
                f"    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, "
                f"BATTLEMON_HELD_ITEM, ITEM_{token}_MEMORY, {label}\n"
            )
            labels.append(
                f"{label}:\n"
                f"    UpdateVar OPCODE_SET, BTLVAR_MOVE_TYPE, TYPE_{token}\n"
                f"    GoTo _175\n\n"
            )

        insertion = (
            "_000:\n"
            "    CompareVarToValue OPCODE_EQU, BTLVAR_CURRENT_MOVE, "
            "MOVE_MULTI_ATTACK, _MercuryMultiAttack\n"
        )
        original = original.replace(anchor, insertion, 1)

        multi = (
            "\n_MercuryMultiAttack:\n"
            + "".join(checks)
            + "    UpdateVar OPCODE_SET, BTLVAR_MOVE_TYPE, TYPE_NORMAL\n"
            + "    GoTo _175\n\n"
            + "".join(labels)
        )
        marker = """_081:
"""
        if original.count(marker) != 1:
            raise SystemExit("Multi-Attack: Judgment type-label anchor missing")
        original = original.replace(marker, multi + marker, 1)
        effect.write_text(original, encoding="utf-8")

    registry_path = move_registry or (root / "generated/moves.txt")
    rows = [
        line.strip()
        for line in registry_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if "MOVE_MULTI_ATTACK" not in rows:
        if "MAX_MOVES" not in rows:
            raise SystemExit("Multi-Attack: move registry missing MAX_MOVES")
        rows.insert(rows.index("MAX_MOVES"), "MOVE_MULTI_ATTACK")
    registry_path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def patch_script_item_locks(root: Path) -> None:
    path = root / "src/battle/battle_script.c"

    helper = f"""static BOOL Mercury_IsMemoryItemScript(int item)
{{
    switch (item) {{
{chr(10).join(f"    case ITEM_{token}_MEMORY:" for token, _ in MEMORIES)}
        return TRUE;
    default:
        return FALSE;
    }}
}}

static BOOL Mercury_IsSilvallyMemoryLockedScript(
    BattleContext *battleCtx,
    int battler)
{{
    return Battler_Ability(battleCtx, battler) == ABILITY_RKS_SYSTEM
        && Mercury_IsMemoryItemScript(
            battleCtx->battleMons[battler].heldItem);
}}

"""
    insert_before_once(
        path,
        """static BOOL BtlCmd_TryStealItem(BattleSystem *battleSys, BattleContext *battleCtx)
{
""",
        helper,
        "Memory script-side item lock helpers",
    )

    replace_in_function(
        path,
        "static BOOL BtlCmd_TryKnockOff(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    if (DEFENDING_MON.heldItem && Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->defender, ABILITY_STICKY_HOLD) == TRUE) {
""",
        """    if (Mercury_IsSilvallyMemoryLockedScript(
            battleCtx, battleCtx->defender)) {
        BattleScript_Iter(battleCtx, jumpOnFail);
    } else if (DEFENDING_MON.heldItem && Battler_IgnorableAbility(battleCtx, battleCtx->attacker, battleCtx->defender, ABILITY_STICKY_HOLD) == TRUE) {
""",
        "Memory Knock Off lock",
    )

    replace_in_function(
        path,
        "static BOOL BtlCmd_TrySwapItems(BattleSystem *battleSys, BattleContext *battleCtx)",
        """    if (BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker) && (battleType & BATTLE_TYPE_FRONTIER_LINK) == FALSE) {
""",
        """    if (Mercury_IsSilvallyMemoryLockedScript(
            battleCtx, battleCtx->attacker)
        || Mercury_IsSilvallyMemoryLockedScript(
            battleCtx, battleCtx->defender)) {
        BattleScript_Iter(battleCtx, jumpOnFail);
    } else if (BattleSystem_GetBattlerSide(battleSys, battleCtx->attacker) && (battleType & BATTLE_TYPE_FRONTIER_LINK) == FALSE) {
""",
        "Memory Trick/Switcheroo lock",
    )

    # MR08P2's Symbiosis donor path must not pass a Silvally-held Memory.
    replace_once(
        path,
        """        && Battler_Ability(battleCtx, ally) == ABILITY_SYMBIOSIS
        && battleCtx->battleMons[ally].heldItem != ITEM_NONE
        && battleCtx->battleMons[ally].heldItem != ITEM_GRISEOUS_ORB) {
""",
        """        && Battler_Ability(battleCtx, ally) == ABILITY_SYMBIOSIS
        && battleCtx->battleMons[ally].heldItem != ITEM_NONE
        && battleCtx->battleMons[ally].heldItem != ITEM_GRISEOUS_ORB
        && Mercury_IsSilvallyMemoryLockedScript(
            battleCtx, ally) == FALSE) {
""",
        "Memory Symbiosis lock",
    )


def patch_special_restrictions(root: Path) -> None:
    lib = root / "src/battle/battle_lib.c"
    copy = root / "res/battle/scripts/subscripts/subscript_copy_ability.s"
    swap = root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s"
    suppress = root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s"
    worry = root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s"

    replace_once(
        lib,
        """        && ability1 != ABILITY_POWER_CONSTRUCT;
""",
        """        && ability1 != ABILITY_POWER_CONSTRUCT
        && ability1 != ABILITY_RKS_SYSTEM;
""",
        "RKS Trace defender1",
    )
    replace_once(
        lib,
        """        && ability2 != ABILITY_POWER_CONSTRUCT;
""",
        """        && ability2 != ABILITY_POWER_CONSTRUCT
        && ability2 != ABILITY_RKS_SYSTEM;
""",
        "RKS Trace defender2",
    )

    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _091\n",
        "RKS Role Play target",
    )
    insert_after_once(
        copy,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _091\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _091\n",
        "RKS Role Play user",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _156\n",
        "RKS Skill Swap target",
    )
    insert_after_once(
        swap,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _156\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_ATTACKER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _156\n",
        "RKS Skill Swap user",
    )
    insert_after_once(
        suppress,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _034\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _034\n",
        "RKS Gastro Acid lock",
    )
    insert_after_once(
        worry,
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_POWER_CONSTRUCT, _041\n",
        "    CompareMonDataToValue OPCODE_EQU, BTLSCR_DEFENDER, BATTLEMON_ABILITY, ABILITY_RKS_SYSTEM, _041\n",
        "RKS Worry Seed lock",
    )


def update_registry(path: Path) -> None:
    rows = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    for token in IMPLEMENTED:
        if token not in rows:
            rows.append(token)
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def validate(
    root: Path,
    registry: Path,
    move_registry: Path | None,
) -> dict[str, bool]:
    pokemon = (root / "src/pokemon.c").read_text(encoding="utf-8")
    lib = (root / "src/battle/battle_lib.c").read_text(encoding="utf-8")
    script = (root / "src/battle/battle_script.c").read_text(encoding="utf-8")
    effect = (root / "res/battle/scripts/effects/effect_script_0268.s").read_text(encoding="utf-8")
    move_data = json.loads(
        (root / "res/moves/multi_attack/data.json").read_text(encoding="utf-8")
    )
    move_script = root / "res/moves/multi_attack/script.s"
    move_anim = root / "res/moves/multi_attack/anim.s"
    copy = (root / "res/battle/scripts/subscripts/subscript_copy_ability.s").read_text(encoding="utf-8")
    swap = (root / "res/battle/scripts/subscripts/subscript_exchange_abilities.s").read_text(encoding="utf-8")
    suppress = (root / "res/battle/scripts/subscripts/subscript_suppress_target_ability.s").read_text(encoding="utf-8")
    worry = (root / "res/battle/scripts/subscripts/subscript_give_target_insomnia.s").read_text(encoding="utf-8")
    registry_lines = set(registry.read_text(encoding="utf-8").splitlines())

    cannot_start = lib.index("static BOOL Mercury_AbilityCannotBeNeutralized")
    cannot_end = lib.index("static BOOL Mercury_NeutralizingGasRawActive", cannot_start)
    cannot = lib[cannot_start:cannot_end]

    receiver_start = lib.index("static BOOL Mercury_AbilityCanBeReceived")
    receiver_end = lib.index("static int Mercury_CountFaintedPartyMons", receiver_start)
    receiver = lib[receiver_start:receiver_end]

    item_lines = set((root / "generated/items.txt").read_text(encoding="utf-8").splitlines())
    memory_tokens = {f"ITEM_{token}_MEMORY" for token, _ in MEMORIES}

    registry_path = move_registry or (root / "generated/moves.txt")
    registry_rows = [
        line.strip()
        for line in registry_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    move_registry_ok = (
        "MOVE_MULTI_ATTACK" in registry_rows
        and "MAX_MOVES" in registry_rows
        and registry_rows.index("MOVE_MULTI_ATTACK") < registry_rows.index("MAX_MOVES")
    )

    checks = {
        "all_17_memories_registered":
            memory_tokens.issubset(item_lines)
            and all(
                (root / "res/items/data" / f"{token.lower()}_memory.json").is_file()
                for token, _ in MEMORIES
            ),
        "party_summary_type_change":
            "ABILITY_RKS_SYSTEM" in pokemon
            and "Mercury_MemoryTypeFromItem(monDataBlockA->heldItem)" in pokemon,
        "battle_and_ai_multi_attack_type":
            lib.count("case MOVE_MULTI_ATTACK:") >= 2
            and "Mercury_MemoryTypeFromItem" in lib,
        "multi_attack_effect_enabled":
            move_data["effect"]["type"] == "BATTLE_EFFECT_JUDGEMENT"
            and move_data["power"] == 120
            and move_data["class"] == "CLASS_PHYSICAL",
        "multi_attack_all_memory_types":
            "_MercuryMultiAttack:" in effect
            and all(f"ITEM_{token}_MEMORY" in effect for token, _ in MEMORIES)
            and "TYPE_FAIRY" in effect,
        "multi_attack_registry_updated": move_registry_ok,
        "memory_knockoff_swap_theft_fling_locks":
            "Mercury_IsSilvallyMemoryLockedScript" in script
            and "BtlCmd_TryKnockOff" in script
            and "BtlCmd_TrySwapItems" in script
            and "Mercury_IsSilvallyMemoryLocked(battleCtx, battler)" in lib,
        "memory_magician_pickpocket_symbiosis_locks":
            lib.count("Mercury_IsSilvallyMemoryLocked(") >= 4
            and "Mercury_IsSilvallyMemoryLockedScript(" in script
            and "ABILITY_SYMBIOSIS" in script,
        "neutralizing_gas_cannot_suppress":
            "ABILITY_RKS_SYSTEM" in cannot,
        "trace_blocked":
            "ability1 != ABILITY_RKS_SYSTEM" in lib
            and "ability2 != ABILITY_RKS_SYSTEM" in lib,
        "role_play_and_skill_swap_blocked":
            "ABILITY_RKS_SYSTEM" in copy
            and "ABILITY_RKS_SYSTEM" in swap,
        "gastro_acid_and_worry_seed_blocked":
            "ABILITY_RKS_SYSTEM" in suppress
            and "ABILITY_RKS_SYSTEM" in worry,
        "receiver_blocked":
            "ABILITY_RKS_SYSTEM" in receiver,
        "implemented_registry_updated":
            all(token in registry_lines for token in IMPLEMENTED),
    }
    checks.update(validate_ids(root))
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--move-registry", type=Path, default=None)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr08s9-canonical-ability-rks-system.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()
    move_registry = (
        args.move_registry.resolve() if args.move_registry is not None else None
    )

    patch_memory_items(root)
    patch_party_and_summary_typing(root)
    patch_battle_type_helpers(root)
    patch_multi_attack(root, move_registry)
    patch_script_item_locks(root)
    patch_special_restrictions(root)
    update_registry(registry)

    checks = validate(root, registry, move_registry)
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {
        "gate": "MERCURY_MR08S9_CANONICAL_ABILITY_RKS_SYSTEM",
        "status": status,
        "ui_changed": False,
        "locked_mr07_visuals_touched": False,
        "implemented_abilities": list(IMPLEMENTED),
        "implemented_count": len(IMPLEMENTED),
        "memory_items_added": len(MEMORIES),
        "multi_attack_enabled": True,
        "running_modern_mechanics_total": 182,
        "remaining_modern_canonical_mechanics": 5,
        "form_visuals_deferred": True,
        "policy": "Official RKS System Memory typing and Multi-Attack type conversion. Runtime behavior is keyed to ABILITY_RKS_SYSTEM so this canonical mechanic compiles before Mercury's later modern-species roster namespace is installed.",
        "checks": checks,
    }
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if status != "PASS":
        raise SystemExit("MR08S9 validation failed")


if __name__ == "__main__":
    main()
