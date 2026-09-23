# PT04E Gen VI Save/Reload Runtime Checkpoint — 2026-09-23

## Status

**PASS / SEALED**

The canonical Generation VI upper boundary now survives Platinum's real native save/reset/load path.

## CI proof

- Workflow: `PT04E Gen VI Save Reload Runtime`
- Run number: **1**
- Run ID: **35902713013**
- Commit: `de1623155c4b40ec3d7640dee6c87ab8eea1aa7a`
- Conclusion: **success**
- Artifact: `pt04e-gen6-save-reload-runtime-proof`
- Artifact ID: **10769888502**
- SHA-256: `147d8f52b09c70af03d0c458bb46e6c03f15ebcaa9200893297502ef1f6a2079`

## Primary persistence boundary

- **Volcanion**
- National Dex / native species ID: **721**
- Party slot: **0**
- Level: **50**

## Representative Gen VI party

The native gift-mon path created:

1. Volcanion #721 — upper Gen VI boundary
2. Chespin #650 — first Gen VI species / starter
3. Flabébé #669 — female-only base-species resource path
4. Meowstic #678 — gender/form-sensitive species data
5. Aegislash #681 — form-heavy base resource path
6. Sylveon #700 — Fairy-type representative

The harness then used Platinum's native `FieldSystem_Save`, reset through `RESET_ERROR`, reloaded through `gGameStartLoadSaveAppTemplate -> SaveData_Load`, asserted the party/Pokédex state, and reopened the native Party application.

## Runtime assertions passed

- Party count after reload == 6
- Slot 0 species == `SPECIES_VOLCANION`
- Slot 0 level == 50
- Volcanion seen/caught flags survived reload
- Chespin remained in party
- Flabébé remained in party
- Meowstic remained in party
- Aegislash remained in party
- Sylveon remained in party
- Flabébé caught flag survived reload
- Aegislash caught flag survived reload
- Sylveon caught flag survived reload

## Visual review

The post-reload native Party screen was visually reviewed through frame 4800.

Observed:

- `VOLCANION` Lv.50 — **147/147 HP**
- `CHESPIN` Lv.50 — **124/124 HP**
- `FLABÉBÉ` Lv.50 — **112/112 HP**
- `MEOWSTIC` Lv.50 — **135/135 HP**
- `AEGISLASH` Lv.50 — **121/121 HP**
- `SYLVEON` Lv.50 — **166/166 HP**
- all six party icons rendered,
- gender markers rendered sensibly,
- Party UI remained stable through frame 4800,
- no emulator stop or assertion failure occurred.

## What this proves

PT04E now has native evidence for:

- canonical species registration through #721,
- cumulative Gen V + Gen VI generated resources,
- native party creation at the Gen VI boundary,
- Pokédex capture flags at #721,
- save serialization at #721,
- reset and native load reconstruction at #721,
- and stable native party/icon rendering for representative Gen VI species.

## Next gate

`PT04E_GEN6_VOLCANION_BATTLE_RUNTIME`

Use Volcanion #721 as the player's lead against a low-risk native Bidoof and visually confirm its player-side sprite/name/HP and stable native battle UI.
