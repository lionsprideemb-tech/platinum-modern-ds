# MR09 Safe Runtime Lane

Status: ACTIVE
Branch: `feature/mr09-safe-runtime`
Date: 2026-09-29

## Purpose

This branch is the runtime implementation lane for everything that can be built
without deciding Mercury's pending Elite Redux-style custom battle systems.

The rule is intentionally conservative: no unresolved custom status, field, or
new-engine mechanic is allowed to become live merely because an individual
Ability can attach to an existing hook.

## Frozen input checkpoint

The MR09 staging library contains 883 implementation-ready source rows:

- 503 existing-hook
- 287 light-extension
- 93 new-engine-system

The safe-queue builder performs a second dependency screen. In addition to the
93 new-engine-system rows, it defers non-new-engine rows that still reference
pending custom systems such as Bleed, Fear/Scare, Enrage, Toxic Terrain,
Eerie/Fog mechanics, Creeping Thorns, Frostbite, or contagious custom spores.

Current conservative queue:

- 883 staged total
- 93 direct new-engine rows deferred
- 38 extra dependency rows deferred
- 48 canonical Elite Redux overrides kept on their existing canonical IDs
- 704 unique custom Abilities eligible for the safe custom namespace
- 752 total safe rows
- provisional safe custom IDs 311..1014
- 9 IDs remain through the current 1023 Ability storage ceiling

The 704 custom IDs are an implementation namespace, not a species-distribution
decision. No Pokémon should receive one until its runtime hook is certified.

## Runtime rules

1. Use the existing MR08 canonical engine hooks wherever behavior is genuinely
   identical.
2. Light extensions may add bounded state or branch logic, but may not create a
   pending custom gameplay system.
3. Work in 12-15 Ability atomic commits unless a shared hook makes a slightly
   larger group materially safer.
4. Never invent missing semantics.
5. An Ability changes from `queued_not_implemented` only in the same commit
   that installs and validates its actual battle mechanics.
6. Preserve Primary/Innate routing and suppression behavior.
7. Do not touch the locked MR07 Summary/editor visuals.
8. Keep the 93 new-engine rows and the 38 dependency rows quarantined for the
   user's custom-mechanics review.

## Moves

The independent community-move lane already has a certified no-new-mechanics
pipeline through CM10. That work remains separate from this branch so the
ability integration cannot destabilize the certified move checkpoint. Any move
whose behavior depends on one of the quarantined systems stays deferred until
the same mechanics review.

## Capacity warning

The current safe custom namespace fits under ID 1023, but only nine IDs remain.
The held custom-system group cannot all be added later without either reducing
the final custom roster or expanding the Ability storage architecture. Do not
consume those nine spare IDs casually.
