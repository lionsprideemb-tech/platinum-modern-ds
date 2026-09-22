# DS03 Twinleaf Target Resource Allocation

The pinned HeartGold source was audited before assigning target IDs.

Latest passing capacity audit:
- workflow run: `35764349659`
- map header next append: **540**
- matrix next append: **288**
- zone-event next append: **491**
- script source-ID next append: **965**
- message next append: **829**
- land-data NARC next append: **676**

## Allocation policy

Twinleaf uses **append-only resources**. No Johto/Kanto resource is replaced during the proof-of-concept.

This gives us two safety properties:

1. HG-Engine's original world remains available for debugging/fallback.
2. Every imported Sinnoh resource has an obvious project-owned ID range.

## Reserved Twinleaf ranges

- map headers: **540–546**
- matrices: **288–293**
- zone events: **491–497**
- messages: **829–835**
- scripts/init scripts: **965–978 reserved**
- land-data members: **676–681**

The exact one-to-one mapping is stored in `platinum_port/twinleaf/target_allocation.json`.

## Matrix strategy

For the first bootable Twinleaf proof we will **not** import Platinum's entire 30×30 Sinnoh main matrix.

Instead:
- Twinleaf exterior receives an isolated 1×1 target matrix.
- each distinct interior receives a 1×1 matrix.
- the two generic residences share one matrix/member.

That lets us certify rendering, collision, events and interior warps without requiring Route 201, Sandgem, Verity, or hundreds of unrelated Sinnoh land-data members to exist yet.

When the contiguous world slice expands, the exterior proof matrix can be replaced by a converted/remapped regional matrix without changing Twinleaf's visual land-data member.

## Deferred IDs

Area-data, building-model, building-texture and related graphics resources are intentionally not allocated yet. Those archives must be audited first because map geometry can be valid while referenced building models/textures are still absent.
