# `biz.dfch.specmgr.general.tools._language_variants`

Per-language document location for the read-only translation tools (feat-197-i18n Phase 140).

The shared, private, ``mcp``-free helper behind the ``list_languages`` and ``check_translation_drift`` tools: given a
document ``type``/``id`` it finds the on-disk document of one *language* (or of every language) without ever
touching the EN-only scans of the other generic tools (REQ-013) -- it resolves each language's own directory through
the domain's own ``<d>_base_dir(language)`` (ADR 38efdb66 item 1: EN = the flat ``docs/{type}/``, any other validated
code = ``docs/{type}/{language}/``), reads through the domain's own cache-backed ``load_by_id``/``read_<d>``
(a variant is parsed through its language's heading table, derived from its path position), and discovers the
language directories of a domain through the shared :func:`~biz.dfch.specmgr.general.tools._doc_paths.
iter_language_dirs`. Nothing here writes, creates, or invalidates anything.

**Per-domain adapters.** The eleven i18n-eligible domains (:data:`~biz.dfch.specmgr.general.tools._language_guard.
LANGUAGE_AWARE_DOMAINS`) all expose the same three callables under the same names -- ``<d>.tools._paths.<d>_base_dir``,
``<d>.tools._io.load_by_id``, ``<d>.tools._cache.read_<d>`` -- so the adapter table is built by one loop instead of
33 hand-written imports; a domain that lacks one fails at import time, loudly.

**Located, parseable or not.** :func:`locate` returns a :class:`Location` for a document that exists on disk: a
healthy one carries ``parseable=True``; a document that exists but fails to parse (a broken file, or a language whose
heading table is missing) is *still located* -- ``parseable=False`` with the parse-failure message, the string form of
the very exception the domain's cache-backed reader raises, so it is byte-identical to the domain's ``list_<d>``
failed-row ``error`` and to ``get_<d>``'s ``ParseFailureResult.error`` for the same file in the same language (ADR
9080b37c). A document that does not exist at all raises the domain's own ``XNotFoundError`` (a ``LookupError``).

## Classes

### `Location`

A language variant of a document that exists on disk.

Attributes
----------
language:
    The language code of the variant (``"en"`` for the flat default-language document).
path:
    The resolved on-disk path.
parseable:
    ``True`` if the document parses in its language; ``False`` if it exists but fails to parse.
error:
    ``None`` if ``parseable``, else the parse-failure message.


### `_DomainAdapter`

One domain's three language-aware callables (see the module docstring).


## Functions

### `_build_adapters() -> 'dict[str, _DomainAdapter]'`

Build the per-domain adapter table from the domains' own modules (one loop; a missing callable fails loudly).


### `_reader_reporting_table_errors(read: 'Callable[[Path], object]') -> 'Callable[[Path], object]'`

Wrap a domain reader so a heading-table ``ValueError`` is reported as a parse failure, not propagated.

``find_parse_failure`` surfaces ``AssertionError``/``ValidationError``/``yaml.YAMLError`` as a parse failure; the
heading-table loader's plain ``ValueError`` (a language directory whose language has no packaged table) would
propagate out of it. For the read-only listing such a document *exists* and is merely unusable, so it is reported
like any other unparseable document -- the ``ValueError``'s text becomes the failure message.


### `list_language_variants(type_: 'str', id_: 'str') -> 'LanguageListResult'`

List every language the document ``id_`` of ``type_`` exists in (REQ-012, ACC-008).

Probes the flat EN directory and then every shape-valid ``{language}`` subdirectory of the domain's base
directory (:func:`~biz.dfch.specmgr.general.tools._doc_paths.iter_language_dirs`), each through :func:`locate`.
``"en"`` leads the result when the EN source exists and is never invented when it does not; the other languages
follow sorted by code. A variant that exists but fails to parse is listed with ``parseable=False``. Only ``.md``
documents participate (the domains' own scans are ``*.md`` globs), so a non-``.md`` sibling asset or a
shape-invalid directory name is never reported.

Parameters
----------
type_:
    One of the eleven i18n-eligible domains (already validated by the caller).
id_:
    The document id (already validated by the caller).

Returns
-------
LanguageListResult
    The languages found, in order, with one entry per language.

Raises
------
LookupError
    The domain's own ``XNotFoundError``: the document exists in no language at all (no EN source and no
    variant), with the message naming that fact.


### `locate(type_: 'str', id_: 'str', language: 'str') -> 'Location'`

Locate the ``language`` variant of document ``id_`` of ``type_`` on disk, parseable or not.

The caller has already validated ``type_`` (a language-aware domain), ``id_`` and ``language`` (shape, and for
a non-default language the heading table) -- this function does no argument validation of its own beyond
asserts, and reads nothing but the one language's directory.

Parameters
----------
type_:
    One of the eleven i18n-eligible domains.
id_:
    The document id (shared by every language variant).
language:
    The language to locate; ``"en"`` = the flat directory.

Returns
-------
Location
    The located document; ``parseable=False`` (with ``error``) when it exists but fails to parse.

Raises
------
LookupError
    The domain's own ``XNotFoundError``: no document with this id exists in this language's directory.
ValueError
    The resolved path lies outside the language's base directory (``assert_within``, defense in depth).

