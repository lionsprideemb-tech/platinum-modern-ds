#!/usr/bin/env python3
"""Rebuild Mercury's complete MR08 canonical Ability mechanics stack."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


def natural_key(path: Path):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", path.name)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("pokeplatinum_root", type=Path)
    ap.add_argument("--implemented-registry", type=Path, required=True)
    ap.add_argument("--reports-dir", type=Path, default=Path("mr08-stack-reports"))
    ap.add_argument("--report", type=Path, default=Path("mr08-stack.json"))
    args = ap.parse_args()

    root = args.pokeplatinum_root.resolve()
    registry = args.implemented_registry.resolve()
    reports = args.reports_dir.resolve()
    reports.mkdir(parents=True, exist_ok=True)

    installers = sorted(Path("tools").glob("install_mr08*.py"), key=natural_key)
    if not installers:
        raise SystemExit("no MR08 installers found")

    completed = []
    for installer in installers:
        report = reports / f"{installer.stem}.json"
        cmd = [
            sys.executable,
            str(installer),
            str(root),
            "--implemented-registry",
            str(registry),
            "--report",
            str(report),
        ]
        subprocess.run(cmd, check=True)
        completed.append(installer.name)

    certification = reports / "mr08-final-certification.json"
    subprocess.run(
        [
            sys.executable,
            "tools/audit_mr08_final_canonical_abilities.py",
            str(root),
            "--implemented-registry",
            str(registry),
            "--installers-dir",
            "tools",
            "--report",
            str(certification),
        ],
        check=True,
    )

    cert = json.loads(certification.read_text(encoding="utf-8"))
    result = {
        "gate": "MERCURY_MR08_COMPLETE_STACK_REBUILD",
        "status": cert["status"],
        "installer_count": len(completed),
        "installers": completed,
        "certification": str(certification),
        "canonical_modern_implemented": cert["implemented_registry"]["modern_count"],
    }
    args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit("MR08 stack rebuild failed")


if __name__ == "__main__":
    main()
