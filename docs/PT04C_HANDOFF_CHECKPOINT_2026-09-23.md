# PT04C Mercury DS Runtime Handoff Checkpoint — 2026-09-23

## Branch

`feature/pt04c-victini-runtime`

## Last fully sealed runtime checkpoints

### 1. Native Party / Pokédex
- Passing run: **#8**
- Run ID: `35876365117`
- Passing commit: `d4ae44a7c38f76a02707f92018dcca5edaa1000f`
- Sealed checkpoint commit: `755ef386aa163c319c58ffdef2ce935153dbfb72`
- Verified:
  - Victini is species / National Dex ID 494.
  - Victini is created through native `Pokemon_GiveMonFromScript`.
  - Native party contains Victini.
  - Pokédex seen/caught flags are set.
  - Native party UI renders Victini correctly at Lv. 50.

### 2. Native Summary
- Passing run: **#12**
- Run ID: `35879611845`
- Passing commit: `2c004030c18650a2445a76b66074bcd8617e114f`
- Sealed checkpoint commit: `a39fc294f848e6fff0c9b85880f48ca635c625e6`
- Verified:
  - Victini front sprite renders.
  - VICTINI name and Lv. 50 render.
  - PSYCHIC / FIRE typing renders.
  - Trainer Memo page renders.
  - Pokémon Skills page renders.
  - Battle Moves page renders.
  - Temporary PT04C move set: Endure / Headbutt / Zen Headbutt / Reversal.
  - Temporary PT04C ability: Synchronize.
  - Native Summary navigation was verified page-by-page.

### 3. Native PC Storage
- Passing run: **#13**
- Run ID: `35880712862`
- Passing commit: `204481f534355dad96acf6ec99eab2973b6e6161`
- Sealed checkpoint commit: `11c8bdf67481e7768f16748316fbd7063821a2af`
- Verified:
  - Victini stores through native `PCBoxes_TryStoreBoxMonAt`.
  - Boxed species value remains `SPECIES_VICTINI`.
  - Native PC storage UI launches.
  - Box 1 / Slot 1 visibly shows Victini.
  - Full Victini PC preview sprite renders.
  - VICTINI / Lv. 50 / PSYCHIC / FIRE render correctly in PC.

## Current unfinished gate

### Native Battle Entry
Goal: prove the already-verified player-side Victini (#494) can be loaded into Platinum's real battle engine.

Current harness design:
- Player party retains Victini in slot 0.
- Runtime asserts `Party_HasSpecies(..., SPECIES_VICTINI)`.
- Opponent is native **Bidoof Lv. 5** to isolate player-side species-494 behavior.
- Native entrypoint: `Encounter_NewVsSpeciesAtLevel`.
- CI-only harness; approved normal game flow remains untouched.

### Attempts
- Run #14 / `35881442253`: failed **before build** because the battle installer used a nonexistent include anchor. No sealed work was affected.
- Fix commit: `d982ff0be41b67b2554cff98a9e355799c856007`.
- Current retry: **Run #15**
- Run ID: `35881692234`
- Current state at checkpoint: in progress; dependencies completed and pinned pokeplatinum checkout had begun.
- Do not treat battle entry as passed until Run #15 (or its corrected successor) completes compile + archive checks + DeSmuME and the battle screenshots are visually reviewed.

## Next action on resume

1. Read Run #15 status.
2. If it failed, inspect only the failed step/log and patch that issue.
3. If it passed, download `pt04c-victini-native-battle-entry-proof`.
4. Visually verify player Victini in the native battle UI.
5. Seal a battle-entry checkpoint.
6. Only then begin the isolated save/reload gate.

## Locked project constraints retained

- No rollback of approved DS/Platinum design work.
- PT04C test harness remains CI-only.
- Normal Mercury DS game flow remains untouched by runtime harness patches.
- Do not start wider Gen V registration yet.
- Do not start save/reload until battle entry is separately verified and sealed.
