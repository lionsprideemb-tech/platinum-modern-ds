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

Research progression can later reveal extra information such as possible ability, approximate IV quality, Egg Move/special move, held-item chance, and rare-form status.

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

### MR06B2 — targeted encounter runtime

- Selecting a valid target creates that encounter directly.
- Remove chain dependency, patch lottery, and 50-step recharge from Mercury Radar flow.
- Preserve ordinary wild encounter tables and ordinary walking encounters.
- Validate species and level range against the selected current-area Radar entry.

### MR06B3 — fixed Research habitat layer

- Import the previously authored fixed Research Poké Radar habitat assignments.
- Keep this data separate from the normal route NARC so Research targets never overwrite ordinary ecology.
- No daily rotation.

### MR06B4 — research metadata/polish

- Add progressive ability / IV-quality / Egg Move / held-item / rare-form hints.
- DS/Platinum-quality visual pass.
- Runtime screenshots and player ROM proof.

## Regression guards

A passing MR06B build must prove:

1. no `ENCOUNTERS` option is added to the normal Start Menu;
2. the Poké Radar is the only player-facing entry point for this scanner;
3. Honey Tree and Great Marsh systems remain independent;
4. Surf/fishing are not exposed as Radar targeting modes;
5. authored normal encounters are byte/manifest-equivalent to the sealed MR06A inputs unless a separately approved encounter change is made;
6. the player ROM still normal-boots in DeSmuME.
