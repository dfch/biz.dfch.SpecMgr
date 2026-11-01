# History: Add artifact type "Verification Case Record" (VCR)

#### 2026-08-31T15:30:00.000Z - Phase 4 complete: cross-cutting registration; feature fully implemented end to end
Implemented Task 4.0 (the implicit prerequisite): wired `vcr/__init__.py`
to `from . import prompts, resources, tools`, mirroring `dec/__init__.py`
file-for-file (module docstring adapted to VCR's actual schema/tools/
resources/prompts, including the `specmgr://dtais` cross-reference). This
resolves the non-blocking circular-import fragility noted in the Phase
2/3 Updates entries (`tests/vcr/tools/`/`tests/vcr/resources/`/
`tests/vcr/prompts/` now import cleanly in isolation too, not just as
part of the full suite).
Implemented Task 4.1: added `vcr` to `server.py`'s bottom import line
(alphabetical position, after `uc`) and updated its module docstring in
full -- three new `specmgr://vcr/schema`/`.../example`/`.../template`
resource lines (after `feat`'s, before `iso25010`), a new
`specmgr://dtais` resource line (between `feat/template` and
`iso25010`), a new VCR sentence in the "no `{id}`/no `list`" paragraph, a
new "Verification case record tools (`vcr/tools/`)" paragraph (before
"General tools"), a new "Verification case record prompts
(`vcr/prompts/`)" paragraph (before "General prompts"), the `general`
tools paragraph's domain-count language bumped (`update`: nine -> ten
whole-body domains, list gains `vcr`; `set_status`: "all ten domains" ->
"all eleven domains", list gains `vcr` right before `adr`), and the
closing "Modules are grouped domain-first" paragraph's three
domain-enumeration spots (the domain list, the import-list sentence, and
the tools/resources/prompts registration sentence) all gain `vcr`. Re-read
the entire docstring end to end afterward to confirm every VCR mention is
internally consistent with what Phases 1-3 actually built.
Implemented Task 4.2: added a new `vcr/` bullet to `AGENTS.md`'s Status
section, positioned after `feat/` and before `general/` (mirroring
`dec/`'s bullet shape/depth), describing VCR's actual schema (`##
Verifies` single-value cross-reference, `## Coverage` closed vocabulary,
`## Acceptance Criteria` DTAIS-classified `### AC-NNN` entries), its 8
tools, 3 resources, 2 prompts, generic `update`/`set_status` dispatch, and
the cross-cutting `specmgr://dtais` resource. Also updated every other
domain-enumeration spot in the same file: the `general/` bullet's own
resource list (`specmgr://version`, `specmgr://iso25010` -> gains
`specmgr://dtais` with a one-line description), the `general/tools/`
`update` sub-bullet's domain count/list (nine -> ten, gains `vcr`), the
`set_status` sub-bullet's domain count (ten -> eleven), the "The nine
`get_<d>` tools" sentence (-> "The ten `get_<d>` tools"), the "Still
genuinely missing" bullets (`validate_vcr` added to the `validate_*` list,
`delete_vcr` added to the `delete_*` list), the "each register `tools`,
`resources`, and `prompts`" summary bullet (gains `vcr`), and the MCP
server section's "imports every domain package" sentence (gains `vcr`).
Did not touch the "Models location" paragraph (VCR has no exception to
document) or any unrelated `.specmgr/feat/` references.
Implemented Task 4.3: added "Verification Case Record (VCR)" to root
`README.md`'s artifact list (alphabetically last, after "Use Case (UC)"),
following the same precedent `feat-31-feature`'s own Phase 5 used to add
"Feature (FEAT)" to that same list -- confirmed the "Environment
Variables" section itself needed no change (it is already fully generic,
`SPECMGR_DOCS_DIR`-based, with no per-domain enumeration). Updated
`.pre-commit-config.yaml`: inserted `vcr/models/v1` into all 10 existing
occurrences of the shared `files:` regex (the `specmgr-schema` hook plus
the 9 per-package `specmgr-schema-<domain>-package` hooks), right after
`uc/models/v2` and before the always-last `models/md`, added a new
`specmgr-schema-vcr-package` hook block (appended after
`specmgr-schema-feat-package`, VCR-ified: `vcr/data/vcr_schema.json`,
`specmgr://vcr/schema`, `docs/vcr_schema.json`, `--type vcr
--output-dir src/biz/dfch/specmgr/vcr/data`) with the same updated regex,
and updated the `specmgr-schema` hook's own description text to list
`vcr` last. Added a `CHANGELOG.md` `[Unreleased]` `### Added` entry
("Twelfth domain feature (VCR/Verification Case Record tooling)"),
mirroring the FEAT entry's structure/depth (models, tools, resources +
prompts, the cross-cutting `specmgr://dtais` resource, cross-cutting
registration, test coverage).
Implemented Task 4.4: ran `specmgr docs`, `specmgr mcp-docs`,
`specmgr adr-toc`, `specmgr schema`, and
`specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`,
each exactly twice -- the first run wrote real changes (`docs/GENERATED.md`,
`docs/api/README.md`, `docs/api/biz.dfch.specmgr.server.md`,
`docs/api/biz.dfch.specmgr.vcr.md`, `docs/MCP.md`, `docs/adr/README.md`
regenerated with no diff, every `docs/*_schema.json` and the packaged
`vcr/data/vcr_schema.json` copy reported "unchanged"), the second run
confirmed byte-identical output (`md5sum` comparison before/after for the
docs-generation commands; "unchanged"/no-diff for every schema and the
adr-toc command) -- no residual drift from this phase's own edits.
Manually read the generated `docs/MCP.md` and confirmed all 8 VCR tools
(`create_vcr`, `parse_vcr`, `list_vcr`, `get_vcr`, `get_vcr_example`,
`get_vcr_template`, `delete_vcr`, `validate_vcr`), all 3 VCR resources
(`specmgr://vcr/schema`/`.../example`/`.../template`), both VCR prompts
(`create_vcr`, `update_vcr`), and the standalone `specmgr://dtais`
resource appear with sensible, accurate descriptions. Quality gate green:
`ruff format --check` (1386 files already formatted), `ruff check` (all
checks passed), `vulture src/ whitelist.py --min-confidence 60` (no
output, no new whitelist entries needed), and the full `unittest` suite
(2452 tests, `OK` -- unchanged from Phase 3's count, since Phase 4 added
no new test files, only cross-cutting registration/docs). Updated the
Task List's Phase 4 checkboxes, walked every ACC-001..006 item and marked
all six `[x]` with a concrete justification citing the specific test
file/resource/tool proving each, and updated Current Status to reflect
the feature is now fully implemented end to end. Bumped this README's own
frontmatter `status` from `planning` to `done` and `version` from `1.0.0`
to `1.1.0`.

#### 2026-08-31T14:00:00.000Z - Phase 3 complete: `vcr/resources/`, `vcr/prompts/`, and the cross-cutting `specmgr://dtais` resource implemented
Implemented Task 3.1 (`vcr/resources/`): `vcr_schema.py`/`vcr_example.py`/
`vcr_template.py`, mirroring `dec/resources/`'s three files exactly
(rename `Dec`/`dec` -> `Vcr`/`vcr`, same URIs
`specmgr://vcr/schema`/`.../example`/`.../template`, same
`read_packaged_text` plumbing), plus `vcr/resources/__init__.py`. The
schema resource needed generator plumbing first: added
`generate_vcr_schema()` to `commands/schema.py` (mirroring
`generate_dec_schema` exactly) and a `"vcr"` entry to `_GENERATORS`
(alphabetically last, after `"uc"`), then ran
`specmgr schema --type vcr` (writes `docs/vcr_schema.json`) and
`specmgr schema --type vcr --output-dir src/biz/dfch/specmgr/vcr/data`
(writes the packaged copy `vcr/data/vcr_schema.json`) -- both exited 1
on first generation (new file) and 0 (unchanged) on every subsequent run,
confirmed once more at the very end of the phase.
Implemented Task 3.2 (`vcr/prompts/`): `create_vcr.py`/`update_vcr.py`,
mirroring `dec/prompts/create_dec.py`/`update_dec.py` exactly (same
`string.Template`/`$topic`/`$id`/`$instructions` substitution shape,
`raw=True` for `update_vcr`'s line-range line numbers, narration-only
contract -- never calls `TodoWrite`/`question`/`list_vcr`/`create_vcr`/
`get_vcr`/`update`/`set_status` itself), plus `vcr/prompts/__init__.py`.
Their packaged instructions
(`vcr/data/vcr_create_instructions.md`/`vcr_update_instructions.md`)
adapt `dec`'s exact structure/tone to VCR's own schema (`## Verifies` ->
`## Coverage` -> `## Acceptance Criteria` -> `## More Information` ->
`## Updates` section recap, the closed DTAIS method vocabulary spelled
out verbatim, VCR's own four-value `draft`/`progress`/`complete`/
`approved` status set instead of DEC's six-value set, and references to
the new `specmgr://dtais` resource for method-word guidance) -- including
DEC's own step-0 "check `list_vcr` for a near-duplicate first" convention
and the same tool-call-sequence ending in `create_vcr(content)`/optional
`validate_vcr(content, full=False)`.
Implemented Task 3.3 (the cross-cutting `specmgr://dtais` resource,
REQ-006): `general/data/general_dtais.md` filled in every placeholder
from the Design Notes' persisted draft outline -- a closed-vocabulary
bullet list of the five DTAIS words (verbatim, in the same order as
`vcr.models.v1.body`'s `_AC_HEADING_PATTERN` method group, confirmed by a
new test), a "## When to apply each method" section with concrete
per-method guidance (informed by well-established V&V domain knowledge:
`Demonstration` for observable behavior without a quantitative
threshold, `Test` for a quantitative/measured threshold, `Analysis` for
calculation/modeling/simulation or pre-existence-of-system verification,
`Inspection` for artifact/source examination without operating the
system, and this feature's own addition `Special` for external
certification/compliance/supplier-conformance sign-off), and a
"## Relationship to `## Coverage`" section explaining that `## Coverage`
is a roll-up of every acceptance criterion's verification status (not an
independent field), concretely illustrated with `example.md`'s own
AC-004-pending-`Special`-certification `partial`-coverage scenario.
`general/resources/dtais.py` copies the plan's persisted sketch verbatim
(only the `..tools`/`...server` relative-import order was corrected to
match this codebase's actual isort convention, confirmed against
`general/resources/iso25010.py`'s own ordering), and
`general/resources/__init__.py` now imports/exports `dtais` alongside
`iso25010`/`version` (alphabetical).
Added 52 new unit tests across `tests/vcr/resources/`
(`test_vcr_schema.py`/`test_vcr_example.py`/`test_vcr_template.py`,
mirroring `tests/dec/resources/`'s three files), `tests/vcr/prompts/`
(`test_create_vcr.py`/`test_update_vcr.py`, mirroring
`tests/dec/prompts/`'s two files), and
`tests/general/resources/test_dtais.py` (mirroring
`tests/rsk/resources/test_tara.py`'s structure: a regex asserting the
five documented method-word bullets exactly match the model's closed
DTAIS set in order, a per-word round-trip through
`AcceptanceCriterion.from_text` confirming every documented word is
genuinely accepted end to end, and a rejected-word case using
`"Certification"` -- VCR's own retired 5th-method name -- which raises
`AssertionError` (an `AcceptanceCriterion` alias mismatch, not
`pydantic.ValidationError`, unlike RSK's `Strategy`-based rejected-word
test) since `AcceptanceCriterion` is a regex-`@alias`-matched heading
class, not a `field_validator`-checked value). Quality gate green: `ruff
format --check`, `ruff check`, `vulture` (no new whitelist entries
needed), and the full `unittest` suite (2452 tests, `OK`, up from 2400)
all pass. Did not touch `server.py`, `AGENTS.md`, top-level `README.md`,
or `.pre-commit-config.yaml` -- all reserved for Phase 4; `vcr/__init__.py`
also stays untouched (still no `tools`/`resources`/`prompts` import), so
the same non-blocking circular-import fragility noted in the Phase 2
Updates entry (isolated `vcr.models.v1` imports before `general` has
fully loaded) still applies identically to the new `vcr/resources`/
`vcr/prompts` modules in isolation -- unaffected in the full repo-wide
suite, which is the specified quality gate.

#### 2026-08-31T12:30:00.000Z - Phase 2 complete: `vcr/tools/` implemented, generic `update`/`set_status` dispatch wired for `type="vcr"`
Implemented the full `vcr/tools/` package, mirroring `dec/tools/` file-for-
file: `_paths.py` (`VCR_TYPE_NAME`, `VcrNotFoundError`, `vcr_base_dir`/
`ensure_vcr_base_dir`/`iter_vcr_paths`/`find_vcr_path`, built on the shared
`general.tools._doc_paths` helpers, not a new dependency), `_lock.py`
(`vcr_lock`), `_io.py` (`read_vcr`/`load_by_id`), `_write.py`
(`write_vcr_file`), and the 8 standard `@mcp.tool()` wrappers: `create_vcr`
(fresh `uuid.uuid4()` id, `type="vcr"`, `status="draft"` always on create,
filename `vcr-{id}-{slug}.md`), `parse_vcr`, `get_vcr` (with `raw: bool =
False`), `get_vcr_example`/`get_vcr_template` (reading new packaged data),
`list_vcr` (paged from day one, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13),
`delete_vcr` (stub, always `NotImplementedError`), and `validate_vcr`
(disk-free/id-free dry run, `full: bool = False`). Copied the
already-finalized `example.md`/`template.md` planning drafts byte-for-byte
into `vcr/data/vcr_example.md`/`vcr_template.md`
(confirmed via `diff`: zero output) and declared the new
`"biz.dfch.specmgr.vcr"` package-data entry in `pyproject.toml`, inserted
after `"biz.dfch.specmgr.uc"` and before `"biz.dfch.specmgr.general"`,
matching every other domain's two-pattern (`data/*.md`, `data/*.json`)
shape even though no `vcr_schema.json` exists yet (Phase 3's job). Added
`vcr` as a tenth entry to the generic `update` tool's `_ADAPTERS` (new
`_update_vcr`, ported verbatim from `_update_dec`, appended last after
`feat`) and as an eleventh entry to `set_status`'s `_ADAPTERS` (new
`_set_status_vcr`, ported verbatim from `_set_status_dec` including the
`assert superseded_by is None` guard, inserted right after `feat` and
before the always-last `adr`), updating both tools' `Literal[...]`
parameter types, module/tool docstrings, and domain-count language
("nine"/"ten" -> "ten"/"eleven" as appropriate) throughout. Added 64 new
unit tests under `tests/vcr/tools/` (mirroring `tests/dec/tools/`'s 13
files file-for-file, using a minimal valid VCR body fixture: `## Verifies`
`## Coverage` + one `### AC-001 (Test): ...` entry, matching Phase 1's
own `test_parser.py` fixture shape) plus new `vcr` cases appended to the
table-driven `_CASES` lists in `tests/general/tools/test_update.py` (a
genuine duplicate-`### AC-001` `pydantic.ValidationError` field-error case,
mirroring DEC's own duplicate-`### Option` case) and
`test_set_status.py` (`valid_status="progress"`, `invalid_status="accepted"`
-- confirmed against `VcrFrontmatter`'s actual closed
`draft`/`progress`/`complete`/`approved` set before use), and updated both
files' registration/domain-count docstring language and the
`type` enum assertion in `test_update.py`'s
`test_update_registered_with_type_enum_and_optional_range`. Did not touch
`server.py`, did not create `vcr/resources`/`vcr/prompts`, and did not add
`vcr` to `server.py`'s import line -- all reserved for Phase 3/4;
`vcr/__init__.py` also stays untouched (still no `tools`/`resources`/
`prompts` import). Noted one non-blocking fragility for a future
implementer: since `vcr/__init__.py` does not yet bootstrap `vcr.tools`
(unlike every other already-registered domain's own `__init__.py`, which
bootstraps its `tools` package before anything else can reach its models
mid-import), running `tests/vcr/tools/` in isolation can hit a circular
import `ImportError` in files that import `vcr.models.v1` directly before
anything else has loaded `general.tools` (which now imports
`vcr.tools._io` et al., transitively re-entering `vcr.models.v1` while
it's still mid-import) -- resolved automatically once Phase 4 wires
`vcr/__init__.py` to import `tools`/`resources`/`prompts` the same way
`dec/__init__.py` already does; the full repo-wide suite (the specified
quality gate) is unaffected.
Quality gate green: `ruff format --check`, `ruff check`, `vulture` (no new
whitelist entries needed), and the full `unittest` suite (2400 tests,
`OK`, up from 2336) all pass.

#### 2026-08-31T11:15:00.000Z - Phase 1 correction: `AcceptanceCriterion.description` added; `example.md`/`template.md` now empirically validate end to end
Fixed a real specification error (not a genuine open design question) in
the schema landed by the previous Phase 1 entry: `AcceptanceCriterion` had
no field for the free-form descriptive paragraph that already-finalized
`example.md` demonstrates under 3 of its 4 `### AC-NNN (Method): ...`
headings (AC-001/002/004 each carry prose before/without `#### Test
Steps`; AC-003 has none). Added `description: MarkdownParagraph | None =
None` to `AcceptanceCriterion` in `vcr/models/v1/body.py`, declared before
`test_steps` (document order: heading -> optional description -> optional
`Test Steps`), both independently optional. While empirically re-validating
via a throwaway `/tmp` scratch script (per instruction) that called
`parse_vcr`/`Vcr.from_text` directly against `example.md`'s and
`template.md`'s actual body text, surfaced one more, closely-related gap
in scope of the same fix: `## Updates` in both drafts carries a permanent
leading "newest first" anchor `<!-- ... -->` comment (already noted as a
first-class, non-authoring-guidance structural anchor in this feature's
own Design Notes and clean-example-convention discussion), but `Updates`
was declared as a plain `MarkdownSection2` (DEC's own shape, whose
`dec_example.md` carries no such comment) instead of
`MarkdownSection2WithComment`. Changed `Updates` to
`MarkdownSection2WithComment` (mirroring `feat`'s own
`Updates(MarkdownSection3WithComment)` precedent) so this validates too.
After both fixes, the scratch script confirmed **both** `example.md` and
`template.md` now parse successfully end to end via `parse_vcr` (every
frontmatter field, `Verifies`, `Coverage`, all `AcceptanceCriterion`
entries' `description`/`test_steps` combinations, `More Information`, and
`Updates` with its comment) -- the only discrepancy from a byte-exact
round-trip is the pre-existing, already-documented `MarkdownListItem`
"tight numbered list renders as loose" quirk (unrelated to VCR, confirmed
via `difflib` diff: only blank lines inserted between numbered `Test
Steps` items), not a schema defect. The scratch script was deleted after
the run, never committed. Added 9 new `test_body.py` tests (all four
`description`/`test_steps` combinations plus `Updates`' leading comment)
and adjusted the reference-document fixtures in `test_body.py`/
`test_parser.py` to exercise AC-001 (both fields), AC-003 (description
only), and a new AC-004 (neither) -- mirroring `example.md`'s own shape --
plus the `Updates` comment. Quality gate re-run clean: `ruff format
--check`, `ruff check`, `vulture` (no new whitelist entries needed --
`description` is already a ubiquitous field/kwarg name used throughout the
codebase), and the full `unittest` suite (2336 tests, `OK`).

#### 2026-08-31T10:30:00.000Z - Phase 1 complete: `vcr/models/v1/` implemented and unit-tested
Implemented the full `vcr/models/v1/` schema and parser, mirroring `dec`'s
`models/v1` layout file-for-file (`frontmatter.py`, `body.py`,
`document.py`, `parser.py`, `summary.py`, `_util.py`, `__init__.py`, plus
`vcr/models/__init__.py` and an empty `vcr/__init__.py`). `VcrFrontmatter`
narrows `status` to the closed `draft`/`progress`/`complete`/`approved`
set (REQ-004). `body.py` implements `Verifies` verbatim from the Design
Notes' persisted class sketch (`MarkdownSection2WithComment`, regex-checked
`value`, mandatory `notes`), `Coverage` (RSK `Strategy`-style closed
3-value `full`/`partial`/`none` paragraph, REQ-002), `TestSteps` (`####
Test Steps`, a numbered procedure list, `min_length=1`), `AcceptanceCriterion`
(a regex-aliased `### AC-NNN (Method): <text>` heading with `number`/`method`
`@computed_field`s and an optional `test_steps` child), `AcceptanceCriteria`
(`>=1` entries), reused `MoreInformation`/`UpdateEntry`/`Updates` (DEC's
exact shape), and the top-level `Vcr` H1 container with a
`_validate_ac_numbers_unique` `model_validator` mirroring DEC's
`Decision._validate_option_numbers_unique` (mandatory `acceptance_criteria`,
so no `is not None` guard needed). `VcrSummary` is a plain `DocSummary`
subclass with no extra fields (DEC precedent, not RSK's enriched one).
Confirmed via a quick interactive sanity check before writing tests that
`AcceptanceCriterion` needed a different computed-field extraction
mechanic than DEC's `Option`/RSK's `Probability`/`Impact`: those are *leaf*
sections (zero other declared fields), so their own `.text` returns the
*complete* extent (heading marker + body) verbatim; `AcceptanceCriterion`
declares one other field (`test_steps`), making it *composite*, so its
`.text` returns only the heading's own inline content (marker already
stripped) -- the `number`/`method` regex therefore matches against
`self.text` directly, not `self.text.splitlines()[0]`. A consequence: an
`AcceptanceCriterion`'s body may contain nothing besides an optional
`#### Test Steps` -- there is no separate free-form description/notes
paragraph field, matching UC's `Extension`/`SubVariation` precedent
(condition/title info lives entirely in the heading, the declared field(s)
are the *only* body content) rather than DEC's leaf `Option` (which
absorbs arbitrary body prose since it declares no other field at all).
This means the already-finalized `example.md`'s AC-001/002/004 descriptive
paragraphs (prose directly under the heading, before/without `Test Steps`)
do **not** validate against this Phase 1 schema as literally written --
a known, deliberate gap flagged for Phase 3 (packaging `example.md`/
`template.md` as real package data) to resolve, either by revising
`example.md` or by reconsidering the schema then; Task 0.1 already noted
neither draft had been validated against `models/md` yet, and this phase's
own test fixtures (inline `textwrap.dedent`, per instructions) do not
depend on either draft file. Wrote 103 new tests across
`tests/vcr/models/v1/test_frontmatter.py`/`test_body.py`/`test_parser.py`,
covering every heading alias (including all 5 DTAIS method words and the
`AC-NNN` 3-digit/gap-allowed/duplicate-rejected number shape), `Verifies`'/
`Coverage`'s regex value validation, `TestSteps` presence/absence,
mandatory-vs-optional section behavior, misordering, and full-document
round-trips through `parse_vcr`. Added a `whitelist.py` entry
(`_validate_ac_numbers_unique`, `verifies`, `test_steps`) for three genuine
Pydantic-framework vulture false positives (mirroring the existing `dec
(feat-21 Phase 1)`/`_validate_option_numbers_unique` precedent exactly).
Quality gate green: `ruff format --check`, `ruff check`, `vulture` (with
the new whitelist entries), and the full `unittest` suite (2331 tests,
`OK`) all pass. Did not touch `server.py`, did not create
`vcr/tools`/`vcr/resources`/`vcr/prompts`, and `vcr/__init__.py` stays
empty (module docstring only, no `tools`/`resources`/`prompts` import) --
all reserved for Phase 2/3/4.

#### 2026-08-31T09:10:00.000Z - Phase 0 complete: drafted template.md, confirmed AC-NNN regex/duplicate check
Drafted `template.md` (Task 0.1's remaining sub-bullet), reading
`example.md` plus `dec_template.md`/`rsk_template.md`/`prb_template.md`/
`req_template.md`/`uc_template.md` (`src/biz/dfch/specmgr/<domain>/data/`)
first to confirm the codebase's actual `*_template.md` conventions: short
"blind text" placeholder prose (`prb`/`uc` precedent), an HTML comment
restoring authoring/enforcement guidance on fields whose precedent class
is a `*WithComment` variant (`req_template.md`'s `## Level`/`## Priority`),
and appending "Mandatory."/"Optional."/cardinality notes as trailing prose
directly inside free-form blind-text content otherwise (`prb_template.md`/
`uc_template.md`). Cross-checked every comment placement against the
already-finalized `example.md` before adding one: `## Verifies` is the
document's *only* comment-bearing section (`Verifies` is sketched as
`MarkdownSection2WithComment` in Design Notes, and `example.md` itself
already exercises the slot) plus `## Updates`' permanent anchor;
`## Coverage`, `## Acceptance Criteria`, and `#### Test Steps` show no
comment in `example.md` either, matching their precedent classes'
lack of comment support (`rsk.Strategy`, `dec.ProsAndCons`, `dec.Option`)
-- adding one there would have committed `template.md` to a schema shape
Phase 1 hasn't decided and `example.md` already contradicts. So
`template.md` exercises every section from `example.md`'s shape
(frontmatter with placeholder id `deaddead-face-face-face-deaddeadface`;
`## Verifies` with one leading comment bundling both the "optional
context" convention and the enforced value/notes shape, a placeholder
`REQ <uuid>: <title>` value using a second, distinct placeholder UUID
`c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee`, and a mandatory `notes`
paraphrase; a bare `## Coverage` value with no note at all, matching
`rsk_template.md`'s identical `## Strategy` precedent (an exact-match
`re.fullmatch` value has no room for trailing text either); `## Acceptance
Criteria` with two `### AC-NNN (Method): ...` entries -- the first
carrying the `>= 1`/DTAIS-closed-set/unique-number guidance as a trailing
prose sentence in its own free-form body paragraph, and an optional
`#### Test Steps` list; the second with no `#### Test Steps`, and a
trailing note explaining why -- `## More Information` using the exact
`dec_template.md`/`feat_template.md` boilerplate sentence instead of a
comment; `## Updates` with its permanent "newest first" anchor). Then ran
Task 0.2: a throwaway `/tmp/vcr_scratch_task02.py` script (deleted after
the run, never committed) tested `_AC_HEADING_PATTERN = re.compile(r"###
AC-(\d{3}) \((Demonstration|Test|Analysis|Inspection|Special)\): (.+)")`
against 6 valid headings (all 5 DTAIS words plus a 3-digit boundary case
`AC-999`) and 8 invalid headings (2-digit/4-digit number, an unknown
method word `Certification`, missing parentheses, missing colon, missing
criterion text, a non-digit number, and wrong case) via `re.fullmatch`,
and a `dec`-`_validate_option_numbers_unique`-style seen-set duplicate
check against 6 number-list fixtures (no duplicates, two different
allowed-gap cases, an exact duplicate, a duplicate at opposite ends of the
list, and a single-entry list). First draft of the pattern omitted the
literal escaped parentheses around the method group, which the script
caught immediately (valid cases wrongly failed to match, and the
"missing parentheses" invalid case wrongly matched); fixed and re-ran --
all 14 heading cases and all 6 duplicate-check cases passed on the second
run. Confirmed the corrected pattern also matches all four real
`### AC-NNN (Method): ...` headings in the already-finalized
`example.md` verbatim. `example.md` itself was read-only throughout --
left byte-for-byte unchanged (`git status`/`git diff` confirm no
modification). Updated Task 0.1/0.2 checkboxes and Current Status
accordingly; no Decisions Made entry needed (no open design question was
settled here, just an empirical confirmation of already-decided
REQ-003/Design Notes text).

#### 2026-08-31T08:50:00.000Z - Merged example.v2.md/example.v3.md into a single, cleaned example.md
Reviewed `example.v2.md` (concurrently edited by the user: DTAIS/`Special`
rename applied directly, plus two comment tweaks) against `example.v3.md`
(my own DTAIS-rename pass, created before noticing the user's edit) --
confirmed the two had converged on the same content, with the user's `v2`
slightly ahead (refined comment wording). Then reviewed every HTML
comment in the document for whether it helps a future *using* agent
(authoring a new `vcr` document) vs. a future *implementing* agent
(building the Pydantic models) -- surveyed `dec`/`uc`/`req`/`rsk`/`prb`/
`feat`/`qa`'s already-shipped `*_example.md`/`*_template.md` files to
find the actual codebase convention (see new Design Notes bullet).
Result: removed every instructional/enforcement comment (`## Coverage`'s
vocabulary hint, AC-001's regex/resource-discovery hint, the `## Acceptance Criteria` comment that wrongly said the list "may be empty" -- contradicting
already-decided REQ-003's `>= 1` -- `#### Test Steps`'s and `## More Information`'s optionality notes, and the Updates entry's "enforced via
REGEX" note, none of which correspond to an actual designed comment-slot);
kept `## Updates`' "newest first" anchor (a permanent structural comment,
not authoring guidance, per `feat`'s identical convention); removed the
top meta/changelog comment block entirely (that history now lives only in
this README); and added one new realistic filled-in comment under
`## Verifies` to exercise its designed optional `comment` field (mirroring
RSK's/PRB's H1-comment pattern), since it had never been demonstrated.
Deleted `example.v2.md` and `example.v3.md`; `example.md` is now the
feature's single, definitive draft, intended for a future implementer to
build against directly. Updated Task 0.1, Current Status, and Design
Notes (candidate outline + new clean-example-convention bullet)
accordingly.

#### 2026-08-31T08:35:00.000Z - Renamed DTAIC/Certification to DTAIS/Special; added `specmgr://dtais` resource plan
Renamed the "Certification" verification method to "Special" (acronym
DTAIC -> DTAIS) throughout the current-design text (REQ-003, ACC-003,
Overview, Scope, Design Notes) -- past dated Updates/Decisions log entries
left unchanged as historical record. Added REQ-006/ACC-006: a new
cross-cutting `specmgr://dtais` resource explaining the DTAIS vocabulary,
mirroring `sop`'s still-unimplemented `specmgr://rasci` design and `rsk`'s
shipped `specmgr://rsk/tara`/`specmgr://rsk/risk-matrix` raw-markdown
resources. Persisted a full sketch (`general/resources/dtais.py`,
`general/resources/__init__.py` registration, and a draft
`general/data/general_dtais.md` content outline covering all 5 methods)
in Design Notes for Phase 3 (Task 3.3, new). Added `example.v3.md`
(supersedes `example.v2.md`) with AC-004 renamed to `(Special)`.

#### 2026-08-31T08:15:00.000Z - Added example.v2.md, redesigned `## Verifies`
Redesigned `## Verifies` from a cardinality-1-constrained
`MarkdownListItemWithNotes` bullet list to a single-value field
(`Verifies(MarkdownSection2WithComment)`: mandatory `value` line +
mandatory `notes` paraphrase + optional leading `comment`), after an
explore-agent survey found no codebase precedent for either the
list-of-one design or a heading-embedded-id alternative, but did find a
direct precedent for true 1:1 relationships (SOP's `Accountable`, RSK's
`Strategy`/`Owner`, REQ/GOL's `Source`). Persisted the resulting
`Verifies` class sketch (regex, field_validator, docstring) in Design
Notes for Phase 1. Added `example.v2.md` -- same scenario as `example.md`
but with the new `## Verifies` shape and a real YAML frontmatter block
(`id`/`status`/`type`/`created`/`updated`/`version`), so it is usable
directly once `vcr/models/v1/` exists rather than staying body-only.
Updated REQ-001, the candidate H1/body outline, and Task 0.1 to match.

#### 2026-08-31T07:52:00.000Z - Added discussion-draft example.md
Added `example.md` (API key revocation latency scenario, thematically
continuing `feat-32-sysrs/example.v4.md`'s partner-API-key story) for
user review -- illustrates `## Verifies`/`## Coverage`/
`## Acceptance Criteria` (all four DTAIC methods, with and without
optional `#### Test Steps`)/`## More Information`/`## Updates`. Not yet
validated against `models/md` (no `vcr` model code exists). Also
corrected the `## Updates` entry nesting in this README's own candidate
body outline (Design Notes) from `####` to `###`, matching `sysrs`'s own
"no Plan/Progress split -> one level shallower than `feat`" reasoning,
which applies identically to `vcr`.

#### 2026-08-31T07:25:24.241Z - Created
Feature folder created after an interactive planning session (conducted
on the `feat-32-sysrs` branch/worktree) settled the `vcr` schema shape,
DTAIC vocabulary, frontmatter status lifecycle, and simple-surface
tooling scope. GitHub issue #33 opened with a short overview as its
description; branch/worktree `feat-33-vcr` created off `origin/dev`.
