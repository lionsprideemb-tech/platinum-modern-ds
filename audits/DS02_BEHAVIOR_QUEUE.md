# DS02 Behavior Audit Queue

Static file presence is only the first half of the #001–1025 certification.

A species can have stats, learnsets and graphics and still need engine work for a special mechanic. After the static coverage audit passes, DS02 will review only mechanics that can materially change in-battle, evolution, form, or storage behavior.

## Behavior groups

### Form/state changes
- battle-triggered form changes
- item/mask/plate-driven forms
- weather/terrain-driven forms
- HP-threshold forms
- party-composition forms
- school/solo or aggregate forms
- disguise/stance/hero-style states

### Ability-dependent species behavior
- signature abilities that alter form/state
- abilities requiring partner/field interactions
- abilities with modern generation-specific rules

### Evolution methods
- trade replacements/adaptations
- move-known evolutions
- time-of-day/location evolutions
- friendship/affection evolutions
- party/species-dependent evolutions
- walking/step requirements
- unusual Gen VIII/IX conditions

### Signature move behavior
- moves that transform the user
- moves tied to forms/items
- multi-Pokémon interactions
- modern targeting or field effects

### Persistence/UI integrity
- party
- PC storage
- Pokédex registration
- save/load
- breeding/egg species
- trainer/wild usage
- icon/sprite/form restoration

## Certification rule

Do not mark a special mechanic as working because its constant or data row exists.

A behavior is VERIFIED only when its implementation path is identified and either:
1. covered by an existing automated HG-Engine test, or
2. covered by a project regression test we add.

Adapted mechanics must be explicitly documented rather than silently behaving differently from the modern games.
