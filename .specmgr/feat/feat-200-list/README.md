---
classification: null
created: '2026-10-07T07:48:18.241+02:00'
id: feat-200-list
status: done
type: feat
updated: '2026-10-07T09:28:39.561+02:00'
version: 1.0.0
---

# Feature: Add a glob parameter to list_feat (and other list_ tools) for partial-id lookup

## Plan

### Overview

`list_feat` and the other paged `list_<d>` tools return every artifact in the corpus — there is no way to filter by id. When a user or agent only knows part of an id — "feat-7" without the full `feat-7-<slug>`, or the leading characters of a UUID — the only option is an unfiltered full listing, which for `feat` is also the expensive cold case (feat-187). This feature adds an optional `glob` parameter to `list_feat` that matches against the feature's `id`, and extends the same parameter to the other paged `list_<d>` tools (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs), whose ids are UUIDs and where a known prefix is equally common (e.g. `dead*`). One simple rule — glob-match the full id string — covers both id shapes.

### Requirements

- REQ-001: `list_feat` accepts an optional `glob: str | None = None` parameter; when given, only features whose `id` (`feat-NNN-slug`) matches the glob are returned.

- REQ-002: Each of the other eleven paged `list_<d>` tools (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs) accepts the same `glob` parameter, matching against the document's id (UUID).

- REQ-003: `total`, `max_results`/`offset` paging, `truncated`, and `error_count` are computed on the filtered set, so their meaning is unchanged (a `glob`-given result has `error_count = 0` by construction, since failed rows carry `id=None` and never match — see Design Notes).

- REQ-004: Matching is case-insensitive: the stored id and the pattern are both lowercased before matching, so a pattern may be given in any case. Ids are stored in one canonical lowercase form (`feat` slugs are shape-validated as lowercase, UUIDs are created via `str(uuid.uuid4())`); by-id lookups are exact and case-sensitive, so the case-insensitive glob is a deliberate search-UX choice, not a property of existing lookup behaviour.

- REQ-005: When `glob` is absent (`None`), every tool that receives the parameter (all twelve) behaves exactly as today (byte-identical results and return shape).

### Acceptance Criteria

- [ ] ACC-001: `list_feat(glob="feat-7*")` against a fixture corpus (temp dir with `SPECMGR_FEAT_DIR` overridden, holding a known set of `feat-7*` ids plus non-matching ids) returns exactly the matching features and no others, and `total` equals that count.

- [ ] ACC-002: For a document with a known UUID (e.g. from `docs/req/`), `list_req(glob="<first 4 hex chars>*")` — in any case of the pattern — returns that row and no others.

- [ ] ACC-003: With `glob=None`, all twelve tools' output is unchanged (existing tests stay green, no new drift).

- [ ] ACC-004: Paging composes with the filter: for a pattern with N matches, `offset=N` returns zero rows and `truncated` reflects the filtered total.

- [ ] ACC-005: A corpus containing a broken (failed-to-parse) document: the unfiltered listing still shows its failed row and `error_count` counts it (today's behaviour); for any `glob` the failed row is absent and `error_count = 0`.

### Scope

#### Included

- The `glob` parameter on `list_feat` and the eleven other paged `list_<d>` tools.

- One shared id-filter helper in `general/tools/`.

- Docstring updates and the `docs/MCP.md` regeneration they trigger.

- Unit tests for filtering and its composition with paging.

#### Explicitly Out Of Scope

- Filtering on any field other than `id` (title, status, classification).

- Fuzzy or typo-tolerant matching.

- Changes to `get_<d>`/`parse_<d>` or to resources (listing is a tool, not a resource, ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).

- Any new CLI command.

- `list_adr`: the thirteenth paged `list_<d>` tool, deliberately excluded — ADR is being phased out (issue #46), `AdrSummary` does not subclass `DocSummary`, and `list_adr` produces no failed-to-parse rows.

### Dependencies

#### Depends On

- FEAT feat-187-list-feat-timeout: `list_feat`'s two-stage (dirty/clean `DocCache`) row resolution — `status: done`, dependency satisfied.

### Design Notes

Matching rule. The `glob` value is evaluated with `fnmatchcase(id.lower(), pattern.lower())` — both the stored id and the pattern are explicitly lowercased first. This is deliberate: on POSIX, `fnmatch.fnmatch` is case-sensitive (its `os.path.normcase` is the identity), so the portable case-insensitive form is lowercase-both-sides plus `fnmatchcase`. The case-insensitivity is a deliberate search-UX choice, not an alignment with existing lookups: by-id resolution (`get_<d>` and path scanning) is exact and case-sensitive, and the true shared property is that ids are stored in one canonical lowercase form (`feat` slugs are shape-validated as lowercase via `assert_feat_id`; document UUIDs are created as `str(uuid.uuid4())`). An empty string is a pattern, not an off-switch: `glob=""` matches no id (ids are never empty) and yields a zero-row result; only `glob=None` disables filtering.

Pipeline position. Each `list_<d>` tool builds one summary row per document, then computes `total`, applies `offset`/`max_results` paging, and sets `truncated`. The filter runs on the row list between the row build and the `total` computation, so `total` is the match count and paging keeps its existing meaning on the smaller set. `error_count` is recomputed on the same filtered row list; because failed-to-parse rows carry `id=None` and never match any `glob`, a `glob`-given result has no failed rows and `error_count = 0` by construction (keeping the whole-directory count would allow `error_count > total`). Broken-document discovery — the `repair` workflow's `list_<d>`-based surfacing of failed rows — therefore stays an unfiltered-listing / `ref`-based job: ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 rejected hiding parse failures for exactly this reason. For `feat` specifically the row build is feat-187's two-stage (dirty/clean `DocCache`) resolution — the filter applies to the rows it produces and must not re-scan the filesystem on its own (that would bypass the cache and regress the cold-scan timeout fix) — and during the warmup window a not-yet-fully-parsed broken folder transiently resolves to a healthy row with a real id (so it can match) before converging to an `id=None` failed row; the filter sees whatever its row build produces, healthy or failed.

One shared helper. The filter lives in a single function in `general/tools/` (alongside the other shared list plumbing) and is called by all twelve tools, so the matching rule cannot drift between domains and is tested in one place.

### Related Decisions

- ADR ec9f5262-9912-49d0-903f-fcfb54f28c13: listing is a paged `list_<d>` tool, not a `specmgr://<d>/list` resource — this feature extends those tools' parameter surface.

- ADR 3982712a-a46b-4b2b-809f-9c6925a49b44 (feat-187): `list_feat`'s two-stage dirty/clean `DocCache` — the filter must sit after that resolution (see Design Notes).

### Task List

#### Phase 100: list_feat glob

- [ ] Task 100.100: Add the shared id-glob filter helper in `general/tools/` (lowercase id + pattern, then `fnmatchcase`) with unit tests.
- [ ] Task 100.110: Add the `glob: str | None = None` parameter to `list_feat`, applied after the domain's row build (both cache stages) and before `total`/paging; update the docstring.
- [ ] Task 100.120: Tests for `list_feat` on fixture corpora (temp dir, `SPECMGR_FEAT_DIR` overridden): the `feat-7*` case, filtered `total`/`offset`/`truncated`/`error_count`, uppercase-pattern case-insensitivity, failed-row exclusion for a broken fixture (ACC-005), and unchanged `glob=None` output.

#### Phase 110: Extend to the other list tools

- [ ] Task 110.100: Add the same `glob` parameter to the eleven other paged `list_<d>` tools via the shared helper.
- [ ] Task 110.110: Tests for a UUID-prefix match (e.g. `dead*`) on fixture corpora plus docstring updates and `docs/MCP.md` regeneration.

#### Phase 120: Quality gate

- [ ] Task 120.100: Run `ruff format --check`, `ruff check`, `vulture`, the full `pytest` suite, and the `specmgr docs`/`specmgr mcp-docs` drift checks; update this feature's Progress section.

## Progress

### Current Status

**As of 2026-10-07**: Planning. GitHub issue #200 is open; this feature folder was created from it. No implementation has started.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T09:17:56.462+02:00 - Plan refined (feat-refiner pass)

Refined the plan against the codebase (no implementation): `error_count` is now recomputed on the filtered row list, so a `glob`-given result has `error_count = 0` by construction (failed rows carry `id=None` and never match; broken-document discovery stays an unfiltered-listing / `ref`-based job — new ACC-005); `list_adr` named explicitly out of scope (ADR phase-out, `AdrSummary` not a `DocSummary` subclass, no failed rows); the case-insensitivity rationale corrected (by-id lookups are exact and case-sensitive — ids are merely stored in canonical lowercase — a deliberate search-UX choice); a `### Dependencies` section added with a machine-resolvable `FEAT feat-187-list-feat-timeout` reference; REQ-005's quantifier aligned with ACC-003 ("all twelve"); ACC-001/Task 100.120/Task 110.110 switched from the live repo corpus to fixture corpora (`SPECMGR_FEAT_DIR` overridden, the feat-187 test convention); the Created and Decisions-Made entry timestamps aligned to the frontmatter `created` (`2026-10-07T07:48:18.241+02:00`, the programmatic stamp taken as authoritative over the earlier hand-written clock).

#### 2026-10-07T07:48:18.241+02:00 - Created

Created the feature plan for GitHub issue #200 (an optional `glob` id-filter parameter for `list_feat` and the other paged `list_<d>` tools).

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-10-07T07:48:18.241+02:00 - Parameter named glob; matching is case-insensitive

Issue #200 proposed the name `glob` (alternative: `filter`); `glob` was chosen because it names the matching semantics. Matching was settled as case-insensitive — the stored id and the pattern are both lowercased before `fnmatchcase` — because ids are stored in one canonical lowercase form (`feat` slugs are shape-validated, UUIDs via `str(uuid.uuid4())`); by-id lookups are exact and case-sensitive, so the case-insensitive glob is a deliberate search-UX choice, not an alignment with existing lookup behaviour. An empty-string pattern matches nothing; only `None` disables filtering.

### Related PRs / Commits

- [Issue #200](https://github.com/dfch/biz.dfch.SpecMgr/issues/200): tracking issue for this feature.
