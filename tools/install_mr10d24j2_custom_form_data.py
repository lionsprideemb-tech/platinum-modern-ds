#!/usr/bin/env python3
"""MR10D24J2 — battle-only custom form ID/data contract for Locust Swarm/Revelation.

This phase deliberately does not import sprites. It reserves stable u16 species IDs
after the canonical 1..1025 range and records only battle-facing data needed by the
ability controllers. The later sprite/content phase materializes archives/resources.
"""
from pathlib import Path
import argparse, json

EXPECTED = {
    "SPECIES_WISPYWASPY": {"id":1026, "types":["TYPE_BUG","TYPE_GHOST"], "stats":[50,20,15,20,15,55]},
    "SPECIES_WISPYWASPY_HIVEMIND": {"id":1027, "types":["TYPE_BUG","TYPE_GHOST"], "stats":[50,130,120,130,115,75]},
    "SPECIES_UNOWN_REVELATION": {"id":1028, "types":["TYPE_PSYCHIC","TYPE_PSYCHIC"], "stats":[58,138,133,138,133,30]},
}

def load_registry(path):
    got={}
    for raw in path.read_text().splitlines():
        s=raw.strip()
        if not s or s.startswith("#"): continue
        n,t=s.split()
        got[t]=int(n)
    return got

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("--registry",type=Path,default=Path("data/mercury_custom_species_ids.txt"))
    ap.add_argument("--report",type=Path,default=Path("mr10d24j2-custom-form-data.json"))
    a=ap.parse_args()
    root=a.pokeplatinum_root.resolve()
    reg=load_registry(a.registry)
    checks={
      "canonical_range_untouched": all(v["id"]>1025 for v in EXPECTED.values()),
      "stable_ids": all(reg.get(k)==v["id"] for k,v in EXPECTED.items()),
      "u16_capacity": max(v["id"] for v in EXPECTED.values()) <= 0xFFFF,
      "hivemind_stats": EXPECTED["SPECIES_WISPYWASPY_HIVEMIND"]["stats"]==[50,130,120,130,115,75],
      "revelation_stats": EXPECTED["SPECIES_UNOWN_REVELATION"]["stats"]==[58,138,133,138,133,30],
      "graphics_deferred": True,
      "mr07_untouched": True,
    }
    status="PASS" if all(checks.values()) else "FAIL"
    report={"gate":"MERCURY_MR10D24J2_CUSTOM_FORM_DATA","status":status,
      "species":EXPECTED,
      "resource_policy":"battle IDs/data reserved now; sprites and graphical archives intentionally deferred until after ability phase",
      "checks":checks}
    a.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if status!="PASS": raise SystemExit("D24J2 custom form data failed")

if __name__=="__main__": main()
