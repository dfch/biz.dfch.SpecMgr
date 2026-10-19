#!/usr/bin/env bash
# feat-189 Phase 135 (Task 135.110) runner: the two Phase 130 missed cells
# (prb-create-noprompt for T1b, prb-update-prompt for T3d) x n=3 = 6 runs,
# SEQUENTIAL, 600 s timeout per run, retry-once protocol on non-zero exit
# (incl. timeout, exit 124) -- identical protocol to Phase 130's run_all.sh.
#
# This script is a MINIMAL delta of evidence/harness/run_all.sh (the Phase 130
# runner), kept file-for-file identical in every function that touches a run:
# write_project_config (the Phase 130 run-dir project opencode.json shape --
# the worktree .venv/bin/specmgr mcp override of the global `specmgr` entry
# PLUS the vllm-sys0-2 provider registration of the pinned model id, required
# by opencode 1.19.3's strict static models map -- Deviations D3), seed_dir
# (fresh seed UUID per run, frontmatter id: line rewrite), seed_verify
# (list_<domain> through the worktree server before every update run),
# status_row, is_complete, run_one (identical instruction, immediate
# mirroring of the event stream + stderr to the feature evidence folder,
# parse_events.py digest, final-docs copy). The ONLY deltas:
#   - CELLS = the two re-verified cells only (R1: run ONLY prb-create-noprompt
#     and prb-update-prompt);
#   - run ids carry the "-135" infix (<cell>-135-n<k>) so the 6 runs never
#     collide with the Phase 130 run ids in the /tmp root or the status files;
#   - a FRESH /tmp root (/tmp/opencode/feat189-135) so no Phase 130 artifact is
#     touched;
#   - separate status/log mirrors (runner-status-135.tsv / runner-135.log) so
#     the Phase 130 audit trail stays byte-identical.
#
# Instructions: the IDENTICAL Phase 130 files (evidence/instructions/
# prb-create-noprompt.txt / prb-update-prompt.txt -- sha256 verified against
# evidence/instruction-hashes.txt before launch, R1). Seeds: the identical
# Phase 130 content (evidence/seeds/prb_seed.md; fresh UUID per run, R1).
#
# Resumability: $EVID/runner-status.tsv carries one line per attempt; a
# cell/k is skipped when already marked complete (primary exit 0, or a retry
# row exists) -- same contract as run_all.sh.
#
# ENVIRONMENT NOTE (2026-10-18, this phase): the pinned model
# qwen3.8-27b-bf16-896k-mtp-2 was NO LONGER served by the pinned endpoint
# (127.0.0.1:8007 -- it then served qwen3.8-27b-bf16-896k; the MTP name 404s;
# no other local endpoint serves it -- evidence/preflight-135.txt), so no run
# was launched: per the Phase 135 hard rule a down pinned-model endpoint is a
# STOP-and-report. Re-launch this script once the MTP endpoint is back.

set -u
WT=/home/user/src/biz.dfch.SpecMgr.worktrees/feat-189-reduce-agent-round-trips
FEAT_EVID=$WT/.specmgr/feat/feat-189-reduce-agent-round-trips/evidence
ROOT=/tmp/opencode/feat189-135
OC=/home/user/.opencode/bin/opencode
MODEL="vllm-sys0-2/qwen3.8-27b-bf16-896k-mtp-2"
PY=$WT/.venv/bin/python
EVID=$ROOT/evidence
STATUS=$EVID/runner-status.tsv
LOG=$EVID/runner.log
N_RUNS=3
TIMEOUT=600

CELLS="prb-create-noprompt prb-update-prompt"

mkdir -p "$ROOT/runs" "$EVID" "$FEAT_EVID/runs" "$FEAT_EVID/final-docs"
touch "$STATUS"
if [ ! -s "$STATUS" ]; then
  printf 'run-id\texit\tduration\tseed-uuid\ttimestamp\n' > "$STATUS"
fi
if [ ! -f "$FEAT_EVID/runner-status-135.tsv" ]; then
  cp "$STATUS" "$FEAT_EVID/runner-status-135.tsv"
fi

log() { echo "$(date -Is) $*" >> "$LOG"; }

write_project_config() { # $1 = dir
  # Two entries, both project-level (the global config is untouched):
  # 1. mcp.specmgr -> the WORKTREE server (.venv/bin/specmgr mcp), keeping
  #    the server NAME `specmgr` so tool calls keep the specmgr_ prefix
  #    parse_events.py keys on.
  # 2. provider.vllm-sys0-2.models -> registers the pinned model id
  #    qwen3.8-27b-bf16-896k-mtp-2 (opencode 1.19.3 enforces the provider's
  #    static `models` map strictly -- Deviations D3; the global config's map
  #    lists only qwen3.8-27b-bf16-896k).
  sed "s|@WT@|$WT|" > "$1/opencode.json" <<'EOF'
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "vllm-sys0-2": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "vllm (SYS0) 2",
      "options": {
        "baseURL": "http://127.0.0.1:8007/v1"
      },
      "models": {
        "qwen3.8-27b-bf16-896k-mtp-2": {
          "name": "qwen3.8-27b-bf16-896k-mtp-2",
          "limit": {
            "context": 917504,
            "output": 131072
          }
        }
      }
    }
  },
  "mcp": {
    "specmgr": {
      "type": "local",
      "enabled": true,
      "command": ["@WT@/.venv/bin/specmgr", "mcp"]
    }
  }
}
EOF
}

seed_dir() { # $1 = run-dir, $2 = domain; echoes the fresh seed uuid
  local dir="$1" domain="$2" uuid
  mkdir -p "$dir/docs/$domain"
  uuid=$("$PY" -c "import uuid; print(uuid.uuid4())")
  cp "$FEAT_EVID/seeds/${domain}_seed.md" "$dir/docs/$domain/$uuid.md"
  "$PY" - "$dir/docs/$domain/$uuid.md" "$uuid" <<'EOF'
import re
import sys

path, uuid = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
text = re.sub(r"^id: .*$", f"id: {uuid}", text, count=1, flags=re.M)
open(path, "w", encoding="utf-8").write(text)
EOF
  echo "$uuid"
}

seed_verify() { # $1 = run-dir, $2 = domain; 0 iff the seed parses (total 1, error_count 0)
  local dir="$1" domain="$2"
  # mcp_probe_wt.py CLI: <action> <cwd> [args...]  -- cwd FIRST, then the tool name.
  # (No heredoc on the parser: a heredoc would replace the pipe as its stdin.)
  "$PY" "$FEAT_EVID/harness/mcp_probe_wt.py" call_tool "$dir" "list_$domain" "{}" 2>/dev/null \
    | "$PY" "$FEAT_EVID/harness/seed_verify.py" "$domain"
}

status_row() { # $1=run-id $2=exit $3=duration $4=seed-uuid
  local ts
  ts=$(date -Is)
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$ts" | tee -a "$STATUS" >> "$FEAT_EVID/runner-status-135.tsv"
}

is_complete() { # $1 = cell-135-n<k> primary run id; 0 if this cell/k already has a formal result
  local primary="$1"
  grep -q "^${primary}	0	" "$STATUS" && return 0
  grep -q "^${primary}-retry	" "$STATUS" && return 0
  return 1
}

run_one() { # $1 = run-id, $2 = cell (instruction key), $3 = domain
  local run_id="$1" cell="$2" domain="$3"
  local dir="$ROOT/runs/$run_id"
  local seed_uuid="-"
  rm -rf "$dir"
  mkdir -p "$dir"
  write_project_config "$dir"
  if [[ "$cell" == *-update-* ]]; then
    seed_uuid=$(seed_dir "$dir" "$domain")
    if ! seed_verify "$dir" "$domain" >> "$LOG" 2>&1; then
      # environment failure (server could not parse the seed): record an
      # exit-3 row (duration 0) so a resumed session sees the attempt and
      # the retry-once protocol below still applies
      log "$run_id SEED-VERIFY-FAILED (environment; recorded exit=3)"
      status_row "$run_id" 3 0 "$seed_uuid"
      return 3
    fi
  fi
  local instr t0 t1 rc
  instr=$(cat "$FEAT_EVID/instructions/$cell.txt")
  log "$run_id start (seed=$seed_uuid)"
  t0=$(date +%s)
  timeout "$TIMEOUT" "$OC" run --dir "$dir" -m "$MODEL" --title "$run_id" --format json "$instr" \
    > "$EVID/run-$run_id.json" 2> "$EVID/run-$run_id.stderr"
  rc=$?
  t1=$(date +%s)
  # IMMEDIATELY mirror the raw evidence to the feature folder (never a
  # /tmp-only copy), then digest it.
  cp "$EVID/run-$run_id.json" "$FEAT_EVID/runs/$run_id.json"
  cp "$EVID/run-$run_id.stderr" "$FEAT_EVID/runs/$run_id.stderr"
  "$PY" "$FEAT_EVID/harness/parse_events.py" "$run_id" "$EVID/run-$run_id.json" "$dir" "$seed_uuid" \
    > "$FEAT_EVID/runs/$run_id.digest.txt" 2>&1
  # persist the final documents for the all-n-runs audit (baseline
  # final-docs/ convention)
  if [ -d "$dir/docs" ]; then
    mkdir -p "$FEAT_EVID/final-docs/$run_id"
    cp -r "$dir/docs" "$FEAT_EVID/final-docs/$run_id/"
  fi
  status_row "$run_id" "$rc" "$((t1 - t0))" "$seed_uuid"
  log "$run_id exit=$rc duration=$((t1 - t0))s seed=$seed_uuid"
  return "$rc"
}

# Pre-launch instruction identity check (R1): the two instruction files must
# still be byte-identical to the Phase 130 copies recorded in
# evidence/instruction-hashes.txt -- any deviation is a protocol break.
for cell in $CELLS; do
  recorded=$(grep " ${cell}\.txt\$" "$FEAT_EVID/instruction-hashes.txt" | awk '{print $1}')
  actual=$("$PY" -c "import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" "$FEAT_EVID/instructions/$cell.txt")
  if [ "$recorded" != "$actual" ]; then
    echo "INSTRUCTION MISMATCH for $cell: recorded=$recorded actual=$actual -- REFUSING to launch" >&2
    exit 2
  fi
  log "instruction identity OK: $cell sha256=$actual"
done

log "runner start: cells x n=$N_RUNS, model=$MODEL, timeout=${TIMEOUT}s, worktree server via per-run-dir opencode.json (Phase 135 re-verification of the Phase 130 missed cells)"
for cell in $CELLS; do
  domain=${cell%%-*}
  for k in $(seq 1 "$N_RUNS"); do
    primary="$cell-135-n$k"
    if is_complete "$primary"; then
      log "$primary already complete (resumed); skipping"
      continue
    fi
    rc=0
    run_one "$primary" "$cell" "$domain" || rc=$?
    if [ "$rc" -ne 0 ]; then
      retry="$primary-retry"
      if grep -q "^${retry}	" "$STATUS"; then
        log "$retry already present (resumed); skipping"
        continue
      fi
      log "$retry launching (fresh clean dir, identical instruction)"
      run_one "$retry" "$cell" "$domain" || rc=$?
    fi
  done
done
log "ALL DONE"
cp "$STATUS" "$FEAT_EVID/runner-status-135.tsv"
cp "$LOG" "$FEAT_EVID/runner-135.log"
echo "runner finished; see $FEAT_EVID/runner-status-135.tsv"
