# MR08 Ability Mechanics Policy — Canonical Gen 1–9 First

**Status:** LOCKED PROJECT RULE  
**Approved:** 2026-09-27  
**Branch:** `feature/mr07-summary-skills`

## Rule

During the current ability-mechanics implementation phase, Pokémon Mercury Redux will only implement mechanics that exist in the nine official mainline Pokémon generations (Generations I–IX).

The current 100-ability Step 1 therefore covers only canonical/vanilla Pokémon ability mechanics.

## Allowed in Step 1

- Official abilities and mechanics from Generations I–IX.
- Modern canonical behavior updates for older abilities when the official games changed how they work.
- DS-engine support code required to reproduce those canonical mechanics.
- Shared battle hooks needed by multiple canonical abilities.

## Deferred until a later design phase

Do **not** add new fan-made/custom mechanics during Step 1, even if they are available in:
- Elite Redux
- other ROM hacks
- public DS repositories
- Mercury custom ability concepts

Those sources may still be consulted as implementation references, but custom mechanics themselves remain deferred.

## Custom ability policy later

After the canonical Gen I–IX ability foundation is complete and stable, custom abilities may be reviewed separately. At that point Mercury can decide which new mechanics are worth adding, balancing, renaming, merging, or rejecting.

## Batch implementation rule

The canonical 100-ability workload should be handled in grouped batches by shared battle hook/mechanic family rather than one ability at a time. Full ROM builds should be used at milestone batches instead of after every individual ability.

This file is the project marker for the canonical-first ability rule.
