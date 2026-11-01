#!/usr/bin/env python3
"""feat-189 Phase 130 (Task 130.100): seed verification helper.

Reads the mcp_probe_wt.py call_tool output (a CallToolResult dump) for
list_<domain> on a seeded run dir from STDIN and exits 0 iff the seed
parses cleanly: total == 1, error_count == 0, the single row carries a
real id/title (no <failed to parse> marker). Prints one verdict line.

Usage: mcp_probe_wt.py call_tool <run-dir> list_<domain> '{}' | seed_verify.py <domain>
"""

from __future__ import annotations

import json
import sys


def main() -> None:
    domain = sys.argv[1]
    dump = json.load(sys.stdin)
    page = json.loads(dump["content"][0]["text"])
    row = page["results"][0]
    title = str(row.get("title", ""))
    ok = (
        page["total"] == 1
        and page["error_count"] == 0
        and bool(row.get("id"))
        and bool(title)
        and "failed to parse" not in title
    )
    verdict = "OK" if ok else "FAIL"
    line = (
        f"seed_verify {domain}: total={page['total']} error_count={page['error_count']} "
        f"id={row.get('id')} title={title!r} -> {verdict}"
    )
    print(line)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
