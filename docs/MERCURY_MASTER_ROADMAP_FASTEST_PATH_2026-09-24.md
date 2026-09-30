# Mercury DS — Master Roadmap: Fastest Path to a Finished Game

**Status:** AUTHORITATIVE PROJECT ROADMAP  
**Date:** 2026-09-24  
**Primary development branch:** `feature/mercury-build-forward`  
**Project goal:** Build a complete, modernized Pokémon Platinum first; freeze it as a golden baseline; then transform it into Pokémon Mercury Redux through small, isolated, reversible feature passes.

---

## 1. Core strategy

The fastest safe route is **not** to build Mercury Redux all at once.

The project will proceed in three layers:

1. **Finished Platinum foundation**
   - Preserve Platinum's complete world, story, maps, progression, trainers, credits, and save flow.
   - Use native Platinum as the runtime/world foundation.

2. **Modern Platinum**
   - Modernize the engine and Pokémon data while keeping the adventure intact.
   - Target: a complete New Game -> Cynthia -> credits game with the modern roster/mechanics foundation.

3. **Mercury Redux**
   - Starting from the frozen Modern Platinum baseline, add one Mercury feature at a time:
     randomizer, encounters, HM-free traversal, shops, trainer redesigns, Megas, Deltas, quests, customization, etc.

The rule is simple:

> **Never make two unrelated large systems mandatory for the same checkpoint.**

Every major feature must be independently reversible.

---

## 2. Source/ROM architecture

### Authoritative source

The GitHub repository and source/decomp build remain the **master copy** of the game.

All permanent Mercury changes must be reproducible from source.

### Clean Platinum ROM

The user's clean USA Platinum ROM is a **private build/reference input**, not source control content.

Use it for:
- binary comparison,
- fast packaging/injection experiments where useful,
- verification against untouched Platinum,
- final patch generation.

Do **not** commit or upload the commercial ROM to the public repository.

### Development packaging

Prefer the fastest reproducible route:

- source compile for changed ARM code/overlays,
- rebuild changed data/NARCs/assets,
- reuse untouched Platinum content,
- produce a complete test ROM artifact,
- later distribute Mercury as a patch requiring the user's clean Platinum ROM.

Full clean rebuilds remain the certification path when required.

---

## 3. Existing foundation — already proven

These are not restart targets.

- Native Platinum runtime/world foundation established.
- Reproducible Platinum source build established.
- Mercury title work exists.
- Fairy/type foundation exists.
- Canonical roster architecture through National Dex #1025 exists.
- Post-Gen-IV species boundary was proven through native Party, Summary, PC, battle, and save/reload paths.
- Bulk donor resources for Generations V-IX have already been audited.
- Full 1025-species resource generation exists.
- A normal playable Platinum-derived ROM candidate has already booted and progressed through the early game.
- Current production work moved to `feature/mercury-build-forward`.

Do not repeat one-Pokémon lifecycle testing unless a new engine change specifically invalidates that proof.

---

# STAGE I — MODERN PLATINUM

Goal: produce **Mercury Modern Platinum 1.0**, a complete Platinum adventure with the modern engine/data foundation.

---

## MP01 — Full canonical species layer

**Status:** architecture/resource layer substantially complete.

### Required
- National Dex #1-1025.
- Stable internal species IDs.
- Sprite/icon/base-data resources.
- Fairy typing support.
- Save/party/PC/battle compatibility for expanded IDs.

### Done when
- All 1025 canonical base species can exist as valid game objects.
- Normal ROM compiles.
- Representative Gen V-IX species survive save/reload and battle.

### Testing
Only targeted representative checks. No full playthrough yet.

---

## MP02 — Learnsets

**Current active work: PT05A.**

### Required
- Replace post-Gen-IV placeholder learnsets.
- Import compatible level-up moves in bulk.
- Preserve meaningful progression within Platinum's 20-entry level-up table.
- Import compatible egg moves.
- Track unsupported modern moves rather than silently replacing them.

### Deferred subpasses
- TM/HM compatibility mapping.
- Platinum tutor-table mapping.
- Evolution-only move behavior where native Platinum differs.

### Done when
- #494-1025 have usable non-placeholder level-up learnsets where donor data exists.
- Data processor accepts every species.
- Normal ROM compiles.

---

## MP03 — Evolution layer

**Current active work: PT05B.**

### Required
- Import all post-Gen-IV evolution links in bulk.
- Translate evolution methods Platinum already supports.
- Use documented temporary playable fallbacks for unsupported modern/trade methods.
- Preserve a machine-readable fallback report.

### Mercury policy later
Trade evolutions and awkward modern methods will be deliberately modernized for single-player accessibility.

### Done when
- Evolution families no longer dead-end because they were added after Gen IV.
- Every fallback is documented.
- Normal ROM compiles.

---

## MP04 — Canonical moves through Gen 9

### Donor state
The pinned HG-Engine donor already contains the canonical move registry through Gen 9, including the modern Gen VIII/IX set.

### Required
- Expand Platinum move IDs/tables safely.
- Port move metadata.
- Port battle effects/mechanics.
- Port move animations where available.
- Map missing/unsupported animations to safe temporary effects only when necessary and document them.
- Preserve Gen IV moves and scripts.

### Order
1. Move constants/table capacity.
2. Damage/category/type/accuracy/PP metadata.
3. Common reusable effects.
4. Signature/special effects.
5. Animations.
6. Regression compile.

### Done when
- All canonical Gen 9 move IDs needed by the 1025 roster exist.
- Pokémon learnsets no longer need to discard moves purely because the move ID is absent.
- Representative special-effect moves work in battle.
- Normal ROM compiles.

---

## MP05 — Canonical abilities through Gen 9

### Donor state
The pinned HG-Engine donor already contains the canonical ability registry through Gen 9.

### Required
- Expand ability IDs/tables.
- Port passive battle hooks in groups.
- Preserve vanilla Gen IV behavior.
- Import primary/secondary/hidden ability data for #494-1025.
- Keep known upstream edge cases documented instead of blocking the whole project.

### Grouping for speed
- Stat-entry abilities.
- Immunity/absorb abilities.
- Contact/reaction abilities.
- Weather/terrain abilities.
- Move-modifier abilities.
- Switching/form/special-state abilities.
- Legendary/signature mechanics.

### Done when
- Modern species no longer require widespread fallback abilities.
- Representative abilities from each generation execute correctly.
- Normal ROM compiles.

---

## MP06 — Modern species data cleanup

### Required
- Base EXP handling.
- Held-item mapping.
- gender/egg-group/growth-rate cleanup.
- TM compatibility.
- tutor compatibility.
- breeding data.
- forms required for normal species functionality.
- dex metadata needed by menus.

### Done when
- Expanded species feel like real integrated Pokémon, not compatibility shells.

---

## MP07 — Modern battle/QoL baseline

Only changes that improve the finished Platinum game without redesigning Mercury yet.

### Candidate baseline features
- Fairy chart fully certified.
- Modern move/ability interactions required by imported roster.
- Reusable TM policy if chosen.
- Evolution modernization for inaccessible methods.
- Modern repel/field conveniences where low risk.
- Faster text/battle options if low risk.
- sensible EXP/evolution compatibility.

### Explicitly not yet
- Randomizer.
- custom bosses.
- custom Megas.
- Delta Pokémon.
- story rewrites.
- custom encounter overhaul.
- HM-free replacement system.
- side quests/customization.

### Done when
Modern mechanics do not block normal Platinum progression.

---

## MP08 — Modern Platinum integration build

Produce a named candidate:

**Mercury Modern Platinum 1.0 RC**

### Must contain
- Complete native Platinum world/story.
- 1025-species-capable engine.
- Gen 9 move foundation.
- Gen 9 ability foundation.
- modern evolution compatibility.
- Fairy.
- stable save/load.
- stock Platinum progression intact.

### Build rule
At this point, stop adding features and certify the game.

---

## MP09 — Fast certification

Do not return to tile-by-tile testing.

### Certification method

**Static/source checks**
- mandatory maps/scripts/trainers exist,
- required flags/vars are intact,
- all eight badge paths exist,
- Galactic/Spear Pillar/Distortion World chain exists,
- League/credits path exists.

**Targeted runtime gates**
Jump or prepare controlled states immediately before major gates and test the actual event:
- starter/Pokédex,
- Roark,
- Gardenia,
- Fantina,
- Maylene,
- Wake,
- Byron,
- Candice,
- Volkner,
- Galactic HQ,
- Spear Pillar,
- Distortion World,
- Victory Road,
- Elite Four,
- Cynthia,
- credits,
- save/reload.

**One final continuous playthrough**
Only after all major gates pass independently.

### Done when
One normal New Game -> credits run has no progression-blocking crash, bad warp, softlock, battle failure, or save corruption.

---

## MP10 — Golden baseline freeze

Create immutable checkpoint:

`checkpoint/modern-platinum-1.0-golden`

Preserve:
- exact commit SHA,
- build workflow/run,
- ROM hash,
- donor revisions,
- compiler/build manifest,
- known non-blocking issues,
- patch-generation instructions.

This becomes the permanent parent for Mercury Redux development.

---

# STAGE II — MERCURY CORE FEATURES

Every feature begins from the golden baseline or a certified descendant.

---

## MR01 — Encounter overhaul

First Mercury content change because it is highly isolated.

### Required
- regional/national availability plan,
- early Gible/Riolu priority,
- route-by-route encounter tables,
- rare encounters,
- gifts/statics separated from wild tables.

### Rule
No randomizer yet. Establish the authored encounter game first.

### Certification
- table validation,
- sample encounters,
- no invalid species/forms,
- progression access sanity check.

---

## MR02 — HM-free traversal

### Required
- badges/story gates remain meaningful,
- compatible party Pokémon can perform field actions without occupying move slots,
- Cut/Surf/Rock Smash/Strength/Defog/Rock Climb/Waterfall policies,
- replace obsolete HM-giver rewards where planned.

### Certification
Test every mandatory field gate once.

---

## MR03 — Randomizer foundation

Build after authored encounters and traversal rules are stable.

### Required toggles
- stats,
- abilities,
- movesets,
- types,
- wild encounters,
- trainers,
- gifts,
- statics,
- independent controls rather than one master randomizer.

### Required modes
- Scaled/Progression.
- Chaos/Fully Random.

### Hard rule
Randomization must not mutate canonical source data permanently. It is runtime/seed configuration.

---

## MR04 — Evolution/item/shop modernization

### Required
- single-player evolution alternatives,
- Department Store battle/evolution item access,
- held-item policies,
- convenience inventory changes,
- later automatic held-item refresh system.

---

## MR05 — Trainer/boss rebalance

Proceed regionally.

### Order
1. Roark/Gardenia.
2. Fantina onward major-boss framework.
3. rivals/Galactic.
4. Gym 4-8.
5. Elite Four.
6. Cynthia.
7. Youngster Martin arc/rematches.

### Rule
Cynthia remains the hardest mandatory single trainer.

---

# STAGE III — MERCURY IDENTITY FEATURES

These come only after the game remains complete with MR01-MR05.

---

## MI01 — Mega Evolution expansion

- existing compatible Megas,
- ZA Megas,
- Mercury originals,
- boss Mega assignments,
- custom abilities/stat blocks,
- Mega UI/runtime certification.

Build species/mechanics first, art second where necessary.

---

## MI02 — Delta/Hisuian/custom species content

- Delta variants and lore,
- Valley Windworks Delta Drifloon/Drifblim first event,
- Hisuian threads,
- Regalibur/Arbalistia split evolution work,
- custom forms and sprites.

---

## MI03 — Redux-style ability/innate framework

### Required
- primary + innate architecture,
- Global Innate Abilities toggle,
- OFF means primary ability only in battle/UI/boss logic,
- Abilitydex.

This is intentionally late because it touches nearly every battle calculation.

---

## MI04 — UI modernization

- richer battle UI,
- Abilitydex,
- Movedex,
- selected Elite Redux-style information surfaces,
- preserve stock fallback screens until replacements are certified.

---

## MI05 — Player customization

- skin tone,
- clothing,
- hair salons,
- overworld-visible appearance,
- Eterna early shop,
- Veilstone Keystone styles.

---

## MI06 — Side quests/trades/optional systems

- side quests,
- city-specific Trade Halls,
- local trades,
- Surprise Trade,
- Arcade/Capsule Coupon system,
- Ball appearance editor,
- optional rewards/resources.

---

## MI07 — Map/story expansion

Only now make large world edits.

- expanded Eterna Forest,
- custom event staging,
- additional NPCs,
- Galactic tone changes,
- Delta story beats,
- city/route polish.

### Map rule
Preview/certify each edited map and do not silently leave Hoenn/GBA placeholders.

---

# STAGE IV — FINAL MERCURY CERTIFICATION

---

## FC01 — Content audit

Check:
- every mandatory story flag,
- every Gym,
- every rival,
- every Galactic boss,
- Victory Road,
- Elite Four/Cynthia,
- custom Mega references,
- encounter validity,
- evolution reachability,
- shops/items,
- randomizer exclusions,
- side-quest isolation.

---

## FC02 — Emulator matrix

Test on:
- Delta iOS,
- Pizza Boy is no longer relevant to DS builds; replace with supported DS emulator targets,
- melonDS/DeSmuME development environment,
- at least one additional real-user DS emulator target.

Record emulator-specific issues separately from game-code failures.

---

## FC03 — Fresh-save end-to-end run

Fresh New Game only.

Test:
- intro,
- all eight badges,
- all mandatory Galactic content,
- Distortion World,
- Victory Road,
- League/Cynthia,
- credits,
- save/reload at representative points,
- randomizer OFF,
- randomizer ON with one fixed seed.

---

## FC04 — Release candidate

Freeze:
- source commit,
- build manifest,
- ROM hash for internal artifact,
- clean-ROM patch,
- changelog,
- known issues,
- credits/licenses for source/assets,
- restore branch.

---

# 4. Speed rules

These rules override the old slow-testing pattern.

### Build rules
- Batch data changes by system/generation, not Pokémon-by-Pokémon.
- Prefer donor imports and generators over hand-editing hundreds of files.
- Compile after meaningful batches, not after every tiny edit.
- Keep the clean Platinum world/story untouched until Modern Platinum is frozen.
- Never rebuild a solved architecture problem unless a new failure proves it necessary.

### Test rules
- Do not automate long walks to reach a test.
- Test major gates directly with controlled prerequisite state.
- Use screenshots only for visually meaningful checkpoints.
- Use static validation for data tables and story-resource presence.
- Run the expensive continuous playthrough only at certification points.

### Failure rules
- Fix the actual shared cause, not one affected Pokémon at a time.
- If a table limit fails, teach the importer the limit.
- If an identifier class is missing, expand/map the class in bulk.
- If one feature threatens the baseline, isolate it behind its own branch/checkpoint.

---

# 5. Branch/checkpoint policy

### Active production
`feature/mercury-build-forward`

### Golden milestones
Use immutable checkpoint branches for:
- Modern Platinum 1.0.
- Encounter overhaul.
- HM-free traversal.
- Randomizer.
- Core trainer/boss pass.
- Mega foundation.
- Final release candidate.

### Naming
`checkpoint/<milestone>-YYYY-MM-DD`

Never continue experimental development directly on a sealed checkpoint.

---

# 6. Immediate execution order

This is the order to follow from the current repository state:

1. Finish **PT05A learnsets** and obtain a compiling ROM.
2. Finish **PT05B evolutions** and obtain a compiling ROM.
3. Port/expand **Gen 5-9 moves** in bulk.
4. Port/expand **Gen 5-9 abilities** in bulk.
5. Replace temporary ability/move fallbacks in #494-1025.
6. Finish TM/tutor/evolution compatibility cleanup.
7. Build **Mercury Modern Platinum 1.0 RC**.
8. Run major-gate certification.
9. Run one fresh New Game -> Cynthia/credits playthrough.
10. Freeze **Modern Platinum 1.0 Golden**.
11. Start Mercury changes with **encounter overhaul**.
12. Add **HM-free traversal**.
13. Add **randomizer**.
14. Add shops/evolution/item QoL.
15. Rebalance trainers/bosses.
16. Add Megas/Deltas/custom systems.
17. Add UI/customization/quests/map expansions.
18. Final Mercury certification/release candidate.

---

# 7. Definition of success

The project is considered structurally safe when we can always answer:

> "What is the newest complete game we can return to?"

Until Modern Platinum 1.0 is frozen, the answer is the stock-story modernized candidate.

After it is frozen, every Mercury feature is optional relative to that baseline.

The final target is not merely a collection of implemented mechanics. It is:

> **A reproducible, complete, playable Pokémon Mercury Redux ROM derived from a known-good modernized Platinum baseline, with every major feature added in isolated, recoverable layers.**
