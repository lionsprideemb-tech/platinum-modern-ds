# Mercury Redux Title Screen — Locked Implementation Spec

**Status:** IMPLEMENTING  
**Foundation:** Native Pokémon Platinum title-screen application

## Non-negotiable goal

The Mercury Redux title screen must look professionally authored at the same visual standard as vanilla Platinum. It must read immediately as a **Nintendo DS-era title screen**, not as a GBA ROM hack, upscaled GBA graphic, or pixel-art recreation.

### DS-native visual rules

- author at native DS title dimensions and layer structure
- use Platinum's 8bpp/4bpp indexed graphics pipeline rather than GBA-style tile art conventions
- preserve anti-aliased logo edges, gradients, bevels, transparency, and layered composition
- avoid chunky pixel fonts, thick block outlines, oversized badges, and low-detail flat fills
- preserve Platinum's native blinking prompt and title-screen animation logic
- any future title/UI graphics must be designed for DS first rather than drawn at GBA scale and enlarged
- runtime screenshots, not concept mockups, decide whether an asset looks sufficiently DS-native

## Behavior preserved exactly from Platinum

The title application remains Platinum's native `src/applications/title_screen.c` flow:

- original opening/title reveal timing
- original title BGM
- original fade timing
- original blinking `PRESS START`
- A / START advances normally
- B + UP + SELECT save-clear combination remains intact
- original inactivity/opening replay behavior remains intact
- original Giratina 3D lower-screen animation remains active for this first certified version
- original transition/blur behavior on Start remains intact

## Mercury visual identity

The first certified Mercury implementation deliberately follows Platinum's composition instead of replacing it with a full-screen illustration.

### Physical top screen
- authentic Pokémon wordmark retained as a DS-native anchor
- `PLATINUM VERSION` subtitle removed
- custom metallic `MERCURY` subtitle added
- smaller spaced `REDUX` wordmark beneath
- violet / indigo / platinum accent treatment
- Platinum's native frame geometry retained, recolored toward Mercury's cooler palette
- native blinking `PRESS START` stays a separate live layer

### Physical bottom screen
- Platinum Giratina animation retained during the title-screen certification phase
- this can later become a Mercury-specific legendary/custom animation without blocking the core game

## Why this architecture

Platinum already has a highly polished layered title application. Reusing its behavior and replacing only branded art preserves the professional DS presentation while making the game visibly ours.

This avoids flattening everything into a single image and preserves animation, blinking text, fades, input handling, and screen transitions.

## Build source of truth

`tools/generate_mercury_title.py` generates the Mercury-specific title graphics directly from the pinned native Platinum assets during CI.

That script:
1. preserves the authentic Pokémon wordmark,
2. removes the Platinum-specific subtitle,
3. renders `MERCURY REDUX` as a new DS-resolution title treatment,
4. recolors the existing title frame into Mercury's violet/platinum palette,
5. changes the native prompt colors to silver-violet.

## Acceptance gate

The title phase is certified only when a real DeSmuME capture from the built ROM visibly shows:

- Pokémon Mercury Redux branding on the physical top screen,
- a clean professional composition at 256×192,
- the separate native `PRESS START` prompt,
- the original lower-screen title animation,
- successful Start/A transition out of the title screen.

No concept-art mockup counts as certification.
