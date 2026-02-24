#!/usr/bin/env python3
"""Client for desktop_agent.py."""

import argparse
import base64
import json
import pathlib
import urllib.error
import urllib.request


def request_json(url, method="GET", body=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Desktop agent client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--token", required=True)

    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("health")

    ex = sub.add_parser("execute")
    ex.add_argument("--plan", help="Path to JSON plan containing {actions:[...]} or an action list")
    ex.add_argument("--json", help="Raw JSON string")
    ex.add_argument("--default-pause", type=float, default=0.10)

    cp = sub.add_parser("capture")
    cp.add_argument("--out", required=True, help="Output PNG path")

    sub.add_parser("stop")

    args = parser.parse_args()
    if not args.cmd:
        parser.error("a command is required")
    base = f"http://{args.host}:{args.port}"

    try:
        if args.cmd == "health":
            payload = request_json(f"{base}/health")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        if args.cmd == "execute":
            if not args.plan and not args.json:
                raise SystemExit("execute requires --plan or --json")
            if args.plan:
                text = pathlib.Path(args.plan).read_text(encoding="utf-8-sig")
            else:
                text = args.json
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                actions = parsed.get("actions")
            elif isinstance(parsed, list):
                actions = parsed
            else:
                raise SystemExit("Plan must be object or list")
            body = {
                "token": args.token,
                "default_pause": args.default_pause,
                "actions": actions,
            }
            payload = request_json(f"{base}/execute", method="POST", body=body)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        if args.cmd == "capture":
            body = {"token": args.token}
            payload = request_json(f"{base}/capture", method="POST", body=body)
            if not payload.get("ok"):
                print(json.dumps(payload, ensure_ascii=False, indent=2))
                return
            data = base64.b64decode(payload["image_base64"])
            pathlib.Path(args.out).write_bytes(data)
            print(f"saved screenshot: {args.out}")
            return

        if args.cmd == "stop":
            body = {"token": args.token}
            payload = request_json(f"{base}/stop", method="POST", body=body)
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return

    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {raw}")
    except Exception as exc:
        print(f"ERROR: {exc}")


if __name__ == "__main__":
    main()
