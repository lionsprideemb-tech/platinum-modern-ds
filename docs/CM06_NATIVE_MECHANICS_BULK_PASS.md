# CM06 Native Mechanics Bulk — PASS

Date: 2026-09-25

## Result

The first full bulk pass for community moves that require **no new battle
mechanics** passed in native `pokeplatinum`.

GitHub Actions workflow: **CM06 Native Mechanics Bulk**  
Run ID: `36137516832`  
Conclusion: **success**

## Bulk selection

The audited 519-move community catalog was partitioned automatically:

- Previously materialized before CM06: **24**
- Added in CM06 using existing Platinum mechanics: **153**
- Total live community moves after CM06: **177**
- Deferred for later mechanics/design review: **342**
- CM06 ID range: **1048-1200**

The accounting gate verified:

`24 + 153 + 342 = 519`

No deferred move was approximated just to increase the count.

## Native proof

CM06 restored the complete modernized Platinum foundation and CM01-CM05,
installed all 153 selected moves, compiled the full ROM, and ran a
representative Iron Fangs battle proof in DeSmuME.

Proof artifact: `cm06-native-mechanics-bulk-proof`  
Artifact ID: `10865139423`  
Artifact digest:
`sha256:6d32617e8c0f7f48600fe3c63032c17de388ab436bc441e77e1df54cd3f1f0f4`

## Policy going forward

The **342 deferred moves are the mechanics-review pool**. They remain out of the
native-only implementation lane until their missing/custom behavior is reviewed.

This keeps the fast path complete: every move the selector could represent with
existing Platinum effects/targets/priorities was bulk-installed first.

**CM06: PASS**
