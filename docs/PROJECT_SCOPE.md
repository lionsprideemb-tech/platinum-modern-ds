# Project Scope

## Foundation

Platinum Modern DS now uses **Pokémon Platinum itself as the runtime and world foundation**.

We are no longer trying to transplant Sinnoh into HGSS/HG-Engine. The HG-Engine work remains preserved as a research/reference branch, but the active project modifies the native Platinum decompilation directly.

## Version 1 priorities

1. Reproducible native `pret/pokeplatinum` build in GitHub Actions.
2. Establish a clean project-owned overlay/patch workflow.
3. Make one harmless visible source modification and prove it in a built runtime.
4. Add modern type/mechanics support, beginning with Fairy.
5. Design safe Pokédex expansion architecture toward #1025.
6. Expand moves, abilities, items, evolution methods, graphics, and forms.
7. Add high-value QoL without disturbing Platinum's world/story.
8. Rebuild selected Elite Redux-style information UI natively for Nintendo DS.

## Preserve by default

Unless a feature specifically requires changing them, preserve Platinum's:

- Twinleaf, Route 201, Sandgem, and all Sinnoh map geometry
- interiors and warps
- camera and field rendering
- story/event progression
- trainers and encounters until intentionally edited
- music and map identity
- save/load behavior

## Explicit non-blockers for early playability

These features must not delay a stable modernized Platinum baseline:

- Full UI replacement
- Custom Pokémon/forms
- Mercury-specific story rewrites
- Large-scale side quests
- Clothing/customization systems
- Full randomizer
- Every optional postgame enhancement

The stock Platinum UI remains the fallback until replacement screens are certified.
