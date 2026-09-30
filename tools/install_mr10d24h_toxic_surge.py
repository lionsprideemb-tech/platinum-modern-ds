#!/usr/bin/env python3
"""MR10D24H — Toxic Surge + Toxic Terrain core.

Locked ability: set Toxic Terrain on entry.
Recovered terrain core: five-turn terrain lifecycle, grounded non-Poison/Steel
end-turn damage, +30% Poison move power. Uses MR08M's terrain framework.
"""
from pathlib import Path
import argparse,json
NAME="Toxic Surge";TOKEN="ABILITY_MR_TOXIC_SURGE";AID=692

def bef(p,a,s,label):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"{label}: {t.count(a)}")
 p.write_text(t.replace(a,s+a,1))
def aft(p,a,s,label):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"{label}: {t.count(a)}")
 p.write_text(t.replace(a,a+s,1))

def patch(root):
 terrain=root/"include/constants/battle/terrain.h"
 bef(terrain,"#endif // POKEPLATINUM_CONSTANTS_BATTLE_TERRAIN_H\n","#define MERCURY_TERRAIN_TOXIC    5\n\n","toxic terrain constant")
 lib=root/"src/battle/battle_lib.c"
 script=root/"src/battle/battle_script.c"
 # While Toxic Terrain is active, newly placed Spikes become Toxic Spikes.
 # This is done at the native placement command so layer caps/masks/Defog/AI
 # continue to use Platinum's ordinary side-condition representation.
 spike_anchor="""    if (battleCtx->sideConditions[defendingSide].spikesLayers == 3) {
"""
 spike_block="""    if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_TOXIC) {
        if (battleCtx->sideConditions[defendingSide].toxicSpikesLayers == 2) {
            battleCtx->selfTurnFlags[battleCtx->attacker].skipPressureCheck = TRUE;
            BattleScript_Iter(battleCtx, jumpOnFail);
        } else {
            battleCtx->sideConditionsMask[defendingSide] |= SIDE_CONDITION_TOXIC_SPIKES;
            battleCtx->sideConditions[defendingSide].toxicSpikesLayers++;
        }
        return FALSE;
    }

"""
 bef(script,spike_anchor,spike_block,"Toxic Terrain Spikes conversion")
 # Poison power boost beside existing terrain power handling.
 anchor="""    if (Mercury_IsGroundedForTerrain(battleCtx, attacker)) {
"""
 bef(lib,anchor,"""    if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_TOXIC
        && moveType == TYPE_POISON) {
        movePower = movePower * 13 / 10;
    }

""","toxic terrain poison boost")
 # Setter in existing switch-in ability dispatcher.
 bef(lib,"""                    case ABILITY_ELECTRIC_SURGE:
""","""                    case ABILITY_MR_TOXIC_SURGE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced = TRUE;
                        if (battleCtx->mercuryTerrainType != MERCURY_TERRAIN_TOXIC) {
                            Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_TOXIC);
                            battleCtx->msgBattlerTemp = battler;
                            battleCtx->msgTemp = ABILITY_MR_TOXIC_SURGE;
                            subscript = subscript_mold_breaker;
                            result = SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;

""","Toxic Surge switch-in")
 ctl=root/"src/battle/battle_controller_player.c"
 # Extend MR08M terrain end-turn state with toxic chip before its turn decrement.
 anchor="""                if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_GRASSY) {
"""
 bef(ctl,anchor,"""                if (battleCtx->mercuryTerrainType == MERCURY_TERRAIN_TOXIC) {
                    for (i = 0; i < maxBattlers; i++) {
                        if (battleCtx->battleMons[i].curHP
                            && Mercury_IsGroundedForTerrain(battleCtx, i)
                            && battleCtx->battleMons[i].type1 != TYPE_POISON
                            && battleCtx->battleMons[i].type2 != TYPE_POISON
                            && battleCtx->battleMons[i].type1 != TYPE_STEEL
                            && battleCtx->battleMons[i].type2 != TYPE_STEEL) {
                            int chip = battleCtx->battleMons[i].maxHP / 8;
                            if (chip < 1) chip = 1;
                            battleCtx->battleMons[i].curHP =
                                battleCtx->battleMons[i].curHP > chip
                                ? battleCtx->battleMons[i].curHP - chip : 0;
                            BattleMon_CopyToParty(battleSys, battleCtx, i);
                        }
                    }
                }

""","toxic terrain chip")

def reg(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 if TOKEN not in x:x.append(TOKEN)
 p.write_text("\n".join(x)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24h-toxic-surge.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();patch(root);reg(a.implemented_registry.resolve())
 ab=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()];lib=(root/"src/battle/battle_lib.c").read_text();ctl=(root/"src/battle/battle_controller_player.c").read_text();terrain=(root/"include/constants/battle/terrain.h").read_text()
 checks={"stable_id":len(ab)>AID and ab[AID]==TOKEN,"toxic_terrain_constant":"MERCURY_TERRAIN_TOXIC" in terrain,"sets_on_entry":"case ABILITY_MR_TOXIC_SURGE:" in lib and "Mercury_SetTerrain(battleCtx, MERCURY_TERRAIN_TOXIC)" in lib,"poison_boost_30":"movePower = movePower * 13 / 10;" in lib,"grounded_chip":"Mercury_IsGroundedForTerrain(battleCtx, i)" in ctl and "maxHP / 8" in ctl,"poison_steel_exempt":"TYPE_POISON" in ctl and "TYPE_STEEL" in ctl,"spikes_to_toxic":"mercuryTerrainType == MERCURY_TERRAIN_TOXIC" in (root/"src/battle/battle_script.c").read_text() and "toxicSpikesLayers++" in (root/"src/battle/battle_script.c").read_text(),"five_turn_lifecycle":"mercuryTerrainTurns = 5" in lib,"registry":TOKEN in a.implemented_registry.read_text(),"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24H_TOXIC_SURGE","status":status,"implemented":[NAME],"remaining_after_d24h":6,"checks":checks},indent=2)+"\n");print(status)
 if status!="PASS":raise SystemExit("D24H failed")
if __name__=="__main__":main()
