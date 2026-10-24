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


## Major reviewer and evidence-triage update — October 23, 2026
The sole creative review interface remains [Sprites/master-review.html](https://lionsprideemb-tech.github.io/Sprites/master-review.html). It now includes a **read-only Approved source art** mode: all **74 historically approved original GBA-source front/back pairs**, grouped into **39 actual families**, with original labels, real recorded types, front/back and shiny views. Missing-shiny filtering isolates exactly **five** alternate forms (Breloom, Combee, Vespiquen, Dwebble and Crustle). They require original-source recovery and are **not** candidates for a second KEEP vote.

- [Five missing shiny source repairs](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/legacy-approved-artwork-repair-2026-10-23.json)
- [Grouped identity/family source conflicts](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-family-triage-2026-10-23.json): 19 held source records (10 evolution evidence conflicts, 6 ambiguous artist/region labels, 3 unverified labels). No guessed family or Pokémon ID is promoted to canon.
- [Regression source checks](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/tests/master-review-integrity.cjs) and [GitHub Actions workflow](https://github.com/lionsprideemb-tech/Sprites/blob/main/.github/workflows/sprite-review-integrity.yml).

The **166 original iPhone decisions (154 KEEP / 12 CUT)** are untouched. Backup imports now **merge** rather than discard absent votes, preserve non-current identifiers, and save unresolved technical-hold identity corrections. A GitHub JSON export is still required before review choices become committed project state; the Pages reviewer does not push to GitHub itself.

**Safety:** This was a reviewer, metadata, and test update. The 74 sources remain **GBA originals, not certified DS sprite conversions**. There have been no edits to the ROM, gameplay, Pokédex species registry, stored historical votes, or artwork files. Do not infer a checked GitHub Actions run from the existence of the workflow alone.


## Source-backed name and evolution repair — October 23, 2026

The single canonical [Mercury master reviewer](https://lionsprideemb-tech.github.io/Sprites/master-review.html) now uses the [updated source-linked dataset](https://github.com/lionsprideemb-tech/Sprites/blob/main/master-review-data.json) and records each material original-label change in the [27-record reconciliation](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-family-reconciliation-2026-10-23.json). Compared with the previous 25 warning rows, **12 identity warnings were resolved**, leaving **13 explicit checks** documented in [current status](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-family-current-status-2026-10-23.json). This supersedes older warning totals only as the current reviewer status; historical audit sources are preserved verbatim.

Verified structural repairs: **Furrva → Kocomb (normal → Granebee; militant → Beelitant)**. Furrva is source documented but is missing as an actionable sprite entry, so a source-linked reference warning is displayed with no implied vote. The former invented combined "Platerigus → Mikitarian → Traumatisse" grouping is separated into **Mikitari Yamask → Platerigus**, **Mikitari Spritzee → Traumatisse**, and **standalone Mikitari Falinks**. **Mikitari Buneary → Lopunny** and **Lumio Spinarak → Ariados** are identified by their actual Pokémon names with regional designation kept separate from creator attribution. Both Rainther technical alternatives now show verified Water typing. "Pythonova S" art aliases are grouped under the real Hissiorite → Cobarett → Pythonova line, but the S images are still on technical hold.

Hayog/Hogouse/Hogriks and Minamai/Marelstorm remain **proposed groupings with evolution edges unconfirmed**; Hoothoot/Noctowl/Enchantowl has a documented species graph, but the exact Lumio/Atsui Noctowl illustration is *not* automatically associated with a differently sourced Enjin/Ender Enchantowl. Remaining warnings and exact source paths are in the exception file. No new fake species or arbitrary type was invented.

A test of the committed browser script with a simulated iPhone-style DOM loaded the original **166 protected choices**, and verified the new Spritzee and bee family pages, the Furrva missing-member warning, and the read-only approved-source mode with no runtime exceptions. The committed test assertions also passed against live GitHub file contents with a Node-compatible adapter. Neither test implies a deployed iPhone Safari session or successful GitHub Actions run.

**No Pokémon ROM, playable baseline, Dex species IDs, user KEEP/CUT decisions or artwork files were modified by this repair.** Source verification of names is not sprite quality certification or a license to integrate new content.


## Source recovery and family exception reduction — 2026-10-23

The canonical [Sprites master reviewer](https://lionsprideemb-tech.github.io/Sprites/master-review.html) now has **158 active art candidates, 14 technical holds, and five identity/evolution warnings**. The two new candidate cards are the previously *unvoted* original/Gen 4 Rainther artwork options, each with matched front and back; they are **not** implemented or DS-certified.

Original generation-specific source front/back pairs for **eight** held sprite records were verified and linked via [exact source-pair manifest](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/verified-exception-source-pairs-2026-10-23.json): two Rainther sources; Hissiorite/Cobarett/Pythonova Gen 3; PythonovaS Gen 3/Gen 4-5 shiny companions; and Atsui NOCTOWL_1. Previously approved Hissiorite/Cobarett/Pythonova design-1 KEEP votes and other historical decisions remain protected. The S suffix was confirmed as a *shiny companion* from its matching source pack, **not** a new Pokémon. The Atsui Noctowl variant is not silently linked to the separately published Enjin/Ender Enchantowl lineage.

Mikitari's Furrva original front and back were identified on Pokéngine (Bug, Free to use with credit), and are available as a **read-only external visual reference** inside the bee family until original source bytes are confirmed committed. The credited GitHub Actions source-byte preservation workflow is recorded at `Sprites/.github/workflows/recover-furrva-original-source.yml` and is not authority to call any artwork DS-ready.

The five remaining unresolved warnings are exact evolution edges for Hayog/Hogouse/Hogriks and Minamai/Marelstorm. These names/types and source artists are verified, but a complete documented directed graph is not. Keep these together *as comparison groups without implementing evolution arrows*. [Current exception record](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/identity-family-current-status-2026-10-23.json).

The untouched original iPhone export is **166 decisions = 154 KEEP + 12 CUT**, and the protected ROM/Dex boundary remains closed. **No artwork deletions, new national numbers, type guesses, old vote rewrites, or ROM modifications** were made. The original master integrity workflow was repaired to accept only source-backed audited changes; [run 40038273659](https://github.com/lionsprideemb-tech/Sprites/actions/runs/40038273659) passed. See the [release report](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/FINAL_IDENTITY_MISSING_FAMILY_RELEASE_2026-10-23.md).


## Actual Furrva source artwork recovered (2026-10-23)

The official creator-credited original **Furrva** front and back files are now physically archived in Sprites (successful [GitHub Actions run 40038462240](https://github.com/lionsprideemb-tech/Sprites/actions/runs/40038462240)): [source manifest](https://github.com/lionsprideemb-tech/Sprites/blob/main/DS_CUSTOM_LIBRARY/recovered/Pokengine_Mikitari_Furrva_Source/source_manifest.json). Original WebP plus losslessly decoded PNG source previews: **front 34×30 px, back 55×51 px**; the original uneven sizes are preserved. Artist **Mikitari**; Pokéngine explicitly says **Free to use with credit**. Both previews are now shown as **reference-only** in the existing iPhone family reviewer. No fake sprites, invented shinies, new approval choices or DS-ready claims.

Previous source repair results also remain in force: eight linked full source pairs, two newly *undecided* Rainther artwork comparisons, correct Pythonova shiny companions, isolated non-Enchantowl Atsui Noctowl art, and exactly **five remaining unverified evolution-link warnings** (Hayog/Hogouse/Hogriks, Minamai/Marelstorm). All **166 previously submitted decisions** remain unchanged. The ROM and Pokédex integrations stay closed until separate explicit user-approved staging and native DS tests.


## DS64 source-faithful conversion & image-quality gate — 2026-10-23

The [Sprites project release report](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/DS64_SOURCE_QUALITY_RELEASE_2026-10-23.md) records a **substantial separate technical-conversion batch**. The isolated [technical conversion manifest](https://github.com/lionsprideemb-tech/Sprites/blob/main/DS_CUSTOM_LIBRARY/converted/Verified_Source_DS64_Technical_2026_10_23/technical_quality_manifest.json) audits **83 source artwork sets**, covering 74 historically approved GBA forms, 8 separately matched source comparison sets, and artist-attributed Furrva. **104 technical 64×64 candidate sprite views** were generated: **12 direct pixel-preserved**, **53 from exact reversible duplicate-pixel 2× collapse**, and **39 with explicit palette quantization that still requires visual approval**. The other 228 potential slots comprise **179 unsafe oversized**, **17 partial alpha**, **four unreadable original source PNGs** (Munna and Musharna alternate normal fronts/backs), and **28 source views missing**. Technical candidates are not Nintendo DS native engine graphics or automatically approved artwork.

The **single iPhone [master reviewer](https://lionsprideemb-tech.github.io/Sprites/master-review.html)** now has a read-only **DS technical conversion quality** mode: source and technical image shown together with type, source, family and conversion-status labels; family/source and quarantine filters; disabled Keep/Cut while inspecting quality. Conversion and hash checks run in GitHub Actions; the separate browser smoke test checks JSON export, preserving all **166 original votes (154 KEEP, 12 CUT)**.

Furrva normal front/back source art is recovered, with lossless centered 64×64 technical PNG candidates; its missing shiny images were **not invented**. The previously matched 8 alternative source pairs and all 74 original approvals remain intact. The five unsettled evolution links in Hayog/Hogouse/Hogriks and Minamai/Marelstorm remain unresolved pending actual creator/source proof.

**Integration boundary remains closed:** No ROM files, gameplay mechanics, species IDs, already-approved art or decision records were modified. Nothing from `DS_CUSTOM_LIBRARY/converted/Verified_Source_DS64_Technical_2026_10_23` may be staged into the playable ROM without separate palette/tile-encoding, image-quality, explicit approval and engine checks.


## Major oversized-source sprite recovery & visual quality release — 2026-10-23

The single [Mercury iPhone sprite reviewer](https://lionsprideemb-tech.github.io/Sprites/master-review.html) now includes a read-only original/DS64/nearest-neighbor side-by-side visual mode and **separately exportable, source-hash-bound visual-quality feedback**. Choosing "Preview looks acceptable" is **not** a Pokémon design KEEP vote, native DS art certification or ROM integration authorization. The original **166 iPhone decisions (154 KEEP/12 CUT)** and **five unresolved evolution-link records** remain intact. Use [the full verified release report](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/OVERSIZED_SPRITE_VISUAL_RECOVERY_RELEASE_2026-10-23.md) and [machine-readable current status](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/oversized-visual-recovery-current-status-2026-10-23.json).

Original Munna and Musharna alternate front/back sprites were recovered **losslessly as authentic image-data streams** by retaining their source-critical PNG IDAT chunks while stripping malformed ancillary profile/metadata. Original approved PNGs were not overwritten; new recovered files have exact source-hash and attribution records. [Recovery evidence](https://github.com/lionsprideemb-tech/Sprites/blob/main/DS_CUSTOM_LIBRARY/recovered/Reborn_Plates_Legacy_PNG_Container_Repairs/recovery_manifest.json).

Across 83 source artwork sets, there are now **108 source-derived 64×64 technical candidates (68 source-color preserved, 40 palette-reduced)**, **27 complete normal front/back pairs**, and **17 complete four-view sets**. Oversized/partial-alpha original art remains technically blocked (179 + 17 source views), but **196 explicitly comparison-only nearest-neighbor previews** were generated and hash-verified. **28 source views remain missing; zero PNGs remain undecodable.** The 40 palette-reduced views have measured changed-pixel percentages and await the user's actual visual quality choices. **No previews are native DS engine tiles or ROM-ready by default**.

Verified scripts and GitHub Actions include the separate image-container repair workflow, technical sprite converter, nearest-neighbor visual comparison builder, historical decision invariants, and simulated iPhone comparison/JSON export test. Do not infer that a live Safari session or ROM emulator was run. The Dex and Platinum repositories receive **this documentation only**, never the quarantined preview art or changes to species IDs, gameplay, approved design decisions, or the playable ROM.


## October 24 final artwork choices — ALL active decisions complete

This updates, rather than replaces, the historical October 23 review. **All 158 actionable artworks have user decisions** (the 154 previously decided active artworks plus four now finalized). The immutable historical 166 original iPhone decisions (154 KEEP / 12 CUT) remain preserved as the original 2026-10-23 source snapshot; four new exact-artwork votes are in a separate appendix: [2026-10-24 final approval overlay](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/final-artwork-approval-overlay-2026-10-24.json).

- Wailmer alternate artwork `reconcile:wailmer-alternate-form-1` — **KEEP**.
- Wailord alternate artwork `reconcile:wailord-alternate-form-1` — **KEEP**.
- Rainther original battler artwork `compare:rainther:1` — **CUT competing design only**, not the Pokémon.
- Rainther Gen 4 artwork `compare:rainther:2` — **KEEP**.

The user also explicitly reconfirmed the latest archived art selections, superseding inconsistent earlier exports without rewriting the original records: **Mega Lucario Z Design 2 (Elite Redux Bulk) KEEP / Design 1 (DrPrettyman) CUT**, and **Mega Golisopod Design 1 (DrPrettyman) KEEP / Design 2 (Elite Redux Bulk) CUT**. These four Mega decisions were already part of the original 166, not four new votes. See [release report](https://github.com/lionsprideemb-tech/Sprites/blob/main/review/FINAL_ARTWORK_APPROVALS_2026-10-24.md).

**No sprite insertion into game code, native DS certification, species/evolution changes or asset file substitutions are authorized by these votes alone.** The original 14 technical holds, five evolution relationship warnings, 179 oversized views, 17 partial-alpha views, 28 missing source views and 40 pending palette-quality checks remain separate. Technical quality feedback cannot override the creative source choice. Future gameplay/Pokédex integration must use the selected exact source and pass native DS tile/palette and relevant QA gates first.
