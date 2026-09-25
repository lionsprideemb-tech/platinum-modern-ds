#!/usr/bin/env python3
"""Build the bulk community-move batch that needs no new Platinum mechanics.

The source catalog has already been mechanics-audited. This selector is deliberately
conservative: a move is admitted only when its complete audited behavior can be
represented by an existing pokeplatinum battle effect, target range, priority and
ordinary move flags. Anything with a custom status, field rule, conditional power,
new targeting rule or other extra behavior stays deferred for the later mechanics
review.

Animation choice is independent of mechanics. If the source already points at a
Gen 1-4 Platinum move, that native animation is reused. Otherwise a type/category
native-Platinum visual baseline is assigned so the move is runnable while the
separate animation review remains free to replace it later.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import textwrap
from pathlib import Path

TYPE_MAP = {
    "Normal": "TYPE_NORMAL",
    "Fire": "TYPE_FIRE",
    "Water": "TYPE_WATER",
    "Electric": "TYPE_ELECTRIC",
    "Grass": "TYPE_GRASS",
    "Ice": "TYPE_ICE",
    "Fighting": "TYPE_FIGHTING",
    "Poison": "TYPE_POISON",
    "Ground": "TYPE_GROUND",
    "Flying": "TYPE_FLYING",
    "Psychic": "TYPE_PSYCHIC",
    "Bug": "TYPE_BUG",
    "Rock": "TYPE_ROCK",
    "Ghost": "TYPE_GHOST",
    "Dragon": "TYPE_DRAGON",
    "Dark": "TYPE_DARK",
    "Steel": "TYPE_STEEL",
    "Fairy": "TYPE_FAIRY",
}

CLASS_MAP = {
    "Physical": "CLASS_PHYSICAL",
    "Special": "CLASS_SPECIAL",
    "Status": "CLASS_STATUS",
}

CONTEST_BY_CLASS = {
    "Physical": "CONTEST_TYPE_TOUGH",
    "Special": "CONTEST_TYPE_BEAUTY",
    "Status": "CONTEST_TYPE_SMART",
}

FALLBACK_ANIM = {
    ("Normal", "Physical"): "strength",
    ("Normal", "Special"): "swift",
    ("Normal", "Status"): "growl",
    ("Fire", "Physical"): "fire_punch",
    ("Fire", "Special"): "flamethrower",
    ("Fire", "Status"): "sunny_day",
    ("Water", "Physical"): "aqua_tail",
    ("Water", "Special"): "surf",
    ("Water", "Status"): "rain_dance",
    ("Electric", "Physical"): "thunder_punch",
    ("Electric", "Special"): "thunderbolt",
    ("Electric", "Status"): "thunder_wave",
    ("Grass", "Physical"): "leaf_blade",
    ("Grass", "Special"): "energy_ball",
    ("Grass", "Status"): "synthesis",
    ("Ice", "Physical"): "ice_punch",
    ("Ice", "Special"): "ice_beam",
    ("Ice", "Status"): "hail",
    ("Fighting", "Physical"): "close_combat",
    ("Fighting", "Special"): "aura_sphere",
    ("Fighting", "Status"): "bulk_up",
    ("Poison", "Physical"): "poison_jab",
    ("Poison", "Special"): "sludge_bomb",
    ("Poison", "Status"): "toxic",
    ("Ground", "Physical"): "earthquake",
    ("Ground", "Special"): "earth_power",
    ("Ground", "Status"): "sandstorm",
    ("Flying", "Physical"): "aerial_ace",
    ("Flying", "Special"): "air_slash",
    ("Flying", "Status"): "tailwind",
    ("Psychic", "Physical"): "zen_headbutt",
    ("Psychic", "Special"): "psychic",
    ("Psychic", "Status"): "calm_mind",
    ("Bug", "Physical"): "x_scissor",
    ("Bug", "Special"): "signal_beam",
    ("Bug", "Status"): "string_shot",
    ("Rock", "Physical"): "rock_slide",
    ("Rock", "Special"): "power_gem",
    ("Rock", "Status"): "rock_polish",
    ("Ghost", "Physical"): "shadow_claw",
    ("Ghost", "Special"): "shadow_ball",
    ("Ghost", "Status"): "confuse_ray",
    ("Dragon", "Physical"): "dragon_claw",
    ("Dragon", "Special"): "dragon_pulse",
    ("Dragon", "Status"): "dragon_dance",
    ("Dark", "Physical"): "crunch",
    ("Dark", "Special"): "dark_pulse",
    ("Dark", "Status"): "nasty_plot",
    ("Steel", "Physical"): "iron_head",
    ("Steel", "Special"): "flash_cannon",
    ("Steel", "Status"): "iron_defense",
    ("Fairy", "Physical"): "return",
    ("Fairy", "Special"): "aurora_beam",
    ("Fairy", "Status"): "charm",
}

EXPLICIT_EFFECT_MAP = {
    "EFFECT_HIT": "BATTLE_EFFECT_HIT",
    "EFFECT_POISON_HIT": "BATTLE_EFFECT_POISON_HIT",
    "EFFECT_BURN_HIT": "BATTLE_EFFECT_BURN_HIT",
    "EFFECT_FREEZE_HIT": "BATTLE_EFFECT_FREEZE_HIT",
    "EFFECT_PARALYZE_HIT": "BATTLE_EFFECT_PARALYZE_HIT",
    "EFFECT_FLINCH_HIT": "BATTLE_EFFECT_FLINCH_HIT",
    "EFFECT_MULTI_HIT": "BATTLE_EFFECT_MULTI_HIT",
    "EFFECT_CONFUSE_HIT": "BATTLE_EFFECT_CONFUSE_HIT",
    "EFFECT_DEFENSE_DOWN_HIT": "BATTLE_EFFECT_LOWER_DEFENSE_HIT",
    "EFFECT_SPECIAL_ATTACK_DOWN_HIT": "BATTLE_EFFECT_LOWER_SP_ATK_HIT",
    "EFFECT_SPEED_DOWN_HIT": "BATTLE_EFFECT_LOWER_SPEED_HIT",
    "EFFECT_ATTACK_DOWN_HIT": "BATTLE_EFFECT_LOWER_ATTACK_HIT",
    "EFFECT_SPECIAL_DEFENSE_DOWN_HIT": "BATTLE_EFFECT_LOWER_SP_DEF_HIT",
    "EFFECT_ACCURACY_DOWN_HIT": "BATTLE_EFFECT_LOWER_ACCURACY_HIT",
    "EFFECT_ATTACK_UP_HIT": "BATTLE_EFFECT_RAISE_ATTACK_HIT",
    "EFFECT_DEFENSE_UP_HIT": "BATTLE_EFFECT_RAISE_DEF_HIT",
    "EFFECT_SPECIAL_ATTACK_UP_HIT": "BATTLE_EFFECT_RAISE_SP_ATK_HIT",
    "EFFECT_ALL_STATS_UP_HIT": "BATTLE_EFFECT_RAISE_ALL_STATS_HIT",
    "EFFECT_BADLY_POISON_HIT": "BATTLE_EFFECT_BADLY_POISON_HIT",
    "EFFECT_RECOIL_33": "BATTLE_EFFECT_RECOIL_THIRD",
    "EFFECT_RECOIL_THIRD": "BATTLE_EFFECT_RECOIL_THIRD",
    "EFFECT_RECOIL_50": "BATTLE_EFFECT_RECOIL_HALF",
    "EFFECT_RECOIL_HALF": "BATTLE_EFFECT_RECOIL_HALF",
    "EFFECT_PROTECT": "BATTLE_EFFECT_PROTECT",
    "EFFECT_RECOIL_IF_MISS": "BATTLE_EFFECT_CRASH_ON_MISS",
    "EFFECT_HIGH_CRITICAL": "BATTLE_EFFECT_HIGH_CRITICAL",
    "EFFECT_DOUBLE_HIT": "BATTLE_EFFECT_HIT_TWICE",
    "EFFECT_HIT_ESCAPE": "BATTLE_EFFECT_SWITCH_HIT",
    "EFFECT_BRICK_BREAK": "BATTLE_EFFECT_REMOVE_SCREENS",
    "EFFECT_ABSORB": "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT",
    "EFFECT_EXPLOSION": "BATTLE_EFFECT_HALVE_DEFENSE",
    "EFFECT_TRIPLE_KICK": "BATTLE_EFFECT_HIT_THREE_TIMES",
    "EFFECT_SUPERPOWER": "BATTLE_EFFECT_LOWER_OWN_ATK_AND_DEF",
    "EFFECT_OVERHEAT": "BATTLE_EFFECT_USER_SP_ATK_DOWN_2",
    "EFFECT_FACADE": "BATTLE_EFFECT_DOUBLE_POWER_WHEN_STATUSED",
    "EFFECT_STEALTH_ROCK": "BATTLE_EFFECT_STEALTH_ROCK",
    "EFFECT_CLOSE_COMBAT": "BATTLE_EFFECT_DEF_SPD_DOWN_HIT",
    "EFFECT_SUCKER_PUNCH": "BATTLE_EFFECT_HIT_FIRST_IF_TARGET_ATTACKING",
    "EFFECT_DEFOG": "BATTLE_EFFECT_REMOVE_HAZARDS_SCREENS_EVA_DOWN",
}

EFFECT_ALLOWED_DETAIL = {
    "BATTLE_EFFECT_HIT": set(),
    "BATTLE_EFFECT_BYPASS_ACCURACY": set(),
    "BATTLE_EFFECT_HIGH_CRITICAL": set(),
    "BATTLE_EFFECT_POISON_HIT": {"status_effects"},
    "BATTLE_EFFECT_BURN_HIT": {"status_effects"},
    "BATTLE_EFFECT_FREEZE_HIT": {"status_effects"},
    "BATTLE_EFFECT_PARALYZE_HIT": {"status_effects"},
    "BATTLE_EFFECT_CONFUSE_HIT": {"status_effects"},
    "BATTLE_EFFECT_FLINCH_HIT": set(),
    "BATTLE_EFFECT_LOWER_ATTACK_HIT": {"stat_changes"},
    "BATTLE_EFFECT_LOWER_DEFENSE_HIT": {"stat_changes"},
    "BATTLE_EFFECT_LOWER_SPEED_HIT": {"stat_changes"},
    "BATTLE_EFFECT_LOWER_SP_ATK_HIT": {"stat_changes"},
    "BATTLE_EFFECT_LOWER_SP_DEF_HIT": {"stat_changes"},
    "BATTLE_EFFECT_LOWER_ACCURACY_HIT": {"stat_changes"},
    "BATTLE_EFFECT_RAISE_ATTACK_HIT": {"stat_changes"},
    "BATTLE_EFFECT_RAISE_DEF_HIT": {"stat_changes"},
    "BATTLE_EFFECT_RAISE_SP_ATK_HIT": {"stat_changes"},
    "BATTLE_EFFECT_RAISE_ALL_STATS_HIT": {"stat_changes"},
    "BATTLE_EFFECT_MULTI_HIT": {"multi_hit_or_duration"},
    "BATTLE_EFFECT_HIT_TWICE": {"multi_hit_or_duration"},
    "BATTLE_EFFECT_HIT_THREE_TIMES": {"multi_hit_or_duration"},
    "BATTLE_EFFECT_RECOIL_QUARTER": {"recoil"},
    "BATTLE_EFFECT_RECOIL_THIRD": {"recoil"},
    "BATTLE_EFFECT_RECOIL_HALF": {"recoil"},
    "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT": {"drain_or_healing"},
    "BATTLE_EFFECT_SWITCH_HIT": {"switching_behavior"},
    "BATTLE_EFFECT_HALVE_DEFENSE": {"recoil"},
    "BATTLE_EFFECT_REMOVE_SCREENS": set(),
    "BATTLE_EFFECT_PROTECT": set(),
    "BATTLE_EFFECT_CRASH_ON_MISS": set(),
    "BATTLE_EFFECT_BADLY_POISON_HIT": {"status_effects"},
    "BATTLE_EFFECT_DOUBLE_POWER_WHEN_STATUSED": set(),
    "BATTLE_EFFECT_LOWER_OWN_ATK_AND_DEF": {"stat_changes"},
    "BATTLE_EFFECT_USER_SP_ATK_DOWN_2": {"stat_changes"},
    "BATTLE_EFFECT_DEF_SPD_DOWN_HIT": {"stat_changes"},
    "BATTLE_EFFECT_HIT_FIRST_IF_TARGET_ATTACKING": set(),
    "BATTLE_EFFECT_STEALTH_ROCK": {"field_weather_terrain_behavior"},
    "BATTLE_EFFECT_REMOVE_HAZARDS_SCREENS_EVA_DOWN": {"stat_changes", "field_weather_terrain_behavior"},
}

DETAIL_FIELDS = (
    "status_effects",
    "stat_changes",
    "multi_hit_or_duration",
    "recoil",
    "drain_or_healing",
    "switching_behavior",
    "field_weather_terrain_behavior",
)

PLAIN_PRIMARY = {
    "",
    "None",
    "none",
    "Damage",
    "damage",
    "damage/status logic in source record",
    "High-power damage",
    "Spread damage to all adjacent foes",
    "Priority +1 damage",
    "Damage; +1 priority",
    "Damage; +2 priority",
    "Uranium effect code 000",
}

CUSTOM_BLOCK_RE = re.compile(
    r"(frostbite|bleed|drows|petrif|quicksilver|drench|waterlog|inverse room|"
    r"nuclear|blessed field|factory|short-circuit|toxic terrain|third type|"
    r"super[- ]effective|ignores? protect|ignores? .*stat|future sight|"
    r"every[- ]other|cannot be used twice|cannot use twice|loses? .* typing|"
    r"sound moves|follows the user.s type|random type|uses? (?:the )?target.s "
    r"(?:defense|sp\. def|special defense)|sticky terrain|thunderstorm)",
    re.I,
)

TRAIT_WORDS = (
    "strong-jaw",
    "strong jaw",
    "keen-edge",
    "keen edge",
    "iron-fist",
    "iron fist",
    "mega-launcher",
    "mega launcher",
    "horn",
    "arrow",
    "hammer",
    "ballistic",
    "reckless",
    "bone",
    "air",
    "throwing",
    "striker",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean_empty(value: str) -> bool:
    return not value.strip() or value.strip().lower() in {"none", "no", "n/a"}


def normalize_token(token: str) -> str:
    token = re.sub(r"[^A-Z0-9_]", "_", token.upper())
    if not token.startswith("MOVE_"):
        token = "MOVE_" + token
    return token


def map_target(value: str) -> str | None:
    t = value.strip().lower()
    singles = {
        "one target",
        "one target other than the user",
        "one adjacent pokémon",
        "one adjacent pokemon",
        "one adjacent target",
        "one pokémon other than the user",
        "one pokemon other than the user",
        "one adjacent pokémon (nearother)",
    }
    if t in singles:
        return "RANGE_SINGLE_TARGET"
    if "random adjacent" in t or "random opposing" in t:
        return "RANGE_RANDOM_OPPONENT"
    if (
        t in {
            "all adjacent foes",
            "all opposing pokémon",
            "all opposing pokemon",
            "both opposing pokémon",
            "both opposing pokemon",
        }
        or "spread target" in t
    ):
        return "RANGE_ADJACENT_OPPONENTS"
    if t in {
        "all adjacent pokémon",
        "all adjacent pokemon",
        "all nearby pokémon except the user",
        "all nearby pokemon except the user",
        "all pokémon except the user",
        "all pokemon except the user",
    }:
        return "RANGE_ALL_ADJACENT"
    if t in {"user", "the user"}:
        return "RANGE_USER"
    if t in {"user's side", "user / user's side"}:
        return "RANGE_USER_SIDE"
    if t in {"opposing side", "the opposing side"}:
        return "RANGE_OPPONENT_SIDE"
    if t in {"entire battlefield", "battlefield", "both sides of the field"}:
        return "RANGE_FIELD"
    return None


def parse_priority(value: str) -> int:
    match = re.search(r"[-+]?\d+", value)
    return int(match.group()) if match else 0


def parse_int(value: str, default: int = 0) -> int:
    match = re.search(r"-?\d+", value or "")
    return int(match.group()) if match else default


def chance_for(source: dict[str, str], detail: dict[str, str], effect: str) -> int:
    if effect.startswith("BATTLE_EFFECT_STATUS_"):
        return 0
    if effect in {
        "BATTLE_EFFECT_HIT",
        "BATTLE_EFFECT_BYPASS_ACCURACY",
        "BATTLE_EFFECT_HIGH_CRITICAL",
        "BATTLE_EFFECT_MULTI_HIT",
        "BATTLE_EFFECT_HIT_TWICE",
        "BATTLE_EFFECT_HIT_THREE_TIMES",
        "BATTLE_EFFECT_RECOIL_QUARTER",
        "BATTLE_EFFECT_RECOIL_THIRD",
        "BATTLE_EFFECT_RECOIL_HALF",
        "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT",
        "BATTLE_EFFECT_SWITCH_HIT",
        "BATTLE_EFFECT_HALVE_DEFENSE",
        "BATTLE_EFFECT_REMOVE_SCREENS",
        "BATTLE_EFFECT_PROTECT",
        "BATTLE_EFFECT_CRASH_ON_MISS",
        "BATTLE_EFFECT_DOUBLE_POWER_WHEN_STATUSED",
        "BATTLE_EFFECT_LOWER_OWN_ATK_AND_DEF",
        "BATTLE_EFFECT_USER_SP_ATK_DOWN_2",
        "BATTLE_EFFECT_DEF_SPD_DOWN_HIT",
        "BATTLE_EFFECT_HIT_FIRST_IF_TARGET_ATTACKING",
        "BATTLE_EFFECT_STEALTH_ROCK",
        "BATTLE_EFFECT_REMOVE_HAZARDS_SCREENS_EVA_DOWN",
    }:
        return 0

    text = " ".join(
        [
            detail.get("effect_chance", ""),
            source.get("secondary_effect", ""),
            detail.get("status_effects", ""),
            detail.get("stat_changes", ""),
            detail.get("what_it_does", ""),
        ]
    )
    match = re.search(r"(\d+)\s*%", text)
    if match:
        return int(match.group(1))
    if re.search(r"always|100%", text, re.I):
        return 100
    return 0


def infer_generic_effect(detail: dict[str, str]) -> tuple[str | None, str]:
    status = detail.get("status_effects", "")
    stats = detail.get("stat_changes", "")
    multi = detail.get("multi_hit_or_duration", "")
    recoil = detail.get("recoil", "")
    drain = detail.get("drain_or_healing", "")
    switching = detail.get("switching_behavior", "")
    field = detail.get("field_weather_terrain_behavior", "")
    category = detail.get("category", "")
    what = detail.get("what_it_does", "")

    if CUSTOM_BLOCK_RE.search(what):
        return None, "custom-behavior-text"

    populated = [x for x in DETAIL_FIELDS if not clean_empty(detail.get(x, ""))]

    if not clean_empty(field):
        return None, "field-mechanic"

    if not clean_empty(switching):
        if (
            category != "Status"
            and re.search(r"user.*switch|switch.*user|switches? out", switching + " " + what, re.I)
            and len(populated) == 1
        ):
            return "BATTLE_EFFECT_SWITCH_HIT", "inferred-native-switch-hit"
        return None, "switching-mechanic"

    if not clean_empty(recoil):
        if len(populated) != 1:
            return None, "compound-recoil"
        if re.search(r"25%.*damage", recoil, re.I):
            return "BATTLE_EFFECT_RECOIL_QUARTER", "inferred-native-recoil"
        if re.search(r"33%|one.third|1/3", recoil, re.I):
            return "BATTLE_EFFECT_RECOIL_THIRD", "inferred-native-recoil"
        if re.search(r"50%|half", recoil, re.I):
            return "BATTLE_EFFECT_RECOIL_HALF", "inferred-native-recoil"
        if re.search(r"faints? after", recoil, re.I):
            return "BATTLE_EFFECT_HALVE_DEFENSE", "inferred-native-explosion"
        return None, "recoil-mechanic"

    if not clean_empty(drain):
        if len(populated) == 1 and re.search(r"50%|half", drain, re.I):
            return "BATTLE_EFFECT_RECOVER_HALF_DAMAGE_DEALT", "inferred-native-drain"
        return None, "drain-mechanic"

    if not clean_empty(multi):
        if len(populated) != 1:
            return None, "compound-multihit"
        if re.search(r"2.?5 hits", multi, re.I):
            return "BATTLE_EFFECT_MULTI_HIT", "inferred-native-multihit"
        if re.search(r"exactly 3 hits", multi, re.I) and not re.search(
            r"critical|increasing", multi, re.I
        ):
            return "BATTLE_EFFECT_HIT_THREE_TIMES", "inferred-native-three-hit"
        return None, "multihit-mechanic"

    if not clean_empty(status):
        if len(populated) != 1:
            return None, "compound-status"
        hit = category != "Status"
        if re.search(r"badly poison", status, re.I):
            return (
                "BATTLE_EFFECT_BADLY_POISON_HIT"
                if hit
                else "BATTLE_EFFECT_STATUS_BADLY_POISON",
                "inferred-native-status",
            )
        table = (
            ("burn", "BATTLE_EFFECT_BURN_HIT", "BATTLE_EFFECT_STATUS_BURN"),
            ("paraly", "BATTLE_EFFECT_PARALYZE_HIT", "BATTLE_EFFECT_STATUS_PARALYZE"),
            ("poison", "BATTLE_EFFECT_POISON_HIT", "BATTLE_EFFECT_STATUS_POISON"),
            ("confus", "BATTLE_EFFECT_CONFUSE_HIT", "BATTLE_EFFECT_STATUS_CONFUSE"),
            ("freeze", "BATTLE_EFFECT_FREEZE_HIT", None),
        )
        if re.search(r"\bor\b|\band\b", status, re.I):
            return None, "multi-status"
        for needle, hit_effect, status_effect in table:
            if needle in status.lower():
                return (hit_effect if hit else status_effect), "inferred-native-status"
        return None, "custom-status"

    if not clean_empty(stats):
        if len(populated) != 1:
            return None, "compound-stat"
        hit = category != "Status"
        stat_rules = [
            (r"target Speed -1", "BATTLE_EFFECT_LOWER_SPEED_HIT", "BATTLE_EFFECT_SPEED_DOWN"),
            (r"target Defense -1", "BATTLE_EFFECT_LOWER_DEFENSE_HIT", "BATTLE_EFFECT_DEF_DOWN"),
            (r"target Sp\. Atk -1", "BATTLE_EFFECT_LOWER_SP_ATK_HIT", "BATTLE_EFFECT_SP_ATK_DOWN"),
            (r"target Sp\. Def -1", "BATTLE_EFFECT_LOWER_SP_DEF_HIT", "BATTLE_EFFECT_SP_DEF_DOWN"),
            (r"target Accuracy -1", "BATTLE_EFFECT_LOWER_ACCURACY_HIT", "BATTLE_EFFECT_ACC_DOWN"),
            (r"target Attack -1", "BATTLE_EFFECT_LOWER_ATTACK_HIT", "BATTLE_EFFECT_ATK_DOWN"),
            (r"user Attack \+1", "BATTLE_EFFECT_RAISE_ATTACK_HIT", "BATTLE_EFFECT_ATK_UP"),
            (r"user Defense \+1", "BATTLE_EFFECT_RAISE_DEF_HIT", "BATTLE_EFFECT_DEF_UP"),
            (r"user Sp\. Atk \+1", "BATTLE_EFFECT_RAISE_SP_ATK_HIT", "BATTLE_EFFECT_SP_ATK_UP"),
        ]
        for pattern, hit_effect, status_effect in stat_rules:
            if re.search(pattern, stats, re.I):
                if re.search(r"Sp\. Def|Speed|Attack|Defense|Accuracy", stats.replace(re.search(pattern, stats, re.I).group(), ""), re.I):
                    return None, "multi-stat"
                return (hit_effect if hit else status_effect), "inferred-native-stat"
        if not hit and re.search(r"user Sp\. Atk \+2", stats, re.I):
            return "BATTLE_EFFECT_SP_ATK_UP_2", "inferred-native-stat"
        if not hit and re.search(r"user Speed \+1", stats, re.I):
            return "BATTLE_EFFECT_SPEED_UP", "inferred-native-stat"
        return None, "custom-stat"

    lowered = what.lower()
    if re.search(r"high crit|high critical", lowered):
        if not re.search(r"burn|poison|paraly|confus|freeze|frostbite|bleed", lowered):
            return "BATTLE_EFFECT_HIGH_CRITICAL", "inferred-native-high-crit"
        return None, "compound-critical"
    if re.search(r"never misses|cannot miss|without fail|always hits", lowered):
        return "BATTLE_EFFECT_BYPASS_ACCURACY", "inferred-native-never-miss"

    # Remove ordinary interaction-tag prose and priority wording before the
    # final plain-hit check.
    reduced = lowered
    for word in TRAIT_WORDS:
        reduced = reduced.replace(word, "")
    reduced = re.sub(r"[+-]?\d+\s*(?:priority|prio)", "", reduced)
    reduced = re.sub(r"(?:usually|always) goes first", "", reduced)
    blocked = re.compile(
        r"(burn|poison|paraly|confus|freeze|frostbite|bleed|flinch|infatuat|"
        r"sleep|drows|raise|lower|boost.*(?:attack|defense|speed|sp\.)|"
        r"drop.*(?:attack|defense|speed|sp\.)|recoil|heal|drain|switch|"
        r"trap|screen|barrier|hazard|weather|terrain|item|ability|"
        r"double (?:damage|power)|power (?:rises|increases|decreases|depends)|"
        r"based on|if the|when the|every.other|twice|times in a row|"
        r"future sight|fixed damage|one.hit|ohko|half hp|quarter hp)",
        re.I,
    )
    if category != "Status" and not blocked.search(reduced):
        return "BATTLE_EFFECT_HIT", "inferred-native-plain-hit"

    if category == "Status":
        if re.search(r"protects? (?:the )?user|block incoming attacks", lowered):
            return "BATTLE_EFFECT_PROTECT", "inferred-native-protect"
        if re.search(r"sets? rain|starts? rain|summons? rain", lowered):
            return "BATTLE_EFFECT_WEATHER_RAIN", "inferred-native-weather"
        if re.search(r"harsh sunlight|sets? sun|starts? sun", lowered):
            return "BATTLE_EFFECT_WEATHER_SUN", "inferred-native-weather"
        if re.search(r"sets? sandstorm|starts? sandstorm", lowered):
            return "BATTLE_EFFECT_WEATHER_SANDSTORM", "inferred-native-weather"
        if re.search(r"sets? hail|starts? hail", lowered):
            return "BATTLE_EFFECT_WEATHER_HAIL", "inferred-native-weather"
        if re.search(r"stealth rock", lowered):
            return "BATTLE_EFFECT_STEALTH_ROCK", "inferred-native-hazard"
        if re.search(r"toxic spikes", lowered):
            return "BATTLE_EFFECT_TOXIC_SPIKES", "inferred-native-hazard"
        if re.search(r"spikes", lowered):
            return "BATTLE_EFFECT_SET_SPIKES", "inferred-native-hazard"

    return None, "no-native-match"


def detailed_fields_fit(effect: str, detail: dict[str, str]) -> tuple[bool, str]:
    allowed = EFFECT_ALLOWED_DETAIL.get(effect)
    if allowed is None:
        # Native status/weather/stat effects inferred above are safe when their
        # normalized detail was the only special mechanic.
        allowed = set(DETAIL_FIELDS)
    populated = {
        field
        for field in DETAIL_FIELDS
        if not clean_empty(detail.get(field, ""))
    }
    extra = populated - allowed
    if extra:
        return False, "compound-" + "-".join(sorted(extra))
    return True, ""


def sanitize_text(value: str) -> str:
    value = value.replace("\\n", " ").replace("\n", " ")
    value = value.replace("'", "’")
    value = value.replace("—", "-").replace("–", "-")
    value = value.replace("×", "x").replace("½", "half")
    value = value.replace("…", "...")
    value = re.sub(r"\s+", " ", value).strip()
    return value


def description_lines(text: str) -> list[str]:
    clean = sanitize_text(text)
    if not clean:
        clean = "A mysterious move."
    chunks = textwrap.wrap(
        clean,
        width=28,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if len(chunks) > 4:
        chunks = chunks[:4]
        chunks[-1] = chunks[-1].rstrip(" ,;:-") + "..."
    return [line + ("\n" if i < len(chunks) - 1 else "") for i, line in enumerate(chunks)]


def duplicate_blocks(rows: list[dict[str, str]]) -> tuple[set[str], set[str]]:
    blocked: set[str] = set()
    pending: set[str] = set()
    for row in rows:
        names = []
        for part in row["moves"].split("|"):
            part = part.strip()
            part = re.sub(r"^\d+\s+", "", part).strip()
            if part:
                names.append(part)
        decision = row.get("decision", "").strip()
        if not decision:
            pending.update(names)
            continue
        low = decision.lower()
        if "replace both original names" in low:
            blocked.update(names)
        for name in names:
            n = name.lower()
            if f"reject {n}" in low or f"retire {n}" in low:
                blocked.add(name)
            if f"redesign {n}" in low:
                blocked.add(name)
    return blocked, pending


def choose_animation(
    source: dict[str, str],
    detail: dict[str, str],
    pt: Path,
) -> tuple[str, str]:
    ref = source.get("animation_reference", "").strip()
    if re.fullmatch(r"MOVE_[A-Z0-9_]+", ref):
        stem = ref.removeprefix("MOVE_").lower()
        if (pt / "res" / "moves" / stem / "anim.s").is_file():
            return stem, "source-native-platinum-reference"

    fallback = FALLBACK_ANIM[(detail["type"], detail["category"])]
    if not (pt / "res" / "moves" / fallback / "anim.s").is_file():
        fallback = "tackle"
    return fallback, "provisional-native-platinum-baseline"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_root", type=Path)
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--mercury-root", type=Path, default=Path("."))
    ap.add_argument("--start-id", type=int, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    src = args.source_root.resolve()
    pt = args.pokeplatinum_root.resolve()
    mercury = args.mercury_root.resolve()

    community = read_csv(src / "manifests" / "community_moves.csv")
    details = read_csv(src / "manifests" / "FULL_MOVE_APPROVAL_DETAILS.csv")
    duplicates = read_csv(src / "manifests" / "MERCURY_DUPLICATE_REVIEW.csv")

    detail_by_token = {row["move_id"]: row for row in details}

    existing_tokens: set[str] = set()
    for path in sorted((mercury / "data").glob("community_moves_cm*.json")):
        if path.name == args.output.name:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        for move in payload.get("moves", []):
            existing_tokens.add(normalize_token(move["token"]))

    duplicate_blocked, duplicate_pending = duplicate_blocks(duplicates)

    native_effects = {
        line.strip()
        for line in (pt / "generated" / "move_battle_effects.txt").read_text(
            encoding="utf-8"
        ).splitlines()
        if line.strip()
    }

    selected: list[dict] = []
    deferred: list[dict] = []
    seen_tokens = set(existing_tokens)

    for source in community:
        source_token = source["move_id"].strip()
        token = normalize_token(source_token)
        detail = detail_by_token.get(source_token)
        if detail is None:
            deferred.append({"token": token, "reason": "missing-audit-detail"})
            continue
        if token in existing_tokens:
            continue

        name = detail["english_review_name"].strip()
        if name in duplicate_blocked:
            deferred.append({"token": token, "name": name, "reason": "duplicate-rejected-or-redesign"})
            continue
        if name in duplicate_pending:
            deferred.append({"token": token, "name": name, "reason": "duplicate-decision-pending"})
            continue

        if detail.get("mechanics_audit_status", "") != "complete":
            deferred.append({"token": token, "name": name, "reason": "mechanics-audit-not-complete"})
            continue
        if detail["type"] not in TYPE_MAP:
            deferred.append({"token": token, "name": name, "reason": "custom-type"})
            continue
        if detail["category"] not in CLASS_MAP:
            deferred.append({"token": token, "name": name, "reason": "unknown-category"})
            continue

        target = map_target(detail.get("target", ""))
        if target is None:
            deferred.append({"token": token, "name": name, "reason": "target-needs-extension"})
            continue

        flags_text = (detail.get("move_flags", "") + ";" + source.get("tags", "")).lower()
        if any(
            marker in flags_text
            for marker in ("ignores-stat-stages", "dual-type-effect", "anti-flying")
        ):
            deferred.append({"token": token, "name": name, "reason": "special-move-flag"})
            continue
        if re.search(r"ignore[s]? protect", detail.get("what_it_does", ""), re.I):
            deferred.append({"token": token, "name": name, "reason": "ignore-protect-mechanic"})
            continue

        primary = source.get("primary_effect", "").strip()
        effect = EXPLICIT_EFFECT_MAP.get(primary)
        basis = "explicit-native-effect"

        if effect is None and primary.startswith("EFFECT_"):
            direct = "BATTLE_" + primary
            if direct in native_effects:
                effect = direct
                basis = "direct-native-effect"

        if effect is None:
            if primary.startswith("EFFECT_") and primary not in EXPLICIT_EFFECT_MAP:
                deferred.append({"token": token, "name": name, "reason": "new-effect-family", "source_effect": primary})
                continue
            if re.search(r"(custom_behavior|effect code (?!000\b))", primary, re.I):
                deferred.append({"token": token, "name": name, "reason": "custom-source-effect", "source_effect": primary})
                continue
            effect, basis = infer_generic_effect(detail)

        if effect is None or effect not in native_effects:
            deferred.append({
                "token": token,
                "name": name,
                "reason": basis if effect is None else "effect-not-native",
                "source_effect": primary,
            })
            continue

        fits, fit_reason = detailed_fields_fit(effect, detail)
        if not fits:
            deferred.append({
                "token": token,
                "name": name,
                "reason": fit_reason,
                "effect": effect,
            })
            continue

        # Even explicit effects cannot silently discard a separately audited
        # field or custom behavior described outside their source label.
        what = detail.get("what_it_does", "")
        if CUSTOM_BLOCK_RE.search(what):
            # Native effects that intentionally embody the condition are okay.
            trusted = {
                "BATTLE_EFFECT_DOUBLE_POWER_WHEN_STATUSED",
                "BATTLE_EFFECT_HIT_FIRST_IF_TARGET_ATTACKING",
                "BATTLE_EFFECT_REMOVE_HAZARDS_SCREENS_EVA_DOWN",
            }
            if effect not in trusted:
                deferred.append({"token": token, "name": name, "reason": "extra-custom-behavior", "effect": effect})
                continue

        if token in seen_tokens:
            deferred.append({"token": token, "name": name, "reason": "token-collision"})
            continue

        power = parse_int(detail.get("power", ""), 0)
        accuracy = parse_int(detail.get("accuracy", ""), 0)
        pp = parse_int(detail.get("pp", ""), 0)
        if pp <= 0:
            deferred.append({"token": token, "name": name, "reason": "nonstandard-zero-pp"})
            continue

        if detail["category"] != "Status" and power <= 0:
            deferred.append({"token": token, "name": name, "reason": "nonstandard-damage-power"})
            continue

        if effect == "BATTLE_EFFECT_BYPASS_ACCURACY":
            accuracy = 0

        move_flags: list[str] = []
        if detail.get("contact", "").strip().lower() == "yes" or "contact" in flags_text.split(";"):
            move_flags.append("MOVE_FLAG_MAKES_CONTACT")
        if target not in {"RANGE_USER", "RANGE_USER_SIDE", "RANGE_FIELD"}:
            move_flags.append("MOVE_FLAG_CAN_PROTECT")
        if "mirror-move-affected" in flags_text:
            move_flags.append("MOVE_FLAG_CAN_MIRROR_MOVE")

        donor, donor_basis = choose_animation(source, detail, pt)
        raw_traits = [
            item.strip()
            for item in source.get("tags", "").split(";")
            if item.strip()
        ]
        traits = [
            item
            for item in raw_traits
            if item
            not in {
                "contact",
                "mirror-move-affected",
            }
            and not item.startswith("effect-chance-")
            and not item.startswith("priority-")
        ]

        move_id = args.start_id + len(selected)
        selected.append(
            {
                "id": move_id,
                "token": token,
                "name": sanitize_text(name),
                "type": TYPE_MAP[detail["type"]],
                "class": CLASS_MAP[detail["category"]],
                "power": power,
                "accuracy": accuracy,
                "pp": pp,
                "effect": {
                    "type": effect,
                    "chance": chance_for(source, detail, effect),
                },
                "range": target,
                "priority": parse_priority(detail.get("priority", "")),
                "flags": move_flags,
                "contest": {
                    "effect": "CONTEST_EFFECT_BASIC",
                    "type": CONTEST_BY_CLASS[detail["category"]],
                },
                "description": description_lines(
                    detail.get("what_it_does", "")
                    or detail.get("source_description", "")
                ),
                "animation": {
                    "mode": "copy_native_platinum",
                    "donor_move": donor,
                    "selection_basis": donor_basis,
                    "provisional_visual": donor_basis != "source-native-platinum-reference",
                },
                "traits": traits,
                "provenance": (
                    f"{detail.get('source_project', '')} / "
                    f"{detail.get('source_repo', '')} @ "
                    f"{detail.get('source_commit', '')}"
                ).strip(),
                "mechanics_basis": basis,
                "source_token": source_token,
            }
        )
        seen_tokens.add(token)

    if not selected:
        raise SystemExit("native-mechanics sweep selected zero moves")

    payload = {
        "schema_version": 1,
        "lane": "community_imports",
        "start_id": args.start_id,
        "source_library": "lionsprideemb-tech/Pokemon-moves",
        "source_manifest": "manifests/community_moves.csv",
        "batch": "CM06_NATIVE_MECHANICS_BULK",
        "selection_policy": (
            "Only moves whose complete audited behavior maps to existing "
            "pokeplatinum battle effects/targets/priorities are admitted. "
            "Other moves remain deferred for explicit mechanics review."
        ),
        "moves": selected,
    }
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    reason_counts: dict[str, int] = {}
    for row in deferred:
        reason_counts[row["reason"]] = reason_counts.get(row["reason"], 0) + 1

    report = {
        "gate": "CM06_NATIVE_MECHANICS_BULK_SELECTION",
        "source_candidates": len(community),
        "already_materialized": len(existing_tokens),
        "selected_without_new_mechanics": len(selected),
        "first_id": selected[0]["id"],
        "last_id": selected[-1]["id"],
        "deferred_for_review": len(deferred),
        "deferred_reason_counts": dict(sorted(reason_counts.items())),
        "selected": [
            {
                "id": row["id"],
                "token": row["token"],
                "name": row["name"],
                "effect": row["effect"]["type"],
                "mechanics_basis": row["mechanics_basis"],
                "animation_donor": row["animation"]["donor_move"],
                "provisional_visual": row["animation"]["provisional_visual"],
            }
            for row in selected
        ],
        "deferred": deferred,
    }
    args.report.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({k: v for k, v in report.items() if k not in {"selected", "deferred"}}, indent=2))


if __name__ == "__main__":
    main()
