# Windows Input Automation Skill

Automate Windows desktop operations with mouse and keyboard actions.

This skill provides:
- One-shot action plan runner (`scripts/run_actions.py`)
- Local desktop control agent API (`scripts/desktop_agent.py`)
- Client tool for remote command/screenshot (`scripts/desktop_client.py`)

## Structure

- `SKILL.md`: Skill instructions and workflow
- `agents/openai.yaml`: Skill metadata
- `scripts/`: Execution scripts
- `references/`: Action schema and agent API reference
- `examples/`: Sample action plans

## Quick Start

1. Install dependency:

```powershell
python -m pip install pyautogui
```

2. Start agent in your interactive Windows session:

```powershell
python scripts/desktop_agent.py --token YOUR_TOKEN
```

3. Execute a plan:

```powershell
python scripts/desktop_client.py --token YOUR_TOKEN execute --plan examples/open-notepad-via-agent.json
```

4. Capture screenshot:

```powershell
python scripts/desktop_client.py --token YOUR_TOKEN capture --out latest.png
```

## Safety Notes

- Keep `pyautogui.FAILSAFE` enabled (move mouse to screen corner to abort).
- Use a strong token and keep agent bound to `127.0.0.1`.
- Run agent and target app in the same desktop session.
