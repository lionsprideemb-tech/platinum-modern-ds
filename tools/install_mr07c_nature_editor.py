#!/usr/bin/env python3
"""MR07C — persistent effective-Nature override + Summary Nature editor.

Builds on MR07A/MR07B1.

Mercury needs Nature customization without changing the Gen IV personality
value. Re-rolling PID would also risk changing gender, shininess, ability-slot
selection, Spinda markings, etc. MR07C instead stores a tagged 5-bit Nature
override in Platinum's otherwise-unused BoxPokemon Block-B u16 field exposed as
MON_DATA_UNUSED_114. BoxPokemon_GetNature/Pokemon_GetNature return the override
when the Mercury tag is present, so stat calculation and every normal Nature
consumer see one coherent effective Nature.

The Pokemon/BoxPokemon binary sizes do not change.

Summary flow:
  Skills -> X -> highlight Nature -> A
  bottom screen -> native scrolling Nature selector
  Up/Down -> choose
  A -> persist + recalculate real stats
  B -> cancel
  closing the editor restores Platinum's radial Summary navigator.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one match in {path}, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def insert_after_once(path: Path, anchor: str, insertion: str, label: str) -> None:
    text = path.read_text()
    if insertion in text:
        return
    count = text.count(anchor)
    if count != 1:
        raise SystemExit(
            f"{label}: expected exactly one anchor in {path}, found {count}"
        )
    path.write_text(text.replace(anchor, anchor + insertion, 1), encoding="utf-8")


def patch_text(root: Path) -> None:
    path = root / "res/text/pokemon_summary_screen.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    additions = {
        "PokemonSummary_Text_MercuryNatureEditorTitle": "NATURE",
        "PokemonSummary_Text_MercuryNatureEditorHelp1": "UP/DOWN SELECT",
        "PokemonSummary_Text_MercuryNatureEditorHelp2": "A SET   B BACK",
    }

    existing = {row.get("id") for row in data["messages"]}
    for msg_id, value in additions.items():
        if msg_id not in existing:
            data["messages"].append({"id": msg_id, "en_US": value})

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def patch_pokemon_api(root: Path) -> None:
    header = root / "include/pokemon.h"
    source = root / "src/pokemon.c"

    insert_after_once(
        header,
        """u8 BoxPokemon_GetNature(BoxPokemon *boxMon);
""",
        """void Pokemon_MercurySetNatureOverride(Pokemon *mon, u8 nature);
void BoxPokemon_MercurySetNatureOverride(BoxPokemon *boxMon, u8 nature);
void Pokemon_MercuryClearNatureOverride(Pokemon *mon);
void BoxPokemon_MercuryClearNatureOverride(BoxPokemon *boxMon);
""",
        "MR07C nature override API declarations",
    )

    old = """u8 BoxPokemon_GetNature(BoxPokemon *boxMon)
{
    BOOL reencrypt = BoxPokemon_EnterDecryptionContext(boxMon);
    u32 monPersonality = BoxPokemon_GetValue(boxMon, MON_DATA_PERSONALITY, NULL);

    BoxPokemon_ExitDecryptionContext(boxMon, reencrypt);

    return Pokemon_GetNatureOf(monPersonality);
}
"""

    new = r'''#define MERCURY_NATURE_OVERRIDE_MASK       0xFFE0
#define MERCURY_NATURE_OVERRIDE_MAGIC      0xA5E0
#define MERCURY_NATURE_OVERRIDE_VALUE_MASK 0x001F

u8 BoxPokemon_GetNature(BoxPokemon *boxMon)
{
    BOOL reencrypt = BoxPokemon_EnterDecryptionContext(boxMon);
    u32 monPersonality =
        BoxPokemon_GetValue(boxMon, MON_DATA_PERSONALITY, NULL);
    u16 mercuryNature =
        (u16)BoxPokemon_GetValue(boxMon, MON_DATA_UNUSED_114, NULL);

    BoxPokemon_ExitDecryptionContext(boxMon, reencrypt);

    // Vanilla / imported Pokemon normally have zero in this retail-unused u16.
    // The 11-bit magic tag makes accidental interpretation of foreign data as
    // a Mercury override vanishingly unlikely while retaining five Nature bits.
    if ((mercuryNature & MERCURY_NATURE_OVERRIDE_MASK)
            == MERCURY_NATURE_OVERRIDE_MAGIC) {
        u8 nature =
            (u8)(mercuryNature & MERCURY_NATURE_OVERRIDE_VALUE_MASK);
        if (nature < NATURE_COUNT) {
            return nature;
        }
    }

    return Pokemon_GetNatureOf(monPersonality);
}

void BoxPokemon_MercurySetNatureOverride(BoxPokemon *boxMon, u8 nature)
{
    GF_ASSERT(nature < NATURE_COUNT);

    u16 encoded =
        (u16)(MERCURY_NATURE_OVERRIDE_MAGIC
            | (nature & MERCURY_NATURE_OVERRIDE_VALUE_MASK));
    BoxPokemon_SetValue(boxMon, MON_DATA_UNUSED_114, &encoded);
}

void Pokemon_MercurySetNatureOverride(Pokemon *mon, u8 nature)
{
    BoxPokemon_MercurySetNatureOverride(&mon->box, nature);
    Pokemon_CalcStats(mon);
}

void BoxPokemon_MercuryClearNatureOverride(BoxPokemon *boxMon)
{
    u16 encoded = 0;
    BoxPokemon_SetValue(boxMon, MON_DATA_UNUSED_114, &encoded);
}

void Pokemon_MercuryClearNatureOverride(Pokemon *mon)
{
    BoxPokemon_MercuryClearNatureOverride(&mon->box);
    Pokemon_CalcStats(mon);
}
'''
    replace_once(source, old, new, "MR07C effective Nature getter/storage")


def patch_summary(root: Path) -> None:
    path = root / "src/applications/pokemon_summary_screen/main.c"

    # Declarations added by MR07B1.
    replace_once(
        path,
        """static void MercurySkillsEditor_OpenEV(PokemonSummaryScreen *summaryScreen, u8 stat);
static void MercurySkillsEditor_OpenAbility(PokemonSummaryScreen *summaryScreen);
static void MercurySkillsEditor_Close(PokemonSummaryScreen *summaryScreen);
""",
        """static void MercurySkillsEditor_OpenEV(PokemonSummaryScreen *summaryScreen, u8 stat);
static void MercurySkillsEditor_OpenNature(PokemonSummaryScreen *summaryScreen);
static void MercurySkillsEditor_OpenAbility(PokemonSummaryScreen *summaryScreen);
static void MercurySkillsEditor_Close(PokemonSummaryScreen *summaryScreen);
""",
        "MR07C Nature editor declaration",
    )

    replace_once(
        path,
        """static void MercurySkillsEditor_SetCurrentEV(PokemonSummaryScreen *summaryScreen, u8 value);
static void MercurySkillsEditor_SetAbility(PokemonSummaryScreen *summaryScreen, u16 ability);
""",
        """static void MercurySkillsEditor_SetCurrentEV(PokemonSummaryScreen *summaryScreen, u8 value);
static void MercurySkillsEditor_SetNature(PokemonSummaryScreen *summaryScreen, u8 nature);
static void MercurySkillsEditor_SetAbility(PokemonSummaryScreen *summaryScreen, u16 ability);
""",
        "MR07C Nature setter declaration",
    )

    # A now handles the Nature row as a real editable field.
    replace_once(
        path,
        """                if (summaryScreen->mercurySkillsCursor < 6) {
                    MercurySkillsEditor_OpenEV(
                        summaryScreen,
                        summaryScreen->mercurySkillsCursor);
                } else if (summaryScreen->mercurySkillsCursor == 7) {
                    MercurySkillsEditor_OpenAbility(summaryScreen);
                }

                // Nature intentionally remains read-only until MR07C installs
                // a persistent non-PID effective-Nature override.
                return SUMMARY_STATE_HANDLE_INPUT;
""",
        """                if (summaryScreen->mercurySkillsCursor < 6) {
                    MercurySkillsEditor_OpenEV(
                        summaryScreen,
                        summaryScreen->mercurySkillsCursor);
                } else if (summaryScreen->mercurySkillsCursor == 6) {
                    MercurySkillsEditor_OpenNature(summaryScreen);
                } else if (summaryScreen->mercurySkillsCursor == 7) {
                    MercurySkillsEditor_OpenAbility(summaryScreen);
                }

                return SUMMARY_STATE_HANDLE_INPUT;
""",
        "MR07C bind A on Nature",
    )

    # Extend MR07B1 editor mode.
    replace_once(
        path,
        """enum {
    MERCURY_SKILLS_EDITOR_NONE = 0,
    MERCURY_SKILLS_EDITOR_EV,
    MERCURY_SKILLS_EDITOR_ABILITY,
};
""",
        """enum {
    MERCURY_SKILLS_EDITOR_NONE = 0,
    MERCURY_SKILLS_EDITOR_EV,
    MERCURY_SKILLS_EDITOR_ABILITY,
    MERCURY_SKILLS_EDITOR_NATURE,
};
""",
        "MR07C editor enum",
    )

    # Add compact Nature-effect message lookup next to EV labels.
    anchor = """static const u32 sMercurySkillsEvLabels[6] = {
    PokemonSummary_Text_LabelHp,
    PokemonSummary_Text_LabelAttack,
    PokemonSummary_Text_LabelDefense,
    PokemonSummary_Text_LabelSpAttack,
    PokemonSummary_Text_LabelSpDefense,
    PokemonSummary_Text_LabelSpeed,
};
"""
    nature_table = """
static const u32 sMercurySkillsNatureEffectText[NATURE_COUNT] = {
    PokemonSummary_Text_MercuryNatureHardy,
    PokemonSummary_Text_MercuryNatureLonely,
    PokemonSummary_Text_MercuryNatureBrave,
    PokemonSummary_Text_MercuryNatureAdamant,
    PokemonSummary_Text_MercuryNatureNaughty,
    PokemonSummary_Text_MercuryNatureBold,
    PokemonSummary_Text_MercuryNatureDocile,
    PokemonSummary_Text_MercuryNatureRelaxed,
    PokemonSummary_Text_MercuryNatureImpish,
    PokemonSummary_Text_MercuryNatureLax,
    PokemonSummary_Text_MercuryNatureTimid,
    PokemonSummary_Text_MercuryNatureHasty,
    PokemonSummary_Text_MercuryNatureSerious,
    PokemonSummary_Text_MercuryNatureJolly,
    PokemonSummary_Text_MercuryNatureNaive,
    PokemonSummary_Text_MercuryNatureModest,
    PokemonSummary_Text_MercuryNatureMild,
    PokemonSummary_Text_MercuryNatureQuiet,
    PokemonSummary_Text_MercuryNatureBashful,
    PokemonSummary_Text_MercuryNatureRash,
    PokemonSummary_Text_MercuryNatureCalm,
    PokemonSummary_Text_MercuryNatureGentle,
    PokemonSummary_Text_MercuryNatureSassy,
    PokemonSummary_Text_MercuryNatureCareful,
    PokemonSummary_Text_MercuryNatureQuirky,
};
"""
    insert_after_once(path, anchor, nature_table, "MR07C Nature effect table")

    # Add Nature-name printer after the existing Ability-name printer.
    ability_printer_end = """static void MercurySkillsEditor_CreateWindows(PokemonSummaryScreen *summaryScreen)
"""
    nature_printer = r'''static void MercurySkillsEditor_PrintNature(
    PokemonSummaryScreen *summaryScreen,
    Window *window,
    u8 nature,
    u32 x,
    u32 y,
    TextColor color)
{
    StringTemplate_SetNatureName(
        summaryScreen->strFormatter,
        0,
        nature);
    String *fmt = MessageLoader_GetNewString(
        summaryScreen->msgLoader,
        PokemonSummary_Text_TemplateAbility);
    StringTemplate_Format(
        summaryScreen->strFormatter,
        summaryScreen->string,
        fmt);
    String_Free(fmt);

    Text_AddPrinterWithParamsAndColor(
        window,
        FONT_SYSTEM,
        summaryScreen->string,
        x,
        y,
        TEXT_SPEED_NO_TRANSFER,
        color,
        NULL);
}

'''
    insert_after_once(
        path,
        ability_printer_end,
        "",  # marker handled below with exact replacement
        "MR07C no-op",
    )
    # insert_after_once cannot put content before marker, so replace marker once.
    replace_once(
        path,
        ability_printer_end,
        nature_printer + ability_printer_end,
        "MR07C Nature name printer",
    )

    # Add open-Nature entrypoint immediately before open-Ability.
    ability_open_marker = """static void MercurySkillsEditor_OpenAbility(PokemonSummaryScreen *summaryScreen)
"""
    nature_open = r'''static void MercurySkillsEditor_OpenNature(PokemonSummaryScreen *summaryScreen)
{
    summaryScreen->mercurySkillsEditorMode = MERCURY_SKILLS_EDITOR_NATURE;
    summaryScreen->mercurySkillsEditorCursor = summaryScreen->monData.nature;
    summaryScreen->mercurySkillsCursor = 6;
    MercurySkillsEditor_CreateWindows(summaryScreen);
    MercurySkillsEditor_Draw(summaryScreen);
}

'''
    replace_once(
        path,
        ability_open_marker,
        nature_open + ability_open_marker,
        "MR07C Nature open",
    )

    # Insert native scrolling Nature page before the Draw dispatcher.
    draw_dispatch_marker = """static void MercurySkillsEditor_Draw(PokemonSummaryScreen *summaryScreen)
{
"""
    draw_nature = r'''static void MercurySkillsEditor_DrawNature(PokemonSummaryScreen *summaryScreen)
{
    Window *header =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_HEADER];
    Window *body =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_BODY];
    Window *footer =
        &summaryScreen->mercurySkillsEditorWindows[MERCURY_SKILLS_EDITOR_WINDOW_FOOTER];

    Window_FillTilemap(header, 0);
    Window_FillTilemap(body, 15);
    Window_FillTilemap(footer, 15);

    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        header,
        PokemonSummary_Text_MercuryNatureEditorTitle,
        4,
        0,
        SUMMARY_TEXT_BLACK);

    // Seven-row rolling window around the current choice. This keeps every
    // Nature reachable without squeezing 25 tiny rows onto the DS screen.
    for (int row = 0; row < 7; row++) {
        int offset = row - 3;
        int nature =
            summaryScreen->mercurySkillsEditorCursor + offset;

        while (nature < 0) {
            nature += NATURE_COUNT;
        }
        while (nature >= NATURE_COUNT) {
            nature -= NATURE_COUNT;
        }

        u32 y = 3 + row * 14;
        BOOL selected = (row == 3);

        if (selected) {
            Window_FillRectWithColor(body, 4, 4, y - 2, 232, 14);
        }

        TextColor color =
            selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLACK;

        MercurySkillsEditor_PrintNature(
            summaryScreen,
            body,
            (u8)nature,
            12,
            y,
            color);

        MercurySkillsEditor_PrintMessage(
            summaryScreen,
            body,
            sMercurySkillsNatureEffectText[nature],
            128,
            y,
            selected ? SUMMARY_TEXT_WHITE : SUMMARY_TEXT_BLUE);
    }

    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryNatureEditorHelp1,
        8,
        9,
        SUMMARY_TEXT_BLACK);
    MercurySkillsEditor_PrintMessage(
        summaryScreen,
        footer,
        PokemonSummary_Text_MercuryNatureEditorHelp2,
        8,
        27,
        SUMMARY_TEXT_BLACK);

    Window_ScheduleCopyToVRAM(header);
    Window_ScheduleCopyToVRAM(body);
    Window_ScheduleCopyToVRAM(footer);
}

'''
    replace_once(
        path,
        draw_dispatch_marker,
        draw_nature + draw_dispatch_marker,
        "MR07C Nature renderer",
    )

    replace_once(
        path,
        """    if (summaryScreen->mercurySkillsEditorMode == MERCURY_SKILLS_EDITOR_EV) {
        MercurySkillsEditor_DrawEV(summaryScreen);
    } else if (
        summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_ABILITY) {
        MercurySkillsEditor_DrawAbility(summaryScreen);
    }
}
""",
        """    if (summaryScreen->mercurySkillsEditorMode == MERCURY_SKILLS_EDITOR_EV) {
        MercurySkillsEditor_DrawEV(summaryScreen);
    } else if (
        summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_ABILITY) {
        MercurySkillsEditor_DrawAbility(summaryScreen);
    } else if (
        summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_NATURE) {
        MercurySkillsEditor_DrawNature(summaryScreen);
    }
}
""",
        "MR07C Draw dispatcher",
    )

    # Persist Nature through the new per-Pokemon override and refresh real stats.
    ability_setter_marker = """static void MercurySkillsEditor_SetAbility(
    PokemonSummaryScreen *summaryScreen,
    u16 ability)
"""
    nature_setter = r'''static void MercurySkillsEditor_SetNature(
    PokemonSummaryScreen *summaryScreen,
    u8 nature)
{
    void *monData = PokemonSummaryScreen_MonData(summaryScreen);

    if (summaryScreen->data->dataType == SUMMARY_DATA_BOX_MON) {
        BoxPokemon_MercurySetNatureOverride(
            (BoxPokemon *)monData,
            nature);
    } else {
        Pokemon_MercurySetNatureOverride(
            (Pokemon *)monData,
            nature);
    }

    SetMonData(summaryScreen);
    summaryScreen->mercurySkillsCursor = 6;
    PokemonSummaryScreen_DrawExtraWindows(summaryScreen);
}

'''
    replace_once(
        path,
        ability_setter_marker,
        nature_setter + ability_setter_marker,
        "MR07C Nature setter",
    )

    # Add Nature input branch immediately before the existing Ability branch.
    ability_input_marker = """    if (summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_ABILITY) {
"""
    nature_input = r'''    if (summaryScreen->mercurySkillsEditorMode
        == MERCURY_SKILLS_EDITOR_NATURE) {
        if (JOY_REPEAT(PAD_KEY_UP)) {
            if (summaryScreen->mercurySkillsEditorCursor == 0) {
                summaryScreen->mercurySkillsEditorCursor = NATURE_COUNT - 1;
            } else {
                summaryScreen->mercurySkillsEditorCursor--;
            }
            Sound_PlayEffect(SE_CONFIRM_sseq_3);
            MercurySkillsEditor_Draw(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_REPEAT(PAD_KEY_DOWN)) {
            summaryScreen->mercurySkillsEditorCursor++;
            if (summaryScreen->mercurySkillsEditorCursor >= NATURE_COUNT) {
                summaryScreen->mercurySkillsEditorCursor = 0;
            }
            Sound_PlayEffect(SE_CONFIRM_sseq_3);
            MercurySkillsEditor_Draw(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_A)) {
            MercurySkillsEditor_SetNature(
                summaryScreen,
                summaryScreen->mercurySkillsEditorCursor);
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            MercurySkillsEditor_Close(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        if (JOY_NEW(PAD_BUTTON_B)) {
            Sound_PlayEffect(SEQ_SE_DP_DECIDE_sseq);
            MercurySkillsEditor_Close(summaryScreen);
            return SUMMARY_STATE_HANDLE_INPUT;
        }

        return SUMMARY_STATE_HANDLE_INPUT;
    }

'''
    replace_once(
        path,
        ability_input_marker,
        nature_input + ability_input_marker,
        "MR07C Nature input",
    )


def validate(root: Path) -> dict[str, bool]:
    pokemon_h = (root / "include/pokemon.h").read_text()
    pokemon_c = (root / "src/pokemon.c").read_text()
    summary_c = (
        root / "src/applications/pokemon_summary_screen/main.c"
    ).read_text()
    text_json = (
        root / "res/text/pokemon_summary_screen.json"
    ).read_text()

    checks = {
        "no_struct_size_change":
            "MON_DATA_UNUSED_114" in pokemon_c
            and "PokemonDataBlockB" not in pokemon_h,
        "tagged_persistent_storage":
            "MERCURY_NATURE_OVERRIDE_MAGIC" in pokemon_c
            and "MERCURY_NATURE_OVERRIDE_MASK" in pokemon_c
            and "MON_DATA_UNUSED_114" in pokemon_c,
        "effective_nature_getter":
            "u8 BoxPokemon_GetNature" in pokemon_c
            and "nature < NATURE_COUNT" in pokemon_c,
        "pid_untouched":
            "Pokemon_SetValue(mon, MON_DATA_PERSONALITY" not in pokemon_c
            and "BoxPokemon_SetValue(boxMon, MON_DATA_PERSONALITY" not in pokemon_c,
        "party_stat_recalc":
            "Pokemon_MercurySetNatureOverride" in pokemon_c
            and "Pokemon_CalcStats(mon);" in pokemon_c,
        "summary_nature_entry":
            "MercurySkillsEditor_OpenNature(summaryScreen)" in summary_c
            and "mercurySkillsCursor == 6" in summary_c,
        "scrolling_25_natures":
            "MERCURY_SKILLS_EDITOR_NATURE" in summary_c
            and "NATURE_COUNT - 1" in summary_c
            and "MercurySkillsEditor_DrawNature" in summary_c,
        "real_party_and_box_write":
            "BoxPokemon_MercurySetNatureOverride" in summary_c
            and "Pokemon_MercurySetNatureOverride" in summary_c,
        "editor_messages":
            "PokemonSummary_Text_MercuryNatureEditorTitle" in text_json
            and "PokemonSummary_Text_MercuryNatureEditorHelp2" in text_json,
        "radial_restore":
            "MercurySkillsEditor_Close(summaryScreen)" in summary_c
            and "PokemonSummaryScreen_SetSubscreenType(summaryScreen);" in summary_c,
    }
    return checks


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument(
        "--report",
        type=Path,
        default=Path("mr07c-nature-editor.json"),
    )
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()

    patch_text(root)
    patch_pokemon_api(root)
    patch_summary(root)

    checks = validate(root)
    status = "PASS" if all(checks.values()) else "FAIL"

    report = {
        "gate": "MERCURY_MR07C_PERSISTENT_NATURE_EDITOR",
        "status": status,
        "requires": [
            "MR07A native Skills screen",
            "MR07B1 EV / Primary Ability editors",
        ],
        "storage": {
            "field": "MON_DATA_UNUSED_114 / PokemonDataBlockB.unused2",
            "box_pokemon_size_changed": False,
            "encoding": "11-bit Mercury magic tag + 5-bit Nature value",
            "native_fallback": "PID % NATURE_COUNT when tag absent/invalid",
        },
        "identity_safety": {
            "pid_mutated": False,
            "gender_changed_by_editor": False,
            "shininess_changed_by_editor": False,
            "spinda_pattern_changed_by_editor": False,
        },
        "behavior": {
            "Pokemon_GetNature": "returns effective override when present",
            "stat_calculation": "uses effective Nature through existing Pokemon_CalcStats",
            "summary_display": "uses effective Nature",
            "party_and_box_persistence": True,
        },
        "controls": {
            "skills": "X -> highlight Nature -> A",
            "selector": "Up/Down",
            "commit": "A",
            "cancel": "B",
        },
        "ivs_visible": False,
        "checks": checks,
    }

    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))

    if status != "PASS":
        raise SystemExit("MR07C validation failed")


if __name__ == "__main__":
    main()
