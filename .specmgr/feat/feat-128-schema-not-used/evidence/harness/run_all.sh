#!/usr/bin/env bash
# feat-128 Phase 100 runner: 8 controlled opencode runs, sequential (model
# endpoint contention would confound per-run wall clock), 600s timeout each.
set -u
ROOT=/tmp/opencode/feat128
OC=/home/user/.opencode/bin/opencode
MODEL="vllm-sys0-mtp-2/qwen3.8-27b-bf16-896k-mtp-2"
LOG=$ROOT/evidence/runner.log
: > "$LOG"

run_one() {
  local run_id="$1"
  local dir="$ROOT/runs/$run_id"
  local instr
  instr=$(cat "$ROOT/evidence/instructions/$run_id.txt")
  local t0 t1 rc
  t0=$(date +%s)
  timeout 600 "$OC" run --dir "$dir" -m "$MODEL" --title "$run_id" --format json "$instr" \
    > "$ROOT/evidence/run-$run_id.json" 2> "$ROOT/evidence/run-$run_id.stderr"
  rc=$?
  t1=$(date +%s)
  echo "$(date -Is) $run_id exit=$rc duration=$((t1-t0))s" >> "$LOG"
}

for run_id in \
  tsk-create-noprompt \
  tsk-create-prompt \
  tsk-update-noprompt \
  tsk-update-prompt \
  prb-create-noprompt \
  prb-create-prompt \
  prb-update-noprompt \
  prb-update-prompt
do
  run_one "$run_id"
done

echo "$(date -Is) ALL DONE" >> "$LOG"
