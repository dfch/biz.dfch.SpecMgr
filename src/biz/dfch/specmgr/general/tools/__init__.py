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

"""MCP tool wrappers for general-purpose utilities (mirrors ``adr/tools/``'s shape).

``mdformat`` -- a markdown document formatter that preserves YAML frontmatter
blocks (for ADR/UC files) and formats only the body markdown. ``update`` --
the generic, cross-domain whole-body or line-range replace for the
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt; optional read-style body-line
``offset``/``limit`` coordinates -- ``offset`` = 1-based first line,
``limit`` = number of lines, omitted = through end of body, ``0`` = pure
insert, ``offset = N+1`` = the virtual end-of-body append position -- strict
validation, splice-then-validate-whole). ``set_status`` -- the generic,
cross-domain status change for all document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt/adr; ``superseded_by`` is
``adr``-only, composing the status as ``"superseded by {superseded_by}"``).
``set_classification`` -- the generic, cross-domain change of the free-text
``classification`` frontmatter field for the whole-body document
types (``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt;
``adr`` is not supported), bumping ``updated`` and leaving the body and
every other frontmatter field untouched; a blank/whitespace-only value
clears ``classification`` back to ``None``/absent.
``delete`` -- the
generic, cross-domain hard-delete for the whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt; ``adr`` is
not supported), resolving the document by ``id``, taking the domain's own
per-id lock, and removing it from disk (the single ``*.md`` file for the
flat domains, the entire ``<base>/<id>/`` folder for ``feat``),
returning the deleted path as a string. ``edit`` -- the generic,
cross-domain surgical, exact-match string replacement of an existing
document's frontmatter-stripped body for the whole-body document types
(``type`` is one of req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt; ``adr``
is not supported -- an explicit pre-dispatch ``ValueError``, a deliberate
divergence from ``update``'s inherited ``KeyError``): ``old_str`` must
match the on-disk body byte-exactly (no line-ending normalization, no
fuzzy/regex fallback) and be unique unless ``replace_all`` rewrites every
exact occurrence, then the *edited* body must still validate as a whole
document -- the 2-fold contract writes the document only if both stages
pass, nothing is written on any failure (an empty ``new_str`` is a pure
deletion, legal iff stage 2 validates) (feat-159-edit, GitHub issue #159).
``validate`` -- the generic,
cross-domain, disk-free/id-free dry-run content validator for the
whole-body document types (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt; ``adr`` is not supported,
``validate_adr`` remains its own standalone tool); unlike every other
generic tool here, it never raises for a content-validation failure --
it always returns ``{valid: bool, errors: list[{message: str}]}``, only
raising ``ValueError`` for a ``full``/content-shape mismatch or an
unsupported ``type`` (feat-81-83-validation, ADR
078bf395-0a5f-4afd-84f6-b7a2191a00e6).
``find_related`` -- find the documents most semantically related to an
existing document, given its ``type``/``id``, across every whole-body
domain (``adr`` excluded structurally), ranked by cosine similarity of
local sentence embeddings (the ``similarity`` extra), excluding the
source document itself (feat-134-related-artifact-similarity, ADR
750842b2-aca4-4649-ba0c-855ec8e1f505). ``find_similar_text`` -- find the
documents most semantically similar to a free-form ``query`` text (the
pre-creation dedup/discovery companion of ``find_related``). Both return
ranked ``{type, id, title, status, path, score}`` hit rows (an
unparseable candidate appears with ``id = None`` and the ``<failed to
parse>`` marker title/status), and both return the structured,
non-raising ``{available: false, reason, message}`` result whenever the
embedding feature is unavailable (``SPECMGR_SIMILARITY_DISABLED`` present
or the backend/model failed to load) -- the tools always register,
availability is decided at call time (REQ-003). ``list_references`` -- the
generic, cross-domain cross-reference listing tool (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt/adr): scans the source
document's frontmatter-stripped body for ``<TYPE> <id>`` references (the
shared reference-tag vocabulary in ``general.tools._references`` --
the UUID tags with a canonical uuid id, plus ``feat`` carrying the
full ``feat-NNN-slug`` id or the bare ``feat-NNN`` number), dedupes
repeated occurrences (first-occurrence order preserved), resolves each
unique reference to the referenced document in its own target domain, and
returns a paged ``PagedResult`` of one ``ReferenceRow`` per unique
reference (``type``/``id``/``title``/``path``, plus ``error`` for
references that could not be resolved -- the shared ``list_*`` paging
mechanism, ADR ec9f5262; feat-144-ref-artifact, the ``feat`` tag added
by feat-177-list-ref-feat). ``get_reference_diagram`` -- the
read-only, id-based reference-diagram tool (``type`` is one of
req/uc/tsk/qa/prb/gol/rsk/dec/sop/feat/vcr/sysrs/txt/adr): renders one source
document's reference neighbourhood as the deterministic PlantUML component
diagram of the frozen ``specmgr://reference-graph`` rulebook (one node per
artifact, a stereotype + colour per type, per-domain curly-brace component
groups, one label-free edge per unique reference, on-cycle edges red,
dangling targets top-level ``<<UNRESOLVED>>`` nodes) -- the guard order is
``validate_id`` + the
``depth`` 1..5 range check (both ``ValueError`` before any filesystem
access), a missing source raises the source domain's own ``XNotFoundError``,
and an existing-but-broken source returns the non-raising
``ParseFailureResult`` (feat-207-reference-graph, Phase 120).
``get_reference_diagram_all`` -- the read-only, registry-wide
reference-diagram tool: the same deterministic PlantUML component diagram
over every parseable document of all 14 domains (broken documents are
skipped -- the render never fails for content), with the
``include_feat`` switch and an optional ``title`` override
(feat-207-reference-graph, Phase 120).
``list_languages`` -- the read-only language-listing tool for one artifact (feat-197-i18n Phase 140, REQ-012,
ACC-008): given a ``type`` (one of the twelve i18n-eligible domains req/uc/tsk/qa/prb/gol/rsk/dec/sop/vcr/sysrs/txt;
``feat``/``adr`` are permanently English and rejected) and an ``id``, it returns the language codes the artifact
exists in -- ``"en"`` first when the EN source exists, then the other languages holding a variant, sorted by code --
with one entry per language (resolved path, ``parseable``, parse ``error``).
``check_translation_drift`` -- the read-only drift check between a translated variant (``language``) and its source
(``source_language``, default ``"en"``): one structured, non-raising result reports BOTH structural drift
(``missing``/``extra``/``reordered`` sections against the canonical schema, heading text mapped through the language's
heading table, free text of data-carrying headings ignored, an ``unparseable`` finding for a broken document) and
staleness (the source's ``updated`` strictly newer than the variant's) (feat-197-i18n Phase 140, REQ-014, ACC-009).
Neither tool writes, creates, or invalidates anything, and neither translates (translating is the
``translate_artifact`` prompt).
Import this package to register all general tools at once::

    from biz.dfch.specmgr.general import tools  # noqa: F401 (side-effects only)
"""

from .delete import delete
from .edit import edit
from .find_related import find_related
from .find_similar_text import find_similar_text
from .get_reference_diagram import get_reference_diagram
from .get_reference_diagram_all import get_reference_diagram_all
from .list_references import list_references
from .mdformat import mdformat
from .set_classification import set_classification
from .set_status import set_status
from .update import update
from .validate import validate

# The two read-only translation tools (feat-197-i18n Phase 140) are imported last, deliberately out of alphabetical
# order: their shared ``_language_variants`` helper imports every language-aware domain's own ``tools`` modules, so
# they must load only after ``delete`` (the first import above) has cascaded through the server's full domain list --
# importing them first re-enters ``_domains`` while it is still partially initialized (a circular import).
from .check_translation_drift import check_translation_drift  # isort: skip  # noqa: E402
from .list_languages import list_languages  # isort: skip  # noqa: E402

__all__ = [
    "check_translation_drift",
    "delete",
    "edit",
    "find_related",
    "find_similar_text",
    "get_reference_diagram",
    "get_reference_diagram_all",
    "list_languages",
    "list_references",
    "mdformat",
    "set_classification",
    "set_status",
    "update",
    "validate",
]
