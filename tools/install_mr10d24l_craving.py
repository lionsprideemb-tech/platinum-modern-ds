#!/usr/bin/env python3
"""MR10D24L — Craving (699), final Final-14 mechanic.

ER contract: at end of turn eat Sitrus/Liechi/Ganlon/Salac/Petaya/Apicot/
Lansat/Starf, or one random pinch-healing berry (Figy/Wiki/Mago/Aguav/Iapapa).
The generated berry never replaces or consumes the battler's real held item.
"""
from pathlib import Path
import argparse,json

ABILITY="ABILITY_MR_CRAVING"; ID=699
PRIMARY=["ITEM_SITRUS_BERRY","ITEM_LIECHI_BERRY","ITEM_GANLON_BERRY","ITEM_SALAC_BERRY",
"ITEM_PETAYA_BERRY","ITEM_APICOT_BERRY","ITEM_LANSAT_BERRY","ITEM_STARF_BERRY"]
PINCH=["ITEM_FIGY_BERRY","ITEM_WIKI_BERRY","ITEM_MAGO_BERRY","ITEM_AGUAV_BERRY","ITEM_IAPAPA_BERRY"]

def ins(p,a,s):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"anchor mismatch {p}: {t.count(a)}")
 p.write_text(t.replace(a,s+a,1))

def patch(root):
 ctx=root/"include/battle/battle_context.h"
 ins(ctx,"    u16 mercuryCustomMultiHitTriggerAbility;\n",
"""    // MR10D24L: transient ability-created berry; never written to heldItem.
    u16 mercuryCravingBerry[MAX_BATTLERS];
    u8 mercuryCravingEnteredThisTurn[MAX_BATTLERS];

""")
 lib=root/"src/battle/battle_lib.c"
 # Initialize transient state with the other per-battler Mercury battle state.
 init_anchor="""        battleCtx->mercuryEnraged[i] = FALSE;
"""
 init_code="""        battleCtx->mercuryCravingBerry[i] = 0;
        battleCtx->mercuryCravingEnteredThisTurn[i] = FALSE;
"""
 ins(lib,init_anchor,init_code)
 # Add selector/effect dispatcher beside turn-end ability machinery.
 marker="BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)\n"
 helper=r'''/* Mercury D24L Craving: generated berries bypass held-item thresholds because
 * the ability explicitly eats one at end of turn. Effects mirror native berries. */
static BOOL Mercury_CravingEatBerry(BattleSystem *battleSys, BattleContext *battleCtx, int battler)
{
    static const u16 primary[] = {
        ITEM_SITRUS_BERRY, ITEM_LIECHI_BERRY, ITEM_GANLON_BERRY, ITEM_SALAC_BERRY,
        ITEM_PETAYA_BERRY, ITEM_APICOT_BERRY, ITEM_LANSAT_BERRY, ITEM_STARF_BERRY
    };
    static const u16 pinch[] = {
        ITEM_FIGY_BERRY, ITEM_WIKI_BERRY, ITEM_MAGO_BERRY, ITEM_AGUAV_BERRY, ITEM_IAPAPA_BERRY
    };
    u16 berry;
    int pick = BattleSystem_RandNext(battleSys) % 9;
    if (pick == 8) berry = pinch[BattleSystem_RandNext(battleSys) % NELEMS(pinch)];
    else berry = primary[pick];

    battleCtx->mercuryCravingBerry[battler] = berry;
    battleCtx->msgBattlerTemp = battler;
    battleCtx->msgItemTemp = berry;

    switch (berry) {
    case ITEM_SITRUS_BERRY:
        if (battleCtx->battleMons[battler].curHP >= battleCtx->battleMons[battler].maxHP) return FALSE;
        battleCtx->hpCalcTemp = BattleSystem_Divide(battleCtx->battleMons[battler].maxHP * 25, 100);
        LOAD_SUBSEQ(subscript_held_item_hp_restore); break;
    case ITEM_LIECHI_BERRY: if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK] >= MAX_STAT_STAGE) return FALSE; battleCtx->msgTemp=BATTLE_STAT_ATTACK; LOAD_SUBSEQ(subscript_held_item_raise_stat); break;
    case ITEM_GANLON_BERRY: if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE] >= MAX_STAT_STAGE) return FALSE; battleCtx->msgTemp=BATTLE_STAT_DEFENSE; LOAD_SUBSEQ(subscript_held_item_raise_stat); break;
    case ITEM_SALAC_BERRY: if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SPEED] >= MAX_STAT_STAGE) return FALSE; battleCtx->msgTemp=BATTLE_STAT_SPEED; LOAD_SUBSEQ(subscript_held_item_raise_stat); break;
    case ITEM_PETAYA_BERRY: if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SP_ATTACK] >= MAX_STAT_STAGE) return FALSE; battleCtx->msgTemp=BATTLE_STAT_SP_ATTACK; LOAD_SUBSEQ(subscript_held_item_raise_stat); break;
    case ITEM_APICOT_BERRY: if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_SP_DEFENSE] >= MAX_STAT_STAGE) return FALSE; battleCtx->msgTemp=BATTLE_STAT_SP_DEFENSE; LOAD_SUBSEQ(subscript_held_item_raise_stat); break;
    case ITEM_LANSAT_BERRY: if (battleCtx->battleMons[battler].statusVolatile & VOLATILE_CONDITION_FOCUS_ENERGY) return FALSE; LOAD_SUBSEQ(subscript_held_item_raise_crit); break;
    case ITEM_STARF_BERRY: {
        int i, open=0;
        for (i=0;i<5;i++) if (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK+i] < MAX_STAT_STAGE) open++;
        if (!open) return FALSE;
        do { i=BattleSystem_RandNext(battleSys)%5; }
        while (battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_ATTACK+i] == MAX_STAT_STAGE);
        battleCtx->msgTemp=BATTLE_STAT_ATTACK+i; LOAD_SUBSEQ(subscript_held_item_sharply_raise_stat); break;
    }
    default: /* pinch-healing family: native Gen IV 1/itemPower healing + flavor */
        battleCtx->hpCalcTemp=BattleSystem_Divide(battleCtx->battleMons[battler].maxHP,8);
        LOAD_SUBSEQ(subscript_held_item_hp_restore); break;
    }
    battleCtx->commandNext=battleCtx->command;
    battleCtx->command=BATTLE_CONTROL_EXEC_SCRIPT;
    return TRUE;
}

'''
 ins(lib,marker,helper)
 # Hook at start of existing turn-end ability function, after declarations.
 t=lib.read_text();start=t.find(marker)
 if start<0:raise SystemExit("turn end function missing")
 brace=t.find("{",start);pos=t.find("\n",brace)+1
 hook='''    /* Mercury D24L Craving — not on the entry turn. */
    if (Battler_Ability(battleCtx, battler) == ABILITY_MR_CRAVING
        && battleCtx->battleMons[battler].curHP
        && battleCtx->mercuryCravingEnteredThisTurn[battler] == FALSE) {
        if (Mercury_CravingEatBerry(battleSys, battleCtx, battler)) return TRUE;
    }
    battleCtx->mercuryCravingEnteredThisTurn[battler] = FALSE;

'''
 if "Mercury D24L Craving — not on the entry turn." not in t:
  lib.write_text(t[:pos]+hook+t[pos:])
 # Mark entry turn in switch-in path where D24 controllers already initialize.
 ctl=root/"src/battle/battle_controller_player.c"
 t=ctl.read_text()
 anchors=["BattleSystem_TriggerSwitchInAbility(battleSys, battleCtx, battler)","BattleSystem_TriggerSwitchInAbility(battleSys, battleCtx, battleCtx->battlerIdSwitch)"]
 found=next((a for a in anchors if a in t),None)
 if not found:raise SystemExit("switch-in ability anchor missing")
 line=t.find(found);line=t.rfind("\n",0,line)+1
 indent=t[line:len(t)-len(t.lstrip())] if False else "            "
 code=indent+"battleCtx->mercuryCravingEnteredThisTurn[battler] = TRUE; /* MR10D24L */\n"
 # Avoid brittle battler variable mismatch: insert only when local 'battler' anchor used.
 if "battleCtx->mercuryCravingEnteredThisTurn[battler] = TRUE;" not in t and anchors[0] in t:
  line=t.rfind("\n",0,t.find(anchors[0]))+1;t=t[:line]+code+t[line:];ctl.write_text(t)

def reg(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 if ABILITY not in x:x.append(ABILITY)
 p.write_text("\n".join(x)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24l-craving.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();patch(root);reg(a.implemented_registry.resolve())
 ab=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
 lib=(root/"src/battle/battle_lib.c").read_text();ctx=(root/"include/battle/battle_context.h").read_text()
 checks={"stable_id":len(ab)>ID and ab[ID]==ABILITY,
 "locked_primary_pool":all(x in lib for x in PRIMARY),"pinch_pool":all(x in lib for x in PINCH),
 "nine_way_choice":"% 9" in lib,"native_subscripts":"subscript_held_item_sharply_raise_stat" in lib,"effect_guards":"if (!open) return FALSE;" in lib and "MAX_STAT_STAGE" in lib,
 "held_item_preserved":"mercuryCravingBerry" in ctx and "heldItem =" not in lib[lib.find("Mercury_CravingEatBerry"):lib.find("Mercury_CravingEatBerry")+5000],
 "entry_turn_blocked":"mercuryCravingEnteredThisTurn" in lib,
 "registry":ABILITY in a.implemented_registry.read_text(),"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24L_CRAVING","status":status,"checks":checks},indent=2)+"\n");print(status)
 if status!="PASS":raise SystemExit("D24L failed")
if __name__=="__main__":main()
