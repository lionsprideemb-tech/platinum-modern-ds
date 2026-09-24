# Milestones

> **Authoritative execution roadmap:** see `docs/MERCURY_FASTEST_PATH_ROADMAP.md`. That document defines the fastest-path order: finish Modern Platinum first, seal a golden baseline, then add Mercury systems one at a time.

> **Authoritative execution order:** see `docs/MERCURY_MASTER_ROADMAP_FASTEST_PATH_2026-09-24.md`.
>
> Project strategy as of 2026-09-24: finish and freeze **Mercury Modern Platinum 1.0** first, then layer Mercury features onto that known-complete game in small reversible passes. Long tile-by-tile navigation testing is no longer the normal development method.

## Current fast-path sequence

1. PT05A — bulk modern compatible learnsets.
2. PT05B — bulk evolution integration.
3. Modern moves through Gen 9.
4. Modern abilities through Gen 9.
5. Species-data/TM/tutor/forms cleanup.
6. Build and certify Mercury Modern Platinum 1.0.
7. Freeze `checkpoint/modern-platinum-1.0-golden`.
8. Encounter overhaul.
9. HM-free traversal.
10. Randomizer.
11. Item/shop/evolution QoL.
12. Trainer and boss rebalance.
13. Megas, Deltas, innate system, UI, customization, quests, and map/story expansion.
14. Final fresh-save Mercury certification.

---

## PT01 — Native Platinum Baseline
- Pin `pret/pokeplatinum`.
- Reproduce its source build in our own GitHub Actions workflow.
- Run `make check`.
- Record exact source revision and build fingerprint.
- Keep commercial ROM files out of the repository.

## PT02 — Project Modification Proof
- Add `platinum-overlay/` as the project-owned modification layer.
- Apply one harmless, visible modification.
- Build successfully.
- Capture emulator/runtime evidence that the modification is actually present.
- Certify this as the first project-owned playable baseline.

## PT03 — Modern Mechanics Foundation
- Fairy type.
- Modern type chart.
- Physical/special and battle-system compatibility audit.
- Expand constants/tables safely before bulk data import.

## PT04 — Pokédex Expansion Architecture
- Determine species/form limits in native Platinum.
- Expand species-indexed tables systematically.
- Establish graphics/icon/cry/data allocation rules.
- Add canonical Pokémon in controlled batches toward #1025.

## PT05 — Battle Data Expansion
- Moves.
- Abilities.
- Items.
- Evolution methods.
- Learnsets.
- Forms and special mechanics.

## PT06 — Quality of Life
- Modern reusable TMs or chosen TM policy.
- Evolution modernization.
- Faster/common interface improvements.
- Field traversal improvements where desired.
- Additional encounter and party-management conveniences.

## PT07 — Redux-Inspired Platinum UI
- Build one information-rich native dual-screen interface.
- Preserve the stock Platinum screen as a fallback until certified.

## Later Mercury phases
- Custom Pokémon/forms and Megas.
- Ability/innate system.
- Randomizer and presets.
- Boss redesign.
- Side quests and customization.
- Full Mercury Redux content pass.

## Archived research milestones

The earlier DS01–DS04 HG-Engine/HGSS transplant work remains preserved in Git history and feature branches. It is reference material, not the active runtime architecture.
