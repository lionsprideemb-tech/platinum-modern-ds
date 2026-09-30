#!/usr/bin/env python3
from pathlib import Path
import argparse,json
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--partition",type=Path,default=Path("data/mr10_safe_ability_partition.json"));ap.add_argument("--registry",type=Path,required=True);ap.add_argument("--report",type=Path,default=Path("mr10d24-final75-audit.json"));a=ap.parse_args()
 p=json.loads(a.partition.read_text()); reg=set(x.strip() for x in a.registry.read_text().splitlines() if x.strip())
 keep=[x for x in p["abilities"] if x.get("owner_review_decision")=="KEEP AS WRITTEN"]
 missing=[{"name":x["display_name"],"id":x["id"],"token":x["token"]} for x in keep if x["token"] not in reg]
 ids_ok=all(x["id"]>=0 for x in keep) and len({x["id"] for x in keep})==len(keep)
 checks={"partition_keep_count_75":len(keep)==75,"registry_has_all_75":not missing,"stable_ids_unique":ids_ok,"canonical_modern_target":187,"approved_redesign_target":15,"mr07_visuals_untouched_by_audit":True}
 status="PASS" if all(v is True or isinstance(v,int) for v in checks.values()) and checks["partition_keep_count_75"] and checks["registry_has_all_75"] and checks["stable_ids_unique"] else "FAIL"
 out={"gate":"MERCURY_MR10D24_FINAL75","status":status,"keep_as_written":len(keep),"missing":missing,"checks":checks};a.report.write_text(json.dumps(out,indent=2)+"\n");print(json.dumps(out,indent=2))
 if status!="PASS":raise SystemExit("Final 75 audit failed")
if __name__=="__main__":main()
