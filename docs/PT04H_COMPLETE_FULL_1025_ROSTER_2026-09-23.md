# PT04H Full Canonical Roster Complete — 2026-09-23

## Status

**COMPLETE / SEALED**

Mercury DS now has a proven contiguous canonical base-species architecture from **Bulbasaur #1 through Pecharunt #1025**.

## Completed proof chain

- Generation V through Genesect #649 — sealed
- Generation VI through Volcanion #721 — sealed
- Generation VII through Melmetal #809 — sealed
- Generation VIII through Enamorus #905 — sealed
- Generation IX through Pecharunt #1025 — sealed

For the final #1025 boundary, all of the following passed independently:

- donor audit,
- cumulative full-roster compile,
- native save -> DS reset -> native reload,
- representative six-species Gen IX Party rendering,
- native Pecharunt battle rendering.

## Final canonical architecture

- `SPECIES_BULBASAUR` = 1
- `SPECIES_PECHARUNT` = 1025
- `SPECIES_EGG` = 1026
- `SPECIES_BAD_EGG` = 1027

Compiled cumulative archives at the full-roster build:

- `pl_personal.narc`: 1040 members
- `pl_pokegra.narc`: 6156 members
- `pl_poke_icon.narc`: 1079 members
- `height.narc`: 4104 members

## Recovery rule

Do not repeat Victini, Genesect, Volcanion, Melmetal, Enamorus, or Pecharunt runtime proofs unless a later change directly invalidates one of their assumptions.

## New project priority

The next phase is **PLAYABLE_BASELINE**.

Goal: produce and preserve a complete start-to-finish playable Mercury DS build before importing more advanced mechanics.

The baseline should retain:

- Mercury title branding,
- Fairy/type infrastructure already present,
- the complete #1–1025 canonical base-species capacity,
- native Platinum save/load, battle, party, PC, shops, field systems, story scripts, maps, badges, League, Cynthia, credits, and postgame return.

The baseline should avoid adding new high-risk systems until a complete normal game build is certified.

Advanced abilities, modern learnsets, evolution mechanics, forms, custom Megas, balancing, quests, randomizer features, and deeper Mercury story changes remain follow-up work on branches created from the sealed playable copy.
