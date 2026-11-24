# Phase 150 held-out — launch/status note

Status at 2026-11-19 (this file is finalized at the end of the session;
it exists so no session knowledge lives only in a transcript).

SUPERSEDED for the sys1 run by `phase-150-heldout-resume-prompt.md`'s 'sys1 adaptations' section (2026-11-21) and the README's 2026-11-21/2026-11-22 entries: the held-out ran on sys1 with 0 cache hits / 15 fresh trials (`p150-heldout-2026-11-22T064104Z`, clean acceptance); this file's 10-hit/5-fresh expectations are sys0-only history.

## What this note is for

Task 150.140 (the held-out `heldout-review` campaign) plus the
bookkeeping half of Task 150.150, resumed from the context-exhausted
2026-11-18 session. The stop rule already PASSED on 2026-11-17 (iteration
1 of 3, variant v2 `89e0bc4b…fc0`); this session only runs the held-out
campaign and the bookkeeping. Nothing here changes the frozen variant or
the stop-rule verdict.

## State taken over (orchestrator-verified 2026-11-19)

- HEAD `e160b692` (Phase 140 complete), branch `feat-250-c4-structurizr-skills`.
- Frozen skill variant **v2**: `.opencode/skill/c4-model-review/` (6
  markdown files), content hash
  `89e0bc4bb4867b8885a3e393eaf1c76d3811dd39bd17702a533788f0b7620fc0`
  (re-verified from disk via `c4_skills.pins.skill_variant_hash` over the
  sorted `(relpath, sha256)` file pairs).
- Grader hash `b4ae81afcc4ae8e5c0484e480a6dc18ea1c9bf0b75e458c5a3c5d90a4ee8f81b`
  and version tuple hash
  `f22635f6ba9bee3354bb487b5f26753260293fbd8a3394a778f398b507103662`
  (both re-verified; they equal the keys stored in the result cache for
  `heldout-review.none` / `heldout-review.upstream`, so a rerun gets 10
  cache hits).
- Stop-rule evidence: `p150-prove-2026-11-17T165125Z` (seed 916537;
  `none` 0/15 AND `upstream` 0/15) + `p150-iter1-2026-11-17T202412Z`
  (seed 947052; `skill` 2/10 with two full 9/9 passes on `review-model`,
  `skill_margins.margin.ok: true`).

## The 2026-11-18 abort (cycle 1 of the bounded-wait policy)

The context-exhausted session launched the held-out campaign on
2026-11-18 15:43:47Z (run `p150-heldout-2026-11-18T154347Z`, seed 16627).
It resolved 7 of 15 trials (5 cache hits + 2 fresh skill trials:
`skill-k2` PASS 9/9 at 678 s contended, `skill-k4` FAIL at the 1200 s
timeout) and then aborted: "vLLM was still busy after 3601s of waiting
(last seen 3 running request(s)); refusing to start a trial that is
guaranteed to be contended". No `run.json` — a partial. Forensics of that
partial (all trial JSONs + events + preflights + logs + the 2026-11-18
probe `probe-probe-2026-11-18T154019Z` + the 11-18 window samples) were
copied to this folder's `work/` (subfolders
`p150-heldout-abort1-2026-11-18T154347Z/`,
`probe-2026-11-18T154019Z/`, files `p150-heldout.log`,
`preflight-heldout.json`, `window.log`) and the partial results dir was
swept per the bounded-wait policy.

Note: the 11-18 fresh skill trials are NOT cacheable (`skill` is never
cached by design — `c4_skills/cache.py`), so they do not carry over into
the 11-19 rerun; they are forensic history only.

## The 2026-11-19 launch (cycle 2)

- Window at launch (2026-11-19 ~06:45Z): `running=3.0 waiting=0`
  sustained since the 11-18 window watcher's last samples; the user
  reported the shared vLLM "idle", the orchestrator's last check showed
  `running=3.0` (external load) — the runner's own idle check is
  authoritative.
- `run.py preflight`: ok=True (no PIN violation), recorded
  `vllm_idle: false, running: 3` (copy: `work/preflight-2026-11-19.json`).
- Probe: NOT re-run fresh — recorded busy-skip. The chain was verified
  under the identical version tuple by (a) the 2026-11-18 15:40Z probe
  (`probe-probe-2026-11-18T154019Z`, exit 0, `PROBE-OK`, preflight
  ok=True) and (b) the 2026-11-18 abort run completing two fresh skill
  trials through the full container/sidecar/vLLM/MCP chain. A fresh
  probe would have consumed the same 1-h idle budget the campaign needs.
- Campaign command (identical to the 11-18 one, fresh random seed as
  designed — the seed only shuffles trial order; sampling is
  `temperature=0.0`):
  `setsid nohup uv run --frozen python evals/c4-skills/run.py run --cases heldout-review --conditions none,upstream,skill --comparison upstream --k 5 --skills-dir .opencode/skill/c4-model-review --label p150-heldout > .specmgr/feat/feat-250-c4-structurizr-skills/work/p150-heldout-rerun.log 2>&1 &`
- Run: `p150-heldout-2026-11-19T070020Z`, seed **71620**, k=5,
  timeout 1200 s. Plan order (computed from `runner.plan_trials`):
  none-k3, upstream-k2, upstream-k4, none-k0, none-k4 (5 cache hits),
  skill-k0, skill-k2, upstream-k3 (hit), skill-k4, none-k1 (hit),
  skill-k1, none-k2 (hit), upstream-k1 (hit), skill-k3, upstream-k0
  (hit).

## Outcome (final — 2026-11-19 09:35Z): bounded-wait exhausted, held-out PENDING

The 2026-11-19 campaign **aborted after cycle 2** of the bounded-wait
policy — the shared vLLM never offered a second idle slot:

- 05 cache hits resolved at launch (none-k0/k3/k4, upstream-k2/k4; all
  `cache_reason: hit`, originals from `p150-prove-2026-11-17T115537Z`),
  then `skill-k0` started at 07:59:12Z (after a 3529.1 s idle-wait that
  used nearly the whole 3600 s budget on the pre-trial wait) and
  **completed at 08:13:21Z: 598.6 s, contended=true, no timeout,
  8/9 gates — the only failure is `no_false_findings`** (a finding line
  names the clean, correctly `External`-tagged element
  'Loyalty Points Feed'; every detection gate passed).
- The next fresh trial (`skill-k2`, plan slot 6) then idle-waited the
  full budget and aborted the run at 09:13:44Z: "vLLM was still busy
  after 3604s of waiting (last seen 3 running request(s)); refusing to
  start a trial that is guaranteed to be contended". No `run.json`, no
  `report.json` — a partial, kept as history (forensics copied to
  `work/p150-heldout-abort2-2026-11-19T070020Z/`, log at
  `work/p150-heldout-attempt2.log`); sidecar + network torn down
  cleanly.
- Per the bounded-wait policy this is the **second and final abort
  cycle** — the campaign effort STOPS here (no third loop). The
  remaining 9 trials (4 fresh skill: k2/k4/k1/k3; 5 cache hits) never
  ran. The pre-verified fact that all 10 `none`/`upstream` trials are
  cache hits under the current pins (cache keys + k indices verified
  against `evals/c4-skills/cache/heldout-review.{none,upstream}.json`)
  is unchanged; only the 5 fresh `skill` measurements are missing.
- Window evidence (60 s watcher; both sessions' samples in
  `work/window.log`): 11-18 13:52–15:35Z: 20 samples, 15 busy / 5
  idle; 11-19 06:53–09:33Z: 144 parsed samples, **144 busy / 0 idle**
  (median `running=3.0`, range 1.0–4.0 — a sustained external client,
  the host's own trials included only in the 07:59–08:13 window). The
  single 11-19 drain (07:56–08:01Z, 3 watcher samples unparseable —
  the metrics endpoint was unresponsive during the drain) is exactly
  when `skill-k0` ran.
- State left: **bookkeeping complete, held-out pending** — Task
  150.140 remains unticked (no completed campaign run), Task 150.150's
  three sub-parts (attribution check, pinning test, bundle regeneration)
  are done (see below). Nothing changes the frozen variant (v2
  `89e0bc4b…fc0`) or the stop-rule verdict (PASS at iteration 1,
  2026-11-17). A future session with a healthy window resumes via the
  re-run checklist above; the hybrid rule (≥1/5 full passes ⇒ clean
  acceptance; 0/5 or below `none` ⇒ accepted with caveat, rechecked in
  Phase 160) applies to that run's 5 fresh skill trials. The one
  completed skill trial here (k0: 8/9, `no_false_findings` fail) is
  forensics only — it belongs to an aborted run and is never part of a
  held-out verdict.

## If the held-out ever has to be re-run

1. Preconditions: pins unchanged (variant hash `89e0bc4b…fc0`, grader
   hash `b4ae81af…`, version tuple `f22635f6…` — re-verify all three via
   `c4_skills.pins` / `c4_skills.runner.grader_source_paths`), a healthy
   shared-vLLM window (the runner refuses trials on a busy server and
   idle-waits up to 3600 s per fresh trial, aborting the run on breach),
   no leftover `c4eval` containers (`docker ps --filter name=c4eval`).
2. Sweep any partial run dir (no `run.json`) first — the runner refuses
   a stale sidecar and the policy is one dir per attempt.
3. Re-run the identical command above (a fresh seed is fine and
   designed; the 10 `none`/`upstream` trials are cache hits under the
   same pins, the 5 `skill` trials are always fresh); the window
   watcher appends to
   `.specmgr/feat/feat-250-c4-structurizr-skills/work/p150-window-rerun.log`
   (per the going-forward rule — /tmp is throwaway only).
4. Verify from the run dir: `run.json` + `report.json` present; variant
   hash `89e0bc4b…fc0` and grader hash `b4ae81af…` in `run.json`;
   `cache_reason: hit` on all 10 `none`/`upstream` trials (any fresh one
   means the cache key moved — stop and investigate before any verdict);
   the full locked 9-gate set on the 5 skill trials (`cli_valid`,
   `file_untouched`, `vague_label_found`, `library_container_found`,
   `external_tag_found`, `keyless_view_found`, `crowded_view_found`,
   `orphan_found`, `no_false_findings`); the hybrid rule (0/5 or below
   `none` ⇒ "accepted with caveat", ≥1/5 ⇒ clean acceptance); the window
   stop line (≥3 of 5 fresh skill trials at the 1200 s timeout ⇒ the
   sample is tainted).
5. Bounded-wait policy for busy windows: at most 2 abort cycles
   (≈2–3 h wall) — sweep + relaunch on the first, STOP the campaign
   effort after the second and record "bookkeeping complete, held-out
   pending".

## Bookkeeping done this session (Task 150.150)

- Pinning test: drafted in
  `.specmgr/feat/feat-250-c4-structurizr-skills/draft_test_skill_c4_model_review.py`
  (deleted 2026-11-24 by Task 190.170, S1: a byte-identical copy),
  installed at `tests/opencode/test_skill_c4_model_review.py` (30 tests,
  green against the on-disk folder; no network/Docker/model calls).
- Attribution/source-map re-verification against the cached upstream
  checkout at the pinned commit (one MIT source, three adapted files,
  dropped-content list complete, ideas-only marks where rewritten).
- Regenerators: `specmgr docs` (one-line diff: the test-file count
  502 → 503 for the new pinning test file — the only self-consistent
  state) and `specmgr harness-bundle` (bundle 49 → 55, the six
  c4-model-review files; second run byte-identical).
- `tests/commands/test_harness_bundle.py` updated (49 → 55, skill
  31 → 37, docstring + the method rename per the `…55_files`
  precedent).
