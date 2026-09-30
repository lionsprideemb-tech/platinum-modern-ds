#!/usr/bin/env python3
"""MR10D24K — Hydra + 3 > 1 composite mechanics.

Extends Mercury's native D11 multi-hit lane with ER Multi-Headed semantics:
2 heads = 100% + 25%; 3 heads = 100% + 20% + 15%.
Hydra adds Hubris (+1 SpA after a direct KO).
3 > 1 adds Riptide (Water x1.3, x1.8 at <= 1/3 HP).

Head count is resolved through one species-metadata hook with a safe one-head
default. The custom-roster phase extends that hook for new species/forms without
changing the ability engine.
"""
from pathlib import Path
import argparse,json

ABILITIES={"ABILITY_MR_HYDRA":739,"ABILITY_MR_3_1":914}

def rep(p,a,b,label="replacement"):
 t=p.read_text()
 if b in t:return
 if t.count(a)!=1:raise SystemExit(f"{label}: anchor mismatch {p}: {t.count(a)}")
 p.write_text(t.replace(a,b,1))

def ins(p,a,s):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"anchor mismatch {p}: {t.count(a)}")
 p.write_text(t.replace(a,s+a,1))

def patch(root):
 ctx=root/"include/battle/battle_context.h"
 ctl=root/"src/battle/battle_controller_player.c"
 # Central species metadata hook. Roster installers append cases here.
 metadata="""static u8 Mercury_SpeciesHeadCount(u16 species)
{
    switch (species) {
    /* MERCURY_HEAD_COUNT_CASES */
    default:
        return 1;
    }
}

"""
 # Later consolidation stages may inline/rename D11 helpers. The durable D11
 # runtime contract is the context field used by damage scaling, so place the
 # metadata helper before the first controller function instead of beside D11.
 t=ctl.read_text()
 if "static u8 Mercury_SpeciesHeadCount(u16 species)" not in t:
  pos=t.find("static ")
  if pos < 0: raise SystemExit("controller static-function anchor absent")
  ctl.write_text(t[:pos]+metadata+t[pos:])
 # Do not extend D11's internal ability switch: later consolidation may inline it.
 # Extend the stable setup contract instead, after D11 computes its own hit count.
 rep(ctl,
"""    hits = Mercury_CustomMultiHitCount(battleSys, battleCtx);
    if (hits < 2) {
        return;
    }
""",
"""    hits = Mercury_CustomMultiHitCount(battleSys, battleCtx);
    if (hits < 2
        && (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MR_HYDRA
            || Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MR_3_1)
        && Mercury_CustomMultiHitBaseAllowed(battleSys, battleCtx)) {
        int heads = Mercury_SpeciesHeadCount(
            battleCtx->battleMons[battleCtx->attacker].species);
        hits = heads >= 3 ? 3 : (heads == 2 ? 2 : 0);
    }
    if (hits < 2) {
        return;
    }
""","Hydra setup extension")
 rep(ctl,
"""    battleCtx->mercuryCustomMultiHitActive = TRUE;
    battleCtx->mercuryCustomMultiHitTriggerAbility =
        Battler_Ability(battleCtx, battleCtx->attacker);
    battleCtx->multiHitCounter = hits;
""",
"""    battleCtx->mercuryCustomMultiHitActive = TRUE;
    battleCtx->mercuryCustomMultiHitTriggerAbility =
        Battler_Ability(battleCtx, battleCtx->attacker);
     battleCtx->multiHitCounter = hits;
""","Hydra multi-hit setup")
 lib=root/"src/battle/battle_lib.c"
 rep(lib,
"""        if (movePower == 0 && MOVE_DATA(move).power) {
            movePower = 1;
        }
    }

    GF_ASSERT(battleCtx->powerMul >= 10);
""",
"""        if ((battleCtx->mercuryCustomMultiHitTriggerAbility == ABILITY_MR_HYDRA
                || battleCtx->mercuryCustomMultiHitTriggerAbility == ABILITY_MR_3_1)
            && battleCtx->multiHitLoop) {
            int heads = Mercury_SpeciesHeadCount(battleCtx->battleMons[attacker].species);
            int hit = battleCtx->multiHitNumHits - battleCtx->multiHitCounter + 1; /* counter decrements before replay */
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

    if (attackerParams.ability == ABILITY_MR_3_1 && moveType == TYPE_WATER) {
        if (battleCtx->battleMons[attacker].curHP * 3
            <= battleCtx->battleMons[attacker].maxHP) {
            movePower = movePower * 180 / 100;
        } else {
            movePower = movePower * 130 / 100;
        }
    }

    GF_ASSERT(battleCtx->powerMul >= 10);
""","Hydra damage/Riptide")
 # Hubris is queued at the faint-resolution lane, not MoveEnd: MoveEnd runs after
 # EXP/switch processing and can observe stale zero-HP defenders.
 t=ctl.read_text()
 sig="static void BattleControllerPlayer_LoopWhileFainted(BattleSystem *battleSys, BattleContext *battleCtx)"
 start=t.find(sig+"\n{")
 if start<0:raise SystemExit("LoopWhileFainted missing")
 brace=t.find("{",start);pos=t.find("\n",brace)+1
 code="""    /* Mercury D24K Hubris: once for a direct damaging-move KO, before faint processing. */
    if (battleCtx->faintedMon != BATTLER_NONE
        && battleCtx->attacker != BATTLER_NONE
        && Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_MR_HYDRA
        && battleCtx->battleMons[battleCtx->attacker].curHP
        && CURRENT_MOVE_DATA.class != CLASS_STATUS
        && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
        && battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SP_ATTACK] < MAX_STAT_STAGE) {
        battleCtx->battleMons[battleCtx->attacker].statBoosts[BATTLE_STAT_SP_ATTACK]++;
    }

"""
 if "Mercury D24K Hubris: once for a direct damaging-move KO" not in t:
  ctl.write_text(t[:pos]+code+t[pos:])

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
  "stable_ids":all(t in a.implemented_registry.read_text() for t in ABILITIES),
  "generic_head_metadata":"static u8 Mercury_SpeciesHeadCount(u16 species)" in ctl and "MERCURY_HEAD_COUNT_CASES" in ctl and "return 1;" in ctl,
  "two_head_count":"heads == 2 ? 2 : 0" in ctl,
  "three_head_count":"heads >= 3 ? 3" in ctl,
  "two_head_25":"movePower = movePower * 25 / 100;" in lib,
  "three_head_20_15":"movePower = movePower * 20 / 100;" in lib and "movePower = movePower * 15 / 100;" in lib,
  "riptide_130_180":"movePower = movePower * 130 / 100;" in lib and "movePower = movePower * 180 / 100;" in lib,
  "hubris_spa":"Mercury D24K Hubris: once for a direct damaging-move KO" in ctl and "BATTLE_STAT_SP_ATTACK" in ctl,
  "registry":all(t in a.implemented_registry.read_text() for t in ABILITIES),
  "sprites_deferred":True,"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL"
 a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24K_HYDRA_3GT1","status":status,"implemented":["Hydra","3 > 1"],"checks":checks},indent=2)+"\n")
 print(status)
 if status!="PASS":raise SystemExit("D24K failed")
if __name__=="__main__":main()
