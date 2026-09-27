# Mercury MR06B — Research Poké Radar scope

Date: 2026-09-26  
Authoritative parent: `52ac7f50c5476e063ee288f2cc80363634f3753d` (sealed MR06A runtime checkpoint)

## Decision

MR06B is **not** a standalone Encounter Chart menu.

The abandoned `feature/mr06a-encounter-chart-ui` experiment is not the production lineage. It added a general ENCOUNTERS row to the Start Menu and is deliberately excluded from this branch.

The encounter-chart export/runtime from MR05M/MR06A remains valid as an internal data/query layer and may be reused by the Poké Radar. It must not become an always-available general encounter browser.

## Player-facing system

Keep the Platinum item name **Poké Radar**, but modernize its behavior into Mercury's Research Poké Radar:

- use the Poké Radar item to enter the scanner;
- current-area land ecology can be read from the live MR06A encounter runtime;
- the scanner may also expose a fixed Research habitat layer for foreign/ordinary species;
- choose a species deliberately instead of relying on a shaking-patch lottery;
- targeted encounters are immediate;
- no chain is required;
- no 50-step battery/cooldown;
- no daily rotation;
- normal authored Mercury route encounters remain unchanged.

## Elite Redux DexNav adaptation

The player-facing scanner should deliberately feel like a **DS-native adaptation of Elite Redux's DexNav**, not like a text encounter list.

### Bottom screen — target browser

- show Pokémon icons in a compact grid instead of species names in a scrolling text list;
- separate **LOCAL** targets from the fixed **RESEARCH** habitat layer;
- LOCAL uses the current Morning / Day / Evening / Night land table;
- RESEARCH is Mercury's foreign/ordinary-species layer and replaces Elite Redux's hidden-species row concept;
- highlight the selected icon with a cursor and support both D-pad and touch input;
- show an owned/caught marker on species already captured;
- unknown Research targets may appear as silhouettes / question marks until discovered;
- **R** registers or unregisters the selected species as the quick-search target.

Surf and fishing do not become Radar rows.

### Top screen — selected species dossier

For the currently highlighted target, show:

- large species sprite and name;
- type icon(s);
- current-area level range;
- **SEARCH Lv.** / Research Level;
- caught/owned state;
- possible Primary Ability information;
- Potential shown as 0–3 stars;
- special Egg Move / rare move information as it becomes known;
- possible held item information;
- LOCAL or RESEARCH habitat badge.

Mercury's Innates remain controlled by the global Innate Abilities toggle and are not randomized by the Radar. The Radar rolls/displays the Pokémon's **Primary Ability** only.

### Searching in the overworld

Selecting **SEARCH** should:

1. validate that the species belongs to the current LOCAL or RESEARCH target set;
2. generate the target's level and bonus traits;
3. immediately locate a valid nearby grass tile;
4. create a visible rustling / research patch and return the player to the overworld;
5. show a short-lived search HUD with species icon, level, special move, ability/rare-ability marker, held item and Potential stars as unlocked by Search Level;
6. start the targeted battle when the player enters that patch.

"Immediate" means there is **no random chance that the selected target fails to appear and no real-time/daily wait**. It does not mean teleporting directly into battle.

If no valid grass tile exists nearby, fail cleanly with a short message rather than changing the normal encounter table.

### Search Level instead of required chains

Use a per-species **Search Level** (0–999) as the long-term progression mechanic, matching the useful part of DexNav while keeping Mercury's locked no-required-chain rule.

Search Level rises when the player successfully finds/battles that species through the Research Poké Radar. Milestones are:

- 0–4
- 5–9
- 10–24
- 25–49
- 50–99
- 100+

Higher Search Levels improve the odds of:

- a special Egg Move / compatible rare move;
- the rarer Primary Ability slot;
- held items;
- 1–3 guaranteed perfect IVs (Potential stars);
- a modest shiny bonus.

The Elite Redux-style chain counter is **not required** in Mercury. There is no chain break punishment, no 50-step battery, and no daily reset. Repeated searches still feel rewarding because Search Level permanently improves that species' Radar quality.

A captured species may reveal more information in the dossier than an uncaught species, preserving the discovery loop without blocking targeting.

## Explicit exclusions

The Research Poké Radar does **not** become a universal replacement for:

- Honey Trees;
- Surf encounters;
- fishing;
- Great Marsh habitat presentation;
- stationary/legendary encounters;
- gifts/trades;
- normal authored route encounter tables.

Mega, Gigantamax, Primal, and similar battle-only forms are never wild Radar targets.

## MR06B implementation gates

### MR06B1 — item/scanner foundation

- Branch from sealed MR06A, not the rejected Start Menu UI branch.
- Bind player-facing encounter browsing to **ITEM_POKE_RADAR only**.
- Land/current-area data comes from the live MR06A runtime.
- Keep special encounter systems out of the scanner.
- Compile cleanly and normal-boot.

### MR06B2 — Elite Redux-style scanner + targeted encounter runtime

- Build the DS-native icon-grid browser and selected-species dossier.
- Support D-pad + touch selection and R-button target registration.
- Selecting SEARCH generates the target and places a guaranteed nearby rustling grass patch.
- Return to the overworld with a compact search HUD; stepping into the patch starts the battle.
- Remove chain dependency, patch lottery failure, and 50-step recharge from Mercury Radar flow.
- Add per-species Search Level persistence and quality milestones.
- Generate/display level, Primary Ability, special move, held item and Potential stars according to Search Level.
- Preserve ordinary wild encounter tables and ordinary walking encounters.
- Validate species and level range against the selected current-area Radar entry.

### MR06B3 — fixed Research habitat layer

- Import the previously authored fixed Research Poké Radar habitat assignments.
- Keep this data separate from the normal route NARC so Research targets never overwrite ordinary ecology.
- No daily rotation.

### MR06B4 — research metadata/polish

- Polish Search Level unlock/reveal behavior and bonus probabilities.
- Add DS-native silhouettes / discovered / owned presentation.
- Add registered-species quick search.
- DS/Platinum-quality visual pass inspired by Elite Redux DexNav information density without copying its GBA graphics.
- Runtime screenshots and player ROM proof.

## Regression guards

A passing MR06B build must prove:

1. no `ENCOUNTERS` option is added to the normal Start Menu;
2. the Poké Radar is the only player-facing entry point for this scanner;
3. Honey Tree and Great Marsh systems remain independent;
4. Surf/fishing are not exposed as Radar targeting modes;
5. authored normal encounters are byte/manifest-equivalent to the sealed MR06A inputs unless a separately approved encounter change is made;
6. the player ROM still normal-boots in DeSmuME.
