# `biz.dfch.specmgr.models.md._ordering`

Shared, private newest-first ordering validation helper for `models.md` domain body models.

Mirrors `feat.models.v1.body.Updates._validate_newest_first`/
`DecisionsMade._validate_newest_first` (the untouched precedent this
package deliberately does not refactor -- see
`.specmgr/feat/feat-38-39-41-43-44/README.md` Design Notes for Phase 2),
factored out here so the newer `sop.Updates`/`dec.Updates`/`vcr.Updates`/
`tsk.RecentUpdates` containers share one implementation instead of four
near-identical copies of the same `model_validator`.

## Functions

### `validate_newest_first(timestamps: 'list[str]', label: 'str') -> 'None'`

Assert that `timestamps` are ordered newest-first (non-increasing).

Each consecutive pair is compared with `datetime.fromisoformat` (aware
comparison; `Z` is supported by `fromisoformat` on Python 3.11+, this
package's floor). Mixed-granularity rule: when either side of a pair is
a date-only value (`yyyy-MM-dd`, no time component), the comparison
happens at day granularity (`.date()`) instead of full `datetime`
precision -- a date-only entry and a same-day date+time entry are
therefore treated as equal, not ordered against each other by the time
component neither, or only one, of them carries. Equal values (same
day, or identical timestamps) are always allowed (`>=`, not `>`),
matching the FEAT precedent's own non-strict "newest-first" semantics.

Args:
    timestamps: The entries' own timestamp strings, in document order
        (index 0 is the first/topmost entry).
    label: The calling container's own name (e.g. `"Updates"`,
        `"RecentUpdates"`), used only to prefix the assertion message.

Raises:
    AssertionError: some earlier (lower-index) entry's timestamp is
        older than a later (higher-index) entry's timestamp -- i.e. the
        entries are not newest-first.

