# History: offset/limit Coordinates for the update and get Tools

#### 2026-09-02 04:54:34.000+02:00 - Phase 4 Tasks 4.1–4.3 complete (docstrings, `AGENTS.md`, `CHANGELOG.md` moved to `offset`/`limit`; docs regenerated; ADR accepted; feat-7 annotated)
Task 4.1: `src/biz/dfch/specmgr/general/tools/__init__.py`'s module
docstring — the two stale clauses rewritten: `update` now reads "the
generic, cross-domain whole-body or line-range replace for the eleven
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr; optional read-style
body-line ``offset``/``limit`` coordinates -- ``offset`` = 1-based first
line, ``limit`` = number of lines, omitted = through end of body, ``0``
= pure insert, ``offset = N+1`` = the virtual end-of-body append
position -- strict validation, splice-then-validate-whole)" (was "seven
whole-body document types … optional 1-based inclusive body-line
``begin``/``end`` range with the ``N+1`` end-of-body sentinel") and
`set_status` now reads "all twelve document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/adr …)" (was "all eight …
req/uc/tsk/qa/prb/gol/rsk/adr"); the `mdformat`/`delete`/`webfetch`
clauses untouched (already accurate). `src/biz/dfch/specmgr/server.py`'
module docstring — the `update` entry's "optional 1-based inclusive
``begin``/``end`` body-line range with the ``N+1`` end-of-body
sentinel; the spliced result is validated as a whole document before
anything is written" replaced by the read-style `offset`/`limit`
equivalent (omitted ``limit`` = through end of body, ``0`` = pure
insert, ``offset = N+1`` = the virtual end-of-body append position;
strict validation; spliced result validated as a whole document before
anything is written), and each of the eleven `get_<d>` entries (uc,
req, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr — the feat/vcr lines
adapted to their local wrapping) had its `raw=True` parenthetical
extended with the same clause: ", optionally windowed with read-style
``offset``/``limit`` (raw-only, clamping))". `AGENTS.md` — the eleven
per-domain bullets (uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr plus the
`general/` bullet's closing "eleven `get_<d>` tools" sentence) each
moved to "(the text `update`'s `offset`/`limit` index into), with
optional read-style `offset`/`limit` windowing of that raw read
(raw-only; out-of-range values clamp, never error)" keeping their
surrounding structure, and the generic `update` bullet's "optional
1-based inclusive body-line `begin`/`end` with the `N+1` end-of-body
sentinel, splice-then-validate-whole" replaced by "read-style
`offset`/`limit` body-line coordinates (`offset` = 1-based first line,
`limit` = count; omitted `limit` = through end of body, `0` = pure
insert, `offset` `N+1` = append; strict validation, never clamped),
splice-then-validate-whole"; nothing else in `AGENTS.md` touched.
`CHANGELOG.md` — above the existing `### Fixed` entry (untouched) in
`[Unreleased]`, a `### Added` bullet for the `get_<d>` windowing
(eleven tools, raw-only, `offset` 1-based default 1 floored, `limit` a
line count defaulting through end of body capped at the remaining
lines, `offset > N` → empty string, coordinates with `raw=False` →
`ValueError`, served by the new no-I/O `window_body` helper in
`general/tools/_splice.py`, clamping per the `list_<d>` convention,
GitHub issue #28 + ADR 4ec08dcb) and a `### Changed` bullet for the
breaking hard rename (`offset` 1..N+1 with N+1 the virtual append
position, `limit` a count, omitted = through end of body, `0` = pure
insert; strict `ValueError` out-of-range, `limit` without `offset`
before any file access; splice-then-validate-whole/verbatim
persistence/frontmatter carry-over unchanged; every LLM-facing surface
moved in the same release; ADR 4ec08dcb referencing, not superseding,
ADR 36905d5b; GitHub issue #28), styled after the file's existing
**BREAKING** (0.x) bullet. Task 4.2: `uv run --frozen specmgr docs`
changed exactly the two docstring pages (`docs/api/biz.dfch.specmgr.
server.md`, `docs/api/biz.dfch.specmgr.general.tools.md` — the
`general/tools/__init__.py` module page; no other file) and rewrote
`docs/GENERATED.md` byte-identically; `uv run --frozen specmgr
mcp-docs` proved no-change (`docs/MCP.md` absent from `git status`
afterwards — no tool descriptions change in Phase 4); `uv run --frozen
specmgr adr-toc` proved no-change at that point (the status flip
follows in Task 4.3). Task 4.3: the ADR set to accepted via the
specmgr MCP `specmgr_set_status` tool (`id=4ec08dcb-…`, `type="adr"`,
`status="accepted"`), verified via `git status` to have changed this
worktree's `docs/adr/4ec08dcb-fcb7-4961-abaf-ff7803e2f21d-offset-limit-
coordinates-for-the-generic-update-tool-and-get.md` (frontmatter
`status: accepted`); `uv run --frozen specmgr adr-toc` then regenerated
`docs/adr/README.md` (the 4ec08dcb entry now shows `Status: accepted`);
`feat-7-various-improvements/README.md`'s Task 0.32 status text gained
"**`feat-28-get-update` is now complete** (all five phases 0–4 done;
the revised contract is recorded in ADR
4ec08dcb-fcb7-4961-abaf-ff7803e2f21d, accepted)." after the existing
split-out clause (Task 0.15 → feat-13 precedent), its frontmatter
`updated` bumped to 2026-09-02, and a `#### Update 2026-09-02 (Task
0.32 split-out feature complete)` entry prepended to its Recent
Updates; this plan's frontmatter flipped `status: in-progress` →
`done` (`updated` bumped) and Tasks 4.1–4.3 marked done in place.
Task 4.4 (final gate, green): `uv run --frozen ruff format --check`
(1475 files already formatted), `uv run --frozen ruff check` (All
checks passed!), `uv run --frozen vulture src/ whitelist.py
--min-confidence 60` (clean, no output), `uv run --frozen python -m
unittest discover -s tests -t . -p "test_*.py"` (Ran 2784 tests in
109.288s — OK; same count as the Phase 2/3 baselines — docstring,
prose, and changelog changes only, no tests added or removed). Drift
check: `specmgr docs` + `specmgr mcp-docs` + `specmgr adr-toc`
re-run a second time produced no further changes — `git status --short`
byte-identical before and after the runs. ACC-004: `grep -rn "begin"
src/biz/dfch/specmgr --include=*.md` shows only the `sop_example.md:17`
prose word ("can begin productive work"); `grep -rn "begin=\|end=\|begin\b"
src/biz/dfch/specmgr --include=*.py` shows zero range-vocabulary hits —
the only two matches are English phrases "to begin with" in
`rsk/tools/__init__.py:28` and `tsk/tools/__init__.py:28` (neither a
`begin`/`end` range reference); `grep -n "begin" AGENTS.md` zero
hits. ACC-005: the ADR frontmatter says `status: accepted`,
`docs/adr/README.md` shows `Status: accepted` for 4ec08dcb, and the
ADR references 36905d5b in four places (all "referenced, not
superseded"). ACC-006: exactly one commit per phase — this branch
carries the four Phase 0–3 commits (`f15f01f`, `0783675`, `cf8df5d`,
`9efbff5`) plus pre-phase-0 planning/merge housekeeping; Phase 4's
fifth commit is the orchestrator's after this report. Not committed
(the orchestrator commits); not pushed.

#### 2026-09-02 02:22:14.617+02:00 - Phase 3 complete (LLM-facing contract: instruction data files + prompt tests moved to `offset`/`limit` in the same change, gate green)
Task 3.1: the ten packaged `*_update_instructions.md` data files
(`req`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/`feat`/`vcr` — no `uc`,
no prompts package; no `adr`, different mechanism) rewritten in the
"Line-range replace" bullet to the new coordinate wording: "identify
the 1-based line to start at and how many lines to replace -- `offset`
is the first body line, `limit` the number of lines
(`offset`..`offset+limit-1`); `limit` omitted replaces through the last
body line, `limit=0` is a pure insert, and the `N+1` position is
end-of-body: `offset = N+1` appends after the last line -- and call
`update(id, type=\"<d>\", content, offset=..., limit=...)`", and in the
"Whole-body replace" bullet "with no `begin`/`end`" → "with no
`offset`/`limit`". The seven req-shaped files
(`req`/`tsk`/`prb`/`gol`/`rsk`/`dec`/`sop`) take the target wording's
own line breaks verbatim; `qa` keeps its wider wrap style (the
orphaned "passing only" its old wrap produced was rejoined); `feat`
keeps its long trailing-`update(...)`-call line and its extra
`### Updates`/`### Decisions Made` insert sentence; `vcr` keeps its
own-line call + "passing only" continuation and its
"one paragraph, field, or acceptance criterion" bullet opening.
`qa/data/qa_refine_instructions.md`'s "Persist the appended questions"
clean-append step: `update(id, type="qa", content, begin=N+1, end=N+1)`
→ `update(id, type="qa", content, offset=N+1)` (limit omitted is the
append case; the `N+1` end-of-body wording kept). The only `begin`
left in `src/` markdown is the prose word in
`sop/data/sop_example.md:17` ("can begin productive work" — not a
range reference, deliberately untouched). Task 3.2: the ten
`test_update_*` prompt test files (`tests/{req,tsk,qa,prb,gol,rsk,dec,
sop,feat,vcr}/prompts/`) — each `test_mentions_range_update_flow` now
asserts the new literals, byte-identical to the data files:
`assertIn("offset = N+1", result)` and
`assertIn('update(id, type="<d>", content, offset=..., limit=...)',
result)` plus the matching `result.index(...)` ordering assertion; the
now-stale `assertIn("1-based, inclusive line range", result)` (that
phrase no longer exists in the new wording) was replaced by
`assertIn("1-based line to start at and how many", result)`, a phrase
that is contiguous on a single data-file line in all ten domains; the
method docstrings reworded to the `offset`/`limit` vocabulary.
`tests/qa/prompts/test_refine.py` — `test_mentions_n_plus_one_append_
range` literal `update(id, type="qa", content, begin=N+1, end=N+1)` →
`update(id, type="qa", content, offset=N+1)` (assertIn + index; the
docstring's "N+1 end-of-body append range" wording stays valid and was
kept). Beyond the verified 11-file list, one Phase-1 leftover:
`tests/sop/tools/test_integration.py`'s module docstring still said the
round-trip exercises "line-range (`begin`/`end`) branches of `update`"
while the test itself (line 169) calls `update(..., offset=k, limit=1)`
— reworded that one line to `offset`/`limit`. The intentional
`assertNotIn("begin", schema["properties"])` negative assertions in
`tests/general/tools/test_update.py` and the ACC-006 end-to-end walk's
real `update(..., offset=line_number, limit=1)` call (Phase 1) were
left untouched. All 144 prompt tests pass, proving the asserted
literals match the data files exactly. Task 3.3 gate (green): `ruff
format --check` (1475 files already formatted), `ruff check` (All
checks passed!), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), full `unittest` suite (Ran 2784 tests — OK; same
count as the Phase 2 baseline — data-file + literal changes only, no
tests added or removed), `specmgr docs` + `specmgr mcp-docs`
regenerated with no drift (`git status --short` byte-identical before
and after the runs — data files are not API docstrings and no tool
descriptions change in Phase 3). ACC-004 repo searches: `grep -rn
"begin" src/biz/dfch/specmgr --include=*.md` shows only the
`sop_example.md:17` prose word; `grep -rn "begin=\|end=\|begin\b"
src/biz/dfch/specmgr --include=*.py` shows only the two known Phase-4
items (`server.py:215` and `general/tools/__init__.py:24` docstrings)
plus two prose "to begin with" docstring hits in
`rsk/tools/__init__.py:28` and `tsk/tools/__init__.py:28` — no
`begin`/`end` range references remain in `src/`. Not committed (the
orchestrator commits); not pushed.

#### 2026-09-01 21:59:07.448+02:00 - Phase 2 complete (get windowing: `window_body` helper + `offset`/`limit` on the eleven `get_<d>` tools, gate green)
Task 2.1: `general/tools/_splice.py` gains the no-I/O
`window_body(text, offset=1, limit=None)` helper (added to `__all__`
beside `body_text`/`splice_body`): read-style windowing with clamping,
never erroring — `offset` floors to 1, `offset > N` (incl. empty text)
returns `""`, `limit` caps at the remaining lines (`None` = through end
of body, negative = `""`), and the result keeps each window line's
trailing newline (`""` for an empty window, else
`"\n".join(lines[start-1 : start-1+count]) + "\n"`), so the defaults
reproduce a normal trailing-newline body byte-for-byte and consecutive
non-overlapping windows concatenate back to the body; the module
docstring moves to the three-helper shape and the raw/splice invariant
paragraph extends (windowed or not, `window_body` is the single
windowing definition shared by all eleven tools). Task 2.2: the eleven
`get_<d>` tools (`req`/`uc`/`tsk`/`qa`/`prb`/`gol`/`rsk`/`dec`/`sop`/
`feat`/`vcr`) extended — signature `get_<d>(id, raw=False, offset=None,
limit=None)`, a raw-only guard before any file access (coordinates with
`raw=False` → `ValueError` naming both values, `update`-guard style),
the raw branch returning `body_text(path)` directly when both
coordinates are omitted (byte-for-byte pass-through, no rejoin) and
`window_body(text, offset or 1, limit)` otherwise, not-found behaviour
unchanged (incl. windowed raw mode), the `@mcp.tool` descriptions
extended with the windowing sentence, the docstrings gained
`offset`/`limit` Parameters entries + a `ValueError` Raises entry, the
stale Phase-1 `begin`/`end` wording in the `raw` parameter reworded to
`offset`/`limit` and extended for the window, and the module
docstrings' `raw=True` paragraphs extended for the windowing capability
(feat's folder-convention `id` docstring kept). Task 2.3: new
`tests/general/tools/test__splice.py` (18 direct no-I/O tests):
`window_body` defaults byte-for-byte, mid window, `offset > N` → `""`,
limit capping, `limit=0` → `""`, `offset < 1` floors, negative limit →
`""`, empty text → `""`, consecutive-window concatenation; and
`splice_body`'s new signature — single-line replace, multi-line replace,
omitted limit through end, `limit=0` mid-body insert, `offset=N+1`
append (both limit forms), and each strict branch (`offset<1`,
`offset>N+1`, `limit<0`, `offset+limit-1>N`) raising `ValueError`
naming the offending value(s). Task 2.4: the eleven
`tests/<d>/tools/test_get_<d>.py` extended (four new tests per domain,
mirroring the existing style/naming): window slice equality (offset=2,
limit=3 vs the seeded body's lines), clamp/empty cases (`offset` past
the last line → `""`; oversized `limit` caps at the remaining lines),
coordinates + `raw=False` → `ValueError` (offset/limit and limit-only
variants; message names raw), and the windowed ACC-003
read-into-splice round-trip (windowed raw read at domain-specific
`k`/`m` asserted equal to the full read's slice, same-count replacement
fragment spliced via the generic `update` at those coordinates, replaced
lines equal the fragment and unchanged regions byte-identical); the
existing both-modes not-found tests each gained a windowed raw
assertion. All pre-existing tests pass unchanged (default raw read
byte-for-byte identical). Task 2.5 gate (green): `ruff format --check`
(1475 files already formatted — 1474 + the new test file), `ruff check`
(All checks passed!), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), full `unittest` suite (Ran 2784 tests — OK; 2722 +
18 new `test__splice` + 44 new per-domain window tests), `specmgr docs`
\+ `specmgr mcp-docs` regenerated (only the eleven
`docs/api/...get_<d>.md` pages, `docs/api/..._splice.md`,
`docs/api/README.md`, `docs/GENERATED.md` — test-file count 318 → 319 —
and `docs/MCP.md`'s eleven `get_<d>` entries changed; a second
regeneration run is byte-identical, no drift). Not committed (the
orchestrator commits); not pushed.

#### 2026-09-01 18:04:04.427+02:00 - Phase 1 complete (update core `begin`/`end` → `offset`/`limit` rename + test migration, gate green)
Task 1.1: `general/tools/_splice.py` reworked — `splice_body(current_body,
offset, limit, content)` now takes read-style coordinates (`offset` =
1-based first line to replace, `limit` = count; omitted `limit` = through
end of body, `0` = pure insert, `offset=N+1` = virtual end-of-body append
position) with strict validation (`offset<1`, `offset>N+1`, `limit<0`,
`offset+limit-1>N` each raise `ValueError` naming the offending value(s)
and the allowed range; never clamped); the module and `body_text`
docstrings move to the new vocabulary (and the stale "seven get tools"
count is corrected to eleven). `window_body` deliberately not added yet
(Phase 2, Task 2.1). Task 1.2: `general/tools/update.py` reworked — public
`offset`/`limit` parameters, the old both-or-neither guard replaced by
`limit` without `offset` → `ValueError` before any file access, all eleven
`_update_<d>` adapter signatures/branches/`splice_body` calls updated,
`_update_req` docstring and the module docstring reworded, the `@mcp.tool`
description rewritten for the new contract. Task 1.3: every
`update(begin=, end=)` test call site migrated — `tests/general/tools/
test_update.py` (success cases re-expressed per the Design Notes mapping,
error cases re-expressed incl. the new pre-file-access guard tested
against both a non-existent and an existing id, `TestUpdateRegistration`
now asserts `offset`/`limit` in the input schema, that `begin`/`end` are
gone, and that `required` is unchanged), the eleven
`tests/<d>/tools/test_get_<d>.py` round-trip lines,
`tests/feat/tools/test_integration.py`, `tests/sop/tools/test_integration.
py`, and — beyond the Task 1.3 list — the real ACC-006 end-to-end prompt
walk call site in `tests/feat/prompts/test_update_feat.py` (its comment
too); the prompt-literal `assertIn("begin=..., end=...")` assertions in
the `*_prompts` test files were left untouched per the Phase 3 boundary.
Task 1.4 gate (green): `ruff format --check` (1474 files already
formatted), `ruff check` (All checks passed!), `vulture src/ whitelist.py
--min-confidence 60` (clean, no output), full `unittest` suite (Ran 2722
tests — OK), `specmgr docs` + `specmgr mcp-docs` regenerated (only
`docs/api/..._splice.md`, `docs/api/...update.md`, and `docs/MCP.md`'s
`update` entry changed; re-run shows no drift). One flagged observation:
`general/tools/__init__.py`'s package docstring still describes the old
`begin`/`end` range (and predates the dec/sop/feat/vcr domains) — left
untouched as the Phase 4 item the prompt lists under "do not touch"; the
Phase 1 sanity grep therefore shows exactly that one file as the only
`begin`/`end` range vocabulary remaining in `src/biz/dfch/specmgr/
general/`. Not committed (the orchestrator commits); not pushed.

#### 2026-09-01 15:58:41.327+02:00 - Phase 0 complete (feat-7 split-out annotation, ADR draft, gate green)
Task 0.4: feat-7's Task 0.32 annotated per the Task 0.15 → feat-13
precedent — checkbox `[x]`, status set to "split out into
`feat-28-get-update` (GitHub issue #28,
`.specmgr/feat/feat-28-get-update/README.md`) on 2026-09-01" plus a clause
noting the revised contract (`offset`/`limit` for the generic `update` tool
\+ windowed `get_<d>` reads, hard rename, ADR draft) is recorded in this
plan; feat-7 frontmatter `updated` bumped to 2026-09-01; a new `#### Update
2026-09-01 (Task 0.32 split out)` entry prepended to feat-7's Recent Updates
(the indented Background paragraph left untouched). Task 0.5: ADR
`4ec08dcb-fcb7-4961-abaf-ff7803e2f21d` ("offset/limit coordinates for the
generic update tool and `get_<d>` windowed reads") created via
`specmgr_create_adr` with status `draft` (set to accepted at close, Task
4.3) — six options across the three decided axes (hard rename vs. dual
alias; strict vs. clamping splice validation; raw-only vs. both-modes
windowing), the exact `offset`/`limit` semantics including the today→new
`begin`/`end` mapping table, and Consequences naming every LLM-facing
surface that moves in the same release; references ADR
36905d5b-8057-4294-8665-c7eed5534db0 without superseding it. Verified via
`git status` that it landed in this worktree's `docs/adr/`, then `uv run
--frozen specmgr adr-toc` regenerated `docs/adr/README.md`. Task 0.6 gate
(green): `ruff format --check` (1474 files already formatted), `ruff check`
(All checks passed!), `vulture src/ whitelist.py --min-confidence 60`
(clean, no output), full `unittest` suite (Ran 2720 tests — OK). No `src/`
changes, so no `specmgr docs`/`mcp-docs` regeneration needed. Not committed
(the orchestrator commits); not pushed.

#### 2026-09-01 15:13:17.413+02:00 - Merged upstream dev (8e07594)
Upstream `dev` advanced one commit (`8e07594 fix(40): specmgr docs prunes
stale docs/api pages`); merged it into this branch (merge commit `e5d665b`,
no conflicts) and re-ran the complete test cycle — 2720 tests green (up from
2713, the merged commit added 7), `ruff format --check`/`ruff check`/
`vulture` clean. Not pushed. The `More Information` sync reference was
updated to the new dev tip.

#### 2026-09-01 14:41:58.971+02:00 - Session wrap-up; plan made self-contained for a fresh implementation session
Added a `### More Information` section with the operational facts a fresh
implementing agent would otherwise have to rediscover: worktree/branch,
never-push, the per-phase commit-message convention, the specmgr MCP server
cwd caveat (base dirs resolve relative to the server's own cwd — verify
created files land in this worktree via `git status`), the `specmgr adr-toc`
regeneration step for Task 0.5, and the `read`-tool reference for
"read-style" coordinates. No code or contract changes. Implementation picks
up at Task 0.4 (feat-7 Task 0.32 annotation) and Task 0.5 (ADR draft).

#### 2026-09-01 14:09:43.294+02:00 - Feature created; planning complete
Completed: the design phase — all contract decisions taken (see Decisions
Made); synced to upstream `dev` `8c13e16` (uv synced, pre-commit installed,
baseline 2713 tests green); filed GitHub issue #48 for the deferred
`create_feat` id behaviour (no caller id, no `set_feat_id` tool); created this
feature via `specmgr_create_feat` and renamed the auto-assigned
`feat-37-offset-limit-coordinates-for-the-update-and-get-tools` folder +
frontmatter id to `feat-28-get-update`. Next: Phase 0 remainder (feat-7 Task
0.32 annotation, ADR draft) then Phase 1 (`update` core rename).
