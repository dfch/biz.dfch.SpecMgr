---
classification: null
created: '2026-09-03 00:03:19.829+02:00'
id: feat-73-74-76
status: done
type: feat
updated: '2026-10-07T06:21:40.949Z'
version: 1.0.0
---

# Feature: License Audit, sysrs Config Gaps, and Confluence Page Title Fix (issues #73/#74/#76)

## Plan

### Overview

This feature tracks three independent maintenance/quality-gap issues opened on 2026-09-02: (1) auditing NOTICE for correct 3rd-party license info across all direct dependencies, using issue #47/mdformat-simple-breaks as a worked example; (2) closing gaps where the sysrs domain is missing from specmgr://config and possibly other common cross-domain functions other domains already have; and (3) fixing specmgr_confluence_update so it sets the Confluence page title from the markdown's first H1 heading (or leaves the title untouched if there is no H1).

### Requirements

- REQ-001: NOTICE must correctly list license info for every directly used 3rd-party library dependency, verified issue-by-issue against issue #47 as a worked example.

- REQ-002: specmgr://config must expose sysrs alongside every other implemented domain, and any other common cross-domain function missing for sysrs (relative to req/uc/tsk/etc.) must be identified and listed.

- REQ-003: specmgr_confluence_update must set the target Confluence page's title from the first H1 heading of the source markdown file; if the markdown has no H1, the page title must be left unchanged.

### Acceptance Criteria

- [x] ACC-001: Every direct 3rd-party dependency's license entry in NOTICE is manually verified correct (license type + attribution text) and any discrepancy found is fixed.

- [x] ACC-002: specmgr://config's output includes a sysrs entry, and a written gap list of missing sysrs functions (vs. other domains) exists in this feature's Design Notes or a follow-up.

- [x] ACC-003: A markdown file with a first H1 updates the Confluence page title on specmgr_confluence_update; a markdown file with no H1 leaves the existing page title untouched -- both verified by test.

### Scope

#### Included

- NOTICE file audit and correction for all direct 3rd-party library dependencies.

- Gap analysis of specmgr://config and other common cross-domain functions for the sysrs domain, plus fixing the specmgr://config gap itself.

- specmgr_confluence_update: extract first H1 from source markdown and set it as the Confluence page title via the REST API.

#### Explicitly Out Of Scope

- Auditing indirect/transitive dependency licenses (direct dependencies only, per issue #73's wording).

- Implementing any newly discovered missing sysrs functions beyond specmgr://config exposure itself (those become their own follow-up features once identified).

- Any other Confluence page metadata beyond the title (labels, space, permissions, etc.).

### Design Notes

#### sysrs common-function gap analysis (Task 2.2/2.3, #74)

Cross-referenced `sysrs`'s actual tools/resources/prompts/dispatch-tool coverage (verified against
source, not just AGENTS.md prose) against every other whole-body domain, using `sop`/`vcr` as the
closest "dispatch-only from day one" baselines (ADR 36905d5b-8057-4294-8665-c7eed5534db0):

- **`specmgr://config` missing `sysrs` entry** -- confirmed missing (`general/resources/config.py`
  had no `sysrs_base_dir` import or `"sysrs"` key in the `domains` dict, and no `sysrs` in the
  resource's `description=`/docstring domain counts). **Fixed in this phase** (Task 2.1): added the
  `sysrs_base_dir` import, a `"sysrs": DomainConfig(...)` entry mirroring `"vcr"`'s exact shape
  (shared `DOCS_DIR_ENV_VAR`), updated the resource `description=` and `config_info()` docstring
  domain counts/lists from "twelve"/ten-shared to "thirteen"/eleven-shared, and updated
  `models/config_info.py`'s `DomainConfig.env_var`/`ConfigInfo.domains` docstrings similarly. Test
  file `tests/general/resources/test_config.py` updated in lockstep (`_ALL_DOMAINS`,
  `_DOCS_DIR_DOMAINS` now include `sysrs`).

- **Generic dispatch tool coverage (`update`, `set_status`, `set_classification`, `delete`)** --
  all four already fully support `sysrs`: `_UPDATE_ADAPTERS`/dispatch dict in
  `general/tools/update.py` has `"sysrs": _update_sysrs` (line 700) plus `"sysrs"` in the `type`
  `Literal[...]` (line 723); `general/tools/set_status.py` has `_set_status_sysrs` registered
  (line 555) and `"sysrs"` in its `Literal[...]` (line 578); `general/tools/set_classification.py`
  likewise (`_set_classification_sysrs` at line 484, `Literal[...]` at line 504);
  `general/tools/delete.py` has `_DELETE_TYPES` including `"sysrs"` (line 115) and
  `"sysrs": _delete_sysrs` in its adapter dict (line 342). **No gap** -- nothing to fix.

- **`get_sysrs` `raw`/`offset`/`limit` support** -- confirmed present:
  `sysrs/tools/get_sysrs.py` signature is
  `get_sysrs(id: str, raw: bool = False, offset: int | None = None, limit: int | None = None)`,
  using the same shared `body_text`/`window_body` helpers every other domain's `get_<d>` raw path
  uses. **No gap.**

- **`_path_safety.py`'s `_UUID_TYPES`** -- confirmed `"sysrs"` is present in the frozenset
  (`general/tools/_path_safety.py:66`), so `sysrs` gets the same path-injection/wrong-format UUID
  guard as every other UUID-addressed domain. **No gap.**

- **All 7 tools / 3 resources / 2 prompts** -- confirmed all present on disk:
  `sysrs/tools/` has `create_sysrs.py`, `parse_sysrs.py`, `list_sysrs.py`, `get_sysrs.py`,
  `get_sysrs_example.py`, `get_sysrs_template.py`, `validate_sysrs.py` (7/7);
  `sysrs/resources/` has `sysrs_schema.py`, `sysrs_example.py`, `sysrs_template.py` (3/3, matching
  the no-`{id}`/no-`list` convention every other whole-body domain follows); `sysrs/prompts/` has
  `create_sysrs.py`/`update_sysrs.py` (2/2). **No gap.**

- **`specmgr://iso25010` usage in `create_sysrs`/`update_sysrs` prompts** -- confirmed both
  prompts reference the cross-cutting `specmgr://iso25010` resource by name for grouping
  `## Requirements` by ISO/IEC 25010:2023 characteristic, matching AGENTS.md's claim. **No gap.**

**Conclusion**: the *only* gap found for `sysrs` relative to every other whole-body domain was the
missing `specmgr://config` entry, which this phase fixes directly (Task 2.1). No follow-up feature
is needed for `sysrs` itself -- every other common cross-domain function (dispatch tools, `raw`
read support, `_UUID_TYPES` membership, tool/resource/prompt completeness, cross-cutting resource
usage) was already correctly wired when `sysrs` was built (feat-32-sysrs).

### Task List

#### Phase 100: NOTICE License Audit (#73)

- [x] Task 100.100: List every direct 3rd-party library dependency from pyproject.toml.

- [x] Task 100.110: For each dependency, verify NOTICE lists the correct license type and attribution text (using #47/mdformat-simple-breaks as the worked example).

- [x] Task 100.120: Fix any discrepancies found in NOTICE.

#### Phase 110: sysrs Config/Gap Analysis (#74)

- [x] Task 110.100: Add sysrs to specmgr://config.

- [x] Task 110.110: Compare sysrs's tools/resources/prompts against every other whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) to find other missing common functions.

- [x] Task 110.120: Write up the gap list (in Design Notes or a follow-up feature).

- [x] Task 110.130: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` and confirm all pass.

#### Phase 120: Confluence Page Title Fix (#76)

- [x] Task 120.100: In specmgr_confluence_update, parse the first H1 heading from the source markdown file.

- [x] Task 120.110: Set the Confluence page's title field to that H1 text when updating the page body via the REST API.

- [x] Task 120.120: If no H1 is present, leave the existing page title untouched.

- [x] Task 120.130: Add/adjust tests covering both the H1-present and no-H1 cases.

- [x] Task 120.140: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` and confirm all pass.

## Progress

### Current Status

**As of 2026-09-03**: All three phases are complete. Phase 1 (NOTICE license audit, #73): all direct dependencies from `pyproject.toml` were verified against installed package metadata (`importlib.metadata` + each package's own `*.dist-info/licenses/LICENSE*` file), several copyright-holder discrepancies were fixed, and NOTICE entries for the three previously-missing direct dependencies (`mdformat`, `mdformat-simple-breaks`, `httpx`) were added. Phase 2 (#74): `sysrs` is now exposed via `specmgr://config`, and a full gap analysis (Design Notes above) confirmed no other missing common cross-domain functions exist for `sysrs`. Phase 3 (#76): `confluence_update` now sets the Confluence page's title from the source Markdown's first ATX-style H1 heading, leaving the existing title unchanged when no H1 is present, verified by test. All acceptance criteria (ACC-001/ACC-002/ACC-003) are satisfied; this feature is done.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-03 16:00:00.000+02:00 - Phase 3 complete: confluence_update sets page title from the Markdown's first H1 (#76)

`src/biz/dfch/specmgr/general/tools/confluence_update.py`: added a new private helper
`_extract_first_h1(markdown_text: str) -> str | None`, backed by a new module-level constant
`_H1_HEADING_PATTERN = re.compile(r"^#(?!#)[ \t]+(\S.*)$", re.MULTILINE)` -- matches only
ATX-style H1 headings (a single `#`, never `##`/`###`/...), scanning the RAW markdown source
top-to-bottom via `.search()` and returning the first match's text stripped of leading/trailing
whitespace, or `None` if no H1 is found anywhere. `confluence_update()` now reads the markdown
file into `raw_markdown_text`, calls `_extract_first_h1` on it BEFORE the leading-frontmatter
conversion overwrites the `markdown_text` variable (frontmatter's `key: value` lines can never
themselves match the H1 pattern, so scanning the raw text before frontmatter-to-code-block
conversion is safe and simplest), and uses the extracted H1 as the new `title` for the PUT
payload -- falling back to the GET-fetched title unchanged when no H1 is found. Updated the
module docstring's "full write flow" step 3/6, the `confluence_update()` docstring
(behavior prose + `Returns` example dict shape), and the `@mcp.tool(...)` `description=` string
to describe the new H1-driven title behavior (previously all three said "leaving the title
unchanged"/"unchanged title", now corrected). `tests/general/tools/test_confluence_update.py`: renamed
`test_put_payload_has_incremented_version_unchanged_title_and_rendered_body` to
`test_put_payload_has_incremented_version_h1_derived_title_and_rendered_body` and updated its
assertions -- the existing `_MARKDOWN_SOURCE` constant already contains an H1 ("Heading"), so
under the new behavior the PUT payload's title and the returned `result["title"]` are now
`"Heading"`, not the old GET-fetched `_TITLE`. Added new tests: `test_no_h1_in_markdown_leaves_existing_title_unchanged`
and `test_h2_only_markdown_leaves_existing_title_unchanged` (both confirm the PUT payload/result
title stays exactly the GET-fetched title when the markdown has no H1, including when it has
only an H2), `test_frontmatter_then_h1_uses_h1_as_new_title` (a leading YAML frontmatter block
followed by an H1 still updates the title through the full mocked-HTTP `confluence_update()`
flow), plus eight focused unit tests directly against `_extract_first_h1` in isolation covering
a simple first-line H1, an H1 after leading blank lines/preamble text, an H1 correctly found
after a preceding H2 (H2 not mistaken for H1), no H1 anywhere (returns `None`, both with only an
H2 and with only plain paragraphs), an H2-only heading not matching as H1, and an H1 correctly
found after a leading YAML frontmatter block. Checked `tests/general/prompts/test_confluence_update.py`
(no "title" references at all -- prompt-registration/text tests only, left unchanged as expected). Quality gate: full `unittest` suite (3302 tests, `OK`), `ruff format --check` (already
formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60`
(no findings) -- all green, before and after doc regeneration. `specmgr docs` regenerated
`docs/api/biz.dfch.specmgr.general.tools.confluence_update.md` (new `_extract_first_h1`
docstring entry plus the updated docstring/flow-step prose, expected drift); `specmgr mcp-docs`
regenerated `docs/MCP.md` (updated `confluence_update` tool description in both the summary
table and its detail section, expected drift). Quality gate re-run clean after both doc
regenerations. All three acceptance criteria (ACC-001/ACC-002/ACC-003) are now satisfied; this feature is
complete.

