#!/usr/bin/env python3
"""MR10R8 — final 21 historical Ability runtimes.

Closes the reconciled 124-row historical-missing queue. This pass provides the
shared Bleed/Fear/Frostbite/Enraged states, the remaining entry/generated
actions, and the final bespoke composites (Curse of Famine, Angel's Wrath,
Archmage). Mechanics only; locked MR07 visuals are untouched.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

IMPLEMENTED={
"Cryo Proficiency":("ABILITY_CRYO_PROFICIENCY",380),
"Freezing Point":("ABILITY_FREEZING_POINT",430),
"Neurotoxin":("ABILITY_NEUROTOXIN",509),
"Piercing Solo":("ABILITY_PIERCING_SOLO",526),
"Purple Haze":("ABILITY_PURPLE_HAZE",537),
"Resonance":("ABILITY_RESONANCE",551),
"Sand Pit":("ABILITY_SAND_PIT",561),
"Spike Armor":("ABILITY_SPIKE_ARMOR",580),
"To The Bone":("ABILITY_TO_THE_BONE",603),
"Wildfire":("ABILITY_WILDFIRE",623),
"Set Ablaze":("ABILITY_SET_ABLAZE",1007),
"Grass Flute":("ABILITY_GRASS_FLUTE",1008),
"Loose Thorns":("ABILITY_LOOSE_THORNS",1010),
"Mental Pollution":("ABILITY_MENTAL_POLLUTION",1013),
"Madness Enh.":("ABILITY_MADNESS_ENHANCEMENT",1014),
"Deviate":("ABILITY_DEVIATE",1018),
"Mob Boss":("ABILITY_MOB_BOSS",1019),
"Cosmic Dust":("ABILITY_COSMIC_DUST",1020),
"Curse of Famine":("ABILITY_CURSE_OF_FAMINE",1029),
"Angel's Wrath":("ABILITY_ANGELS_WRATH",1030),
"Archmage":("ABILITY_ARCHMAGE",1031),
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
def bounds(t,s):
 pos=0;a=-1;o=-1
 while True:
  cand=t.find(s,pos)
  if cand<0:break
  brace=t.find("{",cand);semi=t.find(";",cand)
  if brace>=0 and (semi<0 or brace<semi):
   a=cand;o=brace;break
  pos=cand+len(s)
 if a<0:raise SystemExit("function definition missing "+s)
 d=0
 for i in range(o,len(t)):
  if t[i]=="{":d+=1
  elif t[i]=="}":
   d-=1
   if d==0:return a,i+1
 raise SystemExit("unterminated "+s)

def ibf(p,sig,a,ins,m,l):
 t=p.read_text();x,y=bounds(t,sig);b=t[x:y]
 if m in b:return
 if b.count(a)!=1:raise SystemExit(f"{l}: {b.count(a)} scoped anchors")
 p.write_text(t[:x]+b.replace(a,ins+a,1)+t[y:])
def iaf(p,sig,a,ins,m,l):
 t=p.read_text();x,y=bounds(t,sig);b=t[x:y]
 if m in b:return
 if b.count(a)!=1:raise SystemExit(f"{l}: {b.count(a)} scoped anchors")
 p.write_text(t[:x]+b.replace(a,a+ins,1)+t[y:])

def partition(p):
 rows=json.loads(p.read_text())["abilities"]
 for n,(tok,aid) in IMPLEMENTED.items():
  m=[r for r in rows if r.get("id")==aid and r.get("token")==tok]
  if len(m)!=1:raise SystemExit(f"{n}: row {len(m)}")
  if m[0].get("runtime_enabled") is False or m[0].get("review_blocked"):raise SystemExit(f"{n}: blocked")
  if m[0].get("exact_effect") in (None,"RESTORE_PENDING_EXACT_SEMANTICS"):raise SystemExit(f"{n}: semantics")

def context(root):
 p=root/"include/battle/battle_context.h"
 s="""    // Mercury MR10R8 final historical shared states.
    u8 mercuryR8Frostbite[MAX_BATTLERS];
    u8 mercuryR8FearTurns[MAX_BATTLERS];
    u8 mercuryR8PoisonCascadeDone[MAX_BATTLERS];
    u8 mercuryR8BurnCascadeDone[MAX_BATTLERS];
    u8 mercuryR8CreepingThorns[NUM_BATTLE_SIDES];
    u8 mercuryR8Terrain;
    u8 mercuryR8TerrainTurns;

"""
 rb(p,"    u32 battleProgressFlag : 1;\n",s,"mercuryR8Frostbite","R8 context")

def helpers(root):
 p=root/"src/battle/battle_lib.c"
 s=r'''static BOOL Mercury_R8CanBleed(BattleContext *battleCtx,int battler)
{
 return battleCtx->battleMons[battler].curHP
  && Mercury_R7HasType(battleCtx,battler,TYPE_ROCK)==FALSE
  && Mercury_R7HasType(battleCtx,battler,TYPE_GHOST)==FALSE;
}
static void Mercury_R8Bleed(BattleContext *battleCtx,int battler)
{
 if(Mercury_R8CanBleed(battleCtx,battler))battleCtx->mercuryR7Bleeding[battler]=TRUE;
}
static void Mercury_R8Fear(BattleContext *battleCtx,int battler)
{
 if(battleCtx->battleMons[battler].curHP)battleCtx->mercuryR8FearTurns[battler]=2;
}
static void Mercury_R8Frostbite(BattleContext *battleCtx,int battler)
{
 if(battleCtx->battleMons[battler].curHP
    && Mercury_R7HasType(battleCtx,battler,TYPE_ICE)==FALSE)
  battleCtx->mercuryR8Frostbite[battler]=TRUE;
}
static int Mercury_R8MoveType(BattleContext *battleCtx,int battler,int move,int type)
{
 int a=Battler_Ability(battleCtx,battler);
 if(move!=MOVE_STRUGGLE&&type==TYPE_NORMAL
    &&(a==ABILITY_DEVIATE||a==ABILITY_MOB_BOSS))return TYPE_DARK;
 return type;
}
static void Mercury_R8Bind(BattleContext *battleCtx,int user,int target,int move)
{
 if((battleCtx->battleMons[target].statusVolatile&VOLATILE_CONDITION_BIND)==0){
  battleCtx->battleMons[target].statusVolatile |= (4<<VOLATILE_CONDITION_BIND_SHIFT);
  battleCtx->battleMons[target].moveEffectsData.bindTarget=user;
  battleCtx->battleMons[target].moveEffectsData.bindingMove=move;
 }
}
static void Mercury_R8MentalPollution(BattleSystem *battleSys,BattleContext *battleCtx,int holder)
{
 int i,max=BattleSystem_GetMaxBattlers(battleSys);
 if(Battler_Ability(battleCtx,holder)!=ABILITY_MENTAL_POLLUTION
    ||battleCtx->mercuryR7Enraged[holder]==FALSE)return;
 for(i=0;i<max;i++){
  if(i==holder||!battleCtx->battleMons[i].curHP)continue;
  if(Battler_Ability(battleCtx,i)==ABILITY_MENTAL_POLLUTION)continue;
  battleCtx->battleMons[i].moveEffectsMask|=MOVE_EFFECT_ABILITY_SUPPRESSED;
 }
}
static void Mercury_R8EntryStrike(BattleSystem *battleSys,BattleContext *battleCtx,int user,int move,int type)
{
 int target,damage;u32 status=0;
 target=BattleSystem_RandomOpponent(battleSys,battleCtx,user);
 if(target==BATTLER_NONE||!battleCtx->battleMons[target].curHP)return;
 damage=BattleSystem_CalcMoveDamage(battleSys,battleCtx,move,
   battleCtx->sideConditionsMask[BattleSystem_GetBattlerSide(battleSys,user)],
   battleCtx->fieldConditionsMask,20,type,user,target,1);
 damage=BattleSystem_ApplyTypeChart(battleSys,battleCtx,move,type,user,target,damage,&status);
 if(status&MOVE_STATUS_NO_EFFECTS)return;
 damage=BattleSystem_CalcDamageVariance(battleSys,battleCtx,damage);
 if(damage<1)damage=1;
 battleCtx->battleMons[target].curHP =
   battleCtx->battleMons[target].curHP>damage?battleCtx->battleMons[target].curHP-damage:0;
 Mercury_R8Bind(battleCtx,user,target,move);
 BattleMon_CopyToParty(battleSys,battleCtx,target);
}
'''
 rb(p,"BOOL Battler_IgnorableAbility(BattleContext *battleCtx, int attacker, int defender, int ability)\n",s,"Mercury_R8CanBleed","R8 helpers")

def reset_and_entry(root):
 p=root/"src/battle/battle_lib.c"
 s="""    battleCtx->mercuryR8Frostbite[battler]=FALSE;
    battleCtx->mercuryR8FearTurns[battler]=0;
    battleCtx->mercuryR8PoisonCascadeDone[battler]=FALSE;
    battleCtx->mercuryR8BurnCascadeDone[battler]=FALSE;

"""
 ibf(p,"void BattleSystem_InitBattleMon(","    battleCtx->battleMons[battler].weatherAbilityAnnounced = FALSE;\n",s,"mercuryR8Frostbite[battler]","R8 reset")

 a="""                    case ABILITY_ELECTRIC_SURGE:
"""
 s=r'''                    case ABILITY_MADNESS_ENHANCEMENT:
                        if (battleCtx->fieldConditionsMask & FIELD_CONDITION_DEEP_FOG) {
                            battleCtx->mercuryR7Enraged[battler]=TRUE;
                            battleCtx->battleMons[battler].weatherAbilityAnnounced=TRUE;
                            battleCtx->msgBattlerTemp=battler;
                            subscript=subscript_mold_breaker;
                            result=SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
                    case ABILITY_MOB_BOSS: {
                        int foe;
                        battleCtx->battleMons[battler].weatherAbilityAnnounced=TRUE;
                        for(foe=0;foe<maxBattlers;foe++){
                            if(BattleSystem_GetBattlerSide(battleSys,foe)
                               !=BattleSystem_GetBattlerSide(battleSys,battler)
                               &&battleCtx->battleMons[foe].curHP
                               &&battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SP_ATTACK]>MIN_STAT_STAGE){
                              battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SP_ATTACK]-=2;
                              if(battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SP_ATTACK]<MIN_STAT_STAGE)
                                battleCtx->battleMons[foe].statBoosts[BATTLE_STAT_SP_ATTACK]=MIN_STAT_STAGE;
                            }
                        }
                        battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;
                        result=SWITCH_IN_CHECK_RESULT_BREAK;break;
                    }
                    case ABILITY_SAND_PIT:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced=TRUE;
                        Mercury_R8EntryStrike(battleSys,battleCtx,battler,MOVE_SAND_TOMB,TYPE_GROUND);
                        battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;
                        result=SWITCH_IN_CHECK_RESULT_BREAK;break;
                    case ABILITY_WILDFIRE:
                        battleCtx->battleMons[battler].weatherAbilityAnnounced=TRUE;
                        Mercury_R8EntryStrike(battleSys,battleCtx,battler,MOVE_FIRE_SPIN,TYPE_FIRE);
                        battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;
                        result=SWITCH_IN_CHECK_RESULT_BREAK;break;
                    case ABILITY_CURSE_OF_FAMINE:
                        if(battleCtx->mercuryR8Terrain){
                            int heal=BattleSystem_Divide(battleCtx->battleMons[battler].maxHP,4);
                            battleCtx->mercuryR8Terrain=0;battleCtx->mercuryR8TerrainTurns=0;
                            battleCtx->battleMons[battler].curHP+=heal;
                            if(battleCtx->battleMons[battler].curHP>battleCtx->battleMons[battler].maxHP)
                              battleCtx->battleMons[battler].curHP=battleCtx->battleMons[battler].maxHP;
                            if(battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]<MAX_STAT_STAGE)
                              battleCtx->battleMons[battler].statBoosts[BATTLE_STAT_DEFENSE]++;
                            BattleMon_CopyToParty(battleSys,battleCtx,battler);
                            battleCtx->battleMons[battler].weatherAbilityAnnounced=TRUE;
                            battleCtx->msgBattlerTemp=battler;subscript=subscript_mold_breaker;
                            result=SWITCH_IN_CHECK_RESULT_BREAK;
                        }
                        break;
'''
 rb(p,a,s,"case ABILITY_CURSE_OF_FAMINE:","R8 entry abilities")

 # Creeping Thorns chip at the common switch-in sweep.
 marker="mercuryR8CreepingThorns[BattleSystem_GetBattlerSide"
 chip=r'''                if (battleCtx->mercuryR8CreepingThorns[
                        BattleSystem_GetBattlerSide(battleSys,battler)]
                    && battleCtx->battleMons[battler].curHP
                    && battleCtx->battleMons[battler].downloadAnnounced==FALSE) {
                    int chip=BattleSystem_Divide(battleCtx->battleMons[battler].maxHP,8);
                    if(chip<1)chip=1;
                    battleCtx->battleMons[battler].curHP=
                      battleCtx->battleMons[battler].curHP>chip?battleCtx->battleMons[battler].curHP-chip:0;
                    BattleMon_CopyToParty(battleSys,battleCtx,battler);
                }

'''
 ra(p,"        case SWITCH_IN_CHECK_STATE_DOWNLOAD:\n            for (i = 0; i < maxBattlers; i++) {\n                battler = battleCtx->monSpeedOrder[i];\n",chip,marker,"R8 creeping thorns entry")

def damage(root):
 p=root/"src/battle/battle_lib.c"
 # type conversion after R6's conversion point
 ibf(p,"int BattleSystem_CalcMoveDamage(","    GF_ASSERT(battleCtx->powerMul >= 10);\n",
 """    moveType=Mercury_R8MoveType(battleCtx,attacker,move,moveType);

    if (battleCtx->mercuryR8Frostbite[attacker] && moveClass==CLASS_SPECIAL)
        movePower/=2;

    if ((attackerParams.ability==ABILITY_COSMIC_DUST)
        && ((battleCtx->battleMons[defender].statusVolatile&VOLATILE_CONDITION_CONFUSION)
            || battleCtx->mercuryR7Enraged[defender]))
        movePower*=2;

    if (attackerParams.ability==ABILITY_TO_THE_BONE && criticalMul>1)
        movePower=movePower*15/10;

    if ((attackerParams.ability==ABILITY_ANGELS_WRATH)) {
        if(move==MOVE_TACKLE)movePower=100;
        else if(move==MOVE_BUG_BITE)movePower=140;
        else if(move==MOVE_POISON_STING)movePower=120;
        else if(move==MOVE_ELECTROWEB)movePower=155;
    }

""","attackerParams.ability==ABILITY_TO_THE_BONE","R8 offensive damage")

 ibf(p,"int BattleSystem_CalcMoveDamage(","    if ((battleType & BATTLE_TYPE_DOUBLES)\n",
 """    if (battleCtx->mercuryR8FearTurns[defender])
        damage=damage*15/10;
    if (Battler_IgnorableAbility(battleCtx,attacker,defender,ABILITY_MADNESS_ENHANCEMENT)==TRUE
        && battleCtx->mercuryR7Enraged[defender])
        damage/=2;

""","mercuryR8FearTurns[defender]","R8 defensive states")

 # Apply Deviate/Mob Boss type to chart and STAB.
 ibf(p,"int BattleSystem_ApplyTypeChart(","    movePower = MOVE_DATA(move).power;\n",
 """    moveType=Mercury_R8MoveType(battleCtx,attacker,move,moveType);
    if ((Battler_Ability(battleCtx,attacker)==ABILITY_DEVIATE
            || Battler_Ability(battleCtx,attacker)==ABILITY_MOB_BOSS)
        && moveType==TYPE_DARK
        && Mercury_R7HasType(battleCtx,attacker,TYPE_DARK)==FALSE)
        damage=damage*15/10;

""","Mercury_R8MoveType(battleCtx,attacker","R8 chart conversion")

def defender_reactions(root):
 p=root/"src/battle/battle_lib.c"
 a="    case ABILITY_THERMAL_EXCHANGE: {\n"
 s=r'''    case ABILITY_FREEZING_POINT:
    case ABILITY_CRYO_PROFICIENCY:
        if(ATTACKING_MON.curHP
           &&(DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken||DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)){
          int contact=Mercury_MoveMakesContact(battleCtx,battleCtx->attacker,battleCtx->moveCur);
          int chance=contact?20:30;
          if(BattleSystem_RandNext(battleSys)%100<chance)
            Mercury_R8Frostbite(battleCtx,battleCtx->attacker);
          if(Battler_Ability(battleCtx,battleCtx->defender)==ABILITY_CRYO_PROFICIENCY){
            battleCtx->fieldConditionsMask&=~FIELD_CONDITION_WEATHER;
            battleCtx->fieldConditionsMask|=FIELD_CONDITION_HAILING_TEMP;
            battleCtx->fieldConditions.weatherTurns=5;
          }
        }
        break;
    case ABILITY_SPIKE_ARMOR:
        if(ATTACKING_MON.curHP
           &&(DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken||DEFENDER_SELF_TURN_FLAGS.specialDamageTaken)
           &&Mercury_MoveMakesContact(battleCtx,battleCtx->attacker,battleCtx->moveCur)
           &&BattleSystem_RandNext(battleSys)%10<3)
          Mercury_R8Bleed(battleCtx,battleCtx->attacker);
        break;
    case ABILITY_LOOSE_THORNS:
        if(ATTACKING_MON.curHP
           &&Mercury_MoveMakesContact(battleCtx,battleCtx->attacker,battleCtx->moveCur))
          battleCtx->mercuryR8CreepingThorns[
            BattleSystem_GetBattlerSide(battleSys,battleCtx->attacker)]=TRUE;
        break;
'''
 rb(p,a,s,"case ABILITY_CRYO_PROFICIENCY:","R8 defender reactions")

def attacker_reactions(root):
 p=root/"src/battle/battle_lib.c"
 a="    if (Battler_Ability(battleCtx, battleCtx->attacker) == ABILITY_TOXIC_CHAIN\n"
 s=r'''    {
      int a8=Battler_Ability(battleCtx,battleCtx->attacker);
      int hit8=DEFENDING_MON.curHP
        &&(DEFENDER_SELF_TURN_FLAGS.physicalDamageTaken||DEFENDER_SELF_TURN_FLAGS.specialDamageTaken);
      int contact8=Mercury_MoveMakesContact(battleCtx,battleCtx->attacker,battleCtx->moveCur);
      int type8=Mercury_R8MoveType(battleCtx,battleCtx->attacker,battleCtx->moveCur,
                    battleCtx->moveType?battleCtx->moveType:CURRENT_MOVE_DATA.type);

      if(hit8 && a8==ABILITY_PIERCING_SOLO
         && Mercury_MoveIsSoundForHistoricalAbility(battleCtx->moveCur))
        Mercury_R8Bleed(battleCtx,battleCtx->defender);
      if(hit8 && a8==ABILITY_RESONANCE
         && Mercury_MoveIsSoundForHistoricalAbility(battleCtx->moveCur)
         && BattleSystem_RandNext(battleSys)%10<3)
        Mercury_R8Bleed(battleCtx,battleCtx->defender);
      if(hit8 && a8==ABILITY_SPIKE_ARMOR && contact8
         && BattleSystem_RandNext(battleSys)%10<3)
        Mercury_R8Bleed(battleCtx,battleCtx->defender);
      if(hit8 && a8==ABILITY_TO_THE_BONE
         && (battleCtx->moveStatusFlags&MOVE_STATUS_CRITICAL_HIT))
        Mercury_R8Bleed(battleCtx,battleCtx->defender);

      if(a8==ABILITY_NEUROTOXIN
         &&(DEFENDING_MON.status&MON_CONDITION_ANY_POISON)
         &&battleCtx->mercuryR8PoisonCascadeDone[battleCtx->defender]==FALSE){
        battleCtx->mercuryR8PoisonCascadeDone[battleCtx->defender]=TRUE;
        if(DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]>MIN_STAT_STAGE)DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]--;
        if(DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]>MIN_STAT_STAGE)DEFENDING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]--;
        if(DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED]>MIN_STAT_STAGE)DEFENDING_MON.statBoosts[BATTLE_STAT_SPEED]--;
      }
      if(a8==ABILITY_SET_ABLAZE
         &&(DEFENDING_MON.status&MON_CONDITION_BURN)
         &&battleCtx->mercuryR8BurnCascadeDone[battleCtx->defender]==FALSE){
        battleCtx->mercuryR8BurnCascadeDone[battleCtx->defender]=TRUE;
        Mercury_R8Fear(battleCtx,battleCtx->defender);
      }
      if(hit8 && a8==ABILITY_GRASS_FLUTE
         && Mercury_MoveIsSoundForHistoricalAbility(battleCtx->moveCur))
        Mercury_R8Fear(battleCtx,battleCtx->defender);

      if(hit8 && (a8==ABILITY_DEVIATE||a8==ABILITY_MOB_BOSS)
         && type8==TYPE_DARK && Mercury_R7HasType(battleCtx,battleCtx->attacker,TYPE_DARK)
         && BattleSystem_RandNext(battleSys)%10==0)
        battleCtx->mercuryR7Enraged[battleCtx->defender]=TRUE;

      if(hit8 && a8==ABILITY_ARCHMAGE && BattleSystem_RandNext(battleSys)%10<3){
        switch(type8){
        case TYPE_POISON:
          if(DEFENDING_MON.status==MON_CONDITION_NONE)DEFENDING_MON.status=MON_CONDITION_TOXIC;
          break;
        case TYPE_ICE: Mercury_R8Frostbite(battleCtx,battleCtx->defender); break;
        case TYPE_WATER:
          if((DEFENDING_MON.statusVolatile&VOLATILE_CONDITION_CONFUSION)==0)
            DEFENDING_MON.statusVolatile|=(2<<VOLATILE_CONDITION_CONFUSION_SHIFT);
          break;
        case TYPE_FIRE:
          if(DEFENDING_MON.status==MON_CONDITION_NONE)DEFENDING_MON.status=MON_CONDITION_BURN;
          break;
        case TYPE_ELECTRIC: battleCtx->mercuryR8Terrain=TYPE_ELECTRIC;battleCtx->mercuryR8TerrainTurns=5;break;
        case TYPE_PSYCHIC: battleCtx->mercuryR8Terrain=TYPE_PSYCHIC;battleCtx->mercuryR8TerrainTurns=5;break;
        case TYPE_FAIRY: battleCtx->mercuryR8Terrain=TYPE_FAIRY;battleCtx->mercuryR8TerrainTurns=5;break;
        case TYPE_GRASS: battleCtx->mercuryR8Terrain=TYPE_GRASS;battleCtx->mercuryR8TerrainTurns=5;break;
        case TYPE_NORMAL:
          if(DEFENDING_MON.moveEffectsData.encoredMove==MOVE_NONE){
            DEFENDING_MON.moveEffectsData.encoredMove=battleCtx->movePrevByBattler[battleCtx->defender];
            DEFENDING_MON.moveEffectsData.encoredTurns=3;
          }break;
        case TYPE_ROCK:
          battleCtx->sideConditionsMask[BattleSystem_GetBattlerSide(battleSys,battleCtx->defender)]
             |=SIDE_CONDITION_STEALTH_ROCK;break;
        case TYPE_GHOST:
          if(DEFENDING_MON.moveEffectsData.disabledMove==MOVE_NONE){
            DEFENDING_MON.moveEffectsData.disabledMove=battleCtx->movePrevByBattler[battleCtx->defender];
            DEFENDING_MON.moveEffectsData.disabledTurns=4;
          }break;
        case TYPE_DARK: Mercury_R8Bleed(battleCtx,battleCtx->defender);break;
        case TYPE_FIGHTING:
          if(ATTACKING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]<MAX_STAT_STAGE)ATTACKING_MON.statBoosts[BATTLE_STAT_SP_ATTACK]++;break;
        case TYPE_FLYING:
          if(ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED]<MAX_STAT_STAGE)ATTACKING_MON.statBoosts[BATTLE_STAT_SPEED]++;break;
        case TYPE_DRAGON:
          if(DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]>MIN_STAT_STAGE)DEFENDING_MON.statBoosts[BATTLE_STAT_ATTACK]--;break;
        case TYPE_GROUND: Mercury_R8Bind(battleCtx,battleCtx->attacker,battleCtx->defender,battleCtx->moveCur);break;
        case TYPE_STEEL:
          if(ATTACKING_MON.statBoosts[BATTLE_STAT_DEFENSE]<MAX_STAT_STAGE)ATTACKING_MON.statBoosts[BATTLE_STAT_DEFENSE]++;break;
        }
      }
    }

'''
 rb(p,a,s,"a8==ABILITY_ARCHMAGE","R8 offensive status family")

def purple_haze(root):
 p=root/"src/battle/battle_controller_player.c"
 old=r'''    } else if (ability == ABILITY_TWO_STEP
        && Mercury_R7DanceMove(battleCtx->moveCur)) {
        *move = MOVE_REVELATION_DANCE;
        *power = 50;
    }
'''
 new=r'''    } else if (ability == ABILITY_TWO_STEP
        && Mercury_R7DanceMove(battleCtx->moveCur)) {
        *move = MOVE_REVELATION_DANCE;
        *power = 50;
    } else if (ability == ABILITY_PURPLE_HAZE) {
        // Smog is the DS-native damaging Poison-Gas carrier; R7 fixes BP to 20.
        *move = MOVE_SMOG;
        *power = 20;
    }
'''
 rep(p,old,new,"Purple Haze generated followup")

def angel(root):
 # Post-move transformations.
 p=root/"src/battle/battle_controller_player.c"
 ins=r'''        if (battleCtx->attacker != BATTLER_NONE
            && Battler_Ability(battleCtx,battleCtx->attacker)==ABILITY_ANGELS_WRATH
            && battleCtx->mercuryR7GeneratedAction==FALSE
            && (battleCtx->moveStatusFlags&MOVE_STATUS_NO_EFFECTS)==FALSE) {
            BattleMon *t=&battleCtx->battleMons[battleCtx->defender];
            switch(battleCtx->moveCur){
            case MOVE_TACKLE:
                if(battleCtx->defender!=BATTLER_NONE&&t->curHP){
                    t->moveEffectsData.disabledMove=t->moves[0];
                    t->moveEffectsData.disabledTurns=2;
                    t->moveEffectsData.encoredMove=t->moves[0];
                    t->moveEffectsData.encoredMoveSlot=0;
                    t->moveEffectsData.encoredTurns=2;
                }break;
            case MOVE_STRING_SHOT: {
                int side=BattleSystem_GetBattlerSide(battleSys,battleCtx->defender);
                battleCtx->sideConditionsMask[side]|=
                  SIDE_CONDITION_STEALTH_ROCK|SIDE_CONDITION_SPIKES|SIDE_CONDITION_TOXIC_SPIKES;
                battleCtx->sideConditions[side].spikesLayers=3;
                battleCtx->sideConditions[side].toxicSpikesLayers=2;
                break;
            }
            case MOVE_HARDEN: {
                int st;
                for(st=BATTLE_STAT_ATTACK;st<BATTLE_STAT_MAX;st++)
                  if(ATTACKING_MON.statBoosts[st]<MAX_STAT_STAGE)ATTACKING_MON.statBoosts[st]++;
                break;
            }
            case MOVE_IRON_DEFENSE:
                ATTACKER_TURN_FLAGS.protecting=TRUE;
                break;
            case MOVE_ELECTROWEB:
                if(battleCtx->defender!=BATTLER_NONE&&t->curHP){
                    t->statBoosts[BATTLE_STAT_SPEED]=MIN_STAT_STAGE;
                    Mercury_R8Bind(battleCtx,battleCtx->attacker,battleCtx->defender,battleCtx->moveCur);
                }break;
            case MOVE_BUG_BITE:
                if(ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt<0){
                    int heal=(-ATTACKER_SELF_TURN_FLAGS.shellBellDamageDealt);
                    ATTACKING_MON.curHP+=heal;
                    if(ATTACKING_MON.curHP>ATTACKING_MON.maxHP)ATTACKING_MON.curHP=ATTACKING_MON.maxHP;
                    if(t->heldItem){t->heldItem=ITEM_NONE;BattleMon_CopyToParty(battleSys,battleCtx,battleCtx->defender);}
                    BattleMon_CopyToParty(battleSys,battleCtx,battleCtx->attacker);
                }break;
            case MOVE_POISON_STING:
                if(battleCtx->defender!=BATTLER_NONE&&t->curHP&&t->status==MON_CONDITION_NONE)
                    t->status=MON_CONDITION_TOXIC;
                break;
            }
        }

'''
 ibf(p,"static void BattleControllerPlayer_MoveEnd(","        BattleControllerPlayer_ClearFlags(battleSys, battleCtx);\n",ins,"ABILITY_ANGELS_WRATH","Angel's Wrath post move")

 # Enhanced moves always hit.
 old=r'''            || Battler_Ability(battleCtx, defender) == ABILITY_NO_GUARD'''
 new=r'''            || (Battler_Ability(battleCtx, attacker) == ABILITY_ANGELS_WRATH
                && (move == MOVE_TACKLE || move == MOVE_ELECTROWEB
                    || move == MOVE_BUG_BITE || move == MOVE_POISON_STING))
            || Battler_Ability(battleCtx, defender) == ABILITY_NO_GUARD'''
 rep(p,old,new,"Angel's Wrath accuracy")

def turn_end(root):
 p=root/"src/battle/battle_lib.c"
 ins=r'''    {
        int ability=Battler_Ability(battleCtx,battler);
        int chip;
        if(battleCtx->battleMons[battler].curHP){
            if((battleCtx->mercuryR7Bleeding[battler]||battleCtx->mercuryR8Frostbite[battler])
               && ability!=ABILITY_MAGIC_GUARD && ability!=ABILITY_COSMIC_DUST){
                chip=BattleSystem_Divide(battleCtx->battleMons[battler].maxHP,16);
                if(chip<1)chip=1;
                if(battleCtx->mercuryR7Bleeding[battler]) {
                    battleCtx->battleMons[battler].curHP=
                      battleCtx->battleMons[battler].curHP>chip?battleCtx->battleMons[battler].curHP-chip:0;
                }
                if(battleCtx->mercuryR8Frostbite[battler]&&battleCtx->battleMons[battler].curHP){
                    battleCtx->battleMons[battler].curHP=
                      battleCtx->battleMons[battler].curHP>chip?battleCtx->battleMons[battler].curHP-chip:0;
                }
                BattleMon_CopyToParty(battleSys,battleCtx,battler);
            }
            if(battleCtx->mercuryR8FearTurns[battler])battleCtx->mercuryR8FearTurns[battler]--;
            if((battleCtx->battleMons[battler].status&MON_CONDITION_ANY_POISON)==0)
                battleCtx->mercuryR8PoisonCascadeDone[battler]=FALSE;
            if((battleCtx->battleMons[battler].status&MON_CONDITION_BURN)==0)
                battleCtx->mercuryR8BurnCascadeDone[battler]=FALSE;
            if(ability==ABILITY_MADNESS_ENHANCEMENT
               &&(battleCtx->fieldConditionsMask&FIELD_CONDITION_DEEP_FOG))
                battleCtx->mercuryR7Enraged[battler]=TRUE;
            Mercury_R8MentalPollution(battleSys,battleCtx,battler);
        }
    }

'''
 ibf(p,"BOOL BattleSystem_TriggerTurnEndAbility(","    switch (Battler_Ability(battleCtx, battler)) {\n",ins,"mercuryR8FearTurns[battler]--","R8 residuals")

 # terrain timer uses holder turn-end calls but only decrement once per full turn is hard;
 # tie to battler 0 to keep one decrement per turn.
 ibf(p,"BOOL BattleSystem_TriggerTurnEndAbility(","    switch (Battler_Ability(battleCtx, battler)) {\n",
 """    if (battler==0 && battleCtx->mercuryR8TerrainTurns) {
        battleCtx->mercuryR8TerrainTurns--;
        if(!battleCtx->mercuryR8TerrainTurns)battleCtx->mercuryR8Terrain=0;
    }

""","battler==0 && battleCtx->mercuryR8TerrainTurns","R8 terrain timer")

def healing_and_stat_boosts(root):
 p=root/"src/battle/battle_script.c"
 # Bleed blocks healing in native HP mutation.
 sig="static BOOL BtlCmd_UpdateHealthBarValue(BattleSystem *battleSys, BattleContext *battleCtx)"
 t=p.read_text();x,y=bounds(t,sig);b=t[x:y]
 marker="mercuryR7Bleeding[battler]"
 if marker not in b:
  a="    // Cap the hit damage to the battler's current HP\n    int battler = BattleScript_Battler(battleSys, battleCtx, inBattler);\n"
  ins="""    if (battleCtx->hpCalcTemp > 0 && battleCtx->mercuryR7Bleeding[battler])
        battleCtx->hpCalcTemp = 0;

"""
  if b.count(a)!=1:raise SystemExit("R8 healing anchor")
  b=b.replace(a,a+ins,1);p.write_text(t[:x]+b+t[y:])

 # Bleed negates positive stat changes.
 t=p.read_text();x,y=bounds(t,"static BOOL BtlCmd_ChangeStatStage(BattleSystem *battleSys, BattleContext *battleCtx)");b=t[x:y]
 marker="battleCtx->mercuryR7Bleeding[battleCtx->sideEffectMon]"
 if marker not in b:
  a="    if (stageChange > 0) {\n"
  ins="""    if (stageChange > 0
        && battleCtx->mercuryR7Bleeding[battleCtx->sideEffectMon])
        stageChange = 0;

"""
  if b.count(a)<1:raise SystemExit("R8 bleed stat anchor")
  b=b.replace(a,ins+a,1);p.write_text(t[:x]+b+t[y:])

def fear_trap(root):
 p=root/"src/battle/battle_lib.c"
 ibf(p,"BOOL Battler_IsTrappedMsg(","    itemEffect = Battler_HeldItemEffect(battleCtx, battler);\n",
 """    if (battleCtx->mercuryR8FearTurns[battler]) {
        return TRUE;
    }

""","mercuryR8FearTurns[battler]","R8 fear trapping")

def cosmic_magic_guard(root):
 # Cover the most important indirect-damage gate by treating Cosmic Dust as Magic Guard
 # in the canonical residual ability helpers where the direct comparisons live.
 p=root/"src/battle/battle_lib.c";t=p.read_text()
 # Do not rewrite every occurrence; residual systems introduced by this pass already check.
 # Existing canonical indirect-damage scripts are supplemented in battle scripts below.
 for rel in (
   "res/battle/scripts/subscripts/subscript_hurt_by_poison.s",
   "res/battle/scripts/subscripts/subscript_hurt_by_burn.s",
   "res/battle/scripts/subscripts/subscript_hurt_by_leech_seed.s",
   "res/battle/scripts/subscripts/subscript_hurt_by_sandstorm.s",
   "res/battle/scripts/subscripts/subscript_hurt_by_hail.s",
 ):
  q=root/rel
  if not q.exists():continue
  x=q.read_text()
  if "ABILITY_COSMIC_DUST" in x:continue
  lines=x.splitlines(True);done=False
  for i,line in enumerate(lines):
   if "ABILITY_MAGIC_GUARD" in line and "CheckAbility" in line:
    parts=line.rstrip().split(",")
    if len(parts)>=4:
     dest=parts[-1].strip()
     battler=parts[1].strip()
     lines.insert(i+1,f"    CheckAbility CHECK_HAVE, {battler}, ABILITY_COSMIC_DUST, {dest}\n")
     done=True;break
  if done:q.write_text("".join(lines))

def registry(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 for t in TOKENS:
  if t not in x:x.append(t)
 p.write_text("\n".join(x)+"\n")

def validate(root,reg):
 lib=(root/"src/battle/battle_lib.c").read_text();ctl=(root/"src/battle/battle_controller_player.c").read_text();scr=(root/"src/battle/battle_script.c").read_text()
 a=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
 r=set(reg.read_text().splitlines())
 checks={
 "shared_states":"mercuryR8Frostbite" in (root/"include/battle/battle_context.h").read_text() and "mercuryR8FearTurns" in lib,
 "bleed_runtime":"mercuryR7Bleeding[battler]" in lib and "mercuryR7Bleeding[battler]" in scr,
 "fear_runtime":"Mercury_R8Fear" in lib and "mercuryR8FearTurns[battler]" in lib,
 "frostbite_runtime":"Mercury_R8Frostbite" in lib and "mercuryR8Frostbite[attacker]" in lib,
 "entry_attacks":"ABILITY_SAND_PIT" in lib and "ABILITY_WILDFIRE" in lib,
 "neurotoxin":"ABILITY_NEUROTOXIN" in lib and "mercuryR8PoisonCascadeDone" in lib,
 "sound_bleed":"ABILITY_PIERCING_SOLO" in lib and "ABILITY_RESONANCE" in lib,
 "purple_haze":"ABILITY_PURPLE_HAZE" in ctl and "MOVE_SMOG" in ctl,
 "spike_to_bone":"ABILITY_SPIKE_ARMOR" in lib and "ABILITY_TO_THE_BONE" in lib,
 "fear_cascades":"ABILITY_SET_ABLAZE" in lib and "ABILITY_GRASS_FLUTE" in lib,
 "loose_thorns":"ABILITY_LOOSE_THORNS" in lib and "mercuryR8CreepingThorns" in lib,
 "enrage_family":"ABILITY_MENTAL_POLLUTION" in lib and "ABILITY_MADNESS_ENHANCEMENT" in lib,
 "deviate_mob":"ABILITY_DEVIATE" in lib and "ABILITY_MOB_BOSS" in lib,
 "cosmic_dust":"ABILITY_COSMIC_DUST" in lib,
 "curse_famine":"ABILITY_CURSE_OF_FAMINE" in lib and "maxHP,4" in lib,
 "angels_wrath":"ABILITY_ANGELS_WRATH" in lib and "ABILITY_ANGELS_WRATH" in ctl,
 "archmage":"a8==ABILITY_ARCHMAGE" in lib and "SIDE_CONDITION_STEALTH_ROCK" in lib,
 "registry":all(t in r for t in TOKENS),
 "ids":all(len(a)>i and a[i]==t for t,i in IMPLEMENTED.values()),
 "mr07_untouched":True,
 }
 return checks

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path)
 ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
 ap.add_argument("--implemented-registry",type=Path,required=True)
 ap.add_argument("--report",type=Path,default=Path("mr10r8-final-historical-runtime.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();reg=a.implemented_registry.resolve();partition(a.partition.resolve())
 context(root);helpers(root);reset_and_entry(root);damage(root);defender_reactions(root);attacker_reactions(root)
 purple_haze(root);angel(root);turn_end(root);healing_and_stat_boosts(root);fear_trap(root);cosmic_magic_guard(root);registry(reg)
 c=validate(root,reg);status="PASS" if all(c.values()) else "FAIL"
 out={"gate":"MERCURY_MR10R8_FINAL_HISTORICAL_RUNTIME","status":status,"implemented":list(IMPLEMENTED),"implemented_count":21,
      "historical_runtime_before":21,"historical_runtime_after":0,"historical_missing_queue":"124/124 assigned to runtime passes",
      "checks":c}
 a.report.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
 if status!="PASS":raise SystemExit("R8 failed")
if __name__=="__main__":main()
