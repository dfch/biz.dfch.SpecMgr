---
status: accepted
date: '2026-09-10'
decision-makers: dfch
id: 92cc4ce8-2cdd-45a7-9ae4-85de5abaf94c
version: 1.0.0
---

# Remove the Confluence tools (`confluence_fetch`, `confluence_update`) from the MCP server

## Context and Problem Statement

GitHub issue #120 ("Remove confluence tools") asks to remove the Confluence-specific MCP tools `confluence_fetch` and `confluence_update`, and their supporting helper modules, prompts, and data files, from this specmgr MCP server. These tools were added by feat-50-confluence (GitHub issue #50) and ADR a156fdf9-052c-4f43-93a2-eeec04a91eac, which renamed a generic `webfetch` tool to `confluence_fetch`, added `confluence_update` as a Confluence-page-writing counterpart, and self-constructed Confluence REST API URLs from browsable page URLs.

This specmgr MCP server exists to manage system-specification artifacts -- the REQ/UC/TSK/QA/PRB/GOL/RSK/DEC/SOP/FEAT/VCR/SYSRS/ADR document-type domains described in `AGENTS.md`. `confluence_fetch`/`confluence_update` instead implement a wiki/CMS synchronization concern (fetching and publishing arbitrary Confluence pages via the Confluence REST API), unrelated to any of those document-type domains. Living in the cross-cutting `general/` package alongside genuinely domain-agnostic utility tools (`mdformat`, the generic `update`/`set_status`/`set_classification`/`delete`/`validate` dispatch tools, and the `iso25010`/`dtais`/`rasci`/`version` reference resources), the two Confluence tools stand out as the only ones that are not utilities *for* spec-document management -- they are a separate product surface (Confluence page I/O) that happens to share a codebase. This blurs the server's single responsibility and is the trigger for this reversal.

This ADR documents the decision to remove `confluence_fetch`, `confluence_update`, and their supporting code entirely, and formally supersedes ADR a156fdf9-052c-4f43-93a2-eeec04a91eac, which is the ADR that originally introduced and shaped this functionality (the rename from `webfetch`, the URL self-construction design, and the shared `_confluence_config.py`/`_confluence_url.py` helpers). That ADR's decision to have these tools at all is reversed here; its own analysis of Confluence REST API/URL/SSO-redirect behavior remains historically accurate but is no longer acted upon.

## Decision Drivers

- MCP tools exposed by this server should stay focused on the single responsibility of managing system-specification documents (REQ/UC/TSK/QA/PRB/GOL/RSK/DEC/SOP/FEAT/VCR/SYSRS/ADR); a wiki/CMS page-sync concern does not belong alongside that, regardless of which package it lives in.
- GitHub issue #120 is an explicit, deliberate request to remove this functionality, not merely to refactor or relocate it.
- Removing unused functionality (and its now-unused `httpx` dependency) reduces the server's maintenance surface, dependency footprint, and test suite size with no loss of capability relevant to this server's stated purpose.
- Confluence page fetch/publish, if still needed by any consumer, is better served by a dedicated, general-purpose Confluence/Atlassian MCP server (as this repo's own coding environment already demonstrates via the separate `atlassian_confluence_*` tools available from an external MCP server) rather than duplicated bespoke logic inside a spec-document-management server.
- ADRs in this repository are a permanent decision log: reversing a prior decision must supersede the original ADR, not silently delete or rewrite it (per the original ADR's own historical record, and this repo's established convention).

## Considered Options

- Option 1: Keep the Confluence tools (`confluence_fetch`, `confluence_update`) as-is; do not act on issue #120.
- Option 2: Remove the Confluence tools and all their supporting code, tests, docs, environment variables, and the `httpx` dependency entirely (chosen).
- Option 3: Move the Confluence tools out of this server into a separate, standalone MCP server/package dedicated to Confluence integration, rather than deleting the functionality outright.

## Decision Outcome

**Chosen option: "Option 2: remove the Confluence tools entirely"**, directly implementing GitHub issue #120's explicit request. Keeping the tools (Option 1) leaves an unrelated domain mixed into a server whose entire purpose, as documented throughout `AGENTS.md`, is spec-document management -- every other tool in `general/` is either a generic dispatch tool operating on the twelve whole-body domains or a reference resource those domains depend on; the Confluence tools are the sole exception, and the issue that requested their removal reflects that this mismatch is no longer acceptable. Extracting them into a standalone MCP server (Option 3) was considered as a way to preserve the functionality for whichever consumer relies on it, but issue #120 asks for removal, not relocation, and building/maintaining a second MCP server/package is a materially larger undertaking than deleting code -- if Confluence integration is still needed by some consumer, this repo's own coding environment already demonstrates that a separate, general-purpose Atlassian MCP server (exposing `atlassian_confluence_*` tools) is the appropriate place for it, not a bespoke reimplementation maintained inside this repository.

This decision covers the ADR/decision-record step only (Phase 1 of feat-120-remove-confluence); the actual deletion of source code, tests, documentation, and the `httpx` dependency is carried out in Phase 2 of the same feature.

### Consequences

**Positive:**
- The MCP server's tool surface once again consists entirely of spec-document-management tools/resources/prompts plus genuinely domain-agnostic utilities, restoring the single-responsibility boundary `AGENTS.md` describes.
- Removes ~1774 lines of Confluence-specific test code and their corresponding source/prompt/data modules, shrinking the codebase and the test suite with no loss of capability relevant to this server's purpose.
- Removes the now-unused `httpx` dependency (and its `NOTICE` entry) once confirmed unused elsewhere in `src/`, shrinking the `mcp` extra's dependency footprint.
- Any consumer who still needs Confluence page fetch/publish can use a dedicated, general-purpose Confluence/Atlassian MCP server instead, which is a better architectural fit than a bespoke implementation bundled into a spec-document-management server.

**Negative:**
- This is a breaking change for any existing consumer of `confluence_fetch`/`confluence_update` and their `SPECMGR_CONFLUENCE_BASE_URL`/`SPECMGR_CONFLUENCE_BEARER` environment variables; such a consumer must migrate to an alternative (e.g. a standalone Confluence/Atlassian MCP server) with no deprecation shim or transition period provided by this repository.
- The URL-self-construction, SSO-redirect-detection, and Confluence-REST-API-shape knowledge captured in ADR a156fdf9-052c-4f43-93a2-eeec04a91eac's analysis is no longer exercised by any code in this repository once Phase 2 completes; that knowledge is preserved only in the superseded ADR's text and in feat-50-confluence's historical feature folder, not in any active implementation.
- If Confluence integration is ever needed again by this server specifically, the removed code would need to be reimplemented (or restored from version control history) rather than simply re-enabled.

### Confirmation

Phase 1 (this ADR) is confirmed by the new ADR file existing under `docs/adr/` and ADR a156fdf9-052c-4f43-93a2-eeec04a91eac's frontmatter `status` reading `superseded by <this ADR's id>`. Phase 2 (the actual removal) is confirmed by: no `confluence_fetch`/`confluence_update` tool or prompt registering with the MCP server; the full quality gate (`ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, `pytest -n auto`) passing with no Confluence-related test collection errors; no remaining `import httpx`/`from httpx` reference under `src/` and `httpx` removed from `pyproject.toml`/`NOTICE`; and `specmgr docs`/`specmgr mcp-docs` producing zero further `git status` diff.

## Pros and Cons of the Options

### Option 1: Keep the Confluence tools as-is

**Pros:**
- No breaking change for any existing consumer of `confluence_fetch`/`confluence_update`.
- Zero implementation effort.

**Cons:**
- Does not address GitHub issue #120's explicit request.
- Leaves an unrelated wiki/CMS-sync concern mixed into a server whose stated purpose is spec-document management, continuing to blur its single responsibility.
- Keeps carrying the `httpx` dependency and ~1774 lines of Confluence-specific tests for functionality this server's purpose does not need.

### Option 2: Remove the Confluence tools entirely

**Pros:**
- Directly implements GitHub issue #120's explicit request.
- Restores the MCP server's tool surface to spec-document-management tools plus genuinely domain-agnostic utilities only.
- Shrinks the codebase, test suite, and dependency footprint (removes `httpx` once confirmed unused elsewhere).
- Simplest option to implement and reason about; no new package/server to design, build, or maintain.

**Cons:**
- Breaking change: any existing consumer must migrate to an alternative (e.g. a standalone Confluence/Atlassian MCP server) with no deprecation shim provided.
- The Confluence-REST-API/URL-conversion/SSO-redirect-detection logic and its real-instance validation notes (captured in the superseded ADR) are no longer exercised by any code in this repository; if needed again, they would have to be reimplemented or restored from version control history.

### Option 3: Move the Confluence tools to a separate standalone MCP server/package

**Pros:**
- Preserves the functionality for any consumer that still needs it, without mixing it into this server's spec-document-management responsibility.
- Reuses the already-validated URL-conversion/SSO-redirect-detection logic rather than discarding it.

**Cons:**
- GitHub issue #120 asks for removal, not relocation -- does not directly satisfy the issue as filed.
- Building and maintaining a second MCP server/package is a materially larger undertaking than deleting code, for functionality this repository's own coding environment shows is already available from an external, general-purpose Atlassian MCP server (`atlassian_confluence_*` tools).
- Not chosen; retained here only for completeness of the options considered.

## More Information

- GitHub issue: https://github.com/dfch/biz.dfch.SpecMgr/issues/120
- Feature folder: `.specmgr/feat/feat-120-remove-confluence/README.md`
- Supersedes ADR a156fdf9-052c-4f43-93a2-eeec04a91eac ("Rename `webfetch` to `confluence_fetch`, add `confluence_update`, and self-construct Confluence REST API URLs instead of relying on a non-existent "confluence skill""), the ADR that originally introduced the functionality removed here.
