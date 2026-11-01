# History: Actionable Validation Errors Across All Document Types

#### 2026-09-01 23:59:00.000Z - Phase 4 Tasks 4.1-4.3 (Verify and Close) completed
Implemented Tasks 4.1-4.3 (Task 4.4 -- the GitHub comment, ACC walk, and marking the feature
`done` -- is explicitly reserved for the orchestrator and was left untouched).
Task 4.1 (REQ-007/ACC-005): new file `tests/regression/test_issue_27.py` (plus
`tests/regression/__init__.py`), 6 tests, reproducing the two known triggers end to end through
`validate_tsk`, `create_tsk`, and the generic `update` tool (`type="tsk"`):
GitHub issue #27's own minimal repro body (fetched verbatim via `gh issue view 27 --json
  body` -- a `tsk` checklist with a bare `<domain>` token in one item's text plus a valid
  `## Recent Updates` entry) is used byte-for-byte as `_ISSUE_27_BODY`. Each test asserts the
  surfaced `AssertionError` contains the raw-HTML rejection's cause + fix-hint substrings
  (`"raw HTML is not permitted"`, `"html_inline '<domain>'"`, `"wrap it in a code span"`,
  `"write it as an HTML comment"`). The `create_tsk`/`update` variants use a valid seed body
  identical except the token is wrapped in backticks (the issue's own documented workaround),
  so `create_tsk` succeeds first and the offending body is introduced via `update`.
feat-7 Task 0.29's trigger: that feature's own README (Background, Task 0.29) preserves only
  one literal fragment of the original TSK document (id `952d39e5-3b79-4389-bc71-a4fe8ca85cd3`,
  itself not recoverable from repo history) -- `"+ group-block style as final..."`. `_FEAT_7_
  TASK_0_29_BODY` is therefore a realistic reconstruction (a plausible `## Recent Updates` entry
  paragraph) embedding that exact fragment as its offending continuation line, not a verbatim
  original document -- called out in the test file's own module docstring, not silently
  presented as verbatim. Each test asserts the "text left over" `AssertionError` contains the
  stray-list-marker cause + fix-hint substrings (`"text left over after processing all
  fields"`, `"a line starting with '-', '*', or '+' begins a new"`, `"CommonMark list"`,
  `"remove the marker or indent the line"`). The `create_tsk`/`update` variants use a valid seed
  body where the same paragraph is joined onto one line (no leading `+`).
All assertions use `assertIn` against the cause/fix substrings (not full exact-string pins --
that is `tests/models/md/test_validation_error_baseline.py`'s job), and do not re-assert the
domain/tool prefix (already covered by Phase 3's `tests/general/tools/test_error_context.py`).
Task 4.2: full quality gate run and green -- `ruff format --check` (1484 files already
formatted), `ruff check` (all checks passed), `vulture src/ whitelist.py --min-confidence 60`
(clean), full `unittest discover` (2787 tests, up from 2781, OK -- the +6 delta is exactly this
phase's new regression tests, zero regressions elsewhere).
Task 4.3: `specmgr docs` and `specmgr mcp-docs` regenerated `docs/api/`, `docs/GENERATED.md`
(only the "Test files: 323 -> 324" count changed), and `docs/MCP.md` (no diff -- Phase 3 already
left it current); both commands are idempotent on a second run. Added a new `AGENTS.md`
paragraph (after the "Still genuinely missing" list, before the `adr-tool-plan.md` §10
pointer sentence) documenting that every `parse_<d>`/`create_<d>`/`validate_<d>` and the
generic `update`/`set_status` tools' error messages now carry field-path/line/domain/tool
context -- no pre-existing AGENTS.md language described these messages as unhelpful/
unenriched, and no AGENTS.md text referenced feat-7 Task 0.29 as still-open, so nothing needed
correcting, only the new paragraph was added.

#### 2026-09-01 23:30:00.000Z - Phase 3 (Tool Boundary) completed
Implemented Tasks 3.1-3.4. New shared module: `src/biz/dfch/specmgr/models/md/_errors.py`
(Task 3.1), exporting `wrap_tool_errors(domain, tool, *, channel=None, also_catch=())` -- a
`@contextlib.contextmanager`-based context manager (chosen over a decorator since most tools
need to wrap only *one* inner call, not their entire body -- e.g. every `validate_<d>` has an
early `ValueError` shape-guard before the wrapped call that must NOT gain the prefix) -- plus
two channel-label constants, `BODY_CHANNEL = "body"` and `FRONTMATTER_CHANNEL = "frontmatter"`.
On a caught exception it re-raises the exact same runtime type with an enriched message,
reusing Phase 1/2's own two reconstruction techniques: message-only reconstruction
(`type(error)(f"{label}: {error}")`) for `AssertionError` and any `also_catch` type (both take
a single message-argument constructor), and `pydantic_core.ValidationError.from_exception_data`
(the same technique `models/md/_frontmatter_parse.py`'s own
`enrich_frontmatter_validation_error` uses) for `pydantic.ValidationError`, prefixing each
per-field message individually. `yaml.YAMLError` is reconstructed the same
`yaml.error.Mark`-preserving way Phase 2 does, except only the `context` field (the first line
`MarkedYAMLError.__str__` renders) is prefixed -- the marks themselves stay exactly as Phase 2
already remapped them (document-relative), never touched again here. The label itself is
`f"{domain} {tool}"`, optionally suffixed `f" ({channel})"` when a channel is knowable in
advance at that call site.
Example messages (before -> after, issue #27's own bare `<domain>` repro): `create_tsk`/
`update(type="tsk")` on a checklist item containing a bare `<domain>` token (`AssertionError`,
before: ```"raw HTML is not permitted in a parsed document at line 3 (relative to this text's
own numbering): html_inline '<domain>'; fix: wrap it in a code span (e.g. `` `<domain>` ``) or
write it as an HTML comment (e.g. `` <!-- <domain> --> ``) instead"``` -- Phase 1's own engine
message, still missing which *tool*/*domain* raised it -- after, `create_tsk`:
`"tsk create_tsk (body): raw HTML is not permitted ... (same detail)"`; after, the generic
`update` tool: `"tsk update (body): raw HTML is not permitted ... (same detail)"`). `req`'s
out-of-vocabulary `## Level` field (`pydantic.ValidationError`, a `create_req`/`validate_req`
body-only failure): before, the bare pydantic message (`"Value error, value must match pattern
'^(MUST|SHOULD|MUST NOT|SHOULD NOT|MAY)$', got 'NOT-A-VALID-LEVEL'"`); after: `"req create_req
(body): Value error, value must match pattern '^(MUST|SHOULD|MUST NOT|SHOULD NOT|MAY)$', got
'NOT-A-VALID-LEVEL'"`.
Applied to all 35 `parse_<d>`/`create_<d>`/`validate_<d>` files that actually exist on disk (11
`parse_<d>`: `dec`/`feat`/`gol`/`prb`/`qa`/`req`/`rsk`/`sop`/`tsk`/`uc`/`vcr`; 12 `create_<d>`/12
`validate_<d>` each: the same 11 plus `adr`) -- see Decisions Made for the tool-count
reconciliation against Task 3.2's own (reversed) literal wording -- plus `general/tools/
update.py`'s 11 per-domain adapters (`_update_<d>`, both the whole-body and range branches) and
`general/tools/set_status.py`'s 12 per-domain adapters (`_set_status_<d>`, wrapping the
`XFrontmatter(**fm_data)`/ADR's `mutations.set_status(...)` reconstruction). ADR's `create_adr`/
`validate_adr` (its own bespoke shape -- see Decisions Made) round out the 35+2 = 37 touched
tool files. Every touched tool's docstring gained a `Raises` section (Task 3.3; none of the 35
domain tool files had one before this phase -- they only described the two channels in prose)
naming the enriched channels and pointing at `wrap_tool_errors`.
New tests: `tests/models/md/test_errors.py` (14 tests, unit-level coverage of
`wrap_tool_errors` itself: all three channels, `also_catch`, pass-through of unrelated
exceptions) and `tests/general/tools/test_error_context.py` (7 tests, Task 3.4/ACC-003:
`create_tsk`/`create_req`, `validate_tsk`/`validate_req`, the generic `update` adapter for both
domains, and one `set_status` case, each asserting the surfaced exception string contains the
domain + tool label). Quality gate: `ruff format --check` (clean, 1481 files), `ruff check`
(clean), `vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest discover`
(2781 tests, up from 2760, OK -- zero exception-type regressions, ACC-004 preserved).

#### 2026-09-01 21:15:00.000Z - Phase 2 (Frontmatter and Value Channels) completed
Implemented Tasks 2.1-2.3. New shared module:
`src/biz/dfch/specmgr/models/md/_frontmatter_parse.py` (deliberately not `_errors.py`, which
Phase 3's Task 3.1 reserves), holding `frontmatter_opening_line()` (the block-relative ->
document-relative line-offset math), `enrich_frontmatter_yaml_error()` (Task 2.1),
`enrich_frontmatter_validation_error()` (Task 2.2), and the composed convenience entry point
`parse_frontmatter()` that every domain parser now calls in place of its previous bare
`frontmatter.loads(text)` / `SomeFrontmatter.model_validate(...)` pair. All twelve domains'
`parser.py` modules were updated to call it: `req`, `uc` (both `v1` and `v2`), `tsk`, `qa`,
`prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`, and ADR's `models/adr/v1/parser.py` — the
`import frontmatter` line moved out of every one of those twelve files into the new shared
module, since `parse_frontmatter` now owns that call.
Remap math (Task 2.1): `frontmatter.loads`/`frontmatter.parse` call `text.strip()` before
splitting on the `---` boundary via `re.compile(r"^-{3,}\s*$", re.MULTILINE).split(text, 2)`,
so PyYAML only ever sees the extracted YAML substring (`fm`), whose own `mark.line` (0-based)
is relative to that substring, not the document. Verified empirically (not guessed) against
`python-frontmatter`'s actual installed source
(`.venv/.../frontmatter/__init__.py`/`default_handlers.py`): the opening `---` delimiter is
always the *stripped* text's own line 1 (frontmatter detection requires the boundary regex to
match at position 0), so `document_line = mark.line + opening_line`, where
`opening_line = 1 + count("\n", leading_whitespace)` and `leading_whitespace` is whatever
`str.lstrip()` would remove from the *original*, unstripped input. Worked example: for
`text = "\n\n---\nid: tsk-1\nstatus: [unterminated\n---\nbody\n"` (two leading blank lines),
PyYAML's own `ParserError` reports block-relative `context_mark.line=1`/`problem_mark.line=2`
(0-based; "line 2"/"line 3" in its own 1-based display) for the two marks around
`status: [unterminated`/the immediately-following `---` line; `opening_line = 1 + 2 = 3`
(the *document*-relative 1-based line of the opening `---`), so the corrected document lines
are `1+3=4`/`2+3=5` (0-based) i.e. document lines 5/6 in PyYAML's own 1-based display —
verified directly against the real 1-based document line numbers of those two source lines.
Implementation only rewrites each `yaml.error.Mark`'s `name` (to `"the frontmatter block"`,
replacing `"<unicode string>"`) and `line` (shifted by `opening_line - 1`); `column`/`buffer`/
`pointer` are left untouched, so PyYAML's own snippet extraction (which walks `buffer`/
`pointer`, not `line`) and its own `context`/`problem` detail strings are carried alongside the
corrected location unchanged, not replaced by it, per the plan's explicit instruction. The
same-type re-raise is `type(error)(context=..., context_mark=<remapped>, problem=...,
problem_mark=<remapped>, note=...)`, since every `MarkedYAMLError` subclass (`ParserError`,
`ScannerError`, ...) inherits that exact constructor signature unchanged from PyYAML's own
`yaml.error.MarkedYAMLError` — verified via `inspect.getsource`, not assumed.
`pydantic.ValidationError` message enrichment (Task 2.2, the open design question the plan
flagged): investigated `pydantic_core.PydanticCustomError` +
`pydantic.ValidationError.from_exception_data(title, line_errors)` (verified: `pydantic.
ValidationError` *is* `pydantic_core._pydantic_core.ValidationError` in pydantic 2.13 -- not a
separate re-implementation -- so constructing one via `from_exception_data`, its own public
classmethod constructor, produces the exact same runtime type as the one
`model_validate` raised, satisfying REQ-006's letter, not just its spirit). For each of the
original error's own `.errors()` entries, a new `InitErrorDetails` is built with
`type=PydanticCustomError("frontmatter_value_error", <our enriched message>)` (a made-up type
tag, not one of pydantic's own recognized ones, which is exactly why the enriched message
renders with no unrelated `https://errors.pydantic.dev/...` documentation-link suffix
appended) and the original `loc`/`input` preserved; `ValidationError.from_exception_data(error.
title, line_errors)` then produces the re-raiseable replacement. No tradeoff or limitation was
hit in the end -- the resulting object passes `isinstance(result, pydantic.ValidationError)`
and `type(result) is type(original)` (both asserted directly in
`tests/models/md/test_frontmatter_errors.py::TestEnrichFrontmatterValidationError::
test_preserves_the_exact_exception_type`), and `str(result)` shows exactly the composed
message with no residual pydantic boilerplate. See Decisions Made below for why this was
judged preferable to the alternatives the plan raised.
Each enriched validation message reads
`"{domain} frontmatter block, field '{field}' (document line {N}): {original pydantic msg}"`
(the `(document line {N})` clause omitted when the field cannot be located as a literal
top-level `key:` line in the frontmatter block, e.g. a `pydantic` "Field required" error for a
key that is simply absent) -- `{domain}` is a literal short code (`"tsk"`, `"req"`, ..., `"adr"`)
passed by each parser, not derived by introspecting the frontmatter class, since ADR's own
`AdrFrontmatter` has no `type` field to introspect at all (unlike every `MarkdownFrontmatter`
subclass) and a plain, explicit string keeps the twelve call sites uniform.
Files touched: `models/md/_frontmatter_parse.py` (new); all twelve domains' `parser.py`
(`req`, `uc/v1`, `uc/v2`, `tsk`, `qa`, `prb`, `gol`, `rsk`, `dec`, `sop`, `feat`, `vcr`,
`models/adr/v1`); `tests/models/md/test_validation_error_baseline.py` (the pinned
`TestFrontmatterYamlErrorBaseline` assertion updated from `"<unicode string>"` to `"the
frontmatter block"` -- exception type `yaml.parser.ParserError` unchanged, per this phase's own
"pin-then-enrich" instruction; `TestFrontmatterValidationErrorBaseline`'s `assertIn` check
needed no change, since the substring it already pinned remains a verbatim part of the new,
longer enriched message). New test file:
`tests/models/md/test_frontmatter_errors.py` (13 tests, Task 2.3) covering the remap math
directly (`frontmatter_opening_line`, including a two-leading-blank-line case), both enrichment
functions directly (type preservation, frontmatter-block naming, field/line composition, the
line-omitted branch, and a plain non-`Marked` `yaml.YAMLError` passthrough), and cross-domain
integration coverage through `parse_tsk`/`parse_req`/`parse_adr` (ACC-002 is satisfied by the
updated `TestFrontmatterYamlErrorBaseline` baseline test via `parse_tsk`, corroborated by this
new file's own `parse_adr`/`parse_req` cases). Quality gate: `ruff format --check` (clean),
`ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), full
`unittest discover` (2760 tests, up from 2747, OK).

#### 2026-09-01 19:45:00.000Z - Phase 1 (models/md Engine Messages) completed
Implemented Tasks 1.0-1.8 in one pass (pin-then-enrich collapsed into a single session rather
than per-task, since the whole phase was small enough to review as one diff -- see Decisions
Made). Files touched: `models/md/_markdown.py` (moved/renamed the existing snippet helper to
a shared, non-underscore-prefixed `snippet()`; added `not_in_mdformat_message()`/
`_first_differing_line()`; enriched `_assert_no_raw_html()`/`_raw_html_message()` with a line
reference — falling back to the nearest ancestor block token's own `.map` for a mapless nested
`html_inline` child — and the code-span/HTML-comment fix hint), `models/md/alias_match.py`
(added `describe_alias()`), `models/md/markdown_str.py` (added the `_path`/`_line`
`PrivateAttr`s; `_field_label()`/`_child_path()`/`_is_heading_type()`/`_no_match_message()`/
`_leftover_text_message()` helpers; threaded `_path`/`_offset` through `from_text`/
`process_field`/`process_list_field`, tracking the running line offset via an actual
before/after line-count delta rather than a summed `get_extent`, so per-item blank-line
elision in `process_list_field` never desynchronizes it), `models/md/markdown_section.py`
(added `_alias_mismatch_message()`; threaded `_path`/`_offset` through `from_text`),
`models/md/markdown_paragraph.py`/`markdown_list_item.py` (same threading), `models/md/markdown_comment.py`/`markdown_block_quote.py`/`markdown_code_block.py`/`markdown_section{1..6}_with_comment.py` (accept-and-forward `_path`/`_offset` for override-signature compatibility;
message fix only, no path tracking, since none of these are in Task 1.7's item list),
`tsk/models/v1/task_item.py`, `rsk/models/v1/assessment.py`, `vcr/models/v1/body.py`, `feat/models/v1/body.py` (Task 1.7's domain-level item-regex message enrichments). New tests:
`tests/models/md/test_validation_error_baseline.py` (10 tests, Task 1.0/ACC-001), `tests/models/md/test_error_messages.py` (16 tests, Task 1.8, including an end-to-end reproduction of
REQ-001's own `Task > RecentUpdates > UpdateEntry > content` worked example via a local
fixture tree), and one addition to `tests/tsk/models/v1/test_task_item.py` (the one Task 1.7
domain case actually reachable through normal parsing, since RSK/VCR/feat's analogous
computed-field raises are documented as unreachable once `match_alias` already enforces the
same heading at parse time). One pre-existing test
(`tests/qa/models/v2/test_parser.py::test_missing_elicitation_context_raises_the_same_structural_error_from_from_text`) asserted the *old* bare `Qa.elicitation_context: ...`
message content and was updated in place to assert `ElicitationContext` instead (exception
type unchanged, AssertionError; only the message content assertion changed, which is exactly
what this phase intentionally does — this is not the Task 1.0 baseline file, so it is not
itself part of the "pin-then-enrich" record, but is called out here for the same reason).
Quality gate: `ruff format --check` (clean), `ruff check` (clean), `vulture src/ whitelist.py --min-confidence 60` (clean), full `unittest discover` (2747 tests, OK). No `specmgr docs`/
`specmgr mcp-docs` regeneration run — that is Phase 4's Task 4.3, and no `models/md/__init__.py`
`__all__` export changed (the new helpers are internal).

#### 2026-09-01 14:30:47.000Z - Session wrap-up: Task 1.0 added; origin/dev merged
Added Task 1.0 (pin the current validation-error strings in a dedicated baseline test file before Phase 1's enrichments, so every message change becomes a reviewable diff); Task 1.1 now depends on Task 1.0. Merged `origin/dev` into this branch as `01e29a5` (pulls in `8e07594`, feat-40's docs-prune): no conflicts, working tree clean, and the incoming `tests/commands/test_docs.py` suite passes post-merge. Plan artifacts committed as `7aac697` (ccm-generated message). No implementation has started — the next step for the phase orchestrator is Phase 1, beginning with Task 1.0.

#### 2026-09-01 12:39:10.000Z - Phase 0 completed
Phase 0 (Decide and Record) is complete: Task 0.1 (this feature was created via `create_feat` and renamed to `feat-27-validation`), Task 0.2 (feat-7's Task 0.29 was annotated as subsumed, with a Recent Updates entry added to that file), and Task 0.3 (the three planning decisions were recorded in the Decisions Made section below). Per user direction, no implementation (Phases 1–4) has been started — this document remains the design and plan only.

#### 2026-09-01 11:56:45.000Z - Created
Created for GitHub issue #27; subsumes feat-7's not-started Task 0.29. Investigation and planning complete; decisions confirmed with the user.
