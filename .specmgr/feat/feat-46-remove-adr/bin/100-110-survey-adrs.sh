#!/usr/bin/env bash
# Surveys every docs/adr/*.md and classifies it for the ADR -> DEC conversion (feat-46).
#
# Per ADR: id, status (+ superseded-by / supersedes), decision-makers mapping, Source value,
# git first/last commit dates (the DEC `created`/`updated`), bare <token> runs to wrap, and the
# result of a trial conversion through the real `parse_dec`:
#   clean            converts and parses
#   blocked-by-247   fails only on the multi-block `## Decision Outcome` (needs feat-247)
#   needs-judgment   any other parse error: stop and decide by hand
#
# Read-only by default (prints the table). With --write it writes adr-manifest.json next to the
# feat README. IMPORTANT: the manifest freezes the git dates -- run --write BEFORE any commit
# touches docs/adr/ (retag, archive). An existing manifest is never overwritten without --force,
# and --force keeps its frozen created/updated values unless --refresh-dates is also given.
#
# Run with: bash 100-110-survey-adrs.sh [--write] [--force] [--refresh-dates]
#   SPECMGR_PYTHON overrides the interpreter (default: uv run --frozen python).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$HERE${PYTHONPATH:+:$PYTHONPATH}" PYTHONDONTWRITEBYTECODE=1
read -r -a PY <<< "${SPECMGR_PYTHON:-uv run --frozen python}"

"${PY[@]}" - "$@" <<'PYEOF'
import json, sys
import adr_dec_lib as lib

args = set(sys.argv[1:])
unknown = args - {"--write", "--force", "--refresh-dates"}
if unknown:
    lib.die(f"unknown option(s): {sorted(unknown)}")

old = json.loads(lib.MANIFEST.read_text()) if lib.MANIFEST.exists() else None
entries = {}
for path in lib.adr_files():
    entry = lib.survey_entry(path)
    if old and not "--refresh-dates" in args and entry["id"] in old["adrs"]:
        entry["created"] = old["adrs"][entry["id"]]["created"]
        entry["updated"] = old["adrs"][entry["id"]]["updated"]
    entries[entry["id"]] = entry
for entry in entries.values():
    if entry["superseded_by"]:
        target = entries.get(entry["superseded_by"])
        if target is None:
            lib.die(f"{entry['id']}: superseded by unknown ADR {entry['superseded_by']}")
        target["supersedes"].append(entry["id"])

manifest = {"adrs": entries}
rows = []
for entry in entries.values():
    text = (lib.repo_root() / "docs" / "adr" / f"{entry['stem']}.md").read_text(encoding="utf-8")
    cls = lib.classify(lib.parse_error(lib.convert(entry, manifest, text)))
    entry["class"] = cls
    rows.append(entry)

counts = {}
for r in rows:
    counts[r["class"]] = counts.get(r["class"], 0) + 1
print(f"{'id':8} {'class':15} {'status':10} {'made-by':22} {'source':18} wrap defaults")
for r in rows:
    print(f"{r['id'][:8]:8} {r['class']:15} {r['status']:10} {str(r['decision_makers'] or '-')[:22]:22} "
          f"{r['source'][:18]:18} {len(r['wrapped_tokens']):4} {','.join(r['defaults']) or '-'}"
          + (f"  superseded-by={r['superseded_by'][:8]}" if r["superseded_by"] else "")
          + (f"  supersedes={[s[:8] for s in r['supersedes']]}" if r["supersedes"] else "")
          + ("  MULTI-ISSUE" if len(r["source_issues"]) > 1 else "")
          + (f"  UNKNOWN-MAKERS={r['unknown_makers']}" if r["unknown_makers"] else ""))
print(f"\n{len(rows)} ADRs: {counts}")

if "--write" in args:
    if lib.MANIFEST.exists() and "--force" not in args:
        lib.die(f"{lib.MANIFEST} exists; use --force (keeps frozen dates) or --force --refresh-dates")
    lib.MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {lib.MANIFEST}")
PYEOF
