#!/usr/bin/env bash
# Checklist / gate for the code-removal phase of feat-46: lists every remaining mention of the
# ADR artifact type outside the places that legitimately keep it (the ADR sources/archive, the
# generated docs/api, the CHANGELOG history, the historical .specmgr/feat documents, the
# committed evals measurement outputs, and the 46 converted DECs whose verbatim body prose the
# fidelity gate forbids rewriting). Read-only.
#
# Greps (case-insensitive) for: the word ADR, SPECMGR_ADR_DIR, models/adr, specmgr.adr,
# adr_toc / adr-toc, docs/adr. Output is grouped by area; with --gate the script exits 1 when
# anything is left outside the allowed set, so it can close the removal phase. The final --gate
# runs at Phase 160.110, after the Phase 150 prose changes have landed (the prose it depends on
# is scheduled there, not in Phase 140).
#
# Run with: bash 400-110-find-adr-code-refs.sh [--gate] [--files]
#   --files  only list the files (one per line) instead of every line
#   SPECMGR_PYTHON overrides the interpreter (default: uv run --frozen python).

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"

PATTERN='\badr\b|SPECMGR_ADR|models/adr|specmgr\.adr|adr[_-]toc|docs/adr'
EXCLUDE='^(docs/adr/|docs/archive/|docs/api/|\.specmgr/feat/|evals/c4-skills/results/|CHANGELOG\.md:'
# The 46 converted DECs keep their verbatim ADR body prose (fidelity gate); exclude exactly
# their manifest stems, not the whole docs/dec/ directory (a future DEC mentioning "adr" must
# still be caught).
if [[ -f "$HERE/../adr-manifest.json" ]]; then
  read -r -a PY <<< "${SPECMGR_PYTHON:-uv run --frozen python}"
  DEC_STEMS="$("${PY[@]}" -c 'import json,sys;print("|".join(m["stem"] for m in json.load(open(sys.argv[1]))["adrs"].values()))' "$HERE/../adr-manifest.json")"
  if [[ -n "$DEC_STEMS" ]]; then
    EXCLUDE+="|docs/dec/(${DEC_STEMS})\.md:"
  fi
fi
EXCLUDE+=")"

hits="$(git grep -n -i -I -E -e "$PATTERN" | grep -v -E -e "$EXCLUDE" || true)"
if [[ -z "$hits" ]]; then
  echo "no remaining ADR mentions outside the allowed set"
  exit 0
fi
if [[ "${1:-}" == "--files" || "${2:-}" == "--files" ]]; then
  cut -d: -f1 <<< "$hits" | sort | uniq -c | sort -rn
else
  awk -F: '{ split($1, p, "/"); area = ($1 ~ /^(src|tests|docs|\.specmgr|\.opencode|\.github)\//) ? p[1] "/" p[2] : "(root)"; n[area]++ }
           END { for (a in n) printf "%6d  %s\n", n[a], a }' <<< "$hits" | sort -rn
  echo "-- $(wc -l <<< "$hits") line(s) in $(cut -d: -f1 <<< "$hits" | sort -u | wc -l) file(s) -- rerun with --files for the file list"
fi
if [[ "${1:-}" == "--gate" || "${2:-}" == "--gate" ]]; then
  exit 1
fi
