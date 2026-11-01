# `biz.dfch.specmgr.feat.tools.get_feat_schema`

``@mcp.tool()`` wrapper: get_feat_schema (feat-189 Phase 105, Task 105.110).

Returns FEAT's generated JSON Schema (2020-12 dialect) as raw text, read
from the packaged data copy (``feat/data/feat_schema.json``, via
``general.tools._packaged_data.read_packaged_text``) rather than
``docs/feat_schema.json`` directly -- the latter is only readable from an
editable/source checkout (``_paths.DOCS_DIR``'s own docstring documents
this), which would break for a real, non-editable ``pip install``. The
packaged copy is kept in sync with ``docs/feat_schema.json`` by the
pre-commit ``specmgr-schema-feat-package`` hook/CI step -- the same
``specmgr schema`` generator as ``docs/feat_schema.json``, just a second
``--output-dir``, so no bespoke copy logic exists in
``commands/schema.py``.

Replaces the removed ``specmgr://feat/schema`` resource
(``feat.resources.feat_schema``) with this tool, per ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3
("Convert the 12 per-domain schema resources to get_<d>_schema tools"):
the raw-text return deliberately follows the sibling
``get_feat_template``/``get_feat_example`` tools' own convention instead of
the removed resource's parsed-dict return (the ADR's micro-decision D1),
and the wire content the agent sees is the same JSON document either way.

## Functions

### `get_feat_schema() -> 'str'`

Return the packaged FEAT JSON Schema's raw text, verbatim.

The schema file is shipped as package data (declared in ``pyproject.toml``'s
``[tool.setuptools.package-data]``), so its presence is a build-time
guarantee, not something that can be missing at runtime in a correctly
installed package. Reads the file fresh on every call (no in-memory
cache). A missing or corrupted packaged file is not caught or wrapped
here -- it propagates as a hard :class:`FileNotFoundError`, the same
let-it-raise convention every other tool/resource in this codebase
follows.

Unlike the removed ``specmgr://feat/schema`` resource (ADR 112b6498-078b-4a59-88b8-8ffb7a5041b3), the
returned text is **not** parsed into a dict: it is the raw JSON document
(the machine-readable / parsed-JSON view of the structure, not the
markdown view), which the agent reads as text.

Returns
-------
str
    The packaged JSON Schema document's raw text, exactly as committed
    on disk (byte-identical to ``docs/feat_schema.json``, kept in sync
    by the pre-commit hook/CI step).

