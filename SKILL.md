---
name: windows-input-automation
description: Automate and remotely drive a Windows desktop by controlling mouse and keyboard through deterministic action plans or a local control agent API. Use when an AI agent must continuously click, type, use shortcuts, capture screenshots, and navigate GUI workflows in an interactive Windows session.
---

# Windows Input Automation

## Overview

Use this skill in three modes:
- Desktop input plans (`scripts/run_actions.py`)
- Desktop input API agent (`scripts/desktop_agent.py` + `scripts/desktop_client.py`)
- Browser DOM agent (`scripts/browser_dom_agent.py` + `scripts/browser_dom_client.py`)

## Workflow

1. Choose control mode:
   - Use Browser DOM agent for web tasks (preferred).
   - Use desktop input only when DOM control is not possible.
2. Start the selected agent in the interactive Windows user session.
3. Set a strong token and keep bind address on `127.0.0.1`.
4. Execute small, verifiable steps.
5. Stop on state mismatch and re-check context before continuing.

## Execution Rules

- Add short `wait` actions between UI transitions.
- Use absolute coordinates only as fallback.
- Prefer `hotkey` and `type` over many low-level key events when possible.
- Keep each plan small and task-scoped; split long flows into multiple plans.
- Keep `pyautogui.FAILSAFE` enabled.
- Run agent and target apps on the same desktop session.
- For web pages, prefer selectors and URL/state checks over visual clicks.

## Run Commands

Install dependency:

```powershell
python -m pip install pyautogui
python -m pip install playwright
python -m playwright install chromium
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

Start browser DOM agent:

```powershell
python scripts/browser_dom_agent.py --token YOUR_LONG_RANDOM_TOKEN
```

Browser health:

```powershell
python scripts/browser_dom_client.py health --token YOUR_LONG_RANDOM_TOKEN
```

Open URL in DOM agent:

```powershell
python scripts/browser_dom_client.py open --token YOUR_LONG_RANDOM_TOKEN --url "https://github.com/logohehe/logohehe"
```

Run DOM plan:

```powershell
python scripts/browser_dom_client.py run --token YOUR_LONG_RANDOM_TOKEN --plan examples/github-readme-dom.json
```

## References

- Action schema: `references/action-schema.md`
- Agent API and payloads: `references/desktop-agent-api.md`
- Browser DOM API and plan schema: `references/browser-dom-agent-api.md`

