#!/usr/bin/env python3
"""MR10D24 integration runner — deterministic final-75 chain.

Runs every D24 installer in dependency order against one pokeplatinum tree and
one implemented-ability registry. Stops immediately on any failed stage.
This is an integration gate, not native-build certification.
"""
from pathlib import Path
import argparse, json, subprocess, sys

STAGES = [
 ("d24b","install_mr10d24b_sludge_spit.py",True),
 ("d24c","install_mr10d24c_color_change.py",True),
 ("d24d","install_mr10d24d_generated_sprint.py",True),
 ("d24f","install_mr10d24f_generated_final.py",True),
 ("d24g","install_mr10d24g_dna_scramble.py",True),
 ("d24h","install_mr10d24h_toxic_surge.py",True),
 ("d24i","install_mr10d24i_blood_stain.py",True),
 ("d24j2","install_mr10d24j2_custom_form_data.py",False),
 ("d24j","install_mr10d24j_threshold_form_controllers.py",True),
 ("d24k","install_mr10d24k_hydra_3gt1.py",True),
 ("d24l","install_mr10d24l_craving.py",True),
]

def run(cmd):
 print("+"," ".join(map(str,cmd)),flush=True)
 subprocess.run([str(x) for x in cmd],check=True)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("pokeplatinum_root",type=Path)
 ap.add_argument("--implemented-registry",type=Path,required=True)
 ap.add_argument("--partition",type=Path,default=Path("data/mr10_safe_ability_partition.json"))
 ap.add_argument("--report-dir",type=Path,default=Path("build/mr10d24-integration"))
 ap.add_argument("--report",type=Path,default=Path("mr10d24-integration.json"))
 a=ap.parse_args()
 root=a.pokeplatinum_root.resolve(); reg=a.implemented_registry.resolve()
 tools=Path(__file__).resolve().parent; out=a.report_dir.resolve(); out.mkdir(parents=True,exist_ok=True)
 if not root.exists(): raise SystemExit(f"missing pokeplatinum root: {root}")
 if not reg.exists(): raise SystemExit(f"missing implemented registry: {reg}")
 completed=[]
 try:
  for tag,script,uses_reg in STAGES:
   report=out/f"{tag}.json"
   cmd=[sys.executable,tools/script,root,"--report",report]
   if uses_reg: cmd += ["--implemented-registry",reg]
   if tag in {"d24b","d24c","d24d","d24f"}: cmd += ["--partition",a.partition.resolve()]
   run(cmd)
   data=json.loads(report.read_text())
   if data.get("status")!="PASS": raise SystemExit(f"{tag} report did not PASS")
   completed.append(tag)
  final=out/"final75.json"
  run([sys.executable,tools/"audit_mr10d24_final75.py","--partition",a.partition.resolve(),"--registry",reg,"--report",final])
  final_data=json.loads(final.read_text())
  status="PASS" if final_data.get("status")=="PASS" and len(completed)==len(STAGES) else "FAIL"
 except (subprocess.CalledProcessError,SystemExit) as e:
  status="FAIL"
  summary={"gate":"MERCURY_MR10D24_INTEGRATION","status":status,"completed":completed,"failed_after":completed[-1] if completed else None,"error":str(e),"native_build_certified":False}
  a.report.write_text(json.dumps(summary,indent=2)+"\n"); raise
 summary={"gate":"MERCURY_MR10D24_INTEGRATION","status":status,"completed":completed,"stage_count":len(completed),"final75":final_data,"native_build_certified":False,"next_gate":"native compile + ROM build"}
 a.report.write_text(json.dumps(summary,indent=2)+"\n"); print(json.dumps(summary,indent=2))
 if status!="PASS": raise SystemExit("D24 integration failed")

if __name__=="__main__": main()
