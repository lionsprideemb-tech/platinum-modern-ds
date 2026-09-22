# DS01 Community Sprite Staging

This directory is intentionally isolated from the active DS01/HG-Engine build.

- The archive is **not** referenced by `engine-overlay/`.
- No build workflow consumes these sprites yet.
- Nothing here changes species constants, Pokédex data, encounter data, or compiled graphics.
- Assets remain staged until they are explicitly audited/mapped into DS01.

Archive: `DS01_Expanded_Community_Sprite_Library_2026-09-22.zip`

SHA-256:
`6f676782799cb206d55a00260a693fccc25f5f59c8fc6b2819aeceaf1beb38f0`

Contents include the converted Mercury/Reborn/Elite Redux material plus curated DS-style community resources, conversion manifests, credits/provenance, and reference-only material.

Do not copy the entire archive wholesale into `engine-overlay/data/graphics/sprites/`. Integrate approved species/forms individually after their HG-Engine identifiers exist.
