# CM07 Canonical Type Resolution — PASS

Date: 2026-09-25

## Result

Mercury Redux now enforces **canonical Pokémon move types only** for the
community-move catalog.

All **32** source moves that used non-canonical types have an explicit Mercury
retype resolution. The original source type is kept only as provenance.

### Canonicalization policy

- Sound -> Normal / Electric / Fighting / Ghost as appropriate to the move
- Nuclear -> Poison
- Shadow -> Ghost or Dark
- Crystal -> Rock
- Qmarks / ??? -> a thematic canonical type such as Normal, Psychic, Fire,
  Electric, or Poison

Any custom type-chart rider tied specifically to the removed source type is
dropped rather than recreating the non-canonical type.

## Implementation

The canonical-type pass follows the expanded CM06 native-mechanics sweep:

- CM01-CM05: 24 live moves
- CM06: 210 additional no-new-mechanics moves at IDs **1048-1257**
- CM07: 18 canonicalized custom-type moves at IDs **1258-1275**
- Total live community moves after CM07: **252**
- Retyped moves still deferred only for mechanic review: **14**

The 14 deferred moves already have canonical Mercury types; they are blocked
only by mechanics such as dynamic typing/category, unusual multi-hit behavior,
field effects, PP manipulation, or other custom battle logic.

## Native proof

GitHub Actions workflow: **CM07 Canonical Type Resolution**  
Run ID: `36141083789`  
Conclusion: **success**

The workflow verified all **32/32** source custom-type records have canonical
Mercury resolutions, rebuilt the expanded CM06 layer, installed CM07, verified
all CM07 native animation donors, compiled the full Platinum ROM, and executed
Atomic Punch in the native DS battle runtime.

Proof artifact: `cm07-canonical-type-resolution-proof`  
Artifact ID: `10866593335`  
Artifact digest:
`sha256:f798d0810fdca4b7de032796a7a2f4f0b7eda9dd4f517520620824b8553233a5`

After CM07, the last live community move ID is **1275** and `MAX_MOVES` is
**1276**.

**CM07: PASS**
