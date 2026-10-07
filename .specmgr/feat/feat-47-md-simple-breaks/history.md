# History: Preserve `---` Thematic Breaks in `mdformat` via `mdformat-simple-breaks`

#### 2026-09-02 00:00:00.000Z - Plan refined ahead of implementation

Resolved three open items surfaced during pre-implementation review: (1) the CHANGELOG entry (Task 1.6) uses `### Fixed`, matching Keep a Changelog's standard category for a bug fix and this repo's own existing section headers; (2) the regression test (ACC-003/Task 1.4) extends the existing `tests/models/md/test__markdown.py` rather than adding a new file, since that file already targets this exact module; (3) PyPI reachability and `mdformat-simple-breaks` package metadata (exactly two releases, `0.0.1`/`0.1.0`; `requires_dist: mdformat~=1.0.0`) were verified directly from the implementation environment -- see Design Notes for the latent `mdformat` 2.x compatibility caveat this uncovered. No requirements/scope changes; implementation still not started.


#### 2026-09-02 00:00:00.000Z - Created

Feature folder created to track fixing GitHub issue #47 (`specmgr mdformat` converts `---` to a 70-underscore thematic break) via the `mdformat-simple-breaks` plugin, pinned to an exact version.
