# PT04E Gen VI Donor Audit Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation VI base-species block is available from the pinned HG-Engine donor and maps cleanly into Mercury DS's contiguous species architecture.

## Scope

- Canonical National Dex range: **#650–721**
- First species: **Chespin**
- Last species: **Volcanion**
- Expected species: **72**
- Parsed species: **72**
- Missing donor species entries: **0**
- Missing required front/back/icon assets: **0**

## CI proof

- Workflow: `PT04E Gen VI Bulk Expansion Audit`
- Run number: **1**
- Run ID: **35901136800**
- Commit: `8cc1d47bbdfbd14e1a25d9cd6964fec2bd66ad69`
- Conclusion: **success**
- Artifact: `pt04e-gen6-donor-audit`
- Artifact ID: **10769421203**
- SHA-256: `5077ff3603f74e96c3564fe78d33b115707587ecc7ebd1098427601b2cb0a059`

## Compatibility findings

Already supported by the current Mercury Platinum layer:

- every Gen VI base type, including Fairy,
- every donor held item used by the base Gen VI block,
- all growth rates after the existing growth-rate translation,
- all egg groups.

Explicit later-mechanics exceptions:

- **21 distinct modern ability constants** are not yet present in the current ability table.
- **11 species** have modern base EXP values above Platinum's current one-byte field and require the planned widening.

The >255 base-EXP species are:

- Chesnaught
- Delphox
- Greninja
- Florges
- Goodra
- Xerneas
- Yveltal
- Zygarde
- Diancie
- Hoopa
- Volcanion

## Form scope

This base-species gate does not claim alternate forms are complete. Gen VI form work remains separate, including examples such as:

- Vivillon patterns,
- Flabébé/Floette/Florges flower colors,
- Furfrou trims,
- Meowstic gender-form semantics,
- Aegislash Blade form,
- Pumpkaboo/Gourgeist sizes,
- Zygarde forms,
- Hoopa Unbound.

Those forms must use the form registry rather than consuming new canonical base-species IDs.

## Next gate

`PT04E_GEN6_BULK_BUILD`

Generate the 72 canonical base-species resource directories, register through Volcanion #721, and compile the expanded Platinum archives before any runtime spot test.
