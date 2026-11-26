# History: Add `## Roles and Responsibilities`, `## Tags`, and `## Source` Sections to DEC Documents

#### 2026-09-19 13:00:00.000Z - Phase 7 planned (not implemented): second-round review findings

A follow-up `feat-reviewer` review of the completed feature (run after
Phase 6 landed) found four items, none of them functional defects: (1) a
**gap** -- ACC-004 claims new-section misordering is covered, but every
existing `TestDecisionMisordering` test only exercises pre-existing
sections (`## Updates`/`## Related Artifacts`), not the three new ones
added by this feature; manually verified the underlying engine still
rejects the new-section case correctly, so this is a missing regression
test, not a bug. (2) an **inconsistency** -- extracting `SourceBase.value`
to the shared base in Phase 1 genericized its `Field(description=...)`
wording from domain-specific ("origin/authority of this requirement"/
"decision") to generic ("this document"), while `req.Source`'s/
`dec.Source`'s own class-level docstrings still use the domain-specific
wording, an unremarked drift between the generated JSON Schema and the
class docstring. (3)-(4) two **code smells** in tests added/touched by
this feature: `tests/dec/models/v1/test_parser.py` duplicates the
`MANDATORY_ROLES_AND_SOURCE` constant instead of importing it from
`tests/dec/tools/_helpers.py` (the module Phase 2 introduced specifically
to avoid this duplication), and `tests/general/tools/test_validate.py`'s
DEC fixtures build bodies via concatenated `textwrap.dedent` calls
instead of the single-call style every sibling generic test file uses.
Added REQ-015 through REQ-018 (Requirements), ACC-014 through ACC-017
(Acceptance Criteria, unchecked), a Scope/Included bullet, and a new
"Phase 7: External Review Remediation (Round 2)" Task List block (Tasks
7.1-7.6, all unchecked) to this README to track fixing these items.
**No code, tests, or docs were changed as part of this update** -- this
is planning only, per explicit instruction; frontmatter `status` set
back to `in-progress` to reflect the newly added, not-yet-done Task
List items.


#### 2026-09-19 10:15:00.000Z - Phase 6 complete: post-review remediation

Added Phase 6 to this README's own Plan section (REQ-011 through REQ-014,
ACC-010 through ACC-013, a new "Known Limitations" section, and a new
"Phase 6: Post-Review Remediation" Task List block), then executed it, to
remediate two gaps an external code review of PR #136 found. Fixed
`tests/dec/models/v1/test_body.py::TestDecisionMisordering::test_updates_before_more_information_raises_assertion_error`
and `::test_related_artifacts_after_pros_and_cons_raises_assertion_error`:
both fixtures now include a valid `## Roles and Responsibilities`/`##
Source` block between `## Decision Outcome` and the actual misordering
trigger, and both now assert on the raised `AssertionError`'s message
content (`"More Information"`/`"Related Artifacts"` respectively) instead
of only its type. Verified the fix matters by temporarily reverting it
locally: both tests then failed with a *different* message (about
`RolesAndResponsibilities`, not the intended heading), confirming the
tests previously passed for the wrong reason; restored the fix
afterward, leaving no reverted state in the final diff. Added a new `##
[Unreleased]` entry to `CHANGELOG.md` documenting the three new `dec`
body sections under `### Added` and a `**BREAKING**`-marked `###
Changed` bullet with a before/after `diff` migration snippet showing how
to add the two mandatory sections to a pre-existing `dec` document.
Added a new "Known Limitations" section to this README (`###` level,
placed next to `### Design Notes`, mirroring
`feat-8-coverage-badge/README.md`'s precedent) documenting the backward-
incompatibility and its cross-reference to the unmerged
`feat-46-remove-adr` branch's own, incompatible plan for GitHub issue
#29. Added a new dated Decisions Made entry recording that the
mandatory-vs-optional cardinality question was explicitly revisited
and the decision was made to keep both sections mandatory, accepting
the resulting breaking change rather than reversing the design. Ran the
full quality gate: `ruff format --check`/`ruff check` clean, `vulture`
clean, `specmgr docs`/`mcp-docs` regenerated with **no content changes**
(expected -- no `src/**/*.py` touched this phase, only `.md`/tests/
`CHANGELOG.md`), `specmgr schema` regenerated all 12 `docs/*_schema.json`
with **no content changes**, full `pytest -n auto` suite green at 3329
tests (unchanged count from Phase 5, since Phase 6 only corrected two
existing tests' fixtures/assertions rather than adding new ones; `tests/dec/`
(240 tests + 69 subtests) and `tests/general/tools/` (252 tests + 852
subtests) individually re-verified green), `specmgr coverage-badge`
unchanged (99%). Not yet committed -- left for the orchestrator to
review and commit.


#### 2026-09-17 15:30:00.000Z - Phase 5 complete: docs and housekeeping

Updated `AGENTS.md`'s `dec/` bullet to document the three new body
sections (mandatory `## Roles and Responsibilities`, optional `## Tags`,
mandatory `## Source`) and the `models/md/common_sections.py`
shared-base-class refactor, referencing this feature. Updated
`.specmgr/feat/feat-7-various-improvements/README.md`'s Task 0.33:
checkbox `[x]`, status set to "split out into `feat-29-dec-source-roles`
... **is now complete**" (mirroring Task 0.32's own precedent exactly),
plus a new "Update 2026-09-17 (Task 0.33 split-out feature complete)"
Recent Updates entry and a frontmatter `updated` bump. Rescoped
`.specmgr/feat/feat-133-tags-dec-rsk/README.md` to RSK-only: dropped
every `dec`-related requirement/acceptance-criterion/task (renumbered
contiguously rather than left as gaps, since nothing outside that file
referenced the old numbering), rewrote its Overview/title/Scope/Design
Notes to reflect the narrower scope, added an "Explicitly Out Of Scope"
bullet pointing at this feature for the DEC half, and added a dated
Decisions Made entry plus a Related PRs/Commits cross-reference back to
this feature. Posted the two GitHub issue comments exactly as approved
by the user (no rewording):
[issue #29 comment](https://github.com/dfch/biz.dfch.SpecMgr/issues/29#issuecomment-5714986670)
and
[issue #133 comment](https://github.com/dfch/biz.dfch.SpecMgr/issues/133#issuecomment-5714987415).
Ran the full quality gate: `ruff format --check`/`ruff check` clean,
`vulture` clean, `specmgr docs`/`mcp-docs` regenerated with **no content
changes** (expected -- only `.md` non-packaged docs were touched this
phase, no `src/**/*.py`), `specmgr schema` regenerated all 12
`docs/*_schema.json` with **no content changes**, full `pytest -n auto`
suite green at 3329 tests (unchanged from Phase 4), `specmgr
coverage-badge` unchanged (99%). **Orchestrator sign-off (same day)**:
independently re-verified the file diffs, both comment URLs (confirmed
live with the exact approved text), and the full quality gate (all
green, no drift, 3329 tests, 99% coverage) -- accepted. ACC-007/ACC-008/
ACC-009 checked, frontmatter `status` bumped to `done`.


#### 2026-09-17 13:05:53.000Z - Phase 4 complete: prompt instructions updated

Updated `dec/data/dec_create_instructions.md` and `dec/data/dec_update_instructions.md`
(mirroring `sop_create_instructions.md`/`sop_update_instructions.md`'s RASCI
narration precedent) to document the three new body sections in their
correct position (`## Roles and Responsibilities` mandatory RASCI
composite, `## Tags` optional, `## Source` mandatory, between `##
Decision Outcome` and `## Related Artifacts`), added a new "Read the
RASCI role definitions" step referencing `specmgr://rasci` before
drafting (create flow: worded as never-skippable, since DEC's section is
mandatory as a whole, unlike SOP's optional one; update flow: worded
with SOP's own "skip this step if the change does not touch the roles
section" caveat, since that caveat is about the edit, not the section's
optionality), and updated the "Structure recap"/"Section order is
binding"/"Build a todo list"/"Show which sections are present"/"Map the
requested change to the right tool" passages accordingly, renumbering
the remaining steps. Also updated `create_dec.py`/`update_dec.py`'s own
module docstrings, which already enumerated DEC's body sections/tool
surface, to mention the three new sections and the `specmgr://rasci`
resource for consistency with the instructions text. Updated
`tests/dec/prompts/test_create_dec.py`/`test_update_dec.py`: fixed one
existing assertion whose exact-text expectation changed
(`test_mentions_mandatory_fields`), and added four new assertions
covering the new sections' presence and the RASCI-resource narration
(both the never-skippable create-flow wording and the
skip-if-not-touched update-flow wording). Ran the full quality gate:
`ruff format --check`/`ruff check` clean, `vulture` clean, `specmgr
docs`/`mcp-docs` regenerated (only the two touched prompts' own API doc
pages changed), `specmgr schema` regenerated all 12 `docs/*_schema.json`
with **no content changes** (expected -- only `.md` data files were
touched this phase, not `.py` schema files), full `pytest -n auto` suite
green at 3329 tests (up from 3326, +3 new test methods net), `specmgr
coverage-badge` unchanged (99%). Not yet committed -- left for the
orchestrator to review and commit.


#### 2026-09-17 00:00:06.000Z - Session handoff: reset Phase 4, queue phase-implementer dispatches

Ended the long-running planning-and-implementation session after Phase 3. Discarded a partial, uncommitted Phase 4 edit to `dec_create_instructions.md` (`git checkout --`) so the next session starts Phase 4 clean from this README's Task List rather than a half-finished draft. Added REQ-010/ACC-009 and this "Orchestration handoff" Design Notes paragraph documenting the decision to implement Phases 4-5 via dedicated `phase-implementer` subagent dispatches instead of continuing inline, to keep each phase's own context small. No code changed in this update; only this README.


#### 2026-09-17 00:00:05.000Z - Phases 2-3 complete: DEC schema, tests, templates/examples

Added `RolesAndResponsibilities` (mandatory), `Tags` (optional), `Source` (mandatory) to `dec/models/v1/body.py`, subclassing Phase 1's shared bases, wired into `Decision`'s field order between `## Decision Outcome` and `## Related Artifacts`. No schema version bump needed (see Design Notes). Updated `tests/dec/models/v1/test_body.py` (new alias/mandatory-section test classes plus `_REFERENCE_TEXT`/`_minimal_decision_kwargs` fixture updates) and `test_parser.py` (`_MINIMAL_DOC`/`_FULL_DOC` plus two inline fixtures). Fixed ~15 other test files across `tests/dec/tools/` (new shared `_helpers.py` fixture module, mirroring `tests/adr/tools/_helpers.py`) and `tests/general/tools/` (`test_update.py`, `test_delete.py`, `test_set_status.py`, `test_set_classification.py`, `test_validate.py`) whose own local minimal-`dec`-body fixtures needed the two new mandatory sections; `test_update.py`'s `dec` case's `eof_marker`/`eof_fragment` also updated to point at the new actual last section (`## Source`). Updated `dec_template.md`/`dec_example.md` packaged data with representative content for all three new sections. Ran the full quality gate: `ruff format --check`/`ruff check` clean, `vulture` clean, `specmgr docs`/`mcp-docs` regenerated, `specmgr schema` regenerated all 12 `docs/*_schema.json` (only `dec` changed content), full `pytest -n auto` suite green at 3326 tests (up from 3317), `specmgr coverage-badge` unchanged (99%).


#### 2026-09-17 00:00:04.000Z - Phase 1 complete: shared base classes

Added `models/md/common_sections.py` (`SourceBase`, `AccountableBase`, `ResponsibleBase`, `SupportBase`, `ConsultedBase`, `InformedBase`, `RolesAndResponsibilitiesBase`), exported from `models/md/__init__.py`. Refactored `req/models/v1/body.py::Source` and `sop/models/v1/body.py`'s six RASCI classes to subclass the new bases (behavior-preserving; both domains' existing test suites pass unchanged). Added `tests/models/md/test_common_sections.py` (10 tests) covering the base classes' own parsing and, most importantly, the `@alias` inheritance mechanism the design depends on. Ran the full quality gate: `ruff format --check`/`ruff check` clean, `vulture` clean, `specmgr docs`/`mcp-docs` regenerated (only `docs/GENERATED.md`'s test count and the two touched domains' API docs changed), `specmgr schema` regenerated all 12 `docs/*_schema.json` (only `req`/`sop` changed content, exactly as the Design Notes predicted), full `pytest -n auto` suite green at 3317 tests (up from 3307), `specmgr coverage-badge` unchanged (99%).


#### 2026-09-17 00:00:00.000Z - Created

Feature created from GitHub issue #29 ("Artifact type 'Decision' (DEC) need additional attributes from ADR frontmatter"), originally tracked as Task 0.33 in `feat-7-various-improvements`. Split into its own feature folder after design discussion concluded the scope required new DEC body sections (not frontmatter fields), a cross-domain shared-base-class refactor, and absorption of `feat-133-tags-dec-rsk`'s DEC half.
