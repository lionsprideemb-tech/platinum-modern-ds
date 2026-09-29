# MR10 — 93 Custom Mechanics Approval

This folder contains the owner-review surface for every MR09 Ability classified as
`new_engine_system`.

## Review page

Open **`mr10-93-mechanics.html`** in a browser. It is fully self-contained: all
93 mechanic records and their deep explanations are embedded in the HTML.

Each mechanic includes:

- exact intended behavior;
- trigger and restrictions;
- a plain-English explanation;
- a concrete battle example;
- why a new engine system is required;
- important battle interactions that must be defined;
- which reusable engine system the work would create for other Abilities/moves;
- specific approval questions;
- four owner choices: **Keep as written / Redesign / Convert to normal Pokémon mechanics / Cut**;
- a freeform notes box.

Choices autosave in browser local storage. The page can export a JSON decisions
file and later import it again. Merely reviewing the page does **not** modify game
code.

## Shared-system view

The page also groups the 93 mechanics into reusable engine areas such as
generated/reactive moves, battle-only typing, multi-hit rewriting, persistent
counters/survival, field conditions, form control, custom status, and linked
damage. This is intentional: the point of the review is not only to judge each
Ability, but to decide which reusable Mercury systems are worth building because
custom moves are waiting on many of the same foundations.

## Validation

Run:

```bash
python3 tools/audit_mr10_mechanics_approval_page.py
```

The audit fails unless all 93 entries contain the complete deep-review fields and
the interactive page embeds all 93 records.
