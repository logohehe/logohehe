---
name: windows-input-automation
description: Automate and remotely drive a Windows desktop by controlling mouse and keyboard through deterministic action plans or a local control agent API. Use when an AI agent must continuously click, type, use shortcuts, capture screenshots, and navigate GUI workflows in an interactive Windows session.
---

# Windows Input Automation

## Overview

Use this skill for two modes:
- One-shot execution with JSON plans (`scripts/run_actions.py`)
- Continuous control with a local desktop agent API (`scripts/desktop_agent.py`)

## Workflow

1. Start the desktop agent in the interactive Windows user session.
2. Set a strong token and keep bind address on `127.0.0.1`.
3. Send action plans via `scripts/desktop_client.py`.
4. Capture screenshots between steps to verify UI state.
5. Use `stop` command or move mouse to a screen corner for failsafe abort.

## Execution Rules

- Add short `wait` actions between UI transitions.
- Use absolute coordinates only when the window layout is stable.
- Prefer `hotkey` and `type` over many low-level key events when possible.
- Keep each plan small and task-scoped; split long flows into multiple plans.
- Keep `pyautogui.FAILSAFE` enabled.
- Run agent and target apps on the same desktop session.

## Run Commands

Install dependency:

```powershell
python -m pip install pyautogui
```

Start agent:

```powershell
python scripts/desktop_agent.py --token YOUR_LONG_RANDOM_TOKEN
```

Health check:

```powershell
python scripts/desktop_client.py health --token YOUR_LONG_RANDOM_TOKEN
```

Execute plan through agent:

```powershell
python scripts/desktop_client.py execute --token YOUR_LONG_RANDOM_TOKEN --plan examples/open-notepad-via-agent.json
```

Capture screenshot:

```powershell
python scripts/desktop_client.py capture --token YOUR_LONG_RANDOM_TOKEN --out latest.png
```

Stop agent:

```powershell
python scripts/desktop_client.py stop --token YOUR_LONG_RANDOM_TOKEN
```

## References

- Action schema: `references/action-schema.md`
- Agent API and payloads: `references/desktop-agent-api.md`

