# Mercury Modern Platinum — Full Playable Baseline RC1

Date: 2026-09-25

## Result

**PASS — complete native Platinum game ROM compiled successfully.**

This checkpoint is the finished-game safety baseline requested before further
Mercury Redux content work. It preserves the complete native Pokémon Platinum
world/story/progression while carrying the modern engine/data architecture
completed through MP05.

Long emulator playthrough testing remains intentionally skipped for this fast
baseline. Certification here is source/static integrity plus a complete native
ROM compilation.

## Included

- Complete native Platinum world and story progression inherited from PB04
- Mercury title resources
- National Dex engine/resource capacity through canonical species #1025
- Modern compatible level-up learnsets for #494-1025
- Modern compatible evolution data for #494-1025
- 16-bit move-ID architecture
- Canonical Gen 5-9 move namespace through ID 919
- 452 post-Gen-IV canonical move definitions
- 308 modern moves currently eligible for natural learnsets via supported effects
- Canonical Gen 1-9 ability namespace through Poison Puppeteer, ID 310
- 10-bit per-Pokémon ability-ID storage capacity 0-1023
- No BoxPokemon save-block size increase
- All six visible Pokémon marking bits preserved
- Species, battle, Summary, wild-encounter, trainer-AI, daycare, and recording
  ability transport widened for the modern namespace

## Deliberately deferred, non-blocking for this baseline

- Modern ability battle hooks beyond native Platinum's implemented ability set
- 323 modern species ability-slot assignments are gated to ABILITY_NONE until
  their mechanics are ported rather than silently approximated
- 144 canonical modern moves remain namespace-valid but are kept out of natural
  learnsets until their effect/target support is implemented
- Final TM/tutor compatibility cleanup
- Modern cry replacement for imported species still using the safe placeholder
- Mercury-specific encounter overhaul, HM-free traversal, randomizer, bosses,
  Megas/Deltas, UI, customization, and side quests

These are follow-on layers on top of this complete-game checkpoint, not blockers
for having a complete Platinum adventure to build from.

## Build proof

Workflow: **MP05 Fast Ability Architecture**

Run ID: `36157672008`

Conclusion: **success**

Source commit tested:
`079b44b1550d6281029087568c583c8f2cd1ef5c`

Artifact:
`mercury-modern-platinum-mp05-ability-architecture`

Artifact ID:
`10873734872`

Artifact digest:
`sha256:f00c99b3474185524ce64d33ad1133bc22531bc797be9be14d9ada1085af419d`

Compiled ROM:
`Pokemon_Mercury_Modern_Platinum_MP05.nds`

ROM SHA-256:
`e8e4398a947b825733d2e802393c157764c86f9f80d29d4f29b0f7f0aa6fc815`

ROM size:
`134217728 bytes`

## Safety point

This branch is the permanent **full playable baseline RC1** safety point.
Further engine modernization and Mercury Redux systems should be layered on a
development descendant rather than rewriting this checkpoint.

**FULL PLAYABLE BASELINE RC1: PASS**
