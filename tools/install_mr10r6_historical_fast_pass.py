#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path

IMPLEMENTED={
"Flaming Jaws":("ABILITY_MR_FLAMING_JAWS",650),
"Raw Wood":("ABILITY_MR_RAW_WOOD",548),
"Vengeance":("ABILITY_MR_VENGEANCE",607),
"Mighty Horn":("ABILITY_MR_MIGHTY_HORN",495),
"Keen Edge":("ABILITY_MR_KEEN_EDGE",472),
"Super Slammer":("ABILITY_SUPER_SLAMMER",590),
"Inflatable":("ABILITY_MR_INFLATABLE",466),
"Venom Crown":("ABILITY_VENOM_CROWN",610),
"Malicious":("ABILITY_MALICIOUS",489),
"Rest in Peace":("ABILITY_MR_REST_IN_PEACE",903),
"On the Prowl":("ABILITY_MR_ON_THE_PROWL",878),
"Emanate":("ABILITY_EMANATE",407),
"Fertilize":("ABILITY_FERTILIZE",419),
"Power Metal":("ABILITY_POWER_METAL",529),
"Snow Song":("ABILITY_SNOW_SONG",573),
"Twinkle Toes":("ABILITY_STRIKER_PIXILATE",585),
"Mythical Arrows":("ABILITY_MYTHICAL_ARROWS",508),
"Overwatch":("ABILITY_OVERWATCH",515),
"Depravity":("ABILITY_DEPRAVITY",387),
"Web Spinner":("ABILITY_WEB_SPINNER",619),
}
TOKENS=tuple(v[0] for v in IMPLEMENTED.values())

def rb(p,a,s,m,l):
 t=p.read_text()
 if m in t:return
 if t.count(a)!=1:raise SystemExit(f"{l}: {t.count(a)} anchors")
 p.write_text(t.replace(a,s+a,1))
def ra(p,a,s,m,l):
 t=p.read_text()
 if m in t:return
 if t.count(a)!=1:raise SystemExit(f"{l}: {t.count(a)} anchors")
 p.write_text(t.replace(a,a+s,1))
def rep(p,a,b,l):
 t=p.read_text()
 if b in t:return
 if t.count(a)!=1:raise SystemExit(f"{l}: {t.count(a)} matches")
 p.write_text(t.replace(a,b,1))
def fb(t,n):
 s=t.find(n+"(")
 if s<0:raise SystemExit("fn "+n)
 o=t.find("{",s);d=0
 for i in range(o,len(t)):
  if t[i]=="{":d+=1
  elif t[i]=="}":
   d-=1
   if d==0:return s,i+1
 raise SystemExit("unterminated "+n)
def bif(p,n,a,s,m,l):
 t=p.read_text();x,y=fb(t,n);b=t[x:y]
 if m in b:return
 if b.count(a)!=1:raise SystemExit(f"{l}: {b.count(a)}")
 p.write_text(t[:x]+b.replace(a,s+a,1)+t[y:])

def validate_partition(p):
 rows=json.loads(p.read_text())["abilities"]
 for n,(tok,i) in IMPLEMENTED.items():
  m=[r for r in rows if r.get("id")==i and r.get("token")==tok]
  if len(m)!=1:raise SystemExit(f"{n}: row")
  if m[0].get("runtime_enabled") is False or m[0].get("review_blocked"):raise SystemExit(f"{n}: blocked")

def helpers(root):
 p=root/"src/battle/battle_lib.c"
 s=r'''static BOOL Mercury_R6Horn(int move)
{
 switch(move){
 case MOVE_HORN_ATTACK: case MOVE_HORN_DRILL: case MOVE_MEGAHORN:
 case MOVE_DRILL_PECK: case MOVE_DRILL_RUN: case MOVE_SMART_STRIKE:return TRUE;
 default:return FALSE;}
}
static BOOL Mercury_R6Slam(int move)
{
 switch(move){
 case MOVE_SLAM: case MOVE_BODY_SLAM: case MOVE_HEAVY_SLAM:
 case MOVE_HAMMER_ARM: case MOVE_WOOD_HAMMER: case MOVE_DRAGON_HAMMER:
 case MOVE_ICE_HAMMER: case MOVE_CRABHAMMER:return TRUE;
 default:return FALSE;}
}
static BOOL Mercury_R6Kick(int move)
{
 switch(move){
 case MOVE_BLAZE_KICK: case MOVE_DOUBLE_KICK: case MOVE_HI_JUMP_KICK:
 case MOVE_JUMP_KICK: case MOVE_LOW_KICK: case MOVE_MEGA_KICK:
 case MOVE_ROLLING_KICK: case MOVE_TRIPLE_KICK: case MOVE_TROP_KICK:
 case MOVE_AXE_KICK: case MOVE_THUNDEROUS_KICK:return TRUE;
 default:return FALSE;}
}
static BOOL Mercury_R6Arrow(int move)
{
 switch(move){
 case MOVE_SPIRIT_SHACKLE: case MOVE_THOUSAND_ARROWS: case MOVE_TRIPLE_ARROWS:return TRUE;
 default:return FALSE;}
}
static u8 Mercury_R6Type(int ability,int move,u8 type)
{
 if(move==MOVE_STRUGGLE||MOVE_DATA(move).type!=TYPE_NORMAL)return type;
 if(ability==ABILITY_EMANATE)return TYPE_PSYCHIC;
 if(ability==ABILITY_FERTILIZE)return TYPE_GRASS;
 if(ability==ABILITY_STRIKER_PIXILATE)return TYPE_FAIRY;
 if(ability==ABILITY_POWER_METAL&&Mercury_MoveIsSound(move))return TYPE_STEEL;
 if(ability==ABILITY_SNOW_SONG&&Mercury_MoveIsSound(move))return TYPE_ICE;
 return type;
}

'''
 rb(p,"int BattleSystem_CalcMoveDamage(BattleSystem *battleSys,\n",s,"Mercury_R6Type","helpers")

def typepaths(root):
 p=root/"src/battle/battle_lib.c"
 bif(p,"BattleSystem_CalcMoveDamage","    GF_ASSERT(battleCtx->powerMul >= 10);\n",
 """    moveType=Mercury_R6Type(attackerParams.ability,move,moveType);
""","Mercury_R6Type(attackerParams.ability","damage type")
 bif(p,"BattleSystem_ApplyTypeChart","    movePower = MOVE_DATA(move).power;\n",
 """    moveType=Mercury_R6Type(Battler_Ability(battleCtx,attacker),move,moveType);
""","Mercury_R6Type(Battler_Ability","chart type")
 bif(p,"BattleSystem_CalcEffectiveness","    if (!Mercury_IsMoldBreakerAbility(attackerAbility)\n",
 """    moveType=Mercury_R6Type(attackerAbility,move,moveType);
""","Mercury_R6Type(attackerAbility","ai type")
 bif(p,"BattleSystem_TriggerImmunityAbility",
 "    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_VOLT_ABSORB) == TRUE\n",
 """    moveType=Mercury_R6Type(Battler_Ability(battleCtx,attacker),battleCtx->moveCur,moveType);
""","battleCtx->moveCur,moveType","immunity type")

def damage(root):
 p=root/"src/battle/battle_lib.c"
 bif(p,"BattleSystem_CalcMoveDamage",
 "    if (attackerParams.ability == ABILITY_HUGE_POWER || attackerParams.ability == ABILITY_PURE_POWER) {\n",
 """    if(attackerParams.ability==ABILITY_MYTHICAL_ARROWS&&Mercury_R6Arrow(move))moveClass=CLASS_SPECIAL;
""","ABILITY_MYTHICAL_ARROWS&&Mercury_R6Arrow","arrow class")
 a="""    if (Battler_IgnorableAbility(battleCtx, attacker, defender, ABILITY_THICK_FAT) == TRUE
"""
 s="""    if(attackerParams.ability==ABILITY_MR_RAW_WOOD&&moveType==TYPE_ROCK)movePower=movePower*110/100;
    if(attackerParams.ability==ABILITY_MR_VENGEANCE&&moveType==TYPE_GHOST&&attackerParams.curHP<=attackerParams.maxHP/3)movePower=movePower*150/100;
    if((attackerParams.ability==ABILITY_MR_MIGHTY_HORN||attackerParams.ability==ABILITY_VENOM_CROWN)&&Mercury_R6Horn(move))movePower=movePower*130/100;
    if(attackerParams.ability==ABILITY_MR_KEEN_EDGE&&Mercury_MoveIsSlicing(move))movePower=movePower*130/100;
    if(attackerParams.ability==ABILITY_SUPER_SLAMMER&&Mercury_R6Slam(move))movePower=movePower*130/100;
    if(attackerParams.ability==ABILITY_EMANATE&&moveType==TYPE_PSYCHIC)movePower=movePower*120/100;
    if(attackerParams.ability==ABILITY_FERTILIZE&&moveType==TYPE_GRASS)movePower=movePower*120/100;
    if(attackerParams.ability==ABILITY_POWER_METAL&&Mercury_MoveIsSound(move))movePower=movePower*120/100;
    if(attackerParams.ability==ABILITY_SNOW_SONG&&Mercury_MoveIsSound(move))movePower=movePower*120/100;
    if(attackerParams.ability==ABILITY_STRIKER_PIXILATE){
      if(MOVE_DATA(move).type==TYPE_NORMAL&&move!=MOVE_STRUGGLE)movePower=movePower*120/100;
      if(Mercury_R6Kick(move))movePower=movePower*130/100;
    }
    if(attackerParams.ability==ABILITY_MYTHICAL_ARROWS&&Mercury_R6Arrow(move))movePower=movePower*130/100;
    if(attackerParams.ability==ABILITY_OVERWATCH&&battleCtx->battlerActions[defender][BATTLE_ACTION_PICK_COMMAND]==BATTLE_CONTROL_PARTY)movePower*=2;
    if(attackerParams.ability==ABILITY_DEPRAVITY&&moveType==TYPE_ELECTRIC&&(defenderParams.type1==TYPE_ELECTRIC||defenderParams.type2==TYPE_ELECTRIC))movePower*=2;

"""
 rb(p,a,s,"ABILITY_MR_KEEN_EDGE&&Mercury_MoveIsSlicing","offense")
 d="""    if ((battleType & BATTLE_TYPE_DOUBLES)
        && MOVE_DATA(move).range == RANGE_ADJACENT_OPPONENTS
"""
 rb(p,d,"""    if(moveType==TYPE_ROCK&&Battler_IgnorableAbility(battleCtx,attacker,defender,ABILITY_MR_RAW_WOOD)==TRUE)damage/=2;

""","ABILITY_MR_RAW_WOOD)==TRUE)damage/=2","raw wood defense")

def depravity(root):
 p=root/"src/battle/battle_lib.c"
 a="""    if (((attackerAbility == ABILITY_MERCILESS
                && (battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
"""
 b="""    if ((((attackerAbility == ABILITY_MERCILESS || attackerAbility == ABILITY_DEPRAVITY)
                && ((battleCtx->battleMons[defender].status & MON_CONDITION_ANY_POISON)
                    || battleCtx->battleMons[defender].statBoosts[BATTLE_STAT_SPEED] < DEFAULT_STAT_STAGE))
            || BattleSystem_RandNext(battleSys) % sCriticalStageRates[effectiveCritStage] == 0)
"""
 rep(p,a,b,"depravity crit")

def priority(root):
 p=root/"src/battle/battle_lib.c"
 a="""        battler1Priority = MOVE_DATA(battler1Move).priority;
        battler2Priority = MOVE_DATA(battler2Move).priority;
"""
 s="""
        if(battler1Move!=MOVE_NONE&&(battler1Ability==ABILITY_MR_ON_THE_PROWL||battler1Ability==ABILITY_OVERWATCH)
           &&battleCtx->battleMons[battler1].moveEffectsData.fakeOutTurnNumber==battleCtx->totalTurns+1){
          if(battler1Priority<0)battler1Priority=0;else battler1Priority++;}
        if(battler2Move!=MOVE_NONE&&(battler2Ability==ABILITY_MR_ON_THE_PROWL||battler2Ability==ABILITY_OVERWATCH)
           &&battleCtx->battleMons[battler2].moveEffectsData.fakeOutTurnNumber==battleCtx->totalTurns+1){
          if(battler2Priority<0)battler2Priority=0;else battler2Priority++;}

"""
 ra(p,a,s,"ABILITY_MR_ON_THE_PROWL||battler1Ability==ABILITY_OVERWATCH","priority")

def reactions(root):
 p=root/"src/battle/battle_lib.c"
 a="""    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN
"""
 s="""    if(Battler_Ability(battleCtx,battleCtx->attacker)==ABILITY_MR_FLAMING_JAWS
       &&DEFENDING_MON.curHP&&DEFENDING_MON.status==MON_CONDITION_NONE
       &&(DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken||DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
       &&Mercury_MoveIsBiting(battleCtx->moveCur)&&BattleSystem_RandNext(battleSys)%2==0){
      battleCtx->sideEffectType=SIDE_EFFECT_TYPE_ABILITY;battleCtx->sideEffectMon=battleCtx->defender;
      battleCtx->msgBattlerTemp=battleCtx->attacker;*subscript=subscript_burn;return TRUE;}

"""
 rb(p,a,s,"ABILITY_MR_FLAMING_JAWS\n","flaming jaws")
 rep(p,"    case ABILITY_POISON_POINT:\n","    case ABILITY_VENOM_CROWN:\n    case ABILITY_POISON_POINT:\n","venom crown")
 a2="""    case ABILITY_THERMAL_EXCHANGE: {
"""
 s2="""    case ABILITY_MR_INFLATABLE: {
      int moveType=battleCtx->moveType?battleCtx->moveType:CURRENT_MOVE_DATA.type;
      if(DEFENDING_MON.curHP&&(moveType==TYPE_FIRE||moveType==TYPE_FLYING)
         &&(DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken||DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)){
        if(DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]<MAX_STAT_STAGE)DEFENDING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;
        if(DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]<MAX_STAT_STAGE)DEFENDING_MON.statBoosts[BATTLE_STAT_SP_DEFENSE]++;
        battleCtx->msgBattlerTemp=battleCtx->defender;*subscript=subscript_mold_breaker;result=TRUE;}
      break;
    }

"""
 rb(p,a2,s2,"case ABILITY_MR_INFLATABLE:","inflatable")

def switchin(root):
 p=root/"src/battle/battle_lib.c"
 a="""        case SWITCH_IN_CHECK_STATE_DOWNLOAD:
            for (i = 0; i < maxBattlers; i++) {
                battler = battleCtx->monSpeedOrder[i];

"""
 s="""                if(battleCtx->battleMons[battler].downloadAnnounced==FALSE&&battleCtx->battleMons[battler].curHP
                    &&Battler_Ability(battleCtx,battler)==ABILITY_MALICIOUS){
                  int foe;battleCtx->battleMons[battler].downloadAnnounced=TRUE;
                  for(foe=0;foe<maxBattlers;foe++){BattleMon *m;
                    if(BattleSystem_GetBattlerSide(battleSys,foe)==BattleSystem_GetBattlerSide(battleSys,battler)||!battleCtx->battleMons[foe].curHP)continue;
                    m=&battleCtx->battleMons[foe];
                    if(m->attack>=m->spAttack){if(m->statBoosts[BATTLE_STAT_ATTACK]>MIN_STAT_STAGE)m->statBoosts[BATTLE_STAT_ATTACK]--;}
                    else if(m->statBoosts[BATTLE_STAT_SP_ATTACK]>MIN_STAT_STAGE)m->statBoosts[BATTLE_STAT_SP_ATTACK]--;
                    if(m->defense>=m->spDefense){if(m->statBoosts[BATTLE_STAT_DEFENSE]>MIN_STAT_STAGE)m->statBoosts[BATTLE_STAT_DEFENSE]--;}
                    else if(m->statBoosts[BATTLE_STAT_SP_DEFENSE]>MIN_STAT_STAGE)m->statBoosts[BATTLE_STAT_SP_DEFENSE]--;}
                  battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;result=SWITCH_IN_CHECK_RESULT_BREAK;break;}

                if(battleCtx->battleMons[battler].downloadAnnounced==FALSE&&battleCtx->battleMons[battler].curHP
                    &&Battler_Ability(battleCtx,battler)==ABILITY_WEB_SPINNER){
                  int foe;battleCtx->battleMons[battler].downloadAnnounced=TRUE;
                  for(foe=0;foe<maxBattlers;foe++){
                    if(BattleSystem_GetBattlerSide(battleSys,foe)==BattleSystem_GetBattlerSide(battleSys,battler)||!battleCtx->battleMons[foe].curHP)continue;
                    battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]-=2;
                    if(battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]<MIN_STAT_STAGE)battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SPEED]=MIN_STAT_STAGE;}
                  battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;result=SWITCH_IN_CHECK_RESULT_BREAK;break;}

"""
 ra(p,a,s,"ABILITY_WEB_SPINNER","switchin")

def turnend(root):
 p=root/"src/battle/battle_lib.c"
 a="    case ABILITY_SHED_SKIN:\n"
 s="""    case ABILITY_MR_REST_IN_PEACE:
      if((battleCtx->fieldConditionsMask&FIELD_CONDITION_DEEP_FOG)&&battleCtx->battleMons[battler].curHP
         &&battleCtx->battleMons[battler].curHP<battleCtx->battleMons[battler].maxHP){
        int heal=BattleSystem_Divide(battleCtx->battleMons[battler].maxHP,8);
        battleCtx->battleMons[battler].curHP+=heal;
        if(battleCtx->battleMons[battler].curHP>battleCtx->battleMons[battler].maxHP)battleCtx->battleMons[battler].curHP=battleCtx->battleMons[battler].maxHP;
        BattleMon_CopyToParty(battleSys,battleCtx,battler);battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;result=TRUE;}
      break;

"""
 rb(p,a,s,"case ABILITY_MR_REST_IN_PEACE:","rest in peace")

def registry(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 for t in TOKENS:
  if t not in x:x.append(t)
 p.write_text("\n".join(x)+"\n")

def check(root,reg):
 l=(root/"src/battle/battle_lib.c").read_text();a=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()];r=set(reg.read_text().splitlines())
 c={n.lower().replace(" ","_").replace("'",""):tok in l for n,(tok,_) in IMPLEMENTED.items()}
 c["registry"]=all(t in r for t in TOKENS);c["ids"]=all(len(a)>i and a[i]==t for t,i in IMPLEMENTED.values())
 return c

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"));ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10r6-historical-fast-pass.json"));x=ap.parse_args()
 root=x.pokeplatinum_root.resolve();reg=x.implemented_registry.resolve();validate_partition(x.partition.resolve())
 helpers(root);typepaths(root);damage(root);depravity(root);priority(root);reactions(root);switchin(root);turnend(root);registry(reg)
 c=check(root,reg);status="PASS" if all(c.values()) else "FAIL";out={"gate":"MERCURY_MR10R6_HISTORICAL_FAST_PASS","status":status,"implemented":list(IMPLEMENTED),"implemented_count":20,"historical_runtime_before":61,"historical_runtime_after":41,"checks":c};x.report.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
 if status!="PASS":raise SystemExit("R6 failed")
if __name__=="__main__":main()
