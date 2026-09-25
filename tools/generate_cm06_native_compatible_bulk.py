#!/usr/bin/env python3
"""Generate a bulk community-move batch that uses only native Platinum mechanics.

The source library contains 519 audited community moves. This generator is
intentionally conservative: it emits a move only when its complete battle
behavior can be represented by an existing pokeplatinum battle effect plus the
normal move-table fields (power, accuracy, PP, range, priority, flags).

Anything requiring a new effect, custom status, conditional type/damage logic,
special field behavior, or an unresolved duplicate/redesign decision is written
to the deferred report instead of being approximated.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import textwrap
import unicodedata
from pathlib import Path

SOURCE_COMMIT = "4250c4bfbb2e8dddd117160cec9e1e8395dfe9f7"

COMMUNITY_END = 1599

CANONICAL_TYPES = {
    "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting",
    "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost",
    "Dragon", "Dark", "Steel", "Fairy",
}

# Approved rejects, explicit redesigns, and unresolved duplicate groups stay out
# of the native-only bulk pass. Existing CM01-CM05 records are excluded
# separately by token.
HOLD_NAMES = {
    "Swift Strike", "Think Fast", "Stampede", "Sky Fall", "Fang Leech",
    "Zombie Strike", "Elbow Drop", "Solar Flare", "Fiery Horn",
    "Lovely Bite", "Cutsie Slap", "Flame Tongue", "Cupid Shot",
    "Squeaky Hammer", "Beatdown", "Relentless Clobber", "Totemic Fury",
    "Illusory Sand",
}

# Known source mechanics that look superficially native but contain an extra
# behavior that Platinum cannot express with the selected native effect.
HOLD_TOKENS = {
    "MOVE_DEATHROLL",          # ignores target stat stages
    "MOVE_SCORCHED_EARTH",     # dynamic Fire/Ground effectiveness typing
    "MOVE_WYRM_WIND",          # post-multihit Speed+/SpDef-
    "MOVE_MOLTEN_STRIKE",      # guaranteed self Speed drop after hit
    "MOVE_TOXIC_NEEDLES",      # multi-hit plus poison chance
    "MOVE_POP_MAYHEM",         # multi-hit plus burn chance
    "MOVE_TANGLING_HUSK",      # type-selective Protect plus contact slow
    "MOVE_MERCULIGHT",         # Protect plus contact paralysis
    "MOVE_SPARKLING_BARRAGE",  # audited text says three beams vs double-hit code
    "MOVE_VEXING_VOID",        # special fog accuracy rule
    "MOVE_SABER_SLASHES",      # dynamic Electric/Fire typing
    "JOLTKICK",                # high-critical ratio plus paralysis
    "POLARFLARE",              # post-use form change
}

DIRECT_EFFECTS = {
    "EFFECT_FLINCH_HIT": "BATTLE_EFFECT_FLINCH_HIT",
    "EFFECT_MULTI_HIT": "BATTLE_EFFECT_MULTI_HIT",
    "EFFECT_BURN_HIT": "BATTLE_EFFECT_BURN_HIT",
    "EFFECT_CONFUSE_HIT": "BATTLE_EFFECT_CONFUSE_HIT",
    "EFFECT_DEFENSE_DOWN_HIT": "BATTLE_EFFECT_LOWER_DEFENSE_HIT",
    "EFFECT_SPEED_DOWN_HIT": "BATTLE_EFFECT_LOWER_SPEED_HIT",
    "EFFECT_PARALYZE_HIT": "BATTLE_EFFECT_PARALYZE_HIT",
    "EFFECT_HIT": "BATTLE_EFFECT_HIT",
    "EFFECT_ATTACK_UP_HIT": "BATTLE_EFFECT_RAISE_ATTACK_HIT",
    "EFFECT_PROTECT": "BATTLE_EFFECT_PROTECT",
    "EFFECT_SPECIAL_ATTACK_DOWN_HIT": "BATTLE_EFFECT_LOWER_SP_ATK_HIT",
    "EFFECT_RECOIL_IF_MISS": "BATTLE_EFFECT_CRASH_ON_MISS",
    "EFFECT_POISON_HIT": "BATTLE_EFFECT_POISON_HIT",
    "EFFECT_BRICK_BREAK": "BATTLE_EFFECT_REMOVE_SCREENS",
    "EFFECT_HIT_ESCAPE": "BATTLE_EFFECT_SWITCH_HIT",
    "EFFECT_TRIPLE_KICK": "BATTLE_EFFECT_HIT_THREE_TIMES",
    "EFFECT_ABSORB": "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT",
    "EFFECT_DOUBLE_HIT": "BATTLE_EFFECT_HIT_TWICE",
    "EFFECT_RECOIL_33": "BATTLE_EFFECT_RECOIL_THIRD",
    "EFFECT_RECOIL_50": "BATTLE_EFFECT_RECOIL_HALF",
    "EFFECT_SUPERPOWER": "BATTLE_EFFECT_ATK_DEF_DOWN",
    "EFFECT_OVERHEAT": "BATTLE_EFFECT_USER_SP_ATK_DOWN_2",
    "EFFECT_SPECIAL_DEFENSE_DOWN_HIT": "BATTLE_EFFECT_LOWER_SP_DEF_HIT",
    "EFFECT_ACCURACY_DOWN_HIT": "BATTLE_EFFECT_LOWER_ACCURACY_HIT",
    "EFFECT_ATTACK_DOWN_HIT": "BATTLE_EFFECT_LOWER_ATTACK_HIT",
    "EFFECT_STEALTH_ROCK": "BATTLE_EFFECT_STEALTH_ROCK",
    "EFFECT_EXPLOSION": "BATTLE_EFFECT_HALVE_DEFENSE",
    "EFFECT_FACADE": "BATTLE_EFFECT_DOUBLE_POWER_WHEN_STATUSED",
}

EFFECT_DONORS = {
    "BATTLE_EFFECT_PROTECT": "protect",
    "BATTLE_EFFECT_STEALTH_ROCK": "stealth_rock",
    "BATTLE_EFFECT_TOXIC_SPIKES": "toxic_spikes",
    "BATTLE_EFFECT_RESTORE_HP_EVERY_TURN": "aqua_ring",
    "BATTLE_EFFECT_SPEED_UP": "agility",
    "BATTLE_EFFECT_ATK_UP": "meditate",
    "BATTLE_EFFECT_SP_ATK_UP": "nasty_plot",
    "BATTLE_EFFECT_CRIT_UP_2": "focus_energy",
    "BATTLE_EFFECT_REMOVE_SCREENS": "brick_break",
    "BATTLE_EFFECT_SWITCH_HIT": "u_turn",
    "BATTLE_EFFECT_HALVE_DEFENSE": "explosion",
    "BATTLE_EFFECT_BYPASS_ACCURACY": "swift",
    "BATTLE_EFFECT_HIGH_CRITICAL": "slash",
    "BATTLE_EFFECT_BIND_HIT": "bind",
    "BATTLE_EFFECT_RECHARGE_AFTER": "hyper_beam",
    "BATTLE_EFFECT_CONTINUE_AND_CONFUSE_SELF": "outrage",
    "BATTLE_EFFECT_DOUBLE_POWER_WHEN_BELOW_HALF": "brine",
    "BATTLE_EFFECT_INCREASE_POWER_WITH_MORE_HP": "eruption",
    "BATTLE_EFFECT_ATK_DEF_DOWN": "superpower",
    "BATTLE_EFFECT_USER_SP_ATK_DOWN_2": "overheat",
    "BATTLE_EFFECT_HIT_THREE_TIMES": "triple_kick",
    "BATTLE_EFFECT_MULTI_HIT": "fury_attack",
    "BATTLE_EFFECT_HIT_TWICE": "double_hit",
    "BATTLE_EFFECT_CRASH_ON_MISS": "jump_kick",
    "BATTLE_EFFECT_RAISE_ATTACK_HIT": "metal_claw",
    "BATTLE_EFFECT_RAISE_DEF_HIT": "steel_wing",
    "BATTLE_EFFECT_RAISE_SP_ATK_HIT": "charge_beam",
    "BATTLE_EFFECT_RAISE_ALL_STATS_HIT": "ancient_power",
    "BATTLE_EFFECT_LOWER_ATTACK_HIT": "aurora_beam",
    "BATTLE_EFFECT_LOWER_DEFENSE_HIT": "crunch",
    "BATTLE_EFFECT_LOWER_SPEED_HIT": "icy_wind",
    "BATTLE_EFFECT_LOWER_SP_ATK_HIT": "mist_ball",
    "BATTLE_EFFECT_LOWER_SP_DEF_HIT": "psychic",
    "BATTLE_EFFECT_LOWER_ACCURACY_HIT": "mud_slap",
    "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT": "giga_drain",
    "BATTLE_EFFECT_RECOIL_THIRD": "brave_bird",
    "BATTLE_EFFECT_RECOIL_HALF": "head_smash",
    "BATTLE_EFFECT_RECOIL_QUARTER": "take_down",
    "BATTLE_EFFECT_THAW_AND_BURN_HIT": "flame_wheel",
}

PHYSICAL_DONORS = {
    "Normal": "strength",
    "Fire": "fire_punch",
    "Water": "aqua_tail",
    "Electric": "thunder_punch",
    "Grass": "leaf_blade",
    "Ice": "ice_punch",
    "Fighting": "brick_break",
    "Poison": "poison_jab",
    "Ground": "earthquake",
    "Flying": "aerial_ace",
    "Psychic": "zen_headbutt",
    "Bug": "x_scissor",
    "Rock": "rock_slide",
    "Ghost": "shadow_claw",
    "Dragon": "dragon_claw",
    "Dark": "crunch",
    "Steel": "iron_head",
    "Fairy": "cut",
}

SPECIAL_DONORS = {
    "Normal": "swift",
    "Fire": "flamethrower",
    "Water": "water_pulse",
    "Electric": "thunderbolt",
    "Grass": "energy_ball",
    "Ice": "ice_beam",
    "Fighting": "aura_sphere",
    "Poison": "sludge_bomb",
    "Ground": "earth_power",
    "Flying": "air_slash",
    "Psychic": "psychic",
    "Bug": "signal_beam",
    "Rock": "power_gem",
    "Ghost": "shadow_ball",
    "Dragon": "dragon_pulse",
    "Dark": "dark_pulse",
    "Steel": "flash_cannon",
    "Fairy": "magical_leaf",
}

TYPE_CONTEST = {
    "Normal": "CONTEST_TYPE_CUTE",
    "Fire": "CONTEST_TYPE_BEAUTY",
    "Water": "CONTEST_TYPE_BEAUTY",
    "Electric": "CONTEST_TYPE_COOL",
    "Grass": "CONTEST_TYPE_SMART",
    "Ice": "CONTEST_TYPE_BEAUTY",
    "Fighting": "CONTEST_TYPE_COOL",
    "Poison": "CONTEST_TYPE_SMART",
    "Ground": "CONTEST_TYPE_TOUGH",
    "Flying": "CONTEST_TYPE_COOL",
    "Psychic": "CONTEST_TYPE_SMART",
    "Bug": "CONTEST_TYPE_SMART",
    "Rock": "CONTEST_TYPE_TOUGH",
    "Ghost": "CONTEST_TYPE_SMART",
    "Dragon": "CONTEST_TYPE_COOL",
    "Dark": "CONTEST_TYPE_SMART",
    "Steel": "CONTEST_TYPE_TOUGH",
    "Fairy": "CONTEST_TYPE_CUTE",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def empty(value: str | None) -> bool:
    if value is None:
        return True
    return value.strip().lower() in {"", "none", "no", "n/a"}


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def load_translations(path: Path) -> dict[str, str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        token: record["english_name"]
        for token, record in data.get("moves", {}).items()
        if record.get("english_name")
    }


def sanitize_text(value: str) -> str:
    value = value.replace("'", "’")
    value = value.replace("“", '"').replace("”", '"').replace("–", "-").replace("—", "-")
    # Keep Platinum-supported smart apostrophe while transliterating accented
    # Latin text so msgenc does not encounter unsupported community characters.
    marker = "__APOS__"
    value = value.replace("’", marker)
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.replace(marker, "’")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def description_lines(value: str) -> list[str]:
    text = sanitize_text(value)
    if not text:
        text = "A community-designed move."
    wrapped = textwrap.wrap(text, width=27, break_long_words=False, break_on_hyphens=False)
    if len(wrapped) > 5:
        wrapped = wrapped[:5]
        if not wrapped[-1].endswith("."):
            wrapped[-1] = wrapped[-1].rstrip(" ,;:") + "."
    return [line + "\n" for line in wrapped]


def parse_int(value: str, default: int = 0) -> int:
    value = (value or "").strip()
    if not value:
        return default
    match = re.search(r"-?\d+", value)
    return int(match.group(0)) if match else default


def parse_priority(detail: dict[str, str], source: dict[str, str]) -> int:
    text = " ".join([
        detail.get("priority", ""),
        source.get("secondary_effect", ""),
        source.get("tags", ""),
    ])
    match = re.search(r"(?:priority|prio)[^\d+-]*([+-]?\d+)", text, re.I)
    if match:
        return int(match.group(1))
    match = re.search(r"([+-]\d+)\s*(?:priority|prio)", text, re.I)
    return int(match.group(1)) if match else 0


def parse_chance(detail: dict[str, str], source: dict[str, str]) -> int:
    # Prefer the source record's structured secondary field over prose when
    # both exist; this avoids known description/config disagreements.
    for text in (
        source.get("secondary_effect", ""),
        detail.get("effect_chance", ""),
        detail.get("status_effects", ""),
        detail.get("stat_changes", ""),
        detail.get("what_it_does", ""),
    ):
        match = re.search(r"(\d+)\s*%", text or "")
        if match:
            return int(match.group(1))
    return 0


def map_target(value: str) -> str | None:
    value = value.casefold().replace("pokemon", "pokémon").strip()
    if value in {
        "one target", "one target other than the user", "one adjacent pokémon",
        "one adjacent target", "one pokémon other than the user",
        "one adjacent pokémon (nearother)",
    }:
        return "RANGE_SINGLE_TARGET"
    if "random adjacent foe" in value or "random opposing" in value:
        return "RANGE_RANDOM_OPPONENT"
    if value in {"all adjacent foes", "all opposing pokémon", "both opposing pokémon"} or "spread target" in value:
        return "RANGE_ADJACENT_OPPONENTS"
    if value in {
        "all adjacent pokémon", "all adjacent pokémon except the user",
        "all nearby pokémon except the user", "all pokémon except the user",
    }:
        return "RANGE_ALL_ADJACENT"
    if value in {"user", "the user"}:
        return "RANGE_USER"
    if value in {"user's side", "user / user's side"}:
        return "RANGE_USER_SIDE"
    if value in {"opposing side", "the opposing side"}:
        return "RANGE_OPPONENT_SIDE"
    if value in {"entire battlefield", "battlefield", "both sides of the field"}:
        return "RANGE_FIELD"
    return None


def secondary_effect(detail: dict[str, str], source: dict[str, str]) -> str | None:
    status = (detail.get("status_effects") or "").casefold()
    stats = (detail.get("stat_changes") or "").casefold()
    multi = (detail.get("multi_hit_or_duration") or "").casefold()
    recoil = (detail.get("recoil") or "").casefold()
    drain = (detail.get("drain_or_healing") or "").casefold()
    secondary = (source.get("secondary_effect") or "").casefold()

    combined = " ".join([status, stats, multi, recoil, drain, secondary])

    if "frostbite" in combined or "bleed" in combined or "petrif" in combined:
        return None

    if not empty(recoil):
        if "25%" in recoil:
            return "BATTLE_EFFECT_RECOIL_QUARTER"
        if "33%" in recoil or "one-third" in recoil or "1/3" in recoil:
            return "BATTLE_EFFECT_RECOIL_THIRD"
        if "50%" in recoil or "half" in recoil:
            return "BATTLE_EFFECT_RECOIL_HALF"
        return None

    if not empty(drain):
        if "50% of damage" in drain or "half of damage" in drain:
            return "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT"
        return None

    if not empty(multi):
        if re.search(r"2.?5 hits", multi):
            return "BATTLE_EFFECT_MULTI_HIT"
        if "two hits" in multi or "2 hits" in multi:
            return "BATTLE_EFFECT_HIT_TWICE"
        if ("exactly 3 hits" in multi or "three hits" in multi) and "critical" not in multi and "increasing" not in multi:
            return "BATTLE_EFFECT_HIT_THREE_TIMES"
        return None

    # Source secondary text is useful for collections whose audit columns are
    # sparse. Only map effects Platinum already supports directly.
    for text in (status, secondary):
        if "burn" in text and not re.search(r"frostbite|paraly|poison|freeze|sleep|confus|\bor\b", text):
            return "BATTLE_EFFECT_BURN_HIT"
        if "paraly" in text and not re.search(r"burn|poison|freeze|sleep|confus|\bor\b", text):
            return "BATTLE_EFFECT_PARALYZE_HIT"
        if "badly poison" in text:
            return "BATTLE_EFFECT_BADLY_POISON_HIT"
        if "poison" in text and not re.search(r"burn|paraly|freeze|sleep|confus|\bor\b", text):
            return "BATTLE_EFFECT_POISON_HIT"
        if re.search(r"\bfreeze", text) and not re.search(r"frostbite|burn|paraly|poison|sleep|confus|\bor\b", text):
            return "BATTLE_EFFECT_FREEZE_HIT"
        if "confus" in text and "user" not in text:
            return "BATTLE_EFFECT_CONFUSE_HIT"
        if "flinch" in text:
            return "BATTLE_EFFECT_FLINCH_HIT"

    for text in (stats, secondary):
        if re.search(r"target.*speed.*(?:-1|lower)", text):
            return "BATTLE_EFFECT_LOWER_SPEED_HIT"
        if re.search(r"target.*defense.*(?:-1|lower)", text):
            return "BATTLE_EFFECT_LOWER_DEFENSE_HIT"
        if re.search(r"target.*sp\.?\s*atk.*(?:-1|lower)", text):
            return "BATTLE_EFFECT_LOWER_SP_ATK_HIT"
        if re.search(r"target.*sp\.?\s*def.*(?:-1|lower)", text):
            return "BATTLE_EFFECT_LOWER_SP_DEF_HIT"
        if re.search(r"target.*accuracy.*(?:-1|lower)", text):
            return "BATTLE_EFFECT_LOWER_ACCURACY_HIT"
        if re.search(r"target.*attack.*(?:-1|lower)", text):
            return "BATTLE_EFFECT_LOWER_ATTACK_HIT"
        if re.search(r"user.*attack.*(?:\+1|raise)", text) and not re.search(r"defense|sp\.|speed|accuracy|evasion", text):
            return "BATTLE_EFFECT_RAISE_ATTACK_HIT"
        if re.search(r"user.*defense.*(?:\+1|raise)", text) and not re.search(r"attack|sp\.|speed|accuracy|evasion", text):
            return "BATTLE_EFFECT_RAISE_DEF_HIT"
        if re.search(r"user.*sp\.?\s*atk.*(?:\+1|raise)", text) and not re.search(r"sp\.?\s*def|attack|defense|speed|accuracy|evasion", text):
            return "BATTLE_EFFECT_RAISE_SP_ATK_HIT"
        if "all" in text and "stat" in text and ("raise" in text or "+1" in text):
            return "BATTLE_EFFECT_RAISE_ALL_STATS_HIT"

    return "NONE"


def map_effect(detail: dict[str, str], source: dict[str, str]) -> str | None:
    primary = (source.get("primary_effect") or "").strip()
    category = detail.get("category", "")

    if primary in DIRECT_EFFECTS:
        return DIRECT_EFFECTS[primary]

    if primary == "RaiseUserSpeed1":
        return "BATTLE_EFFECT_SPEED_UP" if category == "Status" else None
    if primary == "RaiseUserAttack1":
        return "BATTLE_EFFECT_ATK_UP" if category == "Status" else "BATTLE_EFFECT_RAISE_ATTACK_HIT"
    if primary == "RemoveScreens":
        return "BATTLE_EFFECT_REMOVE_SCREENS"
    if primary == "PowerHigherWithUserHP":
        return "BATTLE_EFFECT_INCREASE_POWER_WITH_MORE_HP"
    if primary in {"Drains 50% of damage dealt", "HealUserByHalfOfDamageDone"}:
        return "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT"
    if primary == "RecoilThirdOfDamageDealt":
        return "BATTLE_EFFECT_RECOIL_THIRD"
    if primary == "Damages and lowers Speed":
        return "BATTLE_EFFECT_LOWER_SPEED_HIT"
    if primary in {"damage; priority 1", "Damage; +1 priority", "Priority +1 damage"}:
        return "BATTLE_EFFECT_HIT"
    if re.fullmatch(r"Hits 2.?5 times", primary, re.I):
        return "BATTLE_EFFECT_MULTI_HIT"
    if primary == "Spread damage to all adjacent foes":
        return "BATTLE_EFFECT_HIT"
    if re.fullmatch(r"Rampages for 2.?3 turns, then confuses the user", primary, re.I):
        return "BATTLE_EFFECT_CONTINUE_AND_CONFUSE_SELF"
    if primary == "High-power damage; sharply lowers the user's Sp. Atk":
        return "BATTLE_EFFECT_USER_SP_ATK_DOWN_2"
    if primary == "Damages and traps the target for residual damage":
        return "BATTLE_EFFECT_BIND_HIT"
    if primary == "User switches out after dealing damage":
        return "BATTLE_EFFECT_SWITCH_HIT"
    if primary == "Damage; user must recharge next turn":
        return "BATTLE_EFFECT_RECHARGE_AFTER"
    if primary == "Damage; doubles in power when the target is at half HP or less":
        return "BATTLE_EFFECT_DOUBLE_POWER_WHEN_BELOW_HALF"
    if primary == "Raises the user's critical-hit rate":
        return "BATTLE_EFFECT_CRIT_UP_2"
    if primary == "Applies a recurring self-heal effect":
        return "BATTLE_EFFECT_RESTORE_HP_EVERY_TURN"
    if primary == "AddToxicSpikesToFoeSide":
        return "BATTLE_EFFECT_TOXIC_SPIKES"

    prefix_map = {
        "FunctionCode LowerTargetSpeed1;": "BATTLE_EFFECT_LOWER_SPEED_HIT",
        "FunctionCode LowerTargetSpDef1;": "BATTLE_EFFECT_LOWER_SP_DEF_HIT",
        "FunctionCode LowerTargetSpAtk1;": "BATTLE_EFFECT_LOWER_SP_ATK_HIT",
        "FunctionCode LowerTargetAttack1;": "BATTLE_EFFECT_LOWER_ATTACK_HIT",
        "FunctionCode LowerTargetDefense1;": "BATTLE_EFFECT_LOWER_DEFENSE_HIT",
        "FunctionCode ParalyzeTarget;": "BATTLE_EFFECT_PARALYZE_HIT",
        "FunctionCode FlinchTarget;": "BATTLE_EFFECT_FLINCH_HIT",
        "FunctionCode AlwaysCriticalHit;": "BATTLE_EFFECT_HIGH_CRITICAL",
        "FunctionCode UserFaintsExplosive;": "BATTLE_EFFECT_HALVE_DEFENSE",
        "FunctionCode HealUserByHalfOfDamageDone;": "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT",
    }
    for prefix, effect in prefix_map.items():
        if primary.startswith(prefix):
            return effect

    if primary.startswith("FunctionCode BurnTarget;"):
        flags = detail.get("move_flags", "")
        return "BATTLE_EFFECT_THAW_AND_BURN_HIT" if "ThawsUser" in flags else "BATTLE_EFFECT_BURN_HIT"

    if primary.startswith("FunctionCode RaiseUserSpAtk1;"):
        return "BATTLE_EFFECT_SP_ATK_UP" if category == "Status" else "BATTLE_EFFECT_RAISE_SP_ATK_HIT"

    if primary.lower().startswith("damage/status per pbs record;"):
        low = primary.casefold()
        if "never misses" in low:
            return "BATTLE_EFFECT_BYPASS_ACCURACY"
        if "critical hits land more easily" in low:
            return "BATTLE_EFFECT_HIGH_CRITICAL"
        sec = secondary_effect(detail, source)
        return "BATTLE_EFFECT_HIT" if sec == "NONE" else sec

    # Plain-data source families are accepted only when their structured audit
    # fields describe a single native secondary effect or truly plain damage.
    if primary in {"Damage", "damage", "None", "High-power damage"}:
        sec = secondary_effect(detail, source)
        if sec != "NONE":
            return sec

        text = " ".join([
            detail.get("what_it_does", ""),
            detail.get("source_description", ""),
            source.get("secondary_effect", ""),
        ]).casefold()
        risky = re.compile(
            r"double|critical|ignores|cannot miss|never miss|based on|depends|"
            r"increases with|decreases with|recharge|faint|trap|switch|screen|"
            r"protect|weather|terrain|field|held|berry|item|ability|type|form|"
            r"consecutive|half hp|recover|heal|drain|recoil|rampage|confus|"
            r"burn|poison|paraly|freeze|sleep|flinch|infatu|curse|leech|seed|"
            r"torment|taunt|disable|encore|smack down|grounds"
        )
        if not risky.search(text):
            return "BATTLE_EFFECT_HIT"

    return None


def unsupported_extra(detail: dict[str, str], source: dict[str, str]) -> str | None:
    flags = (detail.get("move_flags") or "").casefold()
    text = " ".join([
        detail.get("what_it_does", ""),
        detail.get("source_description", ""),
        source.get("secondary_effect", ""),
        source.get("notes", ""),
    ]).casefold()

    if not empty(detail.get("field_weather_terrain_behavior")):
        return "field/weather/terrain behavior"
    if not empty(detail.get("switching_behavior")):
        # Native U-turn-style switching is already represented by SWITCH_HIT.
        if "switch" not in (source.get("primary_effect") or "").casefold():
            return "extra switching behavior"

    flag_blockers = {
        "ignores-stat-stages": "ignores stat stages",
        "dual-type-effect": "dynamic/dual type behavior",
        "anti-flying": "anti-flying behavior",
        "ignores-protect": "ignores Protect",
        "form-change": "form change",
        "contact-retaliation": "contact retaliation",
        "mechanics-audit-needed": "unresolved source mechanic",
    }
    for needle, reason in flag_blockers.items():
        if needle in flags:
            return reason

    if "uses target sp. def" in text or "against the target's special defense" in text:
        return "uses nonstandard defensive stat"
    if "protects against non-fire" in text or "attackers that trigger its protection" in text:
        return "custom Protect rider"
    if "never misses in fog" in text:
        return "conditional fog accuracy"
    if "changes the user's form" in text or "toggles" in text and "form" in text:
        return "form change"
    if "high critical" in text and "paraly" in text:
        return "combined high-crit/paralysis effect"
    if "+1 crit" in text and "burn" in text:
        # Platinum has an exact high-crit + burn effect.
        return None
    if "+1 crit" in text and "poison" in text:
        # Platinum has an exact high-crit + poison effect.
        return None
    return None


def map_target_or_reason(detail: dict[str, str]) -> tuple[str | None, str | None]:
    target = map_target(detail.get("target", ""))
    if target is None:
        return None, f"unsupported target: {detail.get('target', '')}"
    return target, None


def choose_donor(
    source: dict[str, str],
    effect: str,
    category: str,
    move_type: str,
    pt_root: Path,
) -> str:
    # Preserve an explicit Gen-1-4 source reuse whenever that donor is actually
    # present in native pokeplatinum.
    ref = (source.get("animation_reference") or "").strip()
    if re.fullmatch(r"MOVE_[A-Z0-9_]+", ref):
        stem = ref.removeprefix("MOVE_").lower()
        if (pt_root / "res" / "moves" / stem / "anim.s").is_file():
            return stem

    donor = EFFECT_DONORS.get(effect)
    if donor and (pt_root / "res" / "moves" / donor / "anim.s").is_file():
        return donor

    table = PHYSICAL_DONORS if category == "Physical" else SPECIAL_DONORS
    donor = table.get(move_type, "swift")
    if not (pt_root / "res" / "moves" / donor / "anim.s").is_file():
        raise SystemExit(f"native donor missing: {donor}")
    return donor


def flags_for(detail: dict[str, str], source: dict[str, str], target: str, effect: str) -> list[str]:
    result: list[str] = []
    raw = " ".join([detail.get("move_flags", ""), source.get("tags", "")]).casefold()

    if detail.get("contact", "").strip().casefold() == "yes" or "contact" in raw:
        result.append("MOVE_FLAG_MAKES_CONTACT")

    if target in {
        "RANGE_SINGLE_TARGET", "RANGE_RANDOM_OPPONENT",
        "RANGE_ADJACENT_OPPONENTS", "RANGE_ALL_ADJACENT",
    }:
        result.append("MOVE_FLAG_CAN_PROTECT")

    if "mirror" in raw:
        result.append("MOVE_FLAG_CAN_MIRROR_MOVE")
    if "magic-coat" in raw or "magic coat" in raw:
        result.append("MOVE_FLAG_CAN_MAGIC_COAT")
    if "snatch" in raw:
        result.append("MOVE_FLAG_CAN_SNATCH")

    # Normal damaging attacks should retain King's Rock compatibility unless
    # they already carry their own flinch behavior.
    if detail.get("category") != "Status" and effect != "BATTLE_EFFECT_FLINCH_HIT":
        result.append("MOVE_FLAG_TRIGGERS_KINGS_ROCK")

    return list(dict.fromkeys(result))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_root", type=Path)
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--start-id", type=int, required=True)
    ap.add_argument("--existing-batch", action="append", type=Path, default=[])
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--deferred", type=Path, required=True)
    args = ap.parse_args()

    source_root = args.source_root.resolve()
    pt_root = args.pokeplatinum_root.resolve()

    community = read_csv(source_root / "manifests" / "community_moves.csv")
    details_rows = read_csv(source_root / "manifests" / "FULL_MOVE_APPROVAL_DETAILS.csv")
    details = {row["move_id"]: row for row in details_rows}
    translations = load_translations(source_root / "docs" / "approval" / "translations.json")

    existing_tokens: set[str] = set()
    for path in args.existing_batch:
        data = json.loads(path.read_text(encoding="utf-8"))
        existing_tokens.update(move["token"] for move in data.get("moves", []))

    hold_norm = {normalize_name(name) for name in HOLD_NAMES}
    emitted: list[dict] = []
    deferred: list[dict] = []

    for source in community:
        token = source["move_id"]
        detail = details.get(token)
        if detail is None:
            deferred.append({"token": token, "reason": "missing full mechanics audit"})
            continue
        if token in existing_tokens:
            continue

        display_name = translations.get(token, detail.get("english_review_name") or source["move_name"])
        if normalize_name(display_name) in hold_norm or normalize_name(source["move_name"]) in hold_norm:
            deferred.append({"token": token, "name": display_name, "reason": "duplicate/redesign hold"})
            continue
        if token in HOLD_TOKENS:
            deferred.append({"token": token, "name": display_name, "reason": "known composite mechanic"})
            continue
        if detail.get("type") not in CANONICAL_TYPES:
            deferred.append({"token": token, "name": display_name, "reason": f"custom type: {detail.get('type')}"})
            continue

        extra = unsupported_extra(detail, source)
        if extra:
            deferred.append({"token": token, "name": display_name, "reason": extra})
            continue

        effect = map_effect(detail, source)
        if effect is None:
            deferred.append({"token": token, "name": display_name, "reason": "no exact native Platinum effect mapping"})
            continue

        target, target_reason = map_target_or_reason(detail)
        if target_reason:
            deferred.append({"token": token, "name": display_name, "reason": target_reason})
            continue
        assert target is not None

        move_id = args.start_id + len(emitted)
        if move_id > COMMUNITY_END:
            raise SystemExit(
                f"native-compatible bulk would exceed community lane: {move_id} > {COMMUNITY_END}"
            )

        category = detail["category"]
        if category not in {"Physical", "Special", "Status"}:
            deferred.append({"token": token, "name": display_name, "reason": f"unknown category: {category}"})
            continue

        # Exact native combined effects already present in Platinum.
        low_text = " ".join([
            detail.get("what_it_does", ""),
            source.get("secondary_effect", ""),
        ]).casefold()
        if "+1 crit" in low_text and "burn" in low_text:
            effect = "BATTLE_EFFECT_HIGH_CRITICAL_BURN_HIT"
        elif "+1 crit" in low_text and "poison" in low_text:
            effect = "BATTLE_EFFECT_HIGH_CRITICAL_POISON_HIT"

        chance = parse_chance(detail, source)
        if effect in {
            "BATTLE_EFFECT_HIT", "BATTLE_EFFECT_REMOVE_SCREENS",
            "BATTLE_EFFECT_SWITCH_HIT", "BATTLE_EFFECT_HALVE_DEFENSE",
            "BATTLE_EFFECT_BYPASS_ACCURACY", "BATTLE_EFFECT_HIGH_CRITICAL",
            "BATTLE_EFFECT_BIND_HIT", "BATTLE_EFFECT_RECHARGE_AFTER",
            "BATTLE_EFFECT_CONTINUE_AND_CONFUSE_SELF",
            "BATTLE_EFFECT_DOUBLE_POWER_WHEN_BELOW_HALF",
            "BATTLE_EFFECT_INCREASE_POWER_WITH_MORE_HP",
            "BATTLE_EFFECT_ATK_DEF_DOWN", "BATTLE_EFFECT_USER_SP_ATK_DOWN_2",
            "BATTLE_EFFECT_HIT_THREE_TIMES", "BATTLE_EFFECT_MULTI_HIT",
            "BATTLE_EFFECT_HIT_TWICE", "BATTLE_EFFECT_CRASH_ON_MISS",
            "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT", "BATTLE_EFFECT_RECOIL_THIRD",
            "BATTLE_EFFECT_RECOIL_HALF", "BATTLE_EFFECT_RECOIL_QUARTER",
            "BATTLE_EFFECT_PROTECT", "BATTLE_EFFECT_STEALTH_ROCK",
            "BATTLE_EFFECT_TOXIC_SPIKES", "BATTLE_EFFECT_RESTORE_HP_EVERY_TURN",
            "BATTLE_EFFECT_SPEED_UP", "BATTLE_EFFECT_ATK_UP",
            "BATTLE_EFFECT_SP_ATK_UP", "BATTLE_EFFECT_CRIT_UP_2",
        }:
            chance = 0

        donor = choose_donor(source, effect, category, detail["type"], pt_root)

        description = detail.get("what_it_does") or detail.get("source_description") or source.get("notes") or ""
        provenance = (
            f"{source.get('source_project')} / {source.get('source_repo')} "
            f"@ {source.get('source_commit')}"
        )

        emitted.append({
            "id": move_id,
            "token": token,
            "name": sanitize_text(display_name),
            "type": f"TYPE_{detail['type'].upper()}",
            "class": f"CLASS_{category.upper()}",
            "power": parse_int(detail.get("power", ""), 0),
            "accuracy": parse_int(detail.get("accuracy", ""), 0),
            "pp": parse_int(detail.get("pp", ""), 5),
            "effect": {"type": effect, "chance": chance},
            "range": target,
            "priority": parse_priority(detail, source),
            "flags": flags_for(detail, source, target, effect),
            "contest": {
                "effect": "CONTEST_EFFECT_BASIC",
                "type": TYPE_CONTEST[detail["type"]],
            },
            "description": description_lines(description),
            "animation": {
                "mode": "copy_native_platinum",
                "donor_move": donor,
            },
            "traits": [
                part.strip().casefold().replace("_", "-")
                for part in re.split(r"[;,]", source.get("tags", ""))
                if part.strip()
            ],
            "provenance": provenance,
            "source_library_commit": SOURCE_COMMIT,
        })

    batch = {
        "schema_version": 1,
        "lane": "community_imports",
        "start_id": args.start_id,
        "source_library": "lionsprideemb-tech/Pokemon-moves",
        "source_commit": SOURCE_COMMIT,
        "source_manifest": "manifests/community_moves.csv",
        "batch": "CM06_NATIVE_COMPATIBLE_BULK",
        "selection_policy": (
            "Only moves representable with existing native Platinum battle effects "
            "and standard move-table fields; no custom mechanic approximation."
        ),
        "moves": emitted,
    }
    args.output.write_text(json.dumps(batch, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    reason_counts: dict[str, int] = {}
    for item in deferred:
        reason_counts[item["reason"]] = reason_counts.get(item["reason"], 0) + 1

    report = {
        "gate": "CM06_NATIVE_COMPATIBLE_SELECTION",
        "source_commit": SOURCE_COMMIT,
        "source_move_count": len(community),
        "existing_tokens_excluded": len(existing_tokens),
        "native_compatible_emitted": len(emitted),
        "first_id": emitted[0]["id"] if emitted else None,
        "last_id": emitted[-1]["id"] if emitted else None,
        "deferred_count": len(deferred),
        "deferred_reason_counts": dict(sorted(reason_counts.items())),
        "deferred": deferred,
    }
    args.deferred.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({
        "native_compatible_emitted": len(emitted),
        "first_id": report["first_id"],
        "last_id": report["last_id"],
        "deferred_count": len(deferred),
        "deferred_reason_counts": report["deferred_reason_counts"],
    }, indent=2))


if __name__ == "__main__":
    main()
