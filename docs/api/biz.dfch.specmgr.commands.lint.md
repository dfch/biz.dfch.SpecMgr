# `biz.dfch.specmgr.commands.lint`

``lint`` -- the in-tree spec artifact parseability gate (feat-218, Phase 100).

Runs the model-level FULL parse of each document's own domain over the
document's complete on-disk text and reports every unparseable document
(file path + parse error), not just the first (REQ-001). The whole-body
domains are parsed through the domain registry's own ``parse_text``
adapters (the ``<d>.models`` package's pure text parsers -- ``parse_req``,
``parse_uc``, ... -- no file I/O, no ``DocCache``, no ``list_<d>``, no MCP
tool), ADR through the top-level ``models.adr`` package's own ``parse_adr``.
The parse-failure channels are the repo's existing ones, imported rather
than re-listed: ``general.models.validate_result._CAUGHT_EXCEPTIONS``
(``AssertionError``, ``pydantic.ValidationError``, ``yaml.YAMLError``) plus
``AdrParseError`` (a ``ValueError`` subclass, the same also-catch the
``validate_adr`` tool uses) plus UTF-8 decode errors -- caught per file so
one bad file cannot abort the aggregate report. Full parses only, never
the listing path (REQ-003): the ``list_feat`` dirty stage (frontmatter+H1
only, ADR 3982712a) is precisely the masking that hid the feat-214 defect
for three consecutive commits.

Three scopes, so the cost scales with the size of a change and never with
the size of the corpus (REQ-004):

* **Path mode** -- explicit ``PATHS`` on the command line. Each path's
  type is inferred from the path layout ALONE (REQ-005: the containing
  directory is named after a type, as in ``docs/req/x.md``, or the path
  has the ``feat/<id>/README.md`` shape), independent of every
  ``SPECMGR_*_DIR`` variable. ``--type`` overrides inference; an
  unrecognized layout is a usage error (exit 2) unless
  ``--skip-unrecognized`` is given, in which case the path is skipped
  and counted.
* **Type sweep** -- ``--type T`` with no paths sweeps every document of
  that type from its base directory: the explicit ``--dir`` argument
  (valid with ``--type`` ONLY) if given, otherwise the domain's
  registered base-dir resolver (REQ-006). ``--type T`` against an empty
  or missing base directory exits 0 with a 0-document summary: a
  registered-but-empty domain is not a misconfiguration.
* **All sweep** -- ``--all`` sweeps every registered type. Explicit
  paths combined with ``--all`` is a usage error; ``--all`` that finds
  zero documents in total is a probable misconfiguration (exit 2).

The ADR README exclusion (REQ-007) is unconditional, in path mode and
sweep mode, with or without ``--skip-unrecognized``: a file is excluded
-- never parsed and never counted as a failure -- when its resolved type
is ``adr`` (inferred from the layout or given by ``--type adr``) and its
base name is ``README.md``, in whichever directory. It is type-specific:
``feat/<id>/README.md`` is a real feat artifact and is never excluded.

Import safety (REQ-002): this module has NO module-level import of the
domain registry (``general.tools._domains``) or of any ``tools`` package.
``cli.py`` imports every ``commands/*`` module at module level, and any
such import would eagerly run the package's own ``__init__`` and drag in
the ``mcp`` extra -- verified by Task 100.100's real import test (with
``mcp`` blocked, ``commands.diagram`` and ``cli.py`` both fail to import
already; only the top-level ``models.*`` packages, ``_envregistry``, and
``plantuml.*`` import cleanly without the extra). Everything
registry-backed is therefore loaded inside the command body by
:func:`_registry_backed`, behind the ``ImportError`` -> exit 1 guard that
mirrors ``specmgr mcp`` and ``specmgr diagram``: the guard turns the
missing-extra condition into the clear exit-1 message whenever the CLI
is importable but the registry-backed chain is not -- in today's
``[cli]``-only install the sibling commands' pre-existing
package-init tangles block the CLI import first (issue #238 territory),
but this module no longer contributes to that. The one module-level
specmgr import is the ADR text parser
(``models.adr`` -- mcp-free by construction and verified import-safe;
the registry's ``--type`` acceptance set is deliberately NOT derived at
import time, so no Typer ``choices``).

Exit codes (pinned, REQ-008 -- the plantuml-check family):

* ``0`` -- every document parsed. Includes a run in which every given
  path was skipped or excluded (0-linted summary), and ``--type T``
  against an empty or missing base directory (0-document summary).
* ``1`` -- at least one document failed to parse, or the ``mcp`` extra
  is missing.
* ``2`` -- usage or resolution error: no paths and no sweep flag; an
  unreadable or missing path; an unrecognized layout without
  ``--skip-unrecognized``; ``--dir`` without ``--type``; explicit paths
  combined with ``--all``; an unknown ``--type``; ``--all`` that finds
  zero documents in total.

Report: every failing ``(path, error)`` pair is printed (the error is
the caught exception's own text, verbatim), each followed by its
per-type repair pointer: whole-body domains ``/repair {type} {id}`` with
the id derived from the path (the ``feat/<id>/README.md`` folder name
for ``feat``; the canonical UUID embedded in the file name for the
others, printed lowercased -- ids are case-insensitive on read and
lowercase is the canonical form), falling back to ``/repair {type}``
when no id can be derived; ADR -- which the repair flow does not cover
-- a line saying so, with the file to be fixed manually from the
reported error. One summary per invocation:
``summary: linted=N failed=N skipped=N excluded=N``, where ``linted`` is
the number of documents the gate took on (parse attempted) and ``failed``
the subset that failed to parse.

## Classes

### `_Failure`

One document that failed the gate: its path, its type, the error text.

Attributes:
    path:
        The document's on-disk path.
    doc_type:
        The resolved document type (drives the repair pointer's shape).
    error:
        The caught exception's own text, verbatim (UTF-8 decode
        failures carry a short ``not valid utf-8: ...`` prefix).


### `_RegistryBacked`

The registry-backed names this module loads lazily (see :func:`_registry_backed`).

Attributes:
    adr:
        The ``adr`` domain name (``general.tools._domains.ADR``).
    feat:
        The ``feat`` domain name (``general.tools._domains.FEAT``) --
        the one whole-body domain whose path shape is
        ``<base>/<id>/README.md``.
    all_domains:
        Every registered document type (``general.tools._domains.
        ALL_DOMAINS``: ``adr`` plus the whole-body domains) -- the
        ``--type`` acceptance set, derived, never hand-listed.
    whole_body_domain:
        The name -> ``WholeBodyDomain`` registry lookup (``general.
        tools._domains.whole_body_domain``) -- the source of each
        whole-body domain's ``base_dir``/``iter_paths``/``parse_text``
        adapters.
    caught_exceptions:
        The whole-body parse-failure channels (``general.models.
        validate_result._CAUGHT_EXCEPTIONS``: ``AssertionError``,
        ``pydantic.ValidationError``, ``yaml.YAMLError``).
    adr_base_dir:
        The ADR base-dir resolver (``adr.tools._paths.adr_base_dir``).
    iter_adr_paths:
        The ADR path iterator (``adr.tools._paths.iter_adr_paths`` --
        every ``*.md`` under the base directory, incl. the generated
        ``README.md`` table of contents, which the exclusion rule
        filters).


### `_WorkItem`

One document the gate took on: its path, its resolved type, its text.

Attributes:
    path:
        The document's on-disk path (as given, or as enumerated in
        sweep mode).
    doc_type:
        The resolved document type (layout-inferred or ``--type``).
    text:
        The complete file text for path-mode items (read during
        resolution; a read failure there is a usage error or a
        pre-recorded decode failure). ``None`` for sweep items --
        their text is read at parse time, where a read failure is a
        per-file parse failure (the file was enumerated by the
        registry, not named by the user).


## Functions

### `_base_dir_for(doc_type: 'str', reg: '_RegistryBacked') -> 'Path'`

The sweep base directory for one type (REQ-006: the registered resolver).

Args:
    doc_type: The document type to sweep.
    reg: The registry-backed names (the ADR base-dir resolver, the
        whole-body registry lookup).

Returns:
    The type's registered base directory (reading its own
    ``SPECMGR_*_DIR`` env var with its own default).


### `_derive_id(doc_type: 'str', path: 'Path', reg: '_RegistryBacked') -> 'str | None'`

The repair pointer's id, derived from the path alone (REQ-008).

``feat``: the folder name of the ``feat/<id>/README.md`` shape (the
feature's own id). The UUID-shaped types: the canonical UUID embedded
in the file name, printed lowercased -- ids are case-insensitive on
read, and lowercase is the canonical form.

Args:
    doc_type: The document's resolved type.
    path: The document's on-disk path.
    reg: The registry-backed names (the ``feat`` domain name).

Returns:
    The derived id, or ``None`` when no id can be derived (the
    pointer falls back to ``/repair {type}``).


### `_fail_usage(errors: 'list[str]') -> 'None'`

Report usage/resolution errors (stderr, one line each) and exit 2.

Args:
    errors: The usage-error messages (without the ``error: `` prefix).


### `_infer_type(path: 'Path', reg: '_RegistryBacked') -> 'str | None'`

The document type from the path layout ALONE (REQ-005).

Two rules, in order: (1) the containing directory's name is a member
of the registry's ``ALL_DOMAINS`` (e.g. ``docs/req/x.md``,
``docs/adr/x.md``); (2) the path has the ``feat/<id>/README.md``
shape -- base name ``README.md`` with exactly one non-``README.md``
path segment between a directory named after the ``feat`` domain and
the file (e.g. ``.specmgr/feat/feat-1-x/README.md``). Independent of
every ``SPECMGR_*_DIR`` variable.

Args:
    path: The document's path.
    reg: The registry-backed names (the ``ALL_DOMAINS`` membership
        set, the ``feat`` domain name).

Returns:
    The inferred type, or ``None`` when no rule matches (the
    unrecognized-layout case).


### `_is_excluded(doc_type: 'str', path: 'Path', reg: '_RegistryBacked') -> 'bool'`

The ADR README exclusion (REQ-007).

A file is excluded when its resolved type is ``adr`` (inferred from
the layout or given by ``--type adr``) and its base name is
``README.md``, in whichever directory. Unconditional (path mode and
sweep mode, with or without ``--skip-unrecognized``); type-specific --
``feat/<id>/README.md`` (type ``feat``) is never excluded.

Args:
    doc_type: The document's resolved type.
    path: The document's path.
    reg: The registry-backed names (the ``adr`` domain name).

Returns:
    ``True`` when the file is excluded (never parsed, never failed).


### `_iter_paths_for(doc_type: 'str', base_dir: 'Path', reg: '_RegistryBacked') -> 'Iterator[Path]'`

The sweep path iterator for one type under a given base directory.

The whole-body domains' registered ``iter_paths`` adapter (the shared
flat-file ``*.md`` enumeration, the ``feat/<id>/README.md`` folder
enumeration for ``feat``), the ADR ``*.md`` enumeration for ``adr``
(which yields the generated ``README.md`` table of contents too --
the exclusion rule filters it).

Args:
    doc_type: The document type to enumerate.
    base_dir: The base directory to enumerate under (``--dir`` or the
        registered resolver's result).
    reg: The registry-backed names.

Returns:
    The iterator over the type's document paths (sorted by name;
    empty for a missing base directory).


### `_parse_document(doc_type: 'str', text: 'str', reg: '_RegistryBacked') -> 'None'`

The model-level FULL parse of one document's exact text (REQ-003).

Whole-body domains: the registry's own ``parse_text`` adapter (the
domain's pure text parser -- no file I/O, no ``DocCache``, no
``list_<d>``, no MCP tool). ADR: the top-level ``models.adr``
package's ``parse_adr``. The parsed document is discarded -- the gate
only cares whether the parse raised.

Args:
    doc_type: The document's resolved type.
    text: The complete file content, frontmatter and body together.
    reg: The registry-backed names (the whole-body registry lookup).

Raises:
    Exception:
        The domain's parse-failure channels (the caller catches
        ``_CAUGHT_EXCEPTIONS`` plus ``AdrParseError``).


### `_registry_backed() -> '_RegistryBacked'`

The registry-backed names, imported lazily (they require the ``mcp`` extra).

Every name below lives in a package whose import chain reaches
``server.py`` (the ``general``/``adr``/domain-package ``__init__``s
eagerly import their ``tools``/``prompts`` sub-packages; the
``tools`` packages import the shared ``mcp`` application instance) --
see the module docstring's Task 100.100 import-test finding. The
caller catches the resulting ``ImportError`` as the missing-extra
condition (exit 1).

Returns:
    The :class:`_RegistryBacked` bundle of registry-backed names.


### `_repair_pointer(failure: '_Failure', reg: '_RegistryBacked') -> 'str'`

The per-type repair pointer for one failing document (REQ-008).

Whole-body domains: ``/repair {type} {id}`` with the path-derived id,
falling back to ``/repair {type}`` when none can be derived. ADR: the
repair flow is whole-body-only, so the pointer says ADR is not
covered and the file is to be fixed manually from the reported error.

Args:
    failure: The failing document.
    reg: The registry-backed names (the ``adr``/``feat`` domain
        names).

Returns:
    The pointer line (indented to follow its failure line).


### `lint(paths: 'Annotated[list[str] | None, typer.Argument(help="Document paths to lint (path mode). Each path\'s type is inferred from its layout unless --type is given (which overrides); unrecognized layouts are a usage error unless --skip-unrecognized is given. Linted regardless of any SPECMGR_*_DIR variable.")]' = None, type: 'Annotated[str | None, typer.Option(\'--type\', help="The document type (one of the registered domains -- a plain value validated at run time, not a fixed choice list). With paths: overrides the per-path layout inference. Without paths: sweeps every document of that type (from --dir if given, else the domain\'s registered base directory).")]' = None, all: "Annotated[bool, typer.Option('--all', help='Sweep every registered document type. Cannot be combined with explicit paths; exits 2 when zero documents are found in total (a probable misconfiguration).')]" = False, dir: 'Annotated[Path | None, typer.Option(\'--dir\', help="The base directory to sweep instead of the domain\'s registered one (valid with --type only).")]' = None, skip_unrecognized: "Annotated[bool, typer.Option('--skip-unrecognized', help='Skip (and count in the summary) paths whose layout matches no type, instead of a usage error.')]" = False) -> 'None'`

Lint specmgr artifacts: the model-level full parse, every failure reported.

Runs the document's own domain's model-level parser (REQ-003: full
parses only, never the listing/cache path) over the given paths
(path mode), every document of ``--type T`` (type sweep), or every
registered type (``--all``). Reports every failing ``(path, error)``
pair with its per-type repair pointer and one summary:
``summary: linted=N failed=N skipped=N excluded=N``.

Exit codes (REQ-008): ``0`` every document parsed (incl. a run where
every path was skipped or excluded, and ``--type T`` against an empty
or missing base directory); ``1`` at least one document failed to
parse (or the ``mcp`` extra is missing); ``2`` usage or resolution
error (see the module docstring for the full list).

