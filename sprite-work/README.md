# Mercury DS Sprite Audit Workspace

This branch isolates sprite review work from the completed ability pass.

## Source archive
- `staging-assets/community-sprites/2026-09-22/DS01_Expanded_Community_Sprite_Library_2026-09-22.zip`
- Source archive remains staged and untouched.
- Do not bulk-copy the archive into the active engine overlay.

## Audit buckets
Each reviewed sprite should be assigned exactly one status:
- READY — game-ready as-is
- POLISH — strong base; minor cleanup required
- REWORK — concept is usable but needs major sprite work
- REJECT — do not integrate

## Review order
1. Custom Megas
2. New evolutions
3. Delta / regional forms
4. Other special forms
5. Miscellaneous extras

## Integration rule
Only READY or completed POLISH sprites should be mapped into the active DS build, and only after the target species/form identifier exists.

## Current state
No sprite from the staging archive is considered approved merely because it is present in the archive. This workspace is for visual review and explicit approval first.
