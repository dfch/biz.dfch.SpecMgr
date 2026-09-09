---
classification: null
created: '2026-09-09 04:33:02.804+02:00'
id: feat-114-qa-introduction-any-markdown
status: planning
type: feat
updated: '2026-09-09 04:33:02.804+02:00'
version: 1.0.0
---

# Feature: QA `### Introduction` Accepts Any Markdown Content

## Plan

### Overview

QA's `### Introduction` section (`qa.models.v2.body.Introduction`) is
currently typed as `body: list[MarkdownParagraph] | None`, so only a run
of plain paragraphs parses successfully under that heading — a bullet
list, code block, block quote, etc. placed there fails to parse today
(a "leftover text" or "no match" `AssertionError`). This is a strict
relaxation (widening), not a tightening, of the schema: `RawRequirements`
and `MoreInformation` already accept arbitrary markdown verbatim as leaf
sections; `Introduction` is the only whole-section field in QA v2 typed
against the narrow `MarkdownParagraph` shape instead. `Introduction`'s
optional leading `<!-- ... -->` comment (inherited from
`MarkdownSection3WithComment`) must keep working exactly as today.

No existing test (positive or negative) exercises a non-paragraph
`### Introduction` body either way, so this change carries no regression
risk against a previously-pinned contract — confirmed by inspection of
`tests/qa/models/v2/test_body.py` and `tests/qa/tools/test_parse_qa.py`
before starting this feature.

### Requirements

- REQ-001: `Introduction.body` accepts any markdown content (paragraphs, lists, code blocks, block quotes, ...) verbatim, not just plain paragraphs.
- REQ-002: `Introduction`'s existing optional leading `comment` field (inherited from `MarkdownSection3WithComment`) continues to work unchanged.
- REQ-003: `Introduction.body` remains optional (`None`-able) exactly as today — an empty or comment-only `### Introduction` section stays legal; this feature does not newly require body content.
- REQ-004: The new `body` field's content is reachable through `model_dump()`/`model_dump_json()` (not just `str()`), matching every other opaque leaf field in this engine (`RawRequirements`, `MoreInformation`, `QaAnswer`, ...).
- REQ-005: The packaged `qa_schema.json` (both the `docs/` copy and the `qa/data/` package copy), `docs/api/` docstring exports, packaged `qa_example.md`/`qa_template.md`, and the `create_qa` prompt instructions all reflect the new shape.

### Acceptance Criteria

- [ ] ACC-001: A `### Introduction` section containing only plain paragraph(s) still parses and round-trips identically to today (no regression).
- [x] ACC-002: A `### Introduction` section containing a non-paragraph element (e.g. a bullet list, or a leading comment followed by a code block) parses and round-trips successfully.
- [x] ACC-003: A `### Introduction` section with only a leading comment and no further content still parses successfully with `body is None`.
- [x] ACC-004: `model_dump()` on a parsed QA document surfaces the `Introduction` body's real text content (not an empty object) for both a plain-paragraph and a non-paragraph body.
- [ ] ACC-005: The full test suite passes after every phase below, not just at the end.
- [ ] ACC-006: `ruff format --check`, `ruff check`, and `vulture` all pass against the final state.
- [ ] ACC-007: `qa_schema.json` (both copies) and `docs/api/` are regenerated and committed in sync with the model change (no drift).

### Scope

#### Included

- `qa/models/v2/body.py`: new `IntroductionBody` leaf class; retyped `Introduction.body`; updated module docstring diagram.
- Test updates/additions in `tests/qa/models/v2/test_body.py` and `tests/qa/tools/test_parse_qa.py`.
- Regenerated `qa_schema.json` (both copies) and `docs/api/` / `docs/GENERATED.md`.
- `qa/data/qa_example.md` and `qa/data/qa_template.md`: demonstrate the new capability (comment + non-paragraph content under `### Introduction`).
- `qa/data/qa_create_instructions.md`: brief wording tweak.

#### Explicitly Out Of Scope

- Any change to `Introduction.comment`'s own behavior or type.
- Making `Introduction.body` mandatory (explicitly decided against — see Decisions Made).
- Any change to `RawRequirements`, `MoreInformation`, `QaAnswer`, or any other QA v2 field.
- Any change to the shared `models/md` engine itself (per this subpackage's established "zero changes to the shared engine" convention, already followed by `QaAnswer`/`QaQuestionAnswer`).
- A new `.specmgr/feat/` retroactive edit of the closed `feat-14-qa-v2-adjacent-qa` feature (this feature stands on its own).

### Dependencies

#### Depends On

- feat-14-qa-v2-adjacent-qa: the QA v2 schema this feature amends.

#### Blocks

- None known.

### Design Notes

`IntroductionBody(MarkdownStr)` is a leaf class (no declared fields) that applies no `@markdown` type/tag restriction of its own — unlike `MarkdownParagraph`/`MarkdownSection*`/`MarkdownComment`, each of which restricts `get_extent`'s match to one specific token type. Because of that, `IntroductionBody.get_extent`/`from_text` fall back to the unmodified `MarkdownStr` base implementation, which simply consumes everything remaining in the given text regardless of its shape — this is documented as the explicit reason that base-case behavior exists (`models/md/markdown_str.py`'s own `from_text` docstring). Since this field is always declared last (and alone, besides `comment`) on `Introduction`, "everything remaining" is exactly correct — no custom stop-condition override is needed, unlike `QaAnswer` (which does need one because further adjacent Q&A pairs can follow it within the same section).

`IntroductionBody` adds a `text` computed property (`return self._value`), mirroring `QaAnswer.text` verbatim. This is required, not cosmetic: `MarkdownStr` itself declares zero pydantic fields (`_value` is a private attribute, invisible to `model_dump()`), empirically confirmed via `MarkdownStr().model_dump() == {}`. Without a `text` computed property, a bare `MarkdownStr`-typed field would serialize to an empty `{}` object over `model_dump()`/`model_dump_json()` — exactly the MCP-transport path this server uses for every tool response — even though `str()` round-trips fine. Every existing opaque leaf class in this codebase (`MarkdownParagraph`, `MarkdownSection`, `MarkdownComment`, `MarkdownListItem`, `QaAnswer`) already carries this same three-line property for this exact reason.

None of the other existing concrete `models/md` leaf types can be reused for this field: `MarkdownSection3`/`MarkdownSection2` (used by `RawRequirements`/`MoreInformation`) require the text to start with a heading token, `MarkdownComment` requires an `html_block` comment token, `MarkdownParagraph` requires a `paragraph_open` token — none matches "a bullet list" or "a code block" sitting directly inside another section's body. Only the base, undecorated `MarkdownStr` has the required "unrestricted" `get_extent`.

`Introduction.body` stays `IntroductionBody | None` (optional, default `None`) — confirmed by direct testing against the current, pre-this-feature code that an empty or comment-only `### Introduction` already parses successfully today (`body is None`); this feature changes what is accepted when body is present, not whether it may be absent.

### Related Decisions

- feat-14-qa-v2-adjacent-qa (feat): the QA v2 schema `Introduction` is part of.

### Task List

#### Phase 1: Model change

- [x] Task 1.1: In `qa/models/v2/body.py`, drop the now-unused `MarkdownParagraph` import; add `MarkdownStr` to the `models.md` import; add `computed_field` to the `pydantic` import.
- [x] Task 1.2: Add `IntroductionBody(MarkdownStr)` with a `text` computed property (mirroring `QaAnswer.text`), per Design Notes.
- [x] Task 1.3: Retype `Introduction.body` from `list[MarkdownParagraph] | None` to `IntroductionBody | None` (`default=None` unchanged); update `Introduction`'s own docstring.
- [x] Task 1.4: Update the module-level docstring's ASCII diagram (`### Introduction` block: `{intro paragraphs}` → `{any markdown}`).
- [x] Task 1.5: Fix the now-broken existing tests to match the new scalar (not list) shape (see Design Notes).
- [x] Task 1.6: Regenerate build artifacts (schema + docs).
- [x] Task 1.7: Run the full test suite. Must pass before moving to Phase 2.

#### Phase 2: New positive/negative test coverage

- [x] Task 2.1: Add a test constructing/parsing an `Introduction` whose body is a non-paragraph element and asserting it round-trips successfully (ACC-002).
- [x] Task 2.2: Add/confirm a test asserting a comment-only `### Introduction` still parses with `body is None` (ACC-003).
- [x] Task 2.3: Confirm (add if missing) a `model_dump()` assertion covering the non-paragraph body case (ACC-004).
- [x] Task 2.4: Run the full test suite. Must pass before moving to Phase 3.

#### Phase 3: Packaged data files

- [x] Task 3.1: Update `qa/data/qa_example.md`'s `### Introduction` section to add a leading comment plus a short bullet list.
- [x] Task 3.2: Update `qa/data/qa_template.md`'s `### Introduction` placeholder wording.
- [x] Task 3.3: Brief wording tweak in `qa/data/qa_create_instructions.md`.
- [x] Task 3.4: Re-run `uv run --frozen specmgr docs` if needed.
- [x] Task 3.5: Run the full test suite. Must pass before moving to Phase 4.

#### Phase 4: Final verification

- [ ] Task 4.1: `uv run --frozen ruff format --check && uv run --frozen ruff check`.
- [ ] Task 4.2: `uv run --frozen vulture src/ whitelist.py --min-confidence 60`.
- [ ] Task 4.3: Run the full test suite one final time.
- [ ] Task 4.4: Review `git status`/`git diff` for completeness, then commit.

## Progress

### Current Status

**As of 2026-09-09**: Phase 1 (model change), Phase 2 (new
positive/negative test coverage), and Phase 3 (packaged data files)
complete. `Introduction.body` is now `IntroductionBody | None` (was
`list[MarkdownParagraph] | None`), both `qa_schema.json` copies and
`docs/api/` are regenerated, and new tests cover a bullet-list body, a
comment-plus-code-block body, a comment-only body (`body is None`), and
`model_dump()` surfacing non-paragraph body content. `qa_example.md`,
`qa_template.md`, and `qa_create_instructions.md` now demonstrate/document
the widened `### Introduction` shape. The full test suite is green (3353
tests, unchanged from the end of Phase 2 -- Phase 3 was a data-file-only
change, no new tests). Phase 4 (final verification) not yet started.

### Blockers

- None.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-09 - Phase 3 complete: packaged data files

Implemented Task 3.1-3.5. `qa/data/qa_example.md`'s `### Introduction` now
opens with the `<!-- filled in during the kickoff interview -->` comment
(the same comment text used throughout Phase 1/2's test fixtures, reused
here for consistency) followed by the existing prose, now ending in a short
bullet list breaking out the two elicitation sessions: two sessions with the
platform team, plus one safety-reviewer sign-off session focused
specifically on the cutover procedure -- demonstrating both a leading
comment and non-paragraph content in one realistic, still-readable example.
`qa/data/qa_template.md`'s `### Introduction` placeholder wording changed
from "Free-form prose framing the interview" to "Free-form markdown (prose,
lists, code blocks, ...) framing the interview", a brief tweak per the
task's own wording, with no added comment/list (kept as pure placeholder
"blind text", per `get_qa_template`'s own tool description).
`qa/data/qa_create_instructions.md`'s `### Introduction` bullet under
"Structure recap" got the identical brief wording tweak ("Free-form markdown
(prose, lists, code blocks, ...) framing the interview"), keeping the "who
was interviewed, when, and why" purpose guidance unchanged. Verified both
edited data files still parse successfully via `parse_qa` (direct Python
snippet) and are unchanged by `mdformat` (`specmgr_mdformat` returned
`False` for both, confirming they remain in the exact mdformat-normalized
form the parser's round-trip assertions expect); `qa_create_instructions.md`
is prompt text, not itself parsed by the QA parser, and was found to NOT
already be in strict mdformat-normalized form even before this edit
(`mdformat` reflows several of its long prose lines regardless of this
feature's change), so it was deliberately left un-reformatted beyond the one
intended wording tweak, to avoid bundling an unrelated, pre-existing
formatting drift into this feature's diff. `uv run --frozen specmgr docs`
produced no diff (expected for a pure data-file change with no docstring
changes). No test file was modified -- no existing test hardcodes the
previous `qa_example.md`/`qa_template.md` prose text, so none needed
updating. Full quality gate green: `ruff format --check`, `ruff check`,
`vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto
--cov=src --cov-report=` (3353 passed, unchanged from Phase 2's count).

#### 2026-09-09 - Phase 2 complete: new positive/negative test coverage

Implemented Task 2.1-2.4. Added `TestIntroductionAcceptsNonParagraphContent`
to `tests/qa/models/v2/test_body.py` with two tests
(`test_bullet_list_body_parses_and_round_trips`,
`test_comment_followed_by_code_block_body_parses_and_round_trips`) covering
both example shapes from the plan (ACC-002), each building a `## General`
section via `General.from_text(...)` (mirroring `_minimal_general()`'s
style) and asserting `introduction.body.text` contains the expected content
plus a byte-for-byte `str(sut) == text` round-trip. Added
`TestIntroductionCommentOnly.test_comment_only_introduction_parses_with_body_none`
confirming a comment-only `### Introduction` still parses with
`introduction.body is None` (ACC-003) -- no prior test covered this exact
case, so this was a genuine addition, not a confirmation of an existing
test. Added `test_model_dump_surfaces_non_paragraph_introduction_body_content`
to `tests/qa/tools/test_parse_qa.py` (alongside a new `_NON_PARAGRAPH_INTRO_DOC`
fixture constant, matching that file's existing `textwrap.dedent`/
`model_dump(mode="json")` idiom) asserting `model_dump()` surfaces a bullet
list's real text under `body["general"]["introduction"]["body"]["text"]`,
not an empty object (ACC-004) -- extending the same concern
`test_model_dump_surfaces_leaf_section_body_content` already covers for
other leaf fields. No production code was touched. Full quality gate green:
`ruff format --check`, `ruff check`, `vulture src/ whitelist.py
--min-confidence 60`, and `pytest -n auto --cov=src --cov-report=` (3353
passed, up from 3349 after Phase 1 -- exactly the 4 new tests added).

#### 2026-09-09 - Phase 1 complete: model change

Implemented Task 1.1-1.7: added `IntroductionBody(MarkdownStr)` (a leaf class
with a `text` computed property mirroring `QaAnswer.text`) to
`qa/models/v2/body.py`, retyped `Introduction.body` from
`list[MarkdownParagraph] | None` to `IntroductionBody | None`, dropped the
now-unused `MarkdownParagraph` import, updated the module docstring's ASCII
diagram (`{intro paragraphs}` -> `{any markdown}`), and fixed the two existing
tests that assumed `introduction.body` was a list
(`tests/qa/models/v2/test_body.py::TestGeneralIntroductionRawRequirements::test_parses_and_round_trips`
and
`tests/qa/tools/test_parse_qa.py::TestParseQaTool::test_model_dump_surfaces_markdownparagraph_backed_fields`)
to index the new scalar directly and expect the trailing newline
`MarkdownStr.text` preserves verbatim (`"Some intro text.\n"`, not
`"Some intro text."`). Regenerated both `qa_schema.json` copies
(`docs/qa_schema.json` and `src/biz/dfch/specmgr/qa/data/qa_schema.json`, via
`specmgr schema --type qa` and `specmgr schema --type qa --output-dir
src/biz/dfch/specmgr/qa/data`, mirroring the exact pre-commit hook commands)
and `docs/api/`/`docs/GENERATED.md` (via `specmgr docs`); confirmed
`specmgr mcp-docs` produces no diff. Full quality gate green: `ruff format
--check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and
`pytest -n auto --cov=src --cov-report=` (3349 passed).

#### 2026-09-09 02:32:25.000Z - Created

Feature folder created from GitHub issue #114, following a plan-mode design discussion that: (1) confirmed the change is a schema relaxation with no existing negative-test coverage to protect; (2) settled on keeping `Introduction.body` optional (not making it mandatory); and (3) settled on a dedicated `IntroductionBody` leaf class (comment stays, body becomes fully opaque) over either "drop comment entirely" or "restrict to paragraphs" alternatives.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-09 - Leave qa_create_instructions.md's pre-existing formatting drift untouched

Running `specmgr_mdformat` against `qa_create_instructions.md` after the
Phase 3 wording tweak reported a change, but diffing showed most of that
diff was pre-existing drift (added blank lines after headings, re-wrapped
long prose lines, a re-indented continuation line) unrelated to this
feature's edit -- confirmed by running the same `mdformat` pass against the
untouched, pre-edit file and observing the identical unrelated diff. Since
`qa_create_instructions.md` is prompt text consumed by the `create_qa` MCP
prompt, not a document parsed by the QA parser (unlike `qa_example.md`/
`qa_template.md`, whose round-trip assertions genuinely depend on staying
mdformat-normalized), there is no functional requirement for it to be
mdformat-clean. Chose to keep only the one intended wording tweak and leave
the pre-existing drift alone, rather than bundling an unrelated
reformatting into this feature's diff -- a future feature or a dedicated
cleanup pass can reformat this file on its own terms.

#### 2026-09-09 - Fix broken tests by expecting the exact raw text (with trailing newline), not `.strip()`

Widening `Introduction.body` to `IntroductionBody(MarkdownStr)` changes its
`text` computed property's value from `MarkdownParagraph.text`'s inline text
(no trailing newline for a one-line paragraph) to `MarkdownStr._value`'s
verbatim line-span capture, which does include the source's trailing
newline (`"Some intro text.\n"`, confirmed empirically against the pre-Phase-1
fixture). Chose to update the two affected assertions to expect that exact
verbatim string rather than reach for `.strip()`/`assertIn()` (the pattern
`RawRequirements`/`QaAnswer`'s own existing tests use elsewhere in the same
file), since these two spots were originally written as exact-equality
checks and `IntroductionBody.text`'s contract -- like `QaAnswer.text`'s -- is
"the raw markdown text verbatim", trailing newline included; changing the
assertion style itself was out of scope for a pure shape fix.

#### 2026-09-09 02:32:25.000Z - Keep Introduction.body optional, do not tighten to mandatory

While designing this feature, it was noted that `Introduction.body` was already optional (`None`-able) even under the old, more restrictive `list[MarkdownParagraph]` typing — confirmed by testing against the pre-feature code that an empty or comment-only `### Introduction` already parses successfully today. Explicitly decided to preserve this exact optionality rather than bundling a tightening (mandatory body) into what is otherwise a pure relaxation — keeps the change minimal and focused.

#### 2026-09-09 02:32:24.000Z - Add a dedicated IntroductionBody leaf class instead of a bare MarkdownStr field

Considered declaring `Introduction.body` directly as `MarkdownStr | None` without a dedicated subclass. Rejected because `MarkdownStr` declares no pydantic fields at all (`_value` is a private attribute), so `model_dump()` on a bare `MarkdownStr` instance returns `{}` — verified empirically. Every other opaque leaf class in this codebase (`MarkdownParagraph`, `MarkdownSection`, `MarkdownComment`, `MarkdownListItem`, `QaAnswer`) already solves this the same way: a minimal subclass adding only a `text` computed property. `IntroductionBody` follows that same, already-established precedent.

### Related PRs / Commits

- [Issue #114](https://github.com/dfch/biz.dfch.SpecMgr/issues/114): tracking issue for this feature.

### More Information

None.
