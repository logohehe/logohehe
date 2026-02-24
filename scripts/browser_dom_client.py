#!/usr/bin/env python3
"""Client for browser_dom_agent.py."""

import argparse
import json
import pathlib
import urllib.request


def request_json(url, method="GET", body=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read()
        return json.loads(raw.decode("utf-8")) if raw else {}


def main():
    parser = argparse.ArgumentParser(description="Browser DOM agent client")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--token", required=True)
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("health")

    op = sub.add_parser("open")
    op.add_argument("--url", required=True)

    st = sub.add_parser("state")
    st.add_argument("--selectors", nargs="*", default=[])

    rn = sub.add_parser("run")
    rn.add_argument("--plan", required=True)

    sub.add_parser("stop")

    args = parser.parse_args()
    if not args.cmd:
        parser.error("a command is required")

    base = "http://%s:%s" % (args.host, args.port)

    if args.cmd == "health":
        print(json.dumps(request_json(base + "/health"), ensure_ascii=False, indent=2))
        return

    if args.cmd == "open":
        body = {"token": args.token, "url": args.url}
        print(json.dumps(request_json(base + "/open", method="POST", body=body), ensure_ascii=False, indent=2))
        return

    if args.cmd == "state":
        body = {"token": args.token, "selectors": args.selectors}
        print(json.dumps(request_json(base + "/state", method="POST", body=body), ensure_ascii=False, indent=2))
        return

    if args.cmd == "run":
        text = pathlib.Path(args.plan).read_text(encoding="utf-8-sig")
        data = json.loads(text)
        steps = data["steps"] if isinstance(data, dict) else data
        body = {"token": args.token, "steps": steps}
        print(json.dumps(request_json(base + "/run", method="POST", body=body), ensure_ascii=False, indent=2))
        return

    if args.cmd == "stop":
        body = {"token": args.token}
        print(json.dumps(request_json(base + "/stop", method="POST", body=body), ensure_ascii=False, indent=2))
        return


if __name__ == "__main__":
    main()
