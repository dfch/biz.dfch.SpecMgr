#!/usr/bin/env bash
# Retags citations of the migrated ADRs to DEC (feat-46): `ADR <uuid>` -> `DEC <uuid>`,
# `ADR <8-hex>` -> `DEC <8-hex>` (unambiguous prefixes only), `docs/adr/<stem>` ->
# `docs/dec/<stem>`. Only ids in adr-manifest.json are touched; foreign ids, ambiguous
# prefixes, "Converted from ADR" provenance lines, the ADR sources, generated files (tier G:
# regenerate them) and the feat-46 folder are never modified.
#
# Dry run by default (per-file counts). With --apply it rewrites the files host-native
# (bytes otherwise unchanged, frontmatter `updated` NOT bumped -- a retag is not an edit).
# Run it only AFTER 200-120-verify-converted.sh --require-all is green, otherwise the new
# `DEC <uuid>` citations do not resolve yet.
#
# Run with: bash 300-120-retag-refs.sh [--tiers ABC] [--apply]
#   default tiers A,B,C; D (historical transcripts) only when asked for explicitly.
#   SPECMGR_PYTHON overrides the interpreter (default: uv run --frozen python).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$HERE${PYTHONPATH:+:$PYTHONPATH}" PYTHONDONTWRITEBYTECODE=1
read -r -a PY <<< "${SPECMGR_PYTHON:-uv run --frozen python}"

"${PY[@]}" - "$@" <<'PYEOF'
import sys
import adr_dec_lib as lib

args, tiers, apply_, i = sys.argv[1:], set("ABC"), False, 0
while i < len(args):
    if args[i] == "--tiers": tiers = set(args[i + 1].upper()); i += 1
    elif args[i] == "--apply": apply_ = True
    else: lib.die(f"unknown option {args[i]!r}")
    i += 1
if "G" in tiers:
    lib.die("tier G (generated files) is never retagged: regenerate them instead")
manifest = lib.load_manifest()
root = lib.repo_root()
total = files = 0
for rel, tier in lib.tracked_text_files():
    if tier not in tiers:
        continue
    path = root / rel
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    new, n = lib.retag_text(text, "ADR", "DEC", manifest)
    if n:
        files += 1; total += n
        print(f"{n:5}  {tier}  {rel}")
        if apply_:
            path.write_bytes(new.encode("utf-8"))
print(f"{total} replacement(s) in {files} file(s) ({'APPLIED' if apply_ else 'dry run'}; tiers {''.join(sorted(tiers))})")
PYEOF
