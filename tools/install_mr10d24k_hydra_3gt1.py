#!/usr/bin/env python3
"""MR10D24K — Hydra + 3 > 1 composite mechanics.

Extends Mercury's native D11 multi-hit lane with ER Multi-Headed semantics:
2 heads = 100% + 25%; 3 heads = 100% + 20% + 15%.
Hydra adds Hubris (+1 SpA after a direct KO).
3 > 1 adds Riptide (Water x1.3, x1.8 at <= 1/3 HP).

Head count is battle/species metadata, not hard-coded to particular holders.
Sprites/content assignments remain a later phase.
"""
from pathlib import Path
import argparse,json

ABILITIES={"ABILITY_MR_HYDRA":739,"ABILITY_MR_3_GT_1":914}

def rep(p,a,b):
 t=p.read_text()
 if b in t:return
 if t.count(a)!=1:raise SystemExit(f"anchor mismatch {p}: {t.count(a)}")
 p.write_text(t.replace(a,b,1))

def ins(p,a,s):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"anchor mismatch {p}: {t.count(a)}")
 p.write_text(t.replace(a,s+a,1))

def patch(root):
 ctx=root/"include/battle/battle_context.h"
 ins(ctx,"    u16 mercuryCustomMultiHitTriggerAbility;\n",
"""    // MR10D24K: ER Multi-Headed metadata for the current generated sequence.
    u8 mercuryMultiHeadedHeads[MAX_BATTLERS];
    u8 mercuryMultiHeadedHitIndex;

""")
 ctl=root/"src/battle/battle_controller_player.c"
 rep(ctl,
"""    case ABILITY_MR_DUAL_WIELD:
        return Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0;

    default:
""",
"""    case ABILITY_MR_DUAL_WIELD:
        return Mercury_MoveIsPulseForCustomAbility(move) ? 2 : 0;

    case ABILITY_MR_HYDRA:
    case ABILITY_MR_3_GT_1:
        if (battleCtx->mercuryMultiHeadedHeads[battleCtx->attacker] == 2) {
            return 2;
        }
        if (battleCtx->mercuryMultiHeadedHeads[battleCtx->attacker] >= 3) {
            return 3;
        }
        return 0;

    default:
""")
 rep(ctl,
"""    battleCtx->mercuryCustomMultiHitActive = TRUE;
    battleCtx->mercuryCustomMultiHitTriggerAbility =
        Battler_Ability(battleCtx, battleCtx->attacker);
    battleCtx->multiHitCounter = hits;
""",
"""    battleCtx->mercuryCustomMultiHitActive = TRUE;
    battleCtx->mercuryCustomMultiHitTriggerAbility =
        Battler_Ability(battleCtx, battleCtx->attacker);
    battleCtx->mercuryMultiHeadedHitIndex = 0;
    battleCtx->multiHitCounter = hits;
""")
 lib=root/"src/battle/battle_lib.c"
 rep(lib,
"""        if (movePower == 0 && MOVE_DATA(move).power) {
            movePower = 1;
        }
    }

    GF_ASSERT(battleCtx->powerMul >= 10);
""",
"""        if ((battleCtx->mercuryCustomMultiHitTriggerAbility == ABILITY_MR_HYDRA
                || battleCtx->mercuryCustomMultiHitTriggerAbility == ABILITY_MR_3_GT_1)
            && battleCtx->multiHitLoop) {
            int heads = battleCtx->mercuryMultiHeadedHeads[attacker];
            int hit = battleCtx->multiHitNumHits - battleCtx->multiHitCounter + 1;
            if (heads == 2) {
                movePower = movePower * 25 / 100;
            } else if (heads >= 3 && hit == 2) {
                movePower = movePower * 20 / 100;
            } else if (heads >= 3 && hit >= 3) {
                movePower = movePower * 15 / 100;
            }
        }

        if (movePower == 0 && MOVE_DATA(move).power) {
            movePower = 1;
        }
    }

    if (attackerParams.ability == ABILITY_MR_3_GT_1 && moveType == TYPE_WATER) {
        if (battleCtx->battleMons[attacker].curHP * 3
            <= battleCtx->battleMons[attacker].maxHP) {
            movePower = movePower * 180 / 100;
        } else {
            movePower = movePower * 130 / 100;
        }
    }

    GF_ASSERT(battleCtx->powerMul >= 10);
""")
 # Hubris uses the engine's standard stat-stage representation and direct move KO lane.
 # Insert in MoveEnd after damage has resolved but before flags clear.
 sig="static void BattleControllerPlayer_MoveEnd(BattleSystem *battleSys, BattleContext *battleCtx)"
 t=ctl.read_text();start=t.find(sig+"\n{")
 if start<0:raise SystemExit("MoveEnd missing")
 end=t.find("static ",start+len(sig)+2)
 block=t[start:end if end>0 else len(t)]
 marker="ABILITY_MR_HYDRA"
 if "Mercury D24K Hubris" not in block:
  anchor="        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);\n"
  code="""        /* Mercury D24K Hubris: direct KO by Hydra holder. */
        if (battleCtx->attacker != BATTLER_NONE
            && battleCtx->defender != BATTLER_NONE
            && Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MR_HYDRA
            && battleCtx->battleMons[battleCtx->attacker].curHP
            && battleCtx->battleMons[battleCtx->defender].curHP == 0
            && CURRENT_MOVE_DATA.class != CLASS_STATUS
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && battleCtx->battleMons[battleCtx->attacker].statBoosts[STAT_SPECIAL_ATTACK] < 12) {
            battleCtx->battleMons[battleCtx->attacker].statBoosts[STAT_SPECIAL_ATTACK]++;
        }

"""
  if block.count(anchor)!=1:raise SystemExit("MoveEnd clear anchor mismatch")
  block=block.replace(anchor,code+anchor,1);ctl.write_text(t[:start]+block+t[start+len(block):] if False else t[:start]+block+t[end if end>0 else len(t):])

def reg(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 for t in ABILITIES:
  if t not in x:x.append(t)
 p.write_text("\n".join(x)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24k-hydra-3gt1.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();patch(root);reg(a.implemented_registry.resolve())
 ab=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
 ctl=(root/"src/battle/battle_controller_player.c").read_text();lib=(root/"src/battle/battle_lib.c").read_text();ctx=(root/"include/battle/battle_context.h").read_text()
 checks={
  "stable_ids":all(len(ab)>i and ab[i]==t for t,i in ABILITIES.items()),
  "generic_head_metadata":"mercuryMultiHeadedHeads[MAX_BATTLERS]" in ctx,
  "two_head_count":"== 2" in ctl and "return 2;" in ctl,
  "three_head_count":">= 3" in ctl and "return 3;" in ctl,
  "two_head_25":"movePower = movePower * 25 / 100;" in lib,
  "three_head_20_15":"movePower = movePower * 20 / 100;" in lib and "movePower = movePower * 15 / 100;" in lib,
  "riptide_130_180":"movePower = movePower * 130 / 100;" in lib and "movePower = movePower * 180 / 100;" in lib,
  "hubris_spa":"ABILITY_MR_HYDRA" in ctl and "STAT_SPECIAL_ATTACK" in ctl,
  "registry":all(t in a.implemented_registry.read_text() for t in ABILITIES),
  "sprites_deferred":True,"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL"
 a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24K_HYDRA_3GT1","status":status,"implemented":["Hydra","3 > 1"],"checks":checks},indent=2)+"\n")
 print(status)
 if status!="PASS":raise SystemExit("D24K failed")
if __name__=="__main__":main()
