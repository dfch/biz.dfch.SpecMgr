# `biz.dfch.specmgr.general.resources.config`

Resource: specmgr://config -- resolved base directory diagnostics (feat-51-mcp-cwd).

The MCP server resolves every per-domain base directory relative to its own
process's current working directory unless a domain's own ``SPECMGR_*_DIR``
env var (or the shared ``SPECMGR_DOCS_DIR`` root eleven of the thirteen
domains share) is explicitly set. This resource lets a client self-diagnose
"am I pointed where I think I am?" by reporting, for all thirteen domains,
the resolved *absolute* base directory and whether the relevant env var was
explicitly set -- without requiring shell access to the server's host
(REQ-001/ACC-001).

**Never discloses arbitrary environment variables (REQ-002/ACC-002).** Only
the twelve known ``SPECMGR_*_DIR`` env var *names* are read here, and only
their *presence* (``os.environ.get(name) is not None``), never their value
and never any other environment variable -- this module never iterates over
or dumps ``os.environ`` wholesale.

Read-only, like every other domain's own ``*_base_dir()`` -- this resource
never creates a directory as a side effect of being read (it never calls any
``ensure_*_base_dir()``).

## Functions

### `config_info() -> 'ConfigInfo'`

Return the resolved base directory and env-var-set flag for every domain.

Explicitly enumerates the known ``SPECMGR_*_DIR`` env var names and
reads only those from the environment (REQ-002) -- ``adr`` and ``feat``
each have their own dedicated env var; the other eleven domains (``req``,
``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
``vcr``, ``sysrs``) all share the one root ``SPECMGR_DOCS_DIR`` env var,
so their ``env_var``/``env_var_set`` fields are identical by design, not
a bug.

Returns
-------
ConfigInfo
    The resolved base directory configuration for all thirteen domains.

