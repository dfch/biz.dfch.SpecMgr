# `biz.dfch.specmgr.models.adr.v1._util`

Shared, private validation helpers for the ``models.adr`` subpackage.

## Functions

### `blank_to_none(value: 'str | None') -> 'str | None'`

Normalize a blank/whitespace-only string to ``None``.

Used by optional frontmatter/body fields so that "absent" and
"whitespace-only" are treated as the same state, consistent with the
render-time rule that an absent optional section omits its heading.


### `default_if_blank(value: 'object', default: 'str') -> 'object'`

Normalize a blank/whitespace-only (or ``None``) value to ``default``.

Used as a ``mode="before"`` validator for mandatory-but-defaulted
string fields (``AdrFrontmatter.status``) so an explicit but empty YAML
key -- e.g. MADR's own bare-bones template ships a placeholder
``status:`` with nothing after the colon, which a YAML loader parses as
``None``, not an absent key -- is treated the same as the key being
absent entirely, rather than failing type validation before the
field's own membership check ever runs. Mirrors :func:`blank_to_none`,
but substitutes a caller-supplied default instead of ``None``, for
fields that are not ``Optional``.


### `validate_schema_version(value: 'str') -> 'str'`

Validate a schema version string against this package's major version.

``value`` must be a ``major.minor.patch`` string whose major component
equals :data:`SCHEMA_MAJOR_VERSION`. Used by ``AdrFrontmatter.version``
(plan §3/§6) -- this schema-tracking field is a specmgr-only extension
to the frontmatter block, not part of the MADR standard, kept alongside
the MADR-defined keys (``status``, ``date``, ...) purely so it survives
the parse/render round-trip of the on-disk ``.md`` file.

