---
created: '2026-08-14T21:21:56.426598'
id: efb7d049-a222-4730-901f-6d57283b387c
status: done
type: tsk
updated: '2026-08-14T21:50:38.434867'
version: 1.0.0
---

# Implement `webfetch` MCP Tool (Bearer-Authenticated, URL-Filtered Fetch for Web Server)

<!-- Implementation plan for feat-7-various-improvements Task 0.14: a general, cross-cutting MCP tool that fetches a URL over HTTP GET, but only if the URL matches a configured base URL (case-insensitively) and sends a bearer token read from an environment variable. Intended primarily for Web Server instances that accept PAT (Personal Access Token) authentication, but implemented as a generic authenticated fetch, not Web Server-specific page-ID/REST-API logic. Number the tasks so that they are easier to track. -->

- [x] Task 1: Add `httpx` as a direct dependency in `pyproject.toml`'s `mcp` extra

    It is already a transitive dependency of the `mcp` package itself, per `uv.lock`. Run `uv sync --all-extras` to update `uv.lock` accordingly.

- [x] Task 2: Define env-var constants and config helper in `general/tools/webfetch.py`

    Create `SPECMGR_WEBFETCH_BASE_URL` and `SPECMGR_WEBFETCH_BEARER` env-var constants, plus a private accessor / config-reading helper. Mirror the constant+private-helper pattern used in `general/tools/_doc_paths.py` and `adr/tools/_paths.py` (module-level `*_ENV_VAR` constants, no `pydantic-settings`, direct `os.environ.get(...)` reads).

- [x] Task 3: Define two custom exceptions in `general/tools/webfetch.py`

    Create `WebfetchNotConfiguredError` (raised when `SPECMGR_WEBFETCH_BASE_URL` and/or `SPECMGR_WEBFETCH_BEARER` are not set) and `WebfetchUrlNotAllowedError` (raised when the requested URL does not match the configured base URL). Follow the repo's house style of typed exceptions rather than error-dict returns.

- [x] Task 4: Implement the `webfetch` MCP tool function in `general/tools/webfetch.py`

    Create the `@mcp.tool(name="webfetch", ...)`-decorated function `webfetch(url: str) -> str`. Validate configuration is present (else raise `WebfetchNotConfiguredError`). Validate the URL against the configured base URL using a case-insensitive prefix match (e.g. `url.casefold().startswith(base_url.casefold())`, not a plain `str.startswith`), else raise `WebfetchUrlNotAllowedError`. Then issue `httpx.get(url, headers={"Authorization": f"Bearer {token}"}, follow_redirects=True, timeout=...)` (note `httpx` does not follow redirects by default, unlike `urllib.request` — this must be set explicitly). Raise on a non-2xx response and return `response.text` as the raw response body (no HTML-to-markdown conversion or JSON parsing — the calling agent processes the raw content itself, consistent with a plain fetch tool).

- [x] Task 5: Register the tool in `general/tools/__init__.py` and update docstrings

    Import the new tool in `general/tools/__init__.py` and add it to `__all__`. Update `general/__init__.py`'s and `server.py`'s module docstrings to list the new `webfetch` tool.

- [x] Task 6: Add comprehensive tests in `tests/general/tools/test_webfetch.py`

    Use `unittest.mock.patch` on the `httpx.get` call and `mock.patch.dict(os.environ, ...)` for the two env vars. Cover: a URL outside the configured base is rejected with `WebfetchUrlNotAllowedError` and no HTTP call is made; a URL matching the base with different casing (in scheme/host and/or in the configured base URL itself) is still accepted; missing env var(s) raise `WebfetchNotConfiguredError`; a successful call sends the correct `Authorization: Bearer <token>` header and returns the raw response body text; a non-2xx response raises.

- [x] Task 7: Regenerate documentation with `specmgr docs` and `specmgr mcp-docs`

    Regenerate `docs/api/`, `docs/GENERATED.md` (`specmgr docs`) and `docs/MCP.md` (`specmgr mcp-docs`), Python 3.13.

- [x] Task 8: Document the tool in `README.md`'s Environment Variables section

    Add documentation for the `webfetch` tool and its two environment variables (`SPECMGR_WEBFETCH_BASE_URL`, `SPECMGR_WEBFETCH_BEARER`) in the top-level `README.md`'s "Environment Variables" section (currently listing `SPECMGR_ADR_DIR`/`SPECMGR_DOCS_DIR`). Follow the existing bullet-list style. This is separate from Task 7 since `README.md`'s prose is hand-maintained, not auto-generated.

- [x] Task 9: Run formatting, linting, and test verification

    Verify with `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite.

- [x] Task 10: Update the task list and set status to done

    Update this task list for every task list item and add updates with specmgr mcp. Set the status of the task list to done.

- [x] Task 11: Update `.specmgr/feat/feat-7-various-improvements/README.md`

    Remove Task 0.14's inline instructions text and replace it with a pointer to this task list's id. Add an entry to that feature's Decisions Made / Recent Updates logs.

## Recent Updates

### 2026-08-16 - Created

Created this task list per `feat-7-various-improvements` Task 0.14's instructions, after clarifying scope with the user: a generic bearer-authenticated GET fetch (not Web Server-page-ID-specific), using `httpx` (promoted from transitive to direct dependency), returning the raw response body, with a case-insensitive base-URL prefix filter, registered as `general/tools/webfetch.py`'s `webfetch` MCP tool.

### 2026-08-16 - Implementation complete

Completed all 11 tasks. `httpx` promoted to a direct dependency in the `mcp` extra (Task 1). Added `general/tools/webfetch.py` with `SPECMGR_WEBFETCH_BASE_URL`/`SPECMGR_WEBFETCH_BEARER` env-var constants and a private config helper (Task 2), `WebfetchNotConfiguredError`/`WebfetchUrlNotAllowedError` typed exceptions (Task 3), and the `webfetch` MCP tool itself using a case-insensitive `casefold()` prefix match plus `httpx.get(..., follow_redirects=True)`, raising on non-2xx and returning the raw `response.text` (Task 4). Registered the tool in `general/tools/__init__.py` and updated the `general/__init__.py` and `server.py` module docstrings (Task 5). Added 8 fully-mocked tests in `tests/general/tools/test_webfetch.py` covering URL-filter rejection with no HTTP call made, case-insensitive matching on both the request URL and the configured base URL, missing-env-var(s) errors, a successful call asserting the `Authorization: Bearer <token>` header and returned body text, and a non-2xx raise (Task 6). Regenerated `docs/api/`, `docs/GENERATED.md`, and `docs/MCP.md` via `specmgr docs`/`specmgr mcp-docs` on Python 3.13 (Task 7). Documented the two new environment variables in the top-level `README.md`'s Environment Variables section (Task 8). Verified clean via `ruff format --check`, `ruff check`, `vulture src/ whitelist.py --min-confidence 60`, and the full `unittest` suite (988 tests, all passing) (Task 9). Updated `.specmgr/feat/feat-7-various-improvements/README.md`: Task 0.14 checked off and its status changed to `done`, plus a matching "Completed" entry added to that feature's Recent Updates log (Task 11).
