# specmgr harness install — Task 130.150 end-to-end walkthrough record

feat-167-mcp-lifecycle-commands-2, Task 130.150 (ACC-008 evidence). The record
of a **fresh, hermetic agent session** that installs the specmgr harness
strictly from the `specmgr://harness-bundle` resource's own `instructions`
field — the agent-driven install protocol — into a clean harness config root.
Companion artifacts: the committed bundle
`src/biz/dfch/specmgr/general/data/general_harness_bundle.json` (the sole
source the agent read) and the generator/enumeration unit tests
(`tests/commands/test_harness_bundle.py`,
`tests/general/resources/test_harness_bundle.py`) that cover ACC-008's other
half (completeness, ordering, exclusions, determinism).

## Why this fixture is committed

ACC-008 requires that an agent following only the bundle's `instructions`
field installs every file byte-exact, skips sha256-identical pre-existing
files, and asks before overwriting a differing one. That behaviour can only be
observed from a **real, fresh agent session** with no access to this repo, its
plan, or the source `.opencode/` files — the bundle must be its only source.
The implementing agent therefore cannot self-produce this walkthrough (it
cannot stand outside itself and follow only the published `instructions`), so
the record is committed as pinned evidence, mirroring the feat-185-uc-diagrams
ACC-002 precedent (`tests/fixtures/uc-diagrams/buy-goods.sequence.walkthrough.md`).

## Execution method

- **Fresh container:** `ghcr.io/anomalyco/opencode:2.2.5` (Alpine/musl), run
  with `--network host` and **no mount of this repository** — the agent could
  not see the plan or the source files; the bundle was its only source.
  OpenCode state verified empty of harness files before the run: the global
  config (`/root/.config/opencode`) held only OpenCode's own `service.json`
  (no `agent/`/`command/`/`skill/` files) and `/root/.local/share/opencode`
  was fresh. `tmux` 3.7c was installed via `apk` to drive the interactive TUI.
- **Model:** `vllm-sys0/qwen3.8-27b-bf16-896k` — a local vLLM endpoint at
  `127.0.0.1:8081`, registered as an OpenAI-compatible provider in the scratch
  project's own `.opencode/opencode.json`.
- **MCP wiring:** the `specmgr` server ran **on the host** (this dev checkout's
  venv) in streamable-http mode at `127.0.0.1:8099`, with its CWD set to the
  scratch project — so it exposed only the packaged resources (including
  `specmgr://harness-bundle`) and never this repo's documents. (The container
  is Alpine/musl and cannot spawn the dev venv's glibc Python; host-side
  hosting is the reason. See Environment notes.)
- **Scratch project:** `/work/scratch-project` (container path), a fresh
  directory pre-seeded with exactly two harness files to exercise the protocol's
  conditional branches, plus its own `.opencode/opencode.json` (provider + MCP
  wiring only):

  | Pre-seeded file | On-disk sha256 | Role |
  |---|---|---|
  | `agent/ref-finder.md` | `05729c7d6797d33bff140ff1b58ca6491540039df2992385c9b06b5ee452ef6d` (== bundle) | the **SKIP** case — already up to date |
  | `command/refs.md` | `a8dbfa63aa8455ac7d96882c62dd7ddacf6dc08fff48865b77d98be0f34c7705` (≠ bundle `92fb03d1d8d4e198e4c74a5ad68cbb94bfbb50aa0788b8573cd15ff2182482f8`) | the **ASK** case — pre-modified with a `[WALKTHROUGH-PREMODIFIED] ` marker in its description line |

- **Prompt sent:** exactly `Install the specmgr harness files` — nothing else.
- **Session:** `ses_e68a825bfffeGoFH0UBuaibARb`, duration 21 m 26 s,
  15.2 tok/s.

## What the agent did (following the `instructions` field)

1. Listed the `specmgr` MCP resources and read `specmgr://harness-bundle`,
   pulling the 24-file bundle (6 `agent/` + 10 `command/` + 8 `skill/*/`)
   out of context into a tool-output file.
2. Applied the protocol's step 1 (pick the harness config root via
   OpenCode's own `customize-opencode` skill) and chose the **project** root
   `/work/scratch-project/.opencode/` — its stated rationale: the project
   already carried a partial harness there, while `~/.config/opencode/` held
   only `service.json`.
3. Compared on-disk sha256 per entry: `agent/ref-finder.md` **matched** (→
   skip), `command/refs.md` **differed** (→ ask), the other 22 were missing
   (→ write).
4. Asked before overwriting `command/refs.md` (the transcript below), then
   transferred every write **byte-exact via hex encoding** (the minimal
   container has no Python/Node/JS scripting runtime — `sha256sum`, `xxd`,
   `awk`, `sed` only) and re-read + sha256-verified each file from disk.
5. Never read, wrote, or merged `opencode.json`, and reported the per-file
   outcome (the final report below).

## The question transcript (protocol step 3: a differing target)

Posed via OpenCode's `question` tool (header: `refs.md conflict`). The exact
strings from the session:

Question (verbatim):

```text
The existing .opencode/command/refs.md differs from the bundled version only by a "[WALKTHROUGH-PREMODIFIED] " marker in its description line. Overwrite it with the pristine bundle version?
```

Options (verbatim `label` / `description`):

```text
Overwrite (Recommended) — Replace the premodified file with the bundle's canonical version; all 24 harness files end up byte-identical to the bundle.
Keep existing — Leave .opencode/command/refs.md untouched; it will be reported as failed (skipped on user decision) and the other 23 files installed as normal.
```

**Answer given:** option 1, `Overwrite (Recommended)` (approved).

## Outcome (the agent's final report, verbatim)

```text
Installation complete. All 24 specmgr harness files are in place at the project harness root `/work/scratch-project/.opencode/` (chosen per OpenCode's config rules: the project already carried a partial harness there, while `~/.config/opencode/` held only `service.json`).

**Per-file outcome (protocol step 5):**

| Result | Count | Files |
|---|---|---|
| **Installed** (new) | 22 | `agent/`: doc-repairer, feat-refiner, feat-reviewer, phase-implementer, phase-orchestrator · `command/`: implement-feature, ref-graph, refine-feature, release, repair, review-feature, translate, translation-status, uc-diagram · `skill/`: feat-numbering, refine-feature, repair, review-feature, specmgr-refs, translate-artifact, translation-status, uc-diagram (each `SKILL.md`) |
| **Skipped** (already up to date) | 1 | `agent/ref-finder.md` — on-disk sha256 already matched the bundle |
| **Updated** (overwritten, approved) | 1 | `command/refs.md` — removed the `[WALKTHROUGH-PREMODIFIED]` marker, per your confirmation |
| **Failed** | 0 | — |

**Verification:** every write was re-read from disk and its sha256 compared against the bundle — final pass confirmed **24/24 exact matches**, with content transferred byte-exact via hex encoding (no reformatting/rewrapping). `opencode.json` was never read, written, or merged.

The harness has already picked the files up — the nine new skills (feat-numbering, refine-feature, repair, review-feature, specmgr-refs, translate-artifact, translation-status, uc-diagram, and the subagents/commands they support) are now registered and active in this session.
```

The per-file table is internally consistent with the bundle's 24 files
(6 `agent/` + 10 `command/` + 8 `skill/*/`): 5 `agent/` + 9 `command/` +
8 `skill/` installed new, + the 1 `agent/` skip (`ref-finder.md`) + the 1
`command/` update (`refs.md`) = 6 + 10 + 8 = 24. (The agent's closing sentence
counts "nine new skills"; the bundle carries exactly 8 `skill/*/` files — the
loose "nine" folds in "the subagents/commands they support" as a ninth item and
does not contradict the 24/24 file count above.)

## Independent verification (orchestrator, host-side, after the run)

A fresh Python check of the scratch tree against the committed bundle
`src/biz/dfch/specmgr/general/data/general_harness_bundle.json`:

- **24/24 files byte-exact** — content equality **and** sha256 match.
- **0 missing**, **0 mismatched**, **0 extra files** under
  `/work/scratch-project/.opencode/{agent,command,skill}/`.
- `opencode.json` **intact** — never read, written, or merged.

This verdict is independent of the agent's own re-verification: it compares the
final on-disk tree to the *committed* bundle, not to the agent's in-session
hashes.

## Environment notes / deviations

Recorded honestly so a future reader knows exactly what was exercised and what
was worked around:

1. **Transient OC 2.2.5 client error (first `read_mcp_resource`).** The agent's
   first attempt to pull the bundle threw
   `ReferenceError: Unknown identifier 'globalThis'` (an OpenCode 2.2.5
   client-side defect in this Alpine image, hit inside the `execute` tool's
   JS sandbox). The immediate retry succeeded, and the bundle content always
   came from the `specmgr://harness-bundle` MCP resource — never from anywhere
   else.
2. **Host-side MCP hosting.** The `specmgr` server ran on the host, not in the
   container, because the container is Alpine/musl and cannot spawn the dev
   venv's glibc Python (see Execution method). The server's CWD was the scratch
   project, so only packaged resources were exposed.
3. **The agent's own first-pass `sed` hiccup.** A `sed` delimiter bug (the `/`
   in the path collided with `sed`'s delimiter) aborted the first install pass
   after `refs.md` had been written; the re-run was idempotent (it classified
   files against the pre-run state: 1 match / 1 diff / 22 missing) and the
   final verification covered all 24 files.
4. **Branch coverage.** The plural-variant branch of protocol step 2 (a root
   that already contains `agents/` or `skills/`) was not exercised in this
   run -- the scratch root used the singular directories throughout; only the
   singular path (install/skip/ask) has end-to-end evidence in this fixture.

None of the three affects the byte-exactness or the skip/ask outcome; all three
are recorded as worked-around, not as defects in the install protocol.

## Traceability

- **Session:** `ses_e68a825bfffeGoFH0UBuaibARb` (OpenCode 2.2.5, the model and
  wiring above). The full session transcript was captured by the orchestrator
  and is **not** committed here (it is ~314 KB); this fixture is the curated,
  self-contained record, and the session id is cited for traceability only.
- **Date:** 2026-11-01 (UTC).
- **Bundle pinned:** the 24-file
  `src/biz/dfch/specmgr/general/data/general_harness_bundle.json` as committed
  for Phase 130 (Tasks 130.100–130.140/160). It was byte-regenerated by the
  Phase 170 fix phase (review cycle 3): the 24-file set is unchanged and the
  two pre-seeded sha256 values cited above are unaffected by that regeneration.
