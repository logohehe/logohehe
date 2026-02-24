#!/usr/bin/env python3
"""Local browser DOM control agent using Playwright."""

import argparse
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

from playwright.sync_api import sync_playwright


class AgentState:
    def __init__(self, token, browser, context, page):
        self.token = token
        self.browser = browser
        self.context = context
        self.page = page
        self.lock = threading.Lock()
        self.stop_event = threading.Event()


def run_step(page, step):
    kind = step.get("type")
    if not kind:
        raise ValueError("Step missing 'type'")

    if kind == "goto":
        page.goto(step["url"], wait_until="domcontentloaded", timeout=int(step.get("timeout_ms", 30000)))
        return
    if kind == "wait_for":
        page.wait_for_selector(
            step["selector"],
            state=step.get("state", "visible"),
            timeout=int(step.get("timeout_ms", 15000)),
        )
        return
    if kind == "click":
        page.click(step["selector"], timeout=int(step.get("timeout_ms", 15000)))
        return
    if kind == "fill":
        if step.get("clear", True):
            page.fill(step["selector"], "")
        page.fill(step["selector"], step["text"])
        return
    if kind == "type":
        page.type(step["selector"], step["text"], delay=float(step.get("delay_ms", 0)))
        return
    if kind == "press":
        page.keyboard.press(step["keys"])
        return
    if kind == "sleep":
        time.sleep(float(step["seconds"]))
        return
    if kind == "assert_url_contains":
        text = step["text"]
        if text not in page.url:
            raise ValueError("URL assertion failed")
        return
    if kind == "assert_exists":
        count = page.locator(step["selector"]).count()
        if count < 1:
            raise ValueError("Selector assertion failed")
        return

    raise ValueError("Unsupported step type: %s" % kind)


def make_handler(agent):
    class Handler(BaseHTTPRequestHandler):
        def _json_response(self, payload, code=200):
            raw = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _read_json(self):
            n = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(n) if n > 0 else b"{}"
            return json.loads(raw.decode("utf-8"))

        def _auth(self, body):
            return body.get("token") == agent.token

        def do_GET(self):
            if self.path == "/health":
                self._json_response({"ok": True, "status": "running", "url": agent.page.url})
                return
            self._json_response({"ok": False, "error": "not found"}, code=404)

        def do_POST(self):
            try:
                body = self._read_json()
            except Exception as exc:
                self._json_response({"ok": False, "error": "invalid json: %s" % exc}, code=400)
                return

            if not self._auth(body):
                self._json_response({"ok": False, "error": "unauthorized"}, code=401)
                return

            try:
                with agent.lock:
                    if self.path == "/open":
                        agent.page.goto(body["url"], wait_until="domcontentloaded", timeout=30000)
                        self._json_response({"ok": True, "url": agent.page.url, "title": agent.page.title()})
                        return

                    if self.path == "/state":
                        selectors = body.get("selectors", [])
                        elements = []
                        for s in selectors:
                            loc = agent.page.locator(s)
                            count = loc.count()
                            texts = []
                            for i in range(min(count, 3)):
                                t = loc.nth(i).inner_text(timeout=1000) if count else ""
                                texts.append(t[:200])
                            elements.append({"selector": s, "count": count, "texts": texts})
                        self._json_response(
                            {
                                "ok": True,
                                "url": agent.page.url,
                                "title": agent.page.title(),
                                "ready_state": agent.page.evaluate("document.readyState"),
                                "elements": elements,
                            }
                        )
                        return

                    if self.path == "/run":
                        steps = body.get("steps", [])
                        if not isinstance(steps, list):
                            self._json_response({"ok": False, "error": "steps must be list"}, code=400)
                            return
                        for step in steps:
                            run_step(agent.page, step)
                        self._json_response({"ok": True, "executed": len(steps), "url": agent.page.url})
                        return

                    if self.path == "/stop":
                        agent.stop_event.set()
                        self._json_response({"ok": True, "stopping": True})
                        return

                self._json_response({"ok": False, "error": "not found"}, code=404)
            except Exception as exc:
                self._json_response({"ok": False, "error": str(exc)}, code=500)

        def log_message(self, fmt, *args):
            return

    return Handler


def main():
    parser = argparse.ArgumentParser(description="Browser DOM control agent")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--token", required=True)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--browser-path", default="")
    parser.add_argument("--user-data-dir", default="")
    args = parser.parse_args()

    browser_path = args.browser_path
    if not browser_path:
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]
        for c in candidates:
            if os.path.exists(c):
                browser_path = c
                break

    p = sync_playwright().start()
    if args.user_data_dir:
        launch_kwargs = {"headless": args.headless}
        if browser_path:
            launch_kwargs["executable_path"] = browser_path
        context = p.chromium.launch_persistent_context(
            args.user_data_dir, viewport={"width": 1440, "height": 900}, **launch_kwargs
        )
        browser = context.browser
        pages = context.pages
        page = pages[0] if pages else context.new_page()
    else:
        launch_kwargs = {"headless": args.headless}
        if browser_path:
            launch_kwargs["executable_path"] = browser_path
        browser = p.chromium.launch(**launch_kwargs)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()
    page.goto("https://github.com", wait_until="domcontentloaded")

    state = AgentState(args.token, browser, context, page)
    server = HTTPServer((args.host, args.port), make_handler(state))
    print("Browser DOM agent listening on http://%s:%s" % (args.host, args.port))
    try:
        while not state.stop_event.is_set():
            server.handle_request()
    finally:
        server.server_close()
        context.close()
        browser.close()
        p.stop()


if __name__ == "__main__":
    main()
