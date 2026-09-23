# PT04F Gen VII Donor Audit Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation VII base-species block is available from the pinned HG-Engine donor and passes Mercury DS's pre-generation compatibility audit.

## Scope

- Canonical National Dex range: **#722–809**
- First species: **Rowlet**
- Last species: **Melmetal**
- Expected species: **88**
- Parsed species: **88**
- Missing donor species entries: **0**
- Missing required front/back/icon assets: **0**
- Unsupported donor gender-ratio encodings: **0**

## CI proof

- Workflow: `PT04F Gen VII Bulk Expansion Audit`
- Run number: **1**
- Run ID: **35904463598**
- Commit: `000a8172f0a359763dce41e02d48ad722345ac00`
- Conclusion: **success**
- Artifact: `pt04f-gen7-donor-audit`
- Artifact ID: **10771060554**
- SHA-256: `3fbb555666ec28a94066b3795d16475659c85242f74cc382e698705d189f206b`

## Compatibility findings

Already supported by the current Mercury Platinum layer:

- all Gen VII base types,
- all growth rates after translation,
- all egg groups,
- all donor gender-ratio encodings used by this batch.

Explicit later-mechanics/build-compatibility exceptions:

- **39 distinct modern ability constants** are not yet present in the current ability table.
- **26 species** have modern base EXP values above Platinum's current one-byte personal-data field.
- New held-item constants needing temporary fallback:
  - `ITEM_CELL_BATTERY`
  - `ITEM_ELECTRIC_SEED`
  - `ITEM_GRASSY_SEED`
  - `ITEM_MISTY_SEED`
- `ITEM_TINY_MUSHROOM` uses the already-known Platinum naming alias `ITEM_TINYMUSHROOM`.

## Form scope

This base-species gate does not claim Generation VII alternate forms are complete. Form work remains separate, including examples such as:

- Oricorio styles,
- Lycanroc forms,
- Wishiwashi School,
- Minior cores/colors,
- Mimikyu busted state,
- Silvally types,
- Necrozma fusions/Ultra,
- Magearna Original Color,
- and Alolan regional forms.

These belong to the form registry/resource layer and do not consume new canonical base-species IDs.

## Next gate

`PT04F_GEN7_BULK_BUILD`

Restore the sealed Gen V and Gen VI generated resources, generate the 88 canonical Gen VII base-species directories, register through Melmetal #809, and compile the cumulative Platinum archives.
