"""DRAFT — Task 1.5 sketch: rebuild the `uc` schema/models on feat-5-md-model-parser's
generic `models/md` engine (`MarkdownStr`/`MarkdownSection1..6`/`MarkdownListItem`/
`MarkdownFrontmatter`).

STATUS: design sketch only, 2026-08-11. NOT wired into `src/`, not tested, not
lint-checked, imports may not even resolve as-is. Intended purely for design
review before Task 1.5 is actually implemented (one class per file, under
either `uc/models/v1/` in place or a new `uc/models/v2/` -- open decision,
see the bottom of this file and feat-4-use-cases/README.md's Task 1.5 entry).

--------------------------------------------------------------------------
IMPORTANT FINDING (blocks a literal "full rebuild" as originally scoped)
--------------------------------------------------------------------------
Cockburn's compound step/action numbering ("3a1.", "3a2.", "3a3." under an
"### 3a. <condition>" heading) is NOT valid CommonMark ordered-list syntax
(an ordered marker must be pure digits + "." /")" -- "3a1" has a letter in
it). Verified empirically: `MarkdownIt().parse(...)` tokenizes the whole
"3a1. ... \\n3a2. ... \\n3a3. ..." block as a single `paragraph_open`/
`inline`/`paragraph_close`, not `ordered_list_open`/`list_item_open`. By
contrast, Main Success Scenario's steps ("1. Buyer calls...", "2. ...")
*are* valid ordered-list markers and tokenize as a real `ordered_list_open`.

Consequences for this draft:
  1. `MainSuccessScenario.steps` maps cleanly onto `list[MarkdownListItem]`
     (see `Step` below) -- and, as a bonus, Task 1.3B's old "steps must be
     numbered 1, 2, 3, ... contiguously" `model_validator` becomes
     structurally unnecessary: a genuine CommonMark ordered list has no
     representable gap/duplicate/out-of-order state to validate against.
  2. `Extension.actions`'s compound numbering CANNOT be parsed via
     `list[MarkdownListItem]` at all -- markdown-it never sees a list there.
  3. Worse, `Extensions`/`SubVariations`'s own per-item h3 headings
     ("### 3a. ...", "### Step 1: ...") are *dynamically named per document*
     (their titles are use-case-specific data, not a fixed template field
     name) -- feat-5's own REQ-007 note already flagged that the generic
     engine has "no repeated/list section concept yet" for this. So even
     the *outer* Extension-per-h3 decomposition, not just action-numbering,
     is out of reach for `MarkdownStr.from_text`'s statically-declared-field
     model as it stands today.

Given that, `Extensions`/`SubVariations` are modelled below exactly like
feat-5's own `tests/models/md/test_uc_example.py` fixture already does:
leaf `MarkdownSection2`s, whole heading+body extent stored verbatim in
`_value`. A *second*, separate, non-generic-engine parsing pass then
recovers the typed `Extension`/`ExtensionAction`/`SubVariation` structure
(and re-runs Task 1.3B's compound-numbering/step-reference-resolution
invariants) from that leaf's raw text -- see `parsed_extensions`/
`parsed_sub_variations` below. This reuses the *existing*, already-tested
regex patterns from `uc/models/v1/parser.py` (`_EXTENSION_HEADING_PATTERN`,
`_NUMBERED_ITEM_PATTERN`, ...) and the *existing*, already-tested
`Extension`/`ExtensionAction`/`SubVariation` Pydantic models unchanged --
only the *outer* document structure (frontmatter, top-level sections,
Characteristic Information's ~15 h3 fields, Main Success Scenario's real
list) moves onto the new engine. This is a hybrid, not the clean full
replacement Task 1.5 was originally scoped as -- see the "Open decision"
block at the bottom.
"""

from __future__ import annotations

import re
from typing import Literal

from biz.dfch.specmgr.models.md.alias import alias
from biz.dfch.specmgr.models.md.alias_type import AliasType
from biz.dfch.specmgr.models.md.frontmatter import MarkdownFrontmatter
from biz.dfch.specmgr.models.md.markdown_list_item import MarkdownListItem
from biz.dfch.specmgr.models.md.markdown_section1 import MarkdownSection1
from biz.dfch.specmgr.models.md.markdown_section2 import MarkdownSection2
from biz.dfch.specmgr.models.md.markdown_section3 import MarkdownSection3

# Reused as-is (unchanged) from the current custom-parser implementation --
# these already express the compound-numbering/cross-reference invariants
# (Task 1.3B) the generic engine has no equivalent for.
from biz.dfch.specmgr.uc.models.v1.extension import Extension
from biz.dfch.specmgr.uc.models.v1.sub_variation import SubVariation

# --------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------


class UcFrontmatter(MarkdownFrontmatter):
    """Use-case frontmatter, narrowing the generic `MarkdownFrontmatter` base.

    Replaces `uc/models/v1/use_case_frontmatter.py`'s standalone
    `UseCaseFrontmatter`, which re-declared `id`/`version`/`created`/
    `updated`/`status` from scratch. Two things are narrowed beyond the
    base's free-form defaults, since the old model was stricter here:
    `id`'s `uc-NNN` pattern and `status`'s closed five-value vocabulary.
    """

    type: Literal["uc"] = "uc"
    id: str = ""  # overrides base's `str | None = None`; still validated below

    _ID_PATTERN = re.compile(r"^uc-[0-9]+$")
    _ALLOWED_STATUS = {"draft", "proposed", "accepted", "deprecated", "superseded"}

    # NOTE: sketch only -- real implementation would use `field_validator`,
    # omitted here for brevity. `status` inherits the base's free-form
    # `str = "draft"` default; narrowing it to `_ALLOWED_STATUS` needs its
    # own `field_validator`, same shape as `AdrFrontmatter.status`'s.


# --------------------------------------------------------------------------
# Small reusable base classes (not in feat-5 itself -- convenience additions)
# --------------------------------------------------------------------------


class BulletListSection(MarkdownSection3):
    """An h3 section whose entire body is a single bullet list of plain strings.

    Covers `Preconditions`/`SuccessEndCondition`/`FailedEndCondition`/
    `SecondaryActors`/`ChannelsToPrimaryActor`/`ChannelsToSecondaryActors`/
    `RelatedUseCases` below -- all "### Heading\\n\\n- item\\n- item" shaped.
    Unlike `tests/models/md/test_uc_example.py`'s fixture (which leaves
    these as opaque leaf blobs, sufficient only to *prove* the engine), this
    recovers the actual `list[str]` structure the old v1 models had.
    """

    items: list[MarkdownListItem]

    @property
    def values(self) -> list[str]:
        """Plain-string view of every bullet, marker-free."""
        return [item.text for item in self.items]


class ProseSection(MarkdownSection3):
    """An h3 section whose body is a single free-text block (no list).

    Covers `GoalInContext`/`Scope`/`Level`/`PrimaryActor`/`Trigger`/
    `Frequency`/`Priority`/`PerformanceTarget` below. A leaf `MarkdownSection`
    stores its *whole* extent (heading + body) verbatim in `_value` (see
    `MarkdownSection.from_text`'s leaf branch) -- `body` strips the heading
    line back off for callers that just want the prose.
    """

    @property
    def body(self) -> str:
        lines = self._value.splitlines()[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
        return "\n".join(lines).strip()


# --------------------------------------------------------------------------
# Characteristic Information's ~15 h3 fields, in document order
# --------------------------------------------------------------------------
# Every heading in the real document carries a "(required)"/"(optional)"
# suffix (see `tests/feat-5-md-model-parser/uc_example.md`), so each needs an
# explicit `AliasType.LITERAL` alias -- `@alias`'s default
# `AliasType.SPACE_SEPARATED` auto-derivation can't express that suffix.
# (Same pattern already proven in `tests/models/md/test_uc_example.py`.)


@alias(value="Goal in Context (required)", type=AliasType.LITERAL)
class GoalInContext(ProseSection): ...


@alias(value="Scope (required)", type=AliasType.LITERAL)
class Scope(ProseSection): ...


@alias(value="Level (required)", type=AliasType.LITERAL)
class Level(ProseSection):
    _ALLOWED = {"Summary", "Primary task", "Subfunction"}
    # NOTE: sketch only -- a real `field_validator`/`model_validator` would
    # check `self.body in self._ALLOWED`, porting forward the old
    # `CharacteristicInformation.validate_level` check.


@alias(value="Preconditions (required)", type=AliasType.LITERAL)
class Preconditions(BulletListSection): ...


@alias(value="Success End Condition (required)", type=AliasType.LITERAL)
class SuccessEndCondition(BulletListSection): ...


@alias(value="Failed End Condition (optional)", type=AliasType.LITERAL)
class FailedEndCondition(BulletListSection): ...


@alias(value="Primary Actor (required)", type=AliasType.LITERAL)
class PrimaryActor(ProseSection): ...


@alias(value="Secondary Actors (optional)", type=AliasType.LITERAL)
class SecondaryActors(BulletListSection): ...


@alias(value="Trigger (required)", type=AliasType.LITERAL)
class Trigger(ProseSection): ...


@alias(value="Frequency (optional)", type=AliasType.LITERAL)
class Frequency(ProseSection): ...


@alias(value="Priority (optional)", type=AliasType.LITERAL)
class Priority(ProseSection): ...


@alias(value="Performance Target (optional)", type=AliasType.LITERAL)
class PerformanceTarget(ProseSection): ...


@alias(value="Channels to Primary Actor (optional)", type=AliasType.LITERAL)
class ChannelsToPrimaryActor(BulletListSection): ...


@alias(value="Channels to Secondary Actors (optional)", type=AliasType.LITERAL)
class ChannelsToSecondaryActors(BulletListSection): ...


@alias(value="Related Use Cases (optional)", type=AliasType.LITERAL)
class RelatedUseCases(BulletListSection):
    """Each bullet is "Superordinate: ..." or "Subordinate: ..., ...".

    The generic engine has no way to declare "exactly one bullet starting
    with a fixed label" as a structural field (unlike the old model's
    dedicated `superordinate: str | None` / `subordinate: list[str] | None`
    fields) -- so this parses `.values` on demand instead, mirroring the old
    `_RELATED_USE_CASE_BULLET_PATTERN` regex.
    """

    _LABEL_RE = re.compile(r"^(?P<label>Superordinate|Subordinate):\s*(?P<value>.+)$", re.IGNORECASE)

    @property
    def superordinate(self) -> str | None:
        for value in self.values:
            m = self._LABEL_RE.match(value)
            if m and m.group("label").lower() == "superordinate":
                return m.group("value").strip()
        return None

    @property
    def subordinate(self) -> list[str]:
        for value in self.values:
            m = self._LABEL_RE.match(value)
            if m and m.group("label").lower() == "subordinate":
                return [v.strip() for v in m.group("value").split(",")]
        return []


@alias(value="Characteristic Information (required)", type=AliasType.LITERAL)
class CharacteristicInformation(MarkdownSection2):
    """All metadata/context about the use case.

    Field order mirrors the document's own h3 heading order exactly --
    `MarkdownStr.from_text` slices the section's body sequentially.
    """

    goal_in_context: GoalInContext
    scope: Scope
    level: Level
    preconditions: Preconditions
    success_end_condition: SuccessEndCondition
    failed_end_condition: FailedEndCondition | None = None
    primary_actor: PrimaryActor
    secondary_actors: SecondaryActors | None = None
    trigger: Trigger
    frequency: Frequency | None = None
    priority: Priority | None = None
    performance_target: PerformanceTarget | None = None
    channels_to_primary_actor: ChannelsToPrimaryActor | None = None
    channels_to_secondary_actors: ChannelsToSecondaryActors | None = None
    related_use_cases: RelatedUseCases | None = None


# --------------------------------------------------------------------------
# Main Success Scenario -- the one part of the document that IS a real
# CommonMark ordered list, so it genuinely benefits from the new engine.
# --------------------------------------------------------------------------


class Step(MarkdownListItem):
    """One main-success-scenario step.

    No extra fields: `.text` (inherited) is the description, and the step's
    number is simply its 1-based position in `MainSuccessScenario.steps` --
    not a stored field. See the module docstring's point 1: a genuine
    CommonMark ordered list is contiguous by construction, so there is no
    gap/duplicate/out-of-order state left to validate -- Task 1.3B's old
    `MainSuccessScenario.validate_steps_numbered_contiguously` becomes
    structurally unnecessary here, not merely "ported forward".
    """


@alias(value="Main Success Scenario (required)", type=AliasType.LITERAL)
class MainSuccessScenario(MarkdownSection2):
    steps: list[Step]

    def numbered_steps(self) -> list[tuple[int, str]]:
        """`(1-based position, description)` pairs, e.g. for sequence-diagram generation."""
        return [(i, step.text) for i, step in enumerate(self.steps, start=1)]


# --------------------------------------------------------------------------
# Extensions / Sub-Variations -- leaf sections (see module docstring), with
# a second, non-generic-engine parse pass recovering typed structure.
# --------------------------------------------------------------------------

_EXTENSION_HEADING_PATTERN = re.compile(r"^###\s+(?P<step_reference>[0-9]+[a-z]?)\.\s*(?P<condition>.+)$")
_NUMBERED_ITEM_PATTERN = re.compile(r"^(?P<number>[0-9]+[a-z]?[0-9]*)\.\s+(?P<description>.+)$")
_SUB_VARIATION_HEADING_PATTERN = re.compile(r"^###\s+Step\s+(?P<step_reference>[0-9]+):\s*.+$", re.IGNORECASE)
_BULLET_ITEM_PATTERN = re.compile(r"^-\s+(?P<text>.+)$")


@alias(value="Extensions (optional)", type=AliasType.LITERAL)
class Extensions(MarkdownSection2):
    """Leaf: dynamically-named h3 sub-headings are inert text to the generic engine.

    `parsed_items` recovers the typed `list[Extension]` (see module
    docstring) via a small dedicated regex pass over `self.body`, reusing
    `Extension`/`ExtensionAction`'s existing pydantic validation
    (compound-numbering contiguity, Task 1.3B) unchanged.
    """

    @property
    def body(self) -> str:
        return "\n".join(self._value.splitlines()[1:]).strip()

    def parsed_items(self) -> list[Extension]:
        # Sketch: split `self.body` on `_EXTENSION_HEADING_PATTERN` lines into
        # per-heading blocks, `_NUMBERED_ITEM_PATTERN`-match each subsequent
        # line into `(number, description)` pairs, then construct
        # `Extension(step_reference=..., condition=..., actions=[ExtensionAction(...), ...])`
        # per block -- i.e. the same shape as `uc/models/v1/parser.py`'s
        # `_parse_extension`/`_parse_numbered_items`, just operating on this
        # leaf's own extracted body text instead of a heading-outline-tree
        # node. Left unimplemented in this sketch; see module docstring.
        raise NotImplementedError("sketch only -- port _parse_extension/_parse_numbered_items here")


@alias(value="Sub-Variations (optional)", type=AliasType.LITERAL)
class SubVariations(MarkdownSection2):
    """Leaf, for the same reason as `Extensions`. `parsed_items` -> `list[SubVariation]`."""

    @property
    def body(self) -> str:
        return "\n".join(self._value.splitlines()[1:]).strip()

    def parsed_items(self) -> list[SubVariation]:
        raise NotImplementedError("sketch only -- port _parse_sub_variation here")


@alias(value="Open Issues (optional)", type=AliasType.LITERAL)
class OpenIssues(MarkdownSection2):
    """A plain bullet list, no sub-headings -- this ONE maps cleanly onto the engine."""

    items: list[MarkdownListItem]

    @property
    def values(self) -> list[str]:
        return [item.text for item in self.items]


@alias(value="Notes (optional)", type=AliasType.LITERAL)
class Notes(BulletListSection): ...


@alias(value="Assumptions (optional)", type=AliasType.LITERAL)
class Assumptions(BulletListSection): ...


@alias(value="Related Information (optional)", type=AliasType.LITERAL)
class RelatedInformation(MarkdownSection2):
    notes: Notes | None = None
    assumptions: Assumptions | None = None


# --------------------------------------------------------------------------
# Root document
# --------------------------------------------------------------------------


@alias(value=".+", type=AliasType.REGEX)
class UseCase(MarkdownSection1):
    """Top-level use case document: an h1 title plus the h2 sections above.

    Permissive `.+` regex `@alias` since a use case's title is
    document-specific data (same reasoning as
    `tests/models/md/test_uc_example.py`'s own `UseCase`).

    NOTE: frontmatter is *not* a field here -- same split as the generic
    engine's own convention (`MarkdownFrontmatter`/REQ-006): the caller
    strips/parses `---...---` via `python-frontmatter` first and constructs
    `UcFrontmatter` separately, then calls `UseCase.from_text` on
    `.content` only. A real implementation would likely pair the two in a
    small wrapper (e.g. `UcDocument(frontmatter: UcFrontmatter, body: UseCase)`),
    mirroring how `models.adr.v1.Adr` already pairs `AdrFrontmatter`+`AdrBody`.
    """

    characteristic_information: CharacteristicInformation
    main_success_scenario: MainSuccessScenario
    extensions: Extensions | None = None
    sub_variations: SubVariations | None = None
    open_issues: OpenIssues | None = None
    related_information: RelatedInformation | None = None

    def validate_extension_and_sub_variation_references(self) -> None:
        """Port of Task 1.3B's `UseCase`-level cross-reference check.

        Once `Extensions.parsed_items`/`SubVariations.parsed_items` are
        implemented, this would resolve every `Extension`/`SubVariation`
        `step_reference` against `{i for i, _ in self.main_success_scenario
        .numbered_steps()}`, exactly like the current
        `_validate_unique_and_resolvable` helper in `uc/models/v1/use_case.py`
        -- unchanged in spirit, just re-pointed at the new accessors.
        """
        raise NotImplementedError("sketch only")


# --------------------------------------------------------------------------
# Open decisions Task 1.5 needs to make before implementation (not yet
# resolved by this sketch -- flagging for repo-owner review):
#
# 1. Accept the hybrid shape above (generic engine for the outer document,
#    a small dedicated regex pass for Extensions/Sub-Variations), OR
# 2. Change the on-disk document format so extension actions become *real*
#    CommonMark ordered lists (e.g. "1. (3a1) Company informs buyer...",
#    embedding the compound reference as text instead of as the list
#    marker), unlocking native `list[MarkdownListItem]` there too -- but
#    this changes `uc_schema.json`/`uc_example.md`/every future use-case
#    document's literal Markdown shape, arguably warranting its own ADR
#    (schema/format-level, not just an implementation swap -- see
#    AGENTS.md's ADR-vs-feature-log criterion), and
# 3. Whether Extensions/Sub-Variations decomposition-by-dynamic-heading is
#    instead a capability gap worth raising back with feat-5 (a "repeated
#    section" primitive alongside its existing "repeated list item"
#    primitive) rather than solved locally in `uc`'s own models -- feat-5 is
#    closed, so this would be new, separate follow-up work there, not a
#    reopening of it.
#
# This sketch implements option 1 (least invasive, reuses existing
# tested code) but does not implement `parsed_items`/`validate_extension_
# and_sub_variation_references` -- those are real work for Task 1.5 itself,
# left as `NotImplementedError` here since they're routine porting, not a
# design question.
# --------------------------------------------------------------------------
