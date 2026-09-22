# PT03A — Fairy Type Engine Implementation Plan

**Prepared:** 2026-09-22  
**Gate:** Do not apply mechanics changes until PT02 title-screen proof is visibly certified.

## Objective

Add Fairy as the 18th normal gameplay type while preserving Platinum's internal Mystery type and all existing numeric type IDs.

## Type IDs

Keep every existing ID unchanged and append:

```
TYPE_DARK     = 17
TYPE_FAIRY    = 18
NUM_POKEMON_TYPES = 19
```

`TYPE_MYSTERY` remains ID 9.

## First implementation surface

### 1. Type enum generation
Overlay:
- `generated/pokemon_types.txt`

Change:
- append `TYPE_FAIRY` immediately after `TYPE_DARK`
- keep `NUM_POKEMON_TYPES` last

### 2. Battle type chart
Overlay:
- `src/battle/battle_lib.c`

Add Fairy interactions:
- Fairy > Fighting, Dragon, Dark
- Fairy < Fire, Poison, Steel
- Fighting, Bug, Dark < Fairy
- Dragon -> Fairy = immune
- Poison, Steel > Fairy

Modern Steel correction:
- remove Steel resistance to Ghost
- remove Steel resistance to Dark

### 3. Keep Hidden Power legacy-compatible
Do not add Fairy to Hidden Power's 16-type output set.
Do not move or repurpose `TYPE_MYSTERY`.

### 4. Protect Battle Hall
Platinum's Battle Hall packs 18 ranks into 9 bytes. A global increase to 19 type IDs must not make its rank loops index a tenth byte.

PT03A must explicitly keep Battle Hall selection/rank loops on the original supported battle-type count until its storage and UI are deliberately expanded.

Create a dedicated constant for this temporary compatibility boundary rather than relying blindly on `NUM_POKEMON_TYPES`.

### 5. Defer visual/UI Fairy resources to PT03B
PT03A is the engine-safe slot and chart phase. Do not assign normal gameplay Pokémon/moves to Fairy until the UI resource tables are ready.

PT03B will add:
- Fairy display text
- Fairy type icon graphics/palette
- summary-screen mapping
- Pokédex mapping
- Pokétch Move Tester entry
- controlled Fairy test move/species

## PT03A automated checks

The CI test must prove at minimum:

- `TYPE_FAIRY == 18`
- existing IDs 0–17 are unchanged
- `TYPE_MYSTERY == 9`
- `NUM_POKEMON_TYPES == 19`
- Dragon -> Fairy = 0x
- Fairy -> Dragon = 2x
- Fairy -> Fighting = 2x
- Fairy -> Dark = 2x
- Fire -> Fairy = 1x
- Poison -> Fairy = 2x
- Steel -> Fairy = 2x
- Fairy -> Fire = 0.5x
- Fairy -> Poison = 0.5x
- Fairy -> Steel = 0.5x
- Ghost -> Steel = 1x
- Dark -> Steel = 1x

Also verify ordinary legacy matchups remain unchanged, including:
- Normal -> Ghost = 0x
- Electric -> Ground = 0x
- Ground -> Flying = 0x
- Ice -> Dragon = 2x
- Fighting -> Normal = 2x

## Acceptance gate

PT03A does not pass merely because it compiles.

It passes only when:
1. native Platinum builds,
2. type IDs are stable,
3. modern matchup tests pass,
4. Mystery behavior is preserved,
5. Battle Hall cannot index beyond its original packed rank storage,
6. a standard non-Fairy battle boots and runs.

PT03B then adds visible Fairy UI/resources and an in-game Fairy proof.
