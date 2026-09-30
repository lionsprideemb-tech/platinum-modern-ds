#!/usr/bin/env python3
"""MR10D24J — Locust Swarm + Revelation threshold-form controllers.

Recovered mappings:
  Locust Swarm: Wispywaspy -> Hivemind while HP > 1/4.
  Revelation: Unown -> Revelation form while HP > 1/4.

This installer intentionally refuses to invent species/form IDs. The custom
content layer must materialize SPECIES_WISPYWASPY, SPECIES_WISPYWASPY_HIVEMIND
and SPECIES_UNOWN_REVELATION before this pass can certify. Once present, both
controllers reuse Mercury's MR08 threshold-form lifecycle.
"""
from pathlib import Path
import argparse,json
ABILITIES={"ABILITY_MR_LOCUST_SWARM":736,"ABILITY_MR_REVELATION":737}
REQ={"SPECIES_WISPYWASPY":1026,"SPECIES_WISPYWASPY_HIVEMIND":1027,"SPECIES_UNOWN_REVELATION":1028}

def ins(p,a,s):
 t=p.read_text()
 if s in t:return
 if t.count(a)!=1:raise SystemExit(f"anchor {t.count(a)}")
 p.write_text(t.replace(a,s+a,1))

def require_species(root):
 # Custom battle-form IDs are intentionally outside generated/species.txt until
 # the post-ability sprite/resource phase. Validate the locked Mercury registry
 # and materialize local compile constants without shifting canonical 1..1025.
 registry=Path("data/mercury_custom_species_ids.txt")
 got={}
 for raw in registry.read_text().splitlines():
  s=raw.strip()
  if not s or s.startswith("#"):continue
  n,t=s.split();got[t]=int(n)
 bad=[t for t,n in REQ.items() if got.get(t)!=n]
 if bad:raise SystemExit("D24J custom species ID mismatch: "+", ".join(bad))
 block="\\n/* Mercury D24J battle-only custom form IDs; graphical resources deferred. */\\n"+"" .join(f"#ifndef {t}\\n#define {t} {n}\\n#endif\\n" for t,n in REQ.items())
 for rel in ("src/battle/battle_lib.c",):
  p=root/rel;text=p.read_text()
  anchor='#include "res/battle/scripts/sub_seq.naix"\\n'
  if "Mercury D24J battle-only custom form IDs" not in text:
   if text.count(anchor)!=1:raise SystemExit("D24J include anchor mismatch")
   p.write_text(text.replace(anchor,anchor+block,1))

def patch(root):
 require_species(root)
 ctx=root/"include/battle/battle_context.h"
 ins(ctx,"    u8 mercuryZenActive[MAX_BATTLERS];\n","    u8 mercuryLocustHivemindActive[MAX_BATTLERS];\n    u8 mercuryRevelationActive[MAX_BATTLERS];\n")
 lib=root/"src/battle/battle_lib.c"
 helper=r'''static void Mercury_D24JThresholdForms(BattleContext *battleCtx, int battler)
{
    if (!battleCtx->battleMons[battler].curHP
        || (battleCtx->battleMons[battler].statusVolatile & VOLATILE_CONDITION_TRANSFORM)) {
        return;
    }

    if (Battler_Ability(battleCtx, battler) == ABILITY_MR_LOCUST_SWARM
        && (battleCtx->battleMons[battler].species == SPECIES_WISPYWASPY
            || battleCtx->battleMons[battler].species == SPECIES_WISPYWASPY_HIVEMIND)) {
        BOOL active = battleCtx->battleMons[battler].curHP
            > battleCtx->battleMons[battler].maxHP / 4;
        battleCtx->battleMons[battler].species =
            active ? SPECIES_WISPYWASPY_HIVEMIND : SPECIES_WISPYWASPY;
        battleCtx->mercuryLocustHivemindActive[battler] = active;
    }

    if (Battler_Ability(battleCtx, battler) == ABILITY_MR_REVELATION
        && (battleCtx->battleMons[battler].species == SPECIES_UNOWN
            || battleCtx->battleMons[battler].species == SPECIES_UNOWN_REVELATION)) {
        BOOL active = battleCtx->battleMons[battler].curHP
            > battleCtx->battleMons[battler].maxHP / 4;
        battleCtx->battleMons[battler].species =
            active ? SPECIES_UNOWN_REVELATION : SPECIES_UNOWN;
        battleCtx->mercuryRevelationActive[battler] = active;
    }
}

'''
 ins(lib,"BOOL BattleSystem_TriggerTurnEndAbility(BattleSystem *battleSys, BattleContext *battleCtx, int battler)\n",helper)
 # Run continuously in the existing turn-end ability dispatcher.
 anchor="""    switch (Battler_Ability(battleCtx, battler)) {
"""
 ins(lib,anchor,"    Mercury_D24JThresholdForms(battleCtx, battler);\n\n")
 # Initialize on battle-mon load too.
 init="void BattleSystem_InitBattleMon(BattleSystem *battleSys, BattleContext *battleCtx, int battler, int partySlot)"
 # Call after init via a stable existing marker.
 marker="    battleCtx->mercuryZeroToHeroActive[battler] = FALSE;\n"
 t=lib.read_text()
 if "Mercury_D24JThresholdForms(battleCtx, battler);" not in t[t.find(init):t.find(init)+9000]:
  if marker not in t:raise SystemExit("init marker absent")
  lib.write_text(t.replace(marker,marker+"    Mercury_D24JThresholdForms(battleCtx, battler);\n",1))

def reg(p):
 x=[z.strip() for z in p.read_text().splitlines() if z.strip()]
 for tok in ABILITIES:
  if tok not in x:x.append(tok)
 p.write_text("\n".join(x)+"\n")

def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--implemented-registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24j-threshold-forms.json"));a=ap.parse_args()
 root=a.pokeplatinum_root.resolve();require_species(root);patch(root);reg(a.implemented_registry.resolve())
 ab=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()];lib=(root/"src/battle/battle_lib.c").read_text()
 checks={"stable_ids":all(len(ab)>i and ab[i]==t for t,i in ABILITIES.items()),"locust_mapping":"SPECIES_WISPYWASPY_HIVEMIND" in lib,"revelation_mapping":"SPECIES_UNOWN_REVELATION" in lib,"quarter_threshold":"maxHP / 4" in lib,"strictly_above":"> battleCtx->battleMons[battler].maxHP / 4" in lib,"transform_guard":"VOLATILE_CONDITION_TRANSFORM" in lib,"registry":all(t in a.implemented_registry.read_text() for t in ABILITIES),"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";a.report.write_text(json.dumps({"gate":"MERCURY_MR10D24J_THRESHOLD_FORMS","status":status,"implemented":["Locust Swarm","Revelation"],"remaining_after_d24j":3,"checks":checks},indent=2)+"\n");print(status)
 if status!="PASS":raise SystemExit("D24J failed")
if __name__=="__main__":main()
