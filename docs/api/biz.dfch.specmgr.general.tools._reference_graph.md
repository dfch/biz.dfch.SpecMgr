# `biz.dfch.specmgr.general.tools._reference_graph`

The reference-graph builders: scoped source-centred and registry-wide graph construction
(feat-207-reference-graph, Phase 110, REQ-002).

Thin over the feat-144-ref-artifact reference machinery (``general.tools._references``'s
:func:`find_references` / :func:`resolve_reference`) and the ``list_references``
tool's own per-domain source-scan legs (the ``(<d>_base_dir, load_<d>_by_id)``
pairs the tool's ``_SOURCE_LOADERS`` table holds, here re-dispatched over
``general.tools._domains.ALL_DOMAINS``): the reference extraction and target
resolution semantics are inherited verbatim -- the 11-tag ``<TYPE> <id>``
vocabulary (the UUID tags with a canonical uuid id, plus ``FEAT`` carrying the
full ``feat-NNN-slug`` id or the bare ``feat-NNN`` number), the code-fence
extraction caveat, and the feat dual-spelling behaviour (rulebook §3.7).

Two builders, one frozen construction semantics each (rulebook §3):

- :func:`build_source_graph` -- the scoped graph: the requested source
  document, its outgoing reference neighbourhood to ``depth`` (level 0 = the
  source; a level-k node is expanded only if k < depth and it resolved to an
  existing document, its body read through the domain's own read path -- the
  cache-aware leg for the 12 whole-body domains, the never-cached leg for
  ``adr``, ADR bfd76370), optionally plus the direct incoming references to
  the source (``reverse``: a full scan of all 13 source domains, additive and
  direct-only on the incoming side, with the feat dual-spelling match rule).
- :func:`build_registry_graph` -- the registry-wide graph: the same 13-domain
  scan; every successfully parsed document is a node; every extracted
  reference an edge; a target not present as a scanned document gets its
  title via :func:`resolve_reference` (dangling ⇒ the unresolved node).

Broken documents in any scan are **skipped** (never a node, never an edge
source; the render never fails -- the ``get_use_case_package_diagram``
precedent). The builders **never raise for target-side content** (a dangling
target becomes a ``title=None`` node); a **missing** source raises the source
domain's own ``XNotFoundError`` (propagated unchanged from the source
domain's own ``load_by_id``), and an **existing-but-broken** source raises
the domain's own parse error (the ``AssertionError``/
``pydantic.ValidationError``/``yaml.YAMLError`` channels, ``AdrParseError``
for ``adr``) -- the Phase 120 tool layer converts that to the non-raising
``ParseFailureResult`` (the feat-150 precedent), the builders themselves
raise. Every build runs over a visited (type, id) set (reference cycles
terminate by construction; they affect only rendering, rulebook §4).

The FEAT exclusion (``include_feat=False``, rulebook §3.5) is ONE post-hoc
rule applied LAST in all three modes: drop every FEAT node except the
explicitly requested source (scoped mode only has such a thing), then drop
every edge touching a dropped node -- a feat target must not surface as a
node in any mode.

Input contract: the builders assume VALIDATED input -- the ``type``/``id``
``_path_safety.validate_id`` guards and the ``depth`` 1..5 validation are the
Phase 120 tool / Phase 130 CLI layer's job (rulebook §7); an unvalidated
``type`` outside ``ALL_DOMAINS`` is a ``KeyError`` programming error (the
``resolve_reference`` unknown-tag channel), not a content failure.

No ``@mcp.tool()`` registration here (and no ``server`` import): the Phase
120 tool modules call into these builders. Plain Python over the per-domain
legs -- independently testable against isolated ``SPECMGR_*_DIR`` registries.

## Functions

### `_apply_feat_exclusion(title: 'str', nodes: 'dict[tuple[str, str], str | None]', edges: 'set[tuple[str, str, str, str]]', include_feat: 'bool', source_key: 'tuple[str, str] | None') -> 'ReferenceGraph'`

The FEAT exclusion (rulebook §3.5 -- ONE post-hoc rule, applied LAST in all modes).

``include_feat=True``: the full graph, unchanged. ``include_feat=False``:
drop every FEAT node except the explicitly requested source
(``source_key`` -- scoped mode only; the registry-wide builder passes
``None``), then drop every edge touching a dropped node. A feat target
must not surface as a node in any mode (the post-hoc drop is the
definition; the builders above never special-case feat during the
build, so this one rule is the whole exclusion).


### `_bare_feat_id(feat_id: 'str') -> 'str'`

The bare ``feat-NNN`` number form of a full ``feat-NNN-slug`` id (rulebook §3.2's match rule).

The source-id ``feat-177-list-ref-feat`` splits at the second hyphen
into ``feat-177`` -- the one reference spelling a full-spelling source
additionally matches in the reverse scan (a bare-spelling source cannot
occur: ``validate_id`` rejects it, rulebook §6).


### `_doc_title(type_: 'str', doc: 'Any') -> 'str'`

The scanned/loaded document's derived title (rulebook §3's node titles).

The same per-domain derivation ``general.tools._references``'s target
resolvers use (so a node reached via a reference and the same document
loaded as a source or scanned in a full scan always carry the identical
title): the ``feat`` H1 with its ``Feature: `` prefix stripped
(:func:`feature_title`), the ``adr`` body's own ``title`` field, every
other domain's body H1 (``doc.body.text``).


### `_iter_source_documents() -> 'Iterator[tuple[str, Path, Any]]'`

Every parseable document across all 13 source domains (rulebook §3.2/§3.3's full scan).

The paged full scan the reverse and registry-wide builders share, in
``ALL_DOMAINS`` order (adr first) and each domain's own sorted path
order (the domain's own path iterator: the shared flat-file
``iter_doc_paths`` for every whole-body domain other than ``feat``,
``iter_feat_paths`` for ``feat``, ``iter_adr_paths`` for ``adr``). Each
path is read through the domain's own leg (the cache-aware
``read_<d>`` for the 12 whole-body domains, the never-cached
``read_adr`` for ``adr``); a document that fails to parse
(:data:`_SCAN_ERROR_TYPES` channels) or vanishes mid-scan
(``FileNotFoundError``) is skipped (rulebook §3.4 -- never a node, never
an edge source), so the scan never raises for content.

Yields ``(type, path, doc)`` -- the document's own parsed model, whose
frontmatter id and derived title the builders read; the reference
extraction itself scans the raw, frontmatter-stripped body text
(``_splice.body_text`` over the yielded path -- the ``list_references``
source-read precedent: extraction needs the literal markdown).


### `_load_source(type_: 'str', id_: 'str') -> 'tuple[Path, Any]'`

Resolve + parse the scoped source document (rulebook §3.4's source-side contract).

The ``list_references`` source-leg precedent (the source domain's own
id resolution, the parsed document discarded except for its path and
derived title): a **missing** source raises the source domain's own
``XNotFoundError`` (propagated unchanged, identical to ``get_<d>``); an
**existing-but-broken** source raises the domain's own parse error (via
:func:`_raise_broken_source` -- the Phase 120 tool layer converts that
to the non-raising ``ParseFailureResult``, the feat-150 precedent).

Returns
-------
tuple[Path, Any]
    ``(path, doc)`` -- the resolved source file (confined to the source
    domain's own base directory) and its parsed document.


### `_raise_broken_source(type_: 'str', base_dir: 'Path', id_: 'str', read_fn: 'Callable[[Path], Any]') -> 'None'`

Re-raise the domain's own parse error for an existing-but-broken source (rulebook §3.4).

Called from :func:`_load_source` on the source domain's
``XNotFoundError`` (a broken source's own id is unreadable by the id
lookup, which skips unparseable files -- so missing and broken surface
as the same ``LookupError`` and must be probed apart here). The
flat domains and ``adr`` go through the shared
:func:`general.tools._doc_paths.find_parse_failure` name-match scan
(for ``adr``, a broken file's own ``AdrParseError``/``ValidationError``
propagates out of ``find_parse_failure``'s leg read directly -- already
the domain's parse error); ``feat`` goes through its folder-per-document
counterpart :func:`find_feat_parse_failure` (the flat-file stem match
cannot see a ``<base>/<id>/README.md``). For a name-matching broken
file, the leg is re-run on the matched path to re-raise the live
exception (the cache-backed leg re-raises a fresh, equivalent stored
failure at near-zero cost, feat-162's byte-identical message); a
name-matching file that parses cleanly on the re-run (a repair racing
the probe) returns silently, letting the original not-found propagate.


### `_reference_matches_source(reference: 'tuple[str, str]', source_key: 'tuple[str, str]', source_bare_id: 'str | None') -> 'bool'`

Whether one extracted reference matches the scoped source on (type, id) (rulebook §3.2).

Strict (type, id) equality for the UUID domains; for a full
``feat-NNN-slug`` source additionally the bare ``feat-NNN`` spelling
(the feat dual-spelling rule -- the reverse side of the inherited
extraction caveat, rulebook §3.7).


### `_unique_references(text: 'str') -> 'list[tuple[str, str]]'`

``find_references`` with repeated (type, id) occurrences deduped (first-occurrence order kept).

The row-materialization-level dedup the ``list_references`` tool does
itself (rulebook §3: each unique (type, id) reference adds exactly one
edge + one node).


### `build_registry_graph(*, include_feat: 'bool' = True) -> 'ReferenceGraph'`

Build the registry-wide reference graph (rulebook §3.3/§3.5).

The same full 13-domain scan the reverse pass uses: every successfully
parsed document is a node (title via :func:`_doc_title`); every
extracted reference is an edge (deduped per source document); a target
not present as a scanned document gets its title via
:func:`resolve_reference` (dangling ⇒ ``title=None`` ⇒ the unresolved
node). Broken documents are skipped (rulebook §3.4) and documents whose
frontmatter id is ``None`` are not addressable nor referenceable, so
they contribute no node (every reference id is a concrete uuid or feat
id; the builders' graph keys are (type, id) pairs). The graph title is
the frozen ``Reference Graph`` default (the tool layer's ``title``
override replaces it before rendering). The FEAT exclusion is applied
last (rulebook §3.5 -- ``source_key=None``: every FEAT node drops).

Parameters
----------
include_feat:
    When ``False``, apply the FEAT exclusion (rulebook §3.5) last:
    drop every FEAT node, then every edge touching a dropped node.

Returns
-------
ReferenceGraph
    The registry-wide graph (title = ``Reference Graph``).

Raises
------
AssertionError
    A non-bool ``include_feat`` (program-invariant failure only -- the
    builder never raises for registry content).


### `build_source_graph(source_type: 'str', source_id: 'str', *, depth: 'int' = 1, reverse: 'bool' = False, include_feat: 'bool' = True) -> 'ReferenceGraph'`

Build the scoped reference graph of one source document (rulebook §3.1/§3.2/§3.5).

Level 0 = the source (loaded via the source domain's own id resolution:
a missing source raises the domain's own ``XNotFoundError``, an
existing-but-broken source raises the domain's own parse error -- the
Phase 120 tool layer's ``ParseFailureResult`` conversion point). The
forward expansion is a BFS over outgoing references: a level-k node is
expanded only if k < ``depth`` and it resolved to an existing document
(its body read through ``_splice.body_text`` -- the raw,
frontmatter-stripped markdown, the ``list_references`` source-read
precedent); each unique (type, id) reference adds exactly one edge +
one node (the node title via :func:`resolve_reference`; a dangling
target = ``title=None`` = the unresolved node). ``reverse=True`` is
ADDITIVE and direct-only on the incoming side: the full 13-domain scan
adds a scanned document as a node + one incoming edge to the source iff
it carries a reference matching the source on (type, id) (the feat
dual-spelling rule: a full ``feat-NNN-slug`` source also matches a bare
``feat-NNN`` reference) -- no transitive incoming expansion (a scanned
document's own references are never walked; only the forward frontier
grows with ``depth``). The graph title is the source's derived H1
(the :func:`_doc_title` derivation -- the same one a reference to the
source would resolve to). The visited (type, id) set bounds the build
(rulebook §3.6); the FEAT exclusion is applied last (rulebook §3.5).

Parameters
----------
source_type:
    The source document's lowercase domain name: one of
    ``ALL_DOMAINS`` (the 12 whole-body domains plus ``adr``). Assumed
    validated by the caller (the Phase 120 tool's own ``type``
    parameter); a name outside ``ALL_DOMAINS`` is a ``KeyError``
    programming error.
source_id:
    The source document's verbatim id (the canonical lowercase-hex
    uuid for the UUID domains, the full ``feat-NNN-slug`` for
    ``feat`` -- a bare ``feat-NNN`` is a wrong-format id the tool layer
    rejects, rulebook §6). Assumed validated by the caller.
depth:
    The forward BFS depth (1..5, default 1 -- the tool/CLI layer
    validates the range; this builder assumes validated input and
    ``assert``s the contract). Governs the forward part only.
reverse:
    When ``True``, add the direct incoming references to the source
    (the additive 13-domain scan, rulebook §3.2).
include_feat:
    When ``False``, apply the FEAT exclusion (rulebook §3.5) last:
    drop every FEAT node except this source (when it is one), then
    every edge touching a dropped node.

Returns
-------
ReferenceGraph
    The scoped graph (title = the source's derived H1).

Raises
------
KeyError
    ``source_type`` is outside ``ALL_DOMAINS`` -- a programming error
    (the tool layer validates the type first).
LookupError
    The source domain's own ``XNotFoundError`` (a ``LookupError``
    subclass): no document of ``source_type`` has this id.
AssertionError / pydantic.ValidationError / yaml.YAMLError / AdrParseError
    The source exists but fails to parse -- the domain's own parse
    error (the tool layer converts it to the non-raising
    ``ParseFailureResult``).
AssertionError
    ``depth`` outside 1..5 or a non-int ``depth`` (the caller's
    validation contract), or a non-str/bool argument.

