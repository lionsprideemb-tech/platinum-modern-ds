# DS01 Sprite Duplicate Triage

Status: REVIEW / QUARANTINE ONLY — no sprite asset in this document is installed, deleted, recolored, renamed, or replaced.

Date: 2026-09-28

## Audit scope

The staged DS01 archive contains 11,437 files, including 11,397 PNGs. The integration-ready lane contains 11,365 image files under `hg_engine_ready/data/graphics/sprites/`.

The duplicate audit is intentionally separate from the live Mercury build. Findings below are integration gates, not automatic cleanup actions.

## Confirmed high-priority collisions

These are not merely similar silhouettes. The current audit found identical encoded bytes or identical rendered pixels across entries that are intended to represent different custom concepts.

### BLOCK — unrelated entries share the same complete battle art

The front sheets and back sheets for all four of the following entries are byte-identical within each orientation:

- `darkrai_mega`
- `heatran_mega`
- `slate`
- `zeraora_mega`

This is a hard integration blocker. None of these four should be selected for Mercury until the intended artwork for each concept is recovered or replaced and re-audited.

### BLOCK — custom Mega is the same rendered front sprite as a G-Max form

The following custom Mega candidates currently render pixel-identically to the corresponding G-Max art:

- `toxtricity_mega` ↔ Toxtricity Amped/Low Key G-Max
- `charizard_mega_z` ↔ Charizard G-Max
- `coalossal_mega` ↔ Coalossal G-Max
- `drednaw_mega` ↔ Drednaw G-Max
- `hatterene_mega` ↔ Hatterene G-Max
- `inteleon_mega` ↔ Inteleon G-Max
- `machamp_mega` ↔ Machamp G-Max
- `snorlax_mega` ↔ Snorlax G-Max
- `urshifu_mega` ↔ Urshifu Single-Strike G-Max
- `urshifu_rapid_strike_style_mega` ↔ Urshifu Rapid-Strike G-Max

Treat these as placeholders or duplicated source art, not approved custom-Mega art.

### REVIEW — custom Mega is a palette/recolor of another form

- `lapras_mega` ↔ Lapras G-Max

The geometry/color-pattern topology is the same while the rendered palette differs. This should be visually reviewed before any decision to keep it as a separate Mega design.

## Expected or low-priority duplicate families

Large parts of the raw duplicate count come from legitimate form/gender storage rather than bad custom art. Examples include:

- male/female slots carrying the same art where no sexual dimorphism exists;
- Scatterbug/Spewpa pattern slots sharing battle art;
- Silvally type forms sharing geometry with palette differences;
- Alcremie flavor/sweet variants;
- Pikachu cap variants;
- Minior color forms;
- canonical paired/form assets such as Mega Latias/Mega Latios and antique/phony tea forms.

These should remain in the library unless a later species/form audit finds a concrete problem.

## Near-duplicate manual-review queue

The first perceptual pass also surfaced smaller clusters worth inspection, but these are not automatically classified as duplicates because perceptual hashing can produce false positives on DS sprite sheets.

Highest-value manual checks:

- `butterfree_mega` ↔ Butterfree G-Max
- `kingler_mega` ↔ Kingler G-Max
- `tinkaton_mega` ↔ base Tinkaton
- `arcanine_redux` ↔ Mightyena
- `beedrill_mega_redux` ↔ `reuniclus_redux`
- `cpf_0106_quagsire_alternate_form_1` ↔ `goodra_hisuian_mega`
- `fearow_redux` ↔ `mesprit_redux`

The broad near-duplicate cluster produced by the first dHash pass is treated as noise and is not an integration blocker. The exact-byte, exact-render, and palette-topology findings above are the trustworthy gates.

## Integration policy created by this audit

Before any staged custom sprite is wired into Mercury:

1. exact-byte collision against a different concept must be zero;
2. exact-render collision against an unrelated/custom form must be resolved;
3. palette-only matches to another transformation must be explicitly approved;
4. near-duplicate warnings require visual review rather than automatic rejection;
5. canonical/form-storage duplication is allowed when it accurately represents the source game/form behavior.

No staged sprite receives runtime integration simply because it is present in `hg_engine_ready`.
