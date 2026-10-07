# History: Generic heading-mapped Markdown-to-Pydantic document parser

#### 2026-08-14T12:00:00.000Z - post-closure docstring shortening: `MarkdownListItem`/`MarkdownParagraph` class docstrings trimmed

Requested by `feat-6-requirement-artifact`'s Task 2.6, since these two
classes' verbose class docstrings get inlined verbatim into every JSON
Schema `$defs` entry that references them (via `model_json_schema()`,
surfaced e.g. as an MCP tool's `outputSchema`) — not new work on this
feature's own scope, but a documentation-quality change to already-shipped
code, made here since this feature owns the module, same
"downstream feature triggers a fix in the closed engine" pattern as the
2026-08-12/2026-08-13 entries below.

- `MarkdownListItem`'s class docstring: ~2.7k chars → ~1.1k chars.
  `MarkdownParagraph`'s: ~1.3k chars → ~0.7k chars. Only the **class**
  docstring was shortened for both — `get_extent`/`from_text`/`__str__`'s
  own method docstrings (which never surface in an emitted JSON schema)
  are untouched, and each shortened class docstring points readers at those
  method docstrings for the full mechanics instead of duplicating them.
- No behavior change — `__doc__` content is not asserted by any test in the
  repo. Full suite green after the change (604 tests passing), `ruff format --check`/`ruff check` clean.
- Net effect on `feat-6-requirement-artifact`'s own `req_schema.json`
  generation: roughly offset by that feature's own Task 2.4 (adding
  `Field(description=...)` to its own fields), so the *total* schema size
  is about the same as before either change — the benefit is capping/
  reducing what these two shared base classes contribute per-reference,
  not the REQ schema's overall size on this particular pass.


#### 2026-08-13T12:00:00.000Z - post-closure bug fix: `MarkdownSection.text` now returns everything for a leaf section

Discovered while `feat-6-requirement-artifact`'s `parse_req` MCP tool
serialized a parsed `Requirement` via `model_dump()` — again the same
"discovered by a downstream feature adopting this closed engine" pattern as
the 2026-08-12 entry below, not new work on this feature's own scope, but a
genuine bug in already-shipped code, fixed in place.

- **Bug**: `MarkdownSection.text` (the computed_field exposing a section's
  content through `model_dump()`/`model_dump_json()`, since `_value` is a
  private attribute invisible to both) always re-parsed `str(self)` and
  returned only the heading's own inline text, regardless of whether the
  class was a leaf (no declared nested fields) or composite. For a
  composite section this is correct and intended — the body is already
  reachable through the declared nested fields, each exposing its own
  `.text` the same way. For a **leaf** section with no field of its own to
  hold the body (e.g. `req/models/v1/body.py`'s bare `class Notes(MarkdownSection2): ...`/`MoreInformation`/`Description`, the only
  three such classes in the repo), this silently dropped the entire body:
  `_value` held the complete heading+body extent verbatim (see
  `from_text`'s leaf branch), but `.text` only ever surfaced the heading
  (e.g. `"Notes"`), so `model_dump()` on such a field returned
  `{"text": "Notes"}` with the prose gone — exactly the class of bug
  `MarkdownParagraph.text`/`MarkdownListItem.text` were introduced to
  prevent for their own leaf case, but `MarkdownSection.text` had never
  been given the equivalent branch.
- **Why this was never caught here**: neither of this feature's own
  fixtures (`various_models.py`, `test_uc_example.py`) nor
  `feat-4-use-cases`' `uc/models/v2` ever asserts on `.text`/`model_dump()`
  for a bare leaf `MarkdownSection` carrying multi-line prose content —
  every `.text` assertion in the repo targets either a composite section's
  heading (e.g. `document.body.text == "Buy Goods"`) or a
  `MarkdownParagraph`/`MarkdownListItem` leaf, both already correctly
  handled.
- **Fix**: `MarkdownSection.text` now checks `self._get_field_names()`
  first; for a leaf (empty list), it returns `str(self)` unchanged (the
  complete extent, heading and body) instead of extracting just the
  heading. The composite branch (and its heading-only contract, still
  relied on by `document.body.text`/`uc/models/v2`'s `Extension`/
  `SubVariation` heading-reference extraction) is unchanged.
- **Test fallout**: added
  `tests/models/md/test_markdown_section.py::TestMarkdownSectionText` (3
  new cases: leaf returns the complete extent, composite returns only the
  heading, and a leaf child nested inside a composite parent still returns
  its own complete extent independently of its parent). No existing test
  asserted the old heading-only behavior for a leaf section, so nothing
  needed updating for the behavior change itself.
- Full repo suite green after the fix (604 tests passing at the time of
  this entry, `tests/models/md/` alone at 175 — the difference from the
  523 recorded in the 2026-08-12 entry below is
  `feat-6-requirement-artifact`'s own new `req` test files, not related to
  this fix's own test fallout). `ruff format --check`/`ruff check`/
  `vulture` clean.
- Addresses part of Follow-up #2 below (byte-exact round-trip/content
  exposure for a leaf section with richer body content) for the
  `model_dump()`/`.text` angle specifically — the round-trip (`__str__`)
  guarantee itself was already correct and unaffected by this bug.


#### 2026-08-12T12:00:00.000Z - post-closure bug fix: `get_extent` now also checks `@alias`

Discovered while `feat-4-use-cases` adopted this engine for its own `uc`
schema (exactly the scenario anticipated by Follow-up #3 above) — not new
work on this closed feature's own scope, but a genuine bug in already-shipped
code, fixed in place rather than worked around downstream.

- **Bug**: `MarkdownSection.get_extent` only ever checked that the next
  token was a heading of its own *level* (`own_tag`/`own_type`), never
  whether that heading's *text* satisfied the class's declared `@alias` --
  unlike `from_text`, which always has checked both. Consequence: for an
  `Optional[...]`/`X | None` heading-section field, `process_field`'s
  "absent" detection (`type_.get_extent(text) == 0`) could never actually
  fire when a *different*, same-level sibling heading immediately followed
  an absent optional field -- `get_extent` still reported a non-zero extent
  (since *some* same-level heading was there), so `process_field` proceeded
  to call `from_text` on the wrong slice, which then failed loudly with
  `"<Class>: heading text '<other heading>' does not match its declared @alias"` instead of correctly leaving the field `None` and moving on.
  Verified this was not `uc/models/v2`-specific: the same pattern already
  latent in this engine's own `CharacteristicInformation`-shaped fixtures
  (an absent `Optional` h3 immediately followed by a *different* h3)
  reproduces identically.
- **Why this was never caught here**: every fixture this feature's own test
  suite exercises (`various_models.py`, `test_uc_example.py`) only ever
  parses documents with *every* optional section present, so the
  "optional field absent, followed by a same-level sibling" path was never
  actually exercised end-to-end against a real `MarkdownSection` subclass --
  only against a synthetic, non-heading `_AlwaysAbsentField` fixture in
  `test_markdown_str.py` (whose overridden `get_extent` was hardcoded to
  always return `0`, sidestepping the very case that broke).
- **Fix**: `MarkdownSection.get_extent` now additionally checks
  `match_alias(cls, tokens[1].content.strip())` right after the existing
  tag/type check, returning `0` (no extent) on a mismatch, mirroring
  `from_text`'s own check exactly (see Task 2.2's amendment above).
- **Test fallout**: `tests/models/md/test_markdown_section.py`'s
  `TestMarkdownSectionGetExtent` (7 pre-existing cases) called
  `get_extent` directly on the bare, unaliased `MarkdownSection3` with
  arbitrary heading text (`"Sec3"`, `"Sibling"`, ...) that never matched
  `MarkdownSection3`'s own `SPACE_SEPARATED`-derived default alias
  (`"Markdown Section 3"`) -- these were deliberately testing
  heading-*level* semantics in isolation from heading-*text* semantics, so
  they were switched to the file's existing `_AnyHeadingLeafSection`
  fixture (a permissive `.+` regex `@alias`) instead of the bare class,
  preserving their original intent unchanged. Added one new regression
  case, `test_no_extent_when_heading_text_does_not_match_declared_alias`.
  No other test in the repo called `get_extent` on a `MarkdownSection`
  subclass with mismatched heading text (confirmed by grep), so this was
  the only fallout.
- Full repo suite green after the fix (523 tests passing at the time of
  this entry, up from the 498 recorded at this feature's own closure --
  the difference is `feat-4-use-cases`' own new `uc/models/v2` test files,
  not related to this fix's own test fallout).


#### 2026-08-11T23:00:00.000Z - (continued, part 12) feature closed

- Confirmed Task 4.1/4.2's commit (`8d99dd3`) was pushed and GitHub issue #5
  was closed. Set frontmatter `status: done` (from `in-progress`); every
  Task List phase (0–6) is now complete, so there is no remaining planned
  work to track under this feature.
- Reconciled the stale "Current Status" paragraph, which still described a
  2026-08-10 in-progress snapshot (untracked git state, 367 tests, a
  pre-existing `F841` exception) that had drifted well behind reality
  (everything committed across several commits since, 498 tests, `ruff`/
  `vulture` fully clean) -- rewritten to describe the actual, final closed
  state instead.
- Replaced the "Next (exact resumption point for a new session)" list --
  meant for an in-progress feature, no longer applicable -- with a
  "Follow-ups" section: trimmed down to the genuinely open, explicitly
  non-blocking items only (inert `validate_heading_structure` assertions,
  a richer round-trip test, `test_uc_example.py`'s optional
  `list[MarkdownListItem]` adoption, and a possible future
  `AdrFrontmatter`/`MarkdownFrontmatter` convergence), dropping the
  already-resolved/strikethrough entries per this file's own "edit in
  place, rely on git history" convention -- their resolution is already
  recorded in this Recent Updates log and in git history.


#### 2026-08-11T22:00:00.000Z - (continued, part 11)

- Completed: Task 4.1/4.2 (REQ-006/ACC-006), the last not-started item in
  this feature's Task List. Preceded by a design discussion with
  repo-owner that produced a new ADR,
  bc5e18ad-6bbf-4265-bae4-3e34984a2d29 ("Generic base frontmatter model for
  markdown document types"): a base `MarkdownFrontmatter`
  (`models/md/frontmatter.py`) with core fields `id`, `type` (a mandatory,
  non-blank document-type discriminator with no default -- added beyond
  the task's originally-listed field set), `created`, `updated`, `status`
  (free-form, defaults to `"draft"`, deliberately not restricted to
  `AdrFrontmatter`'s closed six-value enum), and `version` (validated
  against a new, `models/md`-local `SCHEMA_MAJOR_VERSION`/
  `CURRENT_SCHEMA_VERSION` pair in `models/md/_util.py`, independent of
  `models/adr/v1/_util.py`'s equivalents by explicit repo-owner direction).
  A concrete document type subclasses `MarkdownFrontmatter` and narrows
  `type` to a fixed `Literal["..."]` value with a default (e.g.
  `Literal["uc"] = "uc"`), letting a future generic loader dispatch on
  `type` alone before knowing which concrete subclass applies.
  `AdrFrontmatter` is explicitly left untouched/unconverted -- no shared
  base, no shared validator module -- a possible future convergence is
  noted in the ADR's Consequences but not decided or scheduled.
  Frontmatter *stripping* remains exactly as already decided (REQ-003):
  `python-frontmatter`'s `frontmatter.loads(text).content`/`.metadata`,
  the caller's responsibility, not this engine's.
  - New: `models/md/frontmatter.py` (`MarkdownFrontmatter`),
    `models/md/_util.py` (private validator helpers + version constants),
    both re-exported from `models/md/__init__.py`.
  - New tests: `tests/models/md/test_frontmatter.py` (19 cases) --
    `type` mandatory/non-blank, `status`/`version` defaulting and
    blank-normalization, `version` major-mismatch/malformed rejection,
    `created`/`updated` blank-to-`None`, plus a
    `TestMarkdownFrontmatterSubclassing` suite exercising the
    `Literal`-narrowed `type` discriminator pattern end-to-end (default
    applies with no explicit `type=`, a mismatched value is rejected,
    core-field defaults are still inherited, a subclass may add further
    fields of its own).
  - `whitelist.py` gained `_._validate_type_non_blank` (Pydantic
    `@field_validator`, invoked by Pydantic's validation machinery, not by
    any direct call -- same pattern as the other `_validate_*` entries
    already there).
  - Full suite: 498 tests (up from 479), all passing; `ruff format --check`/`ruff check`/`vulture` clean on every touched file;
    `specmgr docs`/`specmgr adr-toc` re-run, no unexpected drift beyond the
    new module docs/ADR TOC entry.
  - Updated Requirements (REQ-006 -> done), Acceptance Criteria (ACC-006 ->
    done), Task List (Phase 4/Task 4.1/4.2 -> done), Scope (new files),
    Dependencies/Related ADRs (new ADR) accordingly. All phases in this
    feature's Task List are now done.


#### 2026-08-11T21:00:00.000Z - (continued, part 10)

- Completed: Task 3.1/3.2 (REQ-005/ACC-005) — raw HTML rejection, the last
  item Phase 3 needed. Implemented as one choke point rather than
  per-class special-casing: `_markdown.py` gained `parse(text) -> list[Token]` (wraps `md.parse(text)`, then a recursive
  `_assert_no_raw_html` walk over the token list) plus
  `_RAW_HTML_TOKEN_TYPES = ("html_block", "html_inline")`. Confirmed
  empirically first (`markdown_it.parse`) that `html_block` tokens appear
  in the flat top-level list but `html_inline` tokens only ever appear
  nested inside an `"inline"` token's own `.children` -- never flattened
  into the top-level list -- so `_assert_no_raw_html` recurses into
  `.children` too, or it would silently miss every inline HTML tag.
  - Every direct `md.parse(text)`/`md.parse(self._value)` call site (14
    total, across `markdown_str.py`, `markdown_section.py` (x4),
    `markdown_paragraph.py` (x2), `markdown_list_item.py` (x3),
    `markdown_code_block.py` (x3), `markdown_block_quote.py` (x2)) now
    calls the new guarded `parse(text)` instead, importing it in place of
    the bare `md` symbol -- the same "one shared call site" convention
    `_markdown.format_text()` already established for `mdformat` options
    (Task 1.6.3). This means the fix automatically covers
    `MarkdownParagraph`/`MarkdownListItem`/`MarkdownCodeBlock`/
    `MarkdownBlockQuote` too, not only the two classes REQ-005's own
    wording names.
  - Rejected the plan's other originally-sketched option (disabling the
    `html_block`/`html_inline` rules on the shared `MarkdownIt` instance
    outright): that would make markdown-it silently re-tokenize raw HTML
    as something else (e.g. plain text/a paragraph) instead of raising,
    which is the opposite of "reject".
  - `MarkdownStr.from_text`'s leaf branch previously stored `_value`
    without ever tokenizing `text` at all (it relied entirely on a
    composite parent's `get_extent` call having already parsed it first);
    it now also calls `parse(text)` directly, so a leaf class reached
    directly -- not only via a parent -- is still guarded.
  - New tests: `tests/models/md/test_markdown_html_rejection.py` (12
    cases) -- `_markdown.parse` raising on a top-level `html_block`, on
    `html_inline` nested inside a paragraph's or a heading's `inline`
    children, and staying unaffected by plain Markdown formatting
    (`**strong**`/`*emphasis*`) and by HTML-looking text inside a fenced
    code block (opaque code, never block-parsed); plus end-to-end
    `MarkdownStr.from_text` (leaf) and `MarkdownSection.from_text` (leaf,
    via a `@alias(value=".+", type=AliasType.REGEX)`-decorated
    `MarkdownSection2` test double) pass/fail pairs matching ACC-005's
    literal wording.
  - Full suite: 479 tests (up from 467), all passing; `ruff format --check`/`ruff check`/`vulture` clean on every touched file;
    `specmgr docs` re-run with no unexpected drift beyond the new
    `_markdown.py` docstring content and the test-file count bump.
  - Updated Requirements (REQ-005 -> done), Acceptance Criteria (ACC-005
    -> done), Task List (Phase 3/Task 3.1/3.2 -> done) accordingly. Phase
    4 (REQ-006, typed frontmatter) is now the only not-started work left
    in this feature's Task List.


#### 2026-08-11T20:00:00.000Z - (continued, part 9)

- Found and fixed one more piece of stale documentation missed by the
  ADR-reconciliation/REQ-005-rescoping passes above: the plan's own
  **Design Notes** section (not a dated Recent-Updates entry, so it doesn't
  auto-expire the way those do) still described the superseded
  `Heading`-annotated/`_tokens`-based recursive slicing algorithm, still
  called content constraints "opt-in composables" as if the dropped generic
  marker framework were still planned, and still pointed at
  `tests/models/markdown/v1/` instead of the actual `tests/models/md/`.
  Rewrote all three bullets to describe the actual `get_extent`/`_value: str`
  design, REQ-005's concrete (non-opt-in) raw-HTML rejection, and the real
  test path; also pointed the ADR cross-reference at v1.5.0 explicitly.
  Prompted by repo-owner asking "any more updates to our docs needed?" after
  the REQ-005/ADR reconciliation — a reminder that a non-dated "current
  state" section can drift silently in exactly the way dated history entries
  can't.


#### 2026-08-11T19:00:00.000Z - (continued, part 8)

- Rescoped: REQ-005 (and its Phase 3/Task 3.1/3.2/ACC-005 counterparts), per
  repo-owner direction. Prior text planned a generic, composable
  `Annotated`-based content-constraint-marker framework (`AllowedTags`,
  `LengthConstraint`, a generic `NoRawHtml()` marker, a shared validator, a
  `constraints.py` module) — this was never actually decided anywhere beyond
  the two class-level decorators that do exist (`@markdown`/`@alias`), and
  repo-owner flagged it as confusing/unclear on re-reading it. Dropped that
  framework as speculative; REQ-005 is now the one concrete, decided need
  instead: reject raw HTML (both HTML blocks and inline HTML tags) anywhere
  in a parsed document, since the shared `md = MarkdownIt("commonmark")`
  instance currently accepts raw HTML per CommonMark's default. No
  implementation done yet — REQ-005/Task 3.1/3.2 remain not-started, just
  concretely rescoped. Updated Requirements (REQ-005), Acceptance Criteria
  (ACC-005), Scope (reconciliation note + "Explicitly out of scope"), and
  Task List (Phase 3 header/Task 3.1/3.2) accordingly.


#### 2026-08-11T18:00:00.000Z - (continued, part 7)

- Completed: Task 1.6.3 -- `MarkdownListItem` (`markdown_list_item.py`), the
  final Phase 1 building block, resolving a stalled prior session (see
  `session-ses_00ed-markdown-list.md`) that had converged on a
  `MarkdownList`/`MarkdownBulletList`/`MarkdownOrderedList` container-class
  design but stopped short of implementing it. Repo-owner corrected that
  design mid-session: no separate container class is needed at all -- a
  single `MarkdownListItem` (subclassable, leaf-or-composite, shared by
  bullet and ordered lists) used purely as `items: list[MarkdownListItem]`/
  `list[MarkdownListItem] | None` on any existing `MarkdownSection`/
  `MarkdownParagraph`/`MarkdownListItem` fully reuses Task 1.6.1's
  `list[MarkdownStr]` machinery unchanged, with no new container-level
  parsing/rendering code.
  - `get_extent`: requires `tokens[0].type` in `("bullet_list_open", "ordered_list_open")` and `tokens[1].type == "list_item_open"`; returns
    `tokens[1].map[1]` directly -- unlike `MarkdownSection`/`MarkdownParagraph`,
    `list_item_open`'s own map already spans nested content, so no
    stop-condition scan is needed.
  - `from_text`: asserts the same triple plus `tokens[2].type == "paragraph_open"` (every item is assumed to start with a paragraph).
    Leaf (no declared fields): `_value` = the complete extent verbatim,
    marker and any un-modelled nested content included (mirrors
    `MarkdownSection`/`MarkdownParagraph`'s leaf case). Composite (a
    subclass declares fields): `_value` = the leading paragraph's own lines
    verbatim, *marker included* -- deliberately unlike `MarkdownParagraph`'s
    marker-free `_value`, since an item cannot reconstruct its own marker
    from class metadata alone (it depends on bullet-vs-ordered and, for
    ordered lists, final position, neither known to the item itself); the
    remainder is dedented (`mdformat` dedents an extracted indented
    sub-block automatically) and delegated to `super().from_text()`.
  - `__str__`: leaf defers to `super().__str__()`. Composite re-indents the
    declared fields' rendered output by the marker's own width (derived via
    regex from `_value`'s first line) before recombining -- verified
    empirically (throwaway scripts, not committed) that this indent, always
    computed from the item's own *solo* pre-renumbering marker (e.g. always
    `"1. "` for an ordered item in isolation, never the final padded
    `"10. "`), still parses correctly once combined with sibling items and
    renormalized, because CommonMark's nesting rule only needs indentation
    to meet the *literal* text's own marker width at parse time -- the final
    padded renumbering is a pure render-time transformation applied
    afterwards. Confirmed with a real 11-item ordered list (matching
    `uc_example.md`'s `Main Success Scenario` size) with a composite item at
    position 10 (to stress 1- vs 2-digit padding): byte-exact match.
  - New computed field `text` (mirrors `MarkdownSection.name`): re-parses
    `_value` and returns the leading paragraph's inline content,
    marker/indent-stripped.
  - **Cross-cutting prerequisite**: `_markdown.py` gained `format_text()`
    (`mdformat.text(text, options={"number": True})`), adopted by every
    normalization call site in `markdown_str.py`/`markdown_section.py`/
    `markdown_paragraph.py`/`test_uc_example.py`'s `setUpClass`, replacing
    bare `mdformat.text(text)`. Without `number=True`, `mdformat`'s default
    collapses every ordered-list item's marker to `"1."` on each
    normalization pass (CommonMark only treats a list's first number as
    semantically meaningful), making real sequential numbering
    unrepresentable -- confirmed empirically that `number=True` has no
    effect on headings/paragraphs/bullet lists, and the full suite (405
    tests, pre-Task-1.6.3 baseline) stayed green after this switch alone.
  - **Accepted, documented exception to REQ-004** (discussed and agreed with
    repo-owner before implementing): a genuinely *tight* source list
    round-trips to a structurally-equivalent *loose* list, not byte-exact --
    because each item is independently `mdformat`-renormalized in isolation
    (already true of Task 1.6.1's `process_list_field`, not something this
    task changed) before the parent's existing generic `list[MarkdownStr]`
    `__str__` rejoins them, and tightness is a property of the *gap between*
    items, which a solo-renormalized item cannot retain. Loose lists are
    unaffected and remain byte-exact. This matches this feature's own
    founding ADR (832cd6c1-ef8a-4bfc-990e-a610823f61ae), which already
    treats list-rendering variance as out of scope for byte-exact fidelity.
  - Restriction (accepted trade-off, per the design discussion): a bare
    `MarkdownListItem` can only be used inside `list[MarkdownListItem]`,
    never as a top-level/scalar field, since `get_extent`/`from_text`
    structurally require the enclosing list-open wrapper token to exist.
  - New tests: `tests/models/md/test_markdown_list_item.py` (24 cases) --
    `get_extent` (no-extent for a non-list/heading start, leaf bullet/
    ordered own-span-only including a following sibling, extent including
    an un-modelled nested sub-list), `from_text`/`__str__` (leaf bullet/
    ordered round-trip, inline-formatting preservation, opaque nested
    sub-list round-trip, rejects non-list text, composite split/round-trip
    for both bullet and ordered markers, composite with a nested
    `list[MarkdownListItem]` sub-list round-tripping to its loose
    equivalent, the tight->loose widening and loose-stays-exact cases side
    by side, a real 11-item ordered-list-as-a-section-field case with
    correct numbering, the same with a composite item stressing padding,
    and an absent optional `list[MarkdownListItem] | None` field), and
    `text` (marker/indent stripping for leaf bullet/ordered/composite items,
    ignoring an un-modelled nested sub-list).
  - Full suite: 429 passed, 0 failed (405 -> 429, 24 new). `ruff format --check`/`ruff check`/`vulture` clean. `specmgr docs` regenerated (83
    module files, up from 82) and re-run confirmed no further drift;
    `specmgr adr-toc` re-run confirmed no drift (unrelated to this task).
  - Task List: Task 1.6.3 marked done above, its description rewritten to
    describe the actual `MarkdownListItem`-only design (no `MarkdownList`
    container ever landed, by explicit repo-owner decision mid-session).
    Task 1.7 (exercise `@alias`'s `REGEX` branch end-to-end) remains the
    only not-started task left in Phase 1.
- Next: see item 5 above (optional future adoption in `test_uc_example.py`'s
  fixture); items 2-4 above are unchanged, not touched this session.


#### 2026-08-11T17:00:00.000Z - (continued, part 6)

- Completed: Task 1.6.2 -- `MarkdownParagraph` (`markdown_paragraph.py`), a
  single class (no `MarkdownParagraph1..6` spectrum -- a paragraph has no
  level) pinned to `@markdown(type="paragraph_open", tag="p")`, with no
  `@alias` enforcement of its own text (agreed via clarifying questions this
  session: a paragraph's content is free-form prose, not a title to match
  against a class-name-derived alias, unlike a heading).
  - `get_extent`/`from_text`: leaf case (no declared fields) claims exactly
    the paragraph's own line span (`paragraph_open.map[1]`), nothing more --
    unlike a leaf `MarkdownSection`, which greedily claims everything up to
    the next sibling/ancestor heading since "nothing else will retain that
    text." A leaf `MarkdownParagraph` deliberately does *not* mirror that:
    content following it (even a sibling paragraph) is left untouched.
  - Composite case (has declared `MarkdownStr`/`list[MarkdownStr]` fields):
    `_value` holds only the paragraph's own inline text; the remainder is
    delegated to `super().from_text()` for field population, exactly like
    `MarkdownSection.from_text`'s post-heading body delegation. `get_extent`
    bounds this delegation only by the next heading of *any* level (h1-h6)
    -- not some paragraph-specific level, since a paragraph has none and,
    per repo-owner clarification, can never itself contain a heading. A
    following sibling paragraph does *not* stop it; only a heading does.
    `__str__` mirrors `MarkdownSection.__str__`'s composite branch minus the
    heading-marker (`"#" * level`) reconstruction, since a paragraph has
    none to reconstruct.
  - Design converged via clarifying questions before implementation (leaf
    extent = own block only; no `@alias` check; composite stop condition =
    any heading level, with the child fields' own `get_extent`/`from_text`
    determining the real boundary within that window) -- see this session's
    Q&A for the reasoning `git log -p` doesn't otherwise capture.
  - New tests: `tests/models/md/test_markdown_paragraph.py` (12 cases) --
    `get_extent` (no-extent, leaf-own-span-only including multi-line and
    trailing-sibling-paragraph cases, composite-to-end-of-input,
    composite-not-stopped-by-a-sibling-paragraph, composite-stops-before-any-
    heading-level parametrized h1-h6) and `from_text`/`__str__` (leaf
    round-trip, leaf inline-formatting preservation, leaf rejects
    non-paragraph text, composite splits intro text from its delegated
    field, composite round-trips exactly, composite leaves a following
    heading available for a sibling field in a larger document).
  - Registered in `models/md/__init__.py`'s imports/`__all__`.
  - Full suite: 402 passed, 0 failed (390 -> 402, 12 new). `ruff format --check`/`ruff check`/`vulture` clean.
  - Task 1.6.3 (`MarkdownList`) remains not-started.


#### 2026-08-11T16:00:00.000Z - (continued, part 5)

- Completed: Task 1.6.1 -- `list[MarkdownStr]`/`list[MarkdownStr] | None` field
  support in `markdown_str.py`, added ad hoc (not part of the original task
  list; repo-owner requested it directly this session):
  - `_unwrap_list(annotation) -> tuple[type, bool]`: new sibling to
    `_unwrap_optional`, recognizing plain `list[X]` only (no
    `Sequence`/`tuple` support by explicit decision).
    `_get_field_names`/`from_text` apply `_unwrap_optional` then
    `_unwrap_list` in that order, so `list[X] | None` resolves to
    `(X, optional=True, is_list=True)` -- the two axes are independent.
  - `process_list_field(name, item_type, text, *, optional=False) -> tuple[str, list[MarkdownStr] | None]`: loops `item_type.get_extent`/
    slice/`mdformat`-renormalize/`item_type.from_text` while an item
    matches. A first draft mirrored `process_field`'s `(extent, value)`
    contract (matching the initial design discussion) but this was found to
    be **incorrect**, not just a style choice: summing per-item extents
    computed against a locally-renormalized string silently loses lines
    `mdformat.text()` drops between items (e.g. a separating blank line),
    so a caller-side `remaining_text.splitlines()[extent:]` computed from
    that sum no longer lines up with the caller's actual `remaining_text`
    -- exactly the class of bug `from_text` itself already moved off an
    integer line-index `cursor` to avoid (see 2026-08-10 entry below).
    Fixed by having `process_list_field` return the already-fully-reduced
    `remaining_text` string directly; `from_text`'s per-field loop adopts it
    as-is for list fields, bypassing the generic extent-based slicing step
    used for scalar fields.
  - Semantics: no item found on the list's *first* iteration is an absence
    -- an assertion error for a mandatory `list[X]` field, or `(text, None)` (untouched) for `list[X] | None`. No item found on any
    *subsequent* iteration just ends the list normally, i.e. items 2+ are
    implicitly optional without needing `Optional[X]` on `item_type`
    itself.
  - `__str__`: a list field renders every item in declaration order via
    `str(item)`, appended the same way a scalar field's single rendered
    string is today; a `None` list is skipped exactly like an absent
    optional scalar field.
  - Also removed a leftover debug `print(f"_get_field_names: ...")` from
    `_get_field_names` while touching that method (unrelated cleanup, not
    gated behind its own task).
  - New tests in `tests/models/md/test_markdown_str.py`
    (`_MarkerItemField`/`_RequiredListContainer`/
    `_TrailingOptionalListContainer`/`_PresentOptionalListContainer`/
    `_ListThenTrailingContainer` fixtures): mandatory list collects all
    matching items and round-trips, mandatory list with zero items raises,
    optional list absent when remaining text is empty, optional list
    populated when items are found, and a list stopping at the first
    non-matching item so a subsequent scalar field can still consume the
    remainder. `_MarkerItemField` deliberately uses a plain-text marker
    (`"item: "`), not real list syntax (`"- "`) -- joining several
    pre-rendered leaf blocks with a blank line (`MarkdownStr.__str__`'s
    normal behavior) turns a *tight* markdown list back into a *loose* one,
    which would fail a round-trip assertion for a reason unrelated to
    list-field support itself.
  - Full suite: 389 passed, 0 failed (384 -> 389, 5 new).
    `ruff format --check`/`ruff check`/`vulture` clean.
  - Task 1.6.2 (`MarkdownParagraph`) and Task 1.6.3 (`MarkdownList`) remain
    not-started -- their descriptions are still pending from the
    repo-owner, deliberately deferred to a later session per explicit
    instruction this session.


#### 2026-08-11T15:00:00.000Z - (continued, part 4)

- Completed: Corrected an error in ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae
  (now v1.4.0) and in `alias_match.py`'s actual code, per explicit
  repo-owner direction: a class declaring no `@alias` at all must default
  to `AliasType.SPACE_SEPARATED`'s derivation of `cls.__name__` (the same
  default `@alias` itself already uses), not a literal match against the
  raw class name -- the part 3 entry below incorrectly documented the
  latter as intended/shipped behavior.
  - `alias_match.py`: `match_alias`'s no-`_alias_metadata` branch now
    returns `heading_text == space_separated_name(cls.__name__)` instead of
    `heading_text == cls.__name__`; updated its docstring accordingly.
    `markdown_section.py`'s `from_text` docstring and `alias_type.py`'s
    stale "`LITERAL`... is the default alias type" docstring line (already
    inconsistent with `alias.py`'s real `SPACE_SEPARATED` decorator
    default, independent of this bug) were also corrected.
  - Removed the now-superfluous explicit annotations that part 3 (wrongly)
    added or kept to satisfy the incorrect literal default:
    `various_models.py`'s `CharacteristicInformation` lost its
    `@alias(value="Characteristic Information", type=AliasType.LITERAL)`;
    `test_markdown_section_levels.py`'s `TopLevel`..`SixthLevel` (six
    classes) lost their `@alias(type=AliasType.SPACE_SEPARATED)`. Both are
    now exactly what the corrected default produces automatically.
  - `various_models.py`'s `RelatedInformation` needed no change -- it was
    already (correctly) left undecorated, but the previous incorrect
    default made it fail to match its `"Related Information"` heading; two
    tests were failing before this fix
    (`test_markdown_section.TestMarkdownSectionStr.test_composite_document_reemits_every_heading_and_body`,
    `test_markdown_str.TestFromText.test_main_document_from_text`) and pass
    after it, with no fixture change.
  - `test_alias_match.py`/`test_markdown_section.py`: renamed and rewrote
    the no-`@alias`-default tests
    (`test_class_with_no_alias_defaults_to_literal_class_name_match` ->
    `..._space_separated_class_name_match`) to assert the corrected
    behavior; `test_alias_match.py` also gained a fixture without a leading
    underscore (`NoAliasMultiWord`) since `space_separated_name` applied to
    an underscore-prefixed name (the previous `_NoAlias`) produces an odd
    `"_ No Alias"` result, irrelevant to what the test demonstrates.
  - Full suite green (see next full-suite run for the exact count);
    `ruff format --check`/`ruff check` clean; `specmgr docs`/`specmgr adr-toc` regenerated.
  - REQ-001/ACC-001 above updated to stop claiming "a class with no `@alias`
    at all always matches any heading text", stale since before v1.2.0.


#### 2026-08-11T14:00:00.000Z - (continued, part 3)

- Completed: Brought `alias_match.py`/`markdown_section.py` in line with
  ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.2.0/v1.3.1 (previously
  documentation-only revisions -- this entry is the code catching up):
  - `match_alias`: a class with no `@alias` metadata at all now defaults to
    a literal match against `cls.__name__`, instead of unconditionally
    returning `True`. Updated its and `space_separated_name`'s docstrings
    accordingly; updated `MarkdownSection.from_text`'s docstring to stop
    claiming `_alias_metadata` is "otherwise never checked against
    anything."
  - Reconciled every fixture that relied on the old "no alias = accept
    anything" default (ADR v1.2.0's open item (1)): `various_models.py`'s
    `MainDocument` (H1, document-specific title) now declares
    `@alias(value=".+", type=AliasType.REGEX)`; its `RelatedInformation`
    (multi-word class name, space-separated heading) now declares
    `@alias(type=AliasType.SPACE_SEPARATED)`; `test_uc_example.py`'s
    `UseCase` (H1) likewise gained the `.+` regex alias. `Scope`/`Notes`/
    `Assumptions` needed no change -- their single-word class names already
    equal their fixture headings literally, matching the new default by
    coincidence. `test_markdown_section_levels.py`'s `TopLevel`..
    `SixthLevel` (multi-word class names, space-separated headings) all
    gained `@alias(type=AliasType.SPACE_SEPARATED)`.
  - Fixed 4 tests in `tests/models/md/test_markdown_section.py` that called
    `MarkdownSection3.from_text` directly with arbitrary heading text
    (`"Sec3"`, `"Anything Goes"`, `"Leaf H3"`) that no longer matches the
    literal-class-name default: introduced `_AnyHeadingLeafSection`
    (`@alias(value=".+", type=AliasType.REGEX)`) for tests where the
    heading text is incidental to what's actually being tested (extent/
    round-trip mechanics), and rewrote `test_class_with_no_alias_accepts_ any_heading_text` into two tests demonstrating the new default
    directly: `test_class_with_no_alias_defaults_to_literal_class_name_ match` (heading equal to class name succeeds) and
    `test_class_with_no_alias_rejects_a_different_heading` (anything else
    fails).
  - `test_alias_match.py`: renamed/split `test_class_with_no_alias_ metadata_always_matches` into
    `test_class_with_no_alias_defaults_to_literal_class_name_match` and
    `test_class_with_no_alias_rejects_a_different_heading`; added
    `test_regex_alias_accepts_any_non_empty_heading_text` (positive cases
    plus the empty-string rejection, per ADR v1.3.1's `.+` vs `.*` decision).
  - Full suite: 372 passed, 0 failed (368 -> 372: 4 fixed by rewrite/split,
    net 4 new). `ruff format --check`/`ruff check` clean (same pre-existing,
    unrelated `F841`). `specmgr docs` regenerated, no drift beyond the
    docstring content changes above (still 80 modules).


#### 2026-08-11T13:00:00.000Z - (continued, part 2)

- Completed: `markdown_section4.py`/`5.py`/`6.py` were also flagged as
  unreferenced (no import anywhere outside their own file, no test
  instantiated them), but unlike `metadata_utils.py` these are real,
  needed pieces of the h1-h6 spectrum, not dead code to remove. Kept them
  and instead:
  - Found, while investigating, that they weren't merely unused but
    actively broken: their `validate_headings` `model_validator` still had
    a *live* `assert self._tokens[0].tag == "h4"` (etc.) — `_tokens`
    (`markdown_section.py`) is declared but never populated by `from_text`
    (only `_value` is), so it's permanently `[]`, and this assertion would
    raise `IndexError` on construction of any `MarkdownSection4`/`5`/`6`
    instance. `markdown_section1.py`/`2.py`/`3.py` already have this same
    dead assertion fully commented out; `4`/`5`/`6` did not. Commented it
    out the same way in all three, matching `1`–`3`.
  - Added `tests/models/md/test_markdown_section_levels.py`: a six-level
    fixture (`TopLevel` h1 down to `SixthLevel` h6, one nested field per
    level) exercised through `TopLevel.from_text`, asserting every level
    down to `SixthLevel` is populated, the h6 leaf retains its full
    extent, `str(instance)` round-trips the source text exactly, and
    `get_extent` agrees across h4/h5/h6. This is the first test coverage
    that reaches h4-h6 at all (previous h1-h3-only fixtures never
    exercised these three classes or the bug above).
  - Full suite: 378 passed, 0 failed (374 -> 378). `specmgr docs` re-run
    clean (same 81 modules, only content diffs). `ruff format --check`/
    `ruff check` clean (same pre-existing, unrelated `F841`).


#### 2026-08-11T12:00:00.000Z - (continued)

- Completed: Deleted `src/biz/dfch/specmgr/models/md/metadata_utils.py`
  (`get_direct_metadata`/`get_inherited_metadata`/`find_metadata_source`/
  `get_metadata_chain`/`has_metadata`) after confirming, per repo-owner
  question, that it was unused dead code: no call site anywhere in
  `src/`/`tests/` besides its own definitions, no test file exercised it,
  and its `@annotate`-decorator docstring examples didn't even match the
  real `@markdown` decorator name — a sign it drifted from the rest of the
  module rather than being actively maintained. Removed its
  `models/md/__init__.py` re-exports and its `docs/api/` page, then
  re-ran `specmgr docs` (clean, 81 module files instead of 82) and the
  full suite (374 tests, unchanged — confirming nothing depended on it).
  Updated Scope/Task List above (Task 1.5 struck through as removed rather
  than done).


#### 2026-08-11T11:00:00.000Z - Reconciliation

- Completed: Reconciled the Requirements/Acceptance Criteria/Task List
  sections above with the actual `src/biz/dfch/specmgr/models/md/`
  implementation (Next item 1 from 2026-08-10), replacing the superseded
  `Annotated[Heading(...)]`/`heading.py`/`parser.py`/`constraints.py`/
  `frontmatter.py`-shaped text with descriptions of the real
  `@markdown`/`@alias`/`alias_match`/`MarkdownStr`/`MarkdownSection1..6`
  design (ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae v1.1.0).
  - Investigation ahead of the rewrite surfaced that considerably more had
    already landed than the 2026-08-10 entries below describe, all staged
    (`git add`ed) but never logged here: `metadata_utils.py` (`_metadata`
    introspection helpers), `Optional[X]`/`X | None` field support in
    `MarkdownStr.from_text`/`process_field` (3 new test cases), and —most
    notably — `tests/models/md/test_uc_example.py`, a full second fixture
    model tree (`UseCase` + every `##`/`###` section) that parses the real
    `tests/feat-5-md-model-parser/uc_example.md` end-to-end (frontmatter
    stripped via `python-frontmatter`, matching `models.adr.v1.parser`'s
    convention) and byte-exact round-trips it — i.e. REQ-007/ACC-007 (the
    full-fixture proof) is now satisfied, not still pending. Full suite:
    374 tests passing (up from 367), confirmed via `unittest discover`;
    `specmgr docs` re-run confirms `docs/api/`/`docs/GENERATED.md` have no
    drift (already regenerated and staged).
  - REQ-005 (content constraints: `AllowedTags`/`LengthConstraint`/
    `NoRawHtml`) and REQ-006 (typed `DocumentFrontMatter`) remain genuinely
    not-started, not just undocumented — no `constraints.py`/`frontmatter.py`
    module exists. REQ-005's originally-scoped opt-in `RoundTrip()` marker
    is dropped as moot: the engine's byte-exact round-trip (REQ-004) is
    already unconditional/always-on by construction (every leaf `_value`
    retains its full extent verbatim), so there is nothing left for such a
    marker to gate.
  - Scope, per explicit instruction: this entry touches only the
    Requirements/Acceptance Criteria/Task List/Scope reconciliation and
    logging it here; it does not implement Phase 3/4 (constraints,
    frontmatter typing) or revisit `validate_heading_structure`/`REGEX`
    end-to-end coverage (Next items 2–4 below, left as-is/unstarted).
  - Left untouched at the time, out of scope for this feature and not
    investigated further: `src/biz/dfch/specmgr/models/generic_md_parser.py`
    and `tests/test_generic_md_parser.py` (also staged, `@annotate_structure`/
    `MarkdownModel`-based) — an orphaned module not referenced by this or
    any other feature's README. **Update, same day:** subsequent
    investigation (prompted by a repo-owner question) traced it to a
    committed session transcript (`session-ses_01e6-md-pydantic-parser.md`,
    git-ignored) showing it pre-dated ADR 832cd6c1/this feature entirely — a
    prior, independent prototype an earlier session found already
    uncommitted in the working tree and was explicitly told to leave alone
    ("Leave it, ADR/plan stand as target design"). Confirmed it had zero
    production callers (only its own two test files: `tests/test_generic_md_parser.py`,
    `tests/feat-3-md-str-constraints/test_modelvalidator.py`), so, per
    repo-owner decision, it and both consumer test files (plus
    `GENERIC_MD_PARSER.md` and its `docs/api/` page) were deleted outright
    rather than integrated or further investigated. `tests/feat-3-md-str-constraints/`'s
    remaining, unrelated spike files (`test_token_tree_sample_markdown1.py`,
    `test_uc_example_tokens.py`, fixtures) and `.specmgr/feat/feat-3-md-str-constraints/`
    itself were explicitly left in place, not part of this deletion. Suite:
    380 -> 370 tests (10 removed, all belonging to the deleted files); `specmgr docs` re-run clean (80 modules, down from 81).
- Next: unchanged — see Next items 2–4 above (item 1 is now struck through
  as done; items 2–4 were not investigated or touched this session, so
  item 3's premise may itself now be partly stale given `uc_example.md`'s
  richer content — left for a future session to re-check, not assumed
  either way here).


#### 2026-08-10T20:00:00.000Z - Core recursive extraction mechanics

- Completed (this session): Implemented and unit-tested the core recursive
  extraction mechanics under `src/biz/dfch/specmgr/models/md/`:
  - `MarkdownStr.get_extent(text) -> int`: generic fallback extent
    calculation (max `token.map[1]` across all tokens with a map); returns a
    **line count** (not a 0-based index) so `0` unambiguously means "no
    extent" and `text.splitlines()[:get_extent(text)]` is the idiomatic
    slice — deliberately chosen over a last-line-index return to avoid an
    index/no-extent collision at line 0.
  - `MarkdownSection.get_extent(text) -> int`: heading-level-aware override.
    A level-N section's extent spans its own heading through any nested
    *deeper* heading, stopping at (excluding) the next heading whose level
    is `<= N` (sibling or ancestor) — confirmed correct for h1..h6 via
    parametrized `subTest` cases in `test_markdown_section.py`. Returns `0`
    if the text's first token isn't this class's own heading.
  - `MarkdownStr.process_field(name, type_, text) -> tuple[int, MarkdownStr]`:
    encapsulates one field's extent lookup + `mdformat`-normalized slicing +
    recursive `from_text` construction, extracted out of `from_text`'s loop
    body for testability/overridability. Fixed a `SyntaxError`
    (`type_: type of MarkdownStr` → `type_: type[MarkdownStr]`) introduced
    while drafting this.
  - `MarkdownStr.from_text(text) -> MarkdownStr`: replaced the hardcoded
    `field_type.from_text("abc")` placeholder with real cursor-based
    line distribution across declared fields (in declaration order), each
    field's share determined by `process_field`. Added a trailing assertion
    that the whole loop consumed every line (`cursor == len(lines)`), so
    leftover/unclaimed text after the last field fails loudly instead of
    being silently dropped.
  - Fixed a real, `mdformat`-precondition-driven bug surfaced by the above:
    `process_field`'s line-rejoin (`"\n".join(lines[:extent])`) drops the
    trailing newline that `from_text`'s `text == mdformat.text(text)`
    precondition requires; fixed by normalizing via `mdformat.text(...)`
    before the recursive `from_text` call.
  - `various_models.py` cleanup (done by repo owner mid-session): removed
    redundant/incorrect `@markdown(...)` redecoration on classes that
    already inherit correct `_metadata` from their `MarkdownSection1/2/3`
    base (the redecoration was overwriting, not merging, `_metadata`,
    silently breaking tag validation for `CharacteristicInformation`
    et al.); kept `@alias` where still needed.
  - New tests: `tests/models/md/test_markdown_section.py` (7 cases: no-extent,
    end-of-input fallback, nested-deeper-heading inclusion, sibling-stops,
    ancestor-stops, plus parametrized h1/h2/h3-stop and h4/h5/h6-don't-stop);
    `tests/models/md/test_markdown_str.py` expanded with `get_extent`
    line-count-contract tests and `from_text`/`process_field` tests using
    fixed-extent test doubles (`_FixedExtentField`/`_TwoLineField`/
    `_OneLineField`) to isolate the cursor/distribution logic from real
    markdown-heading parsing.
- Next (superseded by the entry below — kept for history): fix
  `MarkdownSection.from_text` (delegate to `MarkdownStr.from_text` after
  heading-triple validation), then rewrite `test_main_document_from_text`
  against realistic multi-heading input.


#### 2026-08-10T19:00:00.000Z - (continued)

- Completed: Fixed the two items from the "Next" list above, plus a bug
  discovered while prototyping the first fix:
  - `MarkdownStr.from_text`: the not-yet-consumed remainder was tracked as
    an integer `cursor` into the *original* `text.splitlines()`, and the raw
    (un-normalized) substring `"\n".join(lines[cursor:])` was passed straight
    into `process_field`/`get_extent`. A raw substring of an
    already-`mdformat`-compliant document is not itself guaranteed to be
    `mdformat`-compliant (e.g. it can start with a blank line `mdformat`
    would strip), which broke `get_extent`'s precondition assertion as soon
    as real nested-heading content (not the fixed-extent test doubles) was
    exercised — this was exactly the "known caveat" flagged in the previous
    entry, confirmed as a real blocker, not a hypothetical one. Fixed by
    replacing `cursor` with a `remaining_text` **string** that is
    re-normalized via `mdformat.text(...)` after every field consumes its
    `extent` lines, so it is always `mdformat`-compliant by construction
    before the next field's `get_extent` call. The trailing completeness
    check changed from `cursor == len(lines)` to `remaining_text == ""`.
  - `MarkdownSection.from_text`: replaced the
    `field_type.from_text("TODO : text from 4th token")` placeholder.
    Resolved the previously-open design question (whether child fields
    should only see the body after the heading) as **yes**: after
    validating the heading triple against `cls._metadata`, the heading's own
    line span (`tokens[0].map[1]`) is stripped off, the remainder is
    `mdformat`-normalized, and delegated to `super().from_text(body)` (i.e.
    `MarkdownStr.from_text`, resolved via cooperative `super()` with `cls`
    still bound to the concrete subclass) for the actual recursive field
    population. Renamed the parameter `v` -> `text` for consistency with
    `MarkdownStr.from_text`.
  - Per explicit repo-owner request, `_value` is now set to the heading's
    **inline content** (`tokens[1].content.strip()`, i.e. the raw markdown
    source between the heading markers) rather than the section's full raw
    text, for both the leaf and composite branches — this is what will let
    a future `__str__` override re-emit `"## " + self._value` instead of
    re-deriving the heading from nested fields. Verified empirically that
    `.content` preserves inline formatting markup verbatim (e.g.
    `"This is a *heading* with **strong** formatting"` round-trips through
    `_value` unchanged, since markdown-it's `inline` token keeps the raw
    source in `.content` and only its `.children` holds the structurally
    parsed form) — added a regression assertion for this
    (`### *Goal* In Context`) in the rewritten test below. Note this is a
    deliberate trade-off for leaf sections: any body text after a leaf
    section's heading is no longer retained anywhere by `from_text` (full
    round-trip fidelity stays opt-in/out of scope per this feature's Scope
    section).
  - Rewrote `tests/models/md/test_markdown_str.py::test_main_document_from_text`
    to use a realistic, `mdformat`-compliant, two-level-nested document
    (`MainDocument` h1 -> `CharacteristicInformation`/`RelatedInformation`
    h2 -> their h3 leaf children) instead of the stale hardcoded
    `"abc"`/single-line-input assertions, checking each `_value` against the
    section's actual heading title.
  - Moved `various_models.py` from
    `src/biz/dfch/specmgr/models/md/various_models.py` to
    `tests/models/md/various_models.py` (repo-owner request): it is a
    test-only fixture model tree, not production code. Updated its internal
    imports to absolute (`biz.dfch.specmgr.models.md....`) since it no
    longer lives inside that package, and updated
    `test_markdown_str.py`'s import to a relative `from .various_models import ...`.
  - Full suite: 349 passed, 0 failed (previously 349 passed, 1 known
    failure). `ruff format --check`/`ruff check` clean on every file touched
    this entry.
- Next (superseded by the entry below — kept for history): fix
  `MarkdownSection`/`MarkdownStr` rendering (`__str__`) so a composite
  section re-emits its own heading, not just its children's text.


#### 2026-08-10T18:00:00.000Z - (continued, part 2)

- Completed: Added `MarkdownSection.__str__`, overriding
  `MarkdownStr.__str__`. Derives the heading level from `cls._metadata['tag']`
  (`_HEADING_TAGS.index(tag) + 1`), reconstructs `"#" * level + " " + self._value`, and — only if the section declares nested fields — appends
  `super().__str__()` (the children's already-`mdformat`-normalized
  concatenation) after a blank line, then re-normalizes the whole thing with
  `mdformat.text(...)`. A leaf section (no nested fields) renders just its
  reconstructed heading line, per the trade-off already made in
  `from_text` (see previous entry) — deliberately not attempting to recover
  body text that `from_text` never retained.
  - Confirmed as a side effect that `MarkdownSection.name` (the
    `computed_field` that re-parses `str(self)` looking for a heading) now
    also works correctly for composite sections — it previously found no
    heading in `str(self)` and effectively couldn't have worked, though no
    test exercised it before now.
  - New tests: `tests/models/md/test_markdown_section.py::TestMarkdownSectionStr`
    (3 cases) — a leaf section re-emits its own heading; inline formatting
    markup inside a leaf heading (`*Emphasized*`) round-trips through
    `__str__` verbatim; a full `MainDocument` fixture's `str()` reproduces
    every descendant heading (h1 through both h2/h3 branches), not just the
    leaf headings `MarkdownStr.__str__` alone would have produced.
  - Full suite: 352 passed, 0 failed (349 -> 352 with the new tests).
    `ruff format --check`/`ruff check` clean on every file touched this
    entry (same pre-existing, unrelated `F841` as before).
- Next (superseded by the entry below — kept for history): reconcile
  Requirements/Acceptance Criteria/Task List with the actual
  implementation, and decide whether leaf sections need a second field to
  retain body content.


#### 2026-08-10T17:00:00.000Z - (continued, part 3)

- Completed: Corrected a design error in the previous two entries, caught
  by the repo owner: `MarkdownSection._value` was being set to the
  heading's inline content for **every** section, leaf and composite alike
  — which meant a leaf section's body text (there being no nested field to
  hold it) was silently and permanently dropped by `from_text`, something
  the previous entries flagged as a "deliberate trade-off" rather than
  recognizing as a straightforward bug. Fixed:
  - `MarkdownSection.from_text`: the leaf branch (`not field_names`) now
    sets `instance._value = text` — the complete extent `from_text`
    received, heading and body verbatim — exactly like the base
    `MarkdownStr.from_text` leaf case. The composite branch is unchanged
    (still stores only the heading's inline content), since a composite
    section's body is already fully represented, recursively, by its
    nested fields all the way down to whichever leaf(ves) ultimately hold
    it in full; storing the full extent on the composite too would just
    duplicate what its children already carry.
  - `MarkdownSection.__str__`: the leaf branch now defers to
    `super().__str__()` (`MarkdownStr.__str__`'s leaf case, which returns
    `_value` unchanged) instead of reconstructing `"#" * level + " " + self._value` — since `_value` already *is* the full rendered section
    now, reconstructing the heading on top of it would have doubled it up.
    The composite branch is unchanged.
  - Net effect: `str(instance)` is now a full, byte-exact round-trip of
    whatever `from_text` consumed, verified end-to-end against the
    `various_models.py` fixture (`str(MainDocument.from_text(text)) == text`, exactly). This resolves the "leaf body text is silently
    dropped"/"round-trip fidelity" caveat from the previous two entries —
    it was a bug in this session's own work, not an inherent, pre-existing
    limitation of the engine.
  - Updated the 4 now-incorrect assertions this design error had baked
    into: `test_main_document_from_text`
    (`tests/models/md/test_markdown_str.py`) now checks each leaf field's
    `_value` against its full heading+body text and adds a
    `str(doc) == text` round-trip assertion; the 3
    `TestMarkdownSectionStr` cases (`tests/models/md/test_markdown_section.py`)
    now assert full-extent round-trips instead of heading-only output
    (renamed accordingly:
    `test_leaf_section_reemits_its_complete_extent_verbatim`,
    `test_composite_document_reemits_every_heading_and_body`).
  - Full suite: 352 passed, 0 failed (same count as before — this was a
    correction, not new coverage). `ruff format --check`/`ruff check`
    clean on every file touched this entry (same pre-existing, unrelated
    `F841` as before).
- Next (superseded by the entry below — kept for history): reconcile
  Requirements/Acceptance Criteria/Task List with the actual
  implementation; the leaf-body-text question from previous entries is now
  resolved and removed from "Next".


#### 2026-08-10T16:00:00.000Z - (continued, part 4)

- Completed: Per repo-owner request, `MarkdownSection.from_text` now
  honours `@alias` (previously `_alias_metadata`, set by `@alias`, was
  inert class data — nothing ever checked it against the actual parsed
  heading text):
  - Added `src/biz/dfch/specmgr/models/md/alias_match.py`: `match_alias(cls, heading_text) -> bool`, encapsulating the three `AliasType` comparisons
    (`LITERAL`: exact string equality, case-sensitive, no normalization,
    per explicit repo-owner direction — "LITERAL means LITERAL";
    `SPACE_SEPARATED`: equality against `space_separated_name(cls.__name__)`,
    a new PascalCase -> title-case-with-spaces helper; `REGEX`: `re. fullmatch` against the declared pattern), plus the policy that a class
    with **no** `@alias` metadata at all always matches — `@alias` is
    opt-in per class, not mandatory on every `MarkdownSection` subclass.
  - Wired it into `MarkdownSection.from_text`: right after the existing
    `@markdown` type/tag heading-triple validation (as requested, so the
    two checks read as one contiguous block), asserts `match_alias(cls, heading_text)` before branching on leaf vs. composite. Moved the
    `heading_text = t_mid.content.strip()` computation earlier so it is
    available to this assertion in both branches (previously only computed
    in the composite branch).
  - This immediately surfaced two already-wrong `@alias` values in
    `tests/models/md/various_models.py` that had never been checked against
    anything: `GoalInContext`'s `@alias(value="Goats in Coats", ...)` and
    `CharacteristicInformation`'s `@alias(value="characteristic_information", ...)`, neither of which matched the fixture documents' actual heading
    text used throughout `test_markdown_str.py`/`test_markdown_section.py`
    (`"*Goal* In Context"` and `"Characteristic Information"` respectively).
    Corrected both literal values to match (per repo-owner direction:
    "fix the alias, but make new tests that verify it is working").
    `Scope`/`Notes`/`Assumptions`/`RelatedInformation`/`MainDocument` declare
    no `@alias` at all and were therefore unaffected (nothing to honour).
  - New tests: `tests/models/md/test_alias_match.py` (11 cases) — unit tests
    for `space_separated_name` and every `match_alias` branch (no-alias
    always matches; `LITERAL` match/mismatch/case-sensitivity/no-trailing-
    parenthetical-stripping; `SPACE_SEPARATED` match/mismatch; `REGEX`
    match/mismatch). `tests/models/md/test_markdown_section.py:: TestMarkdownSectionAliasEnforcement` (4 cases) — `from_text` accepts a
    heading matching a declared `@alias`, rejects one that doesn't, accepts
    any heading text for a class with no `@alias`, and (end-to-end) rejects
    a `MainDocument` fixture document whose `CharacteristicInformation`
    heading doesn't match its `@alias`.
  - Full suite: 367 passed, 0 failed (352 -> 367 with the 15 new tests).
    `ruff format --check`/`ruff check` clean on every file touched this
    entry (same pre-existing, unrelated `F841` as before).
- Next: see "Next" above — reconcile Requirements/Acceptance
  Criteria/Task List with the actual implementation (now including
  `alias_match.py`); the leaf-body-text question is resolved; `@alias`'s
  `REGEX` branch is unit-tested but not yet exercised end-to-end through
  the fixture (added as a new, low-priority "Next" item).
- Notes: This session's work happened interactively/incrementally (small
  scoped diffs, test-driven at each step) rather than against a pre-written
  task list — the Task List below has drifted from what's actually
  implemented and needs reconciliation (see "Next" item 1).


#### 2026-08-08T14:00:00.000Z - (even later)

- Completed: Added a committed, standalone spike-test suite under
  `tests/feat-5-md-model-parser/` proving out several of the design
  primitives from `req_parser.py`'s continuation notes and the PARSING
  STRATEGY, ahead of any real Phase 1 implementation:
  - `test_field_declaration_order.py` — pins down (as a committed test
    rather than an ad hoc chat check) that `pydantic.BaseModel.model_fields`
    preserves field declaration order, including fields inherited from a
    base class.
  - `test_parse_heading.py` / `test_annotations.py` — a `get_section(token, tokens)` helper (plus its `walk_token_tree` depth-first token-tree
    walker building block) that slices a heading's own span out of a flat
    `markdown-it-py` token list. Iterated twice: first only stopped at an
    exact `(type, tag)` match; then fixed, per explicit request, so any
    same-or-shallower heading level terminates the span (an `h1` now
    correctly terminates a preceding `h2`'s section, not just another
    `h2`) — this directly matches the PARSING STRATEGY's step 2b span
    definition ("everything up to the next same-or-shallower-level
    heading").
  - `test_walk_attributes.py` — a `walk_attributes(cls)` generalization of
    the declaration-order guarantee to any plain class (not just
    `pydantic.BaseModel`): walks `cls.__mro__` base-to-derived and merges
    each class's own (non-inherited) `__annotations__`, correctly keeping a
    redeclared attribute at its original position rather than moving it to
    the end. Written because `cls.__annotations__` via attribute lookup, in
    Python ≥3.10, no longer transparently falls back to a base class's
    annotations dict when a subclass declares none of its own — each class
    now gets its own (possibly empty) dict, so a naive walker would
    silently lose inherited attributes without this MRO-merging approach.
  - All 18 tests pass; `ruff format`/`ruff check` clean.
- Next: unchanged from the entry below — formalize `alias` as a real class
  attribute, implement class-name-derived default alias, write
  `parse_document`/`render_document`, generalize `Document`'s remaining
  fields, decide `DocumentFrontMatter`'s typed shape, then start Phase 1 in
  earnest (after revising its task list, which still reflects the
  superseded `Heading`-annotation mechanism).
- Notes: None of this spike work touches `feat-3-md-str-constraints` or
  `feat-4-use-cases`.


#### 2026-08-08T13:00:00.000Z - (later)

- Completed: Revised the design (and ADR 832cd6c1-ef8a-4bfc-990e-a610823f61ae,
  now v1.1.0) after further review of `req_parser.py`: replaced the
  `Annotated[Heading(tag=, alias=)]` field-metadata mechanism with a
  `MarkdownHeading1`..`MarkdownHeading6` base-class hierarchy (level encoded
  structurally, each with a default "no same-or-higher-level heading nested
  beneath me" validator) plus a class-level `alias` for identity matching
  only; every heading-bearing instance now stores its own heading token
  triple verbatim (no more render-time heading resynthesis from metadata),
  so inline formatting inside a heading round-trips for free; settled on a
  sequential cursor-based recursive-descent parsing algorithm (fields walked
  in declaration order, matched by `(tag, alias)`, with a mandatory trailing
  completeness check per nesting level to catch out-of-order/unrecognized
  sections). Applied the resulting fixes to `req_parser.py` and added a
  continuation-notes block at the top of that file for session handoff.
- Next: Formalize the `alias` mechanism as a real class attribute (not a
  comment placeholder); implement class-name-derived default alias; write
  the actual `parse_document`/`render_document` functions; generalize
  `Document`'s remaining fields (`main_success_scenario`, `extensions`,
  `sub_variants`, `open_issues`, `related_information`) to dedicated
  `MarkdownHeading2` subclasses; add `CharacteristicInformation`'s nested h3
  fields; decide `DocumentFrontMatter`'s typed shape; then begin Phase 1
  tasks below in earnest (the task list still reflects the superseded
  `Heading`-annotation mechanism and needs a pass before work starts).
- Notes: This feature intentionally does not touch `feat-3-md-str-constraints`
  or `feat-4-use-cases` content. See `tests/feat-5-md-model-parser/req_parser.py`'s
  top-of-file notes block for the fullest up-to-date design detail.


#### 2026-08-08T12:00:00.000Z - Created

- Completed: Examined `tests/feat-5-md-model-parser/req_parser.py` and
  `uc_example.md`; clarified design (declarative `Heading` metadata, opt-in
  constraints, recursive nesting, typed frontmatter) via Q&A; wrote ADR
  832cd6c1-ef8a-4bfc-990e-a610823f61ae; discovered and resolved a conflict
  with the pre-existing (uncommitted) regex-based plan in
  `feat-3-md-str-constraints/README.md` by keeping the two as separate,
  non-blocking features; created this feature folder.
- Next: Begin Phase 1 (core primitives).
- Notes: This feature intentionally does not touch `feat-3-md-str-constraints`
  or `feat-4-use-cases` content.
