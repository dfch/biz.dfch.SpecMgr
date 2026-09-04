# `biz.dfch.specmgr.general.resources.rasci`

Resource: specmgr://rasci (feat-30 Task 3.5, REQ-011).

Cross-cutting resource defining the generic RASCI (Responsible/
Accountable/Support/Consulted/Informed) responsibility-assignment
framework -- what RASCI is, the five roles' standard definitions, and how
RASCI differs from plain RACI. Motivated by the ``sop`` domain but
deliberately not scoped to it: RASCI, like ISO/IEC 25010, is a well-known
external framework rather than domain-coupled guidance, so this resource
follows ``specmgr://iso25010``'s cross-cutting placement under
``general/resources/`` rather than ``rsk/tara``'s domain-scoped one (whose
content is inseparable from RSK's own ``## Strategy`` vocabulary). The
content is limited to the five roles' generic definitions -- no
``sop``-specific heading names or cardinality rules leak in here; those
stay exclusively in ``sop``'s own schema field docstrings (surfaced via
``specmgr://sop/schema``) and packaged instructions.

Served as raw packaged markdown (``text/markdown``, mirroring
``iso25010``/``dtais``/``rsk/resources/tara``'s raw-markdown output, per
ADR 356d8781-e446-4c26-917a-eda85648ce9d's uniform convention: raw
markdown output, backed by a dedicated model that is parsed on every
resource call purely to fail fast on structural drift, with the parsed
result discarded and the original raw text returned unchanged) -- the
audience is an LLM agent that needs to read guidance, not code that needs
data. The ``sop`` domain reaches this resource via four explicit
cross-references (the six RASCI-family class
docstrings in ``sop/models/v1/body.py``, the ``create_sop``/``update_sop``
packaged instructions, ``sop/__init__.py``'s module docstring, and
``server.py``'s module docstring) rather than by copying the role
definitions into the ``sop`` schema.

## Functions

### `rasci() -> 'str'`

Return the packaged RASCI guidance's full markdown text, verbatim.

Same packaged-data source and no-cache, hard-failure-on-missing-file
design as every other cross-cutting ``general`` resource -- reads the
file fresh on every call. Also parses the text via
:func:`~biz.dfch.specmgr.general.models.parse_rasci` on every call
purely to fail fast on structural drift in production (ADR
356d8781-e446-4c26-917a-eda85648ce9d); the parsed result is discarded
and the raw text is returned unchanged.

Returns
-------
str
    The RASCI guidance document's raw markdown source.

Raises
------
FileNotFoundError
    If the packaged ``general_rasci.md`` is missing.
AssertionError
    If the packaged file's heading/list structure is malformed.
pydantic.ValidationError
    If the packaged file is structurally sound but a field value fails
    schema validation.

