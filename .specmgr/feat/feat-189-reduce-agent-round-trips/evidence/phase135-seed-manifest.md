# Phase 135 re-verification seed/instruction manifest (Task 135.110)

**Executed 2026-10-19** (the 2026-10-18 attempt was blocked by the renamed
pinned model -- see `preflight-135.txt`; the operator ruled the model is
the SAME model on the SAME port, now served as `qwen3.8-27b-bf16-896k` --
`preflight-135b.txt`, deviation D7 in `round-trip-rerun.md`).

6 formal runs (2 cells x n=3), sequential, 600 s timeout, retry-once armed
but never triggered (all exit 0), fresh /tmp root
`/tmp/opencode/feat189-135`, runner `evidence/harness/run_135.sh` (a
minimal delta of the Phase 130 `run_all.sh` -- same project-config shape
per D3 with the model id updated per D7, same seed/verify/digest/mirror
logic, run ids `<cell>-135-n<k>`, separate status/log mirrors):

- Model string (every run): `vllm-sys0-2/qwen3.8-27b-bf16-896k` (endpoint
  127.0.0.1:8007, opencode 1.19.3).
- Instructions: IDENTICAL Phase 130 files, sha256-verified by the runner's
  own pre-launch guard against `instruction-hashes.txt` before the first
  run:

```text
395ba85f59bbdfe44edb6c9dc88bdc9da006eff11eac7ce4b6fffcb2a9f66cf8  prb-create-noprompt.txt
53ddec39a6f91522524efbd3b642249bef353f9486621a31088bc28cc437d79b  prb-update-prompt.txt
```

- Seeds: content byte-identical to the Phase 130 / feat-128 baseline
  `evidence/seeds/prb_seed.md` (sha256
  `ca37ba5029681a26a9fbe6f7368798389d00e039dda9e5b1e12dd6b8c5df4c92` per
  `seed-manifest.md`); a FRESH UUID per update run (frontmatter `id:`
  rewrite); each verified parseable through the worktree server
  (`list_prb`: total=1, error_count=0, real title) before launch. The
  create cells carry `-`.

Per-run seed UUIDs (from `runner-status-135.tsv`):

| run-id | seed-uuid |
| --- | --- |
| prb-create-noprompt-135-n1 | - |
| prb-create-noprompt-135-n2 | - |
| prb-create-noprompt-135-n3 | - |
| prb-update-prompt-135-n1 | 719ea9d8-e841-4ec1-9754-f0014d09373c |
| prb-update-prompt-135-n2 | 1a6f46ca-c20f-44be-9a58-8a75505df4b0 |
| prb-update-prompt-135-n3 | e9be94a5-01db-40b4-9240-317ec1fd1700 |

Outcome: T1b HOLDS in all 3 runs (4/4/4 calls, first-try `create_prb` 3/3,
0 validation-failure retries, 0 schema fetches) and T3d HOLDS in all 3
runs (4/4/5 calls, 0 schema fetches, 0 closed-form validation failures) --
see `round-trip-rerun.md` "Phase 135 re-verification".
