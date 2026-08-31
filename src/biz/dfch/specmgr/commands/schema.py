# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""``schema`` -- generate JSON Schema (2020-12) for registered document-type models.

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
"""

import json
from pathlib import Path
from typing import Annotated, Callable

import typer
from pydantic.json_schema import GenerateJsonSchema

from .._paths import DOCS_DIR
from ..dec.models.v1 import SCHEMA_COMMENT_VERSION as DEC_SCHEMA_COMMENT_VERSION
from ..dec.models.v1.document import DecDocument
from ..feat.models.v1 import SCHEMA_COMMENT_VERSION as FEAT_SCHEMA_COMMENT_VERSION
from ..feat.models.v1.document import FeatDocument
from ..gol.models.v1 import SCHEMA_COMMENT_VERSION as GOL_SCHEMA_COMMENT_VERSION
from ..gol.models.v1.document import GolDocument
from ..prb.models.v1 import SCHEMA_COMMENT_VERSION as PRB_SCHEMA_COMMENT_VERSION
from ..prb.models.v1.document import PrbDocument
from ..qa.models.v2 import SCHEMA_COMMENT_VERSION as QA_SCHEMA_COMMENT_VERSION
from ..qa.models.v2.document import QaDocument
from ..req.models.v1 import SCHEMA_COMMENT_VERSION as REQ_SCHEMA_COMMENT_VERSION
from ..req.models.v1.document import ReqDocument
from ..rsk.models.v1 import SCHEMA_COMMENT_VERSION as RSK_SCHEMA_COMMENT_VERSION
from ..rsk.models.v1.document import RskDocument
from ..tsk.models.v1 import SCHEMA_COMMENT_VERSION as TSK_SCHEMA_COMMENT_VERSION
from ..tsk.models.v1.document import TskDocument
from ..uc.models.v2 import SCHEMA_COMMENT_VERSION as UC_SCHEMA_COMMENT_VERSION
from ..uc.models.v2.document import UcDocument
from ..vcr.models.v1 import SCHEMA_COMMENT_VERSION as VCR_SCHEMA_COMMENT_VERSION
from ..vcr.models.v1.document import VcrDocument

_DEFAULT_OUTPUT_DIR = DOCS_DIR


def generate_req_schema() -> str:
    """Generate REQ's JSON Schema (2020-12 dialect) from ``ReqDocument.model_json_schema()``.

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
    """
    schema_dict = ReqDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = REQ_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_qa_schema() -> str:
    """Generate QA's JSON Schema (2020-12 dialect) from ``QaDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``qa.models.v2``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``qa.models.v2.SCHEMA_COMMENT_VERSION``
    (currently ``"v2"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = QaDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = QA_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_uc_schema() -> str:
    """Generate UC's JSON Schema (2020-12 dialect) from ``UcDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``uc.models.v2``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``uc.models.v2.SCHEMA_COMMENT_VERSION``
    (currently ``"v2"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = UcDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = UC_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_tsk_schema() -> str:
    """Generate TSK's JSON Schema (2020-12 dialect) from ``TskDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``tsk.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``tsk.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = TskDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = TSK_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_prb_schema() -> str:
    """Generate PRB's JSON Schema (2020-12 dialect) from ``PrbDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``prb.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``prb.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = PrbDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = PRB_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_gol_schema() -> str:
    """Generate GOL's JSON Schema (2020-12 dialect) from ``GolDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``gol.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``gol.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = GolDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = GOL_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_rsk_schema() -> str:
    """Generate RSK's JSON Schema (2020-12 dialect) from ``RskDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``rsk.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``rsk.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = RskDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = RSK_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_dec_schema() -> str:
    """Generate DEC's JSON Schema (2020-12 dialect) from ``DecDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``dec.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``dec.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = DecDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = DEC_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_feat_schema() -> str:
    """Generate FEAT's JSON Schema (2020-12 dialect) from ``FeatDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``feat.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``feat.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = FeatDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = FEAT_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


def generate_vcr_schema() -> str:
    """Generate VCR's JSON Schema (2020-12 dialect) from ``VcrDocument.model_json_schema()``.

    Mirrors :func:`generate_req_schema` exactly, but for ``vcr.models.v1``:
    the ``"$schema"`` key is injected the same way (Pydantic v2 omits it by
    default), and ``"$comment"`` holds ``vcr.models.v1.SCHEMA_COMMENT_VERSION``
    (currently ``"v1"``) instead of REQ's own version token.

    Serializes with ``indent=2, sort_keys=True`` plus a trailing newline, for
    the same byte-identical-output/drift-detection reason as
    :func:`generate_req_schema`.
    """
    schema_dict = VcrDocument.model_json_schema()
    schema_dict["$schema"] = GenerateJsonSchema.schema_dialect
    schema_dict["$comment"] = VCR_SCHEMA_COMMENT_VERSION
    return json.dumps(schema_dict, indent=2, sort_keys=True) + "\n"


#: Registry mapping a doc-type name (as accepted by ``--type``) to its
#: ``generate_x() -> str`` function. Add an entry here when a new document
#: type's schema generator is implemented (e.g. ``"adr"``).
_GENERATORS: dict[str, Callable[[], str]] = {
    "dec": generate_dec_schema,
    "feat": generate_feat_schema,
    "gol": generate_gol_schema,
    "prb": generate_prb_schema,
    "qa": generate_qa_schema,
    "req": generate_req_schema,
    "rsk": generate_rsk_schema,
    "tsk": generate_tsk_schema,
    "uc": generate_uc_schema,
    "vcr": generate_vcr_schema,
}


def schema(
    type_: Annotated[
        str | None,
        typer.Option(
            "--type",
            help=f"Restrict generation to one registered doc type ({', '.join(sorted(_GENERATORS))}). "
            "Omit to generate all registered types.",
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output-dir",
            help="Directory to write '{type}_schema.json' files into (default: docs/).",
        ),
    ] = _DEFAULT_OUTPUT_DIR,
) -> None:
    """Generate JSON Schema (2020-12) for one or all registered document types.

    Writes ``{output_dir}/{type}_schema.json`` for each selected type
    (``--type``, or every registered type if omitted). Exits with status 1
    if any written file's content differs from what was already on disk
    (including the file not existing yet), so CI can rely on this command's
    own exit code instead of a separate ``git diff --exit-code`` step. The
    file is written regardless of drift, so a local run always leaves
    ``docs/`` up to date to commit.
    """
    if type_ is not None and type_ not in _GENERATORS:
        valid = ", ".join(sorted(_GENERATORS))
        typer.echo(f"Unknown --type {type_!r}; must be one of: {valid}")
        raise typer.Exit(1)

    selected = {type_: _GENERATORS[type_]} if type_ is not None else dict(_GENERATORS)

    output_dir.mkdir(parents=True, exist_ok=True)

    changed = False
    for name, generate in selected.items():
        output_path = output_dir / f"{name}_schema.json"
        new_content = generate()
        old_content = output_path.read_text(encoding="utf-8") if output_path.exists() else None

        output_path.write_text(new_content, encoding="utf-8")

        if old_content != new_content:
            changed = True
            typer.echo(f"✓ Wrote {output_path} (changed)")
        else:
            typer.echo(f"✓ Wrote {output_path} (unchanged)")

    if changed:
        raise typer.Exit(1)
