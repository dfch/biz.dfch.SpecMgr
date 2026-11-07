---
status: accepted
date: '2026-09-28'
decision-makers: OpenCode agent + user decision
id: 19ff316b-cd11-41a7-a616-ffd84917da51
version: 1.0.0
---

# Revise the generic update tool's success return to frontmatter plus an optional before/after snippet

## Context and Problem Statement

GitHub issue #153 reports that a wrong-but-in-bounds `offset` to the generic `update` tool's line-range mode (`offset`/`limit`) can silently corrupt a document. `update`'s coordinates address 1-based lines of the frontmatter-stripped body, but the on-disk YAML frontmatter block is variable-length, so a caller that computes an offset as "raw file line number minus an assumed frontmatter length" can land on a structurally similar line (e.g. a blank line instead of the intended list item). `update` is splice-then-validate-whole: such a wrong splice often still passes schema validation, is written, and the success response -- a bare per-domain frontmatter object only, per feature feat-69-update-context's "frontmatter-only" return precedent -- carries no information about which lines were actually dropped and inserted. In the reported incident, the off-by-N corruption was discoverable only by an unprompted manual re-read.

Feature feat-69-update-context established that precedent deliberately: every successful write (`update`, `set_status`, `set_classification`, and every `create_<d>`) returns the frontmatter object only, small and bounded regardless of document size, because append-only documents otherwise drive the response payload up monotonically with every write. This ADR decides whether and how to revise that precedent for `update` specifically: feat-153-off-by-n adopts issue #153's fix #2 and returns a before/after snippet of the touched region alongside the frontmatter, in a new `UpdateResult` wrapper. It records the snippet-size contract the revision rests on -- the snippet is bounded by the touched range, not the document size -- and the whole-body-equivalent range's `snippet=None` exception. It also records that feat-153's companion change on the read surface (the opt-in `numbered` raw-read parameter on every `get_<d>`, fix #4) leaves ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c's `ParseFailureResult` channel unaffected.

## Decision Drivers

- Detection, not prevention: with issue #153's `dry_run` fix explicitly deferred, a wrong `offset` is still written to disk before the caller can act. The only in-band signal that the splice landed where intended is the success response itself, and it must not require an extra `get_<d>` round-trip.
- Keep the response small for the documented use case: feat-69-update-context's core driver (a response bounded regardless of document size) must hold for the localized edits that are `update`'s range mode's documented use case -- the snippet scales with the touched range, not the document.
- Uniform return shape: range mode, whole-body mode, and all 12 whole-body domains return the same wrapper type; the whole-body cases are expressed as `snippet=None`, not as different types.
- Scope the revision to `update` alone: the off-by-N risk is specific to `update`'s `offset`/`limit` splice; `create_<d>`/`set_status`/`set_classification` have no line-range coordinates and keep feat-69's bare-frontmatter return.
- Do not disturb established read-surface precedents: ADR 4ec08dcb-fcb7-4961-abaf-ff7803e2f21d's raw/splice invariant (what the client counts is what the server splices) and ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c's channel (a document that fails to parse never returns raw text) must hold for the new `numbered` reads too.

## Considered Options

- Option 1: Keep feat-69-update-context's frontmatter-only return for `update` (status quo); detection stays the caller's manual `get_<d>(raw=True)` re-read.
- Option 2: Return the frontmatter plus the full before and after body text.
- Option 3: Return the frontmatter plus a hard-capped snippet with elision markers (first/last K lines, "..." in between).
- Option 4 (chosen): Return a new `UpdateResult` wrapper carrying the frontmatter plus an optional `snippet` -- a before/after window of the touched range (dropped lines numbered pre-splice, inserted lines numbered post-splice, up to 2 unchanged context lines per side) -- bounded by the touched range, no hard cap; whole-body mode and the whole-body-equivalent range (`offset=1` + omitted `limit`) return `snippet=None`.

## Decision Outcome

Option 4. The generic `update` tool's success return changes, across all 12 whole-body domains, from the per-domain frontmatter union to a new `UpdateResult` wrapper exposing `frontmatter` (the same per-domain frontmatter object feat-69-update-context returns today) and `snippet: str | None`. The contract:

1. **When the snippet is present.** `snippet` is `None` in exactly two cases: whole-body mode (no `offset`) and the whole-body-equivalent range (`offset=1` + omitted `limit`), which `splice_body` documents as equivalent to the no-range mode and the existing `test_offset_one_equals_whole_body_mode` test pins. Every other range-mode call that *succeeds* returns a non-`None` snippet string (which is the empty string `""` only for a no-op splice on an empty body). This "every other range-mode call" guarantee is scoped to the successful path: once ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f (feat-170-update-edit-parse-failure) composed onto the same `update` surface, a range-mode call can instead return `ParseFailureResult` or `ValidateResult` -- neither of which carries a `snippet` field at all -- so the true composed success-or-failure return type for `update` is `UpdateResult | ParseFailureResult | ValidateResult`, not `UpdateResult` alone; see that ADR's Decision Outcome item 5 for the failure-path members.

2. **What the snippet contains.** Four labeled groups, in this order: (a) up to 2 unchanged context lines immediately above the touched range; (b) the dropped lines -- the before window, empty for a pure insert (`limit=0`) and for the end-of-body append position; (c) the inserted lines -- the after window, empty for a pure delete (empty `content`); (d) up to 2 unchanged context lines immediately below the touched range. Dropped lines are numbered with their **pre-splice** 1-based body-line numbers (they no longer exist afterward, so no post-splice number applies to them); inserted and context lines are numbered with their **post-splice** 1-based body-line numbers, the context lines taken from the post-splice body and clamped at the body's start/end (clamped, not errored, mirroring `window_body`). The two numbering sequences are independent and need not be contiguous or to overlap when the replacement changes the line count; a 1-for-1 replacement shows the same number on both sides only by coincidence.

3. **The exact snippet line format.** Each snippet line is `<marker> <n>: <line text>`: `<marker>` is exactly one character -- `-` for a dropped line, `+` for an inserted line, a space for a context line; `<n>` is the plain decimal line number with no zero padding and no fixed-width alignment; the separator is exactly `": "`; `<line text>` is the line's verbatim text (an empty body line therefore renders as `<marker> <n>: ` with a trailing space -- no empty-line special case). The snippet text is its lines joined with `"\n"` plus a single trailing `"\n"`, or `""` when it contains no lines at all. Equivalently: every snippet line is a 2-character marker prefix (`"- "`, `"+ "`, or `"  "`) prepended to exactly the line a `get_<d>(raw=True, numbered=True)` read prints for that number -- the snippet and the numbered read are one format family. Worked example -- splicing `offset=4`, `limit=1` into a 6-line body whose line 2 is empty and whose lines 3--6 are `## Some Heading`, `(the single old line that was replaced)`, `(unchanged line)`, `(final line)`, replacing the one line with `first new line` / `second new line` / `third new line`, yields exactly this snippet (plus its single trailing newline):

```
  2: 
  3: ## Some Heading
- 4: (the single old line that was replaced)
+ 4: first new line
+ 5: second new line
+ 6: third new line
  7: (unchanged line)
  8: (final line)
```

The `  2: ` line is the empty context line (trailing space); lines 2--3 and 7--8 are post-splice context (space marker, post-splice numbers); the `-` line is the dropped line in pre-splice numbering; the `+` lines are the inserted lines in post-splice numbering. The two lines numbered 4 exist in different numbering spaces -- that is the expected pre-splice/post-splice split, not a defect.

4. **The snippet-size contract.** The snippet's size is bounded by the touched range: at most `limit` dropped lines + `len(content.splitlines())` inserted lines + 4 context lines, and nothing else. There is no hard cap and no elision markers. This deliberately relaxes issue #153 fix #2's "stays small regardless of document size" property -- and feat-69-update-context's same-shape driver -- to "small for the localized edits that are the documented use case": a caller that deliberately splices a large range (short of the whole-body-equivalent exception) receives a proportionally large snippet. The whole-body-equivalent range returns `snippet=None` rather than a document-sized snippet.

5. **Scope.** The revision is scoped to `update` alone: `create_<d>`, `set_status`, and `set_classification` keep feat-69-update-context's bare-frontmatter return unchanged, `delete` keeps its path-string return, and ADR-specific tools remain excluded as always. The already-merged generic `edit` tool (feat-159-edit) is out of scope: its exact-match `old_str`/`new_str` makes the before/after self-evident, and it has no `offset`/`limit` range mode.

6. **The `get_<d>` read surface (companion change, recorded as unaffected).** feat-153's fix #4 adds an opt-in `numbered: bool = False` parameter to every `get_<d>`'s `raw=True` read: when `True`, each body line is prefixed with its 1-based absolute body-line number in the `"<n>: "` form (plain decimal, no padding; a windowed read numbers from the clamped offset `max(1, k)` and never restarts at 1). `numbered` adds no new member to the `get_<d>` return union, and ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c's channel takes precedence over numbering: a numbered read of a document that exists but fails to parse returns `ParseFailureResult`, never numbered text. `numbered=True` combined with `raw=False` raises `ValueError` before any file access -- ahead of the parse-failure channel, mirroring the existing `offset`/`limit`-with-`raw=False` guard -- so a misused argument reports `ValueError` even for a document that fails to parse. A `numbered=False` read remains byte-identical to today's `raw=True` output.

### Consequences

- Good: the off-by-N failure mode of issue #153 becomes visible in-band: the success response itself shows which lines were dropped (with the numbers they had) and which were inserted (with the numbers they have), so a wrong `offset` is detected without an extra `get_<d>` round-trip.
- Good: `numbered=True` reads let the caller derive `offset` coordinates by inspection in the same coordinate space `update` splices in, extending ADR 4ec08dcb-fcb7-4961-abaf-ff7803e2f21d's raw/splice invariant to numbered reads.
- Bad (breaking): `update`'s success return type changes from the per-domain frontmatter union to `UpdateResult` across all 12 whole-body domains; callers and tests that read frontmatter fields directly off the result move to `result.frontmatter`.
- Bad: the snippet can be large for a deliberately large splice -- the bounded-by-touched-range contract trades issue #153's literal "small regardless of document size" for "small for the documented use case".
- Bad: a second documented return-shape asymmetry in the write-tool family: `update` alone returns `UpdateResult` while `set_status`/`set_classification`/`create_<d>` return bare frontmatter -- a future contributor must know `update` is the exception.
- Neutral: `get_<d>`'s healthy-document shape is byte-identical to today (`numbered` defaults off; `numbered=False` unchanged), the `ParseFailureResult` channel is unaffected, and `delete`/`edit`/ADR tools are unchanged.

### Confirmation

Confirmed at the design level during feat-153-off-by-n Phase 1 (2026-09-28): the wrapper shape, the snippet-window algorithm (pre-splice/post-splice numbering split, 2-line context, boundary clamping, the whole-body-equivalent `snippet=None` rule), the exact snippet line format, the snippet-size contract, and the `numbered` parameter contract are pinned in the feature plan's Design Notes and Decisions Made log (2026-09-28 entry), and this ADR is accepted before implementation per the plan's Task 1.3. Unit-level confirmation (the feature plan's ACC-002/ACC-003/ACC-004/ACC-011) happens in feat-153's Phases 2--5, against all 12 whole-body domains, mirroring the confirmation style ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c records for feat-150's Phase 1a. As with that ADR and with 519d1206-4d2a-4500-9046-6db635209996/b399f1ce-ed42-4929-b01c-7a57d18e8014, no live MCP-client round-trip is attempted or recorded as an outstanding commitment.

## Pros and Cons of the Options

### Option 1: Keep the frontmatter-only return for update (status quo)

#### Pros

- No return-shape change, no migration for callers or tests, and feat-69-update-context's precedent stands untouched across all four write-tool families.
- No new windowing algorithm to implement or get wrong.

#### Cons

- Issue #153's exact failure mode remains: a wrong-but-in-bounds `offset` is written with no in-band feedback, and detection depends on an unprompted manual `get_<d>(raw=True)` re-read -- the very thing that failed in the reported incident.
- feat-153's other adopted fixes (#1 documentation, #4 numbered reads) reduce the chance of a wrong offset but cannot detect one after it is written.

### Option 2: Return frontmatter plus the full before and after body text

#### Pros

- Maximum detection: nothing about the splice is hidden.
- No windowing algorithm to get wrong.

#### Cons

- Reintroduces exactly what feat-69-update-context removed: a response payload that grows with document size on every `update` call -- append-only documents (QA transcripts, FEAT READMEs) make that cost monotonic across a session.
- Every localized edit pays the whole-document cost, so the common case becomes the most expensive case.

### Option 3: Return frontmatter plus a hard-capped snippet with elision markers

#### Pros

- Strictly bounded size in every case; satisfies issue #153's literal "stays small regardless of document size" property.

#### Cons

- For the documented use case (localized edits) the cap is never hit, so the machinery -- the cap, the elision markers, and a second reading convention for clients -- buys nothing.
- A large deliberate splice gets an elided snippet that hides exactly the lines a caller most wants to see.
- The whole-body-equivalent range (`offset=1` + omitted `limit`) still needs a `snippet=None` special case anyway, so the cap does not simplify the contract.

### Option 4: Return frontmatter plus a touched-range-bounded optional snippet (chosen)

#### Pros

- Detection is in-band for the documented use case, at a cost proportional to the touched range (dropped + inserted + 4 context lines) rather than the document size.
- A uniform wrapper type across modes and all 12 whole-body domains; the whole-body cases are `snippet=None`, not different types.
- The snippet line format is one family with the `numbered` read prefix: every snippet line is a 2-character marker prefix plus exactly the line a `get_<d>(raw=True, numbered=True)` read prints, so the format is specified and tested in one convention.
- Revises feat-69-update-context's precedent narrowly -- `update` alone, the frontmatter still returned -- rather than overturning it: `create_<d>`/`set_status`/`set_classification` are untouched.

#### Cons

- A deliberately large splice yields a proportionally large snippet (the documented relaxation of "small regardless of document size").
- A second documented return-shape asymmetry in the write-tool family (`update` alone returns a wrapper).
- A breaking change for `update` callers and tests (frontmatter fields move under `result.frontmatter`).

## More Information

- GitHub issue #153 ("Off-by-N line-offset corruption risk in the generic update tool"): https://github.com/dfch/biz.dfch.SpecMgr/issues/153.
- Feature plan and progress: `.specmgr/feat/feat-153-off-by-n/README.md` -- Phase 1's Decisions Made log entry (2026-09-28) records the same finalizations as this ADR's Decision Outcome items 3 and 6, plus the worked examples Phase 2's tests (ACC-002/ACC-004) assert against.
- Feature feat-69-update-context (`.specmgr/feat/feat-69-update-context/README.md`): the "frontmatter-only" return precedent this ADR revises for `update` alone, without superseding it.
- ADR 9080b37c-82b3-4f63-81f1-79641d0bf14c ("Extend the non-raising structured-result workaround to get_<d>'s parse-failure case"): feat-150's `ParseFailureResult` channel, recorded here as unaffected by the `numbered` parameter.
- ADR 4ec08dcb-fcb7-4961-abaf-ff7803e2f21d ("offset/limit coordinates for the generic update tool and get_<d> windowed reads"): the `offset`/`limit` range contract and the raw/splice invariant the snippet and the `numbered` reads build on.
- ADR b8c9bfea-6dcf-4158-bfc5-4ec17abb842f ("Extend the non-raising structured-result workaround to the generic mutation tools' failure cases"): feat-170-update-edit-parse-failure, landed on the same branch after this ADR, adds the `ParseFailureResult`/`ValidateResult` failure-path members to `update`'s return type alongside this ADR's `UpdateResult` success member -- the two ADRs' return-type claims must be read together, not in isolation (see Decision Outcome item 1 above and that ADR's own Decision Outcome item 5).
