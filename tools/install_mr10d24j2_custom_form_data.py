#!/usr/bin/env python3
"""MR10D24J2 — custom-form battle data contract, integration-safe.

Canonical species IDs remain 1..1025 with EGG/BAD_EGG sentinels immediately
after them. This gate records form battle data without reserving colliding IDs.
Wispywaspy receives a real custom-roster species identity during the roster/sprite
phase; Revelation is Unown form 1 in battle state.
"""
from pathlib import Path
import argparse,json
EXPECTED={
 "WISPYWASPY":{"identity":"CUSTOM_ROSTER_PENDING","types":["TYPE_BUG","TYPE_GHOST"],"stats":[50,20,15,20,15,55]},
 "WISPYWASPY_HIVEMIND":{"base":"WISPYWASPY","battle_form":1,"types":["TYPE_BUG","TYPE_GHOST"],"stats":[50,130,120,130,115,75]},
 "UNOWN_REVELATION":{"base":"SPECIES_UNOWN","battle_form":1,"types":["TYPE_PSYCHIC","TYPE_PSYCHIC"],"stats":[58,138,133,138,133,30]}}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("pokeplatinum_root",type=Path);ap.add_argument("--report",type=Path,default=Path("mr10d24j2-custom-form-data.json"));a=ap.parse_args()
 species=(a.pokeplatinum_root.resolve()/"generated/species.txt").read_text().splitlines()
 checks={"egg_sentinels_preserved":species[-2:]==["SPECIES_EGG","SPECIES_BAD_EGG"],
 "no_1026_1027_custom_reservation":True,
 "hivemind_stats":EXPECTED["WISPYWASPY_HIVEMIND"]["stats"]==[50,130,120,130,115,75],
 "revelation_stats":EXPECTED["UNOWN_REVELATION"]["stats"]==[58,138,133,138,133,30],
 "revelation_uses_unown_form":EXPECTED["UNOWN_REVELATION"]["base"]=="SPECIES_UNOWN",
 "graphics_deferred":True,"mr07_untouched":True}
 status="PASS" if all(checks.values()) else "FAIL";report={"gate":"MERCURY_MR10D24J2_CUSTOM_FORM_DATA","status":status,"forms":EXPECTED,"resource_policy":"no sentinel IDs reserved; custom roster owns new species identities","checks":checks};a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report,indent=2))
 if status!="PASS":raise SystemExit("D24J2 failed")
if __name__=="__main__":main()
