# Desktop Agent API

Base URL: `http://127.0.0.1:8765`

Auth model:
- Every request must include JSON field `token`.
- Token must match the one passed to `desktop_agent.py --token`.

Endpoints:

- `GET /health`
  - Returns liveness and timestamp.

- `POST /execute`
  - Body:
    ```json
    {
      "token": "YOUR_TOKEN",
      "default_pause": 0.12,
      "actions": [
        {"type": "click", "x": 969, "y": 1416},
        {"type": "wait", "seconds": 0.4},
        {"type": "type", "text": "notepad"},
        {"type": "key", "key": "enter"}
      ]
    }
    ```
  - Executes actions synchronously and returns:
    ```json
    {"ok": true, "executed": 4}
    ```

- `POST /capture`
  - Body:
    ```json
    {"token": "YOUR_TOKEN"}
    ```
  - Returns PNG screenshot as base64:
    ```json
    {"ok": true, "image_base64": "..."}
    ```

- `POST /stop`
  - Body:
    ```json
    {"token": "YOUR_TOKEN"}
    ```
  - Stops the agent process.

Supported actions:
- `move`, `click`, `double_click`, `drag`, `scroll`
- `type`, `key`, `hotkey`
- `key_down`, `key_up`, `mouse_down`, `mouse_up`
- `wait`
