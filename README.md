# Platinum Modern DS

A modernized Pokémon Platinum project built directly on the native Platinum/pokeplatinum runtime. HG-Engine is retained as a donor/reference for modern mechanics, move systems, animation ideas, and implementation patterns—not as Mercury Redux's final runtime.

## Core goals

- Native Pokémon Platinum / pokeplatinum runtime
- National Pokédex support through #1025
- Fairy type and modern battle mechanics
- Updated abilities, moves, items, and evolution methods
- Preserve Platinum's existing Sinnoh world, progression, scripts, events, save flow, and presentation as the playable foundation
- Quality-of-life improvements
- Elite Redux-inspired information-rich DS UI, rebuilt natively for dual screens
- Reproducible GitHub-based build and checkpoint workflow

## Project rules

- GitHub is the source of truth.
- Do not commit clean commercial ROM images.
- Prefer reproducible source conversion/build steps.
- Keep a known-good playable branch at all times.
- UI replacements must never block basic playability.
- Major milestones are tagged and documented.

## Upstream/reference projects

- HG-Engine: https://github.com/BluRosie/hg-engine
- pokeheartgold: https://github.com/pret/pokeheartgold
- pokeplatinum: https://github.com/pret/pokeplatinum
- Elite Redux: https://github.com/Elite-Redux/eliteredux

## Initial milestones

1. PT01 — reproducible clean pokeplatinum build
2. PT02 — native Platinum full-game baseline certification
3. PT03 — #001–1025 roster/data expansion on Platinum
4. PT04 — modern mechanics, Fairy, abilities, moves, items, and evolution support
5. PT05 — modern DS move-animation integration and Platinum-native visual certification
6. PT06 — Elite Redux-inspired information-rich Platinum UI
7. PT07 — Mercury Redux gameplay/content changes layered onto the certified modern Platinum base

## Architecture correction — 2026-09-24

The project's source-of-truth runtime is now explicitly **pokeplatinum / Pokémon Platinum**, not HGSS/HG-Engine.

HG-Engine remains valuable as a donor and reference library for modern battle systems, data structures, move implementations, animation scripts, tests, and quality-of-life ideas. Nothing imported from HG-Engine is considered runtime-compatible or visually certified until it is ported to and tested inside the Platinum runtime.

The guiding rule is: **modernize the already-complete Platinum game first; then build Mercury Redux on top of that finished, tested Platinum base.**
