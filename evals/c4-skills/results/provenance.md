# Provenance and license verification (Task 100.190)

Verified on **2026-11-01** (all SHAs re-verified against the GitHub API at
check time; the `LICENSE` files were fetched at exactly the pinned commits).
Every source below is confirmed **MIT**, so none of them moves to "ideas
only" (the plan's rule for an unconfirmed license). The specmgr repository
is AGPL-3.0-or-later; MIT text adapted into a skill keeps its MIT notice
next to the skill (REQ-010), and this table is the committed provenance
record required by the plan.

| Source | Commit (checked) | License file | License type | Check date |
|---|---|---|---|---|
| `jrjsmrtn/c4-skills` | `e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b` (commit date 2026-09-30; HEAD of `main` at check time) | `LICENSE` (repository root) | MIT — "Copyright (c) 2026 Georges Martin" | 2026-11-01 |
| `passionsplay/structurizr-skill` | `5e45154e1c266e0517d456855b415ba770412f16` (commit date 2026-10-27; HEAD of `main` at check time) | `LICENSE` (repository root) | MIT — "Copyright (c) 2026 Benjamin Turner" | 2026-11-01 |
| `structurizr/structurizr.github.io` | `530a96451b93f8fb96337b58aaaa1ec8c0ad4589` (commit date 2026-10-25; HEAD of `main` at check time) | `LICENSE` (repository root) | MIT (SPDX `MIT` per the GitHub API; the boilerplate copyright line reads "Copyright (c) 2022 just-the-docs", the Jekyll theme the documentation site is built on) | 2026-11-01 |

Notes:

- The upstream skills are fetched at run time from the pinned commit of
  `jrjsmrtn/c4-skills` (never vendored, never patched); its four skill
  folders (`c4-deployment`, `c4-model`, `c4-review`, `structurizr-dsl`) are
  single `SKILL.md` files each, verified against the pinned commit's tree.
- The `structurizr/structurizr.github.io` documentation is the intended
  adaptation source for `structurizr-dsl-authoring` (Phase 120); its
  per-page content sits under the repository's single MIT license.
- Sources deliberately kept "ideas only" (no license in the repository,
  per the plan): `allensanborn/skills`, `bitsmuggler/c4-skill`,
  `fedemagnani/structurizr-dsl`. Concepts from them may inform wording,
  but no text is copied.
