# MP06C Modern Species Data — PASS

Date: 2026-09-25

## Result

MP06C is certified as the first post-RC1 Modern Platinum completion pass.

The full native Platinum ROM compiled successfully with the complete MP05
foundation plus three modern species-data upgrades:

- canonical HG-Engine cries for every base species #494-1025,
- full modern base EXP values stored as u16 instead of clamping values above 255,
- canonical breeding offspring/baby-species mappings for #494-1025.

No long emulator playthrough was run, per the current fast-build policy.

## Proof

Workflow: **MP06C Modern Species Breeding Integration**

Run ID: `36163579515`

Conclusion: **success**

Source commit:
`41b50e4b8f1a2cb635fe66dfeaaafb2e4b5c4be8`

Artifact:
`mercury-modern-platinum-mp06c-breeding`

Artifact ID:
`10875639778`

Artifact digest:
`sha256:58e3f08e5b5fc9db942a5e46a64a7f8170fd52c9ce3b72e106ad56d596b242c0`

Compiled ROM:
`Pokemon_Mercury_Modern_Platinum_MP06C.nds`

ROM SHA-256:
`77d078ca19411ef93967654ee11bc6e4a3dffc2e78ee7a807836ecd4e9236d55`

ROM size:
`134217728 bytes`

## Data proof

- Modern species updated: **532 / 532**
- Missing modern cries: **0**
- Species with canonical offspring mapping written: **532**
- Evolved species redirected from temporary self-offspring to the correct baby/base species: **234**
- Modern base EXP entries restored: **532**
- Base EXP values above 255 preserved instead of clamped: **121**
- Highest imported base EXP value: **390**

## Remaining Modern Platinum completion work

- modern ability mechanics and live ability assignments,
- machine/tutor compatibility for imported species,
- required modern held-item mechanics/items,
- remaining modern move-effect families,
- final integration/certification pass.

**MP06C: PASS**
