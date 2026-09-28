# DS01 Sprite Library Duplicate Audit

Status: ANALYSIS ONLY — no sprite assets were installed, replaced, recolored, or deleted.

## Summary

- Images scanned: **11365**
- Sprite candidates: **11365**
- Male/front visual representatives: **4910**
- Exact byte-duplicate groups: **4643**
- Exact rendered-pixel duplicate groups: **19**
- Palette/recolor candidate groups: **13**
- Near-visual duplicate groups (dHash <= 4): **144**
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

### 1. abra female front, abra male front, abra_redux female front, abra_redux male front, aegislash-shield female front, aegislash-shield male front, alcremie-caramel-swirl-berry-sweet female front, alcremie-caramel-swirl-berry-sweet male front, alcremie-caramel-swirl-clover-sweet female front, alcremie-caramel-swirl-clover-sweet male front, alcremie-caramel-swirl-flower-sweet female front, alcremie-caramel-swirl-flower-sweet male front, alcremie-caramel-swirl-love-sweet female front, alcremie-caramel-swirl-love-sweet male front, alcremie-caramel-swirl-ribbon-sweet female front, alcremie-caramel-swirl-ribbon-sweet male front, alcremie-caramel-swirl-star-sweet female front, alcremie-caramel-swirl-star-sweet male front, alcremie-caramel-swirl-strawberry-sweet female front, alcremie-caramel-swirl-strawberry-sweet male front, alcremie-lemon-cream-berry-sweet female front, alcremie-lemon-cream-berry-sweet male front, alcremie-lemon-cream-clover-sweet female front, alcremie-lemon-cream-clover-sweet male front, alcremie-lemon-cream-flower-sweet female front, alcremie-lemon-cream-flower-sweet male front, alcremie-lemon-cream-love-sweet female front, alcremie-lemon-cream-love-sweet male front, alcremie-lemon-cream-ribbon-sweet female front, alcremie-lemon-cream-ribbon-sweet male front, alcremie-lemon-cream-star-sweet female front, alcremie-lemon-cream-star-sweet male front, alcremie-lemon-cream-strawberry-sweet female front, alcremie-lemon-cream-strawberry-sweet male front, alcremie-matcha-cream-berry-sweet female front, alcremie-matcha-cream-berry-sweet male front, alcremie-matcha-cream-clover-sweet female front, alcremie-matcha-cream-clover-sweet male front, alcremie-matcha-cream-flower-sweet female front, alcremie-matcha-cream-flower-sweet male front, alcremie-matcha-cream-love-sweet female front, alcremie-matcha-cream-love-sweet male front, alcremie-matcha-cream-ribbon-sweet female front, alcremie-matcha-cream-ribbon-sweet male front, alcremie-matcha-cream-star-sweet female front, alcremie-matcha-cream-star-sweet male front, alcremie-matcha-cream-strawberry-sweet female front, alcremie-matcha-cream-strawberry-sweet male front, alcremie-mint-cream-berry-sweet female front, alcremie-mint-cream-berry-sweet male front, alcremie-mint-cream-clover-sweet female front, alcremie-mint-cream-clover-sweet male front, alcremie-mint-cream-flower-sweet female front, alcremie-mint-cream-flower-sweet male front, alcremie-mint-cream-love-sweet female front, alcremie-mint-cream-love-sweet male front, alcremie-mint-cream-ribbon-sweet female front, alcremie-mint-cream-ribbon-sweet male front, alcremie-mint-cream-star-sweet female front, alcremie-mint-cream-star-sweet male front, alcremie-mint-cream-strawberry-sweet female front, alcremie-mint-cream-strawberry-sweet male front, alcremie-rainbow-swirl-berry-sweet female front, alcremie-rainbow-swirl-berry-sweet male front, alcremie-rainbow-swirl-clover-sweet female front, alcremie-rainbow-swirl-clover-sweet male front, alcremie-rainbow-swirl-flower-sweet female front, alcremie-rainbow-swirl-flower-sweet male front, alcremie-rainbow-swirl-love-sweet female front, alcremie-rainbow-swirl-love-sweet male front, alcremie-rainbow-swirl-ribbon-sweet female front, alcremie-rainbow-swirl-ribbon-sweet male front, alcremie-rainbow-swirl-star-sweet female front, alcremie-rainbow-swirl-star-sweet male front, alcremie-rainbow-swirl-strawberry-sweet female front, alcremie-rainbow-swirl-strawberry-sweet male front, alcremie-ruby-cream-berry-sweet female front, alcremie-ruby-cream-berry-sweet male front, alcremie-ruby-cream-clover-sweet female front, alcremie-ruby-cream-clover-sweet male front, alcremie-ruby-cream-flower-sweet female front, alcremie-ruby-cream-flower-sweet male front, alcremie-ruby-cream-love-sweet female front, alcremie-ruby-cream-love-sweet male front, alcremie-ruby-cream-ribbon-sweet female front, alcremie-ruby-cream-ribbon-sweet male front, alcremie-ruby-cream-star-sweet female front, alcremie-ruby-cream-star-sweet male front, alcremie-ruby-cream-strawberry-sweet female front, alcremie-ruby-cream-strawberry-sweet male front, alcremie-ruby-swirl-berry-sweet female front, alcremie-ruby-swirl-berry-sweet male front, alcremie-ruby-swirl-clover-sweet female front, alcremie-ruby-swirl-clover-sweet male front, alcremie-ruby-swirl-flower-sweet female front, alcremie-ruby-swirl-flower-sweet male front, alcremie-ruby-swirl-love-sweet female front, alcremie-ruby-swirl-love-sweet male front, alcremie-ruby-swirl-ribbon-sweet female front, alcremie-ruby-swirl-ribbon-sweet male front, alcremie-ruby-swirl-star-sweet female front, alcremie-ruby-swirl-star-sweet male front, alcremie-ruby-swirl-strawberry-sweet female front, alcremie-ruby-swirl-strawberry-sweet male front, alcremie-salted-cream-berry-sweet female front, alcremie-salted-cream-berry-sweet male front, alcremie-salted-cream-clover-sweet female front, alcremie-salted-cream-clover-sweet male front, alcremie-salted-cream-flower-sweet female front, alcremie-salted-cream-flower-sweet male front, alcremie-salted-cream-love-sweet female front, alcremie-salted-cream-love-sweet male front, alcremie-salted-cream-ribbon-sweet female front, alcremie-salted-cream-ribbon-sweet male front, alcremie-salted-cream-star-sweet female front, alcremie-salted-cream-star-sweet male front, alcremie-salted-cream-strawberry-sweet female front, alcremie-salted-cream-strawberry-sweet male front, alcremie-vanilla-cream-berry-sweet female front, alcremie-vanilla-cream-berry-sweet male front, alcremie-vanilla-cream-clover-sweet female front, alcremie-vanilla-cream-clover-sweet male front, alcremie-vanilla-cream-flower-sweet female front, alcremie-vanilla-cream-flower-sweet male front, alcremie-vanilla-cream-love-sweet female front, alcremie-vanilla-cream-love-sweet male front, alcremie-vanilla-cream-ribbon-sweet female front, alcremie-vanilla-cream-ribbon-sweet male front, alcremie-vanilla-cream-star-sweet female front, alcremie-vanilla-cream-star-sweet male front, alcremie-vanilla-cream-strawberry-sweet female front, alcremie-vanilla-cream-strawberry-sweet male front, anorith female front, anorith male front, aromatisse female front, aromatisse male front, aron female front, aron male front, aron_redux female front, aron_redux male front, audino female front, audino male front, audino-mega female front, audino-mega male front, axew female front, axew male front, azurill female front, azurill male front, bagon female front, bagon male front, baltoy female front, baltoy male front, barboach female front, barboach male front, basculin-blue-striped female front, basculin-blue-striped male front, basculin-red-striped female front, basculin-red-striped male front, basculin-white-striped female front, basculin-white-striped male front, beheeyem female front, beheeyem male front, beldum female front, beldum male front, bellibolt female front, bellibolt male front, bellossom female front, bellossom male front, bellsprout female front, bellsprout male front, bellsprout_redux female front, bellsprout_redux male front, bergmite female front, bergmite male front, bidoof female front, bidoof male front, binacle female front, binacle male front, blipbug female front, blipbug male front, blitzle female front, blitzle male front, blocli female front, blocli male front, bounsweet female front, bounsweet male front, bounsweet_redux female front, bounsweet_redux male front, brambleghast female front, brambleghast male front, bramblin female front, bramblin male front, brionne female front, brionne male front, bronzor female front, bronzor male front, bruxish female front, bruxish male front, budew female front, budew male front, buizel female front, buizel male front, buizel_redux female front, buizel_redux male front, bulbasaur female front, bulbasaur male front, burmy-plant female front, burmy-plant male front, cacnea female front, cacnea male front, capsakid female front, capsakid male front, carbink female front, carbink male front, carkol female front, carkol male front, carvanha female front, carvanha male front, cascoon female front, cascoon male front, castform female front, castform male front, castform-rainy female front, castform-rainy male front, castform-snowy female front, castform-snowy male front, castform-sunny female front, castform-sunny male front, castform_foggy female front, castform_foggy male front, castform_sandy female front, castform_sandy male front, caterpie female front, caterpie male front, celebi female front, celebi male front, charcadet female front, charcadet male front, charjabug female front, charjabug male front, charmander female front, charmander male front, chatot female front, chatot male front, cherrim-overcast female front, cherrim-overcast male front, cherrim-sunshine female front, cherrim-sunshine male front, cherubi female front, cherubi male front, chespin female front, chespin male front, chewtle female front, chewtle male front, chimchar female front, chimchar male front, chimchar_redux female front, chimchar_redux male front, chingling female front, chingling male front, clamperl female front, clamperl male front, clauncher female front, clauncher male front, clefairy female front, clefairy male front, clefairy_redux female front, clefairy_redux male front, cleffa female front, cleffa male front, cleffa_redux female front, cleffa_redux male front, clobbopus female front, clobbopus male front, combee female front, combee male front, combusken female front, combusken male front, corm female front, corm male front, corphish female front, corphish male front, corsola female front, corsola male front, corsola-galar female front, corsola-galar male front, cosmoem female front, cosmoem male front, cosmog female front, cosmog male front, cottonee female front, cottonee male front, cpf_0001_caterpie_alternate_form_1 female front, cpf_0001_caterpie_alternate_form_1 male front, cpf_0003_weedle_alternate_form_2 female front, cpf_0003_weedle_alternate_form_2 male front, cpf_0004_kakuna_alternate_form_2 female front, cpf_0004_kakuna_alternate_form_2 male front, cpf_0007_pidgey_alternate_form_2 female front, cpf_0007_pidgey_alternate_form_2 male front, cpf_0011_clefairy_alternate_form_1 female front, cpf_0011_clefairy_alternate_form_1 male front, cpf_0017_jigglypuff_alternate_form_1 female front, cpf_0017_jigglypuff_alternate_form_1 male front, cpf_0019_paras_alternate_form_1 female front, cpf_0019_paras_alternate_form_1 male front, cpf_0021_venonat_alternate_form_1 female front, cpf_0021_venonat_alternate_form_1 male front, cpf_0023_poliwag_alternate_form_1 female front, cpf_0023_poliwag_alternate_form_1 male front, cpf_0045_gastly_alternate_form_2 female front, cpf_0045_gastly_alternate_form_2 male front, cpf_0059_staryu_alternate_form_1 female front, cpf_0059_staryu_alternate_form_1 male front, cpf_0067_jolteon_alternate_form_3 female front, cpf_0067_jolteon_alternate_form_3 male front, cpf_0070_umbreon_alternate_form_3 female front, cpf_0070_umbreon_alternate_form_3 male front, cpf_0073_sylveon_alternate_form_3 female front, cpf_0073_sylveon_alternate_form_3 male front, cpf_0074_omanyte_alternate_form_1 female front, cpf_0074_omanyte_alternate_form_1 male front, cpf_0076_kabuto_alternate_form_1 female front, cpf_0076_kabuto_alternate_form_1 male front, cpf_0089_croconaw_alternate_form_1 female front, cpf_0089_croconaw_alternate_form_1 male front, cpf_0091_hoothoot_alternate_form_1 female front, cpf_0091_hoothoot_alternate_form_1 male front, cpf_0093_ledyba_alternate_form_1 female front, cpf_0093_ledyba_alternate_form_1 male front, cpf_0095_natu_alternate_form_1 female front, cpf_0095_natu_alternate_form_1 male front, cpf_0097_flaaffy_alternate_form_2 female front, cpf_0097_flaaffy_alternate_form_2 male front, cpf_0100_politoed_alternate_form_1 female front, cpf_0100_politoed_alternate_form_1 male front, cpf_0101_sunflora_alternate_form_1 female front, cpf_0101_sunflora_alternate_form_1 male front, cpf_0102_sunflora_alternate_form_2 female front, cpf_0102_sunflora_alternate_form_2 male front, cpf_0105_wooper_alternate_form_1 female front, cpf_0105_wooper_alternate_form_1 male front, cpf_0108_misdreavus_alternate_form_2 female front, cpf_0108_misdreavus_alternate_form_2 male front, cpf_0119_snubbull_alternate_form_1 female front, cpf_0119_snubbull_alternate_form_1 male front, cpf_0121_corsola_alternate_form_1 female front, cpf_0121_corsola_alternate_form_1 male front, cpf_0125_remoraid_alternate_form_1 female front, cpf_0125_remoraid_alternate_form_1 male front, cpf_0127_phanpy_alternate_form_1 female front, cpf_0127_phanpy_alternate_form_1 male front, cpf_0131_larvitar_ice_form_2 female front, cpf_0131_larvitar_ice_form_2 male front, cpf_0132_larvitar_space_form_4 female front, cpf_0132_larvitar_space_form_4 male front, cpf_0133_pupitar_ice_form_2 female front, cpf_0133_pupitar_ice_form_2 male front, cpf_0134_pupitar_space_form_4 female front, cpf_0134_pupitar_space_form_4 male front, cpf_0145_swampert_alternate_mega_form_2 female front, cpf_0145_swampert_alternate_mega_form_2 male front, cpf_0148_ralts_alternate_form_3 female front, cpf_0148_ralts_alternate_form_3 male front, cpf_0154_skitty_alternate_form_1 female front, cpf_0154_skitty_alternate_form_1 male front, cpf_0156_sableye_alternate_gemstone_form_2 female front, cpf_0156_sableye_alternate_gemstone_form_2 male front, cpf_0158_sableye_alternate_darkness_form_4 female front, cpf_0158_sableye_alternate_darkness_form_4 male front, cpf_0164_numel_alternate_form_3 female front, cpf_0164_numel_alternate_form_3 male front, cpf_0167_electrike_alternate_form_2 female front, cpf_0167_electrike_alternate_form_2 male front, cpf_0171_trapinch_alternate_form_1 female front, cpf_0171_trapinch_alternate_form_1 male front, cpf_0176_baltoy_alternate_form_1 female front, cpf_0176_baltoy_alternate_form_1 male front, cpf_0180_anorith_alternate_form_1 female front, cpf_0180_anorith_alternate_form_1 male front, cpf_0183_chingling_alternate_form_1 female front, cpf_0183_chingling_alternate_form_1 male front, cpf_0187_bagon_alternate_form_2 female front, cpf_0187_bagon_alternate_form_2 male front, cpf_0188_shelgon_alternate_form_2 female front, cpf_0188_shelgon_alternate_form_2 male front, cpf_0192_beldum_alternate_form_2 female front, cpf_0192_beldum_alternate_form_2 male front, cpf_0203_shieldon_alternate_form_1 female front, cpf_0203_shieldon_alternate_form_1 male front, cpf_0205_combee_alternate_form_1 female front, cpf_0205_combee_alternate_form_1 male front, cpf_0212_spiritomb_alternate_form_1 female front, cpf_0212_spiritomb_alternate_form_1 male front, cpf_0213_gible_bluetowel_alternate_forms_form_2 female front, cpf_0213_gible_bluetowel_alternate_forms_form_2 male front, cpf_0232_nosepass_alternate_form_1 female front, cpf_0232_nosepass_alternate_form_1 male front, cpf_0246_munna_alternate_form_1 female front, cpf_0246_munna_alternate_form_1 male front, cpf_0248_pidove_alternate_form_1 female front, cpf_0248_pidove_alternate_form_1 male front, cpf_0253_timburr_alternate_form_1 female front, cpf_0253_timburr_alternate_form_1 male front, cpf_0256_purrloin_alternate_form_1 female front, cpf_0256_purrloin_alternate_form_1 male front, cpf_0258_petilil_alternate_form_1 female front, cpf_0258_petilil_alternate_form_1 male front, cpf_0259_petilil_alternate_form_2 female front, cpf_0259_petilil_alternate_form_2 male front, cpf_0262_sandile_alternate_form_1 female front, cpf_0262_sandile_alternate_form_1 male front, cpf_0265_dwebble_alternate_form_1 female front, cpf_0265_dwebble_alternate_form_1 male front, cpf_0267_yamask_alternate_form_1 female front, cpf_0267_yamask_alternate_form_1 male front, cpf_0274_trubbish_alternate_form_1 female front, cpf_0274_trubbish_alternate_form_1 male front, cpf_0276_solosis_alternate_form_1 female front, cpf_0276_solosis_alternate_form_1 male front, cpf_0277_duosion_alternate_form_1 female front, cpf_0277_duosion_alternate_form_1 male front, cpf_0283_ferroseed_alternate_form_1 female front, cpf_0283_ferroseed_alternate_form_1 male front, cpf_0289_litwick_alternate_form_1 female front, cpf_0289_litwick_alternate_form_1 male front, cpf_0294_mienfoo_bluetowel_alternate_form_form_1 female front, cpf_0294_mienfoo_bluetowel_alternate_form_form_1 male front, cpf_0301_durant_bluetowel_alternate_form_form_1 female front, cpf_0301_durant_bluetowel_alternate_form_form_1 male front, cpf_0302_deino_cybertank_form_1 female front, cpf_0302_deino_cybertank_form_1 male front, cpf_0313_spritzee_alternate_form_1 female front, cpf_0313_spritzee_alternate_form_1 male front, cpf_0314_spritzee_alternate_form_2 female front, cpf_0314_spritzee_alternate_form_2 male front, cpf_0315_aromatisse_alternate_form_1 female front, cpf_0315_aromatisse_alternate_form_1 male front, cpf_0316_aromatisse_alternate_form_2 female front, cpf_0316_aromatisse_alternate_form_2 male front, cpf_0327_goomy_alternate_form_1 female front, cpf_0327_goomy_alternate_form_1 male front, cpf_0329_sliggoo_alternate_form_2 female front, cpf_0329_sliggoo_alternate_form_2 male front, cpf_0334_dartrix_alternate_form_1 female front, cpf_0334_dartrix_alternate_form_1 male front, cpf_0335_dartrix_alternate_form_2 female front, cpf_0335_dartrix_alternate_form_2 male front, cpf_0342_dewpider_alternate_form_1 female front, cpf_0342_dewpider_alternate_form_1 male front, cpf_0344_fomantis_alternate_form_1 female front, cpf_0344_fomantis_alternate_form_1 male front, cpf_0346_sandygast_alternate_form_1 female front, cpf_0346_sandygast_alternate_form_1 male front, cpf_0355_sobble_alternate_form_2 female front, cpf_0355_sobble_alternate_form_2 male front, cranidos female front, cranidos male front, croagunk female front, croagunk male front, croconaw female front, croconaw male front, cubchoo female front, cubchoo male front, cubone female front, cubone male front, cutiefly female front, cutiefly male front, cyndaquil female front, cyndaquil male front, darkrai_mega female front, darkrai_mega male front, darmanitan-zen female front, darmanitan-zen male front, dartrix female front, dartrix male front, darumaka female front, darumaka male front, darumaka-galar female front, darumaka-galar male front, darumaka_redux female front, darumaka_redux male front, dedenne female front, dedenne male front, deerling-autumn female front, deerling-autumn male front, deerling-spring female front, deerling-spring male front, deerling-summer female front, deerling-summer male front, deerling-winter female front, deerling-winter male front, deino female front, deino male front, deino_redux female front, deino_redux male front, delibird female front, delibird male front, dewpider female front, dewpider male front, dewpider_redux female front, dewpider_redux male front, dhelmise female front, dhelmise male front, diglett female front, diglett male front, diglett-alola female front, diglett-alola male front, dipplin female front, dipplin male front, ditto female front, ditto male front, dottler female front, dottler male front, drakloak female front, drakloak male front, dreepy female front, dreepy male front, drilbur_redux female front, drilbur_redux male front, drizzile female front, drizzile male front, drowzee female front, drowzee male front, ducklett female front, ducklett male front, dugtrio female front, dugtrio male front, dugtrio-alola female front, dugtrio-alola male front, duosion female front, duosion male front, durant female front, durant male front, duskull female front, duskull male front, dwebble female front, dwebble male front, earthretha_apprensith female front, earthretha_apprensith male front, earthretha_bombghost female front, earthretha_bombghost male front, earthretha_cubchestra female front, earthretha_cubchestra male front, earthretha_gloom_1 female front, earthretha_gloom_1 male front, earthretha_museon female front, earthretha_museon male front, earthretha_oddish_1 female front, earthretha_oddish_1 male front, earthretha_seegel female front, earthretha_seegel male front, earthretha_thiefire female front, earthretha_thiefire male front, earthretha_vileplume_1 female front, earthretha_vileplume_1 male front, eevee female front, eevee male front, eevee-starter female front, eevee-starter male front, eiscue-ice female front, eiscue-ice male front, eiscue-noice female front, eiscue-noice male front, ekans female front, ekans male front, eldegoss female front, eldegoss male front, electrike female front, electrike male front, electrode female front, electrode male front, electrode-hisui female front, electrode-hisui male front, elekid female front, elekid male front, elgyem female front, elgyem male front, espurr female front, espurr male front, farfetchd female front, farfetchd male front, feebas female front, feebas male front, fennekin female front, fennekin male front, ferroseed female front, ferroseed male front, fidough female front, fidough male front, finneon female front, finneon male front, flaaffy female front, flaaffy male front, fletchling female front, fletchling male front, flittle female front, flittle male front, fluffbee female front, fluffbee male front, fomantis female front, fomantis male front, foongus female front, foongus male front, frigibax female front, frigibax male front, frillish-female female front, frillish-female male front, frillish-male female front, frillish-male male front, froakie female front, froakie male front, frogadier female front, frogadier male front, froslass female front, froslass male front, fuecoco female front, fuecoco male front, furret female front, furret male front, gastly female front, gastly male front, gible female front, gible male front, gible_redux female front, gible_redux male front, gimmighoul-chest female front, gimmighoul-chest male front, glameow female front, glameow male front, gligar female front, gligar male front, gloom female front, gloom male front, golett female front, golett male front, goomy female front, goomy male front, gossifleur female front, gossifleur male front, gothita female front, gothita male front, gothorita female front, gothorita male front, grapploct female front, grapploct male front, greavard female front, greavard male front, grimer female front, grimer male front, grookey female front, grookey male front, grotom_fill female front, grotom_fill male front, growlithe female front, growlithe male front, growlithe-hisui female front, growlithe-hisui male front, growlithe_redux female front, growlithe_redux male front, grubbin female front, grubbin male front, gulpin female front, gulpin male front, happiny female front, happiny male front, happiny_redux female front, happiny_redux male front, hatenna female front, hatenna male front, heatran_mega female front, heatran_mega male front, helioptile female front, helioptile male front, herdier female front, herdier male front, hoopa female front, hoopa male front, hoothoot female front, hoothoot male front, horsea female front, horsea male front, houndour female front, houndour male front, houndour_redux female front, houndour_redux male front, illumise female front, illumise male front, impidimp female front, impidimp male front, indeedee-female female front, indeedee-female male front, indeedee-male female front, indeedee-male male front, inkay female front, inkay male front, iron-bundle female front, iron-bundle male front, iron-valiant female front, iron-valiant male front, ivysaur female front, ivysaur male front, jangmo-o female front, jangmo-o male front, jigglypuff female front, jigglypuff male front, jirachi female front, jirachi male front, jolteon female front, jolteon male front, joltik female front, joltik male front, kabuto female front, kabuto male front, kakuna female front, kakuna male front, kakuna_redux female front, kakuna_redux male front, karrablast female front, karrablast male front, kipmodo female front, kipmodo male front, kirlia_redux female front, kirlia_redux male front, klink female front, klink male front, komala female front, komala male front, kricketot female front, kricketot male front, kricketune female front, kricketune male front, kubfu female front, kubfu male front, larvesta female front, larvesta male front, larvesta_redux female front, larvesta_redux male front, larvitar female front, larvitar male front, larvitar_redux female front, larvitar_redux male front, leafeon female front, leafeon male front, lechonk female front, lechonk male front, ledian female front, ledian male front, ledyba female front, ledyba male front, lileep female front, lileep male front, lillipup female front, lillipup male front, litleo female front, litleo male front, litten female front, litten male front, litwick female front, litwick male front, litwick_redux female front, litwick_redux male front, lombre female front, lombre male front, lotad female front, lotad male front, lunatone female front, lunatone male front, lurantis female front, lurantis male front, luvdisc female front, luvdisc male front, luxio female front, luxio male front, luxio_redux female front, luxio_redux male front, machop female front, machop male front, machop_redux female front, machop_redux male front, magby female front, magby male front, magikarp female front, magikarp male front, magnemite female front, magnemite male front, makuhita female front, makuhita male front, mandibuzz female front, mandibuzz male front, mankey female front, mankey male front, mantyke female front, mantyke male front, marbeep female front, marbeep male front, mareanie female front, mareanie male front, mareep female front, mareep male front, marill female front, marill male front, marshadow female front, marshadow male front, marshtomp female front, marshtomp male front, maschiff female front, maschiff male front, meditite female front, meditite male front, meganium female front, meganium male front, meganium-mega female front, meganium-mega male front, meltan female front, meltan male front, meowstic-male female front, meowstic-male male front, meowth female front, meowth male front, meowth-alola female front, meowth-alola male front, meowth-galar female front, meowth-galar male front, meowth_partner female front, meowth_partner male front, mesprit female front, mesprit male front, metapod female front, metapod male front, mienfoo female front, mienfoo male front, milcery female front, milcery male front, mimikyu-busted female front, mimikyu-busted male front, mimikyu-disguised female front, mimikyu-disguised male front, mimikyu_apex female front, mimikyu_apex male front, mimikyu_apex_busted female front, mimikyu_apex_busted male front, minior-blue female front, minior-blue male front, minior-blue-meteor female front, minior-blue-meteor male front, minior-green female front, minior-green male front, minior-green-meteor female front, minior-green-meteor male front, minior-indigo female front, minior-indigo male front, minior-indigo-meteor female front, minior-indigo-meteor male front, minior-orange female front, minior-orange male front, minior-orange-meteor female front, minior-orange-meteor male front, minior-red female front, minior-red male front, minior-red-meteor female front, minior-red-meteor male front, minior-violet female front, minior-violet male front, minior-violet-meteor female front, minior-violet-meteor male front, minior-yellow female front, minior-yellow male front, minior-yellow-meteor female front, minior-yellow-meteor male front, misdreavus female front, misdreavus male front, morelull female front, morelull male front, morgrem female front, morgrem male front, morpeko-full-belly female front, morpeko-full-belly male front, morpeko-hangry female front, morpeko-hangry male front, mudbray female front, mudbray male front, mudkip female front, mudkip male front, munchlax female front, munchlax male front, munchlax_redux female front, munchlax_redux male front, munkidori female front, munkidori male front, munna female front, munna male front, murkrow female front, murkrow male front, nacli female front, nacli male front, naclstack female front, naclstack male front, natu female front, natu male front, nidoran-f female front, nidoran-f male front, nidoran-m female front, nidoran-m male front, nidorina female front, nidorina male front, nidorino female front, nidorino male front, nihilego female front, nihilego male front, nincada female front, nincada male front, nosepass female front, nosepass male front, numel female front, numel male front, nuzleaf female front, nuzleaf male front, nymble female front, nymble male front, oddish female front, oddish male front, oinkologne-female female front, oinkologne-female male front, omanyte female front, omanyte male front, oricorio-pau female front, oricorio-pau male front, oshawott female front, oshawott male front, pachirisu female front, pachirisu male front, palpitoad female front, palpitoad male front, pancham female front, pancham male front, panpour female front, panpour male front, panpour_redux female front, panpour_redux male front, pansage female front, pansage male front, pansage_redux female front, pansage_redux male front, pansear female front, pansear male front, pansear_redux female front, pansear_redux male front, paras female front, paras male front, patrat female front, patrat male front, pawmi female front, pawmi male front, pawmo female front, pawmo male front, pawniard female front, pawniard male front, pawniard_redux female front, pawniard_redux male front, perrserker female front, perrserker male front, petilil female front, petilil male front, phanpy female front, phanpy male front, phantump female front, phantump male front, phione female front, phione male front, pichu female front, pichu male front, pichu-spiky-eared female front, pichu-spiky-eared male front, pidgey female front, pidgey male front, pidove female front, pidove male front, pikachu female front, pikachu male front, pikachu-alola-cap female front, pikachu-alola-cap male front, pikachu-belle female front, pikachu-belle male front, pikachu-cosplay female front, pikachu-cosplay male front, pikachu-hoenn-cap female front, pikachu-hoenn-cap male front, pikachu-kalos-cap female front, pikachu-kalos-cap male front, pikachu-libre female front, pikachu-libre male front, pikachu-original-cap female front, pikachu-original-cap male front, pikachu-partner-cap female front, pikachu-partner-cap male front, pikachu-phd female front, pikachu-phd male front, pikachu-pop-star female front, pikachu-pop-star male front, pikachu-rock-star female front, pikachu-rock-star male front, pikachu-sinnoh-cap female front, pikachu-sinnoh-cap male front, pikachu-unova-cap female front, pikachu-unova-cap male front, pikachu-world-cap female front, pikachu-world-cap male front, pikipek female front, pikipek male front, piloswine female front, piloswine male front, pincurchin female front, pincurchin male front, pineco female front, pineco male front, piplup_redux female front, piplup_redux male front, plusle female front, plusle male front, poipole female front, poipole male front, politoed female front, politoed male front, poliwag female front, poliwag male front, poltchageist-artisan female front, poltchageist-artisan male front, polteageist-antique female front, polteageist-antique male front, polteageist-phony female front, polteageist-phony male front, poochyena female front, poochyena male front, popplio female front, popplio male front, porygon female front, porygon male front, porygon2 female front, porygon2 male front, prinplup female front, prinplup male front, psyduck female front, psyduck male front, psyduck_redux female front, psyduck_redux male front, pumpkaboo-average female front, pumpkaboo-average male front, pumpkaboo-large female front, pumpkaboo-large male front, pumpkaboo-small female front, pumpkaboo-small male front, pumpkaboo-super female front, pumpkaboo-super male front, pupitar female front, pupitar male front, pupitar_redux female front, pupitar_redux male front, purrloin female front, purrloin male front, pyukumuku female front, pyukumuku male front, quaxly female front, quaxly male front, quilladin female front, quilladin male front, qwilfish female front, qwilfish male front, qwilfish-hisui female front, qwilfish-hisui male front, raboot female front, raboot male front, ralts_redux female front, ralts_redux male front, rattata-alola female front, rattata-alola male front, rattata_redux female front, rattata_redux male front, rellor female front, rellor male front, remoraid female front, remoraid male front, riolu female front, riolu male front, rockruff female front, rockruff male front, rockruff-own-tempo female front, rockruff-own-tempo male front, roggenrola female front, roggenrola male front, rolycoly female front, rolycoly male front, rookidee female front, rookidee male front, roserade female front, roserade male front, rowlet female front, rowlet male front, rufflet female front, rufflet male front, sableye female front, sableye male front, sableye_redux female front, sableye_redux male front, salandit female front, salandit male front, sandile female front, sandile male front, sandshrew female front, sandshrew male front, sandshrew-alola female front, sandshrew-alola male front, sandygast female front, sandygast male front, scatterbug-archipelago female front, scatterbug-archipelago male front, scatterbug-continental female front, scatterbug-continental male front, scatterbug-elegant female front, scatterbug-elegant male front, scatterbug-fancy female front, scatterbug-fancy male front, scatterbug-garden female front, scatterbug-garden male front, scatterbug-high-plains female front, scatterbug-high-plains male front, scatterbug-icy-snow female front, scatterbug-icy-snow male front, scatterbug-jungle female front, scatterbug-jungle male front, scatterbug-marine female front, scatterbug-marine male front, scatterbug-meadow female front, scatterbug-meadow male front, scatterbug-modern female front, scatterbug-modern male front, scatterbug-monsoon female front, scatterbug-monsoon male front, scatterbug-ocean female front, scatterbug-ocean male front, scatterbug-poke-ball female front, scatterbug-poke-ball male front, scatterbug-polar female front, scatterbug-polar male front, scatterbug-river female front, scatterbug-river male front, scatterbug-sandstorm female front, scatterbug-sandstorm male front, scatterbug-savanna female front, scatterbug-savanna male front, scatterbug-sun female front, scatterbug-sun male front, scatterbug-tundra female front, scatterbug-tundra male front, scorbunny female front, scorbunny male front, scrafty female front, scrafty male front, seedot female front, seedot male front, seel_redux female front, seel_redux male front, sewaddle female front, sewaddle male front, shaymin-land female front, shaymin-land male front, shedinja female front, shedinja male front, shelgon female front, shelgon male front, shellder female front, shellder male front, shellos-east female front, shellos-east male front, shellos-west female front, shellos-west male front, shelmet female front, shelmet male front, shieldon female front, shieldon male front, shinx female front, shinx male front, shinx_redux female front, shinx_redux male front, shroodle female front, shroodle male front, shroomish female front, shroomish male front, shuckle_mega female front, shuckle_mega male front, shuppet female front, shuppet male front, shyduck female front, shyduck male front, silcoon female front, silcoon male front, silicobra female front, silicobra male front, sinistcha-masterpiece female front, sinistcha-masterpiece male front, sinistcha-unremarkable female front, sinistcha-unremarkable male front, sinistea-antique female front, sinistea-antique male front, sinistea-phony female front, sinistea-phony male front, sinistea_redux female front, sinistea_redux male front, sizzlipede female front, sizzlipede male front, skiddo female front, skiddo male front, skiploom female front, skiploom male front, skitty female front, skitty male front, skorupi female front, skorupi male front, skwovet female front, skwovet male front, slakoth female front, slakoth male front, slate female front, slate male front, sliggoo female front, sliggoo male front, sliggoo-hisui female front, sliggoo-hisui male front, slither-wing female front, slither-wing male front, slowpoke female front, slowpoke male front, slowpoke-galar female front, slowpoke-galar male front, slugma female front, slugma male front, slugma_redux female front, slugma_redux male front, slurpuff female front, slurpuff male front, smoochum female front, smoochum male front, snivy female front, snivy male front, snom female front, snom male front, snorunt female front, snorunt male front, snorunt_redux female front, snorunt_redux male front, snover female front, snover male front, snubbull female front, snubbull male front, sobble female front, sobble male front, solosis_redux female front, solosis_redux male front, spearow female front, spearow male front, spearow_redux female front, spearow_redux male front, spewpa-archipelago female front, spewpa-archipelago male front, spewpa-continental female front, spewpa-continental male front, spewpa-elegant female front, spewpa-elegant male front, spewpa-fancy female front, spewpa-fancy male front, spewpa-garden female front, spewpa-garden male front, spewpa-high-plains female front, spewpa-high-plains male front, spewpa-icy-snow female front, spewpa-icy-snow male front, spewpa-jungle female front, spewpa-jungle male front, spewpa-marine female front, spewpa-marine male front, spewpa-meadow female front, spewpa-meadow male front, spewpa-modern female front, spewpa-modern male front, spewpa-monsoon female front, spewpa-monsoon male front, spewpa-ocean female front, spewpa-ocean male front, spewpa-poke-ball female front, spewpa-poke-ball male front, spewpa-polar female front, spewpa-polar male front, spewpa-river female front, spewpa-river male front, spewpa-sandstorm female front, spewpa-sandstorm male front, spewpa-savanna female front, spewpa-savanna male front, spewpa-sun female front, spewpa-sun male front, spewpa-tundra female front, spewpa-tundra male front, spheal female front, spheal male front, spinarak female front, spinarak male front, spinda female front, spinda male front, spoink female front, spoink male front, sprigatito female front, sprigatito male front, spritzee female front, spritzee male front, squirtle female front, squirtle male front, staravia female front, staravia male front, starly female front, starly male front, staryu female front, staryu male front, steenee female front, steenee male front, steenee_redux female front, steenee_redux male front, stufful female front, stufful male front, stufful_redux female front, stufful_redux male front, stunfisk-galar female front, stunfisk-galar male front, stunky female front, stunky male front, sunflora female front, sunflora male front, sunkern female front, sunkern male front, swablu female front, swablu male front, swadloon female front, swadloon male front, swinub female front, swinub male front, swinub_redux female front, swinub_redux male front, swirlix female front, swirlix male front, tadbulb female front, tadbulb male front, taillow female front, taillow male front, tandemaus female front, tandemaus male front, tangela female front, tangela male front, tapu-lele female front, tapu-lele male front, tarountula female front, tarountula male front, tatsugiri-curly female front, tatsugiri-curly male front, tatsugiri-droopy female front, tatsugiri-droopy male front, tatsugiri-stretchy female front, tatsugiri-stretchy male front, teddiursa female front, teddiursa male front, tentacool female front, tentacool male front, tepig female front, tepig male front, terapagos female front, terapagos male front, throh_redux female front, throh_redux male front, thwackey female front, thwackey male front, timburr female front, timburr male front, tinkatink female front, tinkatink male front, tirtouga female front, tirtouga male front, togedemaru female front, togedemaru male front, togetic female front, togetic male front, torchic female front, torchic male front, totodile female front, totodile male front, toxel female front, toxel male front, tranquill female front, tranquill male front, trapinch female front, trapinch male front, trapinch_redux female front, trapinch_redux male front, treecko female front, treecko male front, trubbish female front, trubbish male front, trumbeak female front, trumbeak male front, turtwig female front, turtwig male front, turtwig_redux female front, turtwig_redux male front, tympole female front, tympole male front, tynamo female front, tynamo male front, tyrogue female front, tyrogue male front, tyrunt female front, tyrunt male front, umbreon female front, umbreon male front, unown-a female front, unown-a male front, unown-c female front, unown-c male front, unown-d female front, unown-d male front, unown-e female front, unown-e male front, unown-f female front, unown-f male front, unown-g female front, unown-g male front, unown-h female front, unown-h male front, unown-i female front, unown-i male front, unown-j female front, unown-j male front, unown-k female front, unown-k male front, unown-l female front, unown-l male front, unown-m female front, unown-m male front, unown-n female front, unown-n male front, unown-o female front, unown-o male front, unown-p female front, unown-p male front, unown-q female front, unown-q male front, unown-question female front, unown-question male front, unown-r female front, unown-r male front, unown-s female front, unown-s male front, unown-t female front, unown-t male front, unown-u female front, unown-u male front, unown-w female front, unown-w male front, unown-y female front, unown-y male front, unown-z female front, unown-z male front, vanillish female front, vanillish male front, vanillish_redux female front, vanillish_redux male front, vanillite_redux female front, vanillite_redux male front, vaporeon female front, vaporeon male front, varoom female front, varoom male front, venipede female front, venipede male front, venonat female front, venonat male front, vespiquen female front, vespiquen male front, vibrava female front, vibrava male front, victini female front, victini male front, volbeat female front, volbeat male front, voltorb female front, voltorb male front, voltorb-hisui female front, voltorb-hisui male front, vullaby female front, vullaby male front, vulpix-alola female front, vulpix-alola male front, wartortle female front, wartortle male front, wattrel female front, wattrel male front, weedle_redux female front, weedle_redux male front, weepinbell female front, weepinbell male front, whirlipede female front, whirlipede male front, whismur female front, whismur male front, whismur_redux female front, whismur_redux male front, wiglett female front, wiglett male front, wimpod female front, wimpod male front, wishiwashi-solo female front, wishiwashi-solo male front, wispywaspy female front, wispywaspy male front, wooloo female front, wooloo male front, wooper female front, wooper male front, wooper-paldea female front, wooper-paldea male front, wormadam-trash female front, wormadam-trash male front, wurmple female front, wurmple male front, wynaut female front, wynaut male front, xatu female front, xatu male front, yamask female front, yamask male front, yamask-galar female front, yamask-galar male front, yamper female front, yamper male front, zeraora_mega female front, zeraora_mega male front, zorua female front, zorua male front, zorua-hisui female front, zorua-hisui male front, zubat female front, zubat male front — 1548 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/froslass/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0314_spritzee_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0314_spritzee_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magby/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magby/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sewaddle/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sewaddle/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baltoy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/baltoy/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minior-yellow-meteor/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lillipup/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lillipup/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darumaka_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/darumaka_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tangela/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tangela/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swinub_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swinub_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0334_dartrix_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0334_dartrix_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rowlet/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rowlet/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scatterbug-savanna/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slakoth/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slakoth/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corsola/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corsola/female/front.png`
- … 1518 more

### 2. arceus-bug female front, arceus-bug male front, arceus-dark female front, arceus-dark male front, arceus-dragon female front, arceus-dragon male front, arceus-electric female front, arceus-electric male front, arceus-fairy female front, arceus-fairy male front, arceus-fighting female front, arceus-fighting male front, arceus-fire female front, arceus-fire male front, arceus-flying female front, arceus-flying male front, arceus-ghost female front, arceus-ghost male front, arceus-grass female front, arceus-grass male front, arceus-ground female front, arceus-ground male front, arceus-ice female front, arceus-ice male front, arceus-normal female front, arceus-normal male front, arceus-poison female front, arceus-poison male front, arceus-psychic female front, arceus-psychic male front, arceus-rock female front, arceus-rock male front, arceus-steel female front, arceus-steel male front, arceus-unknown female front, arceus-unknown male front, arceus-water female front, arceus-water male front — 38 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-flying/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-flying/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-poison/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-poison/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-unknown/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-unknown/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-normal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-normal/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-steel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-steel/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ghost/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ghost/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fire/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fire/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-dragon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-dragon/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-electric/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-electric/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fighting/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fighting/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-rock/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-rock/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-dark/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-dark/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-water/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-water/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fairy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-fairy/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ground/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arceus-ground/female/front.png`
- … 8 more

### 3. vivillon-archipelago female front, vivillon-archipelago male front, vivillon-continental female front, vivillon-continental male front, vivillon-elegant female front, vivillon-elegant male front, vivillon-fancy female front, vivillon-fancy male front, vivillon-garden female front, vivillon-garden male front, vivillon-icy-snow female front, vivillon-icy-snow male front, vivillon-jungle female front, vivillon-jungle male front, vivillon-marine female front, vivillon-marine male front, vivillon-modern female front, vivillon-modern male front, vivillon-monsoon female front, vivillon-monsoon male front, vivillon-ocean female front, vivillon-ocean male front, vivillon-poke-ball female front, vivillon-poke-ball male front, vivillon-polar female front, vivillon-polar male front, vivillon-river female front, vivillon-river male front, vivillon-sandstorm female front, vivillon-sandstorm male front, vivillon-savanna female front, vivillon-savanna male front, vivillon-sun female front, vivillon-sun male front, vivillon-tundra female front, vivillon-tundra male front — 36 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-polar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-polar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-fancy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-fancy/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-savanna/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-savanna/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-garden/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-garden/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-icy-snow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-icy-snow/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-tundra/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-tundra/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-monsoon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-monsoon/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-ocean/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-ocean/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-poke-ball/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-poke-ball/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-modern/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-modern/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-sandstorm/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-sandstorm/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-archipelago/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-archipelago/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-river/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-river/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-jungle/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-jungle/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-marine/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vivillon-marine/female/front.png`
- … 6 more

### 4. alakazam_redux female front, alakazam_redux male front, bronzong female front, bronzong male front, cinccino female front, cinccino male front, drednaw female front, drednaw male front, forretress female front, forretress male front, gengar-gmax female front, gengar-gmax male front, gengar_mega_x female front, gengar_mega_x male front, kadabra female front, kadabra male front, pentadug female front, pentadug male front, piloswine_redux female front, piloswine_redux male front, quagsire female front, quagsire male front, sandslash female front, sandslash male front, simisear female front, simisear male front, starmie female front, starmie male front, swalot female front, swalot male front, tentacruel female front, tentacruel male front — 32 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pentadug/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pentadug/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/simisear/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/simisear/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/forretress/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/forretress/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sandslash/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sandslash/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bronzong/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bronzong/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/piloswine_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/piloswine_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tentacruel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tentacruel/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gengar_mega_x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gengar_mega_x/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gengar-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gengar-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/starmie/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/quagsire/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/quagsire/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kadabra/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kadabra/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swalot/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/swalot/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cinccino/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cinccino/female/front.png`
- … 2 more

### 5. silvally-bug female front, silvally-bug male front, silvally-dark female front, silvally-dark male front, silvally-dragon female front, silvally-dragon male front, silvally-electric female front, silvally-electric male front, silvally-fighting female front, silvally-fighting male front, silvally-fire female front, silvally-fire male front, silvally-flying female front, silvally-flying male front, silvally-ghost female front, silvally-ghost male front, silvally-grass female front, silvally-grass male front, silvally-ground female front, silvally-ground male front, silvally-ice female front, silvally-ice male front, silvally-normal female front, silvally-normal male front, silvally-poison female front, silvally-poison male front, silvally-psychic female front, silvally-psychic male front, silvally-steel female front, silvally-steel male front, silvally-water female front, silvally-water male front — 32 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fighting/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fighting/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ice/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-water/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-water/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-normal/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-dragon/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-poison/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-grass/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ground/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-steel/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-fire/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-ghost/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-electric/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-electric/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-bug/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-psychic/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-psychic/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-flying/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/silvally-flying/female/front.png`
- … 2 more

### 6. cobalion female front, cobalion male front, furfrou-dandy female front, furfrou-dandy male front, furfrou-diamond female front, furfrou-diamond male front, furfrou-heart female front, furfrou-heart male front, furfrou-kabuki female front, furfrou-kabuki male front, furfrou-la-reine female front, furfrou-la-reine male front, furfrou-matron female front, furfrou-matron male front, furfrou-natural female front, furfrou-natural male front, furfrou-pharaoh female front, furfrou-pharaoh male front, furfrou-star female front, furfrou-star male front, iron-crown female front, iron-crown male front — 22 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-star/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-star/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-diamond/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-diamond/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-matron/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-matron/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/iron-crown/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/iron-crown/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-natural/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-natural/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-kabuki/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-kabuki/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cobalion/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cobalion/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-heart/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-heart/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-la-reine/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-la-reine/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-dandy/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-dandy/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-pharaoh/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/furfrou-pharaoh/female/front.png`

### 7. camerupt-mega female front, camerupt-mega male front, decidueye_hisuian_mega female front, decidueye_hisuian_mega male front, garbodor-gmax female front, garbodor-gmax male front, garbodor_mega female front, garbodor_mega male front, roserade_mega female front, roserade_mega male front, typhlosion_mega female front, typhlosion_mega male front — 12 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/roserade_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/roserade_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/camerupt-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/camerupt-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/decidueye_hisuian_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/decidueye_hisuian_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/garbodor_mega/female/front.png`

### 8. altaria-mega female front, altaria-mega male front, chandelure_mega female front, chandelure_mega male front, chandelure_redux_mega female front, chandelure_redux_mega male front, exploud_redux female front, exploud_redux male front, phanfernal female front, phanfernal male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_redux_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/phanfernal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/phanfernal/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/chandelure_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/altaria-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/altaria-mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/exploud_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/exploud_redux/female/front.png`

### 9. flabebe-blue female front, flabebe-blue male front, flabebe-orange female front, flabebe-orange male front, flabebe-red female front, flabebe-red male front, flabebe-white female front, flabebe-white male front, flabebe-yellow female front, flabebe-yellow male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-blue/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-blue/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-yellow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-yellow/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-red/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-red/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-orange/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-orange/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-white/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flabebe-white/female/front.png`

### 10. floette-blue female front, floette-blue male front, floette-orange female front, floette-orange male front, floette-red female front, floette-red male front, floette-white female front, floette-white male front, floette-yellow female front, floette-yellow male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-orange/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-orange/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-white/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-white/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-blue/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-blue/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-red/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-red/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-yellow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floette-yellow/female/front.png`

### 11. florges-blue female front, florges-blue male front, florges-orange female front, florges-orange male front, florges-red female front, florges-red male front, florges-white female front, florges-white male front, florges-yellow female front, florges-yellow male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-orange/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-orange/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-blue/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-blue/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-red/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-red/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-yellow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-yellow/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-white/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/florges-white/female/front.png`

### 12. genesect female front, genesect male front, genesect-burn female front, genesect-burn male front, genesect-chill female front, genesect-chill male front, genesect-douse female front, genesect-douse male front, genesect-shock female front, genesect-shock male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-shock/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-shock/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-douse/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-douse/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-burn/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-burn/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-chill/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/genesect-chill/female/front.png`

### 13. corviknight female front, corviknight male front, pikachu-gmax female front, pikachu-gmax male front, pikachu_partner_mega female front, pikachu_partner_mega male front, scrafty-mega female front, scrafty-mega male front, scrafty_mega female front, scrafty_mega male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corviknight/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corviknight/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu_partner_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/pikachu_partner_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/scrafty-mega/female/front.png`

### 14. kilowattrel female front, kilowattrel male front, squawkabilly-blue-plumage female front, squawkabilly-blue-plumage male front, squawkabilly-green-plumage female front, squawkabilly-green-plumage male front, squawkabilly-white-plumage female front, squawkabilly-white-plumage male front, squawkabilly-yellow-plumage female front, squawkabilly-yellow-plumage male front — 10 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-blue-plumage/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-blue-plumage/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-green-plumage/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-green-plumage/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-yellow-plumage/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-yellow-plumage/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kilowattrel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kilowattrel/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-white-plumage/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/squawkabilly-white-plumage/female/front.png`

### 15. cpf_0111_dunsparce_bt_alt_forms_toxic_form_1 female front, cpf_0111_dunsparce_bt_alt_forms_toxic_form_1 male front, cpf_0112_dunsparce_bt_alt_forms_earth_form_2 female front, cpf_0112_dunsparce_bt_alt_forms_earth_form_2 male front, cpf_0114_dunsparce_bt_alt_forms_insect_form_4 female front, cpf_0114_dunsparce_bt_alt_forms_insect_form_4 male front, cpf_0115_dunsparce_bt_alt_forms_spooky_form_5 female front, cpf_0115_dunsparce_bt_alt_forms_spooky_form_5 male front — 8 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0112_dunsparce_bt_alt_forms_earth_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0112_dunsparce_bt_alt_forms_earth_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0114_dunsparce_bt_alt_forms_insect_form_4/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0114_dunsparce_bt_alt_forms_insect_form_4/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0111_dunsparce_bt_alt_forms_toxic_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0111_dunsparce_bt_alt_forms_toxic_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0115_dunsparce_bt_alt_forms_spooky_form_5/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0115_dunsparce_bt_alt_forms_spooky_form_5/female/front.png`

### 16. clefable female front, clefable male front, cpf_0012_clefable_alternate_form_1 female front, cpf_0012_clefable_alternate_form_1 male front, glalie female front, glalie male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0012_clefable_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0012_clefable_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glalie/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/glalie/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/clefable/female/front.png`

### 17. cpf_0018_wigglytuff_alternate_form_1 female front, cpf_0018_wigglytuff_alternate_form_1 male front, wigglytuff female front, wigglytuff male front, wigglytuff_apex female front, wigglytuff_apex male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0018_wigglytuff_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0018_wigglytuff_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wigglytuff/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wigglytuff/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wigglytuff_apex/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/wigglytuff_apex/female/front.png`

### 18. cpf_0285_klang_alternate_form_1 female front, cpf_0285_klang_alternate_form_1 male front, klang female front, klang male front, terrakion female front, terrakion male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0285_klang_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0285_klang_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/klang/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/klang/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/terrakion/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/terrakion/female/front.png`

### 19. earthretha_belstatue female front, earthretha_belstatue male front, earthretha_belstatue_1 female front, earthretha_belstatue_1 male front, earthretha_belstatue_2 female front, earthretha_belstatue_2 male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_belstatue_1/female/front.png`

### 20. boltund female front, boltund male front, eevee-gmax female front, eevee-gmax male front, sylveon female front, sylveon male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/eevee-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/eevee-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/boltund/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/boltund/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sylveon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sylveon/female/front.png`

### 21. finizen female front, finizen male front, fogging female front, fogging male front, palafin-zero female front, palafin-zero male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/fogging/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/fogging/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/finizen/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/finizen/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/palafin-zero/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/palafin-zero/female/front.png`

### 22. gourgeist-large female front, gourgeist-large male front, gourgeist-small female front, gourgeist-small male front, gourgeist-super female front, gourgeist-super male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-small/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-small/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-large/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-large/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-super/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gourgeist-super/female/front.png`

### 23. corvisquire female front, corvisquire male front, graveler female front, graveler male front, graveler-alola female front, graveler-alola male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/graveler-alola/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/graveler-alola/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/graveler/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/graveler/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corvisquire/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corvisquire/female/front.png`

### 24. groudon female front, groudon male front, groudon-primal female front, groudon-primal male front, hariyama female front, hariyama male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/groudon-primal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/groudon-primal/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/groudon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/groudon/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hariyama/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hariyama/female/front.png`

### 25. machamp female front, machamp male front, machamp-gmax female front, machamp-gmax male front, machamp_mega female front, machamp_mega male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/machamp-gmax/female/front.png`

### 26. ogerpon-cornerstone-mask female front, ogerpon-cornerstone-mask male front, ogerpon-hearthflame-mask female front, ogerpon-hearthflame-mask male front, ogerpon-wellspring-mask female front, ogerpon-wellspring-mask male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ogerpon-cornerstone-mask/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ogerpon-cornerstone-mask/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ogerpon-wellspring-mask/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ogerpon-wellspring-mask/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ogerpon-hearthflame-mask/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ogerpon-hearthflame-mask/female/front.png`

### 27. cpf_0034_ponyta_alternate_form_1 female front, cpf_0034_ponyta_alternate_form_1 male front, keldeo-ordinary female front, keldeo-ordinary male front, ponyta female front, ponyta male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ponyta/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ponyta/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/keldeo-ordinary/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/keldeo-ordinary/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0034_ponyta_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0034_ponyta_alternate_form_1/female/front.png`

### 28. landorus-incarnate female front, landorus-incarnate male front, thundurus-incarnate female front, thundurus-incarnate male front, tornadus-incarnate female front, tornadus-incarnate male front — 6 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tornadus-incarnate/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tornadus-incarnate/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/thundurus-incarnate/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/thundurus-incarnate/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/landorus-incarnate/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/landorus-incarnate/female/front.png`

### 29. absol female front, absol male front, cpf_0185_absol_alternate_form_2 female front, cpf_0185_absol_alternate_form_2 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/absol/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0185_absol_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0185_absol_alternate_form_2/female/front.png`

### 30. aegislash_blade_redux female front, aegislash_blade_redux male front, lucario_mega_z female front, lucario_mega_z male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aegislash_blade_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario_mega_z/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lucario_mega_z/female/front.png`

### 31. arcanine female front, arcanine male front, arcanine-hisui female front, arcanine-hisui male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine-hisui/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine-hisui/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arcanine/female/front.png`

### 32. arctibax female front, arctibax male front, gengar female front, gengar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arctibax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/arctibax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gengar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gengar/female/front.png`

### 33. basculegion-female female front, basculegion-female male front, basculegion-male female front, basculegion-male male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-female/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/basculegion-male/female/front.png`

### 34. blastoise-gmax female front, blastoise-gmax male front, blastoise_mega_x female front, blastoise_mega_x male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/blastoise-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/blastoise-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/blastoise_mega_x/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/blastoise_mega_x/female/front.png`

### 35. blissey female front, blissey male front, cpf_0130_blissey_alternate_form_1 female front, cpf_0130_blissey_alternate_form_1 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/blissey/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/blissey/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0130_blissey_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0130_blissey_alternate_form_1/female/front.png`

### 36. boarlock female front, boarlock male front, giratina-origin female front, giratina-origin male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/boarlock/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/boarlock/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/giratina-origin/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/giratina-origin/female/front.png`

### 37. bunnelby female front, bunnelby male front, cpf_0311_bunnelby_alternate_form_1 female front, cpf_0311_bunnelby_alternate_form_1 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bunnelby/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/bunnelby/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0311_bunnelby_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0311_bunnelby_alternate_form_1/female/front.png`

### 38. butterfree-gmax female front, butterfree-gmax male front, butterfree_mega female front, butterfree_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/butterfree-gmax/female/front.png`

### 39. centiskorch-gmax female front, centiskorch-gmax male front, centiskorch_mega female front, centiskorch_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/centiskorch_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/centiskorch_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/centiskorch-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/centiskorch-gmax/female/front.png`

### 40. cetoddle_redux female front, cetoddle_redux male front, cpf_0058_chansey_alternate_form_1 female front, cpf_0058_chansey_alternate_form_1 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cetoddle_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cetoddle_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0058_chansey_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0058_chansey_alternate_form_1/female/front.png`

### 41. cinderace-gmax female front, cinderace-gmax male front, cinderace_mega female front, cinderace_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cinderace_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cinderace_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cinderace-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cinderace-gmax/female/front.png`

### 42. copperajah-gmax female front, copperajah-gmax male front, copperajah_mega female front, copperajah_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/copperajah-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/copperajah-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/copperajah_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/copperajah_mega/female/front.png`

### 43. corviknight-gmax female front, corviknight-gmax male front, corviknight_mega female front, corviknight_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corviknight-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corviknight-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corviknight_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/corviknight_mega/female/front.png`

### 44. beedrill female front, beedrill male front, cpf_0005_beedrill_alternate_form_2 female front, cpf_0005_beedrill_alternate_form_2 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0005_beedrill_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0005_beedrill_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beedrill/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beedrill/female/front.png`

### 45. cpf_0013_vulpix_alternate_form_2 female front, cpf_0013_vulpix_alternate_form_2 male front, cpf_0014_vulpix_alternate_form_3 female front, cpf_0014_vulpix_alternate_form_3 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0014_vulpix_alternate_form_3/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0014_vulpix_alternate_form_3/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0013_vulpix_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0013_vulpix_alternate_form_2/female/front.png`

### 46. cpf_0126_octillery_alternate_form_1 female front, cpf_0126_octillery_alternate_form_1 male front, octillery female front, octillery male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0126_octillery_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0126_octillery_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/octillery/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/octillery/female/front.png`

### 47. cpf_0129_hitmontop_alternate_form_1 female front, cpf_0129_hitmontop_alternate_form_1 male front, hitmontop female front, hitmontop male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0129_hitmontop_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0129_hitmontop_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hitmontop/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hitmontop/female/front.png`

### 48. cpf_0152_breloom_alternate_form_2 female front, cpf_0152_breloom_alternate_form_2 male front, cpf_0153_breloom_alternate_form_3 female front, cpf_0153_breloom_alternate_form_3 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0152_breloom_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0152_breloom_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0153_breloom_alternate_form_3/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0153_breloom_alternate_form_3/female/front.png`

### 49. cpf_0189_salamence_alternate_form_1 female front, cpf_0189_salamence_alternate_form_1 male front, cpf_0191_salamence_alternate_mega_form_3 female front, cpf_0191_salamence_alternate_mega_form_3 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0191_salamence_alternate_mega_form_3/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0191_salamence_alternate_mega_form_3/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0189_salamence_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0189_salamence_alternate_form_1/female/front.png`

### 50. cpf_0209_lopunny_bluetowel_alternate_forms_form_1 female front, cpf_0209_lopunny_bluetowel_alternate_forms_form_1 male front, cpf_0211_lopunny_alternate_mega_form_3 female front, cpf_0211_lopunny_alternate_mega_form_3 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0209_lopunny_bluetowel_alternate_forms_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0209_lopunny_bluetowel_alternate_forms_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0211_lopunny_alternate_mega_form_3/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0211_lopunny_alternate_mega_form_3/female/front.png`

### 51. cpf_0221_skorupi_alternate_form_1 female front, cpf_0221_skorupi_alternate_form_1 male front, cpf_0222_skorupi_alternate_form_2 female front, cpf_0222_skorupi_alternate_form_2 male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0222_skorupi_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0222_skorupi_alternate_form_2/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0221_skorupi_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0221_skorupi_alternate_form_1/female/front.png`

### 52. cpf_0286_klinklang_alternate_form_1 female front, cpf_0286_klinklang_alternate_form_1 male front, klinklang female front, klinklang male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0286_klinklang_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0286_klinklang_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/klinklang/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/klinklang/female/front.png`

### 53. cpf_0290_lampent_alternate_form_1 female front, cpf_0290_lampent_alternate_form_1 male front, lampent female front, lampent male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0290_lampent_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0290_lampent_alternate_form_1/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lampent/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/lampent/female/front.png`

### 54. cpf_0155_delcatty_alternate_form_1 female front, cpf_0155_delcatty_alternate_form_1 male front, delcatty female front, delcatty male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delcatty/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delcatty/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0155_delcatty_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0155_delcatty_alternate_form_1/female/front.png`

### 55. delphox_serena female front, delphox_serena male front, gardevoir_redux female front, gardevoir_redux male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox_serena/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/delphox_serena/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gardevoir_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gardevoir_redux/female/front.png`

### 56. dondozo female front, dondozo male front, gliscor_redux female front, gliscor_redux male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dondozo/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dondozo/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gliscor_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gliscor_redux/female/front.png`

### 57. dudunsparce-three-segment female front, dudunsparce-three-segment male front, dudunsparce-two-segment female front, dudunsparce-two-segment male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dudunsparce-two-segment/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dudunsparce-two-segment/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dudunsparce-three-segment/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/dudunsparce-three-segment/female/front.png`

### 58. cpf_0210_lopunny_alternate_form_2 female front, cpf_0210_lopunny_alternate_form_2 male front, earthretha_pangshi female front, earthretha_pangshi male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_pangshi/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/earthretha_pangshi/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0210_lopunny_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0210_lopunny_alternate_form_2/female/front.png`

### 59. empoleon_mega female front, empoleon_mega male front, mamoswine_redux_mega female front, mamoswine_redux_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/empoleon_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/empoleon_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mamoswine_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mamoswine_redux_mega/female/front.png`

### 60. flutter-mane female front, flutter-mane male front, vulpix female front, vulpix male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flutter-mane/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flutter-mane/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vulpix/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/vulpix/female/front.png`

### 61. gastrodon-east female front, gastrodon-east male front, gastrodon-west female front, gastrodon-west male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gastrodon-west/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gastrodon-west/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gastrodon-east/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/gastrodon-east/female/front.png`

### 62. grimmsnarl-gmax female front, grimmsnarl-gmax male front, grimmsnarl_mega female front, grimmsnarl_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/grimmsnarl_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/grimmsnarl_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/grimmsnarl-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/grimmsnarl-gmax/female/front.png`

### 63. cpf_0015_ninetales_alternate_form_2 female front, cpf_0015_ninetales_alternate_form_2 male front, hippotaton female front, hippotaton male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hippotaton/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hippotaton/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0015_ninetales_alternate_form_2/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0015_ninetales_alternate_form_2/female/front.png`

### 64. cpf_0054_hitmonlee_alternate_form_1 female front, cpf_0054_hitmonlee_alternate_form_1 male front, hitmonlee female front, hitmonlee male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hitmonlee/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/hitmonlee/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0054_hitmonlee_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0054_hitmonlee_alternate_form_1/female/front.png`

### 65. kangaskhan female front, kangaskhan male front, kangaskhan-mega female front, kangaskhan-mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kangaskhan/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kangaskhan/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kangaskhan-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kangaskhan-mega/female/front.png`

### 66. kingler-gmax female front, kingler-gmax male front, kingler_mega female front, kingler_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler-gmax/female/front.png`

### 67. kyogre female front, kyogre male front, kyogre-primal female front, kyogre-primal male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kyogre/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kyogre/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kyogre-primal/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kyogre-primal/female/front.png`

### 68. linoone female front, linoone male front, linoone-galar female front, linoone-galar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/linoone-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/linoone-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/linoone/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/linoone/female/front.png`

### 69. magearna female front, magearna male front, magearna-original female front, magearna-original male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magearna/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magearna/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magearna-original/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/magearna-original/female/front.png`

### 70. maushold-family-of-four female front, maushold-family-of-four male front, maushold-family-of-three female front, maushold-family-of-three male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/maushold-family-of-three/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/maushold-family-of-three/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/maushold-family-of-four/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/maushold-family-of-four/female/front.png`

### 71. melmetal-gmax female front, melmetal-gmax male front, melmetal_mega female front, melmetal_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/melmetal-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/melmetal-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/melmetal_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/melmetal_mega/female/front.png`

### 72. meowth-gmax female front, meowth-gmax male front, meowth_partner_mega female front, meowth_partner_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowth-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowth-gmax/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowth_partner_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/meowth_partner_mega/female/front.png`

### 73. kingler_redux female front, kingler_redux male front, minccino_redux female front, minccino_redux male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minccino_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/minccino_redux/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/kingler_redux/female/front.png`

### 74. moltres female front, moltres male front, moltres-galar female front, moltres-galar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/moltres/female/front.png`

### 75. mr-mime female front, mr-mime male front, mr-mime-galar female front, mr-mime-galar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mr-mime-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mr-mime-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mr-mime/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/mr-mime/female/front.png`

### 76. cpf_0075_omastar_alternate_form_1 female front, cpf_0075_omastar_alternate_form_1 male front, omastar female front, omastar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/omastar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/omastar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0075_omastar_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0075_omastar_alternate_form_1/female/front.png`

### 77. orbeetle-gmax female front, orbeetle-gmax male front, orbeetle_mega female front, orbeetle_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/orbeetle_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/orbeetle_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/orbeetle-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/orbeetle-gmax/female/front.png`

### 78. cpf_0220_purugly_alternate_form_1 female front, cpf_0220_purugly_alternate_form_1 male front, purugly female front, purugly male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/purugly/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/purugly/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0220_purugly_alternate_form_1/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/cpf_0220_purugly_alternate_form_1/female/front.png`

### 79. goldeen female front, goldeen male front, rhyhorn female front, rhyhorn male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rhyhorn/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/rhyhorn/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/goldeen/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/goldeen/female/front.png`

### 80. sandaconda-gmax female front, sandaconda-gmax male front, sandaconda_mega female front, sandaconda_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sandaconda_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sandaconda_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sandaconda-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sandaconda-gmax/female/front.png`

### 81. floragato female front, floragato male front, sawk female front, sawk male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sawk/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sawk/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floragato/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/floragato/female/front.png`

### 82. seaking female front, seaking male front, whimsicott female front, whimsicott male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/seaking/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/seaking/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/whimsicott/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/whimsicott/female/front.png`

### 83. sharpedo female front, sharpedo male front, sharpedo-mega female front, sharpedo-mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sharpedo/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sharpedo/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sharpedo-mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sharpedo-mega/female/front.png`

### 84. crocalor female front, crocalor male front, shiftry female front, shiftry male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/shiftry/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/shiftry/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/crocalor/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/crocalor/female/front.png`

### 85. slowbro-galar female front, slowbro-galar male front, victreebel female front, victreebel male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slowbro-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slowbro-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/victreebel/female/front.png`

### 86. slowking female front, slowking male front, slowking-galar female front, slowking-galar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slowking/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slowking/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slowking-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/slowking-galar/female/front.png`

### 87. sneasel female front, sneasel male front, sneasel-hisui female front, sneasel-hisui male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sneasel/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sneasel/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sneasel-hisui/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/sneasel-hisui/female/front.png`

### 88. snorlax_redux female front, snorlax_redux male front, snorlax_redux_mega female front, snorlax_redux_mega male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_redux_mega/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_redux_mega/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_redux/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/snorlax_redux/female/front.png`

### 89. tauros female front, tauros male front, tauros-paldea-combat-breed female front, tauros-paldea-combat-breed male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tauros/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tauros/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tauros-paldea-combat-breed/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/tauros-paldea-combat-breed/female/front.png`

### 90. flapple-gmax female front, flapple-gmax male front, toxtricity-low-key female front, toxtricity-low-key male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/toxtricity-low-key/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flapple-gmax/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/flapple-gmax/female/front.png`

### 91. typhlosion female front, typhlosion male front, typhlosion-hisui female front, typhlosion-hisui male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion-hisui/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion-hisui/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/typhlosion/female/front.png`

### 92. iron-leaves female front, iron-leaves male front, virizion female front, virizion male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/virizion/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/virizion/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/iron-leaves/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/iron-leaves/female/front.png`

### 93. golurk female front, golurk male front, zamazenta-crowned female front, zamazenta-crowned male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zamazenta-crowned/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zamazenta-crowned/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golurk/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/golurk/female/front.png`

### 94. zarude female front, zarude male front, zarude-dada female front, zarude-dada male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zarude/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zarude/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zarude-dada/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zarude-dada/female/front.png`

### 95. zigzagoon female front, zigzagoon male front, zigzagoon-galar female front, zigzagoon-galar male front — 4 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zigzagoon-galar/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zigzagoon-galar/female/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zigzagoon/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/zigzagoon/female/front.png`

### 96. abomasnow female front, abomasnow male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/abomasnow/female/front.png`

### 97. aipom female front, aipom male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aipom/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/aipom/female/front.png`

### 98. alakazam female front, alakazam male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/alakazam/female/front.png`

### 99. ambipom female front, ambipom male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ambipom/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/ambipom/female/front.png`

### 100. beautifly female front, beautifly male front — 2 files

Dimensions: 160x80

Source buckets: hg_engine_ready

- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beautifly/male/front.png`
- `DS01_Expanded_Community_Sprite_Library_2026-09-22/hg_engine_ready/data/graphics/sprites/beautifly/female/front.png`

## Duplicated concept candidates

None detected.

