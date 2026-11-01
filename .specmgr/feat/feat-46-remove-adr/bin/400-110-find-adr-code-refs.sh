#!/usr/bin/env bash
# Checklist / gate for the code-removal phase of feat-46: lists every remaining mention of the
# ADR artifact type outside the places that legitimately keep it (the ADR sources/archive, the
# CHANGELOG history, historical transcripts, this feature folder). Read-only.
#
# Greps (case-insensitive) for: the word ADR, SPECMGR_ADR_DIR, models/adr, specmgr.adr,
# adr_toc / adr-toc, docs/adr. Output is grouped by area; with --gate the script exits 1 when
# anything is left outside the allowed set, so it can close the removal phase.
#
# Run with: bash 400-110-find-adr-code-refs.sh [--gate] [--files]
#   --files  only list the files (one per line) instead of every line

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(git -C "$HERE" rev-parse --show-toplevel)"
cd "$ROOT"

PATTERN='\badr\b|SPECMGR_ADR|models/adr|specmgr\.adr|adr[_-]toc|docs/adr'
EXCLUDE='^(docs/adr/|docs/archive/|\.specmgr/feat/feat-46-remove-adr/|\.specmgr/feat/[^/]+/(session-|history\.md)|CHANGELOG\.md$|docs/api/)'

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
