# `biz.dfch.specmgr.txt.tools.get_txt_schema`

``@mcp.tool()`` wrapper: get_txt_schema (feat-229-txt Phase 110).

Returns TXT's generated JSON Schema (2020-12 dialect) as raw text, read
from the packaged data copy (``txt/data/txt_schema.json``, via
``general.tools._packaged_data.read_packaged_text``) rather than
``docs/txt_schema.json`` directly -- the latter is only readable from an
editable/source checkout (``_paths.DOCS_DIR``'s own docstring documents
this), which would break for a real, non-editable ``pip install``. The
packaged copy is kept in sync with ``docs/txt_schema.json`` by the
pre-commit ``specmgr-schema-txt-package`` hook/CI step -- the same
``specmgr schema`` generator as ``docs/txt_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in
``commands/schema.py``.

Follows the ``get_vcr_schema``-style precedent (feat-189 Phase 105, ADR
112b6498-078b-4a59-88b8-8ffb7a5041b3): TXT ships the schema as a tool from
day one, since the domain was built after that ADR was accepted -- there
is no removed ``specmgr://txt/schema`` resource in its history. The
raw-text return deliberately follows the sibling
``get_txt_template``/``get_txt_example`` tools' own convention.

## Functions

### `get_txt_schema() -> 'str'`

Return the packaged TXT JSON Schema's raw text, verbatim.

The schema file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or
corrupted packaged file is not caught or wrapped here -- it propagates
as a hard :class:`FileNotFoundError`, the same let-it-raise convention
every other tool/resource in this codebase follows.

The returned text is the raw JSON document (the machine-readable /
parsed-JSON view of the structure, not the markdown view), which the
agent reads as text.

Returns
-------
str
    The packaged JSON Schema document's raw text, exactly as committed
    on disk.

