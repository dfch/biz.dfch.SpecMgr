# feat-reviewer: Local Repo Conventions

This file supplements `.opencode/agent/feat-reviewer.md`'s own, repo-agnostic
checklist with findings specific to **this** repository's own file layout and
tooling. `feat-reviewer` reads this file if it exists and applies it as an
additional checklist layer, under "Local repo conventions (if any)" in its
report. A repo without this file is reviewed using the agent's Generic and
Feature-plan layers only.

## Diff resolution

- This repo's Conventional Commits scope commit subjects by domain (e.g.
  `feat(prb): ...`), not by feature id -- most implementation commits never
  mention the `feat-NNN-slug` id or issue number at all. Don't try to find
  "the feature's commits" by grepping subjects for either.

## Checklist additions

- **Parser correctness and edge cases**: read every new/changed regex,
  `field_validator`, or parser against `models/md`'s own conventions --
  soft-wrap/lazy-continuation handling, `re.DOTALL` usage, whitespace
  assumptions (`MarkdownParagraph`/`MarkdownListItem`/`MarkdownSection`
  `.text` preserves embedded line breaks verbatim; `mdformat` never
  reflows). Concurrency, off-by-one, greedy-regex ambiguity, and
  dead/unused capture groups are the most common defect classes found
  here historically.
- **Test fixture reach**: beyond the generic Testability item above --
  do old fixtures across the whole test suite (not just the domain's own
  `tests/<domain>/`) still need updating, e.g. shared fixtures in
  `tests/general/tools/`?
- **Artifact consistency**: this codebase requires several artifacts to
  move together whenever a domain's body schema changes -- the model
  itself, its docstrings, `<domain>/data/*_template.md` and
  `*_example.md`, both JSON Schema copies (`docs/*_schema.json` and the
  packaged `src/.../data/*_schema.json`), `docs/api/`,
  `docs/GENERATED.md`, `docs/MCP.md`, `server.py`'s module docstring, the
  domain's `AGENTS.md` bullet, `CHANGELOG.md`, and `whitelist.py` (for any
  new vulture-invisible validator/method). Flag anything that moved
  without its counterparts, or wording that drifted out of sync.
- **Dead-code and vulture-visibility**: unused capture groups, unreachable
  branches, unused imports/symbols `vulture` would catch (see
  `whitelist.py` for known accepted false positives) -- file these under
  **Improvements**, or **Errors** if one indicates a real bug (e.g. a
  silently-unused computed result).
