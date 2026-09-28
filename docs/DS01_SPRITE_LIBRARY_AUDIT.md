# DS01 Sprite Library Duplicate Audit

Status: ANALYSIS ONLY — no sprite assets were installed, replaced, recolored, or deleted.

## Summary

- Images scanned: **11365**
- Sprite candidates: **11365**
- Male/front visual representatives: **4910**
- Exact byte-duplicate groups: **4643**
- Exact rendered-pixel duplicate groups: **19**
- Palette/recolor candidate groups: **13**
- Near-visual duplicate groups (dHash <= 4): **16**
- Concept-name collision groups: **0**

### Classification

- **Exact byte duplicate**: identical encoded image bytes.
- **Exact pixel duplicate**: different files/encodings that render identically.
- **Palette/recolor candidate**: identical per-pixel color-pattern topology after palette labels are normalized, but different rendered RGB values.
- **Near visual duplicate**: same dimensions and perceptual dHash distance within the configured threshold, excluding exact/palette matches.
- **Concept collision**: normalized sprite naming points at the same concept across multiple distinct visuals or source buckets.

## Exact byte duplicates

### 1. scatterbug-archipelago female back, scatterbug-archipelago male back, scatterbug-continental female back, scatterbug-continental male back, scatterbug-elegant female back, scatterbug-elegant male back, scatterbug-fancy female back, scatterbug-fancy male back, scatterbug-garden female back, scatterbug-garden male back, scatterbug-high-plains female back, scatterbug-high-plains male back, scatterbug-icy-snow female back, scatterbug-icy-snow male back, scatterbug-jungle female back, scatterbug-jungle male back, scatterbug-marine female back, scatterbug-marine male back, scatterbug-meadow female back, scatterbug-meadow male back, scatterbug-modern female back, scatterbug-modern male back, scatterbug-monsoon female back, scatterbug-monsoon male back, scatterbug-ocean female back, scatterbug-ocean male back, scatterbug-poke-ball female back, scatterbug-poke-ball male back, scatterbug-polar female back, scatterbug-polar male back, scatterbug-river female back, scatterbug-river male back, scatterbug-sandstorm female back, scatterbug-sandstorm male back, scatterbug-savanna female back, scatterbug-savanna male back, scatterbug-sun female back, scatterbug-sun male back, scatterbug-tundra female back, scatterbug-tundra male back — 40 files

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

### 2. scatterbug-archipelago female front, scatterbug-archipelago male front, scatterbug-continental female front, scatterbug-continental male front, scatterbug-elegant female front, scatterbug-elegant male front, scatterbug-fancy female front, scatterbug-fancy male front, scatterbug-garden female front, scatterbug-garden male front, scatterbug-high-plains female front, scatterbug-high-plains male front, scatterbug-icy-snow female front, scatterbug-icy-snow male front, scatterbug-jungle female front, scatterbug-jungle male front, scatterbug-marine female front, scatterbug-marine male front, scatterbug-meadow female front, scatterbug-meadow male front, scatterbug-modern female front, scatterbug-modern male front, scatterbug-monsoon female front, scatterbug-monsoon male front, scatterbug-ocean female front, scatterbug-ocean male front, scatterbug-poke-ball female front, scatterbug-poke-ball male front, scatterbug-polar female front, scatterbug-polar male front, scatterbug-river female front, scatterbug-river male front, scatterbug-sandstorm female front, scatterbug-sandstorm male front, scatterbug-savanna female front, scatterbug-savanna male front, scatterbug-sun female front, scatterbug-sun male front, scatterbug-tundra female front, scatterbug-tundra male front — 40 files

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

### 3. spewpa-archipelago female back, spewpa-archipelago male back, spewpa-continental female back, spewpa-continental male back, spewpa-elegant female back, spewpa-elegant male back, spewpa-fancy female back, spewpa-fancy male back, spewpa-garden female back, spewpa-garden male back, spewpa-high-plains female back, spewpa-high-plains male back, spewpa-icy-snow female back, spewpa-icy-snow male back, spewpa-jungle female back, spewpa-jungle male back, spewpa-marine female back, spewpa-marine male back, spewpa-meadow female back, spewpa-meadow male back, spewpa-modern female back, spewpa-modern male back, spewpa-monsoon female back, spewpa-monsoon male back, spewpa-ocean female back, spewpa-ocean male back, spewpa-poke-ball female back, spewpa-poke-ball male back, spewpa-polar female back, spewpa-polar male back, spewpa-river female back, spewpa-river male back, spewpa-sandstorm female back, spewpa-sandstorm male back, spewpa-savanna female back, spewpa-savanna male back, spewpa-sun female back, spewpa-sun male back, spewpa-tundra female back, spewpa-tundra male back — 40 files

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

### 4. spewpa-archipelago female front, spewpa-archipelago male front, spewpa-continental female front, spewpa-continental male front, spewpa-elegant female front, spewpa-elegant male front, spewpa-fancy female front, spewpa-fancy male front, spewpa-garden female front, spewpa-garden male front, spewpa-high-plains female front, spewpa-high-plains male front, spewpa-icy-snow female front, spewpa-icy-snow male front, spewpa-jungle female front, spewpa-jungle male front, spewpa-marine female front, spewpa-marine male front, spewpa-meadow female front, spewpa-meadow male front, spewpa-modern female front, spewpa-modern male front, spewpa-monsoon female front, spewpa-monsoon male front, spewpa-ocean female front, spewpa-ocean male front, spewpa-poke-ball female front, spewpa-poke-ball male front, spewpa-polar female front, spewpa-polar male front, spewpa-river female front, spewpa-river male front, spewpa-sandstorm female front, spewpa-sandstorm male front, spewpa-savanna female front, spewpa-savanna male front, spewpa-sun female front, spewpa-sun male front, spewpa-tundra female front, spewpa-tundra male front — 40 files

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

### 5. scatterbug-archipelago icon, scatterbug-continental icon, scatterbug-elegant icon, scatterbug-fancy icon, scatterbug-garden icon, scatterbug-high-plains icon, scatterbug-icy-snow icon, scatterbug-jungle icon, scatterbug-marine icon, scatterbug-meadow icon, scatterbug-modern icon, scatterbug-monsoon icon, scatterbug-ocean icon, scatterbug-poke-ball icon, scatterbug-polar icon, scatterbug-river icon, scatterbug-sandstorm icon, scatterbug-savanna icon, scatterbug-sun icon, scatterbug-tundra icon — 20 files

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

### 6. spewpa-archipelago icon, spewpa-continental icon, spewpa-elegant icon, spewpa-fancy icon, spewpa-garden icon, spewpa-high-plains icon, spewpa-icy-snow icon, spewpa-jungle icon, spewpa-marine icon, spewpa-meadow icon, spewpa-modern icon, spewpa-monsoon icon, spewpa-ocean icon, spewpa-poke-ball icon, spewpa-polar icon, spewpa-river icon, spewpa-sandstorm icon, spewpa-savanna icon, spewpa-sun icon, spewpa-tundra icon — 20 files

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

### 7. silvally-bug icon, silvally-dark icon, silvally-dragon icon, silvally-electric icon, silvally-fairy icon, silvally-fighting icon, silvally-fire icon, silvally-flying icon, silvally-ghost icon, silvally-grass icon, silvally-ground icon, silvally-ice icon, silvally-normal icon, silvally-poison icon, silvally-psychic icon, silvally-rock icon, silvally-steel icon, silvally-water icon — 18 files

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

### 8. minior-blue-meteor female back, minior-blue-meteor male back, minior-green-meteor female back, minior-green-meteor male back, minior-indigo-meteor female back, minior-indigo-meteor male back, minior-orange-meteor female back, minior-orange-meteor male back, minior-red-meteor female back, minior-red-meteor male back, minior-violet-meteor female back, minior-violet-meteor male back, minior-yellow-meteor female back, minior-yellow-meteor male back — 14 files

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

### 9. minior-blue-meteor female front, minior-blue-meteor male front, minior-green-meteor female front, minior-green-meteor male front, minior-indigo-meteor female front, minior-indigo-meteor male front, minior-orange-meteor female front, minior-orange-meteor male front, minior-red-meteor female front, minior-red-meteor male front, minior-violet-meteor female front, minior-violet-meteor male front, minior-yellow-meteor female front, minior-yellow-meteor male front — 14 files

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

### 10. darkrai_mega female back, darkrai_mega male back, heatran_mega female back, heatran_mega male back, slate female back, slate male back, zeraora_mega female back, zeraora_mega male back — 8 files

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

### 11. darkrai_mega female front, darkrai_mega male front, heatran_mega female front, heatran_mega male front, slate female front, slate male front, zeraora_mega female front, zeraora_mega male front — 8 files

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

### 12. minior-blue-meteor icon, minior-green-meteor icon, minior-indigo-meteor icon, minior-orange-meteor icon, minior-red-meteor icon, minior-violet-meteor icon, minior-yellow-meteor icon — 7 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-green-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-indigo-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-orange-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-blue-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-red-meteor/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-violet-meteor/icon.png`

### 13. mothim-plant female back, mothim-plant male back, mothim-sandy female back, mothim-sandy male back, mothim-trash female back, mothim-trash male back — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/female/back.png`

### 14. mothim-plant female front, mothim-plant male front, mothim-sandy female front, mothim-sandy male front, mothim-trash female front, mothim-trash male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/female/front.png`

### 15. cpf_0340_ribombee_bluetowel_alternate_form_form_1 female back, cpf_0340_ribombee_bluetowel_alternate_form_form_1 male back, cpf_0341_ribombee_bluetowel_alternate_form_form_2 female back, cpf_0341_ribombee_bluetowel_alternate_form_form_2 male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/female/back.png`

### 16. cpf_0340_ribombee_bluetowel_alternate_form_form_1 female front, cpf_0340_ribombee_bluetowel_alternate_form_form_1 male front, cpf_0341_ribombee_bluetowel_alternate_form_form_2 female front, cpf_0341_ribombee_bluetowel_alternate_form_form_2 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0341_ribombee_bluetowel_alternate_form_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0340_ribombee_bluetowel_alternate_form_form_1/female/front.png`

### 17. darmanitan_redux female back, darmanitan_redux male back, darmanitan_redux_bond female back, darmanitan_redux_bond male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/female/back.png`

### 18. darmanitan_redux female front, darmanitan_redux male front, darmanitan_redux_bond female front, darmanitan_redux_bond male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darmanitan_redux_bond/female/front.png`

### 19. genesect-burn icon, genesect-chill icon, genesect-douse icon, genesect-shock icon — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-shock/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-douse/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-burn/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-chill/icon.png`

### 20. gourgeist-average icon, gourgeist-large icon, gourgeist-small icon, gourgeist-super icon — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-small/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-large/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-super/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-average/icon.png`

### 21. greninja-ash female back, greninja-ash male back, greninja-battle-bond female back, greninja-battle-bond male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/female/back.png`

### 22. greninja-ash female front, greninja-ash male front, greninja-battle-bond female front, greninja-battle-bond male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-ash/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/greninja-battle-bond/female/front.png`

### 23. pumpkaboo-average icon, pumpkaboo-large icon, pumpkaboo-small icon, pumpkaboo-super icon — 4 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-average/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-small/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-super/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pumpkaboo-large/icon.png`

### 24. rockruff female back, rockruff male back, rockruff-own-tempo female back, rockruff-own-tempo male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/female/back.png`

### 25. rockruff female front, rockruff male front, rockruff-own-tempo female front, rockruff-own-tempo male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rockruff-own-tempo/female/front.png`

### 26. toxtricity-amped-gmax female back, toxtricity-amped-gmax male back, toxtricity-low-key-gmax female back, toxtricity-low-key-gmax male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/back.png`

### 27. toxtricity-amped-gmax female front, toxtricity-amped-gmax male front, toxtricity-low-key-gmax female front, toxtricity-low-key-gmax male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/front.png`

### 28. zygarde-10 female back, zygarde-10 male back, zygarde-10-power-construct female back, zygarde-10-power-construct male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/female/back.png`

### 29. zygarde-10 female front, zygarde-10 male front, zygarde-10-power-construct female front, zygarde-10-power-construct male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10-power-construct/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-10/female/front.png`

### 30. zygarde-50 female back, zygarde-50 male back, zygarde-50-power-construct female back, zygarde-50-power-construct male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/female/back.png`

### 31. zygarde-50 female front, zygarde-50 male front, zygarde-50-power-construct female front, zygarde-50-power-construct male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50-power-construct/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zygarde-50/female/front.png`

### 32. mothim-plant icon, mothim-sandy icon, mothim-trash icon — 3 files

Dimensions: 32x64

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-plant/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-trash/icon.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mothim-sandy/icon.png`

### 33. abomasnow-mega female back, abomasnow-mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/female/back.png`

### 34. abomasnow-mega female front, abomasnow-mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow-mega/female/front.png`

### 35. abomasnow female back, abomasnow male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/female/back.png`

### 36. abomasnow_santa female back, abomasnow_santa male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/female/back.png`

### 37. abomasnow_santa female front, abomasnow_santa male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow_santa/female/front.png`

### 38. abra female back, abra male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/female/back.png`

### 39. abra female front, abra male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra/female/front.png`

### 40. abra_redux female back, abra_redux male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/female/back.png`

### 41. abra_redux female front, abra_redux male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abra_redux/female/front.png`

### 42. absol-mega-z female back, absol-mega-z male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/female/back.png`

### 43. absol-mega-z female front, absol-mega-z male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega-z/female/front.png`

### 44. absol-mega female back, absol-mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/female/back.png`

### 45. absol-mega female front, absol-mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol-mega/female/front.png`

### 46. absol female back, absol male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/female/back.png`

### 47. absol female front, absol male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/female/front.png`

### 48. absol_mega_z female back, absol_mega_z male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/female/back.png`

### 49. absol_mega_z female front, absol_mega_z male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol_mega_z/female/front.png`

### 50. abyssand female back, abyssand male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/female/back.png`

### 51. abyssand female front, abyssand male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abyssand/female/front.png`

### 52. accelgor female back, accelgor male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/female/back.png`

### 53. accelgor female front, accelgor male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/accelgor/female/front.png`

### 54. aegislash-blade female back, aegislash-blade male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/female/back.png`

### 55. aegislash-blade female front, aegislash-blade male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-blade/female/front.png`

### 56. aegislash-shield female back, aegislash-shield male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/female/back.png`

### 57. aegislash-shield female front, aegislash-shield male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash-shield/female/front.png`

### 58. aegislash_blade_redux female back, aegislash_blade_redux male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/female/back.png`

### 59. aegislash_blade_redux female front, aegislash_blade_redux male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/female/front.png`

### 60. aegislash_blade_redux_mega female back, aegislash_blade_redux_mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/female/back.png`

### 61. aegislash_blade_redux_mega female front, aegislash_blade_redux_mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux_mega/female/front.png`

### 62. aegislash_redux female back, aegislash_redux male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/female/back.png`

### 63. aegislash_redux female front, aegislash_redux male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux/female/front.png`

### 64. aegislash_redux_mega female back, aegislash_redux_mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/female/back.png`

### 65. aegislash_redux_mega female front, aegislash_redux_mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_redux_mega/female/front.png`

### 66. aerodactyl-mega female back, aerodactyl-mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/female/back.png`

### 67. aerodactyl-mega female front, aerodactyl-mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl-mega/female/front.png`

### 68. aerodactyl female back, aerodactyl male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/female/back.png`

### 69. aerodactyl female front, aerodactyl male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aerodactyl/female/front.png`

### 70. aggron-mega female back, aggron-mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/female/back.png`

### 71. aggron-mega female front, aggron-mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron-mega/female/front.png`

### 72. aggron female back, aggron male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/female/back.png`

### 73. aggron female front, aggron male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron/female/front.png`

### 74. aggron_redux female back, aggron_redux male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/female/back.png`

### 75. aggron_redux female front, aggron_redux male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux/female/front.png`

### 76. aggron_redux_mega female back, aggron_redux_mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/female/back.png`

### 77. aggron_redux_mega female front, aggron_redux_mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aggron_redux_mega/female/front.png`

### 78. alakazam-mega female back, alakazam-mega male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/female/back.png`

### 79. alakazam-mega female front, alakazam-mega male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam-mega/female/front.png`

### 80. alakazam_mega_redux female back, alakazam_mega_redux male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/female/back.png`

### 81. alakazam_mega_redux female front, alakazam_mega_redux male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_mega_redux/female/front.png`

### 82. alakazam_redux female back, alakazam_redux male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/female/back.png`

### 83. alakazam_redux female front, alakazam_redux male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/female/front.png`

### 84. alcremie-caramel-swirl-berry-sweet female back, alcremie-caramel-swirl-berry-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/female/back.png`

### 85. alcremie-caramel-swirl-berry-sweet female front, alcremie-caramel-swirl-berry-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-berry-sweet/female/front.png`

### 86. alcremie-caramel-swirl-clover-sweet female back, alcremie-caramel-swirl-clover-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/female/back.png`

### 87. alcremie-caramel-swirl-clover-sweet female front, alcremie-caramel-swirl-clover-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-clover-sweet/female/front.png`

### 88. alcremie-caramel-swirl-flower-sweet female back, alcremie-caramel-swirl-flower-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/back.png`

### 89. alcremie-caramel-swirl-flower-sweet female front, alcremie-caramel-swirl-flower-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/front.png`

### 90. alcremie-caramel-swirl-love-sweet female back, alcremie-caramel-swirl-love-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/female/back.png`

### 91. alcremie-caramel-swirl-love-sweet female front, alcremie-caramel-swirl-love-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-love-sweet/female/front.png`

### 92. alcremie-caramel-swirl-ribbon-sweet female back, alcremie-caramel-swirl-ribbon-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/female/back.png`

### 93. alcremie-caramel-swirl-ribbon-sweet female front, alcremie-caramel-swirl-ribbon-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-ribbon-sweet/female/front.png`

### 94. alcremie-caramel-swirl-star-sweet female back, alcremie-caramel-swirl-star-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/female/back.png`

### 95. alcremie-caramel-swirl-star-sweet female front, alcremie-caramel-swirl-star-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-star-sweet/female/front.png`

### 96. alcremie-caramel-swirl-strawberry-sweet female back, alcremie-caramel-swirl-strawberry-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/female/back.png`

### 97. alcremie-caramel-swirl-strawberry-sweet female front, alcremie-caramel-swirl-strawberry-sweet male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-strawberry-sweet/female/front.png`

### 98. alcremie-gmax female back, alcremie-gmax male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/female/back.png`

### 99. alcremie-gmax female front, alcremie-gmax male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-gmax/female/front.png`

### 100. alcremie-lemon-cream-berry-sweet female back, alcremie-lemon-cream-berry-sweet male back — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-lemon-cream-berry-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-lemon-cream-berry-sweet/female/back.png`

## Exact rendered-pixel duplicates

### 1. toxtricity-amped-gmax female front, toxtricity-amped-gmax male front, toxtricity-low-key-gmax female front, toxtricity-low-key-gmax male front, toxtricity_mega female front, toxtricity_mega male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-amped-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key-gmax/female/front.png`

### 2. alcremie-matcha-cream-love-sweet female back, alcremie-matcha-cream-love-sweet male back, alcremie-ruby-cream-love-sweet female back, alcremie-ruby-cream-love-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/female/back.png`

### 3. alcremie-matcha-cream-ribbon-sweet female back, alcremie-matcha-cream-ribbon-sweet male back, alcremie-ruby-cream-ribbon-sweet female back, alcremie-ruby-cream-ribbon-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/female/back.png`

### 4. alcremie-mint-cream-ribbon-sweet female back, alcremie-mint-cream-ribbon-sweet male back, alcremie-salted-cream-ribbon-sweet female back, alcremie-salted-cream-ribbon-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/female/back.png`

### 5. alcremie-matcha-cream-clover-sweet female back, alcremie-matcha-cream-clover-sweet male back, alcremie-ruby-cream-clover-sweet female back, alcremie-ruby-cream-clover-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/female/back.png`

### 6. alcremie-matcha-cream-star-sweet female back, alcremie-matcha-cream-star-sweet male back, alcremie-ruby-cream-star-sweet female back, alcremie-ruby-cream-star-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/female/back.png`

### 7. alcremie-caramel-swirl-flower-sweet female back, alcremie-caramel-swirl-flower-sweet male back, alcremie-ruby-swirl-flower-sweet female back, alcremie-ruby-swirl-flower-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/back.png`

### 8. alcremie-mint-cream-love-sweet female back, alcremie-mint-cream-love-sweet male back, alcremie-salted-cream-love-sweet female back, alcremie-salted-cream-love-sweet male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/female/back.png`

### 9. charizard-gmax female front, charizard-gmax male front, charizard_mega_z female front, charizard_mega_z male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/charizard_mega_z/female/front.png`

### 10. coalossal-gmax female front, coalossal-gmax male front, coalossal_mega female front, coalossal_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/coalossal-gmax/female/front.png`

### 11. drednaw-gmax female front, drednaw-gmax male front, drednaw_mega female front, drednaw_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/drednaw-gmax/female/front.png`

### 12. hatterene-gmax female front, hatterene-gmax male front, hatterene_mega female front, hatterene_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hatterene_mega/female/front.png`

### 13. inteleon-gmax female front, inteleon-gmax male front, inteleon_mega female front, inteleon_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/inteleon-gmax/female/front.png`

### 14. latias-mega female front, latias-mega male front, latios-mega female front, latios-mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latios-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/latias-mega/female/front.png`

### 15. machamp-gmax female front, machamp-gmax male front, machamp_mega female front, machamp_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/female/front.png`

### 16. pikachu-original-cap female back, pikachu-original-cap male back, pikachu-partner-cap female back, pikachu-partner-cap male back — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-partner-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-partner-cap/female/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-original-cap/male/back.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-original-cap/female/back.png`

### 17. snorlax-gmax female front, snorlax-gmax male front, snorlax_mega female front, snorlax_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax-gmax/female/front.png`

### 18. urshifu-single-strike-gmax female front, urshifu-single-strike-gmax male front, urshifu_mega female front, urshifu_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-single-strike-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-single-strike-gmax/female/front.png`

### 19. urshifu-rapid-strike-gmax female front, urshifu-rapid-strike-gmax male front, urshifu_rapid_strike_style_mega female front, urshifu_rapid_strike_style_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_rapid_strike_style_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu_rapid_strike_style_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-rapid-strike-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/urshifu-rapid-strike-gmax/female/front.png`

## Palette / recolor candidates

### 1. silvally-bug female front, silvally-bug male front, silvally-ground female front, silvally-ground male front, silvally-poison female front, silvally-poison male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/female/front.png`

### 2. alcremie-matcha-cream-love-sweet female front, alcremie-matcha-cream-love-sweet male front, alcremie-ruby-cream-love-sweet female front, alcremie-ruby-cream-love-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-love-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-love-sweet/female/front.png`

### 3. alcremie-matcha-cream-ribbon-sweet female front, alcremie-matcha-cream-ribbon-sweet male front, alcremie-ruby-cream-ribbon-sweet female front, alcremie-ruby-cream-ribbon-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-ribbon-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-ribbon-sweet/female/front.png`

### 4. alcremie-mint-cream-ribbon-sweet female front, alcremie-mint-cream-ribbon-sweet male front, alcremie-salted-cream-ribbon-sweet female front, alcremie-salted-cream-ribbon-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-ribbon-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-ribbon-sweet/female/front.png`

### 5. alcremie-matcha-cream-clover-sweet female front, alcremie-matcha-cream-clover-sweet male front, alcremie-ruby-cream-clover-sweet female front, alcremie-ruby-cream-clover-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-clover-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-clover-sweet/female/front.png`

### 6. alcremie-matcha-cream-star-sweet female front, alcremie-matcha-cream-star-sweet male front, alcremie-ruby-cream-star-sweet female front, alcremie-ruby-cream-star-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-cream-star-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-matcha-cream-star-sweet/female/front.png`

### 7. alcremie-caramel-swirl-flower-sweet female front, alcremie-caramel-swirl-flower-sweet male front, alcremie-ruby-swirl-flower-sweet female front, alcremie-ruby-swirl-flower-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-ruby-swirl-flower-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-caramel-swirl-flower-sweet/female/front.png`

### 8. alcremie-mint-cream-love-sweet female front, alcremie-mint-cream-love-sweet male front, alcremie-salted-cream-love-sweet female front, alcremie-salted-cream-love-sweet male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-salted-cream-love-sweet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alcremie-mint-cream-love-sweet/female/front.png`

### 9. lapras-gmax female front, lapras-gmax male front, lapras_mega female front, lapras_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lapras-gmax/female/front.png`

### 10. silvally-dragon female front, silvally-dragon male front, silvally-steel female front, silvally-steel male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/female/front.png`

### 11. silvally-fire female front, silvally-fire male front, silvally-grass female front, silvally-grass male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/female/front.png`

### 12. silvally-dark female front, silvally-dark male front, silvally-ice female front, silvally-ice male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dark/female/front.png`

### 13. silvally-ghost female front, silvally-ghost male front, silvally-normal female front, silvally-normal male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/female/front.png`

## Near visual duplicates

### 1. abomasnow_santa female front, abomasnow_santa male front, abra female front, abra male front, abra_redux female front, abra_redux male front, absol female front, absol male front, absol-mega female front, absol-mega male front, absol-mega-z female front, absol-mega-z male front, absol_mega_z female front, absol_mega_z male front, abyssand female front, abyssand male front, aegislash-blade female front, aegislash-blade male front, aegislash-shield female front, aegislash-shield male front, aegislash_blade_redux female front, aegislash_blade_redux male front, aegislash_redux female front, aegislash_redux male front, aegislash_redux_mega female front, aegislash_redux_mega male front, aggron female front, aggron male front, aggron-mega female front, aggron-mega male front, aggron_redux female front, aggron_redux male front, aggron_redux_mega female front, aggron_redux_mega male front, aipom female front, aipom male front, alakazam-mega female front, alakazam-mega male front, alakazam_redux female front, alakazam_redux male front, alcremie-caramel-swirl-berry-sweet female front, alcremie-caramel-swirl-berry-sweet male front, alcremie-caramel-swirl-clover-sweet female front, alcremie-caramel-swirl-clover-sweet male front, alcremie-caramel-swirl-flower-sweet female front, alcremie-caramel-swirl-flower-sweet male front, alcremie-caramel-swirl-love-sweet female front, alcremie-caramel-swirl-love-sweet male front, alcremie-caramel-swirl-ribbon-sweet female front, alcremie-caramel-swirl-ribbon-sweet male front, alcremie-caramel-swirl-star-sweet female front, alcremie-caramel-swirl-star-sweet male front, alcremie-caramel-swirl-strawberry-sweet female front, alcremie-caramel-swirl-strawberry-sweet male front, alcremie-gmax female front, alcremie-gmax male front, alcremie-lemon-cream-berry-sweet female front, alcremie-lemon-cream-berry-sweet male front, alcremie-lemon-cream-clover-sweet female front, alcremie-lemon-cream-clover-sweet male front, alcremie-lemon-cream-flower-sweet female front, alcremie-lemon-cream-flower-sweet male front, alcremie-lemon-cream-love-sweet female front, alcremie-lemon-cream-love-sweet male front, alcremie-lemon-cream-ribbon-sweet female front, alcremie-lemon-cream-ribbon-sweet male front, alcremie-lemon-cream-star-sweet female front, alcremie-lemon-cream-star-sweet male front, alcremie-lemon-cream-strawberry-sweet female front, alcremie-lemon-cream-strawberry-sweet male front, alcremie-matcha-cream-berry-sweet female front, alcremie-matcha-cream-berry-sweet male front, alcremie-matcha-cream-clover-sweet female front, alcremie-matcha-cream-clover-sweet male front, alcremie-matcha-cream-flower-sweet female front, alcremie-matcha-cream-flower-sweet male front, alcremie-matcha-cream-love-sweet female front, alcremie-matcha-cream-love-sweet male front, alcremie-matcha-cream-ribbon-sweet female front, alcremie-matcha-cream-ribbon-sweet male front, alcremie-matcha-cream-star-sweet female front, alcremie-matcha-cream-star-sweet male front, alcremie-matcha-cream-strawberry-sweet female front, alcremie-matcha-cream-strawberry-sweet male front, alcremie-mint-cream-berry-sweet female front, alcremie-mint-cream-berry-sweet male front, alcremie-mint-cream-clover-sweet female front, alcremie-mint-cream-clover-sweet male front, alcremie-mint-cream-flower-sweet female front, alcremie-mint-cream-flower-sweet male front, alcremie-mint-cream-love-sweet female front, alcremie-mint-cream-love-sweet male front, alcremie-mint-cream-ribbon-sweet female front, alcremie-mint-cream-ribbon-sweet male front, alcremie-mint-cream-star-sweet female front, alcremie-mint-cream-star-sweet male front, alcremie-mint-cream-strawberry-sweet female front, alcremie-mint-cream-strawberry-sweet male front, alcremie-rainbow-swirl-berry-sweet female front, alcremie-rainbow-swirl-berry-sweet male front, alcremie-rainbow-swirl-clover-sweet female front, alcremie-rainbow-swirl-clover-sweet male front, alcremie-rainbow-swirl-flower-sweet female front, alcremie-rainbow-swirl-flower-sweet male front, alcremie-rainbow-swirl-love-sweet female front, alcremie-rainbow-swirl-love-sweet male front, alcremie-rainbow-swirl-ribbon-sweet female front, alcremie-rainbow-swirl-ribbon-sweet male front, alcremie-rainbow-swirl-star-sweet female front, alcremie-rainbow-swirl-star-sweet male front, alcremie-rainbow-swirl-strawberry-sweet female front, alcremie-rainbow-swirl-strawberry-sweet male front, alcremie-ruby-cream-berry-sweet female front, alcremie-ruby-cream-berry-sweet male front, alcremie-ruby-cream-clover-sweet female front, alcremie-ruby-cream-clover-sweet male front, alcremie-ruby-cream-flower-sweet female front, alcremie-ruby-cream-flower-sweet male front, alcremie-ruby-cream-love-sweet female front, alcremie-ruby-cream-love-sweet male front, alcremie-ruby-cream-ribbon-sweet female front, alcremie-ruby-cream-ribbon-sweet male front, alcremie-ruby-cream-star-sweet female front, alcremie-ruby-cream-star-sweet male front, alcremie-ruby-cream-strawberry-sweet female front, alcremie-ruby-cream-strawberry-sweet male front, alcremie-ruby-swirl-berry-sweet female front, alcremie-ruby-swirl-berry-sweet male front, alcremie-ruby-swirl-clover-sweet female front, alcremie-ruby-swirl-clover-sweet male front, alcremie-ruby-swirl-flower-sweet female front, alcremie-ruby-swirl-flower-sweet male front, alcremie-ruby-swirl-love-sweet female front, alcremie-ruby-swirl-love-sweet male front, alcremie-ruby-swirl-ribbon-sweet female front, alcremie-ruby-swirl-ribbon-sweet male front, alcremie-ruby-swirl-star-sweet female front, alcremie-ruby-swirl-star-sweet male front, alcremie-ruby-swirl-strawberry-sweet female front, alcremie-ruby-swirl-strawberry-sweet male front, alcremie-salted-cream-berry-sweet female front, alcremie-salted-cream-berry-sweet male front, alcremie-salted-cream-clover-sweet female front, alcremie-salted-cream-clover-sweet male front, alcremie-salted-cream-flower-sweet female front, alcremie-salted-cream-flower-sweet male front, alcremie-salted-cream-love-sweet female front, alcremie-salted-cream-love-sweet male front, alcremie-salted-cream-ribbon-sweet female front, alcremie-salted-cream-ribbon-sweet male front, alcremie-salted-cream-star-sweet female front, alcremie-salted-cream-star-sweet male front, alcremie-salted-cream-strawberry-sweet female front, alcremie-salted-cream-strawberry-sweet male front, alcremie-vanilla-cream-berry-sweet female front, alcremie-vanilla-cream-berry-sweet male front, alcremie-vanilla-cream-clover-sweet female front, alcremie-vanilla-cream-clover-sweet male front, alcremie-vanilla-cream-flower-sweet female front, alcremie-vanilla-cream-flower-sweet male front, alcremie-vanilla-cream-love-sweet female front, alcremie-vanilla-cream-love-sweet male front, alcremie-vanilla-cream-ribbon-sweet female front, alcremie-vanilla-cream-ribbon-sweet male front, alcremie-vanilla-cream-star-sweet female front, alcremie-vanilla-cream-star-sweet male front, alcremie-vanilla-cream-strawberry-sweet female front, alcremie-vanilla-cream-strawberry-sweet male front, alcremie_mega female front, alcremie_mega male front, alomomola female front, alomomola male front, altaria female front, altaria male front, altaria-mega female front, altaria-mega male front, altaria_redux female front, altaria_redux male front, amaura female front, amaura male front, ambipom female front, ambipom male front, amoonguss female front, amoonguss male front, ampharos female front, ampharos male front, ampharos-mega female front, ampharos-mega male front, amphybuzz female front, amphybuzz male front, amphybuzz_mega female front, amphybuzz_mega male front, annihilape female front, annihilape male front, anorith female front, anorith male front, appletun female front, appletun male front, appletun-gmax female front, appletun-gmax male front, applin female front, applin male front, arachtres female front, arachtres male front, arashinne female front, arashinne male front, arbok female front, arbok male front, arbok_mega female front, arbok_mega male front, arboliva female front, arboliva male front, arcanine female front, arcanine male front, arcanine-hisui female front, arcanine-hisui male front, arcanine_hisuian_mega female front, arcanine_hisuian_mega male front, arcanine_mega female front, arcanine_mega male front, arcanine_mega_redux female front, arcanine_mega_redux male front, arceus-bug female front, arceus-bug male front, arceus-dark female front, arceus-dark male front, arceus-dragon female front, arceus-dragon male front, arceus-electric female front, arceus-electric male front, arceus-fairy female front, arceus-fairy male front, arceus-fighting female front, arceus-fighting male front, arceus-fire female front, arceus-fire male front, arceus-flying female front, arceus-flying male front, arceus-ghost female front, arceus-ghost male front, arceus-grass female front, arceus-grass male front, arceus-ground female front, arceus-ground male front, arceus-ice female front, arceus-ice male front, arceus-normal female front, arceus-normal male front, arceus-poison female front, arceus-poison male front, arceus-psychic female front, arceus-psychic male front, arceus-rock female front, arceus-rock male front, arceus-steel female front, arceus-steel male front, arceus-unknown female front, arceus-unknown male front, arceus-water female front, arceus-water male front, archaludon female front, archaludon male front, archen female front, archen male front, archeops female front, archeops male front, arctibax female front, arctibax male front, arctovish female front, arctovish male front, arctozolt female front, arctozolt male front, ariados female front, ariados male front, armaldo female front, armaldo male front, armarouge female front, armarouge male front, aromatisse female front, aromatisse male front, aron female front, aron male front, aron_redux female front, aron_redux male front, arrokuda female front, arrokuda male front, articuno female front, articuno male front, articuno-galar female front, articuno-galar male front, audino female front, audino male front, audino-mega female front, audino-mega male front, avalugg-hisui female front, avalugg-hisui male front, axew female front, axew male front, azelf female front, azelf male front, azelf_redux female front, azelf_redux male front, azumarill female front, azumarill male front, azurill female front, azurill male front, bagon female front, bagon male front, baltoy female front, baltoy male front, banette female front, banette male front, banette-mega female front, banette-mega male front, barbaracle female front, barbaracle male front, barbaracle-mega female front, barbaracle-mega male front, barbaracle_mega female front, barbaracle_mega male front, barboach female front, barboach male front, bariong female front, bariong male front, barraskewda female front, barraskewda male front, basculegion-female female front, basculegion-female male front, basculegion-male female front, basculegion-male male front, basculin-blue-striped female front, basculin-blue-striped male front, basculin-red-striped female front, basculin-red-striped male front, basculin-white-striped female front, basculin-white-striped male front, bastiodon female front, bastiodon male front, baxcalibur female front, baxcalibur male front, baxcalibur-mega female front, baxcalibur-mega male front, baxcalibur_mega female front, baxcalibur_mega male front, bayleef female front, bayleef male front, beautifly female front, beautifly male front, beedrill female front, beedrill male front, beedrill-mega female front, beedrill-mega male front, beedrill_redux female front, beedrill_redux male front, beefender female front, beefender male front, beheeyem female front, beheeyem male front, beldum female front, beldum male front, bellibolt female front, bellibolt male front, bellossom female front, bellossom male front, bellsprout female front, bellsprout male front, bellsprout_redux female front, bellsprout_redux male front, beniccino female front, beniccino male front, bergmite female front, bergmite male front, bewarden female front, bewarden male front, bewarden_redux female front, bewarden_redux male front, bewear female front, bewear male front, bewear_redux female front, bewear_redux male front, bibarel female front, bibarel male front, bidoof female front, bidoof male front, binacle female front, binacle male front, bisharp female front, bisharp male front, bisharp_redux female front, bisharp_redux male front, blacephalon female front, blacephalon male front, blastoise female front, blastoise male front, blastoise-gmax female front, blastoise-gmax male front, blastoise_mega_x female front, blastoise_mega_x male front, blaziken female front, blaziken male front, blaziken-mega female front, blaziken-mega male front, blipbug female front, blipbug male front, blissey female front, blissey male front, blissey_redux female front, blissey_redux male front, blitzle female front, blitzle male front, blizzard_maw female front, blizzard_maw male front, blocli female front, blocli male front, bloxtack female front, bloxtack male front, boarlock female front, boarlock male front, boldore female front, boldore male front, boltund female front, boltund male front, bombirdier female front, bombirdier male front, bonsly female front, bonsly male front, bouffalant female front, bouffalant male front, bounsweet female front, bounsweet male front, bounsweet_redux female front, bounsweet_redux male front, braixen female front, braixen male front, brambleghast female front, brambleghast male front, bramblin female front, bramblin male front, braviary female front, braviary male front, breezing female front, breezing male front, breloom female front, breloom male front, breloom_mega female front, breloom_mega male front, brionne female front, brionne male front, bronzong female front, bronzong male front, bronzor female front, bronzor male front, brute-bonnet female front, brute-bonnet male front, bruxish female front, bruxish male front, bubbleo female front, bubbleo male front, budew female front, budew male front, buizel female front, buizel male front, buizel_redux female front, buizel_redux male front, bulbasaur female front, bulbasaur male front, buneary female front, buneary male front, bunnelby female front, bunnelby male front, burmy-plant female front, burmy-plant male front, burmy-sandy female front, burmy-sandy male front, burmy-trash female front, burmy-trash male front, buzzwole female front, buzzwole male front, cacjack female front, cacjack male front, cacnea female front, cacnea male front, cacturne female front, cacturne male front, calyrex female front, calyrex male front, calyrex-ice female front, calyrex-ice male front, calyrex-shadow female front, calyrex-shadow male front, calyrex_cloud_rider female front, calyrex_cloud_rider male front, camerupt female front, camerupt male front, camerupt-mega female front, camerupt-mega male front, capsakid female front, capsakid male front, carbink female front, carbink male front, carbonix female front, carbonix male front, carbonix_mega female front, carbonix_mega male front, carkol female front, carkol male front, carnivine female front, carnivine male front, carracosta female front, carracosta male front, carvanha female front, carvanha male front, cascoon female front, cascoon male front, cascoon_primal female front, cascoon_primal male front, castform female front, castform male front, castform-rainy female front, castform-rainy male front, castform-snowy female front, castform-snowy male front, castform-sunny female front, castform-sunny male front, castform_foggy female front, castform_foggy male front, castform_sandy female front, castform_sandy male front, caterpie female front, caterpie male front, celebi female front, celebi male front, celesteela female front, celesteela male front, centiskorch female front, centiskorch male front, centiskorch-gmax female front, centiskorch-gmax male front, centiskorch_mega female front, centiskorch_mega male front, ceruledge female front, ceruledge male front, cetoddle female front, cetoddle male front, cetoddle_redux female front, cetoddle_redux male front, chandelure female front, chandelure male front, chandelure-mega female front, chandelure-mega male front, chandelure_mega female front, chandelure_mega male front, chandelure_mega_y female front, chandelure_mega_y male front, chandelure_redux female front, chandelure_redux male front, chandelure_redux_mega female front, chandelure_redux_mega male front, chansey female front, chansey male front, chansey_redux female front, chansey_redux male front, charcadet female front, charcadet male front, charizard female front, charizard male front, charizard-gmax female front, charizard-gmax male front, charizard-mega-y female front, charizard-mega-y male front, charizard_mega_z female front, charizard_mega_z male front, charjabug female front, charjabug male front, charmander female front, charmander male front, charmeleon female front, charmeleon male front, chatot female front, chatot male front, cherrim-overcast female front, cherrim-overcast male front, cherrim-sunshine female front, cherrim-sunshine male front, cherubi female front, cherubi male front, chesnaught female front, chesnaught male front, chesnaught-mega female front, chesnaught-mega male front, chesnaught_battle_bond female front, chesnaught_battle_bond male front, chesnaught_mega female front, chesnaught_mega male front, chespin female front, chespin male front, chewtle female front, chewtle male front, chi-yu female front, chi-yu male front, chien_pao_mega female front, chien_pao_mega male front, chikorita female front, chikorita male front, chimchar female front, chimchar male front, chimchar_redux female front, chimchar_redux male front, chimecho female front, chimecho male front, chimecho-mega female front, chimecho-mega male front, chimecho_mega female front, chimecho_mega male front, chinchou female front, chinchou male front, chingling female front, chingling male front, cinccino female front, cinccino male front, cinccino_redux female front, cinccino_redux male front, cinderace female front, cinderace male front, cinderace-gmax female front, cinderace-gmax male front, cinderace_mega female front, cinderace_mega male front, clamperl female front, clamperl male front, clauncher female front, clauncher male front, clawitzer female front, clawitzer male front, clawitzer_redux female front, clawitzer_redux male front, claydol female front, claydol male front, clefable female front, clefable male front, clefable-mega female front, clefable-mega male front, clefable_redux female front, clefable_redux male front, clefable_redux_mega female front, clefable_redux_mega male front, clefairy female front, clefairy male front, clefairy_redux female front, clefairy_redux male front, cleffa female front, cleffa male front, cleffa_redux female front, cleffa_redux male front, clobbopus female front, clobbopus male front, clodsire female front, clodsire male front, clodsire_mega female front, clodsire_mega male front, cloyster female front, cloyster male front, coalossal female front, coalossal male front, coalossal-gmax female front, coalossal-gmax male front, coalossal_mega female front, coalossal_mega male front, cobalion female front, cobalion male front, cofagrigus female front, cofagrigus male front, combee female front, combee male front, combusken female front, combusken male front, comfey female front, comfey male front, copperajah female front, copperajah male front, copperajah-gmax female front, copperajah-gmax male front, copperajah_mega female front, copperajah_mega male front, corm female front, corm male front, cormoth female front, cormoth male front, cormoth_mega female front, cormoth_mega male front, corphish female front, corphish male front, corsola female front, corsola male front, corsola-galar female front, corsola-galar male front, corviknight female front, corviknight male front, corviknight-gmax female front, corviknight-gmax male front, corviknight_mega female front, corviknight_mega male front, corvisquire female front, corvisquire male front, cosmoem female front, cosmoem male front, cosmog female front, cosmog male front, cottonee female front, cottonee male front, cpf_0001_caterpie_alternate_form_1 female front, cpf_0001_caterpie_alternate_form_1 male front, cpf_0002_butterfree_alternate_form_1 female front, cpf_0002_butterfree_alternate_form_1 male front, cpf_0003_weedle_alternate_form_2 female front, cpf_0003_weedle_alternate_form_2 male front, cpf_0004_kakuna_alternate_form_2 female front, cpf_0004_kakuna_alternate_form_2 male front, cpf_0005_beedrill_alternate_form_2 female front, cpf_0005_beedrill_alternate_form_2 male front, cpf_0007_pidgey_alternate_form_2 female front, cpf_0007_pidgey_alternate_form_2 male front, cpf_0008_pidgeotto_alternate_form_2 female front, cpf_0008_pidgeotto_alternate_form_2 male front, cpf_0011_clefairy_alternate_form_1 female front, cpf_0011_clefairy_alternate_form_1 male front, cpf_0012_clefable_alternate_form_1 female front, cpf_0012_clefable_alternate_form_1 male front, cpf_0013_vulpix_alternate_form_2 female front, cpf_0013_vulpix_alternate_form_2 male front, cpf_0014_vulpix_alternate_form_3 female front, cpf_0014_vulpix_alternate_form_3 male front, cpf_0015_ninetales_alternate_form_2 female front, cpf_0015_ninetales_alternate_form_2 male front, cpf_0016_ninetales_alternate_form_3 female front, cpf_0016_ninetales_alternate_form_3 male front, cpf_0017_jigglypuff_alternate_form_1 female front, cpf_0017_jigglypuff_alternate_form_1 male front, cpf_0018_wigglytuff_alternate_form_1 female front, cpf_0018_wigglytuff_alternate_form_1 male front, cpf_0019_paras_alternate_form_1 female front, cpf_0019_paras_alternate_form_1 male front, cpf_0020_parasect_alternate_form_1 female front, cpf_0020_parasect_alternate_form_1 male front, cpf_0021_venonat_alternate_form_1 female front, cpf_0021_venonat_alternate_form_1 male front, cpf_0023_poliwag_alternate_form_1 female front, cpf_0023_poliwag_alternate_form_1 male front, cpf_0024_poliwhirl_alternate_form_1 female front, cpf_0024_poliwhirl_alternate_form_1 male front, cpf_0026_abra_alternate_form_1 female front, cpf_0026_abra_alternate_form_1 male front, cpf_0027_abra_alternate_form_2 female front, cpf_0027_abra_alternate_form_2 male front, cpf_0028_kadabra_alternate_form_2 female front, cpf_0028_kadabra_alternate_form_2 male front, cpf_0031_geodude_bluetowel_alternate_forms_form_2 female front, cpf_0031_geodude_bluetowel_alternate_forms_form_2 male front, cpf_0032_graveler_bluetowel_alternate_forms_form_2 female front, cpf_0032_graveler_bluetowel_alternate_forms_form_2 male front, cpf_0033_golem_bluetowel_alternate_forms_form_2 female front, cpf_0033_golem_bluetowel_alternate_forms_form_2 male front, cpf_0034_ponyta_alternate_form_1 female front, cpf_0034_ponyta_alternate_form_1 male front, cpf_0037_slowbro_bluetowel_alternate_forms_form_2 female front, cpf_0037_slowbro_bluetowel_alternate_forms_form_2 male front, cpf_0038_slowbro_mega_alt_form_form_3 female front, cpf_0038_slowbro_mega_alt_form_form_3 male front, cpf_0039_slowbro_bluetowel_alternate_forms_form_4 female front, cpf_0039_slowbro_bluetowel_alternate_forms_form_4 male front, cpf_0040_slowbro_bluetowel_alternate_forms_form_5 female front, cpf_0040_slowbro_bluetowel_alternate_forms_form_5 male front, cpf_0043_doduo_alternate_form_1 female front, cpf_0043_doduo_alternate_form_1 male front, cpf_0045_gastly_alternate_form_2 female front, cpf_0045_gastly_alternate_form_2 male front, cpf_0046_haunter_alternate_form_2 female front, cpf_0046_haunter_alternate_form_2 male front, cpf_0047_gengar_alternate_form_2 female front, cpf_0047_gengar_alternate_form_2 male front, cpf_0050_drowzee_alternate_form_2 female front, cpf_0050_drowzee_alternate_form_2 male front, cpf_0051_hypno_alternate_form_2 female front, cpf_0051_hypno_alternate_form_2 male front, cpf_0052_krabby_alternate_form_2 female front, cpf_0052_krabby_alternate_form_2 male front, cpf_0054_hitmonlee_alternate_form_1 female front, cpf_0054_hitmonlee_alternate_form_1 male front, cpf_0055_hitmonchan_alternate_form_1 female front, cpf_0055_hitmonchan_alternate_form_1 male front, cpf_0056_koffing_bluetowel_alternate_forms_form_2 female front, cpf_0056_koffing_bluetowel_alternate_forms_form_2 male front, cpf_0057_weezing_bluetowel_alternate_forms_form_2 female front, cpf_0057_weezing_bluetowel_alternate_forms_form_2 male front, cpf_0058_chansey_alternate_form_1 female front, cpf_0058_chansey_alternate_form_1 male front, cpf_0059_staryu_alternate_form_1 female front, cpf_0059_staryu_alternate_form_1 male front, cpf_0060_starmie_alternate_form_1 female front, cpf_0060_starmie_alternate_form_1 male front, cpf_0061_electabuzz_alternate_form_1 female front, cpf_0061_electabuzz_alternate_form_1 male front, cpf_0062_magmar_alternate_form_1 female front, cpf_0062_magmar_alternate_form_1 male front, cpf_0063_magikarp_alternate_form_2 female front, cpf_0063_magikarp_alternate_form_2 male front, cpf_0067_jolteon_alternate_form_3 female front, cpf_0067_jolteon_alternate_form_3 male front, cpf_0068_flareon_alternate_form_3 female front, cpf_0068_flareon_alternate_form_3 male front, cpf_0069_espeon_alternate_form_3 female front, cpf_0069_espeon_alternate_form_3 male front, cpf_0070_umbreon_alternate_form_3 female front, cpf_0070_umbreon_alternate_form_3 male front, cpf_0071_leafeon_alternate_form_3 female front, cpf_0071_leafeon_alternate_form_3 male front, cpf_0073_sylveon_alternate_form_3 female front, cpf_0073_sylveon_alternate_form_3 male front, cpf_0074_omanyte_alternate_form_1 female front, cpf_0074_omanyte_alternate_form_1 male front, cpf_0075_omastar_alternate_form_1 female front, cpf_0075_omastar_alternate_form_1 male front, cpf_0076_kabuto_alternate_form_1 female front, cpf_0076_kabuto_alternate_form_1 male front, cpf_0084_bayleef_bluetowel_alternate_form_form_1 female front, cpf_0084_bayleef_bluetowel_alternate_form_form_1 male front, cpf_0085_meganium_alternate_form_1 female front, cpf_0085_meganium_alternate_form_1 male front, cpf_0086_quilava_alternate_form_1 female front, cpf_0086_quilava_alternate_form_1 male front, cpf_0087_typhlosion_alternate_form_1 female front, cpf_0087_typhlosion_alternate_form_1 male front, cpf_0088_typhlosion_alternate_form_2 female front, cpf_0088_typhlosion_alternate_form_2 male front, cpf_0089_croconaw_alternate_form_1 female front, cpf_0089_croconaw_alternate_form_1 male front, cpf_0091_hoothoot_alternate_form_1 female front, cpf_0091_hoothoot_alternate_form_1 male front, cpf_0092_noctowl_alternate_form_1 female front, cpf_0092_noctowl_alternate_form_1 male front, cpf_0093_ledyba_alternate_form_1 female front, cpf_0093_ledyba_alternate_form_1 male front, cpf_0094_ledian_alternate_form_1 female front, cpf_0094_ledian_alternate_form_1 male front, cpf_0095_natu_alternate_form_1 female front, cpf_0095_natu_alternate_form_1 male front, cpf_0096_xatu_alternate_form_1 female front, cpf_0096_xatu_alternate_form_1 male front, cpf_0097_flaaffy_alternate_form_2 female front, cpf_0097_flaaffy_alternate_form_2 male front, cpf_0098_ampharos_alternate_form_2 female front, cpf_0098_ampharos_alternate_form_2 male front, cpf_0100_politoed_alternate_form_1 female front, cpf_0100_politoed_alternate_form_1 male front, cpf_0101_sunflora_alternate_form_1 female front, cpf_0101_sunflora_alternate_form_1 male front, cpf_0102_sunflora_alternate_form_2 female front, cpf_0102_sunflora_alternate_form_2 male front, cpf_0105_wooper_alternate_form_1 female front, cpf_0105_wooper_alternate_form_1 male front, cpf_0107_slowking_bluetowel_alternate_forms_form_2 female front, cpf_0107_slowking_bluetowel_alternate_forms_form_2 male front, cpf_0108_misdreavus_alternate_form_2 female front, cpf_0108_misdreavus_alternate_form_2 male front, cpf_0109_mismagius_alternate_form_2 female front, cpf_0109_mismagius_alternate_form_2 male front, cpf_0110_girafarig_bluetowel_alternate_form_form_1 female front, cpf_0110_girafarig_bluetowel_alternate_form_form_1 male front, cpf_0111_dunsparce_bt_alt_forms_toxic_form_1 female front, cpf_0111_dunsparce_bt_alt_forms_toxic_form_1 male front, cpf_0112_dunsparce_bt_alt_forms_earth_form_2 female front, cpf_0112_dunsparce_bt_alt_forms_earth_form_2 male front, cpf_0113_dunsparce_bt_alt_forms_sky_form_3 female front, cpf_0113_dunsparce_bt_alt_forms_sky_form_3 male front, cpf_0114_dunsparce_bt_alt_forms_insect_form_4 female front, cpf_0114_dunsparce_bt_alt_forms_insect_form_4 male front, cpf_0115_dunsparce_bt_alt_forms_spooky_form_5 female front, cpf_0115_dunsparce_bt_alt_forms_spooky_form_5 male front, cpf_0119_snubbull_alternate_form_1 female front, cpf_0119_snubbull_alternate_form_1 male front, cpf_0120_granbull_alternate_form_1 female front, cpf_0120_granbull_alternate_form_1 male front, cpf_0121_corsola_alternate_form_1 female front, cpf_0121_corsola_alternate_form_1 male front, cpf_0122_sneasel_alternate_form_1 female front, cpf_0122_sneasel_alternate_form_1 male front, cpf_0123_sneasel_alternate_form_2 female front, cpf_0123_sneasel_alternate_form_2 male front, cpf_0124_weavile_alternate_form_1 female front, cpf_0124_weavile_alternate_form_1 male front, cpf_0125_remoraid_alternate_form_1 female front, cpf_0125_remoraid_alternate_form_1 male front, cpf_0126_octillery_alternate_form_1 female front, cpf_0126_octillery_alternate_form_1 male front, cpf_0127_phanpy_alternate_form_1 female front, cpf_0127_phanpy_alternate_form_1 male front, cpf_0128_donphan_alternate_form_1 female front, cpf_0128_donphan_alternate_form_1 male front, cpf_0129_hitmontop_alternate_form_1 female front, cpf_0129_hitmontop_alternate_form_1 male front, cpf_0130_blissey_alternate_form_1 female front, cpf_0130_blissey_alternate_form_1 male front, cpf_0131_larvitar_ice_form_2 female front, cpf_0131_larvitar_ice_form_2 male front, cpf_0132_larvitar_space_form_4 female front, cpf_0132_larvitar_space_form_4 male front, cpf_0133_pupitar_ice_form_2 female front, cpf_0133_pupitar_ice_form_2 male front, cpf_0134_pupitar_space_form_4 female front, cpf_0134_pupitar_space_form_4 male front, cpf_0139_grovyle_alternate_form_2 female front, cpf_0139_grovyle_alternate_form_2 male front, cpf_0142_combusken_alternate_form_2 female front, cpf_0142_combusken_alternate_form_2 male front, cpf_0143_blaziken_alternate_mega_form_2 female front, cpf_0143_blaziken_alternate_mega_form_2 male front, cpf_0145_swampert_alternate_mega_form_2 female front, cpf_0145_swampert_alternate_mega_form_2 male front, cpf_0146_swampert_alternate_mega_form_3 female front, cpf_0146_swampert_alternate_mega_form_3 male front, cpf_0148_ralts_alternate_form_3 female front, cpf_0148_ralts_alternate_form_3 male front, cpf_0152_breloom_alternate_form_2 female front, cpf_0152_breloom_alternate_form_2 male front, cpf_0153_breloom_alternate_form_3 female front, cpf_0153_breloom_alternate_form_3 male front, cpf_0154_skitty_alternate_form_1 female front, cpf_0154_skitty_alternate_form_1 male front, cpf_0155_delcatty_alternate_form_1 female front, cpf_0155_delcatty_alternate_form_1 male front, cpf_0156_sableye_alternate_gemstone_form_2 female front, cpf_0156_sableye_alternate_gemstone_form_2 male front, cpf_0157_sableye_alternate_gemstone_mega_form_3 female front, cpf_0157_sableye_alternate_gemstone_mega_form_3 male front, cpf_0158_sableye_alternate_darkness_form_4 female front, cpf_0158_sableye_alternate_darkness_form_4 male front, cpf_0159_sableye_alternate_darkness_mega_form_5 female front, cpf_0159_sableye_alternate_darkness_mega_form_5 male front, cpf_0161_swalot_alternate_form_2 female front, cpf_0161_swalot_alternate_form_2 male front, cpf_0162_wailmer_alternate_form_1 female front, cpf_0162_wailmer_alternate_form_1 male front, cpf_0164_numel_alternate_form_3 female front, cpf_0164_numel_alternate_form_3 male front, cpf_0165_camerupt_alternate_form_3 female front, cpf_0165_camerupt_alternate_form_3 male front, cpf_0166_camerupt_mega_alternate_form_4 female front, cpf_0166_camerupt_mega_alternate_form_4 male front, cpf_0167_electrike_alternate_form_2 female front, cpf_0167_electrike_alternate_form_2 male front, cpf_0168_manectric_alternate_form_2 female front, cpf_0168_manectric_alternate_form_2 male front, cpf_0169_manectric_mega_alternate_form_3 female front, cpf_0169_manectric_mega_alternate_form_3 male front, cpf_0170_grumpig_alternate_form_1 female front, cpf_0170_grumpig_alternate_form_1 male front, cpf_0171_trapinch_alternate_form_1 female front, cpf_0171_trapinch_alternate_form_1 male front, cpf_0172_vibrava_alternate_form_1 female front, cpf_0172_vibrava_alternate_form_1 male front, cpf_0176_baltoy_alternate_form_1 female front, cpf_0176_baltoy_alternate_form_1 male front, cpf_0177_claydol_alternate_form_1 female front, cpf_0177_claydol_alternate_form_1 male front, cpf_0178_lileep_alternate_form_1 female front, cpf_0178_lileep_alternate_form_1 male front, cpf_0179_cradily_alternate_form_1 female front, cpf_0179_cradily_alternate_form_1 male front, cpf_0180_anorith_alternate_form_1 female front, cpf_0180_anorith_alternate_form_1 male front, cpf_0181_armaldo_alternate_form_1 female front, cpf_0181_armaldo_alternate_form_1 male front, cpf_0183_chingling_alternate_form_1 female front, cpf_0183_chingling_alternate_form_1 male front, cpf_0184_chimecho_alternate_form_1 female front, cpf_0184_chimecho_alternate_form_1 male front, cpf_0185_absol_alternate_form_2 female front, cpf_0185_absol_alternate_form_2 male front, cpf_0187_bagon_alternate_form_2 female front, cpf_0187_bagon_alternate_form_2 male front, cpf_0188_shelgon_alternate_form_2 female front, cpf_0188_shelgon_alternate_form_2 male front, cpf_0189_salamence_alternate_form_1 female front, cpf_0189_salamence_alternate_form_1 male front, cpf_0191_salamence_alternate_mega_form_3 female front, cpf_0191_salamence_alternate_mega_form_3 male front, cpf_0192_beldum_alternate_form_2 female front, cpf_0192_beldum_alternate_form_2 male front, cpf_0193_metang_alternate_form_2 female front, cpf_0193_metang_alternate_form_2 male front, cpf_0201_cranidos_alternate_form_1 female front, cpf_0201_cranidos_alternate_form_1 male front, cpf_0202_rampardos_alternate_form_1 female front, cpf_0202_rampardos_alternate_form_1 male front, cpf_0203_shieldon_alternate_form_1 female front, cpf_0203_shieldon_alternate_form_1 male front, cpf_0204_bastiodon_alternate_form_1 female front, cpf_0204_bastiodon_alternate_form_1 male front, cpf_0205_combee_alternate_form_1 female front, cpf_0205_combee_alternate_form_1 male front, cpf_0206_vespiquen_alternate_form_1 female front, cpf_0206_vespiquen_alternate_form_1 male front, cpf_0207_pachirisu_alternate_form_1 female front, cpf_0207_pachirisu_alternate_form_1 male front, cpf_0208_buneary_alternate_form_2 female front, cpf_0208_buneary_alternate_form_2 male front, cpf_0209_lopunny_bluetowel_alternate_forms_form_1 female front, cpf_0209_lopunny_bluetowel_alternate_forms_form_1 male front, cpf_0210_lopunny_alternate_form_2 female front, cpf_0210_lopunny_alternate_form_2 male front, cpf_0211_lopunny_alternate_mega_form_3 female front, cpf_0211_lopunny_alternate_mega_form_3 male front, cpf_0212_spiritomb_alternate_form_1 female front, cpf_0212_spiritomb_alternate_form_1 male front, cpf_0213_gible_bluetowel_alternate_forms_form_2 female front, cpf_0213_gible_bluetowel_alternate_forms_form_2 male front, cpf_0214_gabite_bluetowel_alternate_forms_form_2 female front, cpf_0214_gabite_bluetowel_alternate_forms_form_2 male front, cpf_0215_garchomp_bluetowel_alternate_forms_form_1 female front, cpf_0215_garchomp_bluetowel_alternate_forms_form_1 male front, cpf_0217_garchomp_alternate_mega_form_3 female front, cpf_0217_garchomp_alternate_mega_form_3 male front, cpf_0219_glameow_alternate_form_1 female front, cpf_0219_glameow_alternate_form_1 male front, cpf_0220_purugly_alternate_form_1 female front, cpf_0220_purugly_alternate_form_1 male front, cpf_0221_skorupi_alternate_form_1 female front, cpf_0221_skorupi_alternate_form_1 male front, cpf_0222_skorupi_alternate_form_2 female front, cpf_0222_skorupi_alternate_form_2 male front, cpf_0224_carnivine_bluetowel_alternate_form_form_1 female front, cpf_0224_carnivine_bluetowel_alternate_form_form_1 male front, cpf_0230_gligar_alternate_form_1 female front, cpf_0230_gligar_alternate_form_1 male front, cpf_0232_nosepass_alternate_form_1 female front, cpf_0232_nosepass_alternate_form_1 male front, cpf_0233_probopass_alternate_form_1 female front, cpf_0233_probopass_alternate_form_1 male front, cpf_0234_dusclops_alternate_form_1 female front, cpf_0234_dusclops_alternate_form_1 male front, cpf_0242_pignite_alternate_form_1 female front, cpf_0242_pignite_alternate_form_1 male front, cpf_0246_munna_alternate_form_1 female front, cpf_0246_munna_alternate_form_1 male front, cpf_0247_musharna_alternate_form_1 female front, cpf_0247_musharna_alternate_form_1 male front, cpf_0248_pidove_alternate_form_1 female front, cpf_0248_pidove_alternate_form_1 male front, cpf_0249_tranquill_alternate_form_1 female front, cpf_0249_tranquill_alternate_form_1 male front, cpf_0251_roggenrola_alternate_form_1 female front, cpf_0251_roggenrola_alternate_form_1 male front, cpf_0252_boldore_alternate_form_1 female front, cpf_0252_boldore_alternate_form_1 male front, cpf_0253_timburr_alternate_form_1 female front, cpf_0253_timburr_alternate_form_1 male front, cpf_0256_purrloin_alternate_form_1 female front, cpf_0256_purrloin_alternate_form_1 male front, cpf_0257_liepard_alternate_form_1 female front, cpf_0257_liepard_alternate_form_1 male front, cpf_0258_petilil_alternate_form_1 female front, cpf_0258_petilil_alternate_form_1 male front, cpf_0259_petilil_alternate_form_2 female front, cpf_0259_petilil_alternate_form_2 male front, cpf_0260_lilligant_alternate_form_1 female front, cpf_0260_lilligant_alternate_form_1 male front, cpf_0261_lilligant_alternate_form_2 female front, cpf_0261_lilligant_alternate_form_2 male front, cpf_0262_sandile_alternate_form_1 female front, cpf_0262_sandile_alternate_form_1 male front, cpf_0263_krokorok_alternate_form_1 female front, cpf_0263_krokorok_alternate_form_1 male front, cpf_0265_dwebble_alternate_form_1 female front, cpf_0265_dwebble_alternate_form_1 male front, cpf_0266_crustle_alternate_form_1 female front, cpf_0266_crustle_alternate_form_1 male front, cpf_0267_yamask_alternate_form_1 female front, cpf_0267_yamask_alternate_form_1 male front, cpf_0268_yamask_alternate_form_2 female front, cpf_0268_yamask_alternate_form_2 male front, cpf_0270_tirtouga_alternate_form_1 female front, cpf_0270_tirtouga_alternate_form_1 male front, cpf_0271_carracosta_alternate_form_1 female front, cpf_0271_carracosta_alternate_form_1 male front, cpf_0272_archen_alternate_form_1 female front, cpf_0272_archen_alternate_form_1 male front, cpf_0274_trubbish_alternate_form_1 female front, cpf_0274_trubbish_alternate_form_1 male front, cpf_0276_solosis_alternate_form_1 female front, cpf_0276_solosis_alternate_form_1 male front, cpf_0277_duosion_alternate_form_1 female front, cpf_0277_duosion_alternate_form_1 male front, cpf_0278_reuniclus_alternate_form_1 female front, cpf_0278_reuniclus_alternate_form_1 male front, cpf_0279_vanillite_alternate_form_1 female front, cpf_0279_vanillite_alternate_form_1 male front, cpf_0280_vanillish_alternate_form_1 female front, cpf_0280_vanillish_alternate_form_1 male front, cpf_0281_vanilluxe_alternate_form_1 female front, cpf_0281_vanilluxe_alternate_form_1 male front, cpf_0283_ferroseed_alternate_form_1 female front, cpf_0283_ferroseed_alternate_form_1 male front, cpf_0285_klang_alternate_form_1 female front, cpf_0285_klang_alternate_form_1 male front, cpf_0286_klinklang_alternate_form_1 female front, cpf_0286_klinklang_alternate_form_1 male front, cpf_0287_eelektrik_alternate_form_1 female front, cpf_0287_eelektrik_alternate_form_1 male front, cpf_0289_litwick_alternate_form_1 female front, cpf_0289_litwick_alternate_form_1 male front, cpf_0290_lampent_alternate_form_1 female front, cpf_0290_lampent_alternate_form_1 male front, cpf_0291_chandelure_alternate_form_1 female front, cpf_0291_chandelure_alternate_form_1 male front, cpf_0292_cryogonal_alternate_form_1 female front, cpf_0292_cryogonal_alternate_form_1 male front, cpf_0293_accelgor_alternate_form_1 female front, cpf_0293_accelgor_alternate_form_1 male front, cpf_0294_mienfoo_bluetowel_alternate_form_form_1 female front, cpf_0294_mienfoo_bluetowel_alternate_form_form_1 male front, cpf_0296_druddigon_alternate_form_1 female front, cpf_0296_druddigon_alternate_form_1 male front, cpf_0297_golett_alternate_form_1 female front, cpf_0297_golett_alternate_form_1 male front, cpf_0298_golurk_alternate_form_1 female front, cpf_0298_golurk_alternate_form_1 male front, cpf_0299_pawniard_alternate_form_1 female front, cpf_0299_pawniard_alternate_form_1 male front, cpf_0300_bisharp_alternate_form_1 female front, cpf_0300_bisharp_alternate_form_1 male front, cpf_0301_durant_bluetowel_alternate_form_form_1 female front, cpf_0301_durant_bluetowel_alternate_form_form_1 male front, cpf_0302_deino_cybertank_form_1 female front, cpf_0302_deino_cybertank_form_1 male front, cpf_0303_deino_telepathic_form_2 female front, cpf_0303_deino_telepathic_form_2 male front, cpf_0309_delphox_alternate_form_1 female front, cpf_0309_delphox_alternate_form_1 male front, cpf_0311_bunnelby_alternate_form_1 female front, cpf_0311_bunnelby_alternate_form_1 male front, cpf_0313_spritzee_alternate_form_1 female front, cpf_0313_spritzee_alternate_form_1 male front, cpf_0314_spritzee_alternate_form_2 female front, cpf_0314_spritzee_alternate_form_2 male front, cpf_0315_aromatisse_alternate_form_1 female front, cpf_0315_aromatisse_alternate_form_1 male front, cpf_0316_aromatisse_alternate_form_2 female front, cpf_0316_aromatisse_alternate_form_2 male front, cpf_0318_skrelp_alternate_form_1 female front, cpf_0318_skrelp_alternate_form_1 male front, cpf_0320_clauncher_alternate_form_1 female front, cpf_0320_clauncher_alternate_form_1 male front, cpf_0322_tyrunt_alternate_form_1 female front, cpf_0322_tyrunt_alternate_form_1 male front, cpf_0326_dedenne_alternate_form_1 female front, cpf_0326_dedenne_alternate_form_1 male front, cpf_0327_goomy_alternate_form_1 female front, cpf_0327_goomy_alternate_form_1 male front, cpf_0328_sliggoo_alternate_form_1 female front, cpf_0328_sliggoo_alternate_form_1 male front, cpf_0329_sliggoo_alternate_form_2 female front, cpf_0329_sliggoo_alternate_form_2 male front, cpf_0332_noibat_alternate_form_1 female front, cpf_0332_noibat_alternate_form_1 male front, cpf_0334_dartrix_alternate_form_1 female front, cpf_0334_dartrix_alternate_form_1 male front, cpf_0335_dartrix_alternate_form_2 female front, cpf_0335_dartrix_alternate_form_2 male front, cpf_0337_decidueye_alternate_form_2 female front, cpf_0337_decidueye_alternate_form_2 male front, cpf_0340_ribombee_bluetowel_alternate_form_form_1 female front, cpf_0340_ribombee_bluetowel_alternate_form_form_1 male front, cpf_0341_ribombee_bluetowel_alternate_form_form_2 female front, cpf_0341_ribombee_bluetowel_alternate_form_form_2 male front, cpf_0342_dewpider_alternate_form_1 female front, cpf_0342_dewpider_alternate_form_1 male front, cpf_0344_fomantis_alternate_form_1 female front, cpf_0344_fomantis_alternate_form_1 male front, cpf_0345_lurantis_alternate_form_1 female front, cpf_0345_lurantis_alternate_form_1 male front, cpf_0346_sandygast_alternate_form_1 female front, cpf_0346_sandygast_alternate_form_1 male front, cpf_0347_palossand_alternate_form_1 female front, cpf_0347_palossand_alternate_form_1 male front, cpf_0348_hakamo_o_alternate_form_1 female front, cpf_0348_hakamo_o_alternate_form_1 male front, cpf_0350_thwackey_alternate_form_2 female front, cpf_0350_thwackey_alternate_form_2 male front, cpf_0352_scorbunny_alternate_form_2 female front, cpf_0352_scorbunny_alternate_form_2 male front, cpf_0353_raboot_alternate_form_2 female front, cpf_0353_raboot_alternate_form_2 male front, cpf_0354_cinderace_alternate_form_2 female front, cpf_0354_cinderace_alternate_form_2 male front, cpf_0355_sobble_alternate_form_2 female front, cpf_0355_sobble_alternate_form_2 male front, cpf_0357_inteleon_alternate_form_2 female front, cpf_0357_inteleon_alternate_form_2 male front, cpf_0358_arrokuda_alternate_form_1 female front, cpf_0358_arrokuda_alternate_form_1 male front, cpf_0359_barraskewda_alternate_form_1 female front, cpf_0359_barraskewda_alternate_form_1 male front, crabominable female front, crabominable male front, crabominable_redux female front, crabominable_redux male front, crabrawler_redux female front, crabrawler_redux male front, crabruiser_redux female front, crabruiser_redux male front, cradily female front, cradily male front, cramorant female front, cramorant male front, cramorant-gorging female front, cramorant-gorging male front, cramorant-gulping female front, cramorant-gulping male front, cranidos female front, cranidos male front, crawdaunt female front, crawdaunt male front, crawdauntles female front, crawdauntles male front, cresselia female front, cresselia male front, croagunk female front, croagunk male front, crobat female front, crobat male front, crobat_mega female front, crobat_mega male front, crocalor female front, crocalor male front, croconaw female front, croconaw male front, crustle female front, crustle male front, cryogonal female front, cryogonal male front, cubchoo female front, cubchoo male front, cubone female front, cubone male front, cufant female front, cufant male front, cursola female front, cursola male front, cutiefly female front, cutiefly male front, cyclizar female front, cyclizar male front, cyndaquil female front, cyndaquil male front, dachsbun female front, dachsbun male front, darkrai female front, darkrai male front, darkrai-mega female front, darkrai-mega male front, darkrai_mega female front, darkrai_mega male front, darmanitan-galar-standard female front, darmanitan-galar-standard male front, darmanitan-galar-zen female front, darmanitan-galar-zen male front, darmanitan-standard female front, darmanitan-standard male front, darmanitan-zen female front, darmanitan-zen male front, darmanitan_redux female front, darmanitan_redux male front, darmanitan_redux_aura female front, darmanitan_redux_aura male front, darmanitan_redux_blunder female front, darmanitan_redux_blunder male front, darmanitan_redux_bond female front, darmanitan_redux_bond male front, dartrix female front, dartrix male front, darumaka female front, darumaka male front, darumaka-galar female front, darumaka-galar male front, darumaka_redux female front, darumaka_redux male front, decidueye female front, decidueye male front, decidueye-hisui female front, decidueye-hisui male front, decidueye_hisuian_mega female front, decidueye_hisuian_mega male front, decidueye_mega female front, decidueye_mega male front, dedelibird female front, dedelibird male front, dedenne female front, dedenne male front, deerling-autumn female front, deerling-autumn male front, deerling-spring female front, deerling-spring male front, deerling-summer female front, deerling-summer male front, deerling-winter female front, deerling-winter male front, deino female front, deino male front, deino_redux female front, deino_redux male front, delcatty female front, delcatty male front, delibird female front, delibird male front, delphox female front, delphox male front, delphox-mega female front, delphox-mega male front, delphox_battle_bond female front, delphox_battle_bond male front, delphox_mega female front, delphox_mega male front, delphox_serena female front, delphox_serena male front, deoxys-attack female front, deoxys-attack male front, deoxys-defense female front, deoxys-defense male front, deoxys-normal female front, deoxys-normal male front, dewgong_mega female front, dewgong_mega male front, dewgong_redux female front, dewgong_redux male front, dewott female front, dewott male front, dewpider female front, dewpider male front, dewpider_redux female front, dewpider_redux male front, dhelmise female front, dhelmise male front, dialga female front, dialga male front, dialga-origin female front, dialga-origin male front, diancie female front, diancie male front, diancie-mega female front, diancie-mega male front, diglett female front, diglett male front, diglett-alola female front, diglett-alola male front, dipplin female front, dipplin male front, ditto female front, ditto male front, dodrio female front, dodrio male front, dodrio_redux female front, dodrio_redux male front, doduo female front, doduo male front, doduo_redux female front, doduo_redux male front, dolliv female front, dolliv male front, dondozo female front, dondozo male front, donphan female front, donphan male front, dottler female front, dottler male front, dracovish female front, dracovish male front, dracozolt female front, dracozolt male front, dragalge female front, dragalge male front, dragalge-mega female front, dragalge-mega male front, dragalge_mega female front, dragalge_mega male front, dragapult female front, dragapult male front, dragapult_mega female front, dragapult_mega male front, dragonair female front, dragonair male front, dragonite female front, dragonite male front, dragonite-mega female front, dragonite-mega male front, dragonite_mega female front, dragonite_mega male front, dragonite_mega_y female front, dragonite_mega_y male front, drakloak female front, drakloak male front, drampa-mega female front, drampa-mega male front, drampa_mega female front, drampa_mega male front, drapion female front, drapion male front, dratini female front, dratini male front, dreadnaut female front, dreadnaut male front, drednaw female front, drednaw male front, drednaw-gmax female front, drednaw-gmax male front, drednaw_mega female front, drednaw_mega male front, dredwood female front, dredwood male front, dreepy female front, dreepy male front, drifblim female front, drifblim male front, drifloon female front, drifloon male front, drilbur female front, drilbur male front, drilbur_redux female front, drilbur_redux male front, drizzile female front, drizzile male front, drowzee female front, drowzee male front, druddigon female front, druddigon male front, dubwool female front, dubwool male front, ducklett female front, ducklett male front, dududunsparce female front, dududunsparce male front, dududunsparce_mega female front, dududunsparce_mega male front, dudunsparce-three-segment female front, dudunsparce-three-segment male front, dudunsparce-two-segment female front, dudunsparce-two-segment male front, duelumber female front, duelumber male front, dugtrio female front, dugtrio male front, dugtrio-alola female front, dugtrio-alola male front, dunsparce female front, dunsparce male front, duosion female front, duosion male front, duosion_redux female front, duosion_redux male front, duraludon female front, duraludon male front, duraludon-gmax female front, duraludon-gmax male front, durant female front, durant male front, dusclops female front, dusclops male front, duskull female front, duskull male front, dustox female front, dustox male front, dwebble female front, dwebble male front, earthretha_apprensith female front, earthretha_apprensith male front, earthretha_belstatue female front, earthretha_belstatue male front, earthretha_belstatue_1 female front, earthretha_belstatue_1 male front, earthretha_belstatue_2 female front, earthretha_belstatue_2 male front, earthretha_bombghost female front, earthretha_bombghost male front, earthretha_cubchestra female front, earthretha_cubchestra male front, earthretha_gloom_1 female front, earthretha_gloom_1 male front, earthretha_incineroar_1 female front, earthretha_incineroar_1 male front, earthretha_keenstar female front, earthretha_keenstar male front, earthretha_mimiegg female front, earthretha_mimiegg male front, earthretha_museon female front, earthretha_museon male front, earthretha_oddish_1 female front, earthretha_oddish_1 male front, earthretha_pangshi female front, earthretha_pangshi male front, earthretha_seegel female front, earthretha_seegel male front, earthretha_thiefire female front, earthretha_thiefire male front, earthretha_treesmas female front, earthretha_treesmas male front, earthretha_venonat_1 female front, earthretha_venonat_1 male front, earthretha_vileplume_1 female front, earthretha_vileplume_1 male front, eelektrik female front, eelektrik male front, eevee female front, eevee male front, eevee-gmax female front, eevee-gmax male front, eevee-starter female front, eevee-starter male front, eevee_partner_mega female front, eevee_partner_mega male front, eiscue-ice female front, eiscue-ice male front, eiscue-noice female front, eiscue-noice male front, ekans female front, ekans male front, eldegoss female front, eldegoss male front, electabuzz female front, electabuzz male front, electrike female front, electrike male front, electrode female front, electrode male front, electrode-hisui female front, electrode-hisui male front, elekid female front, elekid male front, elgyem female front, elgyem male front, emboar female front, emboar male front, emboar_mega female front, emboar_mega male front, emolga female front, emolga male front, empoleon female front, empoleon male front, empoleon_mega female front, empoleon_mega male front, empoleon_redux_mega female front, empoleon_redux_mega male front, enamorus-incarnate female front, enamorus-incarnate male front, enamorus-therian female front, enamorus-therian male front, entei female front, entei male front, eraticate female front, eraticate male front, escarginite female front, escarginite male front, escarginite_redux female front, escarginite_redux male front, escavalier female front, escavalier male front, espathra female front, espathra male front, espeon female front, espeon male front, espurr female front, espurr male front, eternatus female front, eternatus male front, eternatus-eternamax female front, eternatus-eternamax male front, excadrill-mega female front, excadrill-mega male front, excadrill_mega female front, excadrill_mega male front, excadrill_redux female front, excadrill_redux male front, exeggcute female front, exeggcute male front, exeggcute_redux female front, exeggcute_redux male front, exeggutor female front, exeggutor male front, exeggutor_redux female front, exeggutor_redux male front, exploud female front, exploud male front, exploud_redux female front, exploud_redux male front, falinks female front, falinks male front, falinks-mega female front, falinks-mega male front, falinks_mega female front, falinks_mega male front, farfetchd female front, farfetchd male front, feebas female front, feebas male front, fennekin female front, fennekin male front, feraligatr female front, feraligatr male front, feraligatr-mega female front, feraligatr-mega male front, feraligatr_mega_x female front, feraligatr_mega_x male front, feraligatr_mega_y female front, feraligatr_mega_y male front, ferroseed female front, ferroseed male front, ferrothorn female front, ferrothorn male front, fidough female front, fidough male front, finizen female front, finizen male front, finneon female front, finneon male front, flaaffy female front, flaaffy male front, flabebe-blue female front, flabebe-blue male front, flabebe-orange female front, flabebe-orange male front, flabebe-red female front, flabebe-red male front, flabebe-white female front, flabebe-white male front, flabebe-yellow female front, flabebe-yellow male front, flairgrance female front, flairgrance male front, flamigo female front, flamigo male front, flapple female front, flapple male front, flapple-gmax female front, flapple-gmax male front, flareon female front, flareon male front, fletchinder female front, fletchinder male front, fletchling female front, fletchling male front, flittle female front, flittle male front, floatzel female front, floatzel male front, floette-blue female front, floette-blue male front, floette-eternal female front, floette-eternal male front, floette-orange female front, floette-orange male front, floette-red female front, floette-red male front, floette-white female front, floette-white male front, floette-yellow female front, floette-yellow male front, floragato female front, floragato male front, florges-blue female front, florges-blue male front, florges-orange female front, florges-orange male front, florges-red female front, florges-red male front, florges-white female front, florges-white male front, florges-yellow female front, florges-yellow male front, fluffbee female front, fluffbee male front, flutter-mane female front, flutter-mane male front, flygon female front, flygon male front, flygon_redux female front, flygon_redux male front, flygon_redux_b female front, flygon_redux_b male front, flygon_redux_b_mega female front, flygon_redux_b_mega male front, fogging female front, fogging male front, fomantis female front, fomantis male front, foongus female front, foongus male front, forretress female front, forretress male front, fraxure female front, fraxure male front, frigibax female front, frigibax male front, frillish-female female front, frillish-female male front, frillish-male female front, frillish-male male front, froakie female front, froakie male front, frogadier female front, frogadier male front, froslass female front, froslass male front, froslass-mega female front, froslass-mega male front, froslass_redux female front, froslass_redux male front, frosmoth female front, frosmoth male front, frostuccino female front, frostuccino male front, fuecoco female front, fuecoco male front, furfrou-dandy female front, furfrou-dandy male front, furfrou-debutante female front, furfrou-debutante male front, furfrou-diamond female front, furfrou-diamond male front, furfrou-heart female front, furfrou-heart male front, furfrou-kabuki female front, furfrou-kabuki male front, furfrou-la-reine female front, furfrou-la-reine male front, furfrou-matron female front, furfrou-matron male front, furfrou-natural female front, furfrou-natural male front, furfrou-pharaoh female front, furfrou-pharaoh male front, furfrou-star female front, furfrou-star male front, furret female front, furret male front, gabite female front, gabite male front, gabite_redux female front, gabite_redux male front, gallade female front, gallade male front, gallade_redux female front, gallade_redux male front, gallade_redux_mega female front, gallade_redux_mega male front, galvantula female front, galvantula male front, garbodor female front, garbodor male front, garbodor-gmax female front, garbodor-gmax male front, garbodor_mega female front, garbodor_mega male front, garchomp female front, garchomp male front, garchomp-mega female front, garchomp-mega male front, garchomp_mega_z female front, garchomp_mega_z male front, gardevoir female front, gardevoir male front, gardevoir-mega female front, gardevoir-mega male front, gardevoir_redux female front, gardevoir_redux male front, gardevoir_redux_mega female front, gardevoir_redux_mega male front, gargablox female front, gargablox male front, garganacl female front, garganacl male front, gastly female front, gastly male front, gastrodon-east female front, gastrodon-east male front, gastrodon-west female front, gastrodon-west male front, genesect female front, genesect male front, genesect-burn female front, genesect-burn male front, genesect-chill female front, genesect-chill male front, genesect-douse female front, genesect-douse male front, genesect-shock female front, genesect-shock male front, gengar female front, gengar male front, gengar-gmax female front, gengar-gmax male front, gengar-mega female front, gengar-mega male front, gengar_mega_x female front, gengar_mega_x male front, geodude female front, geodude male front, geodude-alola female front, geodude-alola male front, gholdengo female front, gholdengo male front, gible female front, gible male front, gible_redux female front, gible_redux male front, gigalith female front, gigalith male front, gimmighoul-chest female front, gimmighoul-chest male front, gimmighoul-roaming female front, gimmighoul-roaming male front, girafarig female front, girafarig male front, giratina-altered female front, giratina-altered male front, giratina-origin female front, giratina-origin male front, glalie female front, glalie male front, glalie-mega female front, glalie-mega male front, glalie_redux female front, glalie_redux male front, glalie_redux_mega female front, glalie_redux_mega male front, glameow female front, glameow male front, gligar female front, gligar male front, gligar_redux female front, gligar_redux male front, glimmet female front, glimmet male front, glimmora female front, glimmora male front, glimmora-mega female front, glimmora-mega male front, gliscor female front, gliscor male front, gliscor_redux female front, gliscor_redux male front, gloom female front, gloom male front, gogoat female front, gogoat male front, golbat female front, golbat male front, goldeen female front, goldeen male front, golduck female front, golduck male front, golem female front, golem male front, golem-alola female front, golem-alola male front, golett female front, golett male front, golisopod female front, golisopod male front, golisopod-mega female front, golisopod-mega male front, golisopod_mega_y female front, golisopod_mega_y male front, golurk female front, golurk male front, goodra female front, goodra male front, goodra-hisui female front, goodra-hisui male front, goodra_mega female front, goodra_mega male front, goomy female front, goomy male front, gooschase female front, gooschase male front, gossifleur female front, gossifleur male front, gothita female front, gothita male front, gothitelle female front, gothitelle male front, gothitelle_mega female front, gothitelle_mega male front, gothorita female front, gothorita male front, gouging-fire female front, gouging-fire male front, gourgeist-average female front, gourgeist-average male front, gourgeist-large female front, gourgeist-large male front, gourgeist-small female front, gourgeist-small male front, gourgeist-super female front, gourgeist-super male front, grafaiai female front, grafaiai male front, granbull female front, granbull male front, granitun female front, granitun male front, grapploct female front, grapploct male front, graveler female front, graveler male front, graveler-alola female front, graveler-alola male front, great-tusk female front, great-tusk male front, greavard female front, greavard male front, greedent female front, greedent male front, greninja female front, greninja male front, greninja-ash female front, greninja-ash male front, greninja-battle-bond female front, greninja-battle-bond male front, greninja-mega female front, greninja-mega male front, greninja_mega female front, greninja_mega male front, grimer female front, grimer male front, grimer-alola female front, grimer-alola male front, grimmsnarl female front, grimmsnarl male front, grimmsnarl-gmax female front, grimmsnarl-gmax male front, grimmsnarl_mega female front, grimmsnarl_mega male front, grookey female front, grookey male front, grotle female front, grotle male front, grotle_redux female front, grotle_redux male front, grotom female front, grotom male front, grotom_drum female front, grotom_drum male front, grotom_fill female front, grotom_fill male front, grotom_glass female front, grotom_glass male front, grotom_kick female front, grotom_kick male front, grotom_roll female front, grotom_roll male front, groudon female front, groudon male front, groudon-primal female front, groudon-primal male front, grovyle female front, grovyle male front, growlithe female front, growlithe male front, growlithe-hisui female front, growlithe-hisui male front, growlithe_redux female front, growlithe_redux male front, grubbin female front, grubbin male front, grumpig female front, grumpig male front, guardozel female front, guardozel male front, gulpin female front, gulpin male front, gumshoos female front, gumshoos male front, gurdurr female front, gurdurr male front, gyaradeath female front, gyaradeath male front, gyaradeath_mega_x female front, gyaradeath_mega_x male front, gyaradeath_mega_y female front, gyaradeath_mega_y male front, gyarados female front, gyarados male front, gyarados_mega_y female front, gyarados_mega_y male front, gyarevalry female front, gyarevalry male front, hakamo-o female front, hakamo-o male front, happiny female front, happiny male front, happiny_redux female front, happiny_redux male front, hariyama female front, hariyama male front, hariyama_mega female front, hariyama_mega male front, hariyama_redux female front, hariyama_redux male front, harvesting_tyrant female front, harvesting_tyrant male front, hatenna female front, hatenna male front, hatterene female front, hatterene male front, hatterene-gmax female front, hatterene-gmax male front, hatterene_mega female front, hatterene_mega male front, hattrem female front, hattrem male front, haunter female front, haunter male front, hawlucha female front, hawlucha male front, hawlucha-mega female front, hawlucha-mega male front, hawlucha_mega female front, hawlucha_mega male front, haxorus female front, haxorus male front, heatmor female front, heatmor male front, heatran female front, heatran male front, heatran-mega female front, heatran-mega male front, heatran_mega female front, heatran_mega male front, heliolisk female front, heliolisk male front, helioptile female front, helioptile male front, heliosunny female front, heliosunny male front, heracreus female front, heracreus male front, heracross female front, heracross male front, heracross-mega female front, heracross-mega male front, herdier female front, herdier male front, hippopotas female front, hippopotas male front, hippopotato female front, hippopotato male front, hippotaton female front, hippotaton male front, hippowdon female front, hippowdon male front, hitmonchan female front, hitmonchan male front, hitmonchan_mega female front, hitmonchan_mega male front, hitmonlee female front, hitmonlee male front, hitmonlee_mega female front, hitmonlee_mega male front, hitmontop female front, hitmontop male front, hitmontop_mega female front, hitmontop_mega male front, honchkrow female front, honchkrow male front, honedge female front, honedge male front, hoopa female front, hoopa male front, hoopa-unbound female front, hoopa-unbound male front, hoothoot female front, hoothoot male front, hoppip female front, hoppip male front, horsea female front, horsea male front, houndoom female front, houndoom male front, houndoom-mega female front, houndoom-mega male front, houndoom_mega_redux female front, houndoom_mega_redux male front, houndoom_redux female front, houndoom_redux male front, houndour female front, houndour male front, houndour_redux female front, houndour_redux male front, houndstone female front, houndstone male front, hydrapple female front, hydrapple male front, hydreigon female front, hydreigon male front, hydreigon_mega female front, hydreigon_mega male front, hydroar female front, hydroar male front, hypno female front, hypno male front, hypnocroak female front, hypnocroak male front, igglybuff female front, igglybuff male front, illumise female front, illumise male front, impidimp female front, impidimp male front, incineroar female front, incineroar male front, incineroar_mega female front, incineroar_mega male front, indeedee-female female front, indeedee-female male front, indeedee-male female front, indeedee-male male front, infernape female front, infernape male front, infernape_mega female front, infernape_mega male front, infernape_redux female front, infernape_redux male front, infernape_redux_mega female front, infernape_redux_mega male front, inkay female front, inkay male front, inteleon female front, inteleon male front, inteleon-gmax female front, inteleon-gmax male front, inteleon_mega female front, inteleon_mega male front, iron-boulder female front, iron-boulder male front, iron-bundle female front, iron-bundle male front, iron-crown female front, iron-crown male front, iron-hands female front, iron-hands male front, iron-jugulis female front, iron-jugulis male front, iron-leaves female front, iron-leaves male front, iron-moth female front, iron-moth male front, iron-thorns female front, iron-thorns male front, iron-treads female front, iron-treads male front, iron-valiant female front, iron-valiant male front, ivysaur female front, ivysaur male front, jagged_chungulis female front, jagged_chungulis male front, jangmo-o female front, jangmo-o male front, jellicent-female female front, jellicent-female male front, jellicent-male female front, jellicent-male male front, jigglypuff female front, jigglypuff male front, jirachi female front, jirachi male front, jolteon female front, jolteon male front, joltik female front, joltik male front, jumpluff female front, jumpluff male front, jynx female front, jynx male front, kabuto female front, kabuto male front, kadabra female front, kadabra male front, kadabra_redux female front, kadabra_redux male front, kakuna female front, kakuna male front, kakuna_redux female front, kakuna_redux male front, kangaskhan female front, kangaskhan male front, kangaskhan-mega female front, kangaskhan-mega male front, karrablast female front, karrablast male front, kartana female front, kartana male front, kecleon female front, kecleon male front, kecleong female front, kecleong male front, keldeo-ordinary female front, keldeo-ordinary male front, keldeo-resolute female front, keldeo-resolute male front, kilowattrel female front, kilowattrel male front, kilozuna female front, kilozuna male front, kilozuna_mega female front, kilozuna_mega male front, kingambit female front, kingambit male front, kingambit_redux female front, kingambit_redux male front, kingdra female front, kingdra male front, kingler female front, kingler male front, kingler_redux female front, kingler_redux male front, kipmodo female front, kipmodo male front, kirlia female front, kirlia male front, kirlia_redux female front, kirlia_redux male front, klang female front, klang male front, kleavor_mega female front, kleavor_mega male front, kleavor_redux_mega female front, kleavor_redux_mega male front, klefki female front, klefki male front, klefki_redux female front, klefki_redux male front, klink female front, klink male front, klinklang female front, klinklang male front, koffing female front, koffing male front, komala female front, komala male front, kommo-o female front, kommo-o male front, koraidon-apex-build female front, koraidon-apex-build male front, krabby female front, krabby male front, krabby_redux female front, krabby_redux male front, krampird female front, krampird male front, kricketot female front, kricketot male front, kricketune female front, kricketune male front, krokorok female front, krokorok male front, krookodile female front, krookodile male front, krookodile_mega female front, krookodile_mega male front, kubfu female front, kubfu male front, kyogre female front, kyogre male front, kyogre-primal female front, kyogre-primal male front, kyurem female front, kyurem male front, kyurem-black female front, kyurem-black male front, lairon female front, lairon male front, lairon_redux female front, lairon_redux male front, lampent female front, lampent male front, landorus-incarnate female front, landorus-incarnate male front, landorus-therian female front, landorus-therian male front, lanturn female front, lanturn male front, lanturn_mega female front, lanturn_mega male front, lapras female front, lapras male front, lapras-gmax female front, lapras-gmax male front, lapras_mega female front, lapras_mega male front, larvesta female front, larvesta male front, larvesta_redux female front, larvesta_redux male front, larvitar female front, larvitar male front, larvitar_redux female front, larvitar_redux male front, latios female front, latios male front, leafeon female front, leafeon male front, leavanny female front, leavanny male front, lechonk female front, lechonk male front, ledian female front, ledian male front, ledyba female front, ledyba male front, lepastry female front, lepastry male front, lickilicky female front, lickilicky male front, lickitung female front, lickitung male front, lileep female front, lileep male front, lilligant female front, lilligant male front, lilligant-hisui female front, lilligant-hisui male front, lillipup female front, lillipup male front, linoone female front, linoone male front, linoone-galar female front, linoone-galar male front, litleo female front, litleo male front, litten female front, litten male front, litwick female front, litwick male front, litwick_redux female front, litwick_redux male front, lokix female front, lokix male front, lombre female front, lombre male front, lopunny female front, lopunny male front, lopunny-mega female front, lopunny-mega male front, lotad female front, lotad male front, loudred female front, loudred male front, loudred_redux female front, loudred_redux male front, lucario female front, lucario male front, lucario-mega female front, lucario-mega male front, lucario-mega-z female front, lucario-mega-z male front, lucario_mega_z female front, lucario_mega_z male front, ludicolo female front, ludicolo male front, lugia female front, lugia male front, lumbering_sloth female front, lumbering_sloth male front, lumbering_sloth_engulfed female front, lumbering_sloth_engulfed male front, lumineon female front, lumineon male front, luminositeon female front, luminositeon male front, lunatone female front, lunatone male front, lurantis female front, lurantis male front, luvdisc female front, luvdisc male front, luxio female front, luxio male front, luxio_redux female front, luxio_redux male front, luxray_redux female front, luxray_redux male front, lycanroc-dusk female front, lycanroc-dusk male front, lycanroc-midday female front, lycanroc-midday male front, lycanroc-midnight female front, lycanroc-midnight male front, lycanroc_eclipse female front, lycanroc_eclipse male front, lycanroc_twilight female front, lycanroc_twilight male front, mabosstiff female front, mabosstiff male front, machamp_mega_redux female front, machamp_mega_redux male front, machamp_redux female front, machamp_redux male front, machoke female front, machoke male front, machoke_redux female front, machoke_redux male front, machop female front, machop male front, machop_redux female front, machop_redux male front, magby female front, magby male front, magcargo female front, magcargo male front, magcargo_redux female front, magcargo_redux male front, magearna female front, magearna male front, magearna-original female front, magearna-original male front, magearna_mega female front, magearna_mega male front, magikarp female front, magikarp male front, magmar female front, magmar male front, magmenous female front, magmenous male front, magmortar female front, magmortar male front, magnemite female front, magnemite male front, magneton female front, magneton male front, makuhita female front, makuhita male front, makuhita_redux female front, makuhita_redux male front, malamar female front, malamar male front, malamar_mega female front, malamar_mega male front, mamoswine female front, mamoswine male front, mamoswine_redux female front, mamoswine_redux male front, mamoswine_redux_mega female front, mamoswine_redux_mega male front, manaphy female front, manaphy male front, mandibuzz female front, mandibuzz male front, manectric female front, manectric male front, manectric-mega female front, manectric-mega male front, mankey female front, mankey male front, mantine female front, mantine male front, mantyke female front, mantyke male front, maractus female front, maractus male front, marbeep female front, marbeep male front, mareanie female front, mareanie male front, mareep female front, mareep male front, marill female front, marill male front, marowak female front, marowak male front, marowak-alola female front, marowak-alola male front, marshadow female front, marshadow male front, marshmodo female front, marshmodo male front, marshtomp female front, marshtomp male front, maschiff female front, maschiff male front, maushold-family-of-four female front, maushold-family-of-four male front, maushold-family-of-three female front, maushold-family-of-three male front, mawile female front, mawile male front, mawile-mega female front, mawile-mega male front, mawile_mega_redux female front, mawile_mega_redux male front, mawile_redux female front, mawile_redux male front, mawile_redux_b_mega female front, mawile_redux_b_mega male front, medicham female front, medicham male front, medicham-mega female front, medicham-mega male front, meditite female front, meditite male front, mega_froslass female front, mega_froslass male front, mega_infernape female front, mega_infernape male front, mega_mamoswine female front, mega_mamoswine male front, mega_porygon female front, mega_porygon male front, mega_roserade female front, mega_roserade male front, mega_spiritomb female front, mega_spiritomb male front, mega_weavile female front, mega_weavile male front, meganium female front, meganium male front, meganium-mega female front, meganium-mega male front, meganium_mega female front, meganium_mega male front, melmetal-gmax female front, melmetal-gmax male front, melmetal_mega female front, melmetal_mega male front, meloetta-aria female front, meloetta-aria male front, meloetta-pirouette female front, meloetta-pirouette male front, meltan female front, meltan male front, meowscarada female front, meowscarada male front, meowscarada_mega female front, meowscarada_mega male front, meowstic-female female front, meowstic-female male front, meowstic-male female front, meowstic-male male front, meowstic-mega female front, meowstic-mega male front, meowstic_mega female front, meowstic_mega male front, meowth female front, meowth male front, meowth-alola female front, meowth-alola male front, meowth-galar female front, meowth-galar male front, meowth-gmax female front, meowth-gmax male front, meowth_partner female front, meowth_partner male front, meowth_partner_mega female front, meowth_partner_mega male front, merrykarp female front, merrykarp male front, mesprit female front, mesprit male front, metapod female front, metapod male front, mew female front, mew male front, mewtwo female front, mewtwo male front, mewtwo-mega-x female front, mewtwo-mega-x male front, mewtwo-mega-y female front, mewtwo-mega-y male front, mienfoo female front, mienfoo male front, mienshao female front, mienshao male front, milcery female front, milcery male front, milotic_mega female front, milotic_mega male front, miltank female front, miltank male front, mime-jr female front, mime-jr male front, mimikyu-busted female front, mimikyu-busted male front, mimikyu-disguised female front, mimikyu-disguised male front, mimikyu_apex female front, mimikyu_apex male front, mimikyu_apex_busted female front, mimikyu_apex_busted male front, mimikyu_rayquaza_busted female front, mimikyu_rayquaza_busted male front, minccino female front, minccino male front, minccino_redux female front, minccino_redux male front, minior-blue female front, minior-blue male front, minior-blue-meteor female front, minior-blue-meteor male front, minior-green female front, minior-green male front, minior-green-meteor female front, minior-green-meteor male front, minior-indigo female front, minior-indigo male front, minior-indigo-meteor female front, minior-indigo-meteor male front, minior-orange female front, minior-orange male front, minior-orange-meteor female front, minior-orange-meteor male front, minior-red female front, minior-red male front, minior-red-meteor female front, minior-red-meteor male front, minior-violet female front, minior-violet male front, minior-violet-meteor female front, minior-violet-meteor male front, minior-yellow female front, minior-yellow male front, minior-yellow-meteor female front, minior-yellow-meteor male front, minun female front, minun male front, miraidon-ultimate-mode female front, miraidon-ultimate-mode male front, misdreavus female front, misdreavus male front, mismagius female front, mismagius male front, moltres female front, moltres male front, moltres-galar female front, moltres-galar male front, moltres_ex female front, moltres_ex male front, monferno female front, monferno male front, monferno_redux female front, monferno_redux male front, morelull female front, morelull male front, morgrem female front, morgrem male front, morpeko-full-belly female front, morpeko-full-belly male front, morpeko-hangry female front, morpeko-hangry male front, morpekyll female front, morpekyll male front, morpekyll_hangry female front, morpekyll_hangry male front, mothim-plant female front, mothim-plant male front, mothim-sandy female front, mothim-sandy male front, mothim-trash female front, mothim-trash male front, mr-mime female front, mr-mime male front, mr-mime-galar female front, mr-mime-galar male front, mr-rime female front, mr-rime male front, mudbray female front, mudbray male front, mudkip female front, mudkip male front, mudsdale female front, mudsdale male front, muk-alola female front, muk-alola male front, munchlax female front, munchlax male front, munchlax_redux female front, munchlax_redux male front, munkidori female front, munkidori male front, munna female front, munna male front, murkrow female front, murkrow male front, nacli female front, nacli male front, naclstack female front, naclstack male front, naganadel female front, naganadel male front, natu female front, natu male front, necrozma female front, necrozma male front, necrozma-dawn female front, necrozma-dawn male front, necrozma-ultra female front, necrozma-ultra male front, nickit female front, nickit male front, nidoking female front, nidoking male front, nidoking_mega female front, nidoking_mega male front, nidoqueen female front, nidoqueen male front, nidoqueen_mega female front, nidoqueen_mega male front, nidoran-f female front, nidoran-f male front, nidoran-m female front, nidoran-m male front, nidorina female front, nidorina male front, nidorino female front, nidorino male front, nihilego female front, nihilego male front, nincada female front, nincada male front, ninetales female front, ninetales male front, ninetales-alola female front, ninetales-alola male front, ninjask female front, ninjask male front, noctowl female front, noctowl male front, noibat female front, noibat male front, noibat_redux female front, noibat_redux male front, noivern female front, noivern male front, noivern_redux female front, noivern_redux male front, nosepass female front, nosepass male front, numel female front, numel male front, nuzleaf female front, nuzleaf male front, nymble female front, nymble male front, obstagoon female front, obstagoon male front, octillery female front, octillery male front, oddish female front, oddish male front, ogerpon female front, ogerpon male front, ogerpon-cornerstone-mask female front, ogerpon-cornerstone-mask male front, ogerpon-hearthflame-mask female front, ogerpon-hearthflame-mask male front, ogerpon-wellspring-mask female front, ogerpon-wellspring-mask male front, oinkologne-female female front, oinkologne-female male front, oinkologne-male female front, oinkologne-male male front, okidogi female front, okidogi male front, omanyte female front, omanyte male front, omastar female front, omastar male front, oranguru female front, oranguru male front, orbeetle female front, orbeetle male front, orbeetle-gmax female front, orbeetle-gmax male front, orbeetle_mega female front, orbeetle_mega male front, orchestot female front, orchestot male front, oricorio-baile female front, oricorio-baile male front, oricorio-pau female front, oricorio-pau male front, oricorio-pom-pom female front, oricorio-pom-pom male front, oricorio-sensu female front, oricorio-sensu male front, oricorio_mega female front, oricorio_mega male front, oshawott female front, oshawott male front, overqwil female front, overqwil male front, pachirisu female front, pachirisu male front, palafin-hero female front, palafin-hero male front, palafin-zero female front, palafin-zero male front, palkia female front, palkia male front, palkia-origin female front, palkia-origin male front, palossand female front, palossand male front, palpitoad female front, palpitoad male front, pancham female front, pancham male front, panpour female front, panpour male front, panpour_redux female front, panpour_redux male front, pansage female front, pansage male front, pansage_redux female front, pansage_redux male front, pansear female front, pansear male front, pansear_redux female front, pansear_redux male front, paras female front, paras male front, parasect female front, parasect male front, passimian female front, passimian male front, patrat female front, patrat male front, pawmi female front, pawmi male front, pawmo female front, pawmo male front, pawmot female front, pawmot male front, pawniard female front, pawniard male front, pawniard_redux female front, pawniard_redux male front, pecharunt female front, pecharunt male front, pentadug female front, pentadug male front, pentadug_alolan female front, pentadug_alolan male front, pentawug female front, pentawug male front, perrserker female front, perrserker male front, persian-alola female front, persian-alola male front, petilil female front, petilil male front, phanfernal female front, phanfernal male front, phanpy female front, phanpy male front, phantowl female front, phantowl male front, phantump female front, phantump male front, pheromosa female front, pheromosa male front, phione female front, phione male front, pichu female front, pichu male front, pichu-spiky-eared female front, pichu-spiky-eared male front, pidgeot female front, pidgeot male front, pidgeotto female front, pidgeotto male front, pidgey female front, pidgey male front, pidove female front, pidove male front, pignite female front, pignite male front, pikachu female front, pikachu male front, pikachu-alola-cap female front, pikachu-alola-cap male front, pikachu-belle female front, pikachu-belle male front, pikachu-cosplay female front, pikachu-cosplay male front, pikachu-gmax female front, pikachu-gmax male front, pikachu-hoenn-cap female front, pikachu-hoenn-cap male front, pikachu-kalos-cap female front, pikachu-kalos-cap male front, pikachu-libre female front, pikachu-libre male front, pikachu-original-cap female front, pikachu-original-cap male front, pikachu-partner-cap female front, pikachu-partner-cap male front, pikachu-phd female front, pikachu-phd male front, pikachu-pop-star female front, pikachu-pop-star male front, pikachu-rock-star female front, pikachu-rock-star male front, pikachu-sinnoh-cap female front, pikachu-sinnoh-cap male front, pikachu-unova-cap female front, pikachu-unova-cap male front, pikachu-world-cap female front, pikachu-world-cap male front, pikachu_partner_mega female front, pikachu_partner_mega male front, pikipek female front, pikipek male front, piloswine female front, piloswine male front, piloswine_redux female front, piloswine_redux male front, pincurchin female front, pincurchin male front, pineco female front, pineco male front, pinsir female front, pinsir male front, piplup female front, piplup male front, piplup_redux female front, piplup_redux male front, plundertow female front, plundertow male front, plusle female front, plusle male front, poipole female front, poipole male front, polartic female front, polartic male front, politoed female front, politoed male front, poliwag female front, poliwag male front, poliwhirl female front, poliwhirl male front, poliwrath female front, poliwrath male front, poltchageist-artisan female front, poltchageist-artisan male front, poltchageist-counterfeit female front, poltchageist-counterfeit male front, polteageist-antique female front, polteageist-antique male front, polteageist-phony female front, polteageist-phony male front, ponyta female front, ponyta male front, ponyta-galar female front, ponyta-galar male front, poochyena female front, poochyena male front, popcorm female front, popcorm male front, popplio female front, popplio male front, porygon female front, porygon male front, porygon-z female front, porygon-z male front, porygon2 female front, porygon2 male front, primarina female front, primarina male front, primarina_mega female front, primarina_mega male front, prinplup female front, prinplup male front, prinplup_redux female front, prinplup_redux male front, probopass female front, probopass male front, psyduck female front, psyduck male front, psyduck_redux female front, psyduck_redux male front, pumpkaboo-average female front, pumpkaboo-average male front, pumpkaboo-large female front, pumpkaboo-large male front, pumpkaboo-small female front, pumpkaboo-small male front, pumpkaboo-super female front, pumpkaboo-super male front, pupitar female front, pupitar male front, pupitar_redux female front, pupitar_redux male front, purrloin female front, purrloin male front, purugly female front, purugly male front, pyroar-female female front, pyroar-female male front, pyroar-male female front, pyroar-male male front, pyroar-mega female front, pyroar-mega male front, pyroar_mega female front, pyroar_mega male front, pyukumuku female front, pyukumuku male front, quagsire female front, quagsire male front, quagsire_mega female front, quagsire_mega male front, quaquaval female front, quaquaval male front, quaquaval_mega female front, quaquaval_mega male front, quaxly female front, quaxly male front, quaxwell female front, quaxwell male front, queengambit female front, queengambit male front, quilava female front, quilava male front, quilladin female front, quilladin male front, qwilfish female front, qwilfish male front, qwilfish-hisui female front, qwilfish-hisui male front, raboot female front, raboot male front, rabsca female front, rabsca male front, raging-bolt female front, raging-bolt male front, raichu female front, raichu male front, raichu-alola female front, raichu-alola male front, raichu-mega-x female front, raichu-mega-x male front, raichu_mega_y female front, raichu_mega_y male front, raikou female front, raikou male front, ralts female front, ralts male front, ralts_redux female front, ralts_redux male front, rampardos female front, rampardos male front, rapidash female front, rapidash male front, ratfioso female front, ratfioso male front, raticate female front, raticate male front, raticate-alola female front, raticate-alola male front, raticate_redux female front, raticate_redux male front, ratiking female front, ratiking male front, rattata female front, rattata male front, rattata-alola female front, rattata-alola male front, rattata_redux female front, rattata_redux male front, rayquaza female front, rayquaza male front, rayquaza-mega female front, rayquaza-mega male front, regice female front, regice male front, regidrago female front, regidrago male front, regieleki female front, regieleki male front, regigigas female front, regigigas male front, regirock female front, regirock male front, registeel female front, registeel male front, relicanth female front, relicanth male front, relicanth_mega female front, relicanth_mega male front, rellor female front, rellor male front, remoraid female front, remoraid male front, reshiram female front, reshiram male front, reuniclus_redux_mega female front, reuniclus_redux_mega male front, rexcadrill female front, rexcadrill male front, rhydon female front, rhydon male front, rhyhorn female front, rhyhorn male front, rhyperior female front, rhyperior male front, ribombee_mega female front, ribombee_mega male front, ribombee_redux female front, ribombee_redux male front, ribombee_redux_mega female front, ribombee_redux_mega male front, rillaboom female front, rillaboom male front, rillaboom-gmax female front, rillaboom-gmax male front, rillaboom_mega female front, rillaboom_mega male front, riolu female front, riolu male front, roaring-moon female front, roaring-moon male front, rockruff female front, rockruff male front, rockruff-own-tempo female front, rockruff-own-tempo male front, roggenrola female front, roggenrola male front, rolycoly female front, rolycoly male front, rookidee female front, rookidee male front, roselia female front, roselia male front, roserade female front, roserade male front, roserade_mega female front, roserade_mega male front, rotom female front, rotom male front, rotom-fan female front, rotom-fan male front, rotom-frost female front, rotom-frost male front, rotom-heat female front, rotom-heat male front, rotom-mow female front, rotom-mow male front, rotom-wash female front, rotom-wash male front, rowlet female front, rowlet male front, rufflet female front, rufflet male front, sableye female front, sableye male front, sableye-mega female front, sableye-mega male front, sableye_redux female front, sableye_redux male front, sagaracas female front, sagaracas male front, salamence female front, salamence male front, salamence-mega female front, salamence-mega male front, salandit female front, salandit male front, salazarus female front, salazarus male front, salazzle female front, salazzle male front, samurott_hisuian_mega female front, samurott_hisuian_mega male front, samurott_mega female front, samurott_mega male front, sandaconda female front, sandaconda male front, sandaconda-gmax female front, sandaconda-gmax male front, sandaconda_mega female front, sandaconda_mega male front, sandile female front, sandile male front, sandshrew female front, sandshrew male front, sandshrew-alola female front, sandshrew-alola male front, sandslash female front, sandslash male front, sandslash-alola female front, sandslash-alola male front, sandslash_alolan_mega female front, sandslash_alolan_mega male front, sandslash_mega female front, sandslash_mega male front, sandy-shocks female front, sandy-shocks male front, sandygast female front, sandygast male front, sawk female front, sawk male front, sawk_redux female front, sawk_redux male front, sawsbuck-autumn female front, sawsbuck-autumn male front, sawsbuck-spring female front, sawsbuck-spring male front, sawsbuck-winter female front, sawsbuck-winter male front, scatterbug-archipelago female front, scatterbug-archipelago male front, scatterbug-continental female front, scatterbug-continental male front, scatterbug-elegant female front, scatterbug-elegant male front, scatterbug-fancy female front, scatterbug-fancy male front, scatterbug-garden female front, scatterbug-garden male front, scatterbug-high-plains female front, scatterbug-high-plains male front, scatterbug-icy-snow female front, scatterbug-icy-snow male front, scatterbug-jungle female front, scatterbug-jungle male front, scatterbug-marine female front, scatterbug-marine male front, scatterbug-meadow female front, scatterbug-meadow male front, scatterbug-modern female front, scatterbug-modern male front, scatterbug-monsoon female front, scatterbug-monsoon male front, scatterbug-ocean female front, scatterbug-ocean male front, scatterbug-poke-ball female front, scatterbug-poke-ball male front, scatterbug-polar female front, scatterbug-polar male front, scatterbug-river female front, scatterbug-river male front, scatterbug-sandstorm female front, scatterbug-sandstorm male front, scatterbug-savanna female front, scatterbug-savanna male front, scatterbug-sun female front, scatterbug-sun male front, scatterbug-tundra female front, scatterbug-tundra male front, sceptile female front, sceptile male front, sceptile-mega female front, sceptile-mega male front, scizor female front, scizor male front, scizor_redux female front, scizor_redux male front, scizor_redux_mega female front, scizor_redux_mega male front, scolipede female front, scolipede male front, scolipede-mega female front, scolipede-mega male front, scolipede_mega female front, scolipede_mega male front, scorbunny female front, scorbunny male front, scovillain female front, scovillain male front, scovillain-mega female front, scovillain-mega male front, scovillain_mega female front, scovillain_mega male front, scrafster female front, scrafster male front, scrafty female front, scrafty male front, scrafty-mega female front, scrafty-mega male front, scrafty_mega female front, scrafty_mega male front, scraggy female front, scraggy male front, scream-tail female front, scream-tail male front, scyther female front, scyther male front, scyther_mega female front, scyther_mega male front, scyther_redux female front, scyther_redux male front, scyther_redux_mega female front, scyther_redux_mega male front, seadra female front, seadra male front, seaking female front, seaking male front, sealeo female front, sealeo male front, seedot female front, seedot male front, seel female front, seel male front, seel_redux female front, seel_redux male front, seerkat female front, seerkat male front, selenumbra female front, selenumbra male front, sentret female front, sentret male front, serperior female front, serperior male front, serperior_mega female front, serperior_mega male front, servine female front, servine male front, sewaddle female front, sewaddle male front, sharpedo female front, sharpedo male front, sharpedo-mega female front, sharpedo-mega male front, shaymin-land female front, shaymin-land male front, shaymin-sky female front, shaymin-sky male front, shedinja female front, shedinja male front, shedinja_mega female front, shedinja_mega male front, shelgon female front, shelgon male front, shellder female front, shellder male front, shellos-east female front, shellos-east male front, shellos-west female front, shellos-west male front, shelmet female front, shelmet male front, shieldon female front, shieldon male front, shiftry female front, shiftry male front, shiinotic female front, shiinotic male front, shinx female front, shinx male front, shinx_redux female front, shinx_redux male front, shroodle female front, shroodle male front, shroomish female front, shroomish male front, shuckle female front, shuckle male front, shuckle_mega female front, shuckle_mega male front, shuppet female front, shuppet male front, shyduck female front, shyduck male front, sigilyph female front, sigilyph male front, silcoon female front, silcoon male front, silicobra female front, silicobra male front, silvally-bug female front, silvally-bug male front, silvally-dark female front, silvally-dark male front, silvally-dragon female front, silvally-dragon male front, silvally-electric female front, silvally-electric male front, silvally-fairy female front, silvally-fairy male front, silvally-fighting female front, silvally-fighting male front, silvally-fire female front, silvally-fire male front, silvally-flying female front, silvally-flying male front, silvally-ghost female front, silvally-ghost male front, silvally-grass female front, silvally-grass male front, silvally-ground female front, silvally-ground male front, silvally-ice female front, silvally-ice male front, silvally-normal female front, silvally-normal male front, silvally-poison female front, silvally-poison male front, silvally-psychic female front, silvally-psychic male front, silvally-rock female front, silvally-rock male front, silvally-steel female front, silvally-steel male front, silvally-water female front, silvally-water male front, simipour female front, simipour male front, simipour_redux female front, simipour_redux male front, simisage female front, simisage male front, simisage_redux female front, simisage_redux male front, simisear female front, simisear male front, sinistcha-masterpiece female front, sinistcha-masterpiece male front, sinistcha-unremarkable female front, sinistcha-unremarkable male front, sinistea-antique female front, sinistea-antique male front, sinistea-phony female front, sinistea-phony male front, sinistea_redux female front, sinistea_redux male front, sirfetchd female front, sirfetchd male front, sizzlipede female front, sizzlipede male front, skarmory female front, skarmory male front, skarmory-mega female front, skarmory-mega male front, skarmory_mega female front, skarmory_mega male front, skarmory_mega_y female front, skarmory_mega_y male front, skarmory_redux female front, skarmory_redux male front, skeledirge_mega female front, skeledirge_mega male front, skiddo female front, skiddo male front, skiploom female front, skiploom male front, skitty female front, skitty male front, skorupi female front, skorupi male front, skrelp female front, skrelp male front, skuntank female front, skuntank male front, skwovet female front, skwovet male front, slaking_mega female front, slaking_mega male front, slaking_mega_ape_shift female front, slaking_mega_ape_shift male front, slakoth female front, slakoth male front, slate female front, slate male front, sliggoo female front, sliggoo male front, sliggoo-hisui female front, sliggoo-hisui male front, slither-wing female front, slither-wing male front, slowbro female front, slowbro male front, slowbro-galar female front, slowbro-galar male front, slowbro-mega female front, slowbro-mega male front, slowbro_mega_galarian female front, slowbro_mega_galarian male front, slowking female front, slowking male front, slowking-galar female front, slowking-galar male front, slowking_mega female front, slowking_mega male front, slowking_mega_galarian female front, slowking_mega_galarian male front, slowpoke female front, slowpoke male front, slowpoke-galar female front, slowpoke-galar male front, slugma female front, slugma male front, slugma_redux female front, slugma_redux male front, slurpuff female front, slurpuff male front, smeargle female front, smeargle male front, smoliv female front, smoliv male front, smoochum female front, smoochum male front, sneasel female front, sneasel male front, sneasel-hisui female front, sneasel-hisui male front, sneasler female front, sneasler male front, sneasler_mega female front, sneasler_mega male front, snivy female front, snivy male front, snom female front, snom male front, snorlax-gmax female front, snorlax-gmax male front, snorlax_mega female front, snorlax_mega male front, snorlax_redux female front, snorlax_redux male front, snorlax_redux_mega female front, snorlax_redux_mega male front, snorunt female front, snorunt male front, snorunt_redux female front, snorunt_redux male front, snover female front, snover male front, snubbull female front, snubbull male front, sobble female front, sobble male front, solgaleo female front, solgaleo male front, solosis female front, solosis male front, solosis_redux female front, solosis_redux male front, solrock female front, solrock male front, solrock_system female front, solrock_system male front, sopranice female front, sopranice male front, spearow female front, spearow male front, spearow_redux female front, spearow_redux male front, spectrier female front, spectrier male front, spectrier_cloud female front, spectrier_cloud male front, spewpa-archipelago female front, spewpa-archipelago male front, spewpa-continental female front, spewpa-continental male front, spewpa-elegant female front, spewpa-elegant male front, spewpa-fancy female front, spewpa-fancy male front, spewpa-garden female front, spewpa-garden male front, spewpa-high-plains female front, spewpa-high-plains male front, spewpa-icy-snow female front, spewpa-icy-snow male front, spewpa-jungle female front, spewpa-jungle male front, spewpa-marine female front, spewpa-marine male front, spewpa-meadow female front, spewpa-meadow male front, spewpa-modern female front, spewpa-modern male front, spewpa-monsoon female front, spewpa-monsoon male front, spewpa-ocean female front, spewpa-ocean male front, spewpa-poke-ball female front, spewpa-poke-ball male front, spewpa-polar female front, spewpa-polar male front, spewpa-river female front, spewpa-river male front, spewpa-sandstorm female front, spewpa-sandstorm male front, spewpa-savanna female front, spewpa-savanna male front, spewpa-sun female front, spewpa-sun male front, spewpa-tundra female front, spewpa-tundra male front, spheal female front, spheal male front, spidops female front, spidops male front, spinarak female front, spinarak male front, spinda female front, spinda male front, spindaze female front, spindaze male front, spiritomb female front, spiritomb male front, spiritomb_redux female front, spiritomb_redux male front, spoink female front, spoink male front, sprigatito female front, sprigatito male front, spritzee female front, spritzee male front, squawkabilly-blue-plumage female front, squawkabilly-blue-plumage male front, squawkabilly-green-plumage female front, squawkabilly-green-plumage male front, squawkabilly-white-plumage female front, squawkabilly-white-plumage male front, squawkabilly-yellow-plumage female front, squawkabilly-yellow-plumage male front, squirtle female front, squirtle male front, stakataka female front, stakataka male front, stantler female front, stantler male front, staraptor female front, staraptor male front, staraptor-mega female front, staraptor-mega male front, staraptor_mega female front, staraptor_mega male front, staravia female front, staravia male front, starly female front, starly male front, starmie female front, starmie male front, starmie-mega female front, starmie-mega male front, starmie_mega female front, starmie_mega male front, staryu female front, staryu male front, steelix female front, steelix male front, steelix-mega female front, steelix-mega male front, steenee female front, steenee male front, steenee_redux female front, steenee_redux male front, stonjourner female front, stonjourner male front, stufful female front, stufful male front, stufful_redux female front, stufful_redux male front, stunfisk female front, stunfisk male front, stunfisk-galar female front, stunfisk-galar male front, stunky female front, stunky male front, sudowoodo female front, sudowoodo male front, suicune female front, suicune male front, sunflora female front, sunflora male front, sunkern female front, sunkern male front, surskit female front, surskit male front, swablu female front, swablu male front, swablu_redux female front, swablu_redux male front, swadloon female front, swadloon male front, swalot female front, swalot male front, swalot_mega female front, swalot_mega male front, swampert female front, swampert male front, swampert-mega female front, swampert-mega male front, swanna female front, swanna male front, swellow female front, swellow male front, swinub female front, swinub male front, swinub_redux female front, swinub_redux male front, swirlix female front, swirlix male front, sylveon female front, sylveon male front, tadbulb female front, tadbulb male front, taillow female front, taillow male front, talonflame female front, talonflame male front, talonflame_mega female front, talonflame_mega male front, tandemaus female front, tandemaus male front, tangela female front, tangela male front, tangrowth female front, tangrowth male front, tapu-bulu female front, tapu-bulu male front, tapu-fini female front, tapu-fini male front, tapu-koko female front, tapu-koko male front, tapu-lele female front, tapu-lele male front, tarountula female front, tarountula male front, tatsugiri-curly female front, tatsugiri-curly male front, tatsugiri-droopy female front, tatsugiri-droopy male front, tatsugiri-stretchy female front, tatsugiri-stretchy male front, tatsugiri_mega female front, tatsugiri_mega male front, tauros female front, tauros male front, tauros-paldea-aqua-breed female front, tauros-paldea-aqua-breed male front, tauros-paldea-blaze-breed female front, tauros-paldea-blaze-breed male front, tauros-paldea-combat-breed female front, tauros-paldea-combat-breed male front, teddiursa female front, teddiursa male front, tentacool female front, tentacool male front, tentacruel female front, tentacruel male front, tentagrewl female front, tentagrewl male front, tepig female front, tepig male front, terapagos female front, terapagos male front, terapagos-terastal female front, terapagos-terastal male front, terrakion female front, terrakion male front, throh female front, throh male front, throh_redux female front, throh_redux male front, thundurus-incarnate female front, thundurus-incarnate male front, thundurus-therian female front, thundurus-therian male front, thwackey female front, thwackey male front, timburr female front, timburr male front, ting-lu female front, ting-lu male front, tinkatink female front, tinkatink male front, tinkatink_redux female front, tinkatink_redux male front, tinkatuff female front, tinkatuff male front, tinkatuff_redux female front, tinkatuff_redux male front, tirtouga female front, tirtouga male front, toedscool female front, toedscool male front, toedscruel female front, toedscruel male front, togedemaru female front, togedemaru male front, togepi female front, togepi male front, togetic female front, togetic male front, torchic female front, torchic male front, torkoal female front, torkoal male front, tornadus-incarnate female front, tornadus-incarnate male front, torracat female front, torracat male front, torrentula female front, torrentula male front, tortemple female front, tortemple male front, torterra female front, torterra male front, torterra_mega female front, torterra_mega male front, torterra_redux female front, torterra_redux male front, totodile female front, totodile male front, toucannon female front, toucannon male front, toucannon_mega female front, toucannon_mega male front, toxapex female front, toxapex male front, toxel female front, toxel male front, toxel_redux female front, toxel_redux male front, toxicroak female front, toxicroak male front, toxtricity-amped female front, toxtricity-amped male front, toxtricity-amped-gmax female front, toxtricity-amped-gmax male front, toxtricity-low-key female front, toxtricity-low-key male front, toxtricity-low-key-gmax female front, toxtricity-low-key-gmax male front, toxtricity_mega female front, toxtricity_mega male front, toxtricity_redux female front, toxtricity_redux male front, toxtricity_redux_fuzz female front, toxtricity_redux_fuzz male front, toxtricity_redux_fuzz_mega female front, toxtricity_redux_fuzz_mega male front, toxtricity_redux_mega female front, toxtricity_redux_mega male front, tranquill female front, tranquill male front, trapinch female front, trapinch male front, trapinch_redux female front, trapinch_redux male front, treecko female front, treecko male front, trevenant female front, trevenant male front, tropius female front, tropius male front, trubbish female front, trubbish male front, trumbeak female front, trumbeak male front, tsareena female front, tsareena male front, tsareena_mega female front, tsareena_mega male front, tsareena_redux female front, tsareena_redux male front, tsareena_redux_mega female front, tsareena_redux_mega male front, turtonator female front, turtonator male front, turtwig female front, turtwig male front, turtwig_redux female front, turtwig_redux male front, tympole female front, tympole male front, tynamo female front, tynamo male front, type-null female front, type-null male front, typhlosion female front, typhlosion male front, typhlosion-hisui female front, typhlosion-hisui male front, typhlosion_hisuian_mega female front, typhlosion_hisuian_mega male front, typhlosion_mega female front, typhlosion_mega male front, tyranitar female front, tyranitar male front, tyranitar-mega female front, tyranitar-mega male front, tyranitar_mega_redux female front, tyranitar_mega_redux male front, tyranitar_redux female front, tyranitar_redux male front, tyranjoula female front, tyranjoula male front, tyrantrum female front, tyrantrum male front, tyrogue female front, tyrogue male front, tyrunt female front, tyrunt male front, umbreon female front, umbreon male front, unfezant female front, unfezant male front, unown-a female front, unown-a male front, unown-b female front, unown-b male front, unown-c female front, unown-c male front, unown-d female front, unown-d male front, unown-e female front, unown-e male front, unown-exclamation female front, unown-exclamation male front, unown-f female front, unown-f male front, unown-g female front, unown-g male front, unown-h female front, unown-h male front, unown-i female front, unown-i male front, unown-j female front, unown-j male front, unown-k female front, unown-k male front, unown-l female front, unown-l male front, unown-m female front, unown-m male front, unown-n female front, unown-n male front, unown-o female front, unown-o male front, unown-p female front, unown-p male front, unown-q female front, unown-q male front, unown-question female front, unown-question male front, unown-r female front, unown-r male front, unown-s female front, unown-s male front, unown-t female front, unown-t male front, unown-u female front, unown-u male front, unown-v female front, unown-v male front, unown-w female front, unown-w male front, unown-x female front, unown-x male front, unown-y female front, unown-y male front, unown-z female front, unown-z male front, unown_revelation female front, unown_revelation male front, ursaluna female front, ursaluna male front, ursaluna-bloodmoon female front, ursaluna-bloodmoon male front, ursaluna_mega female front, ursaluna_mega male front, ursaring female front, ursaring male front, urshifu-rapid-strike female front, urshifu-rapid-strike male front, urshifu-rapid-strike-gmax female front, urshifu-rapid-strike-gmax male front, urshifu-single-strike female front, urshifu-single-strike male front, urshifu-single-strike-gmax female front, urshifu-single-strike-gmax male front, urshifu_mega female front, urshifu_mega male front, urshifu_rapid_strike_style_mega female front, urshifu_rapid_strike_style_mega male front, uxie female front, uxie male front, uxie_redux female front, uxie_redux male front, vanillish female front, vanillish male front, vanillish_redux female front, vanillish_redux male front, vanillite female front, vanillite male front, vanillite_redux female front, vanillite_redux male front, vanilluxe female front, vanilluxe male front, vanilluxe_mega female front, vanilluxe_mega male front, vanilluxe_redux female front, vanilluxe_redux male front, vanilluxe_redux_mega female front, vanilluxe_redux_mega male front, vaporeon female front, vaporeon male front, varoom female front, varoom male front, velozel female front, velozel male front, veluza female front, veluza male front, venipede female front, venipede male front, venomoth female front, venomoth male front, venonat female front, venonat male front, venusaur female front, venusaur male front, venusaur-gmax female front, venusaur-gmax male front, venusaur-mega female front, venusaur-mega male front, venusaur_mega_x female front, venusaur_mega_x male front, vespiquen female front, vespiquen male front, vibrava female front, vibrava male front, vibrava_redux female front, vibrava_redux male front, victini female front, victini male front, victini_primal female front, victini_primal male front, victreebel female front, victreebel male front, victreebel-mega female front, victreebel-mega male front, victreebel_mega female front, victreebel_mega male front, victreebel_redux female front, victreebel_redux male front, vigoroth female front, vigoroth male front, vikavolt female front, vikavolt male front, vileplume female front, vileplume male front, virizion female front, virizion male front, vivillon-archipelago female front, vivillon-archipelago male front, vivillon-continental female front, vivillon-continental male front, vivillon-elegant female front, vivillon-elegant male front, vivillon-fancy female front, vivillon-fancy male front, vivillon-garden female front, vivillon-garden male front, vivillon-high-plains female front, vivillon-high-plains male front, vivillon-icy-snow female front, vivillon-icy-snow male front, vivillon-jungle female front, vivillon-jungle male front, vivillon-marine female front, vivillon-marine male front, vivillon-meadow female front, vivillon-meadow male front, vivillon-modern female front, vivillon-modern male front, vivillon-monsoon female front, vivillon-monsoon male front, vivillon-ocean female front, vivillon-ocean male front, vivillon-poke-ball female front, vivillon-poke-ball male front, vivillon-polar female front, vivillon-polar male front, vivillon-river female front, vivillon-river male front, vivillon-sandstorm female front, vivillon-sandstorm male front, vivillon-savanna female front, vivillon-savanna male front, vivillon-sun female front, vivillon-sun male front, vivillon-tundra female front, vivillon-tundra male front, volbeat female front, volbeat male front, volcanion female front, volcanion male front, volcarona female front, volcarona male front, volcarona_redux female front, volcarona_redux male front, voltorb female front, voltorb male front, voltorb-hisui female front, voltorb-hisui male front, vullaby female front, vullaby male front, vulpix female front, vulpix male front, vulpix-alola female front, vulpix-alola male front, wailmer female front, wailmer male front, wailord female front, wailord male front, walrein female front, walrein male front, wartortle female front, wartortle male front, watchog female front, watchog male front, wattrel female front, wattrel male front, weavile female front, weavile male front, weavile_mega female front, weavile_mega male front, weavile_redux female front, weavile_redux male front, weavile_redux_mega female front, weavile_redux_mega male front, weedle female front, weedle male front, weedle_redux female front, weedle_redux male front, weepinbell female front, weepinbell male front, weepinbell_redux female front, weepinbell_redux male front, weezing female front, weezing male front, whimsicott female front, whimsicott male front, whirlipede female front, whirlipede male front, whiscash female front, whiscash male front, whismur female front, whismur male front, whismur_redux female front, whismur_redux male front, wigglytuff female front, wigglytuff male front, wigglytuff_apex female front, wigglytuff_apex male front, wigglytuff_mega female front, wigglytuff_mega male front, wigglytuff_primal female front, wigglytuff_primal male front, wiglett female front, wiglett male front, wimpod female front, wimpod male front, wishiwashi-solo female front, wishiwashi-solo male front, wispywaspy female front, wispywaspy male front, wispywaspy_hivemind female front, wispywaspy_hivemind male front, wo-chien female front, wo-chien male front, wobbuffet female front, wobbuffet male front, woobat female front, woobat male front, wooloo female front, wooloo male front, wooly_worm female front, wooly_worm male front, wooper female front, wooper male front, wooper-paldea female front, wooper-paldea male front, wormadam-plant female front, wormadam-plant male front, wormadam-sandy female front, wormadam-sandy male front, wormadam-trash female front, wormadam-trash male front, wugtrio female front, wugtrio male front, wurmple female front, wurmple male front, wynaut female front, wynaut male front, wyrdeer female front, wyrdeer male front, xatu female front, xatu male front, xerneas-active female front, xerneas-active male front, xerneas-neutral female front, xerneas-neutral male front, xurkitree female front, xurkitree male front, yamask female front, yamask male front, yamask-galar female front, yamask-galar male front, yamper female front, yamper male front, yungoos female front, yungoos male front, yveltal_mega female front, yveltal_mega male front, zacian-crowned female front, zacian-crowned male front, zamazenta female front, zamazenta male front, zamazenta-crowned female front, zamazenta-crowned male front, zangoose female front, zangoose male front, zapdos female front, zapdos male front, zapdos-galar female front, zapdos-galar male front, zapdos_ex female front, zapdos_ex male front, zapdos_ex_mega female front, zapdos_ex_mega male front, zarude female front, zarude male front, zarude-dada female front, zarude-dada male front, zebstrika female front, zebstrika male front, zeraora-mega female front, zeraora-mega male front, zeraora_mega female front, zeraora_mega male front, zigzagoon female front, zigzagoon male front, zigzagoon-galar female front, zigzagoon-galar male front, zoroark female front, zoroark male front, zorua female front, zorua male front, zorua-hisui female front, zorua-hisui male front, zubat female front, zubat male front, zweilous female front, zweilous male front, zweilous_redux female front, zweilous_redux male front, zygarde-10 female front, zygarde-10 male front, zygarde-10-power-construct female front, zygarde-10-power-construct male front, zygarde-50 female front, zygarde-50 male front, zygarde-50-power-construct female front, zygarde-50-power-construct male front, zygarde-complete female front, zygarde-complete male front, zygarde-mega female front, zygarde-mega male front, zygarde_complete_mega female front, zygarde_complete_mega male front — 4274 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0109_mismagius_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0109_mismagius_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0191_salamence_alternate_mega_form_3/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0191_salamence_alternate_mega_form_3/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_hisuian_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_hisuian_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swampert/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swampert/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scyther_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scyther_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0050_drowzee_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0050_drowzee_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/venusaur_mega_x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/venusaur_mega_x/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0286_klinklang_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0286_klinklang_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skeledirge_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/skeledirge_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/braviary/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/braviary/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/calyrex-shadow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/calyrex-shadow/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0314_spritzee_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0314_spritzee_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bewear_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bewear_redux/female/front.png`
- … 4244 more

### 2. machamp female front, machamp male front, machamp-gmax female front, machamp-gmax male front, machamp_mega female front, machamp_mega male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/female/front.png`

### 3. arcanine_redux female front, arcanine_redux male front, mightyena female front, mightyena male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mightyena/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mightyena/female/front.png`

### 4. beedrill_mega_redux female front, beedrill_mega_redux male front, reuniclus_redux female front, reuniclus_redux male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beedrill_mega_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beedrill_mega_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/reuniclus_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/reuniclus_redux/female/front.png`

### 5. butterfree-gmax female front, butterfree-gmax male front, butterfree_mega female front, butterfree_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree-gmax/female/front.png`

### 6. cpf_0106_quagsire_alternate_form_1 female front, cpf_0106_quagsire_alternate_form_1 male front, goodra_hisuian_mega female front, goodra_hisuian_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0106_quagsire_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0106_quagsire_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/goodra_hisuian_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/goodra_hisuian_mega/female/front.png`

### 7. kingler-gmax female front, kingler-gmax male front, kingler_mega female front, kingler_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler-gmax/female/front.png`

### 8. fearow_redux female front, fearow_redux male front, mesprit_redux female front, mesprit_redux male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mesprit_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mesprit_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/fearow_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/fearow_redux/female/front.png`

### 9. rapidash-galar female front, rapidash-galar male front, snorlax female front, snorlax male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rapidash-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rapidash-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax/female/front.png`

### 10. liepard female front, liepard male front, swoobat female front, swoobat male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swoobat/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swoobat/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/liepard/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/liepard/female/front.png`

### 11. tinkaton female front, tinkaton male front, tinkaton_mega female front, tinkaton_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tinkaton_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tinkaton_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tinkaton/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tinkaton/female/front.png`

### 12. abomasnow female front, abomasnow male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/female/front.png`

### 13. alakazam female front, alakazam male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam/female/front.png`

### 14. butterfree female front, butterfree male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree/female/front.png`

### 15. luxray female front, luxray male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/luxray/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/luxray/female/front.png`

### 16. milotic female front, milotic male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/milotic/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/milotic/female/front.png`

## Duplicated concept candidates

None detected.

