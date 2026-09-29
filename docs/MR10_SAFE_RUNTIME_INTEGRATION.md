# MR10 Safe Runtime Integration

Status: ACTIVE  
Branch: `feature/mr10-safe-runtime-integration`  
Date: 2026-09-29

## Locked partition

MR09 staged **883** source Ability rows. The runtime partition now resolves them
against the official 0..310 Ability namespace instead of assigning duplicate IDs
to ordinary Pokémon Abilities.

- 269 staged rows map to canonical Ability IDs.
- 614 staged rows are genuinely non-canonical identities.
- 5 previously approved Mercury-only identities from the earlier runtime-design
  branch are carried forward at their reserved IDs 317..321.
- The final Mercury custom namespace is therefore **619 IDs, 311..929**.
- This remains inside the existing **10-bit / 0..1023** save-compatible Ability
  storage. No save-block growth is needed.
- The 93 staged `new_engine_system` rows stay mechanically quarantined for the
  upcoming design review.
- The safe lane contains **795 decided rows** total: 263 canonical identities /
  overrides and 532 Mercury custom identities.

## Order of work

1. MR10A — materialize all custom IDs/names/descriptions without claiming their
   mechanics are live.
2. MR10B — apply the safe canonical/Elite-Redux override layer, excluding the
   six canonical rows classified as new-engine-system.
3. MR10C+ — install safe custom mechanics by shared hook family. An Ability is
   added to the implemented registry only in the same batch that installs its
   real battle behavior.
4. Move work resumes in parallel from the certified CM10 stack. Existing live
   community moves remain untouched; only candidates whose behavior does not
   depend on the 93 held mechanic decisions may graduate.

The locked MR07 Summary/editor visuals remain untouched throughout this work.
