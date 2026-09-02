---
created: '2026-09-02T15:24:37.128173'
id: feat-51-mcp-cwd
status: planning
type: feat
updated: '2026-09-02T15:24:37.128173'
version: 1.0.0
---

# Feature: Expose Resolved Base Directories via specmgr://config

## Plan

### Overview

The MCP server silently resolves every per-domain base directory (e.g. `SPECMGR_ADR_DIR`, `SPECMGR_FEAT_DIR`, and the shared `SPECMGR_DOCS_DIR`-rooted default) relative to its own process's current working directory. When the server is launched via a bare `uvx --from ...` invocation with no `--directory` and no `SPECMGR_*_DIR` env vars set (as in the README's own "Add to OpenCode" example), that CWD is not under the caller's control and may not match the project the caller is actually working in. Today there is no error, no warning, and no way for a client to detect this mismatch before acting on data scoped to the wrong directory tree.

This feature adds a `specmgr://config` resource that reports, for every domain, the resolved base directory and whether its corresponding environment variable is explicitly set, so a client can self-diagnose "am I pointed where I think I am?" without shell access to the server's host. It also closes two related documentation gaps called out in GitHub issue #51: the README's "Add to OpenCode" example defaulting to an unsafe configuration, and `SPECMGR_FEAT_DIR` being entirely absent from the README's "Environment Variables" section.

### Requirements

- REQ-001: The server must expose a new `specmgr://config` resource reporting, for all twelve domains (adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr), the resolved absolute base directory and whether its `SPECMGR_*_DIR` environment variable is explicitly set.
- REQ-002: `specmgr://config` must never disclose the value of any environment variable other than the directory-path env vars it reports on -- it must not echo back PATs, tokens, or any other secret that may be present in the process environment.
- REQ-003: The README's "Add to OpenCode" example must be updated so it no longer silently defaults to an unrelated CWD, either by recommending `uv run --frozen --directory <path-to-your-project> specmgr mcp` or by explicitly documenting that `SPECMGR_DOCS_DIR`/`SPECMGR_ADR_DIR`/`SPECMGR_FEAT_DIR` must be set for reliable use outside of "CWD happens to already be the project root".
- REQ-004: The README's "Environment Variables" section must document `SPECMGR_FEAT_DIR`, which is currently missing entirely.
- REQ-005: `docs/MCP.md` must be regenerated (via `specmgr mcp-docs`) so it reflects the new `specmgr://config` resource, consistent with the project's existing doc-generation workflow.

### Acceptance Criteria

- [x] ACC-001: Fetching `specmgr://config` returns a structured payload listing all twelve domains, each with its resolved absolute base directory path and a flag indicating whether its `SPECMGR_*_DIR` env var was explicitly set.
- [x] ACC-002: An automated test sets an unrelated environment variable (e.g. a fake PAT) and asserts it never appears anywhere in `specmgr://config`'s output.
- [ ] ACC-003: `README.md`'s "Add to OpenCode" example and "Environment Variables" section reflect the updated guidance, including `SPECMGR_FEAT_DIR`.
- [x] ACC-004: `docs/MCP.md` lists `specmgr://config` after running `specmgr mcp-docs`, with no manual edits required.
- [ ] ACC-005: `uv run --frozen ruff format --check`, `ruff check`, `vulture`, and the full unittest suite all pass with the new resource in place. (Phase 1's own slice passed; ACC-005 stays open pending Phase 2/3.)

### Scope

#### Included

- A new `specmgr://config` resource in `general/resources/` reporting the resolved base directory and env-var-set flag for all twelve domains.
- Unit tests for the new resource, including a test that unrelated environment variables are never disclosed.
- README updates: the "Add to OpenCode" example and the "Environment Variables" section (including `SPECMGR_FEAT_DIR`).
- Regenerating `docs/MCP.md` (and `docs/GENERATED.md` if affected) via the project's existing doc-generation commands.

#### Explicitly Out Of Scope

- Changing the actual default base-directory resolution behavior -- the server will still default to CWD-relative paths when no env var/`--directory` is given; this feature only makes that resolution observable, not different.
- Improving runtime error messages for downstream tool failures caused by misconfiguration (e.g. `set_status` failing on an unknown id).
- Any new CLI flag or startup-time validation/warning -- the resource is the sole diagnostic mechanism introduced by this feature.

### Design Notes

`specmgr://config` returns a payload shaped as `domain -> {base_dir: str, env_var: str, env_var_set: bool}` for each of the twelve domains, modeled after the existing `specmgr://version` resource in `general/resources/`. To satisfy REQ-002/ACC-002, the implementation must explicitly enumerate the known `SPECMGR_*_DIR` keys and read only those from the environment, rather than iterating over or dumping `os.environ` wholesale -- this avoids any risk of leaking unrelated secrets (e.g. PATs used by other integrations) that happen to be present in the same process environment.

### Task List

#### Phase 1: Diagnostic Resource

- [x] Task 1.1: Finalize the `specmgr://config` payload schema (domain -> base_dir, env_var name, env_var_set flag) for all twelve domains.
- [x] Task 1.2: Implement the resource in `general/resources/` and register it in `server.py`.
- [x] Task 1.3: Add unit tests, including the non-disclosure test required by ACC-002.
- [x] Task 1.4: Update `server.py`'s module docstring and regenerate `docs/MCP.md` via `specmgr mcp-docs`.

#### Phase 2: Documentation Updates

- [ ] Task 2.1: Update README's "Add to OpenCode" example per the chosen guidance (REQ-003).
- [ ] Task 2.2: Add `SPECMGR_FEAT_DIR` to README's "Environment Variables" section (REQ-004).

#### Phase 3: Verification

- [ ] Task 3.1: Run the full lint (`ruff format --check`, `ruff check`), `vulture`, and unittest suite.
- [ ] Task 3.2: Manually verify `specmgr://config` output against a real worktree to confirm the reported paths match reality.

## Progress

### Current Status

**As of 2026-09-02**: Phase 1 (Diagnostic Resource) complete -- the `specmgr://config` resource is implemented, tested, and documented. Phase 2 (README documentation updates) and Phase 3 (verification) remain.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 — Phase 1 complete: specmgr://config resource implemented

Added the `specmgr://config` resource reporting, for all twelve document domains (adr, req, uc, tsk, qa, prb, gol, rsk, dec, sop, feat, vcr), the resolved absolute base directory and whether the domain's `SPECMGR_*_DIR` env var is explicitly set. New files: `src/biz/dfch/specmgr/models/config_info.py` (`DomainConfig`/`ConfigInfo` Pydantic models, registered in `models/__init__.py`), `src/biz/dfch/specmgr/general/resources/config.py` (the `config_info()` resource function, registered in `general/resources/__init__.py`), `tests/general/resources/test_config.py` (13 tests, including ACC-002's non-disclosure tests). Updated `server.py`'s module docstring with a `specmgr://config` entry and regenerated `docs/MCP.md` via `specmgr mcp-docs`. Only the twelve known `SPECMGR_*_DIR` env var names are ever read (never `os.environ` wholesale), satisfying REQ-002. Full quality gate (`ruff format --check`, `ruff check`, `vulture`, full unittest suite of 3047 tests) passes.

#### 2026-09-02 00:00:00.000Z — Created

Feature drafted from GitHub issue #51 ("MCP server silently resolves per-domain base directories relative to CWD, with no way for a client to self-diagnose a misconfiguration"), covering a new `specmgr://config` resource and related README documentation fixes.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-09-02 — ConfigInfo model shape and location

`ConfigInfo`/`DomainConfig` were added to top-level `models/config_info.py` (mirroring `VersionInfo`'s location), not inlined in the resource module, since the payload is structured/machine-readable output (like `Iso25010`), not raw markdown prose (like `dtais`/`rasci`). `ConfigInfo` holds a single `domains: dict[str, DomainConfig]` field (domain name -> config) rather than twelve named fields, matching the plan's own "domain -> {...}" mapping wording and avoiding a 12-field model that would need editing for every future domain.

#### 2026-09-02 00:00:02.000Z — Never disclose non-directory environment variables

`specmgr://config` will explicitly enumerate only the known `SPECMGR_*_DIR` keys rather than iterating over the full process environment, to guarantee secrets such as PATs are never disclosed through this resource.

#### 2026-09-02 00:00:01.000Z — Cover all twelve domains, not just the three named in the issue

Although the issue only calls out `SPECMGR_DOCS_DIR`/`SPECMGR_ADR_DIR`/`SPECMGR_FEAT_DIR` by name, the diagnostic resource will report on all twelve domains for consistency and future-proofing.

#### 2026-09-02 00:00:00.000Z — Implement diagnosis as a resource, not a tool

A `specmgr://config` resource was chosen over a `get_config` tool, mirroring the existing `specmgr://version` resource's shape and because the reported information is descriptive/static-ish rather than an action.

### Related PRs / Commits

- [Issue #51](https://github.com/dfch/biz.dfch.SpecMgr/issues/51): tracking issue for this feature.
