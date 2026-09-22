# PT03 — Fairy / Modern Type Foundation Audit

**Prepared:** 2026-09-22  
**Status:** DRAFT AUDIT ONLY — no PT03 mechanics committed until PT02 visual proof is certified.

## Core finding

Native Platinum's type system is source-visible and expandable. The current generated type order is:

```
0  NORMAL
1  FIGHTING
2  FLYING
3  POISON
4  GROUND
5  ROCK
6  BUG
7  GHOST
8  STEEL
9  MYSTERY
10 FIRE
11 WATER
12 GRASS
13 ELECTRIC
14 PSYCHIC
15 ICE
16 DRAGON
17 DARK
18 NUM_POKEMON_TYPES
```

The safest compatibility strategy is to append **FAIRY after DARK**, making Fairy ID 18 and `NUM_POKEMON_TYPES` 19. This preserves every existing Platinum type ID, including the special Mystery type at ID 9.

## Battle-engine changes required

Primary battle effectiveness lives in `src/battle/battle_lib.c` in `sTypeMatchupMultipliers`.

PT03 should implement the modern chart, including Fairy:

- Fairy -> Fighting: 2x
- Fairy -> Dragon: 2x
- Fairy -> Dark: 2x
- Fairy -> Fire: 0.5x
- Fairy -> Poison: 0.5x
- Fairy -> Steel: 0.5x
- Fighting -> Fairy: 0.5x
- Bug -> Fairy: 0.5x
- Dark -> Fairy: 0.5x
- Dragon -> Fairy: 0x
- Poison -> Fairy: 2x
- Steel -> Fairy: 2x
- Fire -> Fairy: 1x
- Fairy -> Fairy: 1x

Modernization also requires the Gen VI Steel-chart correction:

- Ghost -> Steel becomes 1x instead of 0.5x
- Dark -> Steel becomes 1x instead of 0.5x

## Systems that depend on NUM_POKEMON_TYPES

Adding a type affects more than battle damage. The audit found explicit type-count or type-order dependencies in:

- `src/applications/poketch/move_tester/main.c`
  - fixed square matchup table
  - explicit display order
- `src/type_icon.c`
  - type icon character resource table
  - type icon palette table
- Battle Hall / Frontier code
  - type-selection UI
  - trainer-class mapping
  - in-memory packed rank arrays currently use 9 bytes for 18 nibbles
- Pokédex type indexing
  - generated species-by-type archives size from `NUM_POKEMON_TYPES - 1`
  - Mystery is intentionally omitted
- TV/random-type helpers
  - random type selection skips Mystery
- Easy Chat / word banks
  - type words are explicitly enumerated
- Pokétch Move Tester
  - currently enumerates the 17 normal battle types and omits Mystery
- Pokédex type animation/icon mappings
  - explicit switches currently have no Fairy case

## Hidden Power

Platinum's Hidden Power calculation intentionally maps to the classic 16 Hidden Power attack types and skips Mystery.

Appending Fairy at ID 18 means the current numeric calculation naturally continues to exclude Fairy, which matches later official games where Hidden Power never became Fairy-type.

Therefore PT03 should **not** add Fairy to Hidden Power.

## Mystery type

`TYPE_MYSTERY` is used internally by Platinum, including Curse and several skip/remap helpers. PT03 should preserve it exactly at ID 9 rather than repurposing it as Fairy.

This avoids destabilizing existing scripts and data.

## Battle Hall warning

The Battle Hall currently packs 18 type ranks as nibbles into 9 bytes. With Fairy added, a naïve loop to 19 types would overrun that storage.

PT03 must handle this deliberately before changing global type count. Options:

1. keep Battle Hall's selectable list at the original 17 battle types temporarily, or
2. expand its rank storage and audit save compatibility.

For the first mechanics proof, option 1 is safer. Fairy can work in ordinary battles before Battle Hall UI/save support is expanded.

## Visual resources

Fairy needs a native DS type icon resource and palette mapping before it can safely appear on every summary/move screen.

PT03 can be split into:

### PT03A — engine-safe type slot
- append TYPE_FAIRY after TYPE_DARK
- update battle type chart
- keep Battle Hall from indexing Fairy temporarily
- keep Hidden Power unchanged
- compile/runtime regression tests

### PT03B — visible Fairy support
- add FAIRY text/name
- add Fairy icon graphics
- add Move Tester entry
- add Pokédex/UI mappings
- assign one controlled test move or Pokémon to Fairy
- runtime screenshot/battle proof

### PT03C — modern chart certification
- automated matchup checks for all Fairy interactions
- verify Steel no longer resists Ghost/Dark
- dual-type multiplier checks
- immunity check for Dragon -> Fairy
- AI type-chart compatibility check

## PT03 acceptance rule

Do not move into Pokédex expansion until:

1. native Platinum still builds,
2. a Fairy-typed test case is visible in the actual game,
3. battle damage proves Fairy effectiveness/resistance/immunity behavior,
4. existing non-Fairy battles remain stable,
5. Battle Hall and Mystery-type code do not read past their original buffers.

This keeps the project on the same proof-first discipline established by PT01/PT02.
