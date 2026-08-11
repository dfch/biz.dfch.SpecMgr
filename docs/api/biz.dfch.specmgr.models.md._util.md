# `biz.dfch.specmgr.models.md._util`

Shared, private validation helpers for the ``models.md`` subpackage.

Deliberately independent of ``models.adr.v1._util`` -- per ADR
bc5e18ad-6bbf-4265-bae4-3e34984a2d29, ``models.md`` owns its own small
validator helpers rather than depending on the ADR-specific package, even
though the two modules currently look near-identical. A future decision may
converge them; that is not decided here.

## Functions

### `blank_to_none(value: 'str | None') -> 'str | None'`

Normalize a blank/whitespace-only string to ``None``.

Used by optional frontmatter fields (``created``, ``updated``) so that
"absent" and "whitespace-only" are treated as the same state.


### `default_if_blank(value: 'object', default: 'str') -> 'object'`

Normalize a blank/whitespace-only (or ``None``) value to ``default``.

Used as a ``mode="before"`` validator for mandatory-but-defaulted string
fields (``MarkdownFrontmatter.status``) so an explicit but empty YAML key
is treated the same as the key being absent entirely, rather than
reaching the field's own validation with a blank value.


### `validate_schema_version(value: 'str') -> 'str'`

Validate a schema version string against this package's major version.

``value`` must be a ``major.minor.patch`` string whose major component
equals :data:`SCHEMA_MAJOR_VERSION`. Used by
``MarkdownFrontmatter.version``.

