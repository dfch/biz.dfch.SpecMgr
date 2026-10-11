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
the known env var *names* are read here, and the presence flags report
only their *presence* -- every one of them through the central env-var
registry's raw accessor ``_envregistry.get(name) is not None`` (the three
base-dir vars since feat-208 Phase 120; ``SPECMGR_SIMILARITY_DISABLED``,
``SPECMGR_FEAT_WARMUP_DISABLED``, and the three PlantUML source vars since
Phase 130) -- never their value and never any other environment variable.
Since feat-208 Phase 140 the module carries **no** direct ``os.environ``
read at all: the one remaining *value* read, ``FASTEMBED_CACHE_PATH``,
likewise goes through the registry -- its ``get_with_default`` accessor
(inserting the record's registered default for an unset or set-but-empty
value) -- and this module never iterates over or dumps ``os.environ``
wholesale. Two
deliberate, user-requested additions
for the similarity section (feat-134 Phase 7, REQ-013): the *presence* of
``SPECMGR_SIMILARITY_DISABLED`` is likewise reported (flag only, never its
value, the same convention), and ``FASTEMBED_CACHE_PATH`` is read (through
the registry's ``get_with_default`` accessor) to report
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

**Static plantuml section (feat-185-uc-diagrams Phase 120).** The payload
additionally carries a ``plantuml`` section (``PlantumlConfig``): the
**presence-only** state of the exactly-three PlantUML validation-source env
vars (``SPECMGR_PLANTUML_JAR``/``SPECMGR_PLANTUML_BIN``/
``SPECMGR_PLANTUML_URL`` -- rulebook §3.1; each reported as ``{set: bool}``,
never its value: a jar path, a bin path, or a server URL would be a
disclosure violation of REQ-002's own contract), plus ``selected`` -- the
first-set-wins selection over the three (rulebook §3.2, derived from
``plantuml.chain.select_source``; ``"none"`` when all are unset, the
structure-only floor). Static configuration only, like ``similarity``:
whether the selected source actually *answers its canary right now* is the
``validate_plantuml`` tool's own ``source_state``/``available`` result, not
part of this resource.

## Functions

### `_similarity_cache_dir() -> 'str'`

The resolved similarity model cache directory the resource reports (feat-134 Phase 7, REQ-013).

Mirrors ``fastembed.common.utils.define_cache_dir``'s own resolution
algorithm -- ``FASTEMBED_CACHE_PATH`` if set, else
``<tempdir>/fastembed_cache`` -- minus its ``mkdir(parents=True,
exist_ok=True)`` side effect: reading ``specmgr://config`` must never
create a directory (the resource's own no-side-effects contract,
ACC-018). The value read goes through the central env-var registry's
``get_with_default`` accessor (feat-208 Phase 140), whose registered
default is this same ``<tempdir>/fastembed_cache`` expression -- so an
unset or set-but-empty ``FASTEMBED_CACHE_PATH`` falls back to the
default, exactly as the pre-migration ``os.environ.get(...) or
default`` did. The duplication is deliberate, since this module must
not import ``fastembed`` (the ``similarity`` extra may not even be
installed); it is also the drift watchpoint -- a future ``fastembed``
release that changes ``define_cache_dir``'s resolution logic would
silently desync this helper, so keep the two in step on a
``fastembed`` version bump.

Returns:
    The cache directory as an absolute path string (an unset or
    empty ``FASTEMBED_CACHE_PATH`` falls back to the default, so the
    result is always absolute); the directory is never created here.


### `config_info() -> 'ConfigInfo'`

Return the resolved base directory and env-var-set flag for every domain, plus the similarity and
plantuml sections and the feat_warmup_disabled flag.

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

The ``plantuml`` section (feat-185-uc-diagrams Phase 120) is static
configuration only: the **presence** of each of the exactly-three
validation-source env vars (the registry's raw accessor
``_envregistry.get(var) is not None`` -- never a value; feat-208
Phase 130), plus ``selected``, derived from
``plantuml.chain.select_source`` (the rulebook §3.2 first-set-wins
order JAR → BIN → URL; ``"none"`` when all three are unset). The
``validate_plantuml`` tool's own dynamic availability (whether the
selected source answers its canary right now) is deliberately not part
of this payload; it is that tool's ``source_state``/``available``
result.

``feat_warmup_disabled`` (feat-187-list-feat-timeout, Task 110.120, ADR
3982712a-a46b-4b2b-809f-9c6925a49b44) follows the same presence-only
convention: whether ``SPECMGR_FEAT_WARMUP_DISABLED`` is set, gating the
unified startup warmup thread's ``feat`` frontmatter/full-parse phases.

Returns
-------
ConfigInfo
    The resolved base directory configuration for every domain, plus
    the static similarity section, the static plantuml section, and
    the feat_warmup_disabled flag.

