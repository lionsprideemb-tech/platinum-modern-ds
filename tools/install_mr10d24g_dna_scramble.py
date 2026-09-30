#!/usr/bin/env python3
"""MR10D24G — DNA Scramble.

Recovered locked donor semantics:
- Deoxys + damaging move -> Attack Forme
- Recover -> Defense Forme
- other status move -> Speed Forme
The change occurs immediately before move execution. Battle-only stats/types/formNum
are updated; persistent party species data and MR07 UI are untouched.
"""
from pathlib import Path
import argparse,json

NAME="DNA Scramble"; TOKEN="ABILITY_MR_DNA_SCRAMBLE"; AID=734

def before(p,a,s):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit("anchor count "+str(t.count(a)))
 p.write_text(t.replace(a,s+a,1))

def after(p,a,s):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit("anchor count "+str(t.count(a)))
 p.write_text(t.replace(a,a+s,1))

def patch(root):
 lib=root/"src/battle/battle_lib.c"
 helper=r'''static void Mercury_DNAScrambleSetForm(
    BattleSystem *battleSys, BattleContext *battleCtx, int battler, int form)
{
    Pokemon *mon = BattleSystem_GetPartyPokemon(
        battleSys, battler, battleCtx->selectedPartySlot[battler]);

    if (battleCtx->battleMons[battler].species != SPECIES_DEOXYS
        || (battleCtx->battleMons[battler].statusVolatile
            & VOLATILE_CONDITION_TRANSFORM)) {
        return;
    }

    battleCtx->battleMons[battler].formNum = form;
    switch (form) {
    case 1: // Attack: 50/180/20/180/20/150
        Mercury_SetThresholdFormStats(battleCtx, battler, mon, 180, 20, 180, 20, 150);
        break;
    case 2: // Defense: 50/70/160/70/160/90
        Mercury_SetThresholdFormStats(battleCtx, battler, mon, 70, 160, 70, 160, 90);
        break;
    case 3: // Speed: 50/95/90/95/90/180
        Mercury_SetThresholdFormStats(battleCtx, battler, mon, 95, 90, 95, 90, 180);
        break;
    default:
        Mercury_SetThresholdFormStats(battleCtx, battler, mon, 150, 50, 150, 50, 150);
        break;
    }
    battleCtx->battleMons[battler].type1 = TYPE_PSYCHIC;
    battleCtx->battleMons[battler].type2 = TYPE_PSYCHIC;
}

void Mercury_DNAScrambleBeforeMove(
    BattleSystem *battleSys, BattleContext *battleCtx)
{
    int battler = battleCtx->attacker;
    int move = battleCtx->moveCur;
    int form;

    if (battler == BATTLER_NONE
        || Battler_Ability(battleCtx, battler) != ABILITY_MR_DNA_SCRAMBLE
        || battleCtx->battleMons[battler].species != SPECIES_DEOXYS
        || battleCtx->mercuryAbilityGeneratedAction) {
        return;
    }

    if (MOVE_DATA(move).class != CLASS_STATUS) {
        form = 1;
    } else if (move == MOVE_RECOVER) {
        form = 2;
    } else {
        form = 3;
    }
    Mercury_DNAScrambleSetForm(battleSys, battleCtx, battler, form);
}

'''
 before(lib,"BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)\n",helper)
 hdr=root/"include/battle/battle_lib.h"
 before(hdr,"BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);\n","void Mercury_DNAScrambleBeforeMove(BattleSystem *battleSys, BattleContext *battleCtx);\n")
 ctl=root/"src/battle/battle_controller_player.c"
 anchor="        BattleSystem_LoadScript(battleCtx, NARC_INDEX_BATTLE__SKILL__WAZA_SEQ, battleCtx->moveCur);\n"
 before(ctl,anchor,"        Mercury_DNAScrambleBeforeMove(battleSys, battleCtx);\n\n")

def reg(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 if TOKEN not in x:x.append(TOKEN)
 p.write_text("\n".join(x)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24g-dna-scramble.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();patch(root);reg(a.implemented_registry.resolve())
 ab=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
 lib=(root/"src/battle/battle_lib.c").read_text();ctl=(root/"src/battle/battle_controller_player.c").read_text()
 checks={"stable_id":len(ab)>AID and ab[AID]==TOKEN,"pre_move_hook":"Mercury_DNAScrambleBeforeMove(battleSys, battleCtx);" in ctl,"damaging_attack_form":"MOVE_DATA(move).class != CLASS_STATUS" in lib and "form = 1;" in lib,"recover_defense_form":"move == MOVE_RECOVER" in lib and "form = 2;" in lib,"other_status_speed_form":"form = 3;" in lib,"deoxys_only":"species != SPECIES_DEOXYS" in lib,"generated_action_does_not_reform":"mercuryAbilityGeneratedAction" in lib,"registry":TOKEN in a.implemented_registry.read_text(),"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24G_DNA_SCRAMBLE","status":status,"implemented":[NAME],"remaining_after_d24g":7,"checks":checks},indent=2)+"\n");print(status)
 if status!="PASS":raise SystemExit("D24G failed")
if __name__=="__main__":main()
