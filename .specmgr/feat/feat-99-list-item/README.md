---
classification: null
created: '2026-09-04 23:25:55.412+02:00'
id: feat-99-list-item
status: planning
type: feat
updated: '2026-09-04 23:42:11.858+02:00'
version: 1.0.0
---

# Feature: Soft-Wrapped List Items Break create_feat/validate_feat (and Likely Other models/md Domains)

## Plan

### Overview

Soft-wrapped (lazy-continuation) list/checklist item text -- a bullet whose text continues onto an indented second physical line -- currently breaks the shared models/md parser used by create_feat/validate_feat and, likely, every other whole-body domain built on the same parser (req, uc, tsk, qa, prb, gol, rsk, dec, sop, vcr, sysrs). The failure surfaces to MCP callers only as an opaque "Error executing tool `<name>`" with no field path, line reference, or cause/fix hint, defeating the actionable-error contract feat-27-validation established. This feature investigates the scope of the problem across models/md consumers and closes the gap: either by teaching the parser to join soft-wrapped list item lines per standard CommonMark lazy-continuation semantics, or by explicitly rejecting them with an actionable error, plus stopping generic MCP tool error handling from swallowing the underlying exception message.

### Requirements

- REQ-001: Confirm the scope of the parser-level vs. feat-specific bug across all twelve models/md whole-body domains.
- REQ-002: The parser either supports CommonMark lazy-continuation list items (joining wrapped lines) or rejects them with an actionable error (field path, line reference, cause/fix hint).
- REQ-003: MCP tool error handling stops swallowing the underlying exception message for create_/validate_/update tools, surfacing the actionable detail to the client.
- REQ-004: The `get_<d>_template`/`get_<d>_example` outputs and AGENTS.md document the resulting behavior/constraint.

### Acceptance Criteria

- [x] ACC-001: A written summary confirms whether the bug is shared-parser-level (affecting all twelve whole-body domains) or feat-specific, based on reproduction against at least one other domain (e.g. req or tsk).
- [ ] ACC-002: A document with a soft-wrapped list item either parses/validates successfully with the wrapped text correctly joined, or fails with an AssertionError/ValidationError carrying a field path, a 1-based line reference, and a cause/fix hint -- never an opaque unhandled exception.
- [x] ACC-003: An MCP tool call that fails validation (e.g. create_feat) surfaces the underlying exception message to the client, not just "Error executing tool `<name>`".
- [ ] ACC-004: AGENTS.md and the affected `get_<d>_template`/`get_<d>_example` outputs reflect the resulting behavior/constraint on soft-wrapped list items.

### Scope

#### Included

- Reproducing and diagnosing the soft-wrap failure in the shared models/md list-item parsing path.
- Deciding and implementing either lazy-continuation joining or an explicit actionable rejection for soft-wrapped list items.
- Auditing (not necessarily deeply fixing) whether the same failure mode reproduces in at least one other models/md domain besides feat.
- Fixing the MCP error-handling layer so raised AssertionError/ValidationError messages reach the client instead of being replaced by a generic "Error executing tool `<name>`" message.
- Updating AGENTS.md and template/example resource content to document the resulting behavior.

#### Explicitly Out Of Scope

- A full rewrite of the models/md parser architecture.
- Fixing every other unrelated opaque-MCP-error case not tied to list-item parsing.
- Adding brand-new CommonMark features beyond lazy-continuation list items (e.g. nested sub-lists, loose vs. tight list semantics).
- Retroactively reformatting existing on-disk documents that happen to contain soft-wrapped list items.

### Dependencies

#### Depends On

- feat-27-validation and feat-67-70-71's actionable-error conventions (field path, line reference, cause/fix hint), which this feature must remain consistent with.

### Design Notes

The parser is line-oriented so it can compute 1-based line references for actionable error messages. Joining soft-wrapped list-item lines (standard CommonMark lazy continuation) may complicate that line-tracking, since a single logical item would then span multiple physical lines. This tension must be resolved during Phase 1/2, whichever direction (join vs. reject) is chosen.

Diagnosis (2026-09-04) narrowed this further: the failure is not tied to a domain-specific regex like `REQ-NNN:` alone. `tsk`'s plain `TaskItem` checklist (reused as-is by `feat`'s own Task List phases) also breaks on a soft-wrapped item, failing the bare `- [ ]`/`- [x]` checkbox-marker check itself -- so the bug sits in the shared `models/md` list-item extent/extraction logic before any domain-specific pattern is even applied. By contrast, a free-form bullet list with no computed/regex-checked field (e.g. `req`'s `## Tags`) tolerates the exact same wrap without error. So the bug is scoped to `MarkdownListItem` subclasses that impose a structural marker/pattern check on their own text (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`, and likely any other domain's equivalent), not to free-form lists.

### Task List

#### Phase 1: Diagnosis

- [x] Task 1.1: Reproduce the failure with a minimal feat document containing one soft-wrapped list item.
- [x] Task 1.2: Bisect to confirm the failure is specifically the list-item lazy-continuation join, not something else.
- [x] Task 1.3: Check whether the same construct reproduces against one other models/md domain (e.g. req or tsk) to confirm shared-vs-local scope.

#### Phase 2: Fix

- [ ] Task 2.1: Implement either lazy-continuation line-joining for list items in models/md, or an explicit actionable AssertionError/ValidationError (field path, line reference, cause/fix hint) when a soft-wrapped item is encountered.
- [ ] Task 2.2: Stop the MCP tool error wrapper from swallowing the underlying exception message.

#### Phase 3: Documentation and Verification

- [ ] Task 3.1: Update AGENTS.md and the affected `get_<d>_template`/`get_<d>_example` resource content.
- [ ] Task 3.2: Add/extend tests covering soft-wrapped list items across the parser and at least one MCP tool.
- [ ] Task 3.3: Run the full test suite and lint/vulture checks.

## Progress

### Current Status

**As of 2026-09-04**: Phase 1 diagnosis is complete. Reproduced against a minimal `feat` document (`### Requirements` REQ-NNN bullet) and independently against `tsk`'s shared `TaskItem` checklist, confirming this is a shared `models/md` parser-level bug, not `feat`-specific -- it affects any structural, marker/pattern-checked list item (`TaskItem`, `RequirementItem`, `AcceptanceCriterionItem`), while free-form bullet lists (e.g. `req`'s `## Tags`) are unaffected. Separately, an unrelated but closely-related parser fragility was also hit while drafting this very document: a bare `<word>`-shaped token (e.g. `<name>`, `<d>`) in prose is valid CommonMark inline raw HTML and is rejected -- this is expected CommonMark behavior, not a bug, but it shares the same "easy to trigger by accident, painful to diagnose" profile as the soft-wrap issue. Good news: as of today, both failure modes now produce **actionable** errors (field path + line reference, plus an explicit fix hint for the raw-HTML case) through both the disk-free `validate` tool and the real `create_feat` write path -- the opaque `"Error executing tool <name>"` failure mode described in the original issue no longer reproduces on this server, satisfying ACC-003 already. A live audit of this repository's own 40 `.specmgr/feat/*/README.md` documents via `list_feat` found 34 currently fail to parse: 16 are the soft-wrapped `REQ-NNN`/`ACC-NNN`/task-item bullets this feature targets, 3 are the bare-HTML-tag case (`</content>`, `<d>`, `<name>`), 2 are an adjacent timestamp-granularity mismatch in `### Updates`/`### Decisions Made` heading entries, and the remaining 13 are pre-existing, unrelated issues (invalid frontmatter timestamp formats, invalid `status` enum values, structural drift) explicitly out of this feature's scope. Remaining work is Phase 2 (confirm the fix is durable/source-verified, not just an artifact of this particular server instance, and decide join-vs-reject for the wrap itself) and Phase 3 documentation.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-04 21:40:47.000Z - Phase 1 diagnosis complete; error-swallowing already appears fixed

Reproduced the soft-wrap failure against a minimal `feat` document (`REQ-NNN` bullet) and confirmed it is a shared `models/md` parser-level issue, not `feat`-specific, by also reproducing it against `tsk`'s `TaskItem` checklist (fails the bare checkbox-marker check itself, before any domain-specific regex is applied); a free-form bullet list with no structural field check (`req`'s `## Tags`) tolerated the same wrap without error. Separately reproduced the unrelated bare-`<word>`-as-raw-HTML case (`<name>`, `<d>`) that was also hit opaquely while first drafting this document. Both failure modes now surface fully actionable errors (field path, line reference, and -- for the raw-HTML case -- an explicit fix hint) through the `validate` tool and through `create_feat` itself; the opaque `"Error executing tool <name>"` message described in issue #99 no longer reproduces on the current server. A live audit of this repository's own 40 feature documents found 34 currently fail to parse, 16 of them via exactly this soft-wrap pattern and 3 via the bare-HTML-tag pattern, with the remaining 15 being unrelated pre-existing issues.

#### 2026-09-04 21:22:24.000Z - Created

Feature drafted from GitHub issue #99, which reported that soft-wrapped (lazy-continuation) list items break create_feat/validate_feat with an opaque, unhelpful error.

### Related PRs / Commits

- [Issue #99](https://github.com/dfch/biz.dfch.SpecMgr/issues/99): tracking issue for this feature.
