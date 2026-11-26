# `biz.dfch.specmgr.commands.harness_bundle`

``harness-bundle`` -- regenerate the packaged harness bundle from the repo-root ``.opencode/`` tree.

Like ``specmgr docs`` regenerates committed documentation
from the codebase, this command regenerates the single committed package-data
bundle from the repo layout -- read from the current working directory, so
the repo root must be the CWD. A missing ``.opencode/`` directory, a scoped
markdown file that is not decodable as UTF-8 (or otherwise unreadable), and
an unwritable or uncreatable bundle output path are usage errors: each is a
deterministic stderr message naming the problem, exit 2, nothing written,
and no traceback.

It enumerates every ``*.md`` file recursively under exactly
``.opencode/{agent,command,skill}/`` -- exact top-level directory-name
match, singular names (``skill/`` holds one subfolder per skill, the only
nested layout) -- and serializes them, sorted by their ``.opencode/``-relative
``path``, into ``src/biz/dfch/specmgr/general/data/general_harness_bundle.json``
under the repo root, of shape ``{"instructions": <module constant>, "files":
[{"path", "sha256", "content"}]}`` where ``content`` is the file's verbatim
text and ``sha256`` the hex digest of that text. The serialization is
``json.dumps(indent=2, ensure_ascii=False)`` plus a trailing newline and no
timestamps, so two runs over an unchanged tree are byte-identical.

The top-level ``instructions`` field is the module constant
:data:`INSTRUCTIONS` -- the complete agent-driven install protocol
(feat-167-mcp-lifecycle-commands-2 Phase 130, REQ-008). The bundle is served
verbatim by the ``specmgr://harness-bundle`` MCP resource (the ``rasci.py``
pattern over ``read_packaged_text("general", "harness_bundle", "json")``),
and the consumer of that resource is an agent session of some harness
(OpenCode, Claude Code, ...) that installs the files into its own
configuration root per the protocol -- there is deliberately no install CLI.

A stray ``*.md`` at the ``.opencode/`` top level or under a non-scoped
directory (``node_modules/``, a similarly-named directory such as the
former ``zZz-skill/``) warns on stderr and is never bundled. This module is
``[cli]``-only: no ``mcp`` import, no server import.

Run this after adding/removing/editing any bundled ``.opencode/`` markdown
file and commit the result -- the ``specmgr-harness-bundle`` pre-commit hook
and the CI parity check (Python 3.13, alongside the ``specmgr
docs``/``mcp-docs`` steps) fail on drift.

## Functions

### `_scoped_markdown_files(opencode_dir: 'Path') -> 'list[Path]'`

Every ``*.md`` file under the scoped top-level directories, sorted by bundle ``path``.

Exact top-level directory-name match on :data:`_SCOPED_DIRS` (recursive
beneath each); a scoped directory that does not exist contributes
nothing. Sorting is by the ``.opencode/``-relative POSIX path string,
which is the bundle's own ``path`` field.


### `_stray_markdown_warnings(opencode_dir: 'Path') -> 'list[str]'`

One deterministic warning per stray markdown entry outside the bundled scope.

A stray is a ``*.md`` file directly under ``.opencode/`` (top-level) or
any ``*.md`` file under a direct subdirectory whose name is not one of
the scoped directory names (``node_modules/``, a similarly-named
directory such as the former ``zZz-skill/``); each non-scoped directory
yields at most one warning (with its recursive markdown count), so the
warning list stays bounded regardless of how large ``node_modules/``
is. Strays are never bundled.


### `generate_bundle_text(opencode_dir: 'Path') -> 'tuple[str, int]'`

Serialize the harness bundle over ``opencode_dir``'s scoped markdown tree.

Pure: reads the tree, writes nothing. Returns the bundle text together
with the number of bundled files -- the text is exactly what the command
writes to disk (``json.dumps(indent=2, ensure_ascii=False)`` plus a
trailing newline, no timestamps, so two calls over an unchanged tree are
byte-identical), and the count comes from the same single pass over the
scoped tree, so the caller never has to enumerate it a second time.


### `harness_bundle() -> 'None'`

Regenerate ``general/data/general_harness_bundle.json`` from the repo-root ``.opencode/`` tree.

Reads the repo layout from the current working directory (which must be
the repo root): enumerates every ``*.md`` under exactly
``.opencode/{agent,command,skill}/`` (sorted by ``.opencode/``-relative
path), warns on stderr for every stray markdown file outside that scope
(never bundled), and writes the deterministic bundle
(``{"instructions", "files": [{"path", "sha256", "content"}]}``,
``json.dumps(indent=2, ensure_ascii=False)`` + trailing newline, no
timestamps) to ``src/biz/dfch/specmgr/general/data/general_harness_bundle.json``
under the repo root. A missing ``.opencode/`` directory, a scoped
markdown file that is not decodable as UTF-8 (or otherwise unreadable),
and an unwritable or uncreatable bundle output path are usage errors
(each: one deterministic stderr message naming the problem, exit 2,
nothing written, no traceback). Prints a summary line (file count,
total bytes, output path). Run this after any change to a bundled
``.opencode/`` markdown file and commit the result (the
``specmgr-harness-bundle`` pre-commit hook and the CI parity check fail
on drift).

