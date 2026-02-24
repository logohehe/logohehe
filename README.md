# Windows Input Automation Skill

Automate Windows desktop operations with mouse and keyboard actions.

This skill provides:
- One-shot action plan runner (`scripts/run_actions.py`)
- Local desktop control agent API (`scripts/desktop_agent.py`)
- Client tool for remote command/screenshot (`scripts/desktop_client.py`)
- Browser DOM control agent for web automation (`scripts/browser_dom_agent.py`)
- Browser DOM client for selector-based web actions (`scripts/browser_dom_client.py`)

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

## Browser DOM Mode (Recommended for Websites)

1. Install browser dependency:

```powershell
python -m pip install playwright
python -m playwright install chromium
```

2. Start browser DOM agent:

```powershell
python scripts/browser_dom_agent.py --token YOUR_TOKEN
```

3. Run DOM plan:

```powershell
python scripts/browser_dom_client.py --token YOUR_TOKEN run --plan examples/github-readme-dom.json
```

## Safety Notes

- Keep `pyautogui.FAILSAFE` enabled (move mouse to screen corner to abort).
- Use a strong token and keep agent bound to `127.0.0.1`.
- Run agent and target app in the same desktop session.
