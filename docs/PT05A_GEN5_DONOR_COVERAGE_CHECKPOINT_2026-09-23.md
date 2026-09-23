# PT05A Gen V Donor Coverage Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

PT05A confirms that the pinned HG-Engine donor has sufficient source coverage to begin a bulk Generation V import for National Dex **#494-649** rather than adding Pokémon one at a time.

## Passing workflow

- Workflow: `PT05A Gen V Donor Coverage`
- Run: **#1**
- Run ID: `35891385134`
- Passing commit: `ec07950cb3a7eb302ae099fbf55ce515e5f99760`

Artifact:

- Name: `pt05a-gen5-donor-coverage`
- Artifact ID: `10764791811`
- SHA-256: `7948417e1b88ad15bf278da832cb7e889c0b48695f07f22571225111f294a639`

## Gen V range

- First: **#494 Victini**
- Last: **#649 Genesect**
- Total: **156 species**

## Graphics coverage

- Usable battle front/back sprite + icon: **156 / 156**
- Missing species: **0**
- Female-only fallback cases: **2**
  - #629 Vullaby
  - #630 Mandibuzz

The importer must select the complete female donor for those two species rather than assuming every species has a non-empty male sprite directory.

## Supporting donor-table coverage

Every Gen V species token was found in all of these pinned HG-Engine tables:

- `data/HeightTable.c` — 156 / 156
- `data/HiddenAbilityTable.c` — 156 / 156
- `data/IconPaletteTable.c` — 156 / 156
- `data/BaseExperienceTable.c` — 156 / 156
- `data/BabyMons.c` — 156 / 156
- `data/PokedexSort.c` — 156 / 156
- `data/SpeciesToOWFormFemale.c` — 156 / 156
- `data/FollowerProperties.c` — 156 / 156

Large donor sources are also present:

- `data/Species.c` — 2,894,109 bytes
- `data/learnsets/learnsets.json` — 3,460,704 bytes
- `data/SpriteOffsets.c` — 3,493,901 bytes

## Conclusion

The donor is not the bottleneck for the Gen V base-species batch.

The next gate is **PT05B — Gen V compatibility mapping + bulk importer**, where modern move/ability/data identifiers are compared against the Platinum engine and unsupported mechanics are explicitly mapped or deferred before generating 156 native species directories.

Do not return to one-Pokémon lifecycle testing. PT04C already proved the engine boundary and persistence path.
