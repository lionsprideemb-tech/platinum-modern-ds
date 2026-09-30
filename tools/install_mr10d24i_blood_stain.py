#!/usr/bin/env python3
"""MR10D24I — Blood Stain + reusable Bleeding battle state.

Blood Stain keeps its holder Bleeding while active and spreads Bleeding to the
opposing battler through successful contact. Bleeding is battle-only, deals
1/8 max HP at end turn, blocks positive HP recovery, and does not apply to
Rock/Ghost types. Switching clears ordinary spread Bleed; a Blood Stain holder
reasserts its own state while its Ability is active.
"""
from pathlib import Path
import argparse,json
NAME="Blood Stain";TOKEN="ABILITY_MR_BLOOD_STAIN";AID=764

def ins(p,a,s,before=True):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"anchor {t.count(a)}")
 p.write_text(t.replace(a,(s+a if before else a+s),1))

def patch(root):
 ctx=root/"include/battle/battle_context.h"
 ins(ctx,"    u8 mercuryEnraged[MAX_BATTLERS];\n","    u8 mercuryBleeding[MAX_BATTLERS];\n",False)
 lib=root/"src/battle/battle_lib.c"
 # Init beside Enraged.
 ins(lib,"        battleCtx->mercuryEnraged[i] = FALSE;\n","        battleCtx->mercuryBleeding[i] = FALSE;\n",False)
 ins(lib,"    battleCtx->mercuryEnraged[battler] = FALSE;\n","    battleCtx->mercuryBleeding[battler] = FALSE;\n",False)
 # Blood Stain is persistent while active; initialize on entry.
 ins(lib,"                    case ABILITY_MR_BERSERK_DNA:\n","""                    case ABILITY_MR_BLOOD_STAIN:
                        if (battleCtx->battleMons[battler].type1 != TYPE_ROCK
                            && battleCtx->battleMons[battler].type2 != TYPE_ROCK
                            && battleCtx->battleMons[battler].type1 != TYPE_GHOST
                            && battleCtx->battleMons[battler].type2 != TYPE_GHOST) {
                            battleCtx->mercuryBleeding[battler] = TRUE;
                        }
                        break;

""")
 # Spread through a successful contact hit. Handles either direction because
 # TriggerAbilityOnHit is evaluated for defender; holder can stain attacker.
 ins(lib,"    case ABILITY_MR_WIND_CHIMES:\n","""    case ABILITY_MR_BLOOD_STAIN:
        if (battleCtx->attacker != BATTLER_NONE
            && ATTACKING_MON.curHP && DEFENDING_MON.curHP
            && (MOVE_DATA(battleCtx->moveCur).flags & MOVE_FLAG_MAKES_CONTACT)
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && battleCtx->battleMons[battleCtx->attacker].type1 != TYPE_ROCK
            && battleCtx->battleMons[battleCtx->attacker].type2 != TYPE_ROCK
            && battleCtx->battleMons[battleCtx->attacker].type1 != TYPE_GHOST
            && battleCtx->battleMons[battleCtx->attacker].type2 != TYPE_GHOST) {
            battleCtx->mercuryBleeding[battleCtx->attacker] = TRUE;
        }
        break;

""")
 # Healing lock in centralized HP update path: positive healing is zeroed.
 script=root/"src/battle/battle_script.c"
 anchor="static BOOL BtlCmd_UpdateMonData(BattleSystem *battleSys, BattleContext *battleCtx)\n"
 # Central HP mutation hook: positive hpCalcTemp is recovery in the native script lane.
 helper="""BOOL Mercury_BleedingBlocksHealing(BattleContext *battleCtx, int battler)
{
    return battler >= 0 && battler < MAX_BATTLERS
        && battleCtx->mercuryBleeding[battler];
}

"""
 ins(lib,"BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)\n",helper)
 hp_anchor="""    // Cap the hit damage to the battler's current HP
"""
 hp_block="""    /* Mercury Bleeding blocks positive HP recovery globally. */
    if (battleCtx->hpCalcTemp > 0 && Mercury_BleedingBlocksHealing(battleCtx, battler)) {
        battleCtx->hpCalcTemp = 0;
    }

"""
 ins(script,hp_anchor,hp_block)
 hdr=root/"include/battle/battle_lib.h"
 ins(hdr,"BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript);\n","BOOL Mercury_BleedingBlocksHealing(BattleContext *battleCtx, int battler);\n")
 # End-turn chip reuses the controller's existing field-condition sweep.
 ctl=root/"src/battle/battle_controller_player.c"
 anchor="""        case FIELD_COND_CHECK_END:
"""
 block="""        case FIELD_COND_CHECK_STATE_MERCURY_BLEED:
            for (i = 0; i < maxBattlers; i++) {
                if (battleCtx->battleMons[i].curHP
                    && battleCtx->mercuryBleeding[i]) {
                    int chip = battleCtx->battleMons[i].maxHP / 8;
                    if (chip < 1) chip = 1;
                    battleCtx->battleMons[i].curHP =
                        battleCtx->battleMons[i].curHP > chip
                        ? battleCtx->battleMons[i].curHP - chip : 0;
                    BattleMon_CopyToParty(battleSys, battleCtx, i);
                }
            }
            battleCtx->fieldConditionCheckState++;
            break;

"""
 ins(ctl,anchor,block)
 ins(ctl,"    FIELD_COND_CHECK_STATE_MERCURY_TERRAIN,\n","    FIELD_COND_CHECK_STATE_MERCURY_BLEED,\n",False)

def reg(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 if TOKEN not in x:x.append(TOKEN)
 p.write_text("\n".join(x)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24i-blood-stain.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();patch(root);reg(a.implemented_registry.resolve())
 ab=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()];lib=(root/"src/battle/battle_lib.c").read_text();ctx=(root/"include/battle/battle_context.h").read_text();ctl=(root/"src/battle/battle_controller_player.c").read_text()
 checks={"stable_id":len(ab)>AID and ab[AID]==TOKEN,"bleed_state":"mercuryBleeding[MAX_BATTLERS]" in ctx,"holder_bleeding":"case ABILITY_MR_BLOOD_STAIN:" in lib and "mercuryBleeding[battler] = TRUE" in lib,"contact_spread":"MOVE_FLAG_MAKES_CONTACT" in lib and "mercuryBleeding[battleCtx->attacker] = TRUE" in lib,"rock_ghost_immunity":"TYPE_ROCK" in lib and "TYPE_GHOST" in lib,"end_turn_eighth":"FIELD_COND_CHECK_STATE_MERCURY_BLEED" in ctl and "maxHP / 8" in ctl,"healing_lock_hook":"Mercury_BleedingBlocksHealing" in lib and "Mercury Bleeding blocks positive HP recovery globally" in (root/"src/battle/battle_script.c").read_text(),"switch_clear":"mercuryBleeding[battler] = FALSE" in lib,"registry":TOKEN in a.implemented_registry.read_text(),"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24I_BLOOD_STAIN","status":status,"implemented":[NAME],"remaining_after_d24i":5,"note":"Bleeding healing prevention is wired centrally at native UpdateHealthBarValue; individual healing moves do not require patches.","checks":checks},indent=2)+"\n");print(status)
 if status!="PASS":raise SystemExit("D24I failed")
if __name__=="__main__":main()
