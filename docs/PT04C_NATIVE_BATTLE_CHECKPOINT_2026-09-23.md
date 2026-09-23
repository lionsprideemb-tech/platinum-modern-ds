# PT04C Native Victini Battle Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

This checkpoint proves that post-Gen-IV species **SPECIES_VICTINI / National Dex 494** can enter and render inside Pokémon Platinum's native battle engine.

## Proven runtime chain retained

- Run #8: native Party + Pokédex seen/caught proof
- Run #12: native Summary proof
- Run #13: native PC Storage proof
- Run #28: native Battle proof

Earlier sealed gates are not to be repeated unless a later regression directly implicates them.

## Battle proof

GitHub Actions workflow run:

- Run number: **28**
- Run ID: **35888401619**
- Commit: **1c97ff3815bfe42249d7373068b2991a2f18435b**
- Conclusion: **success**

Artifact:

- Name: `pt04c-victini-native-battle-entry-proof`
- Artifact ID: **10763917870**
- SHA-256: `3cd53eeef137102c7411d9d5c3327a122fbb674c7b10711c2cf36b18ac5c71c2`

## Visual verification

Captured native Platinum battle frames were manually reviewed.

- Frame 600: wild Lv.5 Bidoof encounter UI renders normally.
- Frame 900: player send-out sequence says **"Go! VICTINI!"**.
- Frame 960: Victini battle HUD is present as **VICTINI Lv.50**, with **174/174 HP**, while its back sprite begins rendering.
- Frame 1020: Victini's full back sprite is visibly rendered on the player's side.
- Frame 1200: normal native command state is reached with **"What will VICTINI do?"** and **FIGHT / BAG / RUN / POKÉMON** controls.

This is stronger than a no-crash test: species 494 is visibly participating in a native battle with its name, level, HP, battle sprite and command flow intact.

## Control diagnostics

A temporary Mew control on the same battle infrastructure was also used to separate harness/transition behavior from species-494 behavior. The direct native control rendered correctly, confirming the battle application itself was viable. The restored Victini path then reached the full command menu in Run #28.

## PT04C remaining gate

Only the isolated **save → reload → verify Victini survives intact** runtime proof remains before PT04C can be closed and the project can move from the single boundary test species into bulk roster expansion.

## Next action

Do not redo Party, Pokédex, Summary, PC Storage, or Battle.

Proceed directly to:

`PT04C_VICTINI_SAVE_RELOAD_RUNTIME`
