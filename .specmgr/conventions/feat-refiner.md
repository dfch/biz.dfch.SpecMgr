# feat-refiner: Local Repo Conventions

This file supplements `.opencode/agent/feat-refiner.md`'s own, repo-agnostic
checklist with findings specific to **this** repository's own file layout and
tooling. `feat-refiner` reads this file if it exists and applies it as an
additional checklist layer, under "Local repo conventions (if any)" in its
report. A repo without this file is refined using the agent's Generic layer
only.

## Checklist additions

- **Consistency with this repo's own conventions**: if the plan changes a
  domain's schema, does its Task List also account for the artifacts
  `AGENTS.md` says must move together (docstrings, `data/*_template.md`/
  `*_example.md`, both JSON Schema copies, `docs/api/`, `docs/GENERATED.md`,
  `docs/MCP.md`, `server.py`'s docstring, the domain's `AGENTS.md` bullet,
  `CHANGELOG.md`, `whitelist.py`)?
