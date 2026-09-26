# MR03D — Platinum-Native Move Learner UI

## Baseline

MR03C is the functional baseline. It proves:

- universal move list backend
- source filters
- teaching / replacement state flow
- Move / Stats / Ability page switching
- stable 0x30000 Move Reminder heap
- corrected Garchomp portrait tile ordering and VRAM layout
- browse-time Platinum message prompt removed
- eight-screen DeSmuME proof path

Protected baseline:
`checkpoint/mr03c-final-functional-ui-2026-09-26`

MR03D replaces the visible engineering scaffold without rewriting the working backend.

## Design target

### Top screen — Platinum Summary language

Use Platinum's real Pokémon Summary resources from `PL_PST_GRA`.

Primary reusable resources identified in upstream Platinum:

- `tiles_main_NCGR`
- `tiles_main_NCLR`
- `page_info_NSCR`
- `page_skills_NSCR`
- `page_battle_moves_NSCR`
- `move_info_NSCR`
- native Summary tab sprites
- native type icons
- native move category icons
- native page arrows
- native health-bar tile system
- native font/window conventions

The MR03D pages are:

1. **MOVE** — based on Platinum's Battle Moves visual language.
2. **STATS** — based on Platinum's Skills page visual language.
3. **ABILITY** — a Mercury-authored page assembled from Platinum-native panel/tile/sprite vocabulary, not debug rectangles.

L/R remains the page navigation control.

### Bottom screen — Elite Redux interaction concept, DS renderer

Elite Redux is used as a UX reference, not as code to transplant.

Useful ER concepts confirmed in `src/move_relearner.c` / `src/menu_specialized.c`:

- persistent scrollable learnable-move list
- selected move updates details immediately
- Power / Accuracy / PP + description shown without opening another screen
- fast A-to-teach flow
- clear list state and scroll position

Mercury keeps those interaction strengths but renders them with Platinum DS resources.

Bottom layout:

- source-filter tabs: ALL / LEVEL / EGG / TUTOR / SPECIAL
- current four moves
- scrollable learnable list
- selected move detail area
- proper type icon
- proper Physical / Special / Status category icon
- Power / Accuracy / PP
- move description
- DS-native cursor/highlight and scroll arrows
- concise button-help strip

## Architecture

Do not port Elite Redux's GBA background/window/OAM code.

MR03D keeps:

- MR03 backend move enumeration
- existing source metadata
- filtered ListMenu behavior
- selected move IDs
- native Platinum teach / replace state machine
- existing party-menu entry point

MR03D replaces:

- programmatically outlined permanent panels
- text-only type/category presentation where iconography exists
- prototype tabs/cards
- prototype top-page composition

## VRAM rule

The corrected MR03C portrait/VRAM work is a hard regression gate.

New summary graphics must be assigned explicit BG character/screen regions before implementation. No resource may be added until its tile, tilemap, and palette range is documented and shown not to overlap:

- Pokémon portrait character data
- summary background character data
- text windows
- native Move Reminder message/yes-no resources
- bottom-screen list/detail resources

## Implementation phases

### D1 — Native asset plumbing

- load `PL_PST_GRA` alongside Move Reminder resources
- establish safe BG allocation for Summary-derived top graphics
- stage real Summary palette/tile/tilemap resources
- preserve current backend and proof harness

### D2 — Top screen

- MOVE page from Battle Moves shell
- STATS page from Skills shell
- ABILITY page using matching Platinum-native authored pieces
- native type/category icons and page arrows
- retain corrected Pokémon portrait path unless native Summary sprite path can be adopted without regression

### D3 — Bottom screen

- rebuild list/detail layout around DS-authored tilemaps/windows
- replace text type/class labels with icons
- replace box-outline tabs with authored tab assets
- add proper selection/highlight/scroll feedback

### D4 — Interaction polish

- page-change feedback
- filter-change animation/highlight
- confirmation presentation
- long-name/description clipping checks
- empty-list and Cancel behavior
- touch behavior only if it improves the DS-native design

### D5 — proof

Capture and manually inspect at minimum:

- Move / Stats / Ability
- all five source filters
- long move name
- long ability description
- dual-type Pokémon
- single-type Pokémon
- full four-move Pokémon
- Pokémon with empty move slot
- teaching confirmation
- replacement flow

Passing CI is necessary but not sufficient. The visual gate is the Mercury UI Art Direction Standard.
