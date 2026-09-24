# Mercury DS — Fastest Path Roadmap

**Decision date:** 2026-09-24  
**Active branch:** `feature/mercury-build-forward`  
**Primary goal:** finish a complete, modernized Pokémon Platinum first; only then transform that stable game into Pokémon Mercury Redux through small, isolated changes.

---

## 1. Core project decision

Mercury DS will use **native Pokémon Platinum as the finished game/world foundation**.

The source code is the authoritative project. The clean retail Platinum ROM is a private reference/build input only; it is **never committed to GitHub**.

Clean reference supplied for local verification:

- File: `Pokemon - Platinum Version (USA).nds`
- Size: 134,217,728 bytes
- SHA-256: `ede62292aa7f7014ff27d42097e769753380531739889c29b968b67b80f80678`

The clean ROM can be used later for reproducible patch generation and binary comparison, but all engine changes must remain reproducible from source.

### Fast-path rule

Until the modern Platinum baseline is sealed, preserve Platinum's:

- maps and warps,
- story/event scripts,
- badge progression,
- Galactic progression,
- trainers,
- encounter tables,
- shops,
- League/Cynthia flow,
- credits,
- save/load behavior.

Do **not** redesign the adventure while the engine modernization is still moving.

---

## 2. What is already proven

The project does not start from zero.

Already established on existing project branches/checkpoints:

- native `pret/pokeplatinum` source build,
- project-owned Platinum overlay,
- Mercury title resources,
- Fairy/type foundation,
- expanded canonical base-species resource architecture through #1025,
- post-Gen-IV species compile/runtime boundary proof,
- Party / Summary / battle / save-reload proofs for expanded species,
- complete Platinum world/story still available as the underlying adventure,
- pinned HG-Engine donor containing modern Pokémon data,
- canonical moves through Gen 9 in the donor,
- canonical abilities through Gen 9 in the donor,
- sprites/icons and supporting donor tables for the expanded roster.

Current build-forward work:

- **PT05A:** compatible modern learnsets for #494-1025,
- **PT05B:** compatible evolution data for #494-1025.

---

# PART I — FINISH “MODERN PLATINUM”

## Phase MP0 — Protect the working foundation

**Purpose:** prevent regressions and stop architecture churn.

### Rules

1. Keep `feature/mercury-build-forward` as the active modernization branch.
2. Keep the existing working Platinum species architecture on this branch.
3. Do not switch back to the older HGSS-transplant architecture.
4. Do not introduce another competing species-ID system unless the current one hits a proven runtime blocker.
5. Never commit commercial ROM binaries.
6. Every milestone ROM must have:
   - Mercury source commit SHA,
   - pinned upstream SHAs,
   - feature manifest,
   - ROM SHA-256,
   - build log/artifact.

### Definition of done

The current clean build can always be reproduced from source, and the clean retail ROM remains only a reference/patch base.

---

## Phase MP1 — Complete the modern Pokémon data layer

This phase should be done in **large automated batches**, not Pokémon-by-Pokémon.

### MP1A — Learnsets

**Current work: PT05A**

- import compatible level-up moves for #494-1025,
- import compatible egg moves,
- respect Platinum's 20-entry native level-up table limit,
- log unsupported modern moves,
- leave TM/tutor translation to dedicated passes,
- compile a normal ROM.

**Gate:** all #494-1025 species have usable non-placeholder learnsets wherever donor data exists.

### MP1B — Evolutions

**Current work: PT05B**

- import evolution lines for #494-1025,
- translate evolution methods Platinum already supports,
- temporarily map unsupported special/trade methods to documented playable fallbacks,
- never leave a normal evolution family permanently dead-ended,
- log every fallback for later Mercury-specific cleanup.

**Gate:** the expanded roster can evolve through its normal families in a playable build.

### MP1C — Canonical move engine through Gen 9

Use the pinned HG-Engine implementation as the donor instead of recreating moves manually.

Work in generation batches:

1. Gen 5 moves,
2. Gen 6,
3. Gen 7,
4. Gen 8 / Legends: Arceus,
5. Gen 9.

For each batch:

- expand move constants/tables,
- port move metadata,
- port battle effects/handlers,
- port required status/field hooks,
- compile,
- run focused battle tests.

Do **not** block on mechanics that are unusable without a disabled gimmick. Examples:

- Max/G-Max moves can exist in data while Dynamax itself remains disabled.
- Tera-specific behavior can remain deferred until/if Terastallization is added.

**Gate:** normal canonical moves needed by the #1-1025 roster execute correctly; unsupported gimmick-only behavior is explicitly documented.

### MP1D — Canonical abilities through Gen 9

Again, bulk-port from pinned HG-Engine.

Order:

1. constants and metadata,
2. simple stat/trigger abilities,
3. switch-in/switch-out abilities,
4. contact/damage hooks,
5. weather/terrain abilities,
6. transformation/form-dependent abilities,
7. complex edge cases.

Use the donor's battle tests wherever practical.

**Gate:** normal canonical abilities used by the base #1-1025 roster work in battle. Complex gimmick-only abilities may be disabled/documented rather than blocking the entire baseline.

### MP1E — TM/HM and tutor compatibility

Do not stuff modern move names directly into Platinum's old tutor table.

Instead:

- build a move -> machine/tutor translation layer,
- modernize reusable TM policy if desired,
- preserve a valid learnable moveset for every imported species,
- ensure starter/common-story Pokémon remain fully functional.

**Gate:** expanded species are not trapped with only level-up moves.

### MP1F — Required items and evolution support

Import only the modern items necessary to make the modern baseline functional:

- evolution items,
- battle items needed by canonical abilities/moves,
- held items needed by important mechanics.

A giant item-shop redesign is **not** part of this phase.

**Gate:** required modern Pokémon mechanics no longer reference missing item IDs.

### MP1G — Base roster graphics/text integrity

Verify in bulk:

- front/back sprites,
- icons,
- palettes,
- names,
- Pokédex identity,
- types,
- base stats,
- cries where supported,
- Party/PC/Summary rendering.

**Gate:** #1-1025 base species can be instantiated, displayed, battled, saved, and reloaded without corrupting the game.

---

# PART II — BUILD THE GOLDEN MODERN PLATINUM

## Phase MP2 — Normal complete-game build

Build a game that is deliberately boring from a Mercury-content perspective:

> **Pokémon Platinum's complete adventure running on the modernized Mercury engine.**

For this build:

- keep vanilla Sinnoh encounters,
- keep vanilla trainers,
- keep vanilla gyms,
- keep vanilla Galactic story,
- keep vanilla field traversal,
- keep vanilla shops,
- keep vanilla Cynthia,
- keep Platinum progression intact.

Newer Pokémon do **not** need to be distributed throughout Sinnoh yet. They only need to exist correctly in the engine.

### Candidate name

`Pokemon_Mercury_Modern_Platinum_1.0.nds`

---

## Phase MP3 — Fast certification, not tile-by-tile testing

This replaces the slow workflow that was consuming development time.

### Layer A — Static/source integrity

Automatically audit:

- mandatory scripts exist,
- mandatory warps exist,
- badge flags/vars still exist,
- Galactic progression resources still exist,
- Distortion World resources still exist,
- Victory Road/League resources still exist,
- credits/postgame scripts still exist.

### Layer B — Targeted runtime gates

Use development-only QA states/warps to test the meaningful boundaries directly.

Minimum gates:

- title -> New Game,
- Rowan/Twinleaf,
- starter + first battle,
- Pokédex/catching,
- Jubilife,
- Oreburgh + Roark,
- Eterna + Gardenia,
- Hearthome + Fantina,
- Veilstone + Maylene,
- Pastoria + Wake,
- Canalave + Byron,
- Snowpoint + Candice,
- Galactic HQ,
- Spear Pillar,
- Distortion World,
- Sunyshore + Volkner,
- Victory Road,
- Elite Four,
- Cynthia,
- credits,
- post-credit save/reload.

### Layer C — Modern engine canaries

Test representative Pokémon from every added generation.

Each canary should cover:

- spawn/give Pokémon,
- Party screen,
- Summary,
- learn a modern move,
- use a modern ability,
- battle,
- evolution where applicable,
- PC deposit/withdraw,
- save/reset/reload.

### Layer D — One real continuous playthrough

Only after Layers A-C pass, perform **one actual New Game -> Cynthia -> credits run**.

Do not repeatedly walk the entire game during ordinary development.

### Seal

Create an immutable branch such as:

`checkpoint/modern-platinum-golden-YYYY-MM-DD`

That branch becomes the permanent rescue point for Mercury development.

---

# PART III — TURN MODERN PLATINUM INTO MERCURY REDUX

Every feature below begins from a game that was already complete.

Only one major system should be changed at a time.

## MR1 — Encounter overhaul

This is the safest first real Mercury content change.

- redesign route encounter tables,
- add national variety,
- make Gible/Riolu available earlier,
- place desired regional/forms where appropriate,
- preserve story progression.

**Test:** encounter-table audit + several targeted route captures + short progression smoke.

**Seal:** checkpoint.

---

## MR2 — Evolution/QoL policy

- trade evolutions -> item/level alternatives,
- lower unreasonable evolution levels where appropriate,
- modern evolution conveniences,
- held-item/evolution availability cleanup.

**Test:** evolution matrix, not a whole-game replay.

**Seal:** checkpoint.

---

## MR3 — HM-free field traversal

Implement the already-approved philosophy:

- badge/story permission,
- compatible party Pokémon,
- no move-slot requirement,
- remove/replace obsolete HM-gift logic where necessary.

Do not redesign maps unless required.

**Test:** Cut / Rock Smash / Surf / Strength / Rock Climb / Waterfall progression gates individually, then one progression smoke run.

**Seal:** checkpoint.

---

## MR4 — Randomizer framework

Only now add the larger randomizer system.

Required independent toggles:

- stats,
- abilities,
- movesets,
- types,
- wild Pokémon,
- trainers,
- gifts/statics.

Preserve separate **Scaled/Progression** and **Chaos/Fully Random** modes.

Randomization must be deterministic from a saved seed where practical.

**Test:** seed reproducibility + each toggle independently + save/reload.

**Seal:** checkpoint.

---

## MR5 — Shops, items, trades, and economy

- Department Store expansion,
- city specialty inventories,
- modern evolution/battle items,
- in-game trades,
- held-item refresh behavior,
- Arcade/Capsule systems where desired.

**Seal after economy regression tests.**

---

## MR6 — Trainer and boss modernization

Now modify the challenge curve.

Order:

1. ordinary trainers,
2. rivals,
3. Gyms,
4. Galactic commanders/bosses,
5. Elite Four,
6. Cynthia.

Introduce custom Megas only after the base battle engine is stable.

Cynthia remains the hardest mandatory single trainer.

**Seal after each major boss tier rather than after every trainer.**

---

## MR7 — Mega / Delta / custom Pokémon layer

- canonical/ZA Megas selected for Mercury,
- project-original Megas,
- Delta Pokémon,
- split evolutions such as Regalibur/Arbalistia,
- custom abilities,
- innate ability framework.

Keep this separate from the canonical Gen 9 modernization layer so custom mechanics cannot destabilize the golden baseline.

---

## MR8 — UI and customization

Only after gameplay systems are stable:

- Abilitydex,
- Movedex,
- Redux-inspired information screens,
- avatar skin/clothing,
- salons,
- Keystone styles,
- Ball appearance editor.

Stock Platinum UI remains a fallback until each replacement is certified.

---

## MR9 — Side quests and story enrichment

Last major content layer:

- side quests,
- Hisuian/Delta lore,
- city-specific Trade Halls,
- optional story scenes,
- Youngster Martin arc,
- custom flavor/NPC content.

The core Platinum progression should remain recoverable even if optional content fails.

---

# PART IV — FINAL MERCURY CERTIFICATION

## F1 — Automated integrity suite

- clean compile,
- repository guard,
- species/move/ability/item table audits,
- encounter validation,
- trainer validation,
- script/warp validation,
- randomizer seed tests,
- save compatibility tests.

## F2 — Runtime smoke matrix

Check at least:

- Delta DS core,
- melonDS,
- DeSmuME or equivalent desktop reference emulator.

## F3 — Full normal playthrough

New Game -> Cynthia -> credits with standard Mercury settings.

## F4 — Full randomizer playthrough

At least one Scaled/Progression seed through credits.

## F5 — Recovery/regression

- save/reload throughout progression,
- PC storage,
- evolution,
- Mega mechanics,
- HM-free gates,
- optional quests,
- loss/retry paths,
- postgame return.

## F6 — Release seal

Create:

- immutable source checkpoint,
- ROM/build SHA manifest,
- patch against the clean reference ROM,
- release notes,
- known-issues list.

Do not distribute the clean retail ROM.

---

# Development rules that keep this fast

## Build first; test the important boundaries

Normal loop:

`implement batch -> compile -> targeted smoke -> checkpoint -> next batch`

Not:

`walk a few tiles -> screenshot -> walk a few tiles -> screenshot`

## Parallelize independent engineering

Good parallel candidates:

- move-data audit,
- ability compatibility audit,
- evolution mapping,
- graphics/text validation,
- static story-resource audit.

Do not parallel-edit the same source files/branch paths.

## Stop scope creep

Before the Golden Modern Platinum checkpoint, **do not start**:

- custom encounters,
- HM-free traversal,
- randomizer,
- boss redesign,
- custom Megas,
- Delta story,
- side quests,
- clothing/customization,
- major UI replacement.

Existing approved assets/code are preserved, not discarded; they simply wait until the baseline is sealed.

## Checkpoints only when they matter

Create checkpoints at:

1. modern data layer complete,
2. modern engine complete,
3. Golden Modern Platinum complete,
4. each major Mercury system,
5. release candidate.

Do not create a permanent branch for every tiny navigation event.

---

# Immediate execution queue

This is the exact order to follow from the current build-forward branch:

1. **PT05A** — finish #494-1025 compatible learnsets and compile.
2. **PT05B** — finish #494-1025 evolution import and compile.
3. **PT05C** — port canonical Gen 5-9 move engine/data in bulk.
4. **PT05D** — port canonical Gen 5-9 ability engine/data in bulk.
5. **PT05E** — machine/tutor compatibility + required modern items.
6. **PT05F** — #1-1025 graphics/text/Party/PC/save integrity sweep.
7. **MP2** — build the normal complete Modern Platinum candidate.
8. **MP3A-C** — static progression audit + targeted story gates + modern canaries.
9. **MP3D** — one continuous New Game -> Cynthia -> credits certification.
10. **GOLDEN SEAL** — freeze Modern Platinum 1.0.
11. Begin Mercury changes in order: encounters -> evolution QoL -> HM-free -> randomizer -> economy -> bosses -> Megas/Deltas -> UI/customization -> quests/story.

---

# Definition of success

The modernization phase is finished when we can say:

> We have a reproducible Pokémon Platinum game that starts normally, reaches Cynthia and credits normally, saves normally, and runs a modern #1-1025 Pokémon engine with the required canonical moves, abilities, evolutions, graphics, and data.

Only then does the project become a controlled series of Mercury Redux modifications.

That finished modern Platinum checkpoint is the project's permanent safety net.
