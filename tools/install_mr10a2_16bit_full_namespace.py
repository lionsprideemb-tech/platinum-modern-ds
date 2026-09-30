#!/usr/bin/env python3
"""MR10A2 — install the reconciled 16-bit Mercury Ability namespace.

Assumes:
- MP05 canonical 0..310 namespace already installed.
- MR10 16-bit persistence upgrade already installed.
- data/mr10_ability_partition_16bit_full_identity.json is authoritative for
  Mercury custom IDs 320..1066.

IDs 311..319 are taken directly from hg-engine. 314 and 317 remain donor
placeholder/reserved slots so the numeric canonical tail stays stable.
"""

from __future__ import annotations
import argparse, json, re, textwrap
from pathlib import Path

CANONICAL_BASE_MAX = 310
CANONICAL_TAIL_MAX = 319
CUSTOM_FIRST = 320

DEFINE_RE = re.compile(r"^#define\s+(ABILITY_[A-Z0-9_]+)\s+(\d+)\s*$", re.M)

DS_TEXT_REPLACEMENTS = str.maketrans({
    "'": "’",
    '"': "”",
    "\u2018": "‘",
    "\u2019": "’",
    "\u201c": "“",
    "\u201d": "”",
    "\u2013": "-",
    "\u2014": "-",
    "\u00a0": " ",
})

def ds_text(text: str) -> str:
    text = text.translate(DS_TEXT_REPLACEMENTS)
    return text.replace("3 > 1", "3 Beats 1")

def description_value(raw: str):
    parts = raw.split(r"\n")
    if len(parts) == 1:
        return raw
    return [p + ("\n" if i < len(parts)-1 else "") for i,p in enumerate(parts)]

def short_description(effect: str):
    clean = re.sub(r"\s+", " ", ds_text(effect).strip())
    lines = textwrap.wrap(clean, width=31, break_long_words=False, break_on_hyphens=False)
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] = lines[-1].rstrip(" .") + "..."
    if not lines:
        lines = ["Custom Ability."]
    return [s + ("\n" if i < len(lines)-1 else "") for i,s in enumerate(lines)]

def ensure_message(bank: dict, prefix: str, idx: int, value) -> None:
    mid=f"{prefix}_{idx:05d}"
    for m in bank["messages"]:
        if m["id"]==mid:
            m["en_US"]=value
            return
    bank["messages"].append({"id":mid,"en_US":value})

def load_bank(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def save_bank(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")

def load_supported_chars(root: Path) -> set[str]:
    out=set()
    for raw in (root/"tools/msgenc/charmap.txt").read_text(encoding="utf-8").splitlines():
        line=raw.rstrip("\n")
        if not line or line.lstrip().startswith("//") or "=" not in line:
            continue
        v=line.split("=",1)[1]
        if len(v)==1: out.add(v)
    return out

def bank_supported(bank: dict, supported: set[str]) -> bool:
    def ok(v):
        if isinstance(v,str): return all(ch in supported or ch in "\n\r\t" for ch in v)
        if isinstance(v,list): return all(ok(x) for x in v)
        if isinstance(v,dict): return all(ok(x) for k,x in v.items() if k!="id")
        return True
    return all(ok(m.get("en_US")) for m in bank["messages"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("hg_engine_root", type=Path)
    ap.add_argument("--partition", type=Path, default=Path("data/mr10_ability_partition_16bit_full_identity.json"))
    ap.add_argument("--report", type=Path, default=Path("mr10a2-16bit-full-namespace.json"))
    args=ap.parse_args()

    root=args.pokeplatinum_root.resolve()
    hg=args.hg_engine_root.resolve()
    plan=json.loads(args.partition.read_text(encoding="utf-8"))
    custom=sorted((x for x in plan["abilities"] if x.get("runtime_kind")=="custom_id"), key=lambda x:x["id"])
    ids=[x["id"] for x in custom]
    expected=list(range(CUSTOM_FIRST, custom[-1]["id"]+1))
    if ids != expected:
        missing=sorted(set(expected)-set(ids))
        raise SystemExit(f"custom namespace must be contiguous {CUSTOM_FIRST}..{custom[-1]['id']}; missing {missing[:20]}")
    if custom[-1]["id"] > 0xFFFF:
        raise SystemExit("custom namespace exceeds 16-bit capacity")

    donor_text=(hg/"include/constants/ability.h").read_text()
    donor_by_id={int(n):tok for tok,n in DEFINE_RE.findall(donor_text)}
    for i in range(CANONICAL_BASE_MAX+1, CANONICAL_TAIL_MAX+1):
        if i not in donor_by_id:
            raise SystemExit(f"hg-engine missing ability ID {i}")

    reg=root/"generated/abilities.txt"
    abilities=[x.strip() for x in reg.read_text().splitlines() if x.strip()]
    if len(abilities) != CANONICAL_BASE_MAX+1:
        raise SystemExit(f"expected MP05 registry length 311, got {len(abilities)}")

    for i in range(CANONICAL_BASE_MAX+1, CANONICAL_TAIL_MAX+1):
        abilities.append(donor_by_id[i])
    for row in custom:
        if row["id"] != len(abilities):
            raise SystemExit(f"registry gap before {row['display_name']}: expected {len(abilities)}, got {row['id']}")
        abilities.append(row["token"])
    reg.write_text("\n".join(abilities)+"\n", encoding="utf-8")

    names_hg=(hg/"data/text/720.txt").read_text(encoding="utf-8").splitlines()
    upper_hg=(hg/"data/text/721.txt").read_text(encoding="utf-8").splitlines()
    desc_hg=(hg/"data/text/722.txt").read_text(encoding="utf-8").splitlines()
    if min(len(names_hg),len(upper_hg),len(desc_hg)) <= CANONICAL_TAIL_MAX:
        raise SystemExit("hg-engine ability text banks do not reach 319")

    names=load_bank(root/"res/text/ability_names.json")
    upper=load_bank(root/"res/text/ability_names_uppercase.json")
    desc=load_bank(root/"res/text/ability_descriptions.json")
    for bank in (names,upper,desc):
        bank["messages"]=bank["messages"][:CANONICAL_BASE_MAX+1]

    for i in range(CANONICAL_BASE_MAX+1,CANONICAL_TAIL_MAX+1):
        ensure_message(names,"pl_msg_00000610",i,ds_text(names_hg[i]))
        ensure_message(upper,"pl_msg_00000611",i,ds_text(upper_hg[i]))
        ensure_message(desc,"pl_msg_00000612",i,description_value(ds_text(desc_hg[i])))

    for row in custom:
        idx=row["id"]; name=ds_text(row["display_name"])
        ensure_message(names,"pl_msg_00000610",idx,name)
        ensure_message(upper,"pl_msg_00000611",idx,name.upper())
        ensure_message(desc,"pl_msg_00000612",idx,short_description(row["exact_effect"]))

    save_bank(root/"res/text/ability_names.json",names)
    save_bank(root/"res/text/ability_names_uppercase.json",upper)
    save_bank(root/"res/text/ability_descriptions.json",desc)

    supported=load_supported_chars(root)
    checks={
        "official_tail_311_319_present": abilities[311:320] == [donor_by_id[i] for i in range(311,320)],
        "official_placeholders_reserved": abilities[314]=="ABILITY_TEMP2" and abilities[317]=="ABILITY_TEMP4",
        "aura_guard_at_319": abilities[319]=="ABILITY_AURA_GUARD",
        "custom_ids_contiguous_320_tail": ids==expected,
        "full_registry_contiguous": len(abilities)==custom[-1]["id"]+1,
        "registry_tail_predators_edge": abilities[-1]=="ABILITY_MR_PREDATORS_EDGE",
        "registry_contains_deep_pockets": abilities[1065]=="ABILITY_MR_DEEP_POCKETS",
        "registry_contains_predators_edge": abilities[1066]=="ABILITY_MR_PREDATORS_EDGE",
        "name_bank_size": len(names["messages"])==len(abilities),
        "upper_bank_size": len(upper["messages"])==len(abilities),
        "description_bank_size": len(desc["messages"])==len(abilities),
        "text_charmap_safe": all(bank_supported(b,supported) for b in (names,upper,desc)),
        "fits_16bit": custom[-1]["id"] <= 0xFFFF,
    }
    status="PASS" if all(checks.values()) else "FAIL"
    report={
        "gate":"MERCURY_MR10A2_16BIT_FULL_NAMESPACE",
        "status":status,
        "canonical_range":[0,319],
        "reserved_official_slots":[314,317],
        "custom_range":[320,custom[-1]["id"]],
        "custom_count":len(custom),
        "registry_count":len(abilities),
        "next_free_id":custom[-1]["id"]+1,
        "storage_capacity":65535,
        "checks":checks,
    }
    args.report.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if status!="PASS":
        raise SystemExit("MR10A2 full namespace validation failed")

if __name__=="__main__":
    main()
