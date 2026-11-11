#!/usr/bin/env bash
# Finds every citation of the migrated ADRs in tracked files (feat-46). Read-only.
#
# Three shapes: `<TAG> <full uuid>`, `<TAG> <8-hex prefix>` (mapped to an ADR through the
# manifest; a prefix matching several ADRs is reported `ambiguous`), and `docs/adr/<stem>[.md]`
# paths. A uuid/prefix that is not a migrated ADR is `foreign` and never touched; lines saying
# "Converted from ADR" are `keep`; a bare `docs/adr/...` path is `manual`.
# Tiers: G generated, A live artifacts, B src+tests, C prose, D transcripts/sibling files;
# the ADR sources (`docs/adr/*.md` pre-move, the frozen `docs/archive/` after Phase 150) and
# this feature folder are excluded.
#
# Run with: bash 300-110-find-refs.sh [--tags REGEX] [--tiers ABCDG] [--list] [--status S]
#   --tags    citation tag to look for (default ADR; e.g. 'ADR|DEC' to see both)
#   --list    print every hit as file:line  kind  status  text   (default: summary table)
#   --status  only hits with this status (retag|foreign|ambiguous|keep|manual)
#   SPECMGR_PYTHON overrides the interpreter (default: uv run --frozen python).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$HERE${PYTHONPATH:+:$PYTHONPATH}" PYTHONDONTWRITEBYTECODE=1
read -r -a PY <<< "${SPECMGR_PYTHON:-uv run --frozen python}"

"${PY[@]}" - "$@" <<'PYEOF'
import collections, sys
import adr_dec_lib as lib

args, tag, tiers, show, status, i = sys.argv[1:], "ADR", set("ABCDG"), False, None, 0
while i < len(args):
    if args[i] == "--tags": tag = args[i + 1]; i += 1
    elif args[i] == "--tiers": tiers = set(args[i + 1].upper()); i += 1
    elif args[i] == "--status": status = args[i + 1]; i += 1
    elif args[i] == "--list": show = True
    else: lib.die(f"unknown option {args[i]!r}")
    i += 1
manifest = lib.load_manifest()
table = collections.Counter()
for hit in lib.scan_refs(tag, manifest, tiers):
    if status and hit["status"] != status:
        continue
    table[(hit["tier"], hit["kind"], hit["status"])] += 1
    if show:
        print(f"{hit['file']}:{hit['line']}\t{hit['kind']}\t{hit['status']}\t{hit['text']}")
if not show:
    print(f"{'tier':4} {'kind':6} {'status':10} count")
    for (t, k, s), n in sorted(table.items()):
        print(f"{t:4} {k:6} {s:10} {n}")
    print(f"total {sum(table.values())}   (tiers: " + ", ".join(f"{k}={v}" for k, v in lib.TIERS.items()) + ")")
PYEOF
