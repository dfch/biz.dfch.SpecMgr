# History: License Audit, sysrs Config Gaps, and Confluence Page Title Fix (issues #73/#74/#76)

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
include `sysrs` (existing parametrized tests then cover it automatically; no new test cases needed). Performed the full tools/resources/prompts/dispatch-tool gap analysis (Task 2.2) comparing `sysrs`
against every other whole-body domain, using `sop`/`vcr` as the closest dispatch-only baselines --
see the new "Design Notes" section above for the full write-up. Conclusion: the missing
`specmgr://config` entry was the *only* gap; `sysrs` was already fully wired into all four generic
dispatch tools (`update`/`set_status`/`set_classification`/`delete`), `_path_safety.py`'s
`_UUID_TYPES`, has all 7 tools/3 resources/2 prompts, `get_sysrs` already supports
`raw`/`offset`/`limit`, and its prompts already correctly reference `specmgr://iso25010`. No
follow-up feature needed for `sysrs` itself. Quality gate: full `unittest` suite (3292 tests, `OK`), `ruff format --check` (already formatted),
`ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60` (no findings) --
all green. `specmgr docs` regenerated `docs/api/biz.dfch.specmgr.general.resources.config.md` and
`docs/api/biz.dfch.specmgr.models.config_info.md` (docstring-count updates only, expected drift);
`docs/GENERATED.md` had no drift. Quality gate re-run clean after doc regeneration.


#### 2026-09-03 12:00:00.000+02:00 - Phase 1 complete: NOTICE license audit and corrections (#73)

Verified all 10 direct dependencies from `pyproject.toml` (base: `pydantic`, `python-dotenv`, `markdown-it-py`, `python-frontmatter`, `mdformat`, `mdformat-simple-breaks`; `cli` extra: `typer`, `rich`; `mcp` extra: `mcp`, `httpx`) against each package's installed `*.dist-info/licenses/LICENSE*` file (source of truth, not guesswork); `test`/`dev` extras were confirmed out of scope by NOTICE's own header wording ("this project depends on the following third-party libraries") and existing convention (only base + `cli` + `mcp` extras were ever listed). Findings and fixes in `NOTICE`: `pydantic`'s copyright line was stale ("Samuel Colvin and contributors") -- corrected to the actual current holder, "Pydantic Services Inc. and individual contributors" (with the "2017 to present" year range from the shipped LICENSE file); `python-dotenv`'s copyright line was wrong (attributed only to "Saurabh Kumar", omitting the "Ted Tieken"/"Jacob Kaplan-Moss" original django-dotenv authors) and its reproduced license body's disclaimer used a generic numbered-list BSD-3-Clause template instead of python-dotenv's actual bullet-list wording ("Neither the name of django-dotenv..." not "...the copyright holder...") -- both corrected to match the installed LICENSE file verbatim; `typer`'s copyright line was missing its year (2019) present in the actual LICENSE file -- added; `rich`'s copyright line was missing its year (2020) present in the actual LICENSE file -- added; `mcp` / `mcp-types`' copyright line was materially wrong -- NOTICE attributed it to "Model Context Protocol, a Series of LF Projects, LLC." but the package's actual shipped LICENSE file reads "Copyright (c) 2024 Anthropic, PBC" -- corrected; `markdown-it-py` and `python-frontmatter` were already correct, verified verbatim against their installed LICENSE files, no changes needed; and missing entries were added for the three direct dependencies NOTICE omitted entirely: `mdformat` (MIT, Copyright (c) 2021 Taneli Hukkinen, https://github.com/hukkin/mdformat), `mdformat-simple-breaks` (MIT, Copyright (c) 2023 Carles Sala, https://github.com/csala/mdformat-simple-breaks -- this is the #47 worked example the issue names, and it had never been added to NOTICE when the dependency was introduced), and `httpx` (the `mcp` extra's other runtime dependency, `optional "mcp" extra` annotation like `mcp` itself) -- NOTE: `httpx` is BSD-3-Clause, copyright Encode OSS Ltd (2019), NOT MIT as initially assumed; verified against its shipped `LICENSE.md`. Confirmed via `git grep -rln NOTICE` that no test, CI workflow, or config file depends on NOTICE's exact content (only documentation/changelog references exist) -- this phase required no test run, matching the plan's Phase 1 scope (no Task 1.4 quality-gate task).


#### 2026-09-03 00:06:00.000+02:00 - Added final quality-gate tasks to Phase 2 and Phase 3

Added Task 2.4 and Task 3.5, each requiring a full test-suite run (unittest) plus ruff/vulture checks at the end of the code-touching phases (sysrs config change and Confluence title fix). Phase 1 (NOTICE audit) is documentation-only and was left without a test-run task.


#### 2026-09-02 12:00:00.000Z - Created

Feature created to track GitHub issues #73 (NOTICE license audit), #74 (sysrs config/gap analysis), and #76 (Confluence page title fix). No implementation started yet.
