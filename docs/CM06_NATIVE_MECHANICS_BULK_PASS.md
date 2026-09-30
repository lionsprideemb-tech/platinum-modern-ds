# CM06 Native Mechanics Bulk — PASS

Date: 2026-09-25

## Result

The expanded full bulk pass for community moves that require **no new battle
mechanics** passed in native `pokeplatinum`.

GitHub Actions workflow: **CM06 Native Mechanics Bulk**  
Run ID: `36139742050`  
Conclusion: **success**

## Bulk selection

The audited 519-move community catalog was partitioned automatically:

- Previously materialized before CM06: **24**
- Added in CM06 using existing Platinum mechanics: **210**
- Total live community moves after CM06: **234**
- Deferred for mechanics/design review: **285**
- CM06 ID range: **1048-1257**

The accounting gate verified:

`24 + 210 + 285 = 519`

The expanded selector recognizes additional mechanics that are already native to
Platinum rather than incorrectly sending them to the custom-mechanics pool.

## Native proof

CM06 restored the complete modernized Platinum foundation and CM01-CM05,
installed all 210 selected moves, compiled the full ROM, and ran a
representative Iron Fangs battle proof in DeSmuME.

Proof artifact: `cm06-native-mechanics-bulk-proof`  
Artifact ID: `10866273310`  
Artifact digest:
`sha256:1cfc30cbd00c989f3b672c48d237b148b0f1f2f1aaa41d14769c73167e39b8c1`

## Policy going forward

The remaining moves stay out of the native-only lane unless their full audited
behavior is already representable by Platinum. Custom source types are handled
separately by CM07 and are retyped to canonical Pokémon types before becoming
playable.

**CM06: PASS**
