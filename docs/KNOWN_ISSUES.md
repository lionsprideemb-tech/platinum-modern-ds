# Known Issues

This file distinguishes upstream-known engine gaps from regressions introduced by Platinum Modern DS.

## DS01 certified baseline

HG-Engine automated test suite at the certified DS01 checkpoint:

- 401 tests passed
- 0 unexpected failures
- 8 upstream-known failing tests
- 3 skipped tests

### Upstream-known failing tests

1. Disguise — block damage, Transform
2. Ice Face — block damage, Transform
3. Illusion — breaks in Neutralizing Gas
4. Immunity — heal-on-switch interaction while ability is suppressed
5. Wandering Spirit — swaps abilities when defender faints
6. Eject Pack — Mega Ability interaction during a move
7. Fling — Ripen berry effect (Ripen currently unimplemented in this path)
8. Substitute — Substitute takes damage

### Skipped upstream tests

1. Innards Out — full received-damage return / recoil / faint order
2. Sludge Wave — chain kills in Doubles
3. Sludge Wave — chain kills in Doubles with beginning-of-turn switch

These are part of the inherited HG-Engine baseline and should be audited/fixed through the modern-mechanics workstream. Any newly failing test beyond this baseline is treated as a project regression.
