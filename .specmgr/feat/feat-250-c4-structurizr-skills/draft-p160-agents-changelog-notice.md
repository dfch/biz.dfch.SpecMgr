# Draft: Phase 160 repo-docs target text (Task 160.130)

DRAFT — pre-drafted 2026-11-20 AGAINST THE POST-MERGE BASE (`d0fd1434`) for
the Phase 160 session. The three sections below are the exact insertion /
edit texts for `AGENTS.md`, `CHANGELOG.md` and the root `NOTICE`. Each
section states its anchor (the current text it goes next to, verified at
draft time) and the text to insert. The Phase 160 session applies these
AFTER Task 160.100's cumulative data lands (the CHANGELOG bullet and the
AGENTS bullet both cite the final results state), then regenerates
`specmgr docs` if the applied text touches anything docstring-derived
(it does not — all three are hand-written files), and re-runs the bundle
drift check (it does not — none of the three is a bundled `.opencode/`
file).

Base state at draft time:

- `AGENTS.md` — the Status section's per-domain bullets end with the
  `set/` bullet (top-level) and its `general/` sub-bullet, whose last line
  is "`heading_table` loader over `general/data/headings/<language>.json`."
  followed by a blank line and the `**Models location**:` paragraph. No
  mention of the five C4 skills or of `evals/` exists anywhere in the file.
- `CHANGELOG.md` — `[Unreleased]` has `### Added` (three bullets: the
  feat-167 `refine_feat` prompt, the feat-173 `set` domain, the feat-263
  `implement_feat`/`review_feat` prompts — newest at the bottom), then
  `### Changed` / `### Removed` / `### Fixed`.
- `NOTICE` — project header, then one `---`-separated section per
  third-party dependency (pydantic, python-dotenv, markdown-it-py,
  python-frontmatter, mdformat, mdformat-simple-breaks, typer, rich,
  mcp/mcp-types), each carrying copyright / `License: MIT` / URL / the full
  license text. No adapted-text section exists yet.

## 1. `AGENTS.md` — new top-level bullet (the skill surface + the `evals/` directory)

**Anchor:** insert as a new top-level bullet of the Status section,
immediately after the `general/` sub-bullet's last line
("`heading_table` loader over `general/data/headings/<language>.json`.")
and its blank line, i.e. directly before the `**Models location**:`
paragraph. (Considered and rejected: a bullet inside the `general/`
sub-bullet — these are not a domain package and do not belong to
`general/`'s description; the "Still genuinely missing / not yet done"
section — not applicable, this feature ships its surface, it leaves none
of the listed gaps open and adds no new one.)

**Text:**

```markdown
- **C4/Structurizr OpenCode skills + top-level `evals/`** (feat-250-c4-structurizr-skills, GitHub issue #250) — five cross-cutting OpenCode skills under `.opencode/skill/` (not a domain package, no MCP tools, no prompts — pure markdown host surfaces, carried by the harness bundle): `c4-modeling` (the C4 levels, what counts as a container and what does not, external-system modeling, naming/label rules, the common mistakes), `structurizr-dsl-authoring` (DSL syntax, structure and the known gotchas), `structurizr-validate-loop` (the mandatory loop: parse → validate → inspect, a DSL result never returned unless it was validated to `OK` — parsed-only is not a pass, DEC 7a626b12-b189-4561-a51d-ffb2e9e193b4 applied — and every `inspect` finding triaged fix / expected-under-the-MCP-limits / reported), `c4-view-design` (which views to create, the about-20-element-per-view bound, explicit view keys, the C4-PlantUML export gotchas) and `c4-model-review` (a READ-ONLY quality checklist — it reports findings and never edits the model; the read-only behavior is also gate-enforced by the harness). Each `SKILL.md` is thin: `name` equal to its folder, a single-task trigger `description` that must not load on another skill's task (measured by the harness's `no-trigger` case), markdown reference files next to it, the Structurizr-MCP limits the skill depends on stated in full where it depends on them (DSL text only, single file; `!include`/`!docs`/`!adrs` refused; no image rendering — REQ-006) and the no-MCP behavior (validation is not possible, never described as validated — REQ-011). Adapted MIT text carries a per-skill `NOTICE.md` + `source-map.md` (sources: `jrjsmrtn/c4-skills`, `passionsplay/structurizr-skill`, the Structurizr docs — the root `NOTICE` and `evals/c4-skills/results/provenance.md` are the committed provenance record); `c4model.com` is concepts-only (CC BY 4.0, attributed where wording is reused). The skills' effectiveness is measured by the reproducible, development-only container harness in the top-level `evals/` directory (never in the wheel, never in the harness bundle): `evals/c4-skills/` (Python, standard library only; one isolated OpenCode container per trial against the pinned local model, conditions `none` / `upstream` (the unmodified `jrjsmrtn/c4-skills` at the pinned SHA — deliberately unpatched, its Docker-CLI validation advice cannot work in the container, a harsh baseline) / `skill`, gates computed from the real Structurizr CLI `export -format json` output, the recorded version tuple, per-case result caching, the shared-vLLM busy-window refusal, committed results under `evals/c4-skills/results/`); its unit tests live under `tests/evals/` (the graders' known-good/known-bad split over pre-exported JSON fixtures, no model call; the live-CLI tests skip when Docker is missing) and each skill has a pinning test `tests/opencode/test_skill_<name>.py` (name, description keywords, the MCP-limit wording, the read-only wording, the notice/source-map pairing). Each skill was built in its own phase under a fixed stop rule (not worse than `none`, not worse than the comparison condition within the locked margin, ≤3 iterations, one held-out case run once at the end) — the per-phase record is `.specmgr/feat/feat-250-c4-structurizr-skills/README.md`.
```

## 2. `CHANGELOG.md` — one new bullet in `[Unreleased]` → `### Added`

**Anchor:** append as the LAST bullet of `### Added` under `## [Unreleased]`
(after the `implement_feat`/`review_feat` (feat-263) bullet, before
`### Changed`) — the file's convention is newest at the bottom, and
feat-250 lands after the feat-263 merge.

**Text:**

```markdown
- The five C4/Structurizr OpenCode skills under `.opencode/skill/`
  (`c4-modeling`, `structurizr-dsl-authoring`, `structurizr-validate-loop`,
  `c4-view-design`, `c4-model-review` — feat-250-c4-structurizr-skills,
  GitHub issue #250): thin `SKILL.md` files (one single-task trigger
  description each, the Structurizr-MCP limits stated per-skill, the
  no-MCP behavior) with markdown reference files, a per-skill
  `NOTICE.md` + `source-map.md` for the adapted MIT text
  (`jrjsmrtn/c4-skills` @ `e86d8a91…`, `passionsplay/structurizr-skill` @
  `5e45154e…`, the Structurizr docs @ `530a9645…` — the root `NOTICE`
  gains the adapted-text sections, `evals/c4-skills/results/
  provenance.md` the commit/license/check-date record), and a pinning
  test each (`tests/opencode/test_skill_<name>.py`, 24/27/27/26/30
  tests). `structurizr-validate-loop` mandates parse → validate →
  inspect with a never-return-unvalidated-to-`OK` rule and fix/
  expected/reported triage of every `inspect` finding;
  `c4-model-review` is read-only (it reports findings and never edits
  the model). The reproducible measurement harness under the new
  top-level, development-only `evals/` directory (`evals/c4-skills/`,
  Python standard library only — never in the wheel, never in the
  harness bundle): one isolated OpenCode container per trial against
  the pinned local model (`qwen3.8-27b-bf16-896k`, the recorded version
  tuple), the `none`/`upstream`/`skill` conditions (the upstream
  `jrjsmrtn/c4-skills` fetched at the pinned SHA, deliberately
  unpatched), gates from the real Structurizr CLI export JSON,
  per-case result caching, the shared-vLLM busy-window refusal, and
  the committed results under `evals/c4-skills/results/` (per-phase
  prove/iteration/held-out runs with seeds, variant hashes and
  margins). Its unit tests under `tests/evals/` (the graders'
  known-good/known-bad split over pre-exported JSON fixtures, no model
  call; the live-CLI tests skip when Docker is missing) and the
  repository housekeeping (`.gitignore` for the trial work dirs and
  cache, ruff/pylint/pytest treatment of `evals/` and `tests/evals/`)
  round it out. Each skill phase passed its fixed stop rule (not
  worse than `none`, within the locked margin of the comparison
  condition, ≤3 iterations, one held-out case at the end); the
  harness bundle grows to 55 entries (the 28 skill markdown files)
  with the count pin in `tests/commands/test_harness_bundle.py`
  updated accordingly.
```

## 3. Root `NOTICE` — new adapted-text section (appended at the end)

**Anchor:** append at the very end of the file, after the `mcp / mcp-types
(optional "mcp" extra)` section's final line
("…OR OTHER DEALINGS IN THE SOFTWARE."). Follows the file's own format:
`---`-separated sections, copyright / license / URL / full license text per
source.

**Text:**

````markdown

-------------------------------------------------------------------------------
C4/Structurizr OpenCode skills — adapted text
-------------------------------------------------------------------------------

The five C4/Structurizr OpenCode skills under `.opencode/skill/`
(feat-250-c4-structurizr-skills) adapt text from the three MIT-licensed
sources below. The per-skill `NOTICE.md` + `source-map.md` files next to
each `SKILL.md` carry the passage-level attribution (which local file
adapts which source file, and what was dropped or rewritten); the
committed provenance record (commit, license file, license type, check
date) is `evals/c4-skills/results/provenance.md`. The skills' `SKILL.md`
files adapt no text (ideas only) and carry no attribution line.
`c4model.com` (CC BY 4.0) contributed concepts only — no verbatim text is
adapted; where its wording is reused it is attributed in the skill's
source map. The repositories `allensanborn/skills`,
`bitsmuggler/c4-skill` and `fedemagnani/structurizr-dsl` carry no license
and contributed ideas only, never copied text; they are not listed here.

-------------------------------------------------------------------------------
jrjsmrtn/c4-skills
Copyright (c) 2026 Georges Martin
License: MIT
https://github.com/jrjsmrtn/c4-skills (adapted at commit
e86d8a91d3ed793cdf6c035f01d19f1b18cc8b6b)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Adapted in: `c4-modeling` (from the `c4-model` skill), `c4-view-design`
(from the `c4-model` skill's Diagram Types tables and Diagram Selection
Guide), `c4-model-review` (from the `c4-review` skill, made read-only) and
`structurizr-dsl-authoring` (from the `structurizr-dsl` skill).

-------------------------------------------------------------------------------
passionsplay/structurizr-skill
Copyright (c) 2026 Benjamin Turner
License: MIT
https://github.com/passionsplay/structurizr-skill (adapted at commit
5e45154e1c266e0517d456855b415ba770412f16)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Adapted in: `structurizr-validate-loop` (the validate-versus-inspect table
and the DSL gotchas).

-------------------------------------------------------------------------------
structurizr/structurizr.github.io
Copyright (c) 2022 just-the-docs (the Jekyll theme the documentation site
is built on)
License: MIT
https://github.com/structurizr/structurizr.github.io (adapted at commit
530a96451b93f8fb96337b58aaaa1ec8c0ad4589)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Adapted in: `structurizr-dsl-authoring` (the DSL documentation content) and
`c4-view-design` (the view-kind documentation content).
````

## Notes for the applying session

- None of the three files is a bundled `.opencode/` markdown file, so the
  harness bundle and `tests/commands/test_harness_bundle.py` are untouched
  by Task 160.130.
- `AGENTS.md`'s own standing rule — "update it whenever you add/remove/
  rename a resource, tool, or prompt" — is not triggered (no MCP
  surface); the new bullet is the host-surface + `evals/` description.
- Apply after Task 160.100's data lands so the CHANGELOG bullet's results
  statement (and the AGENTS bullet's per-phase record pointer) are final;
  if 160.100 changes any caveat/floor restatement, adjust the two bullets'
  wording accordingly — the NOTICE section is data-independent and can be
  applied as drafted.
