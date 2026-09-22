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
- area-data next append: **106**
- prop/config-set next append: **104**
- prop-texture next append: **104**
- map-texture next append: **106**
- exterior model next append: **340**
- interior model next append: **222**

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
- area-data members: **106–107**
- prop/config sets: **104–105**
- prop-texture sets: **104–105**
- map-texture sets: **106–107**
- exterior prop models: **340–343**
- interior prop models: **222–243**

The exact one-to-one mapping is stored in `platinum_port/twinleaf/target_allocation.json`.

## Matrix strategy

For the first bootable Twinleaf proof we will **not** import Platinum's entire 30×30 Sinnoh main matrix.

Instead:
- Twinleaf exterior receives an isolated 1×1 target matrix.
- each distinct interior receives a 1×1 matrix.
- the two generic residences share one matrix/member.

That lets us certify rendering, collision, events and interior warps without requiring Route 201, Sandgem, Verity, or hundreds of unrelated Sinnoh land-data members to exist yet.

When the contiguous world slice expands, the exterior proof matrix can be replaced by a converted/remapped regional matrix without changing Twinleaf's visual land-data member.

## Visual resource mapping

The visual archives have now been audited and allocated. The exact source files and model-ID remaps are stored in `platinum_port/twinleaf/visual_resources.json`.

Only models actually placed by the initial Twinleaf maps are imported for the proof build: 4 exterior models and 22 interior models. Platinum model IDs cannot be preserved because those slots are already occupied by HGSS assets, so building placement records are rewritten to the append-only target IDs.

For the first rendering proof, HGSS dynamic texture animation is disabled (`0xFFFF`). Special behaviors keyed to original model IDs—such as door/laptop animation hooks—remain a later compatibility gate after static rendering is certified.
