# Platinum Modern DS

A modernized Sinnoh project built on the Nintendo DS using HG-Engine as the gameplay foundation and Pokémon Platinum as the world/content reference.

## Core goals

- HG-Engine foundation
- National Pokédex support through #1025
- Fairy type and modern battle mechanics
- Updated abilities, moves, items, and evolution methods
- Pokémon Platinum world/progression ported to the HG-Engine/HGSS runtime
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

1. DS01 — reproducible clean HG-Engine build
2. DS02 — #001–1025 roster audit
3. DS03 — modern mechanics/QoL certification
4. DS04 — Platinum Twinleaf world proof-of-concept
5. DS05 — Twinleaf → Route 201 → Sandgem playable slice
6. DS06 — first Elite Redux-inspired native DS UI screen
