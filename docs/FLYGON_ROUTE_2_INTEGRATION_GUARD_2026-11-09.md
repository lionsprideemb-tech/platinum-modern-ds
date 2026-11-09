# Platinum Modern DS — Flygon Route 2 integration safeguard (2026-11-09)

## Source of truth
Latest user-approved game roster direction: [Sprites Flygon plan JSON](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/flygon-roster-plan-2026-11-09.json) ([context](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/FLYGON_ROUTE_2_DECISION_2026-11-09.md)). This replaces earlier generic Redux-to-Delta *mapping assumptions for the Flygon family only*, without altering original image KEEP/CUT histories.

## One-Mega two-family plan
1. Keep original Trapinch → Vibrava → Flygon species and standard typings.
2. Keep **one** regular Mega Flygon form (preferred previously approved art candidate `Elite_Redux_Bulk/flygon_mega`, subject to graphics/runtime certification); do not implement all artwork alternatives as separate Megas.
3. Reserve **three future Delta entries**: Delta Trapinch, Delta Vibrava, Delta Flygon (**Bug/Ground**). Delta Trapinch and Delta Vibrava must each have the **Bug** type, but they may be mono Bug or Bug paired with another vanilla type; they are not required to be Bug/Ground. Their exact source-approved artwork and optional secondary types must be verified before species/form IDs are assigned.
4. No Delta Mega is planned.
5. Never import Electric/Dragon Redux B `flygon-redux-b` **or** `flygon-redux-b-mega` into the active ROM sprite/species queue; they are archival-only despite old artwork KEEP votes. Leave files and original votes intact.
6. Do not auto-promote rejected `flygon-redux`, `flygon-redux-mega`, `trapinch-redux`, deleted alternate-form files, or undecided `vibrava-redux`. The older `ER125_REDUX_TO_DELTA_MAP.csv` entries for this family are superseded.
7. Once the three genuine Bug/Ground Delta designs have matching approved artwork and the new species IDs pass collision checks, require full front/back/shiny/icon verification, compatible DS archives, reproducible Platinum build, and emulator visual tests.

**Scope of this commit: planning/integration guard only.** No game resource files, sprites, species registry, maps, mechanics or playable ROM were changed; preserve all existing modern Platinum QoL systems.
