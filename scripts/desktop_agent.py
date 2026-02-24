#!/usr/bin/env python3
"""Local desktop control agent for mouse/keyboard automation on Windows."""

import argparse
import base64
import io
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

import pyautogui


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def execute_action(action):
    kind = action.get("type")
    if not kind:
        raise ValueError("Action missing 'type'")

    if kind == "move":
        pyautogui.moveTo(action["x"], action["y"], duration=float(action.get("duration", 0.0)))
    elif kind == "click":
        if "x" in action and "y" in action:
            pyautogui.click(
                x=action["x"],
                y=action["y"],
                clicks=int(action.get("count", 1)),
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
        else:
            pyautogui.click(
                clicks=int(action.get("count", 1)),
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
    elif kind == "double_click":
        if "x" in action and "y" in action:
            pyautogui.doubleClick(
                x=action["x"],
                y=action["y"],
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
        else:
            pyautogui.doubleClick(
                interval=float(action.get("interval", 0.0)),
                button=action.get("button", "left"),
            )
    elif kind == "drag":
        pyautogui.dragTo(
            action["to_x"],
            action["to_y"],
            duration=float(action.get("duration", 0.3)),
            button=action.get("button", "left"),
        )
    elif kind == "scroll":
        pyautogui.scroll(int(action["amount"]))
    elif kind == "type":
        pyautogui.write(action["text"], interval=float(action.get("interval", 0.0)))
    elif kind == "key":
        pyautogui.press(action["key"])
    elif kind == "hotkey":
        keys = action.get("keys", [])
        if not isinstance(keys, list) or not keys:
            raise ValueError("hotkey action requires non-empty 'keys'")
        pyautogui.hotkey(*keys)
    elif kind == "key_down":
        pyautogui.keyDown(action["key"])
    elif kind == "key_up":
        pyautogui.keyUp(action["key"])
    elif kind == "mouse_down":
        pyautogui.mouseDown(button=action.get("button", "left"))
    elif kind == "mouse_up":
        pyautogui.mouseUp(button=action.get("button", "left"))
    elif kind == "wait":
        time.sleep(float(action["seconds"]))
    else:
        raise ValueError(f"Unsupported action type: {kind}")


class DesktopAgentServer:
    def __init__(self, token):
        self.token = token
        self.action_lock = threading.Lock()
        self.stop_event = threading.Event()


def make_handler(agent_state):
    class Handler(BaseHTTPRequestHandler):
        def _json_response(self, payload, code=200):
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _read_json(self):
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            if not raw:
                return {}
            return json.loads(raw.decode("utf-8"))

        def _auth_ok(self, body):
            return body.get("token") == agent_state.token

        def do_GET(self):
            if self.path == "/health":
                self._json_response({"ok": True, "status": "running", "ts": time.time()})
            else:
                self._json_response({"ok": False, "error": "not found"}, code=404)

        def do_POST(self):
            try:
                body = self._read_json()
            except Exception as exc:
                self._json_response({"ok": False, "error": f"invalid json: {exc}"}, code=400)
                return

            if not self._auth_ok(body):
                self._json_response({"ok": False, "error": "unauthorized"}, code=401)
                return

            if self.path == "/execute":
                actions = body.get("actions", [])
                if not isinstance(actions, list):
                    self._json_response({"ok": False, "error": "'actions' must be a list"}, code=400)
                    return
                default_pause = float(body.get("default_pause", 0.10))
                pyautogui.FAILSAFE = True
                pyautogui.PAUSE = default_pause
                try:
                    with agent_state.action_lock:
                        for action in actions:
                            execute_action(action)
                    self._json_response({"ok": True, "executed": len(actions)})
                except Exception as exc:
                    self._json_response({"ok": False, "error": str(exc)}, code=500)
                return

            if self.path == "/capture":
                try:
                    img = pyautogui.screenshot()
                    buff = io.BytesIO()
                    img.save(buff, format="PNG")
                    encoded = base64.b64encode(buff.getvalue()).decode("ascii")
                    self._json_response({"ok": True, "image_base64": encoded})
                except Exception as exc:
                    self._json_response({"ok": False, "error": str(exc)}, code=500)
                return

            if self.path == "/stop":
                agent_state.stop_event.set()
                self._json_response({"ok": True, "stopping": True})
                return

            self._json_response({"ok": False, "error": "not found"}, code=404)

        def log_message(self, fmt, *args):
            return

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Run local desktop control agent")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    state = DesktopAgentServer(args.token)
    handler = make_handler(state)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)

    print(f"Desktop agent listening on http://{args.host}:{args.port}")
    print("Run in the interactive desktop session. Keep this window open.")
    try:
        while not state.stop_event.is_set():
            httpd.handle_request()
    finally:
        httpd.server_close()
        print("Desktop agent stopped")


if __name__ == "__main__":
    main()
