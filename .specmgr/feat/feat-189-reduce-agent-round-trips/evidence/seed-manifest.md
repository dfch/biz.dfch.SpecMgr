# Seed manifest -- feat-189 Phase 130 re-run

Seed CONTENT is byte-identical to the feat-128 Phase 100 baseline seeds
(`.specmgr/feat/feat-128-schema-not-used/evidence/seeds/`):

```text
ca37ba5029681a26a9fbe6f7368798389d00e039dda9e5b1e12dd6b8c5df4c92  prb_seed.md
8edd1e0d170cf41aa6d651118110e6918947ce0b3c596d5e12fb5026dce2174c  tsk_seed.md
```

Per the harness convention (feat-128 Decisions Made, item 5), each run got a
FRESH UUID: the runner rewrote the frontmatter `id:` line and wrote
`<run-dir>/docs/<domain>/<uuid>.md` before the run; the agent was never told
the path or id. Each seed was verified parseable through the WORKTREE server
(`mcp_probe_wt.py call_tool <run-dir> list_<domain> '{}' | seed_verify.py`:
`total=1`, `error_count=0`, real title) before launch.

Per-run seed UUIDs (from `runner-status.tsv`, column `seed-uuid`; the
create cells carry `-`):

| run-id | seed-uuid |
| --- | --- |
| tsk-update-noprompt-n1 | 70a358d9-7d79-4466-a254-28993d43c9cf |
| tsk-update-noprompt-n2 | 9a4493fb-527a-402d-a2c9-37c6c30582b7 |
| tsk-update-noprompt-n3 | 34d1d50e-0d33-4f9a-8b09-77fb29a8af8d |
| tsk-update-prompt-n1 | 83911645-7c98-4dc2-b77a-754dc1bbb7c3 |
| tsk-update-prompt-n2 | 055fb043-f8d9-461f-a66f-ca91f60c851a |
| tsk-update-prompt-n3 | dd96de9d-5138-47e7-96d6-374a524bb69c |
| prb-update-noprompt-n1 | eb2fa65b-9ab1-4478-9977-b4f99e083a14 |
| prb-update-noprompt-n2 | ef5d1a24-5581-404a-a4ec-019eb63fbba9 |
| prb-update-noprompt-n3 | 40bae7ec-1fe6-48dc-ab74-f8d112529edf |
| prb-update-prompt-n1 | 7b038823-317e-48b8-b67e-9b4244c5af26 |
| prb-update-prompt-n2 | 3ff82e63-e3b6-4a8f-b928-090c6d2c50d1 |
| prb-update-prompt-n3 | 7be8eccd-790c-471d-b7da-c7f71fa40e3d |
