#!/usr/bin/env bash
# feat-189 Phase 130 (Task 130.110) runner: all 8 cells (tsk + prb x create
# + update x with/without prompt) x n=3 = 24 runs, SEQUENTIAL (model
# endpoint contention would confound per-run wall clock -- baseline
# convention), 600 s timeout per run, retry-once protocol on non-zero exit
# (incl. timeout, exit 124): the retry runs in a FRESH clean run dir with
# the identical instruction, is labeled <cell>-n<k>-retry, and is the
# formal result; both streams are kept.
#
# Resumability: $EVID/runner-status.tsv carries one line per attempt
# (run-id, exit, duration, seed-uuid, timestamp, tab-separated, appended as
# each attempt finishes). On start, a cell/k is skipped when already
# marked complete: the primary row has exit 0, or a retry row exists.
# A mirrored copy of the status file is kept in the feature evidence
# folder after every attempt -- never let a /tmp-only copy be the only
# copy.
#
# Server surface: every run dir carries a PROJECT opencode.json overriding
# the global config's `specmgr` mcp entry to the WORKTREE server
# (.venv/bin/specmgr mcp), so the runs exercise the feat-189 surface
# (Task 130.100). The server resolves its base dirs CWD-relative; opencode
# spawns it with cwd = the run dir, so all writes land in the run dir.

set -u
WT=/home/user/src/biz.dfch.SpecMgr.worktrees/feat-189-reduce-agent-round-trips
FEAT_EVID=$WT/.specmgr/feat/feat-189-reduce-agent-round-trips/evidence
ROOT=/tmp/opencode/feat189
OC=/home/user/.opencode/bin/opencode
MODEL="vllm-sys0-2/qwen3.8-27b-bf16-896k-mtp-2"
PY=$WT/.venv/bin/python
EVID=$ROOT/evidence
STATUS=$EVID/runner-status.tsv
LOG=$EVID/runner.log
N_RUNS=3
TIMEOUT=600

CELLS="tsk-create-noprompt tsk-create-prompt tsk-update-noprompt tsk-update-prompt prb-create-noprompt prb-create-prompt prb-update-noprompt prb-update-prompt"

mkdir -p "$ROOT/runs" "$EVID" "$FEAT_EVID/runs" "$FEAT_EVID/final-docs"
touch "$STATUS"
if [ ! -s "$STATUS" ]; then
  printf 'run-id\texit\tduration\tseed-uuid\ttimestamp\n' > "$STATUS"
fi
if [ ! -f "$FEAT_EVID/runner-status.tsv" ]; then
  cp "$STATUS" "$FEAT_EVID/runner-status.tsv"
fi

log() { echo "$(date -Is) $*" >> "$LOG"; }

write_project_config() { # $1 = dir
  # Two entries, both project-level (the global config is untouched):
  # 1. mcp.specmgr -> the WORKTREE server (.venv/bin/specmgr mcp), keeping
  #    the server NAME `specmgr` so tool calls keep the specmgr_ prefix
  #    parse_events.py keys on.
  # 2. provider.vllm-sys0-2.models -> registers the pinned model id
  #    qwen3.8-27b-bf16-896k-mtp-2 (the endpoint serves exactly that model;
  #    the global config's map, last updated 2026-10-17, only lists
  #    qwen3.8-27b-bf16-896k, which the endpoint rejects 404 -- and the
  #    opencode binary was upgraded 1.18.35 -> 1.19.3 between preflight
  #    and these runs, 1.19.3 enforcing the static map strictly).
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
  printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$ts" | tee -a "$STATUS" >> "$FEAT_EVID/runner-status.tsv"
}

is_complete() { # $1 = cell-n<k> primary run id; 0 if this cell/k already has a formal result
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

log "runner start: cells x n=$N_RUNS, model=$MODEL, timeout=${TIMEOUT}s, worktree server via per-run-dir opencode.json"
for cell in $CELLS; do
  domain=${cell%%-*}
  for k in $(seq 1 "$N_RUNS"); do
    primary="$cell-n$k"
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
cp "$STATUS" "$FEAT_EVID/runner-status.tsv"
cp "$LOG" "$FEAT_EVID/runner.log"
echo "runner finished; see $FEAT_EVID/runner-status.tsv"
