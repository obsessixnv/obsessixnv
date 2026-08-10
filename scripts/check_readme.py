#!/usr/bin/env python3
"""Fail if anything the README points at is broken.

The failure this exists to catch: github-readme-stats mirrors answer HTTP 200
and serve an SVG that says "Something went wrong! Maximum retries exceeded".
A status-code check passes that with flying colours, so the body is inspected
too. Local asset paths are checked for existence and well-formedness.

Usage:  python3 scripts/check_readme.py [README.md]
"""

from __future__ import annotations

import concurrent.futures
import os
import re
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

# Substrings that mean "this rendered, but it is an error card"
POISON = (
    "something went wrong",
    "maximum retries",
    "deployment_paused",
    "deployment not found",
    "invalid username",
    "user not found",
    "rate limit exceeded",
    "bad credentials",
    "please add an env variable",
    "internal server error",
)

UA = {"User-Agent": "Mozilla/5.0 (readme-health-check)"}
TIMEOUT = 30


def check_remote(url: str) -> tuple[str, str | None]:
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            status = r.status
            body = r.read(200_000)
    except urllib.error.HTTPError as e:
        return url, f"HTTP {e.code}"
    except Exception as e:  # noqa: BLE001 - network errors are all equally fatal here
        return url, f"unreachable: {type(e).__name__}"

    if status != 200:
        return url, f"HTTP {status}"

    text = body.decode("utf-8", "replace").lower()
    for marker in POISON:
        if marker in text:
            return url, f'HTTP 200 but the body says "{marker}"'
    if not body.strip():
        return url, "HTTP 200 but the body is empty"
    return url, None


def main() -> int:
    path = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    src = open(path, encoding="utf-8").read()
    root = os.path.dirname(os.path.abspath(path))

    # srcset matters as much as src: the light-theme variants of every themed
    # image live only there, so omitting it would check half the README and
    # report "all good" while a light asset was missing.
    refs = re.findall(r'(?:src|srcset|href)="([^"]+)"', src)
    refs += re.findall(r'\]\(([^)\s]+)\)', src)

    # Only &amp; is unescaped, deliberately. html.unescape() would expand bare
    # entity-like runs in query strings -- "&center=true" becomes "¢er=true" --
    # whereas HTML attribute parsing leaves those alone, so browsers fetch the
    # URL as written. Undoing more than &amp; invents failures that do not exist.
    remote = sorted({u.replace("&amp;", "&") for u in refs
                     if u.startswith(("http://", "https://"))})
    local = sorted({u for u in refs
                    if not u.startswith(("http://", "https://", "mailto:", "#"))})

    problems: list[str] = []

    for rel in local:
        target = os.path.join(root, rel.split("#")[0])
        if not os.path.exists(target):
            problems.append(f"{rel}\n      missing file")
            continue
        if target.endswith(".svg"):
            try:
                ET.parse(target)
            except ET.ParseError as e:
                problems.append(f"{rel}\n      malformed SVG: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for url, err in pool.map(check_remote, remote):
            if err:
                problems.append(f"{url}\n      {err}")

    print(f"checked {len(local)} local asset(s) and {len(remote)} remote URL(s)")
    if problems:
        print(f"\n{len(problems)} broken reference(s):\n", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1
    print("all good")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
