#!/usr/bin/env python3
"""MR10A3 — rebase an already-patched Mercury runtime tree onto the final 16-bit namespace.

This deliberately runs *after* the legacy MR10 custom-runtime installers have
patched battle source. Those installers were certified against the temporary
311..929 staging namespace, but the C they emit references symbolic
ABILITY_* tokens rather than numeric literals. Replacing generated/abilities.txt
only after all runtime patches therefore preserves the mechanics while rebinding
those symbols to the reconciled 16-bit IDs.

Gate invariants:
- staging runtime code is already present;
- MP05 canonical 0..310 base exists before rebase;
- final namespace becomes official 0..319 + Mercury 320..1066;
- all implemented registry tokens still exist exactly once after rebase;
- no runtime source rewrite is performed here.
"""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root",type=Path)
    ap.add_argument("hg_engine_root",type=Path)
    ap.add_argument("--partition",type=Path,default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--implemented-registry",type=Path,required=True)
    ap.add_argument("--report",type=Path,default=Path("mr10a3-runtime-namespace-rebase.json"))
    args=ap.parse_args()

    root=args.pokeplatinum_root.resolve()
    hg=args.hg_engine_root.resolve()
    reg=args.implemented_registry.resolve()
    tools=Path(__file__).resolve().parent

    before=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
    implemented=[x.strip() for x in reg.read_text().splitlines() if x.strip()]
    staging_tail=len(before)-1

    subprocess.run([
        sys.executable,
        str(tools/"install_mr10_16bit_ability_storage.py"),
        str(root),
        "--report","mr10a3-storage.json",
    ],check=True)
    subprocess.run([
        sys.executable,
        str(tools/"install_mr10a2_16bit_full_namespace.py"),
        str(root),str(hg),
        "--partition",str(args.partition.resolve()),
        "--report","mr10a3-namespace.json",
    ],check=True)

    after=[x.strip() for x in (root/"generated/abilities.txt").read_text().splitlines() if x.strip()]
    missing=[t for t in implemented if t not in after]
    duplicate=[t for t in implemented if after.count(t)!=1]

    checks={
        "staging_namespace_was_present": staging_tail >= 929,
        "final_tail_is_1066": len(after)==1067,
        "aura_guard_is_319": after[319]=="ABILITY_AURA_GUARD",
        "deep_pockets_is_1065": after[1065]=="ABILITY_MR_DEEP_POCKETS",
        "predators_edge_is_1066": after[1066]=="ABILITY_MR_PREDATORS_EDGE",
        "all_previously_implemented_tokens_survive": not missing,
        "implemented_tokens_unique_in_final_namespace": not duplicate,
        "final_storage_16bit": json.loads(Path("mr10a3-storage.json").read_text())["ability_id_bits"]==16,
        "namespace_gate_pass": json.loads(Path("mr10a3-namespace.json").read_text())["status"]=="PASS",
    }
    status="PASS" if all(checks.values()) else "FAIL"
    report={
        "gate":"MERCURY_MR10A3_RUNTIME_NAMESPACE_REBASE",
        "status":status,
        "staging_registry_count":len(before),
        "final_registry_count":len(after),
        "implemented_registry_count":len(implemented),
        "missing_implemented_tokens":missing,
        "duplicate_implemented_tokens":duplicate,
        "checks":checks,
        "meaning":"Existing runtime source patches are retained and their symbolic Ability references now compile against reconciled 16-bit IDs."
    }
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if status!="PASS":
        raise SystemExit("runtime namespace rebase failed")


if __name__=="__main__":
    main()
