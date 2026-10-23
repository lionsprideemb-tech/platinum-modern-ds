# Mercury Redux sprite curation gate — 2026-10-23

## Current policy

Keep the completed Platinum playable foundation and the approved modern UI, Research Poké Radar, encounter work, moves, and ability systems intact. The separate sprite curation effort must **not** replace the native game ROM or modify the DS data until final review decisions are explicitly exported, reconciled, and validated.

Authoritative review sources:

- Reviewer: https://lionsprideemb-tech.github.io/Sprites/master-review.html
- Candidate metadata: https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json
- Protected decisions: https://github.com/lionsprideemb-tech/Sprites/blob/main/audit/2026-10-23/historical-decisions.json
- Asset repair/collision queue: https://github.com/lionsprideemb-tech/Sprites/blob/main/audit/2026-10-23/repair-queue.json
- Dex handoff: https://github.com/lionsprideemb-tech/Mercury-redux-dex/blob/main/SPRITE_REVIEW_HANDOFF_2026-10-23.md

## Integration gates

1. Reconcile the exported master-review decisions with the 1,043-row historical approval ledger, resolving duplicated form identities and mutually inconsistent records.
2. Confirm that approved designs have correct identity, evolution-family routing, official or explicitly selected custom types, and trustworthy front/back sprites (including shiny/icon requirements for final DS-ready integration).
3. Resolve all type/back-art holds and avoid presuming a sprite filename implies a valid species/form assignment.
4. Stage changes on a dedicated integration branch, with species/form ID collision checks and a reproducible ROM build.
5. Preserve protected official Pokémon/Megas, canonical Platinum progression, the locked Summary UI, and Research Poké Radar. Do not overwrite existing working systems.
6. Integrate *only* explicit final approvals, not items that were imported, automatically staged, or previously rejected.

Current reviewer snapshot has 164 actionable artwork choices and 35 technical holds. These are NOT counts of ROM-ready entries.

**This commit is documentation-only; it does not build, mutate, or integrate the game's sprites.**
