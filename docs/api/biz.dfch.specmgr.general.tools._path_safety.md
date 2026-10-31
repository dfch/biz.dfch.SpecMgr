# `biz.dfch.specmgr.general.tools._path_safety`

Reusable, doc-type-agnostic path-safety assertions for document ids,
language codes, and resolved paths (feat-36-delete, Phase 1).

Prevents path injection through a generic, type-dispatched document
tool's ``type``/``id`` inputs and confines a resolved path to the domain's
own base directory. A private, cross-domain helper in the same package
and in the same style as :mod:`_doc_paths`, :mod:`_splice`, and
:mod:`_paging`: it has **no** ``mcp`` dependency and performs **no
filesystem mutation** -- the functions only inspect ``str`` and
:class:`~pathlib.Path` values and raise :class:`ValueError` on failure,
naming the offending value. (:func:`assert_within`'s read-only
``Path.resolve()`` calls are the module's single, sanctioned filesystem
touch.)

**Language codes (feat-197-i18n, REQ-008/ACC-013).** :func:`assert_language`
is the shape guard for the caller-supplied ``language`` value every
i18n-aware tool takes: an ISO 639-1-shaped lowercase two-letter code
(:data:`LANGUAGE_PATTERN`, fullmatch ``^[a-z]{2}$``). The shape subsumes
the separator/traversal checks :func:`assert_no_traversal` gives ``id`` --
a two-lowercase-letter string can carry no path separator, no traversal
sequence, no case ambiguity -- so no second, separator-specific check is
needed. The guard is deliberately SHAPE-only (an open set: any
shape-valid code passes); whether a code is *usable* (a packaged
heading-mapping table exists for it) is enforced separately at
parse/write time by the table loader (ADR 38efdb66 item 6), so the set of
usable languages grows by adding one JSON file, never by a guard change.

The generic ``delete`` tool (``.specmgr/feat/feat-36-delete/README.md``,
Design Notes sections 2-6) was the first caller. The five functions are
now also called by every ``get_<d>`` tool (including ``get_adr``,
``get_sysrs`` since feat-32-sysrs Phase 3, and ``get_txt`` since
feat-229-txt Phase 130)
and by the generic ``update`` and ``set_status`` tools
(``.specmgr/feat/feat-38-39-41-43-44/README.md``, Phase 4, REQ-009): they
take only plain ``str``/``Path`` inputs, return ``None`` (raise on
failure), and carry no delete-specific state, argument, or return value --
in particular the delete-specific ``DeleteError`` wrapper (REQ-005)
deliberately lives in ``delete.py``, not here, because it is a
delete-specific concern, not a reusable safety primitive.

## Functions

### `_uuid_types() -> 'frozenset[str]'`

The UUID domains as a ``frozenset`` (O(1) membership in :func:`validate_id`).

The UUID domains whose ``id`` is a server-generated v4 UUID: derived
from the shared :data:`_domains.UUID_DOMAINS` source (feat-125-domain-
lists Phase 2, REQ-004) -- every whole-body domain other than ``feat``,
plus ``adr`` (feat-38-39-41-43-44 Phase 4, REQ-009; ``sysrs`` added
feat-32-sysrs Phase 3; ``txt`` added feat-229-txt Phase 130) -- ADR ids
are canonical lowercase-hex UUIDs of
the exact same shape (see ``adr.tools._paths.find_adr_path``/any
``docs/adr/*.md`` frontmatter ``id`` value). The ``frozenset`` keeps
O(1) membership. ``delete``'s own ``Literal`` type still excludes
``"adr"`` (its behavior is unchanged, D-Phase-4) -- that addition is
purely for use by ``get_<d>``/``update``/``set_status``.

The ``_domains`` import is deferred into this helper (called once per
:func:`validate_id` call, not at module import) because ``_domains``
pulls in every domain's own adapter imports (the feat-134 registry,
ADR 750842b2) and this module is imported from every ``get_<d>``
tool -- a module-level import here would be an import cycle.


### `assert_feat_id(id_: 'str') -> 'None'`

Reject any id that is not a well-formed ``feat-NNN-slug`` folder name.

Enforced for the ``feat`` domain (folder-per-document, ADR 8cf940c5):
``feat-``, one or more digits, ``-``, then a non-empty run of lowercase
alnum and hyphen.

Parameters
----------
id_:
    The id to check.

Raises
------
ValueError
    The value does not match the ``feat-NNN-slug`` shape; the message
    names the offending value.


### `assert_language(language: 'str') -> 'None'`

Reject any language value that is not an ISO 639-1-shaped lowercase two-letter code.

The shape guard for the caller-supplied ``language`` every i18n-aware
tool takes (feat-197-i18n, REQ-008/ACC-013, ADR 38efdb66 item 6): the
value must fullmatch :data:`LANGUAGE_PATTERN` (``^[a-z]{2}$``). Called
before any filesystem access, in the same pre-guard position as
``id``'s own :func:`validate_id`, so a payload like ``"../../etc"``,
``"de/x"``, ``"/abs"``, ``"DE"``, or ``""`` can never become part of a
resolved path. The shape subsumes the separator/traversal checks
:func:`assert_no_traversal` applies to ``id`` -- a two-lowercase-letter
string cannot carry a path separator, a traversal sequence, or any
other path-significant character -- so no second check runs.

The guard is SHAPE-only (an open set): any shape-valid code passes.
Whether a code is *usable* -- i.e. a packaged heading-mapping table
exists for it -- is enforced separately at parse/write time (the table
loader raises its own actionable error for a code without a table),
which keeps this guard static and dependency-free while the set of
usable languages grows by adding one JSON file, never by a guard
change.

Parameters
----------
language:
    The language value to check.

Raises
------
ValueError
    The value does not fullmatch :data:`LANGUAGE_PATTERN` (empty, not
    two characters, uppercase, digits, a path separator, or any other
    non-lowercase-letter character); the message names the offending
    value and the expected shape.


### `assert_no_traversal(id_: 'str') -> 'None'`

Reject any id that could contribute a relative path.

Universal guard, independent of domain: the value must be a non-empty
``str`` and must contain no ``/``, no ``\``, and no ``..``. This alone
makes it impossible for the id to escape its base directory when joined
into a path.

Parameters
----------
id_:
    The id to check.

Raises
------
ValueError
    The value is empty (or whitespace-only), or it contains a path
    separator (``/`` or ``\``) or the ``..`` traversal sequence; the
    message names the offending value.


### `assert_uuid(id_: 'str') -> 'None'`

Reject any id that is not a canonical lowercase-hex v4-shaped UUID.

Enforced for every :func:`_uuid_types` domain. (Subsumes
:func:`assert_no_traversal` for well-formed input, but both are applied
so the error message is precise.)

Parameters
----------
id_:
    The id to check.

Raises
------
ValueError
    The value does not match the canonical 8-4-4-4-12 lowercase-hex
    UUID shape; the message names the offending value.


### `assert_within(base_dir: 'Path', candidate: 'Path') -> 'None'`

Defense-in-depth: ``candidate.resolve()`` must be ``is_relative_to(base_dir.resolve())``.

Type-agnostic. Called by the adapters *after* id -> path resolution,
so that even if a future id-validation gap existed, a resolved path
could never point outside the domain's own base directory.

Parameters
----------
base_dir:
    The domain's own base directory.
candidate:
    The resolved candidate path to check.

Raises
------
ValueError
    ``candidate``, once resolved, lies outside ``base_dir`` once
    resolved; the message names both paths.


### `validate_id(type_: 'str', id_: 'str') -> 'None'`

Convenience dispatcher: :func:`assert_no_traversal` plus the type's format check.

``type_`` in :func:`_uuid_types` -> :func:`assert_uuid`;
``type_ == "feat"`` -> :func:`assert_feat_id`; any other ``type_`` ->
``ValueError`` (unknown type). This is the single entry point the
generic ``delete``, ``update``, ``set_status``, and every ``get_<d>``
tool (including ``get_adr``) call before any filesystem access.

Parameters
----------
type_:
    The document type name: one of the whole-body domains, or
    ``adr``.
id_:
    The id to check.

Raises
------
ValueError
    ``type_`` is not one of the supported document type names, or the
    id fails :func:`assert_no_traversal` or the type's own format
    check; the message names the offending value.

