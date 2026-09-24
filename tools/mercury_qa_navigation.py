#!/usr/bin/env python3
"""Reusable Mercury DS navigation probe for Platinum-runtime QA.

Loads a DeSmuME savestate, reads the player's Platinum X/Y RAM coordinates,
probes walkability in each cardinal direction, captures screenshots, and writes
machine-readable JSON. This is intentionally development-only tooling.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from desmume.controls import Keys, keymask
from desmume.emulator import DeSmuME

# Pokémon Platinum US player-position addresses used by long-standing DeSmuME
# Lua tooling. Mercury PB01 retains the Platinum field runtime layout.
X_ADDR = 0x021C5CCE
Y_ADDR = 0x021C5CEE

KEYS = {
    "up": Keys.KEY_UP,
    "down": Keys.KEY_DOWN,
    "left": Keys.KEY_LEFT,
    "right": Keys.KEY_RIGHT,
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", required=True, type=Path)
    ap.add_argument("--state", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--label", default="probe")
    ap.add_argument("--probe-steps", type=int, default=12)
    ap.add_argument("--held", type=int, default=10)
    ap.add_argument("--settle", type=int, default=220)
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    emu = DeSmuME()
    emu.open(str(args.rom))

    frame = 0

    def run(n: int) -> None:
        nonlocal frame
        for _ in range(n):
            emu.cycle(False)
            frame += 1
            if not emu.is_running():
                raise SystemExit(f"Emulator stopped at frame {frame}")

    def xy() -> tuple[int, int]:
        return (
            emu.memory.unsigned.read_short(X_ADDR),
            emu.memory.unsigned.read_short(Y_ADDR),
        )

    def pulse(key, held: int | None = None, settle: int | None = None) -> None:
        held = args.held if held is None else held
        settle = args.settle if settle is None else settle
        m = keymask(key)
        emu.input.keypad_add_key(m)
        run(held)
        emu.input.keypad_rm_key(m)
        run(settle)

    def cap(name: str) -> str:
        filename = f"{name}-{frame:06d}.png"
        emu.screenshot().save(args.out / filename)
        return filename

    def load_base() -> tuple[int, int]:
        nonlocal frame
        emu.savestate.load_file(str(args.state))
        frame = 0
        run(120)
        return xy()

    base = load_base()
    base_shot = cap(f"{args.label}-base")

    report = {
        "gate": "MERCURY_QA_NAVIGATION_PROBE_V1",
        "rom": args.rom.name,
        "state": args.state.name,
        "position_addresses": {
            "x": hex(X_ADDR),
            "y": hex(Y_ADDR),
        },
        "base": {"x": base[0], "y": base[1], "screenshot": base_shot},
        "directions": {},
    }

    for direction, key in KEYS.items():
        start = load_base()
        samples = []
        previous = start
        blocked_streak = 0

        for step in range(1, args.probe_steps + 1):
            pulse(key)
            current = xy()
            moved = current != previous
            samples.append(
                {
                    "step": step,
                    "x": current[0],
                    "y": current[1],
                    "moved": moved,
                }
            )
            if moved:
                blocked_streak = 0
            else:
                blocked_streak += 1
            previous = current

            # Two consecutive no-move pulses is enough to call the corridor blocked.
            if blocked_streak >= 2:
                break

        screenshot = cap(f"{args.label}-{direction}")
        state_out = args.out / f"{args.label}-{direction}.dst"
        emu.savestate.save_file(str(state_out))
        report["directions"][direction] = {
            "start": {"x": start[0], "y": start[1]},
            "end": {"x": previous[0], "y": previous[1]},
            "steps_attempted": len(samples),
            "successful_steps": sum(1 for s in samples if s["moved"]),
            "samples": samples,
            "screenshot": screenshot,
            "state": state_out.name,
        }

    (args.out / f"{args.label}-navigation.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    emu.destroy()


if __name__ == "__main__":
    main()
