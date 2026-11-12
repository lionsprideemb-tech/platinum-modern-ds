# Mercury Redux — Isolated Delta Custom-Species Registry Prototype
Date: 2026-11-12
Branch: qa/delta-custom-registry-prototype-20261112 in lionsprideemb-tech/platinum-modern-ds
Status: QA-only symbolic prototype; NOT a native species patch, ROM release, sprite approval, or save migration.

## November 11 audit reconciliation
- Existing real Dex audit branch: qa/delta-flygon-architecture-20261111, commit 8ea34c7ad72c593b0f9f7845d03acff13fd2ecdd.
- Existing pinned-source Dex audit workflow 43103979480 passed; the earlier audit did not implement a native engine registry.
- There was no Delta/QA branch in platinum-modern-ds before this new branch was created.
- Baselines: Engine 5525e961a1fb98c62bd53bc4a27b0276a39f6719; Dex main faa7cb4016d8030fb4661b49114352d79cac7944; Sprites f15c4671bf7afb15450fc7801bde17aefcdc4f7e; pret c248fb3f8cc9934ded800e489567c5c0eeee92eb; hg-engine 5157c501dc0e6f88ef1654ab121352a5cc9ed7de.

## Protected state and unchanged decisions
- All 1,025 canonical species, including Trapinch #328, Vibrava #329, Flygon #330, remain unchanged.
- NONE 0, Egg 1026, Bad Egg 1027 are protected, not allocatable.
- The pinned Sprites decision file still contains 166 historic entries: 154 KEEP, 12 CUT, with latest conflicting choices respected.
- Route 2 keeps the canonical line and one ordinary Mega plan; it proposes a separate Bug-themed Delta family. The Electric/Dragon Redux B family is retired from the playable roster, not deleted from history.
- All Orpheus/Desert Scarab Delta artwork remains unapproved. No production numeric species IDs, sprite IDs, icon indices, palette banks, Delta evolution method/levels, or save version were assigned.

## Implemented, executable prototype
The QA-only file qa/delta_registry_prototype.py defines three symbolic identities:
- CUSTOM_DELTA_TRAPINCH — Bug required; additional type undecided.
- CUSTOM_DELTA_VIBRAVA — Bug required; additional type undecided.
- CUSTOM_DELTA_FLYGON — Bug/Ground.

The draft evolution graph is Delta Trapinch → Delta Vibrava → Delta Flygon. Earlier canonical evolution at levels 35 and 45 is not replaced. No Delta levels or methods are assigned. The script rejects incorrect direct Trapinch → Flygon edges and unapproved numeric or palette allocation.

A Python model simulates legacy little-endian u16 species fields and checks roundtrips for NONE, canonicals, Egg, and Bad Egg. Unknown values and custom symbols fail closed (no save writes/migration). This is NOT a native DS save serializer or emulator test.

Pinned upstream native source checks cover species and form widths, MAX_SPECIES/NATIONAL_DEX_COUNT coupling, Pokédex bitset/save-size hooks, evolution target plumbing, icon fallbacks, palette lookup, and Meson icon/archive inputs. Under present code, species above NATIONAL_DEX_COUNT are routed to SPECIES_NONE in the icon code. Custom icon and palette routing intentionally reject until native implementation.

The full donor icon palette table has 1,535 explicit assignments: bank 0 = 844, bank 1 = 310, bank 2 = 381, bank 3 = 0. Bank 3 being unassigned in this donor table does NOT prove native Platinum VRAM, shared NCLR, or generated icon archive safety.

The audit's duplicate site IDs 1581, 1751, 1761 remain unclassified for game import; these are not established native collisions. Legacy Electric Redux B source IDs 2081 and 2082 remain history-only, not future Delta IDs.

## Verified QA evidence
- GitHub Actions successful run (42 QA/model checks): https://github.com/lionsprideemb-tech/platinum-modern-ds/actions/runs/43286160472
- Source: qa/delta_registry_prototype.py
- CI: .github/workflows/delta-custom-registry-prototype-qa.yml
- Artifact: delta-symbolic-registry-qa-only; machine-readable registry-prototype-evidence.json.
- Repository Guard passed. No native runtime build, save migration, emulator, game asset patch, or ROM change was run.

## Exact blockers to native approval
1. Native custom namespace, bounds, migration: review versioned IDs separate from 1–1025 and 1026/1027; decouple MAX_SPECIES from National Dex count where necessary; prove party, PC, trades, save/reload and Pokédex caught/seen flags.
2. Icon and palette: implement a real custom route, archive indices and bounds, generated pl_poke_icon.narc, shared NCLR 4bpp palette content and party/PC/battle/summary/Dex/evolution/trade UI lifetime. Do not activate bank 3 on donor evidence alone.
3. Delta evolution: review method/level choices. Preserve vanilla 35 and 45; reject the invalid Orpheus source links (Trapinch → Flygon; Vibrava → Lycanroc).
4. Art and runtime: user approval of matching source-faithful front/back/shiny/icon, rights/provenance, native DS compilation and emulator screen tests still pending. Symbolic validation is not gameplay validation.
5. Dex export: future reviewed policy must exclude Redux B from playable export but preserve all legacy rows, votes and artwork, including duplicated numeric site IDs.

## Next Major Release: Native Registry & Save Compatibility Gate
On this isolated QA branch only, inventory all native consumers of species counts and save records, design a versioned custom namespace and non-production test-only sentinel fixtures, and prove native serialization/lookup behavior without production IDs or ROM integration. Obtain full engine/emulator proof before any real custom species allocation. Do not modify main, the playable ROM, or any artwork decision.
