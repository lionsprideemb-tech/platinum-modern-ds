# DS01 Sprite Library Duplicate Audit

Status: ANALYSIS ONLY — no sprite assets were installed, replaced, recolored, or deleted.

## Summary

- Images scanned: **11365**
- Sprite candidates: **11365**
- Exact byte-duplicate groups: **4643**
- Exact rendered-pixel duplicate groups: **19**
- Palette/recolor candidate groups: **34**
- Near-visual duplicate groups (dHash <= 4): **67**
- Concept-name collision groups: **44**

### Classification

- **Exact byte duplicate**: identical encoded image bytes.
- **Exact pixel duplicate**: different files/encodings that render identically.
- **Palette/recolor candidate**: identical per-pixel color-pattern topology after palette labels are normalized, but different rendered RGB values.
- **Near visual duplicate**: same dimensions and perceptual dHash distance within the configured threshold, excluding exact/palette matches.
- **Concept collision**: normalized sprite naming points at the same concept across multiple distinct visuals or source buckets.

## Exact byte duplicates

### 1. scatterbug archipelago, scatterbug continental, scatterbug elegant, scatterbug fancy, scatterbug garden, scatterbug high plains, scatterbug icy snow, scatterbug jungle, scatterbug marine, scatterbug meadow, scatterbug modern, scatterbug monsoon, scatterbug ocean, scatterbug poke ball, scatterbug polar, scatterbug river, scatterbug sandstorm, scatterbug savanna, scatterbug sun, scatterbug tundra — 40 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-high-plains/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-high-plains/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-river/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-river/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-ocean/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-ocean/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-jungle/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-jungle/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-polar/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-polar/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-tundra/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-tundra/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-garden/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-garden/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-fancy/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-fancy/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-elegant/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-elegant/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-archipelago/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-archipelago/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-modern/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-modern/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-marine/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-marine/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-continental/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-continental/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-poke-ball/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-poke-ball/female/back.png`
- … 10 more

### 2. scatterbug archipelago, scatterbug continental, scatterbug elegant, scatterbug fancy, scatterbug garden, scatterbug high plains, scatterbug icy snow, scatterbug jungle, scatterbug marine, scatterbug meadow, scatterbug modern, scatterbug monsoon, scatterbug ocean, scatterbug poke ball, scatterbug polar, scatterbug river, scatterbug sandstorm, scatterbug savanna, scatterbug sun, scatterbug tundra — 40 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-high-plains/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-high-plains/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-river/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-river/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-ocean/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-ocean/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-jungle/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-jungle/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-polar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-polar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-tundra/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-tundra/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-garden/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-garden/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-fancy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-fancy/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-elegant/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-elegant/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-archipelago/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-archipelago/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-modern/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-modern/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-marine/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-marine/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-continental/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-continental/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-poke-ball/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-poke-ball/female/front.png`
- … 10 more

### 3. spewpa archipelago, spewpa continental, spewpa elegant, spewpa fancy, spewpa garden, spewpa high plains, spewpa icy snow, spewpa jungle, spewpa marine, spewpa meadow, spewpa modern, spewpa monsoon, spewpa ocean, spewpa poke ball, spewpa polar, spewpa river, spewpa sandstorm, spewpa savanna, spewpa sun, spewpa tundra — 40 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-marine/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-marine/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-archipelago/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-archipelago/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-icy-snow/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-icy-snow/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-tundra/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-tundra/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-garden/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-garden/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-fancy/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-fancy/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-jungle/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-jungle/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-river/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-river/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-continental/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-continental/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-modern/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-modern/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-ocean/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-ocean/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-savanna/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-savanna/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-polar/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-polar/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-poke-ball/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-poke-ball/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-sandstorm/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-sandstorm/female/back.png`
- … 10 more

### 4. spewpa archipelago, spewpa continental, spewpa elegant, spewpa fancy, spewpa garden, spewpa high plains, spewpa icy snow, spewpa jungle, spewpa marine, spewpa meadow, spewpa modern, spewpa monsoon, spewpa ocean, spewpa poke ball, spewpa polar, spewpa river, spewpa sandstorm, spewpa savanna, spewpa sun, spewpa tundra — 40 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-marine/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-marine/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-archipelago/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-archipelago/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-icy-snow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-icy-snow/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-tundra/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-tundra/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-garden/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-garden/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-fancy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-fancy/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-jungle/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-jungle/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-river/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-river/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-continental/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-continental/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-modern/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-modern/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-ocean/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-ocean/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-savanna/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-savanna/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-polar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-polar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-poke-ball/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-poke-ball/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-sandstorm/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-sandstorm/female/front.png`
- … 10 more

### 5. scatterbug archipelago, scatterbug continental, scatterbug elegant, scatterbug fancy, scatterbug garden, scatterbug high plains, scatterbug icy snow, scatterbug jungle, scatterbug marine, scatterbug meadow, scatterbug modern, scatterbug monsoon, scatterbug ocean, scatterbug poke ball, scatterbug polar, scatterbug river, scatterbug sandstorm, scatterbug savanna, scatterbug sun, scatterbug tundra — 20 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-high-plains/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-river/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-ocean/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-jungle/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-polar/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-tundra/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-garden/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-fancy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-elegant/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-archipelago/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-modern/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-marine/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-continental/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-poke-ball/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-icy-snow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-sun/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-sandstorm/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-monsoon/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-meadow/icon.png`

### 6. spewpa archipelago, spewpa continental, spewpa elegant, spewpa fancy, spewpa garden, spewpa high plains, spewpa icy snow, spewpa jungle, spewpa marine, spewpa meadow, spewpa modern, spewpa monsoon, spewpa ocean, spewpa poke ball, spewpa polar, spewpa river, spewpa sandstorm, spewpa savanna, spewpa sun, spewpa tundra — 20 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-marine/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-archipelago/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-icy-snow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-tundra/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-garden/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-fancy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-jungle/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-river/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-continental/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-modern/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-ocean/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-savanna/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-polar/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-poke-ball/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-sandstorm/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-high-plains/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-elegant/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-meadow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-monsoon/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-sun/icon.png`

### 7. silvally, silvally bug, silvally dark, silvally dragon, silvally electric, silvally fairy, silvally fighting, silvally fire, silvally flying, silvally ghost, silvally grass, silvally ground, silvally ice, silvally poison, silvally psychic, silvally rock, silvally steel, silvally water — 18 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fighting/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-water/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fairy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-electric/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-psychic/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-rock/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-flying/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/icon.png`

### 8. minior blue meteor, minior green meteor, minior indigo meteor, minior orange meteor, minior red meteor, minior violet meteor, minior yellow meteor — 14 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/female/back.png`

### 9. minior blue meteor, minior green meteor, minior indigo meteor, minior orange meteor, minior red meteor, minior violet meteor, minior yellow meteor — 14 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/female/front.png`

### 10. darkrai mega, heatran mega, slate, zeraora mega — 8 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/female/back.png`

### 11. darkrai mega, heatran mega, slate, zeraora mega — 8 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/female/front.png`

### 12. minior blue meteor, minior green meteor, minior indigo meteor, minior orange meteor, minior red meteor, minior violet meteor, minior yellow meteor — 7 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/icon.png`

### 13. mothim plant, mothim sandy, mothim trash — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/female/back.png`

### 14. mothim plant, mothim sandy, mothim trash — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/female/front.png`

### 15. ribombee bluetowel alternate form form 1, ribombee bluetowel alternate form form 2 — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/female/back.png`

### 16. ribombee bluetowel alternate form form 1, ribombee bluetowel alternate form form 2 — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/female/front.png`

### 17. darmanitan redux, darmanitan redux bond — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/female/back.png`

### 18. darmanitan redux, darmanitan redux bond — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/female/front.png`

### 19. genesect burn, genesect chill, genesect douse, genesect shock — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-shock/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-douse/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-burn/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-chill/icon.png`

### 20. gourgeist average, gourgeist large, gourgeist small, gourgeist super — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-small/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-large/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-super/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-average/icon.png`

### 21. greninja ash, greninja bond — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/female/back.png`

### 22. greninja ash, greninja bond — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/female/front.png`

### 23. pumpkaboo average, pumpkaboo large, pumpkaboo small, pumpkaboo super — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-average/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-small/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-super/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-large/icon.png`

### 24. rockruff, rockruff own tempo — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/female/back.png`

### 25. rockruff, rockruff own tempo — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/female/front.png`

### 26. toxtricity amped gmax, toxtricity low key gmax — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/back.png`

### 27. toxtricity amped gmax, toxtricity low key gmax — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/front.png`

### 28. zygarde 10, zygarde 10 power construct — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/female/back.png`

### 29. zygarde 10, zygarde 10 power construct — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/female/front.png`

### 30. zygarde 50, zygarde 50 power construct — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/female/back.png`

### 31. zygarde 50, zygarde 50 power construct — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/female/front.png`

### 32. mothim plant, mothim sandy, mothim trash — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/icon.png`

### 33. abomasnow mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/female/back.png`

### 34. abomasnow mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/female/front.png`

### 35. abomasnow — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/female/back.png`

### 36. abomasnow santa — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/female/back.png`

### 37. abomasnow santa — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/female/front.png`

### 38. abra — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/female/back.png`

### 39. abra — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/female/front.png`

### 40. abra redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/female/back.png`

### 41. abra redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/female/front.png`

### 42. absol mega z — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/female/back.png`

### 43. absol mega z — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/female/front.png`

### 44. absol mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/female/back.png`

### 45. absol mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/female/front.png`

### 46. absol — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/female/back.png`

### 47. absol — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/female/front.png`

### 48. absol mega z — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/female/back.png`

### 49. absol mega z — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/female/front.png`

### 50. abyssand — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/female/back.png`

### 51. abyssand — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/female/front.png`

### 52. accelgor — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/female/back.png`

### 53. accelgor — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/female/front.png`

### 54. aegislash blade — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/female/back.png`

### 55. aegislash blade — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/female/front.png`

### 56. aegislash shield — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/female/back.png`

### 57. aegislash shield — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/female/front.png`

### 58. aegislash blade redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/female/back.png`

### 59. aegislash blade redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/female/front.png`

### 60. aegislash blade redux mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/female/back.png`

### 61. aegislash blade redux mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/female/front.png`

### 62. aegislash redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/female/back.png`

### 63. aegislash redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/female/front.png`

### 64. aegislash redux mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/female/back.png`

### 65. aegislash redux mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/female/front.png`

### 66. aerodactyl mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/female/back.png`

### 67. aerodactyl mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/female/front.png`

### 68. aerodactyl — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/female/back.png`

### 69. aerodactyl — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/female/front.png`

### 70. aggron mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/female/back.png`

### 71. aggron mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/female/front.png`

### 72. aggron — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/female/back.png`

### 73. aggron — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/female/front.png`

### 74. aggron redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/female/back.png`

### 75. aggron redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/female/front.png`

### 76. aggron redux mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/female/back.png`

### 77. aggron redux mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/female/front.png`

### 78. alakazam mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/female/back.png`

### 79. alakazam mega — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/female/front.png`

### 80. alakazam mega redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/female/back.png`

### 81. alakazam mega redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/female/front.png`

### 82. alakazam redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/female/back.png`

### 83. alakazam redux — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/female/front.png`

### 84. alcremie caramel swirl berry sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/female/back.png`

### 85. alcremie caramel swirl berry sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/female/front.png`

### 86. alcremie caramel swirl clover sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/female/back.png`

### 87. alcremie caramel swirl clover sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/female/front.png`

### 88. alcremie caramel swirl flower sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/back.png`

### 89. alcremie caramel swirl flower sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/front.png`

### 90. alcremie caramel swirl love sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/female/back.png`

### 91. alcremie caramel swirl love sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/female/front.png`

### 92. alcremie caramel swirl ribbon sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/female/back.png`

### 93. alcremie caramel swirl ribbon sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/female/front.png`

### 94. alcremie caramel swirl star sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/female/back.png`

### 95. alcremie caramel swirl star sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/female/front.png`

### 96. alcremie caramel swirl strawberry sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/female/back.png`

### 97. alcremie caramel swirl strawberry sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/female/front.png`

### 98. alcremie gmax — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/female/back.png`

### 99. alcremie gmax — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/female/front.png`

### 100. alcremie lemon cream berry sweet — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-lemon-cream-berry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-lemon-cream-berry-sweet/female/back.png`

## Exact rendered-pixel duplicates

### 1. toxtricity amped gmax, toxtricity low key gmax, toxtricity mega — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/front.png`

### 2. alcremie matcha cream love sweet, alcremie ruby cream love sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/female/back.png`

### 3. alcremie matcha cream ribbon sweet, alcremie ruby cream ribbon sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/female/back.png`

### 4. alcremie mint cream ribbon sweet, alcremie salted cream ribbon sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/female/back.png`

### 5. alcremie matcha cream clover sweet, alcremie ruby cream clover sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/female/back.png`

### 6. alcremie matcha cream star sweet, alcremie ruby cream star sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/female/back.png`

### 7. alcremie caramel swirl flower sweet, alcremie ruby swirl flower sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/back.png`

### 8. alcremie mint cream love sweet, alcremie salted cream love sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/female/back.png`

### 9. charizard gmax, charizard mega z — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard_mega_z/female/front.png`

### 10. coalossal gmax, coalossal mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal-gmax/female/front.png`

### 11. drednaw gmax, drednaw mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw-gmax/female/front.png`

### 12. hatterene gmax, hatterene mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene_mega/female/front.png`

### 13. inteleon gmax, inteleon mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon-gmax/female/front.png`

### 14. latias mega, latios mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/female/front.png`

### 15. machamp gmax, machamp mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/female/front.png`

### 16. pikachu original cap, pikachu partner cap — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-partner-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-partner-cap/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-original-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-original-cap/female/back.png`

### 17. snorlax gmax, snorlax mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax-gmax/female/front.png`

### 18. urshifu mega, urshifu single strike gmax — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-single-strike-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-single-strike-gmax/female/front.png`

### 19. urshifu rapid strike gmax, urshifu rapid strike style mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_rapid_strike_style_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_rapid_strike_style_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-rapid-strike-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-rapid-strike-gmax/female/front.png`

## Palette / recolor candidates

### 1. darkrai mega, heatran mega, slate, zeraora mega — 16 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slate/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/female/back.png`

### 2. silvally, silvally dragon, silvally ghost, silvally steel — 8 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/female/back.png`

### 3. pikachu alola cap, pikachu kalos cap, pikachu world cap — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-kalos-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-kalos-cap/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-alola-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-alola-cap/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-world-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-world-cap/female/back.png`

### 4. silvally dark, silvally ice, silvally rock — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-rock/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-rock/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/female/back.png`

### 5. silvally bug, silvally ground, silvally poison — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/female/back.png`

### 6. silvally bug, silvally ground, silvally poison — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/female/front.png`

### 7. toxtricity amped gmax, toxtricity low key gmax, toxtricity mega — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/back.png`

### 8. alcremie matcha cream love sweet, alcremie ruby cream love sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/female/front.png`

### 9. alcremie matcha cream ribbon sweet, alcremie ruby cream ribbon sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/female/front.png`

### 10. alcremie matcha cream strawberry sweet, alcremie ruby cream strawberry sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-strawberry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-strawberry-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-strawberry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-strawberry-sweet/female/back.png`

### 11. alcremie mint cream ribbon sweet, alcremie salted cream ribbon sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/female/front.png`

### 12. alcremie matcha cream clover sweet, alcremie ruby cream clover sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/female/front.png`

### 13. alcremie matcha cream star sweet, alcremie ruby cream star sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/female/front.png`

### 14. alcremie caramel swirl flower sweet, alcremie ruby swirl flower sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/front.png`

### 15. alcremie mint cream love sweet, alcremie salted cream love sweet — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/female/front.png`

### 16. appletun gmax, flapple gmax — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/appletun-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/appletun-gmax/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flapple-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flapple-gmax/female/back.png`

### 17. flabebe blue, flabebe white — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-blue/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-blue/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-white/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-white/female/back.png`

### 18. floette blue, floette orange, floette red, floette yellow — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-orange/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-blue/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-red/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-yellow/icon.png`

### 19. lapras gmax, lapras mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras-gmax/female/front.png`

### 20. latias mega, latios mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/female/back.png`

### 21. minior blue, minior indigo, minior red, minior violet — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red/icon.png`

### 22. pikachu gmax, pikachu partner mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-gmax/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu_partner_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu_partner_mega/female/back.png`

### 23. poltchageist artisan, poltchageist counterfeit — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/poltchageist-counterfeit/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/poltchageist-counterfeit/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/poltchageist-artisan/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/poltchageist-artisan/female/back.png`

### 24. polteageist antique, polteageist phony — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/polteageist-antique/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/polteageist-antique/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/polteageist-phony/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/polteageist-phony/female/back.png`

### 25. silvally dragon, silvally steel — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/female/front.png`

### 26. silvally fire, silvally grass — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/female/back.png`

### 27. silvally fire, silvally grass — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/female/front.png`

### 28. silvally dark, silvally ice — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/female/front.png`

### 29. silvally, silvally ghost — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/female/front.png`

### 30. sinistea antique, sinistea phony — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sinistea-antique/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sinistea-antique/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sinistea-phony/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sinistea-phony/female/back.png`

### 31. minior green, minior orange, minior yellow — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange/icon.png`

### 32. flabebe blue, flabebe red — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-blue/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-red/icon.png`

### 33. frillish — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-male/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-female/icon.png`

### 34. pikachu hoenn cap, pikachu sinnoh cap — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-sinnoh-cap/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-hoenn-cap/icon.png`

## Near visual duplicates

### 1. abomasnow, abomasnow santa, abra, abra alternate form 1, abra alternate form 2, abra redux, absol, absol alternate form 2, absol alternate mega form 3, absol mega, absol mega z, abyssand, accelgor, accelgor alternate form 1, aegislash blade, aegislash blade redux, aegislash redux, aegislash redux mega, aegislash shield, aerodactyl, aerodactyl mega, aggron, aggron mega, aggron redux, aggron redux mega, aipom, alakazam, alakazam mega, alakazam mega redux, alakazam redux, alcremie caramel swirl berry sweet, alcremie caramel swirl clover sweet, alcremie caramel swirl flower sweet, alcremie caramel swirl love sweet, alcremie caramel swirl ribbon sweet, alcremie caramel swirl star sweet, alcremie caramel swirl strawberry sweet, alcremie gmax, alcremie lemon cream berry sweet, alcremie lemon cream clover sweet, alcremie lemon cream flower sweet, alcremie lemon cream love sweet, alcremie lemon cream ribbon sweet, alcremie lemon cream star sweet, alcremie lemon cream strawberry sweet, alcremie matcha cream berry sweet, alcremie matcha cream clover sweet, alcremie matcha cream flower sweet, alcremie matcha cream love sweet, alcremie matcha cream ribbon sweet, alcremie matcha cream star sweet, alcremie matcha cream strawberry sweet, alcremie mega, alcremie mint cream berry sweet, alcremie mint cream clover sweet, alcremie mint cream flower sweet, alcremie mint cream love sweet, alcremie mint cream ribbon sweet, alcremie mint cream star sweet, alcremie mint cream strawberry sweet, alcremie rainbow swirl berry sweet, alcremie rainbow swirl clover sweet, alcremie rainbow swirl flower sweet, alcremie rainbow swirl love sweet, alcremie rainbow swirl ribbon sweet, alcremie rainbow swirl star sweet, alcremie rainbow swirl strawberry sweet, alcremie ruby cream berry sweet, alcremie ruby cream clover sweet, alcremie ruby cream flower sweet, alcremie ruby cream love sweet, alcremie ruby cream ribbon sweet, alcremie ruby cream star sweet, alcremie ruby cream strawberry sweet, alcremie ruby swirl berry sweet, alcremie ruby swirl clover sweet, alcremie ruby swirl flower sweet, alcremie ruby swirl love sweet, alcremie ruby swirl ribbon sweet, alcremie ruby swirl star sweet, alcremie ruby swirl strawberry sweet, alcremie salted cream berry sweet, alcremie salted cream clover sweet, alcremie salted cream flower sweet, alcremie salted cream love sweet, alcremie salted cream ribbon sweet, alcremie salted cream star sweet, alcremie salted cream strawberry sweet, alcremie vanilla cream berry sweet, alcremie vanilla cream clover sweet, alcremie vanilla cream flower sweet, alcremie vanilla cream love sweet, alcremie vanilla cream ribbon sweet, alcremie vanilla cream star sweet, alcremie vanilla cream strawberry sweet, alomomola, altaria, altaria alternate form 2, altaria mega, altaria redux, amaura, amaura alternate form 1, ambipom, amoonguss, ampharos, ampharos alternate form 2, ampharos mega, amphybuzz, amphybuzz mega, annihilape, anorith, anorith alternate form 1, appletun, appletun gmax, applin, arachtres, araquanid, arashinne, arbok, arbok mega, arboliva, arcanine, arcanine hisui, arcanine hisui mega, arcanine mega, arcanine mega redux, arceus, arceus bug, arceus dark, arceus dragon, arceus electric, arceus fairy, arceus fighting, arceus fire, arceus flying, arceus ghost, arceus grass, arceus ground, arceus ice, arceus poison, arceus psychic, arceus rock, arceus steel, arceus unknown, arceus water, archaludon, archen, archen alternate form 1, archeops, arctibax, arctovish, arctozolt, ariados, armaldo, armaldo alternate form 1, armarouge, aromatisse, aromatisse alternate form 1, aromatisse alternate form 2, aron, aron redux, arrokuda, arrokuda alternate form 1, articuno, articuno ex, articuno ex mega, articuno galar, audino, audino mega, aurorus alternate form 1, avalugg, avalugg hisui, axew, azelf, azelf redux, azumarill, azurill, bagon, bagon alternate form 2, baltoy, baltoy alternate form 1, banette, banette mega, barbaracle, barbaracle mega, barboach, bariong, barraskewda, barraskewda alternate form 1, basculegion, basculin blue striped, basculin red striped, basculin white striped, bastiodon, bastiodon alternate form 1, baxcalibur, baxcalibur mega, bayleef, bayleef bluetowel alternate form form 1, beartic, beautifly, beedrill, beedrill alternate form 2, beedrill alternate mega form 3, beedrill mega, beedrill redux, beefender, beheeyem, beldum, beldum alternate form 2, bellibolt, bellossom, bellsprout, bellsprout redux, beniccino, bergmite, bewarden, bewarden redux, bewear, bewear angry, bewear redux, bibarel, bidoof, binacle, bisharp, bisharp alternate form 1, bisharp redux, blacephalon, blastoise, blastoise gmax, blastoise mega, blastoise mega x, blaziken, blaziken alternate mega form 2, blaziken alternate mega form 3, blaziken mega, blipbug, blissey, blissey alternate form 1, blissey redux, blitzle, blizzard maw, blocli, bloxtack, boarlock, boldore, boldore alternate form 1, boltund, bombirdier, bonsly, bouffalant, bounsweet, bounsweet redux, braixen, brambleghast, bramblin, braviary, braviary hisui, breezing, breloom, breloom alternate form 2, breloom alternate form 3, breloom mega, brionne, brontonana, bronzong, bronzor, brute bonnet, bruxish, bubbleo, budew, buizel, buizel redux, bulbasaur, buneary, buneary alternate form 2, bunnelby, bunnelby alternate form 1, burmy plant, burmy sandy, burmy trash, butterfree, butterfree alternate form 1, butterfree gmax, butterfree mega, buzzwole, cacjack, cacnea, cacturne, calyrex, calyrex cloud rider, calyrex ice, calyrex shadow, camerupt, camerupt alternate form 3, camerupt mega, camerupt mega alternate form 4, capsakid, carbink, carbonix, carbonix mega, carkol, carnivine, carnivine bluetowel alternate form form 1, carracosta, carracosta alternate form 1, carvanha, cascoon, cascoon primal, castform, castform foggy, castform rainy, castform sandy, castform snowy, castform sunny, caterpie, caterpie alternate form 1, celebi, celesteela, centiskorch, centiskorch gmax, centiskorch mega, ceruledge, cetitan, cetitan redux, cetoddle, cetoddle redux, chandelure, chandelure alternate form 1, chandelure mega, chandelure mega y, chandelure redux, chandelure redux mega, chansey, chansey alternate form 1, chansey redux, charcadet, charizard, charizard gmax, charizard mega x, charizard mega y, charizard mega z, charjabug, charmander, charmeleon, chatot, cherrim overcast, cherrim sunshine, cherubi, chesnaught, chesnaught bond, chesnaught mega, chespin, chewtle, chi yu, chien pao, chien pao mega, chikorita, chimchar, chimchar redux, chimecho, chimecho alternate form 1, chimecho mega, chinchou, chingling, chingling alternate form 1, cinccino, cinccino redux, cinderace, cinderace alternate form 2, cinderace gmax, cinderace mega, clamperl, clauncher, clauncher alternate form 1, clawitzer, clawitzer redux, claydol, claydol alternate form 1, clefable, clefable alternate form 1, clefable mega, clefable mega y, clefable redux, clefable redux mega, clefairy, clefairy alternate form 1, clefairy redux, cleffa, cleffa redux, clobbopus, clodsire, clodsire mega, cloyster, coalossal, coalossal gmax, coalossal mega, cobalion, cofagrigus, cofagrigus alternate form 1, combee, combee alternate form 1, combusken, combusken alternate form 2, comfey, conkeldurr, copperajah, copperajah gmax, copperajah mega, corm, cormoth, cormoth mega, corphish, corsola, corsola alternate form 1, corsola galar, corviknight, corviknight gmax, corviknight mega, corvisquire, cosmoem, cosmog, cottonee, crabominable, crabominable redux, crabrawler, crabrawler redux, crabruiser redux, cradily, cradily alternate form 1, cramorant, cramorant gorging, cramorant gulping, cranidos, cranidos alternate form 1, crawdaunt, crawdauntles, cresselia, croagunk, crobat, crobat mega, crocalor, croconaw, croconaw alternate form 1, crustle, crustle alternate form 1, cryogonal, cryogonal alternate form 1, cubchoo, cubone, cufant, cursola, cutiefly, cyclizar, cyndaquil, dachsbun, darkrai, darkrai mega, darkrai nightmare, darmanitan galar standard, darmanitan galar zen, darmanitan redux, darmanitan redux aura, darmanitan redux blunder, darmanitan redux bond, darmanitan standard, darmanitan zen, dartrix, dartrix alternate form 1, dartrix alternate form 2, darumaka, darumaka galar, darumaka redux, decidueye, decidueye alternate form 1, decidueye alternate form 2, decidueye hisui, decidueye hisui mega, decidueye mega, dedelibird, dedenne, dedenne alternate form 1, deerling autumn, deerling spring, deerling summer, deerling winter, deino, deino cybertank form 1, deino redux, deino telepathic form 2, delcatty, delcatty alternate form 1, delibird, delphox, delphox alternate form 1, delphox bond, delphox mega, delphox serena, deoxys, deoxys attack, deoxys defense, dewgong, dewgong mega, dewgong redux, dewott, dewpider, dewpider alternate form 1, dewpider redux, dhelmise, dialga, dialga origin, diancie, diancie mega, diggersby, diglett, diglett alola, dipplin, ditto, dodrio, dodrio redux, doduo, doduo alternate form 1, doduo redux, dolliv, dondozo, donphan, donphan alternate form 1, dottler, doublade redux, dracovish, dracozolt, dragalge, dragalge mega, dragapult, dragapult mega, dragonair, dragonite, dragonite alternate form 1, dragonite delivery, dragonite mega, dragonite mega y, drakloak, drampa mega, drapion, dratini, dreadnaut, drednaw, drednaw gmax, drednaw mega, dredwood, dreepy, drifblim, drifloon, drilbur, drilbur redux, drizzile, drizzile alternate form 2, drowzee, drowzee alternate form 2, druddigon, druddigon alternate form 1, dubwool, ducklett, dududunsparce, dududunsparce mega, dudunsparce three segment, dudunsparce two segment, duelumber, dugtrio, dugtrio alola, dunsparce, dunsparce bt alt forms draco form 6, dunsparce bt alt forms earth form 2, dunsparce bt alt forms insect form 4, dunsparce bt alt forms sky form 3, dunsparce bt alt forms spooky form 5, dunsparce bt alt forms toxic form 1, duosion, duosion alternate form 1, duosion redux, duraludon, duraludon gmax, durant, durant bluetowel alternate form form 1, dusclops, dusclops alternate form 1, dusknoir, dusknoir alternate form 1, duskull, dustox, dwebble, dwebble alternate form 1, earthretha apprensith, earthretha belstatue, earthretha belstatue 1, earthretha belstatue 2, earthretha bombghost, earthretha bunninja, earthretha cubchestra, earthretha gloom 1, earthretha gorochu, earthretha incineroar 1, earthretha keenstar, earthretha mimiegg, earthretha museon, earthretha oddish 1, earthretha pangshi, earthretha seegel, earthretha sithwitch, earthretha thiefire, earthretha thunphony, earthretha treesmas, earthretha venonat 1, earthretha vileplume 1, eelektrik, eelektrik alternate form 1, eelektross, eelektross mega, eevee, eevee gmax, eevee partner mega, eevee starter, eiscue ice, eiscue noice, ekans, eldegoss, electabuzz, electabuzz alternate form 1, electivire, electivire alternate form 1, electrike, electrike alternate form 2, electrode, electrode hisui, elekid, elgyem, emboar, emboar mega, emolga, empoleon, empoleon alternate form 1, empoleon mega, empoleon redux, empoleon redux mega, enamorus incarnate, enamorus therian, entei, eraticate, escarginite, escarginite redux, escavalier, escavalier alternate form 1, espathra, espeon, espeon alternate form 3, espeon galaxy, espurr, eternatus, eternatus eternamax, excadrill, excadrill mega, excadrill redux, exeggcute, exeggcute redux, exeggutor, exeggutor alola, exeggutor redux, exploud, exploud redux, falinks, falinks mega, farfetch d alternate form 1, farfetchd, farfetchd galar, farigiraf, fearow, fearow redux, feebas, fennekin, feraligatr, feraligatr mega, feraligatr mega x, feraligatr mega y, ferroseed, ferroseed alternate form 1, ferrothorn, fezandipiti, fidough, finizen, finneon, flaaffy, flaaffy alternate form 2, flabebe blue, flabebe orange, flabebe red, flabebe white, flabebe yellow, flairgrance, flamigo, flapple, flapple gmax, flareon, flareon alternate form 3, fletchinder, fletchling, flittle, floatzel, floatzel redux, floette blue, floette eternal, floette eternal flower mega, floette mega, floette orange, floette red, floette white, floette yellow, floragato, florges blue, florges orange, florges red, florges white, florges yellow, fluffbee, flutter mane, flygon, flygon mega, flygon redux, flygon redux b, flygon redux b mega, flygon redux mega, fogging, fomantis, fomantis alternate form 1, foongus, forretress, fraxure, frigibax, frillish, froakie, frogadier, froslass, froslass mega, froslass mega y, froslass redux, frosmoth, frostuccino, frostula, fuecoco, fujiflap, furfrou dandy, furfrou debutante, furfrou diamond, furfrou heart, furfrou kabuki, furfrou la reine, furfrou matron, furfrou natural, furfrou pharaoh, furfrou star, furret, gabite, gabite bluetowel alternate forms form 2, gabite redux, gallade, gallade mega, gallade redux, gallade redux mega, galvantula, garbodor, garbodor alternate form 1, garbodor gmax, garbodor mega, garchomp, garchomp alternate form 2, garchomp alternate mega form 3, garchomp bluetowel alternate forms form 1, garchomp mega, garchomp mega z, garchomp redux, gardevoir, gardevoir mega, gardevoir redux, gardevoir redux mega, gargablox, garganacl, gastly, gastly alternate form 2, gastrodon east, gastrodon west, genesect, genesect burn, genesect chill, genesect douse, genesect shock, gengar, gengar alternate form 2, gengar gmax, gengar mega, gengar mega x, geodude, geodude alola, geodude bluetowel alternate forms form 2, gholdengo, gible, gible bluetowel alternate forms form 2, gible redux, gigalith, gimmighoul chest, gimmighoul roaming, girafarig, girafarig bluetowel alternate form form 1, giratina altered, giratina origin, glaceon, glaceon alternate form 3, glalie, glalie mega, glalie redux, glalie redux mega, glameow, glameow alternate form 1, glastrier, gligar, gligar alternate form 1, gligar redux, glimmet, glimmora, glimmora mega, gliscor, gliscor alternate form 1, gliscor redux, gloom, gogoat, golbat, goldeen, golduck, golem, golem alola, golem bluetowel alternate forms form 2, golett, golett alternate form 1, golisopod, golisopod mega, golisopod mega y, golurk, golurk alternate form 1, golurk mega, goodra, goodra alternate form 1, goodra alternate form 2, goodra hisui, goodra hisui mega, goodra mega, goomy, goomy alternate form 1, gooschase, gorebyss, gossifleur, gothita, gothitelle, gothitelle mega, gothorita, gouging fire, gourgeist average, gourgeist large, gourgeist small, gourgeist super, grafaiai, granbull, granbull alternate form 1, granbull mega, granitun, grapploct, graveler, graveler alola, graveler bluetowel alternate forms form 2, great tusk, greavard, greedent, greninja, greninja ash, greninja bond, greninja mega, grimer, grimer alola, grimmsnarl, grimmsnarl gmax, grimmsnarl mega, grookey, grotle, grotle redux, grotom, grotom drum, grotom fill, grotom glass, grotom kick, grotom roll, groudon, groudon primal, grovyle, grovyle alternate form 2, growlithe, growlithe hisui, growlithe redux, grubbin, grumpig, grumpig alternate form 1, guardozel, gulpin, gumshoos, gurdurr, guzzlord, gyaradeath, gyaradeath mega x, gyaradeath mega y, gyarados, gyarados mega y, gyarevalry, hakamo o, hakamo o alternate form 1, happiny, happiny redux, hariyama, hariyama mega, hariyama redux, harvesting tyrant, hatenna, hatterene, hatterene gmax, hatterene mega, hattrem, haunter, haunter alternate form 2, hawlucha, hawlucha mega, haxorus, haxorus mega, heatmor, heatran, heatran mega, heliolisk, helioptile, heliosunny, heracreus, heracreus mega, heracross, heracross mega, herdier, hippopotas, hippopotato, hippotaton, hippowdon, hitmonchan, hitmonchan alternate form 1, hitmonchan mega, hitmonlee, hitmonlee alternate form 1, hitmonlee mega, hitmontop, hitmontop alternate form 1, hitmontop mega, ho oh, honchkrow, honedge, hoopa, hoopa unbound, hoothoot, hoothoot alternate form 1, hoppip, horsea, houndoom, houndoom mega, houndoom mega redux, houndoom redux, houndour, houndour redux, houndstone, huntail, hydrapple, hydreigon, hydreigon mega, hydreigon redux, hydreigon redux mega, hydroar, hypno, hypno alternate form 2, hypnocroak, igglybuff, illumise, impidimp, incineroar, incineroar alternate form 1, incineroar mega, indeedee, infernape, infernape mega, infernape redux, infernape redux mega, inkay, inteleon, inteleon alternate form 2, inteleon gmax, inteleon mega, iron boulder, iron bundle, iron crown, iron hands, iron jugulis, iron leaves, iron moth, iron thorns, iron treads, iron valiant, ivysaur, jagged chungulis, jangmo o, jellicent, jigglypuff, jigglypuff alternate form 1, jirachi, jolteon, jolteon alternate form 3, joltik, jumpluff, jynx, kabuto, kabuto alternate form 1, kabutops, kadabra, kadabra alternate form 2, kadabra redux, kaiosea, kakuna, kakuna alternate form 2, kakuna redux, kangaskhan, kangaskhan mega, karrablast, kartana, kartana fallen, kecleon, kecleong, keldeo ordinary, keldeo resolute, kilowattrel, kilozuna, kilozuna mega, kingambit, kingambit redux, kingambit redux mega, kingdra, kingdra mega, kingler, kingler gmax, kingler mega, kingler redux, kingler redux mega, kipmodo, kirlia, kirlia alternate form 3, kirlia redux, klang, klang alternate form 1, klawf, kleavor, kleavor mega, kleavor redux, kleavor redux mega, klefki, klefki redux, klink, klinklang, klinklang alternate form 1, koffing, koffing bluetowel alternate forms form 2, komala, kommo o, koraidon apex build, krabby, krabby alternate form 2, krabby redux, krampird, kricketot, kricketune, krokorok, krokorok alternate form 1, krookodile, krookodile mega, kubfu, kyogre, kyogre primal, kyurem, kyurem black, lairon, lairon redux, lampent, lampent alternate form 1, lampent redux, landorus incarnate, landorus therian, lanturn, lanturn mega, lapras, lapras gmax, lapras mega, lapras mega x, larvesta, larvesta redux, larvitar, larvitar ice form 2, larvitar redux, larvitar space form 4, latias, latias mega, latios, latios mega, leafeon, leafeon alternate form 3, leavanny, lechonk, ledian, ledian alternate form 1, ledyba, ledyba alternate form 1, lepastry, lickilicky, lickitung, liepard, liepard alternate form 1, lileep, lileep alternate form 1, lilligant, lilligant alternate form 1, lilligant alternate form 2, lilligant hisui, lillipup, linoone, linoone galar, litleo, litten, litwick, litwick alternate form 1, litwick redux, lokix, lombre, lopunny, lopunny alternate form 2, lopunny alternate mega form 3, lopunny bluetowel alternate forms form 1, lopunny mega, lotad, loudred, loudred redux, lucario, lucario mega, lucario mega z, ludicolo, lugia, lumbering sloth, lumbering sloth engulfed, lumineon, luminositeon, lunatone, lurantis, lurantis alternate form 1, luvdisc, luxio, luxio redux, luxray, luxray mega, luxray redux, luxray redux mega, luxzero, luxzero mega, lycanroc dusk, lycanroc eclipse, lycanroc midday, lycanroc midnight, lycanroc twilight, mabosstiff, machamp, machamp gmax, machamp mega, machamp mega redux, machamp redux, machoke, machoke redux, machop, machop redux, magby, magcargo, magcargo redux, magearna, magearna mega, magearna original, magikarp, magikarp alternate form 2, magmar, magmar alternate form 1, magmenous, magmortar, magnemite, magneton, magnezone, magnezone mega, makuhita, makuhita redux, malamar, malamar mega, mamoswine, mamoswine redux, mamoswine redux mega, manaphy, mandibuzz, manectric, manectric alternate form 2, manectric mega, manectric mega alternate form 3, mankey, mantine, mantyke, maractus, marbeep, mareanie, mareep, marill, marowak, marowak alola, marshadow, marshmodo, marshtomp, maschiff, maushold family of four, maushold family of three, mawile, mawile mega, mawile mega redux, mawile redux, mawile redux b, mawile redux b mega, medicham, medicham mega, meditite, mega dusknoir, mega electivire, mega froslass, mega honchkrow, mega infernape, mega magmortar, mega mamoswine, mega porygon, mega roserade, mega spiritomb, mega tangrowth, mega weavile, mega yanmega, meganium, meganium alternate form 1, meganium mega, melmetal, melmetal gmax, melmetal mega, meloetta aria, meloetta pirouette, meltan, meowscarada, meowscarada mega, meowstic, meowstic mega, meowth, meowth alola, meowth galar, meowth gmax, meowth partner, meowth partner mega, merrykarp, mesprit, mesprit redux, metagross, metagross mega, metang, metang alternate form 2, metapod, mew, mewtwo, mewtwo mega x, mewtwo mega y, mienfoo, mienfoo bluetowel alternate form form 1, mienshao, mienshao mega, mightyena, mightyena alternate form 1, milcery, milotic, milotic mega, miltank, mime jr, mimikyu apex, mimikyu apex busted, mimikyu busted, mimikyu disguised, mimikyu rayquaza, mimikyu rayquaza busted, minccino, minccino redux, minior blue, minior blue meteor, minior green, minior green meteor, minior indigo, minior indigo meteor, minior orange, minior orange meteor, minior red, minior red meteor, minior violet, minior violet meteor, minior yellow, minior yellow meteor, minun, miraidon ultimate mode, misdreavus, misdreavus alternate form 2, mismagius, mismagius alternate form 2, moltres, moltres ex, moltres ex mega, moltres galar, monferno, monferno redux, morelull, morgrem, morpeko full belly, morpeko hangry, morpekyll, morpekyll hangry, mothim plant, mothim sandy, mothim trash, mr mime, mr mime galar, mr rime, mudbray, mudkip, mudsdale, muk, muk alola, munchlax, munchlax redux, munkidori, munna, munna alternate form 1, murkrow, musharna, musharna alternate form 1, nacli, naclstack, naganadel, natu, natu alternate form 1, necrozma, necrozma dawn, necrozma ultra, nickit, nidoking, nidoking mega, nidoqueen, nidoqueen mega, nidoran, nidorina, nidorino, nihilego, nincada, ninetales, ninetales alola, ninetales alternate form 2, ninetales alternate form 3, ninjask, noctowl, noctowl alternate form 1, noibat, noibat alternate form 1, noibat redux, noivern, noivern redux, nosepass, nosepass alternate form 1, numel, numel alternate form 3, nuzleaf, nymble, obstagoon, octillery, octillery alternate form 1, oddish, ogerpon, ogerpon cornerstone mask, ogerpon hearthflame mask, ogerpon wellspring mask, oinkologne, okidogi, omanyte, omanyte alternate form 1, omastar, omastar alternate form 1, oranguru, orbeetle, orbeetle gmax, orbeetle mega, orchestot, oricorio baile, oricorio mega, oricorio pau, oricorio pom pom, oricorio sensu, orthworm, oshawott, overqwil, pachirisu, pachirisu alternate form 1, palafin hero, palafin zero, palkia, palkia origin, palossand, palossand alternate form 1, palpitoad, pancham, pangoro, panpour, panpour redux, pansage, pansage redux, pansear, pansear redux, paras, paras alternate form 1, parasect, parasect alternate form 1, passimian, patrat, pawmi, pawmo, pawmot, pawniard, pawniard alternate form 1, pawniard redux, pecharunt, pelipper, pentadug, pentadug alola, pentawug, perrserker, persian, persian alola, petilil, petilil alternate form 1, petilil alternate form 2, phanfernal, phanpy, phanpy alternate form 1, phantowl, phantump, pheromosa, phione, pichu, pichu spiky eared, pidgeot, pidgeot alternate form 2, pidgeot mega, pidgeotto, pidgeotto alternate form 2, pidgey, pidgey alternate form 2, pidove, pidove alternate form 1, pignite, pignite alternate form 1, pikachu, pikachu alola cap, pikachu belle, pikachu cosplay, pikachu gmax, pikachu hoenn cap, pikachu kalos cap, pikachu libre, pikachu original cap, pikachu partner cap, pikachu partner mega, pikachu phd, pikachu pop star, pikachu rock star, pikachu sinnoh cap, pikachu unova cap, pikachu world cap, pikipek, piloswine, piloswine redux, pincurchin, pineco, pinsir, pinsir mega, piplup, piplup redux, plundertow, plusle, poipole, polartic, polartic bluemoon, politoed, politoed alternate form 1, poliwag, poliwag alternate form 1, poliwhirl, poliwhirl alternate form 1, poliwrath, poltchageist artisan, poltchageist counterfeit, polteageist antique, polteageist phony, polteageist redux, ponyta, ponyta alternate form 1, ponyta galar, poochyena, popcorm, popcorm mega, popplio, porygon, porygon z, porygon2, primarina, primarina mega, primeape, prinplup, prinplup redux, probopass, probopass alternate form 1, psyduck, psyduck redux, pumpkaboo average, pumpkaboo large, pumpkaboo small, pumpkaboo super, pupitar, pupitar ice form 2, pupitar redux, pupitar space form 4, purrloin, purrloin alternate form 1, purugly, purugly alternate form 1, pyroar, pyroar mega, pyukumuku, quagsire, quagsire alternate form 1, quagsire mega, quaquaval, quaquaval mega, quaxly, quaxwell, queengambit, quilava, quilava alternate form 1, quilladin, qwilfish, qwilfish hisui, raboot, raboot alternate form 2, rabsca, raging bolt, raichu, raichu alola, raichu mega x, raichu mega y, raikou, ralts, ralts alternate form 3, ralts redux, rampardos, rampardos alternate form 1, rapidash, rapidash galar, rapidash mega, ratfioso, raticate, raticate alola, raticate redux, ratiking, rattata, rattata alola, rattata redux, rayquaza, rayquaza mega, regice, regidrago, regieleki, regigigas, regirock, registeel, relicanth, relicanth mega, rellor, remoraid, remoraid alternate form 1, reshiram, reuniclus, reuniclus alternate form 1, reuniclus mega, reuniclus redux, reuniclus redux mega, revavroom, rexcadrill, rhydon, rhyhorn, rhyperior, ribombee, ribombee bluetowel alternate form form 1, ribombee bluetowel alternate form form 2, ribombee mega, ribombee redux, ribombee redux mega, rillaboom, rillaboom gmax, rillaboom mega, riolu, roaring moon, rockruff, rockruff own tempo, roggenrola, roggenrola alternate form 1, rolycoly, rookidee, roselia, roserade, roserade mega, rotom, rotom fan, rotom frost, rotom heat, rotom mow, rotom wash, rowlet, rufflet, runerigus, sableye, sableye alternate darkness form 4, sableye alternate darkness mega form 5, sableye alternate gemstone form 2, sableye alternate gemstone mega form 3, sableye mega, sableye mega redux, sableye redux, sagaracas, salamence, salamence alternate form 1, salamence alternate mega form 3, salamence mega, salandit, salazarus, salazzle, samurott, samurott bluetowel alternate form form 1, samurott bluetowel alternate form form 2, samurott hisui, samurott hisui mega, samurott mega, sandaconda, sandaconda gmax, sandaconda mega, sandile, sandile alternate form 1, sandshrew, sandshrew alola, sandslash, sandslash alola, sandslash alola mega, sandslash mega, sandy shocks, sandygast, sandygast alternate form 1, sawk, sawk redux, sawsbuck autumn, sawsbuck spring, sawsbuck summer, sawsbuck winter, scatterbug archipelago, scatterbug continental, scatterbug elegant, scatterbug fancy, scatterbug garden, scatterbug high plains, scatterbug icy snow, scatterbug jungle, scatterbug marine, scatterbug meadow, scatterbug modern, scatterbug monsoon, scatterbug ocean, scatterbug poke ball, scatterbug polar, scatterbug river, scatterbug sandstorm, scatterbug savanna, scatterbug sun, scatterbug tundra, sceptile, sceptile alternate form 2, sceptile mega, scizor, scizor mega, scizor redux, scizor redux mega, scolipede, scolipede mega, scorbunny, scorbunny alternate form 2, scovillain, scovillain mega, scrafster, scrafty, scrafty mega, scraggy, scream tail, scyther, scyther mega, scyther redux, scyther redux mega, seadra, seaking, sealeo, seedot, seel, seel redux, seerkat, seismitoad, selenumbra, sentret, serperior, serperior mega, servine, seviper, sewaddle, sharpedo, sharpedo mega, shaymin land, shaymin sky, shedinja, shedinja mega, shelgon, shelgon alternate form 2, shellder, shellos east, shellos west, shelmet, shieldon, shieldon alternate form 1, shiftry, shiinotic, shinx, shinx redux, shroodle, shroomish, shuckle, shuckle mega, shuppet, shyduck, sigilyph, silcoon, silicobra, silvally, silvally bug, silvally dark, silvally dragon, silvally electric, silvally fairy, silvally fighting, silvally fire, silvally flying, silvally ghost, silvally grass, silvally ground, silvally ice, silvally poison, silvally psychic, silvally rock, silvally steel, silvally water, simipour, simipour redux, simisage, simisage redux, simisear, simisear redux, sinistcha masterpiece, sinistcha unremarkable, sinistea antique, sinistea phony, sinistea redux, sirfetchd, sizzlipede, skarmory, skarmory mega, skarmory mega y, skarmory redux, skeledirge, skeledirge mega, skiddo, skiploom, skitty, skitty alternate form 1, skorupi, skorupi alternate form 1, skorupi alternate form 2, skrelp, skrelp alternate form 1, skulberus, skuntank, skwovet, slaking, slaking mega, slaking mega ape shift, slakoth, slate, sliggoo, sliggoo alternate form 1, sliggoo alternate form 2, sliggoo hisui, slither wing, slowbro, slowbro bluetowel alternate forms form 2, slowbro bluetowel alternate forms form 4, slowbro bluetowel alternate forms form 5, slowbro galar, slowbro mega, slowbro mega alt form form 3, slowbro mega galar, slowking, slowking bluetowel alternate forms form 2, slowking galar, slowking mega, slowking mega galar, slowpoke, slowpoke galar, slugma, slugma redux, slurpuff, slyduck, smeargle, smoliv, smoochum, sneasel, sneasel alternate form 1, sneasel alternate form 2, sneasel hisui, sneasler, sneasler mega, snivy, snom, snorlax, snorlax gmax, snorlax mega, snorlax primal, snorlax redux, snorlax redux mega, snorunt, snorunt redux, snover, snubbull, snubbull alternate form 1, sobble, sobble alternate form 2, solgaleo, solosis, solosis alternate form 1, solosis redux, solrock, solrock system, sopranice, spearow, spearow redux, spectrier, spectrier cloud, spewpa archipelago, spewpa continental, spewpa elegant, spewpa fancy, spewpa garden, spewpa high plains, spewpa icy snow, spewpa jungle, spewpa marine, spewpa meadow, spewpa modern, spewpa monsoon, spewpa ocean, spewpa poke ball, spewpa polar, spewpa river, spewpa sandstorm, spewpa savanna, spewpa sun, spewpa tundra, spheal, spidops, spinarak, spinda, spindaze, spiritomb, spiritomb alternate form 1, spiritomb redux, spoink, sprigatito, spritzee, spritzee alternate form 1, spritzee alternate form 2, squawkabilly blue plumage, squawkabilly green plumage, squawkabilly white plumage, squawkabilly yellow plumage, squirtle, stakataka, stantler, staraptor, staraptor mega, staravia, starly, starmie, starmie alternate form 1, starmie mega, staryu, staryu alternate form 1, steelix, steelix mega, steenee, steenee redux, stonjourner, stoutland, stufful, stufful redux, stunfisk, stunfisk galar, stunky, sudowoodo, suicune, sunflora, sunflora alternate form 1, sunflora alternate form 2, sunkern, surskit, swablu, swablu redux, swadloon, swalot, swalot alternate form 1, swalot alternate form 2, swalot mega, swampage, swampage mega, swampert, swampert alternate mega form 2, swampert alternate mega form 3, swampert mega, swanna, swellow, swinub, swinub redux, swirlix, sylveon, sylveon alternate form 3, tadbulb, taillow, talonflame, talonflame mega, tandemaus, tangela, tangrowth, tapu bulu, tapu fini, tapu koko, tapu lele, tarountula, tatsugiri curly, tatsugiri droopy, tatsugiri mega, tatsugiri stretchy, tauros, tauros paldea aqua breed, tauros paldea blaze breed, tauros paldea combat breed, teddiursa, tentacool, tentacruel, tentagrewl, tepig, terapagos, terapagos terastal, terrakion, thievul, throh, throh redux, thundurus incarnate, thundurus therian, thwackey, thwackey alternate form 2, timburr, timburr alternate form 1, ting lu, tinkatink, tinkatink redux, tinkaton, tinkaton mega, tinkaton redux, tinkaton redux mega, tinkatuff, tinkatuff redux, tirtouga, tirtouga alternate form 1, toedscool, toedscruel, togedemaru, togekiss, togepi, togetic, torchic, torkoal, tornadus incarnate, tornadus therian, torracat, torrentula, tortemple, torterra, torterra bluetowel alternate form form 1, torterra mega, torterra redux, torterra redux mega, totodile, toucannon, toucannon mega, toxapex, toxel, toxel redux, toxicroak, toxtricity amped, toxtricity amped gmax, toxtricity low key, toxtricity low key gmax, toxtricity mega, toxtricity redux, toxtricity redux fuzz, toxtricity redux fuzz mega, toxtricity redux mega, tranquill, tranquill alternate form 1, trapinch, trapinch alternate form 1, trapinch redux, treecko, trevenant, tropius, tropius alternate form 1, trubbish, trubbish alternate form 1, trumbeak, tsareena, tsareena mega, tsareena redux, tsareena redux mega, turtonator, turtwig, turtwig redux, tympole, tynamo, type null, typhlosion, typhlosion alternate form 1, typhlosion alternate form 2, typhlosion hisui, typhlosion hisui mega, typhlosion mega, tyranitar, tyranitar mega, tyranitar mega redux, tyranitar redux, tyranjoula, tyrantrum, tyrantrum alternate form 1, tyrogue, tyrunt, tyrunt alternate form 1, umbreon, umbreon alternate form 3, unfezant, unown, unown a, unown b, unown c, unown d, unown e, unown exclamation, unown g, unown h, unown i, unown j, unown k, unown l, unown n, unown o, unown p, unown q, unown question, unown r, unown revelation, unown s, unown t, unown u, unown v, unown w, unown x, unown y, unown z, ursaluna, ursaluna bloodmoon, ursaluna mega, ursaring, urshifu mega, urshifu rapid strike, urshifu rapid strike gmax, urshifu rapid strike style mega, urshifu single strike, urshifu single strike gmax, uxie, uxie redux, vanillish, vanillish alternate form 1, vanillish redux, vanillite, vanillite alternate form 1, vanillite redux, vanilluxe, vanilluxe alternate form 1, vanilluxe mega, vanilluxe redux, vanilluxe redux mega, vaporeon, vaporeon alternate form 3, varoom, velozel, veluza, venipede, venomoth, venomoth alternate form 1, venonat, venonat alternate form 1, venusaur, venusaur gmax, venusaur mega, venusaur mega x, vespiquen, vespiquen alternate form 1, vibrava, vibrava alternate form 1, vibrava redux, victini, victini primal, victreebel, victreebel mega, victreebel redux, vigoroth, vikavolt, vileplume, virizion, vivillon archipelago, vivillon continental, vivillon elegant, vivillon fancy, vivillon garden, vivillon high plains, vivillon icy snow, vivillon jungle, vivillon marine, vivillon meadow, vivillon modern, vivillon monsoon, vivillon ocean, vivillon poke ball, vivillon polar, vivillon river, vivillon sandstorm, vivillon savanna, vivillon sun, vivillon tundra, volbeat, volcanion, volcarona, volcarona redux, voltorb, voltorb hisui, vullaby, vulpix, vulpix alola, vulpix alternate form 2, vulpix alternate form 3, wailmer, wailmer alternate form 1, wailord, walking wake, walrein, wartortle, watchog, wattrel, weavile, weavile alternate form 1, weavile mega, weavile redux, weavile redux mega, weedle, weedle alternate form 2, weedle redux, weepinbell, weepinbell redux, weezing, weezing bluetowel alternate forms form 2, whimsicott, whirlipede, whiscash, whismur, whismur redux, wigglytuff, wigglytuff alternate form 1, wigglytuff apex, wigglytuff mega, wigglytuff mega x, wigglytuff primal, wiglett, wimpod, wingull, wishiwashi school, wishiwashi solo, wispywaspy, wispywaspy hivemind, wo chien, wobbuffet, woobat, wooloo, wooly worm, wooper, wooper alternate form 1, wooper paldea, wormadam plant, wormadam sandy, wormadam trash, wugtrio, wurmple, wynaut, wyrdeer, xatu, xatu alternate form 1, xerneas active, xerneas neutral, xurkitree, yamask, yamask alternate form 1, yamask alternate form 2, yamask galar, yamper, yanmega, yungoos, yveltal, yveltal mega, zacian, zacian crowned, zamazenta, zamazenta crowned, zangoose, zapdos, zapdos ex, zapdos ex mega, zapdos galar, zarude, zarude dada, zebstrika, zekrom, zeraora, zeraora mega, zigzagoon, zigzagoon galar, zoroark, zoroark hisui, zorua, zorua hisui, zubat, zweilous, zweilous cybertank form 1, zweilous redux, zygarde 10, zygarde 10 power construct, zygarde 50, zygarde 50 power construct, zygarde complete, zygarde complete mega, zygarde mega — 8775 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0109_mismagius_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0109_mismagius_alternate_form_2/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0109_mismagius_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0109_mismagius_alternate_form_2/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0191_salamence_alternate_mega_form_3/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0191_salamence_alternate_mega_form_3/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_hisuian_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_hisuian_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_hisuian_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_hisuian_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swampert/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swampert/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swampert/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swampert/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scyther_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scyther_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scyther_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scyther_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0050_drowzee_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0050_drowzee_alternate_form_2/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0050_drowzee_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0050_drowzee_alternate_form_2/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/venusaur_mega_x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/venusaur_mega_x/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/venusaur_mega_x/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/venusaur_mega_x/female/back.png`
- … 8745 more

### 2. aegislash shield, aggron, alcremie caramel swirl berry sweet, alcremie caramel swirl clover sweet, alcremie caramel swirl flower sweet, alcremie caramel swirl love sweet, alcremie caramel swirl ribbon sweet, alcremie caramel swirl star sweet, alcremie caramel swirl strawberry sweet, alcremie lemon cream berry sweet, alcremie lemon cream clover sweet, alcremie lemon cream flower sweet, alcremie lemon cream love sweet, alcremie lemon cream ribbon sweet, alcremie lemon cream star sweet, alcremie lemon cream strawberry sweet, alcremie matcha cream berry sweet, alcremie matcha cream clover sweet, alcremie matcha cream flower sweet, alcremie matcha cream love sweet, alcremie matcha cream ribbon sweet, alcremie matcha cream star sweet, alcremie matcha cream strawberry sweet, alcremie mint cream berry sweet, alcremie mint cream clover sweet, alcremie mint cream flower sweet, alcremie mint cream love sweet, alcremie mint cream ribbon sweet, alcremie mint cream star sweet, alcremie mint cream strawberry sweet, alcremie rainbow swirl berry sweet, alcremie rainbow swirl clover sweet, alcremie rainbow swirl flower sweet, alcremie rainbow swirl love sweet, alcremie rainbow swirl ribbon sweet, alcremie rainbow swirl star sweet, alcremie rainbow swirl strawberry sweet, alcremie ruby cream berry sweet, alcremie ruby cream clover sweet, alcremie ruby cream flower sweet, alcremie ruby cream love sweet, alcremie ruby cream ribbon sweet, alcremie ruby cream star sweet, alcremie ruby cream strawberry sweet, alcremie ruby swirl berry sweet, alcremie ruby swirl clover sweet, alcremie ruby swirl flower sweet, alcremie ruby swirl love sweet, alcremie ruby swirl ribbon sweet, alcremie ruby swirl star sweet, alcremie ruby swirl strawberry sweet, alcremie salted cream berry sweet, alcremie salted cream clover sweet, alcremie salted cream flower sweet, alcremie salted cream love sweet, alcremie salted cream ribbon sweet, alcremie salted cream star sweet, alcremie salted cream strawberry sweet, alcremie vanilla cream berry sweet, alcremie vanilla cream clover sweet, alcremie vanilla cream flower sweet, alcremie vanilla cream love sweet, alcremie vanilla cream ribbon sweet, alcremie vanilla cream star sweet, alcremie vanilla cream strawberry sweet, alomomola, altaria, altaria mega, amaura, appletun gmax, arbok, archen, arctibax, arctozolt, armarouge, aron, articuno galar, axew, baltoy, banette, barboach, basculin blue striped, basculin red striped, basculin white striped, bayleef, beedrill, beheeyem, bellibolt, bellsprout, bergmite, bibarel, bidoof, bisharp, blacephalon, blastoise, blaziken, blipbug, blissey, blitzle, bonsly, bouffalant, bounsweet, braixen, brambleghast, bramblin, breloom, bronzong, bronzor, budew, buizel, bulbasaur, buneary, bunnelby, burmy plant, burmy sandy, burmy trash, butterfree, buzzwole, cacnea, cacturne, calyrex, calyrex ice, carbink, carkol, carracosta, carvanha, cascoon, castform, castform rainy, castform snowy, castform sunny, caterpie, celebi, ceruledge, cetoddle, chandelure mega, chansey, charjabug, charmander, charmeleon, chatot, cherrim overcast, cherrim sunshine, cherubi, chespin, chewtle, chikorita, chimchar, chimecho, cinccino, clamperl, clauncher, claydol, clefairy, cleffa, combee, corphish, cosmoem, cottonee, cranidos, crawdaunt, croagunk, crocalor, croconaw, crustle, cryogonal, cubchoo, cubone, cufant, darkrai mega, darmanitan zen, dartrix, darumaka, decidueye, decidueye hisui, dedenne, deerling autumn, deerling spring, deerling summer, deerling winter, deino, deoxys speed, dewott, dewpider, dhelmise, diggersby, diglett, diglett alola, dipplin, ditto, dodrio, dolliv, dottler, dracovish, dratini, drifblim, drifloon, drilbur, dubwool, ducklett, dugtrio, dugtrio alola, dunsparce, duosion, durant, dusclops, duskull, dwebble, eelektrik, eevee, eiscue ice, ekans, eldegoss, electrode, electrode hisui, elekid, elgyem, empoleon, entei, escavalier, espurr, exeggutor alola, ferroseed, fezandipiti, fidough, finizen, finneon, flaaffy, flabebe blue, flabebe orange, flabebe red, flabebe white, flabebe yellow, flamigo, flapple gmax, flareon, fletchling, flittle, flygon, fomantis, foongus, forretress, fraxure, frigibax, frillish, froakie, froslass, fuecoco, gabite, gallade, genesect, genesect burn, genesect chill, genesect douse, genesect shock, gholdengo, gible, glalie, gloom, goldeen, golem, golett, goomy, gossifleur, gothita, gothitelle, gourgeist average, gourgeist large, gourgeist small, gourgeist super, grapploct, greavard, grimer, grimer alola, grookey, grovyle, growlithe, growlithe hisui, grubbin, grumpig, gulpin, gumshoos, gyarados mega, happiny, hariyama, hatenna, heatmor, heliolisk, helioptile, hippopotas, hippowdon, hitmonchan, hitmonlee, horsea, houndour, igglybuff, illumise, incineroar, inkay, inteleon, iron bundle, iron valiant, ivysaur, jangmo o, jellicent, jirachi, jolteon, joltik, jumpluff, kabuto, kabutops, kakuna, karrablast, kecleon, keldeo ordinary, kilowattrel, kingdra, kingler, kirlia, klang, kleavor, koffing, komala, kricketot, kricketune, krokorok, krookodile, kubfu, lairon, lampent, lapras, larvesta, leavanny, lechonk, ledian, ledyba, lickilicky, lickitung, lileep, lilligant, lilligant hisui, lillipup, linoone, linoone galar, litwick, lombre, lotad, loudred, lucario, lucario mega, lucario mega z, ludicolo, lunatone, luvdisc, lycanroc midnight, machoke, machop, magby, magikarp, magmortar, magnemite, magneton, makuhita, mamoswine, manaphy, mandibuzz, mantyke, mareanie, marshadow, marshtomp, maschiff, medicham, medicham mega, meditite, meloetta aria, meloetta pirouette, meltan, meowth, meowth alola, meowth galar, meowth gmax, metang, metapod, mienfoo, mienshao, milotic, mime jr, mimikyu busted, mimikyu disguised, minun, misdreavus, mismagius, monferno, morelull, morgrem, mr mime, munchlax, munkidori, munna, murkrow, nacli, naclstack, natu, nidoran, nidorino, nihilego, nincada, noibat, nosepass, numel, nuzleaf, nymble, octillery, oddish, ogerpon cornerstone mask, ogerpon hearthflame mask, ogerpon wellspring mask, omanyte, omastar, orbeetle, oricorio baile, oricorio pau, oricorio sensu, orthworm, oshawott, palafin zero, palossand, palpitoad, pancham, pangoro, panpour, pansage, pansear, paras, patrat, pawmo, pawmot, pawniard, petilil, phanpy, phione, pidgey, pidove, pignite, pikachu, pikachu alola cap, pikachu belle, pikachu cosplay, pikachu hoenn cap, pikachu kalos cap, pikachu libre, pikachu original cap, pikachu partner cap, pikachu phd, pikachu pop star, pikachu rock star, pikachu sinnoh cap, pikachu unova cap, pikachu world cap, pikipek, piloswine, pincurchin, pineco, piplup, plusle, politoed, poliwag, poltchageist artisan, poltchageist counterfeit, polteageist antique, polteageist phony, popplio, porygon, prinplup, probopass, psyduck, pumpkaboo average, pumpkaboo large, pumpkaboo small, pumpkaboo super, pupitar, purugly, pyukumuku, quagsire, quaxly, quaxwell, raboot, raichu alola, raikou, ralts, raticate, rattata, regice, regirock, registeel, reshiram, rhydon, rhyperior, ribombee, riolu, rockruff, rockruff own tempo, roggenrola, rolycoly, rookidee, roselia, roserade, rotom, rotom fan, rotom wash, rowlet, rufflet, sableye mega, salazzle, sandaconda, sandshrew, sandshrew alola, sandslash, sandygast, scatterbug archipelago, scatterbug continental, scatterbug elegant, scatterbug fancy, scatterbug garden, scatterbug high plains, scatterbug icy snow, scatterbug jungle, scatterbug marine, scatterbug meadow, scatterbug modern, scatterbug monsoon, scatterbug ocean, scatterbug poke ball, scatterbug polar, scatterbug river, scatterbug sandstorm, scatterbug savanna, scatterbug sun, scatterbug tundra, sceptile, sceptile mega, scrafty, scrafty mega, scraggy, scyther, seadra, sealeo, seedot, sentret, serperior, servine, sewaddle, sharpedo, shaymin land, shaymin sky, shedinja, shellos east, shellos west, shelmet, shiinotic, shroodle, shroomish, shuppet, silicobra, simipour, simisage, sinistcha masterpiece, sinistcha unremarkable, sinistea antique, sinistea phony, skiploom, skrelp, sliggoo, sliggoo hisui, slowbro mega, slowking, slowking galar, slowpoke, slowpoke galar, slugma, slurpuff, smoliv, smoochum, sneasel hisui, snivy, snom, snorlax, snorunt, snover, snubbull, sobble, solgaleo, solosis, solrock, spearow, spewpa archipelago, spewpa continental, spewpa elegant, spewpa fancy, spewpa garden, spewpa high plains, spewpa icy snow, spewpa jungle, spewpa marine, spewpa meadow, spewpa modern, spewpa monsoon, spewpa ocean, spewpa poke ball, spewpa polar, spewpa river, spewpa sandstorm, spewpa savanna, spewpa sun, spewpa tundra, spheal, spinarak, spinda, spiritomb, spoink, spritzee, squawkabilly blue plumage, squawkabilly green plumage, squawkabilly white plumage, squawkabilly yellow plumage, squirtle, starly, starmie, starmie mega, staryu, steenee, stufful, stunfisk, sudowoodo, sunflora, surskit, swablu, swadloon, swalot, swellow, swinub, swirlix, swoobat, tadbulb, taillow, tangela, tangrowth, tapu bulu, tapu fini, tatsugiri curly, tauros, teddiursa, tentacool, tentacruel, tepig, terrakion, thwackey, tinkatink, tinkatuff, tirtouga, togepi, togetic, torchic, torkoal, torterra, totodile, toxtricity amped, toxtricity low key, tranquill, trapinch, treecko, trevenant, trubbish, trumbeak, tsareena, turtwig, tympole, typhlosion hisui, tyrogue, unfezant, unown, unown b, unown d, unown e, unown exclamation, unown g, unown h, unown i, unown j, unown k, unown l, unown o, unown p, unown q, unown question, unown r, unown s, unown t, unown u, unown z, ursaluna, urshifu rapid strike, urshifu rapid strike gmax, urshifu single strike, vanillish, vanillite, venipede, venonat, vibrava, victini, victreebel, vileplume, volbeat, volcanion, voltorb, voltorb hisui, vullaby, vulpix, wailmer, watchog, wattrel, weavile, weedle, weepinbell, weezing, whimsicott, whirlipede, whismur, wiglett, wishiwashi solo, wobbuffet, wooloo, wooper, wormadam plant, wormadam sandy, wormadam trash, wurmple, xatu, yamask, yamask galar, yamper, zangoose, zeraora, zigzagoon, zoroark, zorua, zorua hisui — 751 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magby/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sewaddle/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baltoy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mismagius/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lillipup/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tangela/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rowlet/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magneton/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/castform-sunny/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/serperior/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/duosion/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-strawberry-sweet/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wormadam-trash/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/deerling-spring/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sobble/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bonsly/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-partner-cap/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pidgey/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-high-plains/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/castform/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/spewpa-marine/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hitmonlee/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sliggoo/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gloom/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lotad/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wormadam-plant/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/axew/icon.png`
- … 721 more

### 3. arceus, arceus bug, arceus dark, arceus dragon, arceus electric, arceus fairy, arceus fighting, arceus fire, arceus flying, arceus ghost, arceus grass, arceus ground, arceus ice, arceus poison, arceus psychic, arceus rock, arceus steel, arceus unknown, arceus water — 19 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-flying/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-poison/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-unknown/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-normal/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-steel/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ghost/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fire/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-dragon/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-electric/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fighting/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-rock/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-dark/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-water/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fairy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ground/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ice/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-bug/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-grass/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-psychic/icon.png`

### 4. vivillon archipelago, vivillon continental, vivillon elegant, vivillon fancy, vivillon garden, vivillon high plains, vivillon icy snow, vivillon jungle, vivillon marine, vivillon modern, vivillon monsoon, vivillon ocean, vivillon poke ball, vivillon polar, vivillon river, vivillon sandstorm, vivillon savanna, vivillon sun, vivillon tundra — 19 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-polar/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-fancy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-savanna/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-garden/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-icy-snow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-tundra/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-monsoon/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-ocean/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-poke-ball/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-modern/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-sandstorm/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-archipelago/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-river/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-jungle/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-marine/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-high-plains/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-elegant/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-sun/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-continental/icon.png`

### 5. minior blue, minior blue meteor, minior green, minior green meteor, minior indigo, minior indigo meteor, minior orange, minior orange meteor, minior red, minior red meteor, minior violet, minior violet meteor, minior yellow, minior yellow meteor — 14 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange/icon.png`

### 6. exeggutor, floette blue, floette eternal, floette orange, floette red, floette white, floette yellow — 7 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-orange/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-white/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/exeggutor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-blue/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-red/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-yellow/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-eternal/icon.png`

### 7. charizard mega x, garbodor gmax, garbodor mega — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard-mega-x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard-mega-x/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor-gmax/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor_mega/female/back.png`

### 8. earthretha belstatue, earthretha belstatue 1, earthretha belstatue 2 — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_2/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_2/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_1/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_1/female/back.png`

### 9. machamp, machamp gmax, machamp mega — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/female/front.png`

### 10. granbull mega, mega spiritomb, moltres ex — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mega_spiritomb/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mega_spiritomb/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/granbull_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/granbull_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres_ex/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres_ex/female/back.png`

### 11. electabuzz, gothorita, gurdurr, herdier, wooper paldea — 5 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gurdurr/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wooper-paldea/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/electabuzz/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gothorita/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/herdier/icon.png`

### 12. arcanine redux, mightyena — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mightyena/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mightyena/female/front.png`

### 13. barbaracle, moltres ex mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres_ex_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres_ex_mega/female/front.png`

### 14. beedrill mega redux, reuniclus redux — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beedrill_mega_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beedrill_mega_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/reuniclus_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/reuniclus_redux/female/front.png`

### 15. butterfree gmax, butterfree mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree-gmax/female/front.png`

### 16. mega rhyperior, sceptile alternate mega form 3 — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0141_sceptile_alternate_mega_form_3/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0141_sceptile_alternate_mega_form_3/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mega_rhyperior/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mega_rhyperior/female/front.png`

### 17. metagross alternate form 2 — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0195_metagross_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0195_metagross_alternate_form_2/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0195_metagross_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0195_metagross_alternate_form_2/female/back.png`

### 18. gurdurr alternate form 1 — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0254_gurdurr_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0254_gurdurr_alternate_form_1/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0254_gurdurr_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0254_gurdurr_alternate_form_1/female/back.png`

### 19. krookodile alternate form 1, mega probopass — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0264_krookodile_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0264_krookodile_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mega_probopass/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mega_probopass/female/back.png`

### 20. dragalge mega, kleavor redux — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kleavor_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kleavor_redux/female/front.png`

### 21. earthretha venonat 1, ferrothorn alternate form 1 — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_venonat_1/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_venonat_1/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0284_ferrothorn_alternate_form_1/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0284_ferrothorn_alternate_form_1/female/back.png`

### 22. florges blue, florges orange, florges red, florges white — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-orange/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-blue/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-red/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-white/icon.png`

### 23. hydreigon, samurott mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydreigon/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydreigon/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/samurott_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/samurott_mega/female/back.png`

### 24. kingler gmax, kingler mega — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler-gmax/female/front.png`

### 25. fearow redux, mesprit redux — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mesprit_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mesprit_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/fearow_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/fearow_redux/female/front.png`

### 26. hydroar, pyroar — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar_f/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar_f/female/back.png`

### 27. rapidash galar, snorlax — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rapidash-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rapidash-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax/female/front.png`

### 28. liepard, swoobat — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swoobat/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swoobat/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/liepard/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/liepard/female/front.png`

### 29. boldore, duraludon, duraludon gmax — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/duraludon-gmax/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/boldore/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/duraludon/icon.png`

### 30. accelgor, passimian, thievul — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/passimian/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/thievul/icon.png`

### 31. staraptor, staraptor mega, staravia — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staravia/icon.png`

### 32. brute bonnet, kingambit, vanilluxe — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vanilluxe/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/brute-bonnet/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingambit/icon.png`

### 33. abomasnow — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/female/front.png`

### 34. abra, manectric — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/manectric/icon.png`

### 35. alakazam — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam/female/front.png`

### 36. beldum, heracross — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beldum/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heracross/icon.png`

### 37. butterfree — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree/female/front.png`

### 38. cyclizar, hawlucha — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cyclizar/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha/icon.png`

### 39. delphox, nidorina — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidorina/icon.png`

### 40. deoxys, deoxys attack — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/deoxys-normal/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/deoxys-attack/icon.png`

### 41. doduo — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/doduo/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/doduo/female/back.png`

### 42. dudunsparce three segment, dudunsparce two segment — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dudunsparce-two-segment/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dudunsparce-three-segment/icon.png`

### 43. dustox — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dustox/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dustox/female/back.png`

### 44. electrike, zigzagoon galar — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/electrike/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zigzagoon-galar/icon.png`

### 45. frosmoth, honchkrow — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frosmoth/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/honchkrow/icon.png`

### 46. gastrodon east, gastrodon west — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gastrodon-west/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gastrodon-east/icon.png`

### 47. girafarig — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/girafarig/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/girafarig/female/back.png`

### 48. gyarados — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gyarados/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gyarados/female/back.png`

### 49. indeedee — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-male/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-female/icon.png`

### 50. latias mega, latios mega — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/icon.png`

### 51. magearna, magearna original — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magearna/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magearna-original/icon.png`

### 52. charcadet, milcery — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/milcery/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charcadet/icon.png`

### 53. milotic — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/milotic/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/milotic/female/front.png`

### 54. minccino, purrloin — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minccino/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/purrloin/icon.png`

### 55. morpeko full belly, morpeko hangry — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/morpeko-full-belly/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/morpeko-hangry/icon.png`

### 56. musharna, tinkaton — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/musharna/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tinkaton/icon.png`

### 57. obstagoon, rabsca — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/obstagoon/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rabsca/icon.png`

### 58. palafin hero, rampardos — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/palafin-hero/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rampardos/icon.png`

### 59. golisopod mega, pidgeot — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pidgeot/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod-mega/icon.png`

### 60. raichu, wartortle — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wartortle/icon.png`

### 61. rillaboom, urshifu single strike gmax — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rillaboom/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-single-strike-gmax/icon.png`

### 62. emolga, scolipede — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/emolga/icon.png`

### 63. steelix — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/steelix/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/steelix/female/back.png`

### 64. tatsugiri droopy, tatsugiri stretchy — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tatsugiri-droopy/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tatsugiri-stretchy/icon.png`

### 65. graveler, volcarona — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/volcarona/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/graveler/icon.png`

### 66. diancie, xurkitree — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/xurkitree/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/diancie/icon.png`

### 67. zarude, zarude dada — 2 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zarude/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zarude-dada/icon.png`

## Duplicated concept candidates

### 1. basculegion — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/icon.png`

### 2. frillish — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-male/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/frillish-female/icon.png`

### 3. indeedee — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-male/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/indeedee-female/icon.png`

### 4. jellicent — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-female/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/jellicent-male/icon.png`

### 5. meowstic — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-female/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-male/icon.png`

### 6. nidoran — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-m/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-m/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-m/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-m/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-m/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-f/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-f/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-f/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-f/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/nidoran-f/icon.png`

### 7. oinkologne — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-female/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/oinkologne-male/icon.png`

### 8. pyroar — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-male/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-male/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-male/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-male/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-female/icon.png`

### 9. unown — 10 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-f/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-f/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-f/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-f/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-f/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-m/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-m/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-m/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-m/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/unown-m/icon.png`

### 10. absol mega z — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/icon.png`

### 11. barbaracle mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/barbaracle-mega/icon.png`

### 12. baxcalibur mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baxcalibur_mega/female/back.png`

### 13. chandelure mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_mega/female/back.png`

### 14. chesnaught mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chesnaught_mega/female/back.png`

### 15. chimecho mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chimecho_mega/female/back.png`

### 16. clefable mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable_mega/female/back.png`

### 17. darkrai mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darkrai_mega/female/back.png`

### 18. delphox mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox-mega/icon.png`

### 19. dragalge mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragalge_mega/female/back.png`

### 20. dragonite mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dragonite_mega/female/back.png`

### 21. drampa mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drampa_mega/female/back.png`

### 22. excadrill mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/excadrill_mega/female/back.png`

### 23. falinks mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/falinks_mega/female/back.png`

### 24. froslass mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass_mega/female/back.png`

### 25. glimmora mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glimmora-mega/icon.png`

### 26. golisopod mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golisopod-mega/icon.png`

### 27. greninja mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja_mega/female/back.png`

### 28. hawlucha mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hawlucha_mega/female/back.png`

### 29. heatran mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/heatran_mega/female/back.png`

### 30. lucario mega z — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario-mega-z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario-mega-z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario-mega-z/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario-mega-z/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario-mega-z/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario_mega_z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario_mega_z/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario_mega_z/female/back.png`

### 31. malamar mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/malamar-mega/icon.png`

### 32. meganium mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meganium-mega/icon.png`

### 33. meowstic mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowstic-mega/icon.png`

### 34. pyroar mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pyroar_mega/female/back.png`

### 35. raichu mega x — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu_mega_x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu_mega_x/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu_mega_x/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu_mega_x/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu-mega-x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu-mega-x/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu-mega-x/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu-mega-x/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/raichu-mega-x/icon.png`

### 36. scolipede mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scolipede-mega/icon.png`

### 37. scovillain mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scovillain-mega/icon.png`

### 38. scrafty mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/icon.png`

### 39. skarmory mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skarmory_mega/female/back.png`

### 40. staraptor mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/staraptor-mega/icon.png`

### 41. starmie mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie-mega/icon.png`

### 42. victreebel mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel-mega/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel_mega/female/back.png`

### 43. zeraora mega — 9 files

Dimensions: 160x80, 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora_mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora-mega/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zeraora-mega/icon.png`

### 44. hydroar — 8 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar_f/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar_f/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar_f/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hydroar_f/female/back.png`

