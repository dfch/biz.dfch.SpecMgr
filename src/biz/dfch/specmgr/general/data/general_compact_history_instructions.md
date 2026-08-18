You are compacting the "Recent Updates" section of a `.specmgr` feature
folder's `README.md`, identified by feature id:
$feature_id

Rotation cutoff hint: $cutoff_hint

Follow this sequence exactly. This document type has no dedicated specmgr
MCP tool of its own -- use your own file read/edit/write tools directly on
`.specmgr/feat/$feature_id/README.md` and its optional sibling
`history.md`, per ADR e369ee2e-3353-4f92-991c-6367d76d832e.

Make a todo list and use the `question` tool whenever this prompt tells
you to -- do not guess when something is ambiguous.

## 1. Read the current state first
Read `.specmgr/feat/$feature_id/README.md` in full. If a sibling
`.specmgr/feat/$feature_id/history.md` already exists, read it too. Never
assume prior state -- these files may have been hand-edited since you last
saw them.

## 2. Locate the "Recent Updates" section
Find the `### Recent Updates` heading under `## Progress`. It holds a
sequence of dated `#### YYYY-MM-DD` sub-sections, newest first, each
listing `Completed:`/`Next:`/`Notes:`-style bullet items. If it already
starts with a pointer line such as "See `history.md` for updates before
YYYY-MM-DD.", treat everything after that line as the currently-visible
entries; the pointer line itself is not an entry.

## 3. Determine the rotation cutoff
"Rotation cutoff hint" above is one of:
- A concrete rule, e.g. "keep the last 3 dated entries", "keep only
  entries from the last 30 days", "keep only entries from
  2026-08-18 onward".
- Missing or the literal placeholder text `(not given)`.
If the hint is missing, or does not resolve to one unambiguous cutoff
date/entry, use the `question` tool to ask the user explicitly which
rotation rule to apply -- offer at least: "keep the last N dated entries"
(ask for N), "keep entries from the last N days" (ask for N), and "keep
entries from a specific date onward" (ask for the date) as selectable
options. Do not proceed to step 4 until the cutoff is unambiguous.

## 4. Move older entries into history.md
For every `#### YYYY-MM-DD` sub-section older than the cutoff:
- Copy it verbatim (heading and all its content, byte-for-byte) into
  `history.md`, preserving relative order (oldest-to-newest or
  newest-to-first, matching whatever order `history.md` already uses if
  it exists; otherwise keep the same newest-first order as `README.md`).
- If `history.md` does not exist yet, create it with a top-level
  `# History: {feature title}` heading (reuse the exact title from
  `README.md`'s own `# Feature: ...` H1) before the moved entries.
- Remove that sub-section entirely from `README.md`'s `### Recent
  Updates`.
Never rewrite, summarize, or reorder the content of a moved entry -- an
exact, verbatim move only.

## 5. Leave a pointer in README.md
After removing the older entries, ensure `### Recent Updates` starts with
exactly one pointer line, replacing any previous one:
`See \`history.md\` for updates before YYYY-MM-DD.`
where `YYYY-MM-DD` is the date of the oldest entry you kept (i.e. the
cutoff boundary), followed by the remaining, newer `#### YYYY-MM-DD`
sub-sections unchanged.

## 6. Bump the frontmatter `updated` field
Update `README.md`'s YAML frontmatter `updated` field to today's date
(`YYYY-MM-DD`). Do not touch any other frontmatter field, and do not touch
any other section of `README.md` (Plan, Requirements, Task List, Decisions
Made, etc.) -- this is a scoped edit to `### Recent Updates` plus
frontmatter `updated` only.

## 7. Verify before reporting back
Before telling the user you are done:
- Confirm every entry you moved appears exactly once in `history.md` and
  nowhere in `README.md` (a text search for a distinctive fragment of each
  moved entry is sufficient).
- Confirm `README.md`'s `### Recent Updates` section still parses as valid
  markdown (pointer line, then only `#### YYYY-MM-DD` sub-sections you
  decided to keep).
Report back: how many entries were moved, the cutoff date used, and
`README.md`'s new line count vs. its line count before this edit.
