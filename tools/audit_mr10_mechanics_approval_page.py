#!/usr/bin/env python3
"""Validate the MR10 93-mechanic approval page and its embedded review data."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/approval/mr10-93-mechanics-data.json"
HTML = ROOT / "docs/approval/mr10-93-mechanics.html"

data = json.loads(DATA.read_text(encoding="utf-8"))
html = HTML.read_text(encoding="utf-8")
mechanics = data["mechanics"]

checks = {
    "exactly_93_mechanics": len(mechanics) == 93,
    "unique_review_ids": len({m["review_id"] for m in mechanics}) == 93,
    "unique_names": len({m["name"] for m in mechanics}) == 93,
    "all_have_exact_effect": all(m.get("exact_effect") for m in mechanics),
    "all_have_trigger": all(m.get("trigger") for m in mechanics),
    "all_have_restrictions": all(m.get("restrictions") for m in mechanics),
    "all_have_plain_english": all(m.get("plain_english") for m in mechanics),
    "all_have_battle_example": all(m.get("battle_example") for m in mechanics),
    "all_have_engine_explanation": all(m.get("why_new_system") for m in mechanics),
    "all_have_interactions": all(m.get("interactions_to_define") for m in mechanics),
    "all_have_reuse_note": all(m.get("shared_system_value") for m in mechanics),
    "all_have_approval_questions": all(m.get("approval_questions") for m in mechanics),
    "all_have_system_tags": all(m.get("system_tags") for m in mechanics),
    "all_have_complexity": all(m.get("engine_complexity") in {"Low","Medium","High","Very High"} for m in mechanics),
    "four_decision_options": all(m.get("decision_options") == [
        "KEEP AS WRITTEN",
        "REDESIGN",
        "CONVERT TO NORMAL POKEMON MECHANICS",
        "CUT",
    ] for m in mechanics),
    "html_embeds_93_rows": len(re.findall(r'"review_id"\s*:', html)) == 93,
    "html_has_autosave": "localStorage.setItem" in html,
    "html_has_export": "Export decisions" in html and "mercury-mr10-93-mechanics-decisions.json" in html,
    "html_has_import": "Import previous decisions" in html,
    "html_has_deep_sections": all(x in html for x in (
        "Concrete battle example",
        "Why this is one of the 93",
        "Battle interactions that must be defined",
        "What approving this system buys us elsewhere",
        "Questions this approval should answer",
    )),
}

status = "PASS" if all(checks.values()) else "FAIL"
report = {
    "gate": "MERCURY_MR10_93_MECHANIC_APPROVAL_PAGE",
    "status": status,
    "mechanic_count": len(mechanics),
    "shared_system_count": len(data.get("system_summary", [])),
    "checks": checks,
}
print(json.dumps(report, indent=2))
if status != "PASS":
    raise SystemExit(1)
