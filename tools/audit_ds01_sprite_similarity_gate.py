#!/usr/bin/env python3
"""Validate the sealed DS01 sprite-similarity audit and quarantine policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED_ARCHIVE_SHA = "6f676782799cb206d55a00260a693fccc25f5f59c8fc6b2819aeceaf1beb38f0"
EXPECTED_STRONG_TARGETS = {
    "blastoise_mega_x",
    "butterfree_mega",
    "centiskorch_mega",
    "charizard_mega_z",
    "cinderace_mega",
    "coalossal_mega",
    "copperajah_mega",
    "corviknight_mega",
    "drednaw_mega",
    "garbodor_mega",
    "gengar_mega_x",
    "grimmsnarl_mega",
    "hatterene_mega",
    "inteleon_mega",
    "kingler_mega",
    "lapras_mega",
    "machamp_mega",
    "melmetal_mega",
    "meowth_partner_mega",
    "orbeetle_mega",
    "pikachu_partner_mega",
    "rillaboom_mega",
    "sandaconda_mega",
    "snorlax_mega",
    "toxtricity_mega",
    "urshifu_mega",
    "urshifu_rapid_strike_style_mega",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("similarity", type=Path)
    ap.add_argument("quarantine", type=Path)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()

    similarity = json.loads(args.similarity.read_text(encoding="utf-8"))
    quarantine = json.loads(args.quarantine.read_text(encoding="utf-8"))

    errors: list[str] = []

    if similarity.get("gate") != "MERCURY_DS01_FULL_SPRITE_SIMILARITY_AUDIT":
        errors.append("unexpected similarity audit gate")
    if similarity.get("status") != "PASS":
        errors.append("similarity audit status must be PASS")
    if similarity.get("archive", {}).get("sha256") != EXPECTED_ARCHIVE_SHA:
        errors.append("sprite archive SHA-256 changed")

    coverage = similarity.get("coverage", {})
    if coverage.get("hg_engine_ready_images") != 11365:
        errors.append("expected 11,365 HG-engine-ready images")
    if coverage.get("hg_engine_ready_male_front_designs") != 2455:
        errors.append("expected 2,455 male/front design representatives")
    if coverage.get("nested_source_pack_images") != 11341:
        errors.append("expected 11,341 nested source-pack images")
    if coverage.get("total_image_occurrences_scanned_including_nested_sources") != 22738:
        errors.append("expected 22,738 total image occurrences scanned")

    gmax = similarity.get("mega_vs_gmax_similarity", {})
    strong = set(gmax.get("strong_targets", []))
    if strong != EXPECTED_STRONG_TARGETS:
        missing = sorted(EXPECTED_STRONG_TARGETS - strong)
        extra = sorted(strong - EXPECTED_STRONG_TARGETS)
        errors.append(f"strong Mega/G-Max set mismatch; missing={missing}; extra={extra}")
    if gmax.get("strong_similarity_target_count") != len(EXPECTED_STRONG_TARGETS):
        errors.append("strong Mega/G-Max target count mismatch")

    policy = quarantine.get("policy", {})
    for key in ("install_assets", "delete_assets", "replace_assets"):
        if policy.get(key) is not False:
            errors.append(f"quarantine policy must keep {key}=false")

    blocker_targets: set[str] = set()
    for entry in quarantine.get("confirmed_blockers", []):
        blocker_targets.update(entry.get("entries", []))
    missing_blockers = sorted(EXPECTED_STRONG_TARGETS - blocker_targets)
    if missing_blockers:
        errors.append(f"strong similarity targets missing from confirmed blockers: {missing_blockers}")

    four_way = {"darkrai_mega", "heatran_mega", "slate", "zeraora_mega"}
    if not any(four_way.issubset(set(x.get("entries", []))) for x in quarantine.get("confirmed_blockers", [])):
        errors.append("four-way unrelated placeholder collision is not quarantined")

    recovery = quarantine.get("recovery_assessment", {})
    candidates = {
        row.get("target"): row.get("candidate")
        for row in recovery.get("confirmed_same_concept_alternatives", [])
    }
    for target, expected in {
        "darkrai_mega": "darkrai-mega",
        "heatran_mega": "heatran-mega",
        "zeraora_mega": "zeraora-mega",
    }.items():
        if candidates.get(target) != expected:
            errors.append(f"missing recovered same-concept candidate for {target}")

    report = {
        "gate": "MERCURY_DS01_SPRITE_SIMILARITY_CERTIFICATION",
        "status": "PASS" if not errors else "FAIL",
        "analysis_only": True,
        "archive_sha256": similarity.get("archive", {}).get("sha256"),
        "hg_engine_ready_images": coverage.get("hg_engine_ready_images"),
        "male_front_designs": coverage.get("hg_engine_ready_male_front_designs"),
        "nested_source_images": coverage.get("nested_source_pack_images"),
        "strong_gmax_duplicate_targets": len(strong),
        "errors": errors,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit("DS01 sprite similarity certification failed")


if __name__ == "__main__":
    main()
