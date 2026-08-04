# `biz.dfch.specmgr.models.adr.v1.renderer`

Render an :class:`Adr` back into the canonical on-disk ``.md`` text (plan §7, §10 item 2).

Pipeline stage 3 of "parse -> validate -> render" (plan §7). "parse" and
"validate" are ``parser.py`` and the models' own Pydantic validators
respectively; this module only does the "render" half, and it always
regenerates the *full* file deterministically from the parsed/constructed
:class:`Adr` rather than patching text in place (plan §7) -- there is no
AST-preserving round-trip requirement, so a human's original spacing/comment
choices are never reproduced, only the canonical form the schema defines.

Two independent building blocks:

- :func:`_render_frontmatter` -- serializes :class:`AdrFrontmatter` back to a
  YAML block via ``yaml.safe_dump`` (not hand-rolled string formatting), so
  values that would otherwise round-trip into a different YAML-native type on
  the next parse (e.g. a ``date``-shaped string like ``"2024-01-15"``) get
  correctly quoted by the YAML dumper itself. Keys are emitted in a fixed
  order (``status``, ``date``, ``decision-makers``, ``consulted``,
  ``informed``, ``version``) via ``sort_keys=False`` on an already-ordered
  dict, and any field that is ``None`` is omitted entirely -- consistent with
  ``AdrFrontmatter``'s "whole object, full replace" contract (plan §3): there
  is nothing partial to reconcile at render time, the model already reflects
  exactly what should be written.
- :func:`_render_body` -- walks the fixed section table (plan §4) in
  document order, omitting any optional field that is ``None`` (heading and
  all), then appends the derived ``## Pros and Cons of the Options``
  container (plan §5) iff ``options`` is non-empty, and finally
  ``## More Information`` (always last, per the table).

## Functions

### `_render_body(body: 'AdrBody') -> 'str'`


### `_render_decision_outcome(body: 'AdrBody') -> 'str'`


### `_render_frontmatter(fm: 'AdrFrontmatter') -> 'str'`


### `_render_pros_and_cons(body: 'AdrBody') -> 'str'`


### `_section(title: 'str', content: 'str', level: 'int' = 2) -> 'str'`


### `render_adr(adr: 'Adr') -> 'str'`

Render a full :class:`Adr` into canonical MADR-derived markdown text.

Parameters
----------
adr:
    The structured document to render.

Returns
-------
str
    The complete file content -- YAML frontmatter block followed by the
    markdown body -- exactly as it should be written to disk. Always
    ends with exactly one trailing newline.

