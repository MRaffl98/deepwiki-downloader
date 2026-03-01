#!/usr/bin/env python3
"""
Health check for deepwiki-downloader.

Verifies that the RSC-based extraction approach still works against a known
DeepWiki repo. Exits with code 1 (causing the CI job to fail and trigger a
GitHub notification) if any step breaks.
"""

import json
import re
import sys
import urllib.parse
import urllib.request

TARGET = "https://deepwiki.com/openai/codex"
PROXY = f"https://api.codetabs.com/v1/proxy?quest={urllib.parse.quote(TARGET)}"

# Known sections that must be present in the output
REQUIRED_SECTIONS = [
    "# Overview",
    "# Installation and Setup",
    "# Architecture Overview",
    "# Sandboxing Implementation",
    "# CI Pipeline",
]

# Fail if total section count drops below this
MIN_SECTIONS = 30


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": "deepwiki-health-check/1.0"}
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_sections(html: str) -> list[str]:
    """Mirror of extractRscSections() in index.html."""
    rsc = ""
    for m in re.finditer(r'self\.__next_f\.push\(\[1,(\".*?\")\]\)', html, re.DOTALL):
        try:
            rsc += json.loads(m.group(1))
        except Exception:
            pass

    sections = []
    for m in re.finditer(r"\w+:T([0-9a-fA-F]+),", rsc):
        length = int(m.group(1), 16)  # lengths are hex
        text = rsc[m.end() : m.end() + length]
        if text.strip().startswith("#"):
            sections.append(text.strip())
    return sections


def check(condition: bool, message: str) -> None:
    if not condition:
        print(f"FAIL: {message}")
        sys.exit(1)


def main() -> None:
    print(f"Fetching: {TARGET}")
    print(f"Via proxy: {PROXY}\n")

    # 1. Proxy reachable
    try:
        html = fetch(PROXY)
    except Exception as e:
        print(f"FAIL: Proxy unreachable — {e}")
        sys.exit(1)

    print(f"Response size: {len(html):,} bytes")

    # 2. RSC marker present (proves DeepWiki still uses Next.js App Router)
    check(
        "__next_f" in html,
        "__next_f not found — DeepWiki may have moved away from Next.js App Router",
    )
    print("OK: __next_f present")

    # 3. RSC stream contains T-type text chunks
    rsc = ""
    for m in re.finditer(r'self\.__next_f\.push\(\[1,(\".*?\")\]\)', html, re.DOTALL):
        try:
            rsc += json.loads(m.group(1))
        except Exception:
            pass

    t_chunks = re.findall(r"\w+:T([0-9a-fA-F]+),", rsc)
    check(
        len(t_chunks) > 0,
        "No T-type chunks found in RSC stream — chunk format may have changed",
    )
    print(f"OK: {len(t_chunks)} T-chunks in RSC stream")

    # 4. Enough markdown sections extracted
    sections = extract_sections(html)
    titles = [s.split("\n")[0] for s in sections]

    print(f"\nExtracted {len(sections)} sections:")
    for t in titles[:5]:
        print(f"  {t}")
    if len(sections) > 5:
        print(f"  ... and {len(sections) - 5} more")

    check(
        len(sections) >= MIN_SECTIONS,
        f"Only {len(sections)} sections extracted (expected >= {MIN_SECTIONS}) "
        f"— RSC structure may have changed",
    )
    print(f"\nOK: Section count ({len(sections)}) >= minimum ({MIN_SECTIONS})")

    # 5. Specific known sections are present
    for required in REQUIRED_SECTIONS:
        check(
            any(s.startswith(required) for s in titles),
            f"Required section missing: {required!r}",
        )
    print(f"OK: All {len(REQUIRED_SECTIONS)} required sections present")

    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
