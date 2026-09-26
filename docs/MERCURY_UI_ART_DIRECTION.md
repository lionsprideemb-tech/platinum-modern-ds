# Mercury DS UI Art Direction Standard

## Core rule

Every shipping UI in Pokémon Mercury Redux must look as though it belongs in an official Nintendo DS-era Pokémon title, with Pokémon Platinum as the primary visual language.

Temporary engineering scaffolding is allowed only during implementation and must never be treated as final art.

## Final UI requirements

- Use native DS graphic assets, tilemaps, palettes, sprite resources, window-frame resources, fonts, icons, cursors, arrows, and animation conventions wherever practical.
- Prefer Pokémon Platinum resources and composition rules before inventing new visual language.
- New Mercury graphics must be authored as proper DS assets and integrated through the same resource/rendering systems as the surrounding Platinum UI.
- Maintain pixel-grid discipline, spacing, typography, palette limits, hierarchy, and interaction feedback consistent with official Gen IV interfaces.
- Preserve native-looking transitions, selection states, button prompts, and confirmation flows.

## Prohibited final presentation

The following are implementation-only and are not acceptable as final shipping UI:

- programmer/debug rectangles used as permanent panels
- borders made from repeated one-pixel FillRect calls
- text-only replacements for established Pokémon iconography
- placeholder tabs or boxes
- flat mockup styling that ignores Platinum's tile/sprite language
- UI that visually reads as a ROM-hack/debug screen rather than an official menu

Calls such as Window_FillRectWithColor remain valid for data-driven gauges, masks, transient highlights, or other effects where Platinum itself uses equivalent drawing logic. They are not to be used as a substitute for authored panel/frame artwork.

## Source hierarchy

1. Pokémon Platinum native assets and UI code
2. Other official Gen IV DS Pokémon UI patterns where compatible
3. Mercury-authored DS assets designed to match the above
4. Other games such as Elite Redux only as interaction/layout references, never as a direct GBA renderer transplant

## Review gate

A custom Mercury screen is not visually complete until it passes all of these questions:

- Could this plausibly appear in an official Gen IV Pokémon release?
- Do the panels/tabs/icons look authored rather than programmatically sketched?
- Does it use the same visual grammar as Platinum?
- Are type/category/status indicators represented with proper iconography where appropriate?
- Are spacing, text density, and hierarchy comfortable at 256x192?
- Does switching pages or states preserve a coherent DS-native presentation?

If any answer is no, the screen remains a prototype.

## Scope

This standard applies globally to Mercury Redux, including:

- Move Learner
- Pokémon Summary extensions
- Party UI additions
- Stats and Ability pages
- Abilitydex / Movedex
- Randomizer settings
- Encounter viewer
- HM-free traversal prompts
- Shop/salon/customization menus
- Side-quest interfaces
- Debug tools intended for player-facing builds
- any future custom top- or bottom-screen menu
