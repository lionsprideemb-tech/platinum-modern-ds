# MP05 Canonical Ability Architecture — PASS

Date: 2026-09-25

## Result

MP05 now has a canonical Gen 1-9 ability namespace and the DS-side width needed
to represent it without growing the encrypted BoxPokemon save block.

This pass intentionally separates **ability identity/storage** from **ability
battle behavior**. Modern abilities whose mechanics have not yet been ported
are kept out of live species data rather than being silently approximated.

## Canonical namespace

- Ability IDs: **0..310**
- Canonical ability count: **311**
- Native Platinum implemented abilities: **0..123**
- Modern namespace additions: **187**
- Canonical tail: **ABILITY_POISON_PUPPETEER (310)**
- HG-Engine project-specific IDs 311..319 are excluded from the canonical set.

## Storage architecture

- Species personal-data ability slots widened to `u16`.
- Battle runtime ability holder widened to `u16`.
- Summary/runtime transport paths needed by the current game widened.
- BoxPokemon save block size remains unchanged.
- Ability low 8 bits remain in the native ability byte.
- Ability bit 8 uses an otherwise-unused high bit in the markings byte.
- All six normal player-facing marking bits remain available.
- Current canonical storage capacity: **0..511**.

The battle-recording transfer structure also preserves the added high ability
bit without increasing its size.

## Exactness policy

This architecture does **not** mark an ability implemented merely because its
ID and UI text exist.

The species importer is now given an explicit implemented-ability registry.
Until a modern ability's real mechanics are ported, that ability remains a
reported fallback instead of becoming an inert or approximate live ability.

## Build proof

Workflow: **MP05 Fast Ability Architecture**  
Run ID: `36157628893`  
Conclusion: **success**

Artifact: `mercury-modern-platinum-mp05-ability-architecture`  
Artifact ID: `10874256693`  
Artifact digest:
`sha256:e7f95fd863c94048abc571942fa05de38c37650081ce01b8da433aa49d65ed8c`

The workflow rebuilt the full 1025-species layer, restored the MP04 modern
move/learnset/evolution foundation, installed the ability architecture, and
compiled the complete native DS ROM.

A long runtime playthrough was intentionally skipped by project decision.

## Superseded experiments

Earlier compact-u8 ability experiments on this feature branch are historical
prototypes only. They are superseded by the canonical-ID architecture above and
must not be used as the production ability namespace.

## Next gate

Port modern ability behavior in shared families, then expand the
implemented-ability registry in bulk. Do not assign a modern ability before its
actual behavior is present.

**MP05 CANONICAL ABILITY ARCHITECTURE: PASS**
