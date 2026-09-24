#!/usr/bin/env python3
"""Mercury DS field-route QA runner with automatic wild-battle escape.

Designed for accelerated full-playable smoke testing. It runs deterministic
cardinal routes from a certified savestate, detects when the bottom screen
leaves the normal Platinum field/Poketch presentation, waits out ordinary map
transitions, and escapes wild battles through the touchscreen RUN button.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from desmume.controls import Keys, keymask
from desmume.emulator import DeSmuME

KEYS = {
    "U": Keys.KEY_UP,
    "D": Keys.KEY_DOWN,
    "L": Keys.KEY_LEFT,
    "R": Keys.KEY_RIGHT,
}


def parse_route(spec: str):
    route = []
    for raw in spec.split(","):
        raw = raw.strip().upper()
        if not raw:
            continue
        d = raw[0]
        if d not in KEYS:
            raise ValueError(f"Unknown direction in {raw!r}")
        route.append((d, int(raw[1:])))
    return route


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", required=True, type=Path)
    ap.add_argument("--state", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--label", default="field")
    ap.add_argument("--route", required=True)
    ap.add_argument("--held", type=int, default=10)
    ap.add_argument("--settle", type=int, default=175)
    args = ap.parse_args()

    route = parse_route(args.route)
    args.out.mkdir(parents=True, exist_ok=True)

    emu = DeSmuME()
    emu.open(str(args.rom))
    emu.savestate.load_file(str(args.state))

    frame = 0
    captures = []
    encounters = []

    def run(n: int) -> None:
        nonlocal frame
        for _ in range(n):
            emu.cycle(False)
            frame += 1
            if not emu.is_running():
                raise SystemExit(f"Emulator stopped at frame {frame}")

    def pulse(key, held=None, settle=None) -> None:
        held = args.held if held is None else held
        settle = args.settle if settle is None else settle
        m = keymask(key)
        emu.input.keypad_add_key(m)
        run(held)
        emu.input.keypad_rm_key(m)
        run(settle)

    def tap_run() -> None:
        # Platinum lower-screen RUN button center.
        emu.input.touch_set_pos(128, 160)
        run(16)
        emu.input.touch_release()
        run(800)

    def cap(label: str) -> str:
        name = f"{len(captures):02d}-{label}-{frame:06d}.png"
        emu.screenshot().save(args.out / name)
        captures.append({"stage": label, "frame": frame, "file": name})
        return name

    def lower_stats(img):
        rgb = img.convert("RGB")
        tan = red = total = 0
        # Sample the lower screen on a 4px grid.
        for y in range(196, 382, 4):
            for x in range(4, 252, 4):
                r, g, b = rgb.getpixel((x, y))
                total += 1
                if 120 <= r <= 220 and 100 <= g <= 200 and 45 <= b <= 140 and r > g > b:
                    tan += 1
                if r >= 165 and g <= 115 and b <= 115 and r > g * 1.45:
                    red += 1
        return tan / total, red / total

    def is_overworld(img) -> bool:
        tan_ratio, _ = lower_stats(img)
        return tan_ratio >= 0.35

    def is_fight_menu(img) -> bool:
        _, red_ratio = lower_stats(img)
        return red_ratio >= 0.10

    def recover_field() -> bool:
        img = emu.screenshot()
        if is_overworld(img):
            return False

        # Give ordinary map fades/transitions time to settle before deciding
        # that the field was interrupted by a battle.
        run(700)
        img = emu.screenshot()
        if is_overworld(img):
            return False

        encounter = {
            "start_frame": frame,
            "start_capture": cap(f"encounter-{len(encounters)+1:02d}-start"),
            "run_attempts": 0,
        }

        for _ in range(30):
            img = emu.screenshot()
            if is_overworld(img):
                encounter["end_frame"] = frame
                encounter["end_capture"] = cap(f"encounter-{len(encounters)+1:02d}-cleared")
                encounters.append(encounter)
                return True

            if is_fight_menu(img):
                encounter["run_attempts"] += 1
                tap_run()
            else:
                # Advance battle intro/text/animation toward command selection.
                pulse(Keys.KEY_A, held=12, settle=550)

        encounter["failed_frame"] = frame
        encounter["failed_capture"] = cap(f"encounter-{len(encounters)+1:02d}-failed")
        encounters.append(encounter)
        raise SystemExit("Could not recover to field after detected battle")

    run(240)
    cap(f"{args.label}-start")

    segment_reports = []
    for seg_index, (direction, count) in enumerate(route, start=1):
        key = KEYS[direction]
        before_encounters = len(encounters)
        checkpoints = {count}
        if count >= 8:
            checkpoints.add(count // 2)

        for step in range(1, count + 1):
            pulse(key)
            recover_field()
            if step in checkpoints:
                cap(f"seg{seg_index:02d}-{direction}-{step:02d}")

        state_name = f"{args.label}-seg{seg_index:02d}.dst"
        emu.savestate.save_file(str(args.out / state_name))
        segment_reports.append(
            {
                "segment": seg_index,
                "direction": direction,
                "steps": count,
                "encounters_cleared": len(encounters) - before_encounters,
                "state": state_name,
            }
        )

    run(900)
    recover_field()
    cap(f"{args.label}-stable")
    final_state = args.out / f"{args.label}-final.dst"
    emu.savestate.save_file(str(final_state))

    report = {
        "gate": "MERCURY_QA_FIELD_ROUTE_V1",
        "source_state": args.state.name,
        "route": args.route,
        "segments": segment_reports,
        "wild_encounters": encounters,
        "final_state": final_state.name,
        "captures": captures,
    }
    (args.out / f"{args.label}-meta.json").write_text(json.dumps(report, indent=2) + "\n")
    emu.destroy()


if __name__ == "__main__":
    main()
