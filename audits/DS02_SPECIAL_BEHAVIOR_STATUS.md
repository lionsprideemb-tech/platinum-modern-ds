# DS02 Initial Special-Behavior Status

This is an implementation-status audit for high-risk modern species mechanics on the pinned HG-Engine revision.

Statuses are conservative:
- **VERIFIED_UPSTREAM_TESTED** — implementation exists and dedicated upstream battle tests exist.
- **PARTIAL** — structure/hooks exist, but behavior is incomplete or not fully verified.
- **MISSING_BEHAVIOR** — constants/data exist, but the functional behavior is absent in the inspected implementation path.
- **NEEDS_AUDIT** — not yet classified.

| Species / mechanic | Status | Evidence |
|---|---|---|
| Palafin — Zero to Hero | VERIFIED_UPSTREAM_TESTED | Functional switch/form logic exists in battle code and dedicated tests exist under `data/battle_tests/abilities/zero_to_hero/`, including switch-out/back-in and Flip Turn cases. |
| Morpeko — Hunger Switch | VERIFIED_UPSTREAM_TESTED | Functional handling exists and dedicated tests exist under `data/battle_tests/abilities/hunger_switch/`, including Full Belly → Hangry, Transform, and terastallized cases. |
| Tatsugiri/Dondozo — Commander | MISSING_BEHAVIOR | Ability constants/flags exist, but the dedicated `// Commander` switch-in block in `SwitchInAbilityCheck.c` is empty on the pinned revision; no dedicated Commander battle tests were found. |
| Ogerpon — Embody Aspect | MISSING_BEHAVIOR | Four Embody Aspect ability constants and flags exist, but no functional implementation or dedicated tests were found in the pinned revision. |
| Terapagos — Tera Shift | MISSING_BEHAVIOR | A switch-in state and case exist, but the `ABILITY_TERA_SHIFT` case body is empty and does not trigger form logic on the pinned revision. |
| Terapagos — Tera Shell | MISSING_BEHAVIOR | `BattleController_CheckTeraShell` is explicitly marked `TODO: implement new mechanics` and returns `FALSE`; damage calculation also contains a TODO to factor in Tera Shell. |
| Terapagos — Teraform Zero | MISSING_BEHAVIOR | Ability constant/flags exist, but no functional implementation or dedicated test was found. |

## Interpretation

The canonical #001–1025 static roster is present, but a small number of modern species-specific mechanics are intentionally unfinished upstream.

This is substantially smaller in scope than importing hundreds of missing Pokémon.

For Platinum Modern DS, these gaps can be handled one-by-one after the base engine and Platinum world are stable. They should not block DS01 or the initial Sinnoh world proof-of-concept.

## Next behavior-audit targets

- Gulp Missile
- Ice Face
- Schooling
- Shields Down
- Battle Bond
- Stance Change
- Zen Mode
- Power Construct
- Disguise
- Cramorant forms
- Basculegion / Last Respects interactions
- Maushold / Population Bomb interactions
- Dudunsparce form selection
- Gimmighoul/Gholdengo evolution adaptation
- Kingambit evolution adaptation
- Annihilape evolution adaptation
- regional/form persistence through PC/save/load
