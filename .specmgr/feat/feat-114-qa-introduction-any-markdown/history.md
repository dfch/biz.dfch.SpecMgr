# History: QA `### Introduction` Accepts Any Markdown Content

#### 2026-09-09 03:45:00.000Z - Phase 3 complete: packaged data files

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
`vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto --cov=src --cov-report=` (3353 passed, unchanged from Phase 2's count).


#### 2026-09-09 03:20:00.000Z - Phase 2 complete: new positive/negative test coverage

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
`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and `pytest -n auto --cov=src --cov-report=` (3353
passed, up from 3349 after Phase 1 -- exactly the 4 new tests added).


#### 2026-09-09 02:55:00.000Z - Phase 1 complete: model change

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
`specmgr schema --type qa` and `specmgr schema --type qa --output-dir src/biz/dfch/specmgr/qa/data`, mirroring the exact pre-commit hook commands)
and `docs/api/`/`docs/GENERATED.md` (via `specmgr docs`); confirmed
`specmgr mcp-docs` produces no diff. Full quality gate green: `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and
`pytest -n auto --cov=src --cov-report=` (3349 passed).


#### 2026-09-09 02:32:25.000Z - Created

Feature folder created from GitHub issue #114, following a plan-mode design discussion that: (1) confirmed the change is a schema relaxation with no existing negative-test coverage to protect; (2) settled on keeping `Introduction.body` optional (not making it mandatory); and (3) settled on a dedicated `IntroductionBody` leaf class (comment stays, body becomes fully opaque) over either "drop comment entirely" or "restrict to paragraphs" alternatives.
