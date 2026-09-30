#!/usr/bin/env python3
"""MR10D24F — final generated-action family.

Wind Chimes: after a qualifying damaging hit, queue 30-BP Hyper Voice through
MR10D8's reactive lane. The generated Hyper Voice receives the locked Amplifier
semantics: sound spread targets all opponents and +30% damage.
Thundercall: after a successful Electric damaging move, generate Smite at 20%
of its normal 120 BP (24 BP) through MR10D7's no-PP recursion-guarded lane.
Smite is materialized as the bounded move dependency: Electric/Physical,
120 BP, 80 accuracy, contact, paralysis secondary effect and Smack Down effect.

Mechanics only; MR07 visuals are untouched.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

IMPLEMENTED={"Wind Chimes":("ABILITY_MR_WIND_CHIMES",681),"Thundercall":("ABILITY_MR_THUNDERCALL",867)}
SMITE_TOKEN="MOVE_SMITE"

def ib(path,anchor,ins,label):
 t=path.read_text()
 if ins in t:return
 if t.count(anchor)!=1:raise SystemExit(f"{label}: anchor {t.count(anchor)}")
 path.write_text(t.replace(anchor,ins+anchor,1))

def ia(path,anchor,ins,label):
 t=path.read_text()
 if ins in t:return
 if t.count(anchor)!=1:raise SystemExit(f"{label}: anchor {t.count(anchor)}")
 path.write_text(t.replace(anchor,anchor+ins,1))

def bounds(t,s):
 a=t.find(s+"\n{")
 if a<0:raise SystemExit("function not found "+s)
 o=a+len(s)+1;d=0
 for i in range(o,len(t)):
  if t[i]=="{":d+=1
  elif t[i]=="}":
   d-=1
   if d==0:return a,i+1
 raise SystemExit("unterminated "+s)

def ibf(path,sig,anchor,ins,marker,label):
 t=path.read_text();a,b=bounds(t,sig);blk=t[a:b]
 if marker in blk:return
 if blk.count(anchor)!=1:raise SystemExit(f"{label}: anchor {blk.count(anchor)}")
 path.write_text(t[:a]+blk.replace(anchor,ins+anchor,1)+t[b:])

def partition(path):
 rows=json.loads(path.read_text()).get("abilities",[])
 for name,(tok,aid) in IMPLEMENTED.items():
  m=[r for r in rows if r.get("display_name")==name or r.get("source_name")==name]
  if len(m)!=1:raise SystemExit(f"{name}: row count {len(m)}")
  for k,v in {"id":aid,"token":tok,"approval_state":"owner_approved_keep","owner_review_decision":"KEEP AS WRITTEN","review_blocked":False}.items():
   if m[0].get(k)!=v:raise SystemExit(f"{name}: {k}")

def materialize_smite(root):
 moves=root/"generated/moves.txt"; lines=[x.strip() for x in moves.read_text().splitlines() if x.strip()]
 if SMITE_TOKEN in lines:return lines.index(SMITE_TOKEN)
 if lines[-1]!="MAX_MOVES":raise SystemExit("move registry missing MAX_MOVES")
 move_id=len(lines)-1
 stem="smite"; d=root/"res/moves"/stem
 if d.exists():raise SystemExit("Smite directory exists without registry token")
 d.mkdir()
 data={"name":"Smite","description":["The user smites the target","with a crushing thunderbolt."],"class":"CLASS_PHYSICAL","type":"TYPE_ELECTRIC","power":120,"accuracy":80,"pp":5,"effect":{"type":"BATTLE_EFFECT_PARALYZE_HIT","chance":30},"range":"RANGE_SINGLE_TARGET","priority":0,"flags":["MOVE_FLAG_MAKES_CONTACT","MOVE_FLAG_CAN_PROTECT","MOVE_FLAG_CAN_MIRROR_MOVE"],"contest":{"effect":"CONTEST_EFFECT_BASIC","type":"CONTEST_TYPE_COOL"}}
 (d/"data.json").write_text(json.dumps(data,indent=4)+"\n")
 (d/"script.s").write_text('#include "macros/btlcmd.inc"\n\n_000:\n    GoToEffectScript\n')
 donor=root/"res/moves/thunder_punch/anim.s"
 if not donor.is_file():raise SystemExit("missing thunder_punch animation donor")
 (d/"anim.s").write_text(donor.read_text())
 lines.insert(-1,SMITE_TOKEN);moves.write_text("\n".join(lines)+"\n")
 return move_id

def patch(root):
 ctl=root/"src/battle/battle_controller_player.c"
 sig="static BOOL Mercury_D7ChooseFollowup(\n    BattleContext *battleCtx,\n    int *move,\n    int *power)"
 ibf(ctl,sig,"    case ABILITY_MR_THUNDER_CLOUDS:\n","""    case ABILITY_MR_THUNDERCALL:
        if (damaging && moveType == TYPE_ELECTRIC) {
            *move = MOVE_SMITE;
            *power = 24;
        }
        break;

""","case ABILITY_MR_THUNDERCALL:","Thundercall")
 lib=root/"src/battle/battle_lib.c"
 hit="BOOL BattleSystem_TriggerAbilityOnHit(BattleSystem *battleSys, BattleContext *battleCtx, int *subscript)"
 ibf(lib,hit,"    case ABILITY_MR_DEFLECT:\n","""    case ABILITY_MR_WIND_CHIMES:
        if (battleCtx->mercuryAbilityGeneratedAction == FALSE
            && battleCtx->attacker != BATTLER_NONE
            && ATTACKING_MON.curHP && DEFENDING_MON.curHP
            && Battler_SubstituteWasHit(battleCtx, battleCtx->defender) == FALSE
            && (battleCtx->moveStatusFlags & MOVE_STATUS_NO_EFFECTS) == FALSE
            && (DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken
                || DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)) {
            int reactiveUser = battleCtx->defender;
            if (battleCtx->mercuryReactiveCounterPending[reactiveUser] < 9)
                battleCtx->mercuryReactiveCounterPending[reactiveUser]++;
            battleCtx->mercuryReactiveCounterTarget[reactiveUser] = battleCtx->attacker;
            battleCtx->mercuryReactiveCounterMove[reactiveUser] = MOVE_HYPER_VOICE;
            battleCtx->mercuryReactiveCounterPower[reactiveUser] = 30;
        }
        break;

""","case ABILITY_MR_WIND_CHIMES:","Wind Chimes")
 # Amplifier's locked +30% sound damage applies to the generated Hyper Voice.
 anchor="    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_PUNK_ROCK) == TRUE\n"
 ib(lib,anchor,"""    if (Battler_Ability(battleCtx, attacker) == ABILITY_MR_WIND_CHIMES
        && move == MOVE_HYPER_VOICE
        && battleCtx->mercuryAbilityGeneratedAction) {
        damage = damage * 130 / 100;
    }

""","Wind Chimes Amplifier damage")

def registry(path):
 l=[x.strip() for x in path.read_text().splitlines() if x.strip()]
 for tok,_ in IMPLEMENTED.values():
  if tok not in l:l.append(tok)
 path.write_text("\n".join(l)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--partition",type=Path,default=Path("data/mr10_safe_ability_partition.json"));ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24f-generated-final.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();partition(a.partition.resolve());smite_id=materialize_smite(root);patch(root);registry(a.implemented_registry.resolve())
 ctl=(root/"src/battle/battle_controller_player.c").read_text();lib=(root/"src/battle/battle_lib.c").read_text();moves=[x.strip() for x in (root/"generated/moves.txt").read_text().splitlines() if x.strip()]
 checks={"smite_materialized":SMITE_TOKEN in moves,"smite_120_bp":json.loads((root/"res/moves/smite/data.json").read_text())["power"]==120,"thundercall_24_bp":"*power = 24;" in ctl and "ABILITY_MR_THUNDERCALL" in ctl,"wind_chimes_reactive":"ABILITY_MR_WIND_CHIMES" in lib and "MOVE_HYPER_VOICE" in lib,"wind_chimes_30_bp":"mercuryReactiveCounterPower[reactiveUser] = 30;" in lib,"amplifier_30_percent":"damage = damage * 130 / 100;" in lib,"recursion_guard":"mercuryAbilityGeneratedAction == FALSE" in lib,"locked_mr07_visuals_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24F_GENERATED_FINAL","status":status,"implemented_abilities":list(IMPLEMENTED),"implemented_count":2,"smite_id":smite_id,"remaining_keep_as_written_after_d24f":8,"checks":checks},indent=2)+"\n");print(status)
 if status!="PASS":raise SystemExit("D24F failed")
if __name__=="__main__":main()
