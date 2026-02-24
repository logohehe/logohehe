# Action Plan Schema

A plan is a JSON file with this shape:

```json
{
  "start_delay": 2.0,
  "default_pause": 0.15,
  "actions": [
    {"type": "move", "x": 500, "y": 420, "duration": 0.2},
    {"type": "click", "button": "left", "count": 1},
    {"type": "type", "text": "hello world"},
    {"type": "hotkey", "keys": ["ctrl", "s"]},
    {"type": "wait", "seconds": 1.0}
  ]
}
```

Supported action types:

- `move`: move pointer. Fields: `x` (int), `y` (int), optional `duration` (float).
- `click`: mouse click. Optional fields: `x`, `y`, `button` (`left|right|middle`), `count` (int), `interval` (float).
- `double_click`: same optional fields as click.
- `drag`: drag pointer. Fields: `to_x` (int), `to_y` (int), optional `button`, `duration`.
- `scroll`: wheel scroll. Field: `amount` (int).
- `type`: type text. Fields: `text` (string), optional `interval` (float).
- `key`: press one key. Field: `key` (string).
- `hotkey`: key combo. Field: `keys` (array of strings).
- `wait`: pause execution. Field: `seconds` (float).

Notes:

- `start_delay` gives time to focus the target app before execution starts.
- `default_pause` applies between actions.
- Coordinates are screen coordinates in pixels.
- Keep plans short and deterministic; split long workflows into multiple plans.

