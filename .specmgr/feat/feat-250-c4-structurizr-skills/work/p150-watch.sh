#!/usr/bin/env bash
# 60s window watcher: append vLLM running/waiting samples (ephemeral forensics)
while true; do
  ts=$(date -u +%H:%M:%SZ)
  sample=$(curl -s --max-time 10 http://127.0.0.1:8081/metrics | grep -E '^vllm:num_requests_(running|waiting)\{' | sed -E 's/.*num_requests_(running|waiting)\{[^}]*\} ([0-9.]+)/\1=\2/' | tr '\n' ' ')
  echo "${ts} ${sample}" >> /tmp/opencode/feat250-p150/window.log
  sleep 60
done
