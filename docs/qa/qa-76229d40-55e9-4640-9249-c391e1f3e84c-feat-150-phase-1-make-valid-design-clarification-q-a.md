---
classification: null
created: '2026-09-25 07:03:16.139+02:00'
id: 76229d40-55e9-4640-9249-c391e1f3e84c
status: draft
type: qa
updated: '2026-09-25 08:07:07.181+02:00'
version: 1.0.0
---

# feat-150 Phase 1 (make_valid) Design Clarification Q&A

## General

### Introduction

This Q&A captures design-clarification questions raised while reviewing
`.specmgr/feat/feat-150-mcp-lifecycle-commands/README.md` Phase 1 (the
`make_valid` MCP prompt + `doc-fixer` subagent + `/make-valid` command),
ahead of folding any resulting decisions back into that plan. Conducted as a
single discussion between the requester and the assisting agent.

### Raw Requirements

None -- this document originates from the ongoing feat-150 planning
discussion itself, not a pre-existing external requirements source.

## Elicitation Context

> **0.0010**: Is `make_valid` the right name for Phase 1's MCP
> prompt/command/agent trio?

Reopened (2026-09-25) after an initial "confirmed as-is" pass: `make_valid`
was not the most idiomatic name. It broke the repo's short, bare-word naming
precedent already established for cross-cutting, type-dispatched tools and
prompts (`validate`, `delete`, `list_references`) -- unlike domain-scoped
prompts, which follow `<verb>_<domain>` (`create_req`, `refine_feat`), this
prompt is cross-cutting (`type` + optional `id`, not tied to one domain) --
and it did not share a verb root with the `doc-fixer` subagent that
implements it (validity achieved vs. what the subagent does).

Decision (user, 2026-09-25): renamed to `repair`/`doc-repairer` throughout.
The MCP prompt is now `general.prompts.repair(type, id=None)`, the OpenCode
command is `/repair` (`.opencode/command/repair.md`), and the OpenCode
subagent is `.opencode/agent/doc-repairer.md`. `repair` pairs naturally with
the existing `validate` tool ("validate, then repair"), and `doc-repairer`
now shares the same verb root as the prompt/command it wraps. Applied
throughout `.specmgr/feat/feat-150-mcp-lifecycle-commands/README.md` before
Phase 1 implementation started.

> **0.0020**: Would an OpenCode Skill (`.opencode/skill/repair/SKILL.md`)
> add value beyond the planned subagent+command, for when an agent
> organically encounters an invalid artifact mid-execution (not via
> explicit `/repair` invocation)?

Yes -- it closes a discovery gap the current Phase 1 scope does not cover.
Per OpenCode's Skills documentation, a skill is listed automatically in
every agent's system prompt (`<available_skills>`, unless denied) and
self-triggered by the model when a task matches its `description` -- unlike
the `/repair` command (needs an explicit human invocation) or the
`doc-repairer` subagent (needs an orchestrator that already knows to
delegate via the `task` tool). No repo precedent exists yet for OpenCode
Skills (`.opencode/agent`, `.opencode/command`, `AGENTS.md` were all
checked; none reference the skill mechanism), so this would be the first.

Tradeoffs: a skill grants no new permissions -- it only helps an agent that
already has adequate `edit`/`write` scope to act on what it loads; and it is
a third copy of the repair instructions to keep in sync with the MCP prompt
and the subagent, unless kept deliberately thin (a trigger `description`
plus "prefer delegating to `doc-repairer` via the `task` tool if available;
otherwise fall back to the condensed host-native loop").

Decision (user, 2026-09-25): add the skill. Implemented as REQ-012 / Task
1.2b in Phase 1 of `.specmgr/feat/feat-150-mcp-lifecycle-commands/README.md`:
a thin `.opencode/skill/repair/SKILL.md` (`name: repair`, singular directory
matching this repo's existing `agent/`+`command/` convention), deferring to
`doc-repairer` via the `task` tool when available rather than re-narrating
its full instructions. Flagged as a known, deliberately deferred gap that
Phase 5's packaging/installer (REQ-009/REQ-010) does not yet distribute the
new `skill/` directory alongside `agent`/`command`.

## Functional Suitability

<!-- Tracked separately as GH issue dfch/biz.dfch.SpecMgr#156 -- out of scope for feat-150-mcp-lifecycle-commands -->
> **1.0010**: Is there any additional or changed functionality that this feature must cover?

Yes -- but maybe this is a different feature altogether. We want to change the qa template, example (and schema if possible). We want to suggest a numbering scheme for questions, as it is shown in this QA.

Each section ("Elicitation Context" and the 9 ISO sections) has a predefined numbering scheme:

- The number format is `<category-digit>.<sequence>` (e.g. `0.0010`).
- `<category-digit>` is a single digit fixed to each of the 10 Q&A-bearing
  sections, in the document's own top-to-bottom order: `0` = Elicitation
  Context, `1` = Functional Suitability, `2` = Performance Efficiency,
  `3` = Compatibility, `4` = Interaction Capability, `5` = Reliability,
  `6` = Security, `7` = Maintainability, `8` = Flexibility, `9` = Safety.
  `General` and `More Information` never hold Q&A pairs, so they take no
  digit.
- `<sequence>` is a 4-digit, zero-padded counter scoped independently per
  section, starting at `0010` and incrementing by `10` for each new
  question added to that section (`0010`, `0020`, `0030`, ...); the step
  of `10` (not `1`) leaves room to slot a later question in between two
  existing ones (e.g. `0015`) without renumbering anything else.
- The number lives in exactly one place: as a bold-markdown prefix on the
  question text itself (`> **N.NNNN**: <question text>`). There is no
  separate copy in the `<!-- ... -->` comment -- that field keeps its
  original, unrelated purpose (free-form context on who/when elicited the
  pair), with no numbering responsibility.
- A number, once assigned, is permanent -- never reused, never
  renumbered, even if its question is later edited or the pair is
  removed; a removed question just leaves a gap, mirroring the
  never-renumber convention this repo already uses elsewhere (e.g. VCR's
  `AC-NNN` acceptance criteria, or a feat plan's "next unused phase
  number, never renumbering existing phases").

<!-- Tracked separately as GH issue dfch/biz.dfch.SpecMgr#156 -- out of scope for feat-150-mcp-lifecycle-commands -->
> **1.0020**: Can we enforce this format with our current MD parser? or do we have to change the parser for this? Delegate to a sub-agent for get this info.

Delegated to a research subagent (`explore`, read-only). Verdict: **partially
enforceable now, and every individual piece is enforceable purely inside
`qa/models/v2/` -- no change to the shared `models/md/` parsing library is
structurally required.** The only real caveat is that no single existing
precedent enforces all four pieces at once; each piece individually is a
small, well-precedented, domain-local addition.

Evidence, piece by piece:

- **The comment and the question are already structured, typed fields, not
  discarded/opaque blobs.** `QaQuestionAnswer` (`qa/models/v2/question_answer.py:150-261`)
  declares `comment: MarkdownComment | None`, `question: MarkdownBlockQuote | None`,
  `answer: QaAnswer | None` -- each independently reachable, each exposing its
  own `.text: str` (comment keeps the `<!-- -->` delimiters; the block quote's
  `>` marker is already stripped, confirmed by
  `tests/qa/models/v2/test_question_answer.py:141`).
- **Regex on the question text alone**: enforceable today via a single
  `field_validator("question")` on `QaQuestionAnswer` matching
  `r"\A\*\*\d\.\d{4}\*\*:\s"` against the start of `question.text` -- modeled
  directly on VCR's `Verifies`/`Coverage` field validators
  (`vcr/models/v1/body.py:115-121,140-146`), which already regex-check a
  sibling markdown leaf's (`MarkdownParagraph`) `.text` the same way. No
  cross-field check against `comment` is needed anymore, now that the number
  lives in exactly one place (see the Decision below 1.0030) -- this is
  strictly simpler than the two-field version originally proposed here.

Net: no `models/md/` change is required to *ship* this. A generic, reusable
"content-regex-constrained leaf" building block (mirroring how `@alias`
already generalizes heading-text matching) would be a nice-to-have
generalization for future domains, not a blocker -- rough shape would be a
new `models/md/_sequence.py` (a `validate_strictly_increasing_by_step`
sibling to `_ordering.py`) plus a small regex-constrained-leaf mixin, on the
order of the existing `alias.py`/`alias_type.py`/`alias_match.py` trio
(~300 lines total) if we ever want it -- but Phase 1 of this idea does not
need it.

Decision (user, 2026-09-25): no strict per-section sequence-step validator
will be built -- the "start at 0010, step by 10" numbering is a human
authoring convention only, not a parser-enforced rule, since a new question
must be insertable between two existing ones later (e.g. `0.0015` between
`0.0010` and `0.0020`) without being rejected by validation.

<!-- Tracked separately as GH issue dfch/biz.dfch.SpecMgr#156 -- out of scope for feat-150-mcp-lifecycle-commands -->
> **1.0030**: What advantage is there to repeating the question number in
> both the HTML comment and the question text itself, rather than putting
> it in just one of the two?

Two real advantages, one real cost, and a genuine open question about
whether the cost is worth it:

- **Rendered-view visibility.** HTML comments render as nothing on GitHub,
  in most markdown previewers, and in PDF/HTML export -- they are visible
  only in raw source/diffs. If the number lived only in the comment, nobody
  reading the *rendered* document could reference "question 1.0020" without
  opening raw source. The question-text copy guarantees the number is
  visible wherever the document is viewed.
- **Resilience against an absent/edited-away comment.** `comment` is
  `MarkdownComment | None` -- genuinely optional per the schema, and its
  documented purpose (the QA template's "context for this Q&A pair, such as
  when/by whom it was elicited") has nothing to do with numbering. A
  hand-editor who omits the comment, or a future tool that strips comments,
  silently loses the number if it lives there alone. The question-text copy
  sits inside content that is otherwise mandatory anyway (every pair has a
  question), so the number can't end up un-numbered that way.
- **Cost**: two copies of the same fact need to stay in sync. Catching
  drift (e.g. a reworded question that keeps a stale prefix) needs the
  cross-field `model_validator` described under 1.0020 -- which is exactly
  the same class of "enforced consistency" you just decided against for the
  step size. That is a genuine tension worth resolving explicitly, not
  papering over.

Given the decision above (favor flexibility over enforced consistency), the
honest recommendation is to make the **question-text prefix the single
source of truth** (it is always present, always visible) and leave the
`<!-- ... -->` comment exactly as originally documented -- free-form,
optional context, with no numbering responsibility and no format
requirement placed on it at all. This drops the need for any cross-field
validator entirely, at the cost of the comment no longer doubling as a
machine-anchored, prose-free number slot.

Decision (user, 2026-09-25): the comment-based duplicate is dropped -- the
number lives **only** in the question text, as a bold-markdown prefix
(`> **N.NNNN**: <question text>`). Bold is safe here: `MarkdownBlockQuote.text`
already preserves raw markdown syntax verbatim (confirmed by this very
document's own `**1.0010**`/`**1.0020**`/`**1.0030**` prefixes round-tripping
through `get_qa` unchanged), so `**...**` is just two literal asterisk
characters as far as any future regex validator is concerned -- it also adds
a genuine, independent benefit beyond visibility: bold visually sets the
number apart from the question prose for a reader scanning quickly, which
the plain, unstyled `<!-- ... -->` comment never did either. The `comment`
field on `QaQuestionAnswer` reverts to its originally documented role only --
free-form, optional context, no numbering responsibility, no format
requirement.

## Performance Efficiency

## Compatibility

## Interaction Capability

## Reliability

## Security

## Maintainability

## Flexibility

## Safety

## More Information

This Q&A is intended to be folded into
`.specmgr/feat/feat-150-mcp-lifecycle-commands/README.md`'s Phase 1 scope
once the open items above are resolved; see that document's Task List for
the authoritative plan.
