# `biz.dfch.specmgr.general.tools._doc_paths`

Generic, doc-type-agnostic base directory resolution, filename slugification,
and id -> path lookup (plan Task 3.10).

A single module shared across document domains (REQ now, UC later) instead
of a copy per domain: one root
env var (:data:`DOCS_DIR_ENV_VAR`, default :data:`DEFAULT_DOCS_ROOT`) holds
every doc type's own subdirectory (``{root}/{type_name}/``, e.g. ``docs/req/``
for ``type_name="req"``) -- the domain's own base directory
(:func:`doc_domain_base_dir`), under which every language keeps its own
sharded directory (the uniform layout, feat-245:
``docs/{type}/{language}/{id[:2]}/{id}-{slug}.md``, ``en`` included).


This module has no ``mcp``/file-write
dependency beyond read-only directory listing: :func:`doc_base_dir` never
creates the directory (a read-only tool shouldn't have that side effect),
only :func:`ensure_doc_base_dir` does.

**Cache-backed scan (feat-107-doc-cache Phase 3/4).** :func:`find_doc_path_by_id`
no longer re-parses a file's raw text unconditionally on every scan. Its
``read_fn`` parameter (formerly a text-taking ``parse_fn``) is expected to
be a domain's own content-hash-validated, cache-backed reader (e.g.
``req.tools._cache.read_req``) -- when a candidate file's on-disk content
hash is unchanged since the last time that path was read, ``read_fn``
returns the cached result without re-invoking the underlying parser
(DEC bfd76370-b59b-4d65-b550-a969f6c93c9d). Callers may also pass
``reconcile_fn`` (a domain's own cache-reconcile callable, e.g.
``req.tools._cache.reconcile_req_cache``), invoked once against the freshly
materialized live path listing *before* any per-file work, dropping any
cached entry for a file deleted outside specmgr's own tooling (REQ-005) --
this keeps orphan cleanup to a cheap set comparison rather than additional
file reads. The filesystem nonetheless remains the sole source of truth
(DEC 33c5ab08-ff58-4c73-8c32-23abaf3838e3): a cache entry is only ever a
memoization keyed by a validated content hash, so a stale entry is
structurally impossible -- it can only ever cost one extra parse, never an
incorrect result.

**Skip-on-parse-failure now also catches ``yaml.YAMLError`` (feat-107-doc-cache
Phase 6, REQ-010).** :func:`find_doc_path_by_id`'s per-file scan loop skips
a file that fails to parse so one broken file never blocks lookup of a
different, valid id. Before Phase 6 this only caught ``AssertionError``/
``ValueError``, which does not include ``yaml.YAMLError`` (not a
``ValueError`` subclass) -- even though every ``parse_<domain>`` genuinely
raises it unwrapped for malformed frontmatter YAML, and both ``DocCache``'s
own ``CACHEABLE_ERROR_TYPES`` and ``general.tools._listing.build_summaries``
already treated it as a normal, skippable failure. This was confirmed
pre-existing and unrelated to the cache mechanism itself (unchanged since
before Phase 3), but folded into this same remediation pass since it sits
in code this feature already touches and directly contradicts the cache's
own failure-handling contract.

**Skip-on-parse-failure now also catches ``FileNotFoundError`` (feat-107-doc-cache
Phase 8, REQ-014).** This scan iterates over a path list materialized at
one point in time (the directory-listing snapshot up front), but the
generic ``delete`` tool in ``general.tools`` only holds the *target*
document's own per-id lock, never a whole-domain lock, while ``get_*``/
``list_*`` intentionally take no lock at all (DEC
33c5ab08-ff58-4c73-8c32-23abaf3838e3) -- so a concurrent ``delete`` of *any
other* document in the same domain can remove a file between the scan's
directory listing and that file's own turn in the loop, raising
``FileNotFoundError`` out of ``read_fn``. Before Phase 8 this was not
caught here, even though it is the identical race class REQ-012 (Phase 6)
closed for ``feat`` alone, whose rename-based cache integration REQ-012
originally (and, per its own now-corrected text, incorrectly) claimed was
the only trigger for this class of bug -- the generic ``delete`` tool
triggers the exact same race for every one of the other domains. A file
vanishing mid-scan this way is now skipped exactly like any other
unparseable file, and the scan continues looking for the target id.

**Uniform sharded per-language layout (feat-245, Phase 100 -- refining DEC
38efdb66 item 1).** Every document of a UUID whole-body domain lives in a
shard subdirectory of its language's own directory, the shard named by the
first :data:`SHARD_DIGITS` characters of the document's uuid:
``docs/{type}/{language}/{id[:2]}/{id}-{slug}.md`` -- for every language,
English included. The flat-EN location DEC 38efdb66 item 1 reserved
(``docs/{type}/<type>-<id>-<slug>.md``) is retired: sharding already moves
every English file, so the compatibility argument is void --
:func:`doc_base_dir`/:func:`ensure_doc_base_dir` resolve every language
(``None`` (omitted) or the default language EN
(:data:`~biz.dfch.specmgr.general.models.heading_table.DEFAULT_LANGUAGE`)
included, no flat special case) to ``docs/{type}/{language}/``, so an
omitted language targets the ``en/`` directory. File names carry no
``{type}-`` prefix: the prefix-less ``<uuid>-<slug>.md`` convention
:func:`sharded_doc_path` builds (DEC's existing naming extended to every
sharded domain, REQ-002). The read path is shard-only (REQ-003, the hard
cut-over): :func:`iter_doc_paths` yields a language directory's sharded
listing (``<base>/*/*.md``, sorted by relative path), so a file directly
under ``docs/{type}/`` (missing language dir) or directly under
``docs/{type}/{language}/`` (missing shard dir) is invisible to every
``list_<d>``/``get_<d>``/id-resolution consumer;
:func:`find_doc_path_by_id`/:func:`find_parse_failure` scan the shard
derived from the id (:func:`shard_token`) first and fall back to the
language's full sharded listing, so a document whose placement disagrees
with its id still resolves (the filesystem remains the sole source of
truth, DEC 33c5ab08-ff58-4c73-8c32-23abaf3838e3). The EN-only consumers
(each domain's own scan via the omitted-language base directory, plus
``list_references``, ``find_related``/``find_similar_text``,
``get_reference_diagram(_all)``) are re-rooted at the ``en/`` directory by
that same omitted-language resolution -- ``None`` maps to ``en/``, never
the domain root -- so they never see a variant file by directory layout
alone (REQ-013/ACC-014, DEC 38efdb66 item 8, re-stated for the uniform
layout). :func:`language_for_doc_path` recovers the language a given
document path is encoded by: the path's first subdirectory under the
domain's own base directory (:func:`doc_domain_base_dir`), a shape-
validated two-letter name (``"en"`` included); any other position -- a
flat file, a non-shape-validated first subdirectory, a path outside the
base -- parses canonical. :func:`iter_doc_paths_all_languages` yields the
domain-wide live listing -- the union of the sharded listings of ``en/``
plus every shape-valid ``{language}/`` subdirectory -- that a domain's
reconcile-on-scan needs once a single language's scan no longer covers the
whole domain. Languages and shards sit at different path levels, so no
directory ever plays two roles: the two-letter code that is also a valid
two-hex shard name (``"de"``) needs no disambiguation (the shard/language
collision the uniform layout kills). Only a shard directory named by
exactly :data:`SHARD_DIGITS` lowercase-hex characters is read (feat-245
Phase 180, D4): a file in a non-hex directory is as invisible as a flat
one. An EMPTY shard or language directory -- e.g. the one the generic
``delete`` tool leaves behind after removing its last document -- is
expected and harmless (feat-245 Phase 180, I2; documented, not pruned):
git does not track empty directories, every read path here treats it as
no files, and pruning would race a concurrent ``create_<d>`` of a
different id in the same shard (the locks are per id, not per shard).

**A companion :func:`find_parse_failure` surfaces the parse-failure a skipped id
encodes (feat-150-mcp-lifecycle-commands Phase 1a, DEC
9080b37c-82b3-4f63-81f1-79641d0bf14c).** :func:`find_doc_path_by_id`'s
skip-on-parse-failure behavior above is deliberate and unchanged -- but it
means ``get_<d>`` on a document whose own file is broken raised only the
generic not-found error, with no parse cause/path/line, and that generic
error was being discarded client-side anyway (the DEC 519d1206
``isError: true`` truncation chain). :func:`find_parse_failure` recovers
exactly that case: it scans for the single file whose stem encodes the id
(``f"{id_}-"`` prefix), attempts the domain's own cache-backed reader on it,
and returns ``(path, str(exc))`` when that read raises a parse error, so
``get_<d>`` can return a non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` whose ``error``
text is byte-identical to the domain's ``list_<d>`` failed-row ``error``
(both are ``str()`` of the same exception from the same reader -- identical field
path and cause, including the trailing pydantic documentation line --
feat-162-doc-cache-exception-footer, GitHub issue #162, fixed ``DocCache``'s
exception reconstruction to preserve that footer on a warm re-raise). It returns
``None`` otherwise (no name match, a vanished file, or a name-matching file
that parses cleanly), leaving the caller to re-raise its original not-found
error unchanged. It does not alter :func:`find_doc_path_by_id`'s documented
skip behavior; of the generic id-resolving tools, only ``delete``,
``validate``, and ``list_references`` keep raising exactly as before on a
broken target -- ``update``/``edit``/``set_status``/
``set_classification`` now return the non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` via this probe
on their own ``XNotFoundError`` catch (feat-170-update-edit-parse-failure,
GitHub issue #170, DEC b8c9bfea-6dcf-4158-bfc5-4ec17abb842f, case 4 of the
DEC 519d1206-4d2a-4500-9046-6db635209996 workaround chain).

## Classes

### `DocNotFoundError`

No document file found matching the given id, under a given base directory.

**Methods:**

- `add_note(self, object, /)`
  Exception.add_note(note) --
  add a note to the exception

- `with_traceback(self, object, /)`
  Exception.with_traceback(tb) --
  set self.__traceback__ to tb and return self.


## Functions

### `_docs_root() -> 'Path'`

Return the configured documents root directory, without creating it.

Reads :data:`DOCS_DIR_ENV_VAR` through the central env-var registry's
``get_with_default`` accessor, falling back to the record's default
(the derived :data:`DEFAULT_DOCS_ROOT`) when the variable is unset or
set-but-empty (feat-208, Phase 120).


### `doc_base_dir(type_name: 'str', language: 'str | None' = None) -> 'Path'`

Return the base directory for ``type_name`` documents, in the given language, without creating it.

Resolves the language's own directory under the domain base
(:func:`doc_domain_base_dir`): ``docs/{type_name}/{language}/`` --
**every language, ``en`` included, no flat special case** (feat-245,
the uniform sharded layout, refining DEC 38efdb66 item 1, whose
flat-EN location is retired). ``None`` (omitted) therefore resolves to
the ``en/`` directory -- the EN-only call sites (every domain's own
``iter_<d>_paths()``/``find_<d>_path()`` scans, ``config_info()``, and
the EN-only consumers ``list_references``, ``find_related``/
``find_similar_text``, ``get_reference_diagram(_all)``) pass no
language and are re-rooted at ``en/`` by construction, never seeing a
variant file (REQ-003/REQ-005; the invariant holds only because
``None`` maps to ``en/`` rather than raising or returning the domain
root). Any non-None value is shape-guarded by
:func:`_path_safety.assert_language` first (a caller-supplied payload
like ``"../../etc"`` never reaches the path join) -- the guard runs on
the resolved value, so the defaulted ``"en"`` passes through the same
single code path. Read-only tools/resources use this so merely reading
never has the side effect of creating the directory -- see
:func:`ensure_doc_base_dir` for the write path.

Parameters
----------
type_name:
    The document type's subdirectory name, e.g. ``"req"``.
language:
    The document language to resolve. ``None`` (the default) or
    :data:`DEFAULT_LANGUAGE` (``"en"``) resolve to the ``en/``
    directory; any other shape-validated code (e.g. ``"de"``) resolves
    to that code's own directory under the domain base.

Returns
-------
Path
    The resolved base directory for ``type_name`` documents (in the
    given language).


### `doc_domain_base_dir(type_name: 'str') -> 'Path'`

Return the domain's own base directory (``{docs root}/{type_name}``, e.g. ``docs/req``), without creating it.

The parent of every per-language directory (feat-245, the uniform
sharded layout): ``docs/{type_name}/{language}/`` for every language --
the ``en/`` directory the omitted language of :func:`doc_base_dir`
targets, plus one directory per other language. This is the position
:func:`language_for_doc_path` derives the effective language from (the
document path's first subdirectory under this directory) and
:func:`iter_language_dirs` discovers over (every shape-valid two-letter
subdirectory of it is a language location, ``en/`` included). Reads
:data:`DOCS_DIR_ENV_VAR` through the central env-var registry's
``get_with_default`` accessor, falling back to the record's default
(the derived :data:`DEFAULT_DOCS_ROOT`) when the variable is unset or
set-but-empty. Never creates the directory.

Parameters
----------
type_name:
    The document type's subdirectory name, e.g. ``"req"``.

Returns
-------
Path
    The resolved domain base directory for ``type_name`` documents.


### `ensure_doc_base_dir(type_name: 'str', language: 'str | None' = None) -> 'Path'`

Return the base directory for ``type_name`` documents, in the given language, creating it if missing.

Only a doc type's ``create_*`` tool should call this -- every other
tool/resource uses the read-only :func:`doc_base_dir` instead. The
optional ``language`` parameter selects the same per-language
``docs/{type_name}/{language}/`` resolution as :func:`doc_base_dir`
(feat-245: every language, ``en`` included; the omitted language
targets the ``en/`` directory) before the directory is created.

Parameters
----------
type_name:
    The document type's subdirectory name, e.g. ``"req"``.
language:
    The document language to resolve -- see :func:`doc_base_dir`.

Returns
-------
Path
    The resolved, now-guaranteed-to-exist base directory for
    ``type_name`` documents (in the given language).


### `find_doc_path_by_id(base_dir: 'Path', id_: 'str', read_fn: 'Callable[[Path], _DocT]', get_id_fn: 'Callable[[_DocT], str | None]', reconcile_fn: 'Callable[[Iterable[Path]], None] | None' = None) -> 'Path'`

Resolve an ``id`` to its on-disk file path, for any doc type.

``base_dir`` is one language's own directory (``docs/{type}/{language}/``
-- the ``en/`` directory for English, feat-245's uniform sharded
layout). The scan is shard-narrowed (REQ-004): it materializes the
language's full sharded listing (``<base_dir>/*/*.md``, sorted by
relative path -- :func:`iter_doc_paths`) up front, reconciles a cache
against that same materialized listing (via ``reconcile_fn``, if given)
before doing any per-file work (the reconcile semantics, unchanged),
then reads the files of the shard derived from ``id_``
(:func:`shard_token`) first and only falls back to the listing's
remaining shards if the target is not among them -- a document whose
placement disagrees with its id is still found, so the filesystem
remains the sole source of truth (DEC
33c5ab08-ff58-4c73-8c32-23abaf3838e3). On a correctly placed document
the cold per-id cost drops from O(N-domain) parses to O(N/256). Each
path is read via ``read_fn`` and compared ``get_id_fn(parsed)`` against
``id_``. A file that fails to parse
(``AssertionError`` or ``ValueError``, which ``pydantic.ValidationError``
and every parser-specific error in this codebase -- subclass;
``yaml.YAMLError``, raised unwrapped
for malformed frontmatter YAML by every ``parse_<domain>`` function,
Phase 6, REQ-010; or ``FileNotFoundError``, raised by ``read_fn`` when
a file vanishes between this function's own directory-listing
snapshot and its own turn in the per-file scan loop -- e.g. a
concurrent ``delete`` tool call racing this lock-free scan, Phase 8,
REQ-014) is silently skipped -- one broken (or vanished) file must not
prevent lookup of a different, valid id. (Before Phase 6,
``yaml.YAMLError`` was not caught here -- it is not a ``ValueError``
subclass -- even though ``DocCache``'s own ``CACHEABLE_ERROR_TYPES``
and ``general.tools._listing.build_summaries`` (the ``list_*`` read
callback) both already treated it as a normal, skippable failure;
before Phase 8, ``FileNotFoundError`` was likewise not caught here,
even though it is the identical delete/scan race class REQ-012 (Phase 6)
closed for ``feat`` alone -- see this module's own docstring above for
the full explanation.)

Parameters
----------
base_dir:
    The language's own directory to scan for its sharded ``*.md``
    listing (e.g. ``docs/req/en``).
id_:
    The id to look up.
read_fn:
    Reads and parses a file at the given path into a document object
    (e.g. a domain's own cache-backed ``read_<domain>``, such as
    ``req.tools._cache.read_req``). Unlike the retired ``parse_fn`` this
    replaces, ``read_fn`` takes a ``Path``, not text -- a cache-backed
    reader decides for itself whether to re-read/re-parse ``path`` or
    return an already-validated cached result.
get_id_fn:
    Extracts the id (or ``None``) from a parsed document object (e.g.
    ``lambda doc: doc.frontmatter.id``).
reconcile_fn:
    When given, called once with the full materialized live path
    listing before any per-file work, to drop any cache entry for a
    path no longer present on disk (e.g.
    ``req.tools._cache.reconcile_req_cache``, REQ-005). ``None`` (the
    default) skips reconciliation entirely -- e.g. for a domain that
    has not yet wired a cache through this function.

Returns
-------
Path
    The resolved file path.

Raises
------
DocNotFoundError
    If no file's parsed id matches ``id_``.


### `find_parse_failure(base_dir: 'Path', id_: 'str', read_fn: 'Callable[[Path], _DocT]') -> 'tuple[Path, str] | None'`

Resolve the parse-failure for an id whose on-disk file exists but is unparseable.

Companion to :func:`find_doc_path_by_id` for the one case that function
deliberately cannot surface: a file whose own stem encodes ``id_``
(exactly one file can match, since names are unique) but whose content
fails to parse. :func:`find_doc_path_by_id`
silently skips such a file during its id scan (one broken file must not
block lookup of a different, valid id), so ``get_<d>`` on a broken
document would otherwise only raise the domain's generic not-found error,
with no parse cause, path, or line. This function recovers exactly that
case: it scans the language directory's sharded listing (
:func:`iter_doc_paths` over ``base_dir``) for the single name-matching
file -- a stem that carries ``id_`` as a hyphen-bounded token, i.e.
``f"-{id_}-" in stem`` (the legacy type-prefixed NAME
``<type>-<id>-<slug>.md`` -- the hard cut-over is about LOCATION, not
name: such a file moved into its correct shard without renaming (the
likely downstream migration) already resolves by id (content-based)
and passes the shape-only placement gate, and this match is what makes
``get_<d>`` return the real ``ParseFailureResult`` for it when it is
broken instead of a bare not-found -- feat-245 Phase 180, S3) or a
``f"{id_}-"`` prefix (the prefix-less ``<id>-<slug>.md`` form the
sharded layout writes) -- shard-narrowed first (the name matches inside the shard
derived from ``id_``) with the full listing as the fallback (a
misplaced broken document still surfaces), attempts the domain's own
cache-backed ``read_fn`` on it, and returns
``(path, str(exc))`` if that read raises a parse error
(``AssertionError``/``pydantic.ValidationError``/``yaml.YAMLError`` --
the same channels :func:`general.tools._listing.build_summaries` catches
for the ``list_<d>`` failed row, so ``str(exc)`` here is byte-identical
to that row's ``error`` field -- identical field path and cause,
including the trailing pydantic documentation line, since
feat-162-doc-cache-exception-footer (GitHub issue #162) fixed
``DocCache``'s exception reconstruction to preserve that footer on a
warm re-raise). It returns ``None`` for every other
outcome -- no name match, a name-matching file that vanishes mid-scan
(``FileNotFoundError``), or a name-matching file that parses cleanly
(a frontmatter-id mismatch, i.e. the file is not the requested document)
-- so a caller can re-raise its original not-found error unchanged.

feat-150-mcp-lifecycle-commands Phase 1a, DEC
9080b37c-82b3-4f63-81f1-79641d0bf14c: the ``get_<d>`` tools call this on
the domain's ``XNotFoundError`` and return a non-raising
:class:`~biz.dfch.specmgr.general.models.ParseFailureResult` for a
non-``None`` result. The four generic mutation tools
(``update``/``edit``/``set_status``/``set_classification``) now call it
the same way from their own per-domain adapters on the same catch
(feat-170-update-edit-parse-failure, GitHub issue #170, DEC
b8c9bfea-6dcf-4158-bfc5-4ec17abb842f -- case 4 of the DEC 519d1206
chain), with the same ``read_fn``/``assert_within`` mirroring.

Parameters
----------
base_dir:
    The language's own directory to scan for its sharded ``*.md``
    listing (e.g. ``docs/req/en``).
id_:
    The id whose on-disk file may exist but be unparseable.
read_fn:
    The domain's own cache-backed reader (e.g. ``req.tools._cache.
    read_req``) -- the same callable the domain's ``list_<d>`` tool reads
    with, so the captured ``str(exc)`` matches its failed row.

Returns
-------
tuple[Path, str] | None
    ``(path, error_text)`` for the name-matching, unparseable file, or
    ``None`` if there is no parse failure to surface (no name match, a
    vanished file, or a name-matching file that parses cleanly).


### `iter_doc_paths(base_dir: 'Path') -> 'Iterator[Path]'`

Yield the sharded listing of ``base_dir``: every ``*.md`` file in a two-hex shard directory directly below it.

The per-language scan primitive (feat-245, REQ-003): called with a
language's own base directory (``docs/{type}/{language}/`` -- ``en``
included), it yields ``<base>/<2-hex>/*.md`` sorted by relative path,
i.e. by (shard directory, file name) -- which for the prefix-less
``<uuid>-<slug>.md`` file names equals the lexicographic file-name
order, so ``list_<d>`` result order and ``ref`` values stay stable
except the intended prefix removal (REQ-008). Only a shard directory
whose name is exactly :data:`SHARD_DIGITS` lowercase-hex characters is
listed (feat-245 Phase 180, D4 -- the pattern is derived from
:data:`SHARD_DIGITS`, the same shape the ``specmgr lint`` placement gate
accepts). Files directly under ``base_dir`` (missing shard dir), files
in a non-hex directory (e.g. ``zz/``, ``Notes/``), and any deeper
nesting (deeper than one shard level) are excluded -- the shard-only
read is the hard cut-over: a misplaced file is invisible to every
``list_<d>``/``get_<d>``/id-resolution/``find_parse_failure``/
``list_languages``/similarity-corpus consumer (all of them list through
this function), and the ``specmgr lint`` layout-violation gate
(feat-245 Phase 120) is what catches it. Yields nothing (rather than
raising) if ``base_dir`` does not exist.

The EN-only consumers (each domain's own scan via the omitted-language
base directory, plus ``list_references``, ``find_related``/
``find_similar_text``, and ``get_reference_diagram(_all)``) are
re-rooted at the ``en/`` directory (ACC-008): their ``base_dir``
argument is the ``en/`` directory itself, so this same shard-only
listing never yields a variant file -- by directory layout, with no
glob-shape argument needed (REQ-013/ACC-014, DEC 38efdb66 item 8,
re-stated for the uniform layout).

Parameters
----------
base_dir:
    The language's own base directory to scan for its sharded
    ``*.md`` listing, e.g. ``docs/req/en``.

Returns
-------
Iterator[Path]
    An iterator over the matching paths, sorted by relative path.


### `iter_doc_paths_all_languages(base_dir: 'Path') -> 'Iterator[Path]'`

Yield the domain-wide live ``*.md`` listing: the sharded listing of every language directory.

The reconcile-on-scan counterpart of the uniform sharded layout
(feat-245, refining DEC 38efdb66 item 9): a domain's documents live in
one ``{language}`` subdirectory per language (``en/`` included), so a
scan of one language directory no longer covers the whole domain, and a
domain's cache-reconcile call must be handed the union -- the sharded
listing of ``en/`` plus the sharded listing of every other shape-valid
``{language}/`` subdirectory of ``base_dir`` (the domain's own base
directory, :func:`doc_domain_base_dir`) -- or a scan of one language
would evict the other languages' cached entries. Yields the union
sorted by path, and nothing (rather than raising) if ``base_dir`` does
not exist. Shard-only at the language level, like :func:`iter_doc_paths`:
a flat file (missing language dir) and any deeper nesting are never
part of any domain's live listing (no tool ever scans them, so no cache
entry for them can exist).

Parameters
----------
base_dir:
    The domain's own base directory, e.g. ``docs/dec``
    (:func:`doc_domain_base_dir`).

Returns
-------
Iterator[Path]
    An iterator over the matching, sorted paths.


### `iter_language_dirs(base_dir: 'Path') -> 'Iterator[tuple[str, Path]]'`

Yield ``(language, directory)`` for every shape-valid ``{language}`` subdirectory of ``base_dir``, sorted.

The directory-level discovery primitive of the language layout (feat-197-i18n Phase 140,
DEC 38efdb66 items 1/7; unchanged by feat-245's uniform sharded layout -- in it, the
shape-valid subdirectories of the domain's own base directory are exactly the language
directories, ``en/`` included, the shards sitting one level deeper): a direct subdirectory
of the domain's base directory whose name fullmatches the language-code shape (``^[a-z]{2}$``,
:data:`~biz.dfch.specmgr.general.tools._path_safety.LANGUAGE_PATTERN`) is a language location;
every other entry -- a plain file, a shape-invalid directory name (``"Notes"``, ``"de-DE"``,
a shard-shaped ``"00"``), anything deeper -- is not and is skipped. It never inspects the
directory's contents (a language directory may be empty, hold non-``.md`` assets, or hold
documents of other ids) and never descends. Yields nothing (rather than raising) if
``base_dir`` does not exist. :func:`iter_doc_paths_all_languages` is built on it, and the
language-listing tool (``list_languages``) probes each yielded directory for one id.

Parameters
----------
base_dir:
    The domain's own base directory, e.g. ``docs/dec``.

Returns
-------
Iterator[tuple[str, Path]]
    An iterator over ``(language code, subdirectory path)`` pairs, sorted by language code.


### `language_for_doc_path(base_dir: 'Path', doc_path: 'Path') -> 'str | None'`

Return the language a document path is encoded by, from its position under the domain base ``base_dir``.

The inverse of :func:`doc_base_dir`'s own language resolution
(feat-245, refining DEC 38efdb66 items 1/5): in the uniform sharded
layout the language is encoded by directory location only, and it is
the document path's **first subdirectory under the domain's own base
directory** (:func:`doc_domain_base_dir`, e.g. ``docs/dec``) --
``docs/dec/de/{shard}/x.md`` maps to ``"de"``, and
``docs/dec/en/{shard}/x.md`` maps to ``"en"`` (``"en"`` then resolves
to the canonical parse with no heading-mapping table, exactly like
``None`` does -- the shared table resolver treats the two identically,
so ``en`` is a normal language directory, not a special case). The
first subdirectory must fullmatch the language-code shape
(:data:`LANGUAGE_PATTERN`); every other
position maps to ``None`` -- a document directly under the domain base
(a missing language dir), a first subdirectory that is not a shape-
valid two-letter code (``"Notes"``, ``"de-DE"``, a shard-shaped
``"00"``), or a path outside ``base_dir`` entirely: it is not a
language location, so the document parses canonical-only and the
placement gate (feat-245 Phase 120) catches it. Note the shard level
(``{shard}``, two lowercase-hex characters) is never inspected: a
shape-valid two-letter first subdirectory is a language by its
position, and a shard that looks like one (``"de"``) sits one level
deeper, where no language is derived from it. Both paths are
``.resolve()``d before comparison (the ``DocCache`` REQ-009
normalization discipline), so relative and absolute spellings of the
same location agree.

Parameters
----------
base_dir:
    The domain's own base directory, e.g. ``docs/dec``
    (:func:`doc_domain_base_dir`).
doc_path:
    The on-disk document path to classify.

Returns
-------
str | None
    The shape-validated two-letter code of the document's first
    subdirectory under the domain base (``"en"`` for the default
    language's own directory included), or ``None`` for every other
    position (canonical parse).


### `shard_token(id_: 'str') -> 'str'`

Return the shard directory name for ``id_``: its first :data:`SHARD_DIGITS` characters.

The shard a document of id ``id_`` is placed in (feat-245, REQ-001):
``id_[:SHARD_DIGITS]`` -- e.g. ``"de"`` for ``"deadbeef-..."`` -- the
two-hex prefix of the uuid that names the directory
``docs/{type}/{language}/{shard}/``. In every sharded domain ``id_`` is
a canonical lowercase-hex uuid, so the token is a valid shard name by
construction; no further validation runs here (id shape is guarded at
the tool boundary, :func:`_path_safety.assert_uuid`).

Parameters
----------
id_:
    The document id whose shard to derive.

Returns
-------
str
    The shard directory name (the id's first :data:`SHARD_DIGITS`
    characters).


### `sharded_doc_path(base_dir: 'Path', id_: 'str', slug: 'str') -> 'Path'`

Return the sharded document path ``base_dir/{shard}/{id_}-{slug}.md``, creating the shard directory.

The single shared write-path layout helper every ``create_<d>`` tool
builds its target over (feat-245, REQ-001/REQ-002/REQ-005):
``base_dir`` is the language's own directory (``doc_base_dir(type,
language)`` -- ``docs/{type}/{language}/``, ``en`` included), the shard
subdirectory is named by :func:`shard_token` (the id's first
:data:`SHARD_DIGITS` characters), and the file name is ``{id_}-{slug}.md``
-- **no** ``{type}-`` prefix (the prefix-less naming convention, REQ-002).
Creates the shard directory (and the language directory, if missing) so
the caller can write the file directly; the returned path itself is not
created.

Parameters
----------
base_dir:
    The language's own base directory, e.g. ``docs/req/en``.
id_:
    The document's uuid (the shard is derived from it, and it leads the
    file name).
slug:
    The title slug the file name ends with (``slugify``'s output).

Returns
-------
Path
    ``base_dir / shard_token(id_) / f"{id_}-{slug}.md"``.


### `sharded_variant_path(base_dir: 'Path', source_path: 'Path', id_: 'str') -> 'Path'`

Return a language variant's sharded path ``base_dir/{shard}/{source_path.name}``, creating the shard directory.

The single shared write-path helper of every ``create_<d>`` tool's
*variant* branch (feat-245 Phase 180, E3 -- amending REQ-005's
single-helper wording: :func:`sharded_doc_path` builds a fresh EN
document's name, this helper places a variant): DEC 38efdb66 item 2 makes
the EN source's basename the single filename authority for a variant, so
the variant's file name is ``source_path.name`` **verbatim** -- never
rebuilt from a slug. Rebuilding (``removeprefix(f"{id_}-")`` +
:func:`sharded_doc_path`) would turn an EN source not named
``<id>-<slug>.md`` (a legacy type-prefixed ``<type>-<id>-<slug>.md`` file
moved into its shard without renaming, or a hand-named file) into a
different, doubled ``<id>-<type>-<id>-<slug>.md`` name. ``base_dir`` is
the variant language's own directory (``doc_base_dir(type, language)``),
the shard is :func:`shard_token` of ``id_`` (the variant is placed in its
id's own shard even when the EN source sits in a wrong shard). Creates
the shard directory (and the language directory, if missing); the
returned path itself is not created.

Parameters
----------
base_dir:
    The variant language's own base directory, e.g. ``docs/req/de``.
source_path:
    The resolved path of the EN source document (its basename is reused).
id_:
    The shared document id (the shard is derived from it).

Returns
-------
Path
    ``base_dir / shard_token(id_) / source_path.name``.


### `slugify(title: 'str') -> 'str'`

Derive a filename-safe slug from a document title.

Lowercases
``title``, collapses every run of non-``[a-z0-9]`` characters into a
single ``-``, strips leading/trailing ``-``, truncates to
:data:`_SLUG_MAX_LENGTH` characters (stripping a trailing ``-`` again in
case the truncation lands mid-run), and falls back to
:data:`_FALLBACK_SLUG` if the result would otherwise be empty (e.g. a
title with no alphanumeric characters at all).

Parameters
----------
title:
    The document title to slugify.

Returns
-------
str
    The filename-safe slug.

