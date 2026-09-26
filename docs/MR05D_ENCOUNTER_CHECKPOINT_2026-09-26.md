# Mercury DS — MR05D Encounter Checkpoint

Date: 2026-09-26

## Certified workflow

- Workflow: `MR05B Authored Encounters`
- Run: `36274722458`
- Head commit: `ac6a56038e5af528a083dec519e5ecdb5f0d9c1d`
- Result: **PASS**
- Player artifact: `mercury-mr05d-victory-road`
- Artifact ID: `10917600084`
- Artifact digest: `sha256:227f23207bedca48f6c0693c9398c63bb7833a281a928cc8ea11e48fbae795f2`

## Encounter state now certified

- Routes 201–230: authored across 35 route segments.
- Honey Trees: Mercury premium pool; Burmy removed from the special pool.
- Great Marsh: all 6 biomes authored without daily-RNG availability gating.
- Ravaged Path: authored Surf and fishing.
- Old Chateau: all 9 encounter resources authored.
- Snowpoint Temple: all 6 floors authored.
- Iron Island: all 7 encounter resources translated from the sealed Mercury registry.
  - Riley's Riolu remains a special gift and is not a random encounter.
- Mt. Coronet: 12 additional encounter resources translated from sealed Mercury registries.
  - B1F Feebas is available through normal fishing.
  - Platinum's elusive-rod metadata is preserved for compatibility/reference.
- Victory Road: all 6 encounter resources authored.
  - Main 1F / 2F / B1F.
  - Marley branch Fog Gallery / Underground Lake / Exit Passage.
  - Marley / Route 224 branch opens pre-League without National Dex or Hall-of-Fame gating.
  - Route 224's already-authored route table is preserved.
- Full Mercury four-period runtime:
  - **77** authored Morning/Day/Evening/Night land areas.
  - **3,696** four-period encounter slots.

## Pre-League Regi loop certified

- Snowpoint Temple opens after the Icicle Badge.
- Dormant Regigigas is available pre-League.
- First Regigigas interaction activates the internal Titan Tablet story flag.
- Registeel: Iron Ruins, Iron Island, Lv55.
- Regice: Iceberg Ruins, Mt. Coronet, Lv55.
- Regirock: Rock Peak Ruins, reached from the Route 214 Ruin Maniac Tunnel, Lv55.
- The old external/fateful-event Regigigas, National Dex, and Hall-of-Fame gates are removed from this loop.
- Regirock / Regice / Registeel remain retryable after KO/flee by leaving and re-entering.
- Regigigas remains Lv1 and still requires Regirock + Regice + Registeel in the party.

## Runtime proof

The MR05D ROM compiled successfully and the real DeSmuME normal-boot capture gate passed. The staged player ROM is:

`Pokemon_Mercury_MR05D_Victory_Road.nds`

## Important implementation note

Lycanroc Midday / Midnight / Dusk encounter tokens from the authored Victory Road registry are normalized to the canonical `SPECIES_LYCANROC` entry in the current 1,025-species encounter namespace. Rockruff's evolution/form rules remain the route to the alternate forms; no unsupported form token is written into the encounter NARC.

## Next encounter batch

Continue from this checkpoint. Do not redo the areas above. The next high-value sealed source is `data/encounters/legacy_sources/sinnoh_special_legendary_areas.json`, beginning with Sendoff Spring and Turnback Cave random encounter resources. Static legendary/story access should stay separate from ordinary random encounter tables and preserve existing retry/story rules.
