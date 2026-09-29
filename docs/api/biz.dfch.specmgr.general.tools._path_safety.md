# `biz.dfch.specmgr.general.tools._path_safety`

Reusable, doc-type-agnostic path-safety assertions for document ids and
resolved paths (feat-36-delete, Phase 1).

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

The generic ``delete`` tool (``.specmgr/feat/feat-36-delete/README.md``,
Design Notes sections 2-6) was the first caller. The five functions are
now also called by every ``get_<d>`` tool (including ``get_adr``,
and ``get_sysrs`` since feat-32-sysrs Phase 3)
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
feat-32-sysrs Phase 3) -- ADR ids are canonical lowercase-hex UUIDs of
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

