# `biz.dfch.specmgr.commands.schema`

``schema`` -- generate JSON Schema (2020-12) for registered document-type models.

Generic, doc-type-agnostic command: each document type that wants a generated
JSON Schema artifact registers a ``generate_x() -> str`` function in
``_GENERATORS`` below, keyed by its short doc-type name (``"req"``, ``"uc"``).
``--type`` restricts generation to one registered type; omitting it generates
**all** registered types. Each type is written to its own
``{output_dir}/{type}_schema.json`` (default ``docs/``).

Unlike ``adr-toc``/``docs``, drift detection is built into this command
itself rather than left to a separate ``git diff --exit-code`` CI step: the
previous on-disk content (if any) is compared against the freshly generated
content for every type this invocation touches, and the command exits with
status 1 if any of them differ (including a file that did not exist yet).
The file is still (re)written either way, so a local run always leaves
``docs/`` up to date for a developer to commit; only the exit code signals
drift, which is what a CI step relies on directly.

The emitted dialect is Pydantic v2's native JSON Schema 2020-12 (``$defs``,
not ``definitions``) -- see `feat-6-requirement-artifact`'s README
"Decisions Made" for why this deliberately diverges from
``uc_schema.json``'s hand-authored draft-07.

## Functions

### `generate_qa_schema() -> str`

Generate QA's JSON Schema (2020-12 dialect) from ``QaDocument.model_json_schema()``.

Mirrors :func:`generate_req_schema` exactly, but for ``qa.models.v2``:
the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
default), and ``"$comment"`` holds ``qa.models.v2.SCHEMA_COMMENT_VERSION``
(currently ``"v2"``) instead of REQ's own version token.

Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
the same byte-identical-output/drift-detection reason as
:func:`generate_req_schema`.


### `generate_req_schema() -> str`

Generate REQ's JSON Schema (2020-12 dialect) from ``ReqDocument.model_json_schema()``.

Pydantic v2 deliberately omits the top-level ``$schema`` key by default
(see ``GenerateJsonSchema.generate``'s own comment on this), so it is
added explicitly here from ``GenerateJsonSchema.schema_dialect`` --
otherwise the emitted file would not self-describe which JSON Schema
dialect it actually uses.

Also injects a ``"$comment"`` key holding
``req.models.v1.SCHEMA_COMMENT_VERSION`` (currently ``"v1"``) -- a bare
schema-layout version token, distinct from any document instance's own
``frontmatter.version``, letting a caller that cached an earlier fetch
detect a REQ schema shape change without diffing the whole file.

Serializes with ``indent=2, sort_keys=True`` plus a trailing newline so
repeated generation from unchanged models produces byte-identical
output, which is what makes this command's own drift detection (and any
downstream ``git diff``) meaningful.


### `generate_tsk_schema() -> str`

Generate TSK's JSON Schema (2020-12 dialect) from ``TskDocument.model_json_schema()``.

Mirrors :func:`generate_req_schema` exactly, but for ``tsk.models.v1``:
the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
default), and ``"$comment"`` holds ``tsk.models.v1.SCHEMA_COMMENT_VERSION``
(currently ``"v1"``) instead of REQ's own version token.

Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
the same byte-identical-output/drift-detection reason as
:func:`generate_req_schema`.


### `generate_uc_schema() -> str`

Generate UC's JSON Schema (2020-12 dialect) from ``UcDocument.model_json_schema()``.

Mirrors :func:`generate_req_schema` exactly, but for ``uc.models.v2``:
the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
default), and ``"$comment"`` holds ``uc.models.v2.SCHEMA_COMMENT_VERSION``
(currently ``"v2"``) instead of REQ's own version token.

Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
the same byte-identical-output/drift-detection reason as
:func:`generate_req_schema`.


### `schema(type_: Annotated[str | None, <typer.models.OptionInfo object>] = None, output_dir: Annotated[pathlib.Path, <typer.models.OptionInfo object>] = PosixPath('/docs')) -> None`

Generate JSON Schema (2020-12) for one or all registered document types.

Writes ``{output_dir}/{type}_schema.json`` for each selected type
(``--type``, or every registered type if omitted). Exits with status 1
if any written file's content differs from what was already on disk
(including the file not existing yet), so CI can rely on this command's
own exit code instead of a separate ``git diff --exit-code`` step. The
file is written regardless of drift, so a local run always leaves
``docs/`` up to date to commit.

