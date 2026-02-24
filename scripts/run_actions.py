#!/usr/bin/env python3
"""Execute deterministic mouse/keyboard action plans on Windows."""

import argparse
import json
import time
from pathlib import Path


def load_plan(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as f:
        plan = json.load(f)
    if not isinstance(plan, dict) or "actions" not in plan:
        raise ValueError("Plan must be an object with an 'actions' array")
    if not isinstance(plan["actions"], list):
        raise ValueError("'actions' must be an array")
    return plan


def execute_action(pg, action: dict, dry_run: bool) -> None:
    kind = action.get("type")
    if not kind:
        raise ValueError("Action missing 'type'")

    if dry_run:
        print(f"[dry-run] {action}")
        return

    if kind == "move":
        pg.moveTo(action["x"], action["y"], duration=float(action.get("duration", 0.0)))
    elif kind == "click":
        if "x" in action and "y" in action:
            pg.click(
                x=action["x"],
                y=action["y"],
                clicks=int(action.get("count", 1)),
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
        else:
            pg.click(
                clicks=int(action.get("count", 1)),
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
    elif kind == "double_click":
        if "x" in action and "y" in action:
            pg.doubleClick(
                x=action["x"],
                y=action["y"],
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
        else:
            pg.doubleClick(
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
    elif kind == "drag":
        pg.dragTo(
            action["to_x"],
            action["to_y"],
            duration=float(action.get("duration", 0.3)),
            button=action.get("button", "left"),
        )
    elif kind == "scroll":
        pg.scroll(int(action["amount"]))
    elif kind == "type":
        pg.write(action["text"], interval=float(action.get("interval", 0.0)))
    elif kind == "key":
        pg.press(action["key"])
    elif kind == "hotkey":
        keys = action.get("keys", [])
        if not isinstance(keys, list) or not keys:
            raise ValueError("hotkey action requires non-empty 'keys' array")
        pg.hotkey(*keys)
    elif kind == "wait":
        time.sleep(float(action["seconds"]))
    else:
        raise ValueError(f"Unsupported action type: {kind}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mouse/keyboard plan")
    parser.add_argument("--plan", required=True, help="Path to plan JSON")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without sending input")
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="Global speed factor (>1 slower, <1 faster). Applied to pauses and durations.",
    )
    args = parser.parse_args()

    if args.speed <= 0:
        raise ValueError("--speed must be > 0")

    plan = load_plan(Path(args.plan))
    start_delay = float(plan.get("start_delay", 2.0)) * args.speed
    default_pause = float(plan.get("default_pause", 0.15)) * args.speed

    print(f"Loaded {len(plan['actions'])} actions from {args.plan}")
    print(f"start_delay={start_delay:.2f}s, default_pause={default_pause:.2f}s, dry_run={args.dry_run}")

    if args.dry_run:
        for action in plan["actions"]:
            execute_action(None, action, dry_run=True)
        print("Dry run complete")
        return 0

    import pyautogui as pg

    pg.FAILSAFE = True
    pg.PAUSE = default_pause

    print("Execution starts now. Move mouse to a screen corner to abort (FAILSAFE).")
    time.sleep(start_delay)

    for i, action in enumerate(plan["actions"], start=1):
        adjusted = dict(action)
        if "duration" in adjusted:
            adjusted["duration"] = float(adjusted["duration"]) * args.speed
        if "interval" in adjusted:
            adjusted["interval"] = float(adjusted["interval"]) * args.speed
        if adjusted.get("type") == "wait" and "seconds" in adjusted:
            adjusted["seconds"] = float(adjusted["seconds"]) * args.speed
        print(f"[{i}/{len(plan['actions'])}] {adjusted.get('type')}")
        execute_action(pg, adjusted, dry_run=False)

    print("Execution complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

