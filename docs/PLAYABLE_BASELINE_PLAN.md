# PLAYABLE BASELINE — Build-First Plan

## Project decision

Before importing more advanced modern mechanics, Mercury DS will produce and preserve a complete playable game based on the finished Pokémon Platinum adventure.

The goal of this phase is not to maximize Mercury features. The goal is to establish a **known-good, normal, start-to-finish game build** that later work can safely branch from.

## Baseline foundation already sealed

The playable baseline begins from the completed PT04H checkpoint:

- canonical base-species IDs #1–1025 are proven,
- Pecharunt #1025 is proven through native compile, save/reload, Party UI, and battle rendering,
- Egg/Bad Egg remain after the canonical roster,
- Mercury title resources are preserved,
- Fairy/type infrastructure already present in the Platinum overlay is preserved.

## Baseline rule

Do not add another large mechanics system until the playable baseline is built and frozen.

For the first candidate:

- use Platinum's native maps,
- use Platinum's native story scripts and progression,
- use Platinum's native trainers and encounters,
- use Platinum's native shops and item progression,
- use Platinum's native save/load path,
- use Platinum's native Gym -> Galactic -> Victory Road -> Elite Four -> Cynthia -> credits flow,
- regenerate the complete #1–1025 resource capacity,
- do not install any CI runtime harness into the normal game build.

This intentionally means many added post-Gen-IV species are present as engine resources but are not yet distributed through the adventure. Their modern abilities, movesets, evolution methods, forms, and balancing remain later upgrade passes.

## Certification phases

### PB01 — Normal full-roster ROM candidate

Build the normal game with no runtime-test injection and prove:

- full #1–1025 registry compiles,
- expected final NARC counts are intact,
- Mercury title reaches its live native title screen,
- title accepts native input and continues into normal game flow,
- ROM remains running and nonblank after leaving the title,
- story/map/script resources remain Platinum-native in this first candidate.

### PB02 — Early-game playable certification

Verify manually/automatically where practical:

- New Game,
- Rowan intro,
- player/rival naming,
- Twinleaf,
- Route 201 / Lake Verity opening,
- Sandgem / starter / Pokédex,
- first normal wild battle and capture,
- save -> reset -> continue.

### PB03 — Progression structure certification

Check all mandatory Platinum progression resources remain present and unmodified for:

- Oreburgh / Badge 1,
- Eterna / Badge 2,
- Hearthome / Badge 3,
- Veilstone / Badge 4,
- Pastoria / Badge 5,
- Canalave / Badge 6,
- Snowpoint / Badge 7,
- Sunyshore / Badge 8,
- Galactic HQ / Spear Pillar / Distortion World,
- Victory Road,
- Elite Four,
- Cynthia,
- credits and postgame return.

### PB04 — First playable seal

After a complete playthrough has no progression-blocking crash, softlock, bad warp, or save failure:

- create an immutable playable checkpoint branch,
- preserve a build manifest and ROM hash,
- use that checkpoint as the parent for all later mechanics/content work.

## Deferred until after playable seal

- full modern ability import,
- real modern learnsets and move mechanics,
- evolution modernization,
- base EXP widening,
- alternate/regional forms,
- custom Mercury Megas and Deltas,
- randomizer systems,
- trainer rebalance,
- encounter overhaul,
- custom map/story replacement,
- side quests and customization.

Those systems will be layered onto a finished game rather than standing between the project and a playable ROM.
