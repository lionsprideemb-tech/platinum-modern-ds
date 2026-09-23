# PT04D Gen V Donor Audit Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

This checkpoint proves that the complete canonical Generation V base-species block can be resolved from the pinned HG-Engine donor by species identity, independent of HG-Engine's offset numeric IDs.

## Scope

- Canonical National Dex range: **#494–649**
- First species: **Victini**
- Last species: **Genesect**
- Expected species: **156**
- Parsed species: **156**
- Missing donor species entries: **0**
- Missing required front/back/icon assets: **0**

## CI proof

Final compatibility-aware audit run:

- Workflow: `PT04D Gen V Bulk Expansion Audit`
- Run number: **3**
- Run ID: **35892216107**
- Commit: `e29e5d68165a38e4697ff268a89e70a295a322dd`
- Conclusion: **success**
- Artifact: `pt04d-gen5-donor-audit`
- Artifact ID: **10765287076**
- SHA-256: `b288049a07804227f54367f6eeb9795ea443cf738a9bc8cbff0c1e5acb1c37c0`

## Compatibility findings

The Mercury Platinum overlay already supports every type required by the Gen V donor block, including **TYPE_FAIRY**.

The following map without a missing-constant problem:

- all Gen V donor types,
- all donor growth rates after `GROWTH_X -> EXP_RATE_X`,
- all donor egg groups.

Remaining PT05/mechanics exceptions are narrow and explicit:

- **28** donor ability constants are not yet present in the current Platinum ability table.
- Six donor held-item names do not match current Platinum constants; five are naming aliases and one is a genuinely later item:
  - `ITEM_BLACK_GLASSES -> ITEM_BLACKGLASSES`
  - `ITEM_DEEP_SEA_TOOTH -> ITEM_DEEPSEATOOTH`
  - `ITEM_NEVER_MELT_ICE -> ITEM_NEVERMELTICE`
  - `ITEM_SILVER_POWDER -> ITEM_SILVERPOWDER`
  - `ITEM_TINY_MUSHROOM -> ITEM_TINYMUSHROOM`
  - `ITEM_ABSORB_BULB` requires later item support.
- **26** Gen V species have modern base EXP above Platinum's current one-byte field and require the planned base-EXP widening. PT04D may clamp those values to 255 only as an explicit compatibility build measure.

## Architecture rule retained

Mercury canonical base species remain contiguous:

`NONE, #1..#1025, EGG, BAD_EGG`

The HG-Engine donor's Victini=544 numbering is not copied. Donor content is mapped by species constant/name and canonical National Dex position.

## Next gate

`PT04D_GEN5_BULK_BUILD`

The batch generator must install all 156 species and produce a successful Platinum configure/build with expanded compiled archives before runtime spot testing begins.
