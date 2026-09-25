---
status: accepted
date: '2026-09-23'
decision-makers: dfch
id: 8c889262-152b-4b8e-ae2c-75371f7a9edf
version: 1.0.0
---

# Use full ISO 8601 date+time timestamps in all entry headings and frontmatter (accept T or space, write T)

## Context and Problem Statement

specmgr has two kinds of timestamp locations. The first is the `created`/`updated` fields of the whole-body domains' YAML frontmatter, which are system-owned: only the MCP tools write them, via the shared `general.tools._timestamps.now_timestamp()` formatter. The second is the hand/agent-authored dated log-entry headings `{timestamp} ( - | : ) {title}` in the six domains that have them — `tsk`'s `## Recent Updates`, `dec`/`sop`/`vcr`/`sysrs`'s `## Updates`, and `feat`'s `### Updates` and `### Decisions Made`.

As of this decision, strictness is inconsistent across these locations. Frontmatter `created`/`updated` accepts only the full date+time form `yyyy-MM-dd HH:mm:ss.fff` + (`Z` | `±HH:MM`) — date-only, `T`-separated, six-digit-fraction, and timezone-less values are all rejected (feat-38-39-41-43-44 REQ-006/D5). The entry-heading aliases split into strict — `feat` and `sop` require the full date+time form — and lenient — `tsk`, `dec`, `vcr`, `sysrs` accept a bare `yyyy-MM-dd` date or the full form — a deliberate split from feat-38-39-41-43-44 REQ-004 ("SOP/FEAT entries stay date+time-only"). The leniency is what forces `models/md/_ordering.py::validate_newest_first` to carry a mixed-granularity (day-granularity for date-only pairs) comparison rule plus a naive/aware datetime normalization hazard (documented in feat-32-sysrs), and it is what GitHub issue #146 tripped on: an agent authoring a `tsk`-style date-only heading for a `feat` `### Updates` entry hit a parse failure. Templates and instructions actively teach the lenient convention (e.g. `tsk_template.md`'s `### 2026-08-15 - Created`), and the repo's own documents rely on it (date-only entry headings in `docs/tsk` x2 and `docs/sysrs` x1).

## Decision Drivers

- One convention per timestamp concept across all artifact types (the twelve whole-body domains; the ADR domain is excluded — deprecated, with its own frontmatter model and no `created`/`updated`).
- Accepting correct ISO 8601: the `T`-separated combined date+time form is ISO 8601's standard extended form (ADR 23a14195) and should parse wherever specmgr accepts a timestamp.
- Frontmatter is system-owned: a single machine-written canonical form removes ambiguity from the write side.
- Simplifying newest-first ordering validation (removing the mixed-granularity rule and the naive/aware hazard).
- Agent ergonomics (GitHub issue #146): a uniform, unambiguous validation contract plus actionable parse errors (field path, line, expected regex, offending text) reduces trial-and-error round-trips.

## Considered Options

1. Full date+time only everywhere, accepting both `T` and space separators; the MCP writes frontmatter in `T` form; section titles (entry-heading examples, templates, migrated documents) keep the space form for readability.
2. Full date+time only everywhere, space separator only: tighten the four lenient domains, leave `feat`/`sop` and frontmatter unchanged.
3. Loosen `feat`/`sop` (and frontmatter) to date-or-full: uniform leniency.
4. Status quo: keep the two conventions.

## Decision Outcome

Adopt **Option 1**. All six entry-heading aliases — `feat`'s `UpdateEntry`/`DecisionEntry` and `sop`/`tsk`/`dec`/`vcr`/`sysrs`'s `UpdateEntry` — and the shared frontmatter pattern (`MarkdownFrontmatter._DATE_TIME_PATTERN`) accept exactly `yyyy-MM-dd` + (`T` | space) + `HH:mm:ss` + `.` + exactly-three-digit milliseconds + (`Z` | `±HH:MM`); date-only is rejected everywhere.

The write side switches from space to `T`: `general.tools._timestamps.format_timestamp`/`now_timestamp` emit `yyyy-MM-ddTHH:mm:ss.fff` + (`Z` | `±HH:MM`), inherited by every `create_<d>`/`update`/`set_status` call site without per-site edits. `validate_newest_first`'s mixed-granularity branch is removed (plain aware `datetime.fromisoformat` comparison); `format_date` (zero callers after the tightening) is deleted; `_stringify_metadata` normalizes PyYAML-coerced `datetime` values to the `T` canonical form with milliseconds, instead of bare `str()` which drops them.

Migrations in the same change: the 8 packaged date-only entry headings become space-form midnight UTC (`yyyy-MM-dd 00:00:00.000Z`, per feat-38-39-41-43-44 D7); the 24 packaged template/example frontmatters become `T` form; the 3 `docs/` entry headings become space-form midnight UTC; the 8 tsk/dec/vcr/sysrs instruction files are rewritten to describe the full form only. Implementation and progress: `.specmgr/feat/feat-146-date-time/README.md`.

### Consequences

- **Breaking** (in-place `models/v1` evolution per the prb/feat-132 precedent — no v2 schema): existing `tsk`/`dec`/`vcr`/`sysrs` documents with date-only entry headings fail to parse until migrated; the complete repo-owned inventory is migrated within the feature (listed in the decision outcome).
- Supersedes feat-38-39-41-43-44's D4 (space-separated canonical write form), D5/ACC-005 (T rejection for frontmatter), D7/D11 (date-only migration and normalization shapes), and REQ-004/ACC-004 (the lenient entry-heading split). feat-32-sysrs' "locked lenient `## Updates` shape" note and feat-67-70-71's "deliberately supported alternate granularity" note are refined likewise — brief supersession notes are added to those feature READMEs.
- Aligns with, rather than supersedes, ADR 23a14195 ("Use ISO 8601 for all dates and times"): that ADR's standard combined form is `T`-separated; this ADR makes `T` the machine-written canonical form and accepts space as well for human-facing readability.
- Existing space-form values (frontmatter or entry headings) remain valid indefinitely; frontmatter values converge to `T` on each write. No mass-migration of existing `docs/` frontmatter is performed.
- GitHub issue #146's second claim — a bare, non-descriptive `Error executing tool create_feat` with no validation detail — was verified non-reproducible on the current server + MCP SDK 2.0.0: the alias-mismatch message carries the field path, 1-based line number, raw `@alias` regex, and the offending text, and the SDK propagates the full message (`Error executing tool <name>: <message>`); the reporter's bare error was client-side display truncation. The raw regex is intentionally retained as the machine-readable format contract for agent consumers; no prose rewording of the error is introduced by this decision.
- After the migration, `tests/regression/test_issue_67.py`'s date-only-heading exclusion becomes moot (no packaged data file keeps a date-only heading).

## Pros and Cons of the Options

### Option 1: Full date+time everywhere, T or space

**Pros:**
- One convention per timestamp concept across all artifact types; templates and instructions teach a single shape.
- Accepts correct ISO 8601 (the `T` combined form per ADR 23a14195).
- Machine-written frontmatter has an unambiguous canonical form.
- Newest-first validation simplifies to plain aware-datetime comparison.
- Fixes the #146 confusion class (cross-domain strictness divergence).

**Cons:**
- Breaking for lenient-domain documents with date-only entries — the repo-owned inventory must be migrated in the same change.
- Amends feat-38-39-41-43-44's D4/D5 (write form, T rejection) — explicit supersession must be recorded.

### Option 2: Full date+time everywhere, space only

**Pros:**
- Minimal change surface: only the four lenient domains tighten; the frontmatter regex and the write side are unchanged.

**Cons:**
- Rejects the standard ISO 8601 `T` combined form — contrary to ADR 23a14195's standard combined form and the requester's requirement.
- Keeps the D5 T-rejection and a two-form split between machine-written (space) and human ISO 8601 (`T`) values.

### Option 3: Loosen to date-or-full everywhere

**Pros:**
- Non-breaking; most permissive for hand-authored documents.

**Cons:**
- Keeps the mixed-granularity rule and the naive/aware hazard in `validate_newest_first`.
- Perpetuates the convention templates teach and agents conflate across domains — the root cause of #146.
- Same-day entries remain orderable only at day granularity, which is ambiguous.

### Option 4: Status quo

**Pros:**
- No work.

**Cons:**
- The inconsistency motivating #146 remains; new domains must pick one of two arbitrary conventions.

## More Information

- GitHub issue #146: https://github.com/dfch/biz.dfch.SpecMgr/issues/146
- Implementation plan and progress: `.specmgr/feat/feat-146-date-time/README.md`
- Superseded decisions: `.specmgr/feat/feat-38-39-41-43-44/README.md` (D4/D5/D7/D11, REQ-004/REQ-006, ACC-004/ACC-005); `.specmgr/feat/feat-32-sysrs/README.md` (locked lenient `## Updates` shape); `.specmgr/feat/feat-67-70-71/README.md` (date-only "deliberately supported" note)
- Related ADR: 23a14195-339c-48af-99d2-97c9964041ae ("Use ISO 8601 for all dates and times")
- PyYAML coercion hazard (verified empirically): unquoted timestamp values in either separator coerce to `datetime` on parse, and bare `str()` drops milliseconds — which is why the `_stringify_metadata` normalization from the decision outcome is required for unquoted values to parse.
