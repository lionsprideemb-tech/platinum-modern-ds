# PT04G Gen VIII Donor Audit Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The complete canonical Generation VIII base-species block is available from the pinned HG-Engine donor and passes the Mercury DS pre-build compatibility audit.

## Scope

- Canonical National Dex range: **#810–905**
- First species: **Grookey**
- Last species: **Enamorus**
- Expected species: **96**
- Parsed species: **96**
- Missing donor entries: **0**
- Missing required front/back/icon assets: **0**
- Unsupported raw gender-ratio encodings: **0**

## CI proof

- Workflow: `PT04G Gen VIII Bulk Expansion Audit`
- Run number: **2**
- Run ID: **35909127545**
- Commit: `c1fe60d1a16f0c7062bbf54b4458b06482782f10`
- Conclusion: **success**
- Artifact: `pt04g-gen8-donor-audit`
- Artifact ID: **10771444482**
- SHA-256: `5e70f85b1b470e7f8a841d86306d949db7db782d2d8ca68b7f351aca08236e90`

## Compatibility findings

Already compatible in the current Mercury Platinum layer:

- all donor base types used by the Gen VIII canonical block,
- all donor held-item constants used by the base block,
- all growth rates,
- all egg groups,
- all raw gender-ratio encodings after the existing donor translations.

Explicit later-mechanics exceptions:

- **35 distinct modern ability constants** are not yet present and remain deferred.
- **14 species** have modern base EXP values above Platinum's current one-byte field and require the planned widening.

## Boundary note

Enamorus is female-only in the donor. Its male sprite files are intentional zero-byte placeholders; the real front/back resources are in the female folder. The successful audit uses gender-aware resource detection rather than assuming a male boundary asset.

## Next gate

`PT04G_GEN8_BULK_BUILD`

Restore the sealed Gen V, VI, and VII generated resource layers, generate the 96 Gen VIII canonical base species, register through Enamorus #905, and compile/verify the cumulative Platinum archives.
