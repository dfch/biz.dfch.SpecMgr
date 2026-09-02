---
classification: null
created: '2026-09-03 00:03:19.829+02:00'
id: feat-73-74-76
status: planning
type: feat
updated: '2026-09-03 00:06:13.219+02:00'
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

### Task List

#### Phase 1: NOTICE License Audit (#73)

- [x] Task 1.1: List every direct 3rd-party library dependency from pyproject.toml.

- [x] Task 1.2: For each dependency, verify NOTICE lists the correct license type and attribution text (using #47/mdformat-simple-breaks as the worked example).

- [x] Task 1.3: Fix any discrepancies found in NOTICE.

#### Phase 2: sysrs Config/Gap Analysis (#74)

- [x] Task 2.1: Add sysrs to specmgr://config.

- [x] Task 2.2: Compare sysrs's tools/resources/prompts against every other whole-body domain (req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr) to find other missing common functions.

- [x] Task 2.3: Write up the gap list (in Design Notes or a follow-up feature).

- [x] Task 2.4: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` and confirm all pass.

#### Phase 3: Confluence Page Title Fix (#76)

- [x] Task 3.1: In specmgr_confluence_update, parse the first H1 heading from the source markdown file.

- [x] Task 3.2: Set the Confluence page's title field to that H1 text when updating the page body via the REST API.

- [x] Task 3.3: If no H1 is present, leave the existing page title untouched.

- [x] Task 3.4: Add/adjust tests covering both the H1-present and no-H1 cases.

- [x] Task 3.5: Run the full test suite (`uv run --frozen python -m unittest discover -v -s tests -t . -p "test_*.py"`) plus `ruff format --check`/`ruff check`/`vulture` and confirm all pass.

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
unchanged"/"unchanged title", now corrected).

`tests/general/tools/test_confluence_update.py`: renamed
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
(no "title" references at all -- prompt-registration/text tests only, left unchanged as expected).

Quality gate: full `unittest` suite (3302 tests, `OK`), `ruff format --check` (already
formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60`
(no findings) -- all green, before and after doc regeneration. `specmgr docs` regenerated
`docs/api/biz.dfch.specmgr.general.tools.confluence_update.md` (new `_extract_first_h1`
docstring entry plus the updated docstring/flow-step prose, expected drift); `specmgr mcp-docs`
regenerated `docs/MCP.md` (updated `confluence_update` tool description in both the summary
table and its detail section, expected drift). Quality gate re-run clean after both doc
regenerations.

All three acceptance criteria (ACC-001/ACC-002/ACC-003) are now satisfied; this feature is
complete.

#### 2026-09-03 14:00:00.000+02:00 - Phase 2 complete: sysrs added to specmgr://config; gap analysis found no other gaps (#74)

Added `sysrs` to `specmgr://config`: `general/resources/config.py` now imports `sysrs_base_dir` from
`sysrs.tools._paths` and adds a `"sysrs": DomainConfig(base_dir=..., env_var=DOCS_DIR_ENV_VAR,
env_var_set=docs_dir_set)` entry to the `domains` dict, mirroring the existing `"vcr"` entry's exact
shape (shared `SPECMGR_DOCS_DIR` root env var). Updated the resource's `description=` string and the
`config_info()` docstring's domain-count prose from "twelve"/"ten...share" to
"thirteen"/"eleven...share", now listing `sysrs` explicitly. Also updated
`models/config_info.py`'s `DomainConfig.env_var` and `ConfigInfo.domains` docstrings to match (stale
"ten domains" / missing `"sysrs"` from the domain-name list). Updated
`tests/general/resources/test_config.py`'s `_ALL_DOMAINS`/`_DOCS_DIR_DOMAINS` module-level lists to
include `sysrs` (existing parametrized tests then cover it automatically; no new test cases needed).

Performed the full tools/resources/prompts/dispatch-tool gap analysis (Task 2.2) comparing `sysrs`
against every other whole-body domain, using `sop`/`vcr` as the closest dispatch-only baselines --
see the new "Design Notes" section above for the full write-up. Conclusion: the missing
`specmgr://config` entry was the *only* gap; `sysrs` was already fully wired into all four generic
dispatch tools (`update`/`set_status`/`set_classification`/`delete`), `_path_safety.py`'s
`_UUID_TYPES`, has all 7 tools/3 resources/2 prompts, `get_sysrs` already supports
`raw`/`offset`/`limit`, and its prompts already correctly reference `specmgr://iso25010`. No
follow-up feature needed for `sysrs` itself.

Quality gate: full `unittest` suite (3292 tests, `OK`), `ruff format --check` (already formatted),
`ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings) --
all green. `specmgr docs` regenerated `docs/api/biz.dfch.specmgr.general.resources.config.md` and
`docs/api/biz.dfch.specmgr.models.config_info.md` (docstring-count updates only, expected drift);
`docs/GENERATED.md` had no drift. Quality gate re-run clean after doc regeneration.

#### 2026-09-03 12:00:00.000+02:00 - Phase 1 complete: NOTICE license audit and corrections (#73)

Verified all 10 direct dependencies from `pyproject.toml` (base: `pydantic`, `python-dotenv`, `markdown-it-py`, `python-frontmatter`, `mdformat`, `mdformat-simple-breaks`; `cli` extra: `typer`, `rich`; `mcp` extra: `mcp`, `httpx`) against each package's installed `*.dist-info/licenses/LICENSE*` file (source of truth, not guesswork). `test`/`dev` extras were confirmed out of scope by NOTICE's own header wording ("this project depends on the following third-party libraries") and existing convention (only base + `cli` + `mcp` extras were ever listed).

Findings and fixes in `NOTICE`:
- `pydantic`: copyright line was stale ("Samuel Colvin and contributors") -- corrected to the actual current holder, "Pydantic Services Inc. and individual contributors" (with the "2017 to present" year range from the shipped LICENSE file).
- `python-dotenv`: copyright line was wrong (attributed only to "Saurabh Kumar", omitting the "Ted Tieken"/"Jacob Kaplan-Moss" original django-dotenv authors) and the reproduced license body's disclaimer used a generic numbered-list BSD-3-Clause template instead of python-dotenv's actual bullet-list wording ("Neither the name of django-dotenv..." not "...the copyright holder..."). Both corrected to match the installed LICENSE file verbatim.
- `typer`: copyright line was missing its year (2019) present in the actual LICENSE file -- added.
- `rich`: copyright line was missing its year (2020) present in the actual LICENSE file -- added.
- `mcp` / `mcp-types`: copyright line was materially wrong -- NOTICE attributed it to "Model Context Protocol, a Series of LF Projects, LLC." but the package's actual shipped LICENSE file reads "Copyright (c) 2024 Anthropic, PBC". Corrected.
- `markdown-it-py` and `python-frontmatter`: already correct, verified verbatim against their installed LICENSE files, no changes needed.
- Added missing entries for the three direct dependencies NOTICE omitted entirely: `mdformat` (MIT, Copyright (c) 2021 Taneli Hukkinen, https://github.com/hukkin/mdformat), `mdformat-simple-breaks` (MIT, Copyright (c) 2023 Carles Sala, https://github.com/csala/mdformat-simple-breaks -- this is the #47 worked example the issue names, and it had never been added to NOTICE when the dependency was introduced), and `httpx` (the `mcp` extra's other runtime dependency, `optional "mcp" extra` annotation like `mcp` itself) -- NOTE: `httpx` is BSD-3-Clause, copyright Encode OSS Ltd (2019), NOT MIT as initially assumed; verified against its shipped `LICENSE.md`.

Confirmed via `git grep -rln NOTICE` that no test, CI workflow, or config file depends on NOTICE's exact content (only documentation/changelog references exist) -- this phase required no test run, matching the plan's Phase 1 scope (no Task 1.4 quality-gate task).

#### 2026-09-03 00:06:00.000+02:00 - Added final quality-gate tasks to Phase 2 and Phase 3

Added Task 2.4 and Task 3.5, each requiring a full test-suite run (unittest) plus ruff/vulture checks at the end of the code-touching phases (sysrs config change and Confluence title fix). Phase 1 (NOTICE audit) is documentation-only and was left without a test-run task.

#### 2026-09-02 12:00:00.000Z - Created

Feature created to track GitHub issues #73 (NOTICE license audit), #74 (sysrs config/gap analysis), and #76 (Confluence page title fix). No implementation started yet.
