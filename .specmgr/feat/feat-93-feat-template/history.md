# History: Consolidate Feature Templates/Examples onto the feat MCP Tools

#### 2026-09-04 11:15:00.000+02:00 - Verification complete

Phase 3 (Verification) done. (1) Ran `specmgr docs` + `specadr adr-toc` — both exited cleanly and produced **no changes** to `docs/MCP.md`/`docs/GENERATED.md` (those files are generated from source docstrings; Phase 2 only edited AGENTS.md, not source, so no drift). (2) Full unit-test suite: **3318 tests, OK** (unchanged from baseline). (3) `validate_feat(content, full=True)` on this feature's body: **parses cleanly**. Note: the README's `### Decisions Made` section was migrated from markdown-rendered `- **[date]**:` bullets to the canonical `#### {timestamp} ( - | : ) {title}` H4 heading format required by `feat/models/v1` (matching `feat/data/feat_example.md`); without this the body failed `parse_feat` with an `AssertionError` on `DecisionEntry`. (4) `ruff format --check` + `ruff check` both pass.


#### 2026-09-04 10:45:00.000+02:00 - Implementation complete

Phase 2 (Implementation) done. (1) Deleted `.specmgr/_template/v1/README.md` (110 lines, zero consumers) via `git rm`. (2) ADR e369ee2e: removed the three verbatim fenced template blocks (Option 1 README.md block lines 77–190, Option 2 README.md block lines 233–292, Option 2 progress.md block lines 294–343), updated the Option 1 "Template location" open question to point at the canonical `get_feat_template`/`get_feat_example` tools, and appended a feat-93 pointer note at the end of the ADR. (3) AGENTS.md: rewrote the `feat` "Template" bullet to point at the canonical tools and dropped the `_template/v1/README.md` entry from the `.specmgr/` directory tree. `src/biz/dfch/specmgr/feat/data/` and the tools untouched. Phase 3 (Verification) is next.


#### 2026-09-04 10:15:00.000+02:00 - Discovery complete

Phase 1 (Discovery) done. Confirmed three diverging copies: (1) canonical `src/biz/dfch/specmgr/feat/data/feat_template.md` (1980 B) + `feat_example.md` (2423 B) under `feat/data/`; (2) orphaned `.specmgr/_template/v1/README.md` (110 lines, 2849 B, zero code consumers); (3) verbatim fenced template blocks inside ADR e369ee2e. `grep -rn "_template/v1" src/ tests/` returns no matches (exit 1). ADR e369ee2e fenced blocks: Option 1 README.md block lines 79–190; Option 2 README.md block lines 235–292 and progress.md block lines 296–343.


#### 2026-09-04 10:00:00.000+02:00 - Created

Feature scaffolded from GitHub issue #93 ("Consolidate feature templates/examples onto the feat MCP tools"). Scope, requirements, acceptance criteria, and a 3-phase task list were captured; discovery work has not started yet.
