#!/usr/bin/env bash
# Verifies the converted DEC documents in docs/dec/ against their ADR sources (feat-46).
#
# Per DEC whose id is in adr-manifest.json (a missing DEC is "pending", not a failure, unless
# --require-all): file name == ADR file name; parses via `parse_dec`; frontmatter id/type/
# status/created/updated/version as the manifest says, classification null; the migration
# `## Updates` entry carries the same timestamp as `updated`; FIDELITY -- undoing exactly the
# allowed section transformations (inserted Roles/Source/Related Artifacts/Updates sections,
# the Pros-and-Cons heading rename) of the DEC body reproduces the ADR body with exactly the
# bare <token> wrapping applied (`wrap_bare_tokens`, the `convert()` step) -- including the
# H1, which must equal the wrapped ADR H1 -- after trailing-whitespace and blank-run
# normalisation. Comparing against the wrapped ADR body (rather than unwrapping the spans in
# the DEC text positionally) is required because a positional unwrap is unsound whenever the
# ADR already carries a code span identical to a wrapped run (e.g. 112b6498 with 8 pre-existing
# `get_<d>_schema` spans; feat-46 Phase 120 rule extension); the manifest's wrapped-token list
# must still equal the one re-derived from the ADR body (stale-manifest guard, as in
# `convert()`); supersession -- the superseding DEC lists the older one, the older DEC has
# status `superseded` and no outbound reference to the newer one. Finally `specmgr lint
# --type dec` (full parse of every DEC) unless --no-lint.
#
# Exit codes: 0 all present DECs verified, 1 at least one check failed (or --require-all and
# one is missing), 2 usage error.
#
# Run with: bash 200-120-verify-converted.sh [--adr-dir DIR] [--require-all] [--no-lint]
#   --adr-dir  where the ADR sources live (default docs/adr; use the archive location later)
#   SPECMGR_PYTHON overrides the interpreter (default: uv run --frozen --extra mcp python).
#   The mcp extra is required: parse_dec (the domain __init__ chain reaches server.py, the
#   third-party mcp package) and the embedded `specmgr lint` (needs cli, included by mcp).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$HERE${PYTHONPATH:+:$PYTHONPATH}" PYTHONDONTWRITEBYTECODE=1
read -r -a PY <<< "${SPECMGR_PYTHON:-uv run --frozen --extra mcp python}"

"${PY[@]}" - "$@" <<'PYEOF'
import re, subprocess, sys
from pathlib import Path
import adr_dec_lib as lib

args = sys.argv[1:]
adr_dir, require_all, lint, i = Path("docs/adr"), False, True, 0
while i < len(args):
    if args[i] == "--adr-dir":
        adr_dir = Path(args[i + 1]); i += 1
    elif args[i] == "--require-all":
        require_all = True
    elif args[i] == "--no-lint":
        lint = False
    else:
        lib.die(f"unknown option {args[i]!r}")
    i += 1

root = lib.repo_root()
manifest = lib.load_manifest()
adrs = manifest["adrs"]
failures, present, pending = [], 0, []
texts = {}

for uid, e in adrs.items():
    path = root / "docs" / "dec" / f"{e['stem']}.md"
    if not path.exists():
        pending.append(uid); continue
    present += 1
    problems = []
    text = path.read_text(encoding="utf-8"); texts[uid] = text
    err = lib.parse_error(text)
    if err:
        problems.append(f"parse: {err}")
    fm, body = lib.split_document(text)
    want = {"id": uid, "type": "dec", "status": e["status"], "created": e["created"],
            "updated": e["updated"], "version": "1.0.0", "classification": None}
    for key, val in want.items():
        got = fm.get(key)
        if val is None:
            if got is not None:
                problems.append(f"frontmatter {key}: {got!r} != None (absent/null)")
        elif str(got) != val:
            problems.append(f"frontmatter {key}: {got!r} != {val!r}")
    m = re.search(r"^## Updates\n(?:.*\n)*?### (\S+) - Converted from ADR", body, re.M)
    if not m or m.group(1) != e["updated"]:
        problems.append("migration Updates entry missing or not dated == updated")
    adr_path = root / adr_dir / f"{e['stem']}.md"
    if not adr_path.exists():
        problems.append(f"ADR source missing: {adr_path}")
    else:
        _, adr_body = lib.split_document(adr_path.read_text(encoding="utf-8"))
        wrapped_body, wrapped_list = lib.wrap_bare_tokens(adr_body)
        if wrapped_list != e["wrapped_tokens"]:
            problems.append(f"wrapped tokens differ from the manifest (stale manifest?): {wrapped_list}")
        h1 = lib.title_of(body)
        if h1.strip() != lib.title_of(wrapped_body).strip():
            problems.append(f"title differs: {h1!r}")
        back = lib.unconvert(text, e)
        if lib.normalise(back) != lib.normalise(wrapped_body):
            problems.append("FIDELITY: DEC body minus allowed section transformations != ADR body with the wrapping applied")
    if e["status"] == "superseded" and "## Related Artifacts" in body and f"DEC {e['superseded_by']}" in body:
        problems.append("older DEC must not reference its superseder")
    if problems:
        failures.append((uid, problems))

for uid, e in adrs.items():            # superseder lists the older DEC (when both exist)
    if uid in texts:
        for old in e["supersedes"]:
            if f"- DEC {old}:" not in texts[uid]:
                failures.append((uid, [f"missing Related Artifacts bullet for superseded DEC {old}"]))

for uid, problems in failures:
    print(f"FAIL {uid[:8]}")
    for p in problems:
        print(f"     {p}")
print(f"{present} DEC present, {len(pending)} pending, {len(failures)} failing")
if pending and require_all:
    print(f"--require-all: pending {[p[:8] for p in pending]}"); failures.append(("", ["pending"]))
rc = 1 if failures else 0
if lint and present:
    out = subprocess.run([*sys.executable.split(), "-m", "biz.dfch.specmgr", "lint", "--type", "dec"],
                         capture_output=True, text=True, cwd=root)
    print(out.stdout.strip().splitlines()[-1] if out.stdout.strip() else out.stderr.strip()[:300])
    rc = rc or (1 if out.returncode else 0)
sys.exit(rc)
PYEOF
