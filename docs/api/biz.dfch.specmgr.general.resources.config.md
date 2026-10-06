# `biz.dfch.specmgr.general.resources.config`

Resource: specmgr://config -- resolved base directory diagnostics (feat-51-mcp-cwd).

The MCP server resolves every per-domain base directory relative to its own
process's current working directory unless a domain's own ``SPECMGR_*_DIR``
env var (or the shared ``SPECMGR_DOCS_DIR`` root most domains share) is
explicitly set. This resource lets a client self-diagnose
"am I pointed where I think I am?" by reporting, for every domain,
the resolved *absolute* base directory and whether the relevant env var was
explicitly set -- without requiring shell access to the server's host
(REQ-001/ACC-001).

**Never discloses arbitrary environment variables (REQ-002/ACC-002).** Only
the known ``SPECMGR_*_DIR`` env var *names* are read here, and only
their *presence* (``os.environ.get(name) is not None``), never their value
and never any other environment variable -- this module never iterates over
or dumps ``os.environ`` wholesale. Two deliberate, user-requested additions
for the similarity section (feat-134 Phase 7, REQ-013): the *presence* of
``SPECMGR_SIMILARITY_DISABLED`` is likewise reported (flag only, never its
value, the same convention), and ``FASTEMBED_CACHE_PATH`` is read to report
the *resolved* model cache directory (a path, by design -- the client needs
to know where the model is cached; unset or empty falls back to the default
``<tempdir>/fastembed_cache``). A third presence flag,
``SPECMGR_FEAT_WARMUP_DISABLED`` (feat-187-list-feat-timeout, Task 110.120,
ADR 3982712a-a46b-4b2b-809f-9c6925a49b44), is reported the same way --
whether the unified startup warmup's ``feat`` frontmatter/full-parse phases
are disabled.

Read-only, like every other domain's own ``*_base_dir()`` -- this resource
never creates a directory as a side effect of being read (it never calls any
``ensure_*_base_dir()``), and it never imports ``fastembed`` (the
``similarity`` extra may not be installed; the extra-installed check is a
``importlib.util.find_spec`` spec lookup only, ACC-018).

**Static similarity section (feat-134 Phase 7, REQ-013).** The payload
additionally carries a ``similarity`` section (``SimilarityConfig``):
whether the ``similarity`` extra (``fastembed``) is installed, whether the
presence-based ``SPECMGR_SIMILARITY_DISABLED`` opt-out flag is set, the
fixed model name (the shared ``SIMILARITY_MODEL_NAME`` constant, the same
single source ``get_default_provider()`` reads, ACC-020), and the resolved
model cache directory. Static configuration only: the tools' own dynamic
runtime availability (whether the model is loaded/usable right now) is
their structured ``{available, reason, message}`` result, not part of this
resource -- it deliberately reports no ``loaded`` or other runtime state.

## Functions

### `_similarity_cache_dir() -> 'str'`

The resolved similarity model cache directory the resource reports (feat-134 Phase 7, REQ-013).

Mirrors ``fastembed.common.utils.define_cache_dir``'s own resolution
algorithm -- ``FASTEMBED_CACHE_PATH`` if set, else
``<tempdir>/fastembed_cache`` -- minus its ``mkdir(parents=True,
exist_ok=True)`` side effect: reading ``specmgr://config`` must never
create a directory (the resource's own no-side-effects contract,
ACC-018). The duplication is deliberate, since this module must not
import ``fastembed`` (the ``similarity`` extra may not even be
installed); it is also the drift watchpoint -- a future ``fastembed``
release that changes ``define_cache_dir``'s resolution logic would
silently desync this helper, so keep the two in step on a
``fastembed`` version bump.

Returns:
    The cache directory as an absolute path string (an unset or
    empty ``FASTEMBED_CACHE_PATH`` falls back to the default, so the
    result is always absolute); the directory is never created here.


### `config_info() -> 'ConfigInfo'`

Return the resolved base directory and env-var-set flag for every domain, plus the similarity section.

Explicitly enumerates the known ``SPECMGR_*_DIR`` env var names and
reads only those from the environment (REQ-002) -- ``adr`` and ``feat``
each have their own dedicated env var; every other domain (``req``,
``uc``, ``tsk``, ``qa``, ``prb``, ``gol``, ``rsk``, ``dec``, ``sop``,
``vcr``, ``sysrs``) shares the one root ``SPECMGR_DOCS_DIR`` env var,
so their ``env_var``/``env_var_set`` fields are identical by design, not
a bug.

The ``similarity`` section (feat-134 Phase 7, REQ-013) is static
configuration only: ``find_spec("fastembed")`` (a spec lookup, never an
import) for ``extra_installed``, the presence-based
``SPECMGR_SIMILARITY_DISABLED`` flag for ``disabled``, the shared
``SIMILARITY_MODEL_NAME`` constant for ``model_name``, and
:func:`_similarity_cache_dir` for ``cache_dir`` -- reported, never
created (ACC-018). The tools' own dynamic availability (whether the
model is loaded/usable right now) is deliberately not part of this
payload; it is their structured ``{available, reason, message}``
result.

``feat_warmup_disabled`` (feat-187-list-feat-timeout, Task 110.120, ADR
3982712a-a46b-4b2b-809f-9c6925a49b44) follows the same presence-only
convention: whether ``SPECMGR_FEAT_WARMUP_DISABLED`` is set, gating the
unified startup warmup thread's ``feat`` frontmatter/full-parse phases.

Returns
-------
ConfigInfo
    The resolved base directory configuration for every domain, plus
    the static similarity section.

