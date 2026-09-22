# Platinum Modern DS

A modernized Pokémon Platinum project that keeps **Platinum itself as the runtime, world, story, map, and event foundation**.

The earlier HG-Engine transplant experiment is preserved in Git history and its feature branches, but it is no longer the active architecture.

## Core goals

- Native Pokémon Platinum world and progression
- Preserve Sinnoh maps, interiors, scripts, camera behavior, music, and story flow
- Expand the canonical Pokédex toward #1025 without replacing the Platinum world engine
- Fairy type and modern battle mechanics
- Updated abilities, moves, items, evolutions, learnsets, and encounter data
- High-value quality-of-life improvements
- Elite Redux-inspired information-rich DS UI rebuilt natively for Platinum
- Later Mercury-specific Pokémon, Megas, randomizer systems, quests, and customization
- Reproducible GitHub-based builds and checkpoint branches

## Project rules

- GitHub is the source of truth.
- Do not commit commercial ROM images.
- Build from the pinned `pret/pokeplatinum` source.
- Apply project changes as source/asset overlays or explicit patches.
- Keep a known-good native Platinum baseline at all times.
- Do not replace working Platinum world systems unless a feature truly requires it.
- New mechanics must not break normal Platinum progression.
- Major milestones are tagged and documented.

## Active architecture

- **Runtime/base:** pret/pokeplatinum
- **World/story:** native Pokémon Platinum
- **Modern mechanics donors/references:** HG-Engine, Elite Redux, later-generation research/assets where legally and technically appropriate
- **Project modifications:** `platinum-overlay/`

## Active milestones

1. PT01 — reproducible native Platinum build
2. PT02 — modification overlay + visible proof change
3. PT03 — modern type/mechanics foundation
4. PT04 — Pokédex expansion architecture
5. PT05 — moves / abilities / items / evolutions expansion
6. PT06 — QoL foundation
7. PT07 — first Redux-inspired native Platinum UI screen

See `docs/PT01_PLATINUM_NATIVE_PIVOT.md` for the architecture pivot.
