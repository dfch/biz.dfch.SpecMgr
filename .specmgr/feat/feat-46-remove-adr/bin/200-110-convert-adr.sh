#!/usr/bin/env bash
# Converts ADRs to DEC documents per the "Convert an ADR to a DEC" SOP (feat-46).
#
# For each selected ADR it builds the candidate DEC text from the frozen manifest
# (adr-manifest.json: dates, Source, RASCI mapping, supersession) and runs it through the real
# `parse_dec`. Default is a dry run: it prints one verdict per ADR (and the candidate text when
# exactly one ADR is selected and --show is given). With --write, the candidate is written
# host-native to docs/dec/<uuid>-<slug>.md -- but ONLY if it parses; nothing is ever written
# for a failing candidate, and an existing target file is never overwritten.
#
# Exit codes: 0 every selected ADR converted (or would convert), 1 at least one blocked by
# feat-247 (multi-block Decision Outcome), 2 at least one needs a human judgment / usage error.
#
# Run with: bash 200-110-convert-adr.sh <uuid-or-8hex-prefix>... | --all [--show] [--write]
#   SPECMGR_PYTHON overrides the interpreter (default: uv run --frozen --extra mcp python).
#   The mcp extra is required: the trial conversion imports the real parse_dec, whose dec
#   package __init__ chain reaches server.py (the third-party mcp package).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$HERE${PYTHONPATH:+:$PYTHONPATH}" PYTHONDONTWRITEBYTECODE=1
read -r -a PY <<< "${SPECMGR_PYTHON:-uv run --frozen --extra mcp python}"

"${PY[@]}" - "$@" <<'PYEOF'
import sys
import adr_dec_lib as lib

args = sys.argv[1:]
flags = {a for a in args if a.startswith("--")}
if flags - {"--all", "--show", "--write"}:
    lib.die(f"unknown option(s): {sorted(flags - {'--all', '--show', '--write'})}")
selectors = [a for a in args if not a.startswith("--")]
manifest = lib.load_manifest()
adrs = manifest["adrs"]
if "--all" in flags:
    chosen = list(adrs)
else:
    if not selectors:
        lib.die("give at least one ADR uuid / 8-hex prefix, or --all")
    chosen = []
    for sel in selectors:
        hits = [i for i in adrs if i.startswith(sel)]
        if len(hits) != 1:
            lib.die(f"selector {sel!r} matches {len(hits)} ADRs")
        chosen.append(hits[0])

root = lib.repo_root()
worst = 0
for uid in chosen:
    entry = adrs[uid]
    adr_text = (root / "docs" / "adr" / f"{entry['stem']}.md").read_text(encoding="utf-8")
    dec_text = lib.convert(entry, manifest, adr_text)
    error = lib.parse_error(dec_text)
    cls = lib.classify(error)
    target = root / "docs" / "dec" / f"{entry['stem']}.md"
    verdict = cls
    if cls == "clean" and "--write" in flags:
        if target.exists():
            verdict = "clean (target exists, not overwritten)"
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(dec_text, encoding="utf-8")
            verdict = f"WRITTEN {target.relative_to(root)}"
    print(f"{uid[:8]} {verdict}" + (f"  -- {error}" if error else ""))
    if "--show" in flags and len(chosen) == 1:
        print("-" * 72); print(dec_text); print("-" * 72)
    worst = max(worst, {"clean": 0, "blocked-by-247": 1, "needs-judgment": 2}[cls])
sys.exit(worst)
PYEOF
