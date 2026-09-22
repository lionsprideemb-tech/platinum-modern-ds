# DS03 World Compatibility Certification

**Status: CERTIFIED**

Certified GitHub Actions evidence:
- workflow: `DS03 Platinum World Compatibility`
- run: `35766528414`
- job: `106877351674`
- conclusion: **success**
- certified commit under test: `c81b9b4a06aa00eeb8d045a71a154e50d9c5f2d8`

## What DS03 proves

DS03 proves that the initial Platinum Twinleaf world slice can be translated into append-only HGSS/HG-Engine-compatible resources without redrawing its maps.

Validated:
- DPPt → HGSS land-data/BGS conversion.
- Real `MAP_000`, `MAP_180`, `MAP_184`, `MAP_185`, `MAP_186`, `MAP_187`.
- 48-byte building placement preservation with explicit model-ID remapping.
- AreaData field conversion for Twinleaf exterior/interior.
- Map/prop NSBTX source availability and `BTX0` signatures.
- All 26 placed NSBMD prop-model source files and `BMD0` signatures.
- Generated HGSS prop-set members.
- Twinleaf event structural conversion.
- Append-only target capacities and reserved IDs.

## Deliberately not claimed yet

DS03 does **not** claim that Twinleaf has booted/rendered inside HG-Engine. It also does not certify:
- NPC object-sprite remapping,
- translated Platinum field scripts,
- message-bank conversion,
- special model-ID keyed animations/behaviors,
- final regional matrix integration,
- New Game redirection.

Those are transplant/runtime gates beginning with the next phase.

## Safety / reproducibility

No commercial ROM is committed. Public source assets are fetched from pinned upstream source revisions during CI, generated resources are temporary unless represented as legal source/configuration, and target IDs remain append-only.
