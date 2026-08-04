# `biz.dfch.specmgr.commands.adr_toc`

``adr-toc`` -- generate table of contents for all ADRs in docs/adr.

Scans the ADR base directory (default ``docs/adr``, configurable via
``SPECMGR_ADR_DIR`` environment variable), collects all ADR documents,
and generates a README.md that lists them with their titles, links, and
frontmatter. This table of contents makes it easy to browse all ADRs
at a glance.

Run this after adding new ADRs and commit the result.

## Functions

### `_collect_adr_summaries() -> list[tuple[str, str, str, dict[str, str | None]]]`

Collect (id, title, filename, frontmatter_dict) from all valid ADR files in the base directory.

Returns a sorted list of tuples. Silently skips files that fail to parse.


### `adr_toc(output: Annotated[pathlib.Path | None, <typer.models.OptionInfo object>] = None) -> None`

Generate table of contents (README.md) for all ADRs.

Scans the ADR base directory (default ``docs/adr``, configurable via
``SPECMGR_ADR_DIR`` environment variable) and generates a README.md
that lists all ADRs with their titles, links, and frontmatter.
Pass ``--output`` to write elsewhere instead. Run this after adding
new ADRs and commit the result.


### `generate_adr_toc() -> str`

Generate the full contents of ``docs/adr/README.md`` (table of contents).

