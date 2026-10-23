# Mercury Redux DS — sprite review integration safety (2026-10-23)

## Single source of truth
Do not integrate custom Pokémon/forms from isolated reviewer pages or inferences. Use the canonical [Sprites master reviewer](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review.html) and its [dataset](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json), with the [uploaded 166 user decisions](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/user-iphone-decisions-2026-10-23.json) and [identity/artist audit](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-provenance-audit-2026-10-23.json). Primary review webpage: https://lionsprideemb-tech.github.io/Sprites/master-review.html

## Preserve existing playable DS work
This audit does not modify native Platinum progression, encounter tables, Poké Radar, Move Learner, ability mechanics, title assets, any build checkpoints, or the ROM. The full-game baseline and DS QoL work remain independent of sprite selection.

## Mandatory gate for sprite integration
1. Candidate has a deliberate user KEEP with stable source/structural identity. Archive an alternative CUT without deleting image files.
2. Species and correct form name are verified *separately* from artist name, original filename, source pack, and regional/source labels such as Mikitarian or Luminian.
3. Evolution family and actual type(s) have evidence, not generic Normal or arbitrary guessed lineage.
4. Front/back and required shiny/icon components are validated as the same design. Do not substitute repeated unrelated backs. Prefer native DS art only after identity matching.
5. Specifically, the Platinum Redux embedded-workbook [mapping summary](https://github.com/lionsprideemb-tech/Sprites/blob/main/DS_CUSTOM_LIBRARY/DS_READY_MASTER/platinum_redux_workbook_map_summary.json) reports **3 matched of 212 authoritative entries**; do not treat arbitrary numbered workbook-image associations as verified.
6. No species IDs or ROM changes until the above gates pass and a separate build/test review explicitly approves implementation.

## Existing snapshot
Canonical iPhone user file: **166 votes = 154 KEEP + 12 CUT**. Canonical current reviewer: **156 active entries** (including 2 unreviewed Wailmer/Wailord original-source previews), **16 technical holds**, **25 identity warnings**, with overlapping classifications. These are not counts of finalized species added to the ROM.

## Scope
Documentation-only cross-repository handoff. No asset deletion, sprite re-selection, Pokédex placement, or ROM integration performed.

## October 23 follow-up — source preview recovery
The original front/back/shiny GBA assets for Flying-type alternate Wailmer and Wailord were recovered in the Sprites repository and exposed as two still-undecided creative comparisons. The preserved **166 explicit iPhone votes remain unchanged**. Those two source designs have **not** been certified as DS-ready, assigned Pokédex IDs, or integrated into Platinum. The canonical reviewer now opens on outstanding families and its bulk KEEP action is restricted to designs actually visible on the current page.

## Later approved-source repair inventory (2026-10-23)
The Sprites repository has linked **74 original GBA-source front/back pairs** to previously approved Reborn / Plates identities, with **69 complete shiny quartets and 5 without shiny art**. Evidence: [recovery manifest](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/recovered-approved-legacy-pairs-2026-10-23.json); [read-only gallery](https://lionsprideemb-tech.github.io/Sprites/approved-legacy-recovery.html). They remain source previews, not DS-converted or implementation-ready assets. This is repair evidence only; do not requeue KEEP approvals, assign species IDs, stage into the game, or treat placeholders as verified art. The ROM and Dex were not modified by this linkage.
