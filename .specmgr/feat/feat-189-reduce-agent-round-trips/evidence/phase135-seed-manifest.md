# Phase 135 re-verification seed/instruction manifest (Task 135.110)

**No run launched (2026-10-18)** -- the pinned model
`qwen3.8-27b-bf16-896k-mtp-2` was no longer served by the pinned endpoint
(127.0.0.1:8007; the MTP name 404s, see `preflight-135.txt`), so per the
Phase 135 hard rule the re-verification STOPPED before any attempt. No seed
UUID was consumed; `runner-status-135.tsv` is header-only (zero attempts).

Protocol (unchanged from Phase 130; the runner is
`evidence/harness/run_135.sh`, a minimal delta of `run_all.sh` -- same
project-config shape, same seed/verify/digest/mirror logic, fresh /tmp root
`/tmp/opencode/feat189-135`, run ids `<cell>-135-n<k>`, separate status/log
mirrors so the Phase 130 audit trail stays byte-identical):

- Cells: `prb-create-noprompt` (T1b), `prb-update-prompt` (T3d); n=3 each =
  6 runs, sequential, 600 s timeout, retry-once armed.
- Model pin: `vllm-sys0-2/qwen3.8-27b-bf16-896k-mtp-2` (the Phase 130 pin,
  Deviations D3/D4) -- registered under the host config's `vllm-sys0-2`
  provider by the per-run-dir project `opencode.json` (opencode 1.19.3).
- Server surface: the worktree `.venv/bin/specmgr mcp` via the same
  per-run-dir project override (the FIXED surface -- proven by
  `wire-reproduction-135.txt`, all four non-raw `get_<d>` calls succeed).
- Instructions: IDENTICAL Phase 130 files, sha256-verified at preflight
  against `instruction-hashes.txt` (the runner re-verifies at launch and
  refuses on any deviation):

```text
395ba85f59bbdfe44edb6c9dc88bdc9da006eff11eac7ce4b6fffcb2a9f66cf8  prb-create-noprompt.txt
53ddec39a6f91522524efbd3b642249bef353f9486621a31088bc28cc437d79b  prb-update-prompt.txt
```

- Seeds: content byte-identical to the Phase 130 / feat-128 baseline
  `evidence/seeds/prb_seed.md` (sha256
  `ca37ba5029681a26a9fbe6f7368798389d00e039dda9e5b1e12dd6b8c5df4c92` per
  `seed-manifest.md`); a FRESH UUID per run (frontmatter `id:` rewrite),
  verified parseable through the worktree server before every update run
  (no UUIDs consumed -- no runs).

**Re-launch:** `bash evidence/harness/run_135.sh` once the MTP endpoint is
serving `qwen3.8-27b-bf16-896k-mtp-2` again (resumable via
`runner-status-135.tsv`).
