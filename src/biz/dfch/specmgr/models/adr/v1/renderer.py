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

"""Render an :class:`Adr` back into the canonical on-disk ``.md`` text (plan §7, §10 item 2).

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
"""

from __future__ import annotations

import yaml

from .adr import Adr
from .body import AdrBody
from .frontmatter import AdrFrontmatter

__all__ = ["render_adr"]

#: ``AdrFrontmatter`` attribute name -> rendered YAML key, in the fixed
#: emission order (plan §3's table order, ``version`` last since it is a
#: specmgr-only extension appended after the MADR-defined keys).
_FRONTMATTER_KEYS: tuple[tuple[str, str], ...] = (
    ("status", "status"),
    ("date", "date"),
    ("decision_makers", "decision-makers"),
    ("consulted", "consulted"),
    ("informed", "informed"),
    ("version", "version"),
)


def render_adr(adr: Adr) -> str:
    """Render a full :class:`Adr` into canonical MADR-derived markdown text.

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
    """
    return _render_frontmatter(adr.frontmatter) + "\n" + _render_body(adr.body)


def _render_frontmatter(fm: AdrFrontmatter) -> str:
    data: dict[str, str] = {}
    for attr, yaml_key in _FRONTMATTER_KEYS:
        value = getattr(fm, attr)
        if value is None:
            continue
        data[yaml_key] = value
    dumped = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False).strip("\n")
    return f"---\n{dumped}\n---\n"


def _render_body(body: AdrBody) -> str:
    blocks = [f"# {body.title}", _section("Context and Problem Statement", body.context_and_problem_statement)]

    if body.decision_drivers is not None:
        blocks.append(_section("Decision Drivers", body.decision_drivers))

    blocks.append(_section("Considered Options", body.considered_options))
    blocks.append(_render_decision_outcome(body))

    if body.options:
        blocks.append(_render_pros_and_cons(body))

    if body.more_information is not None:
        blocks.append(_section("More Information", body.more_information))

    return "\n\n".join(blocks).strip() + "\n"


def _render_decision_outcome(body: AdrBody) -> str:
    parts = [_section("Decision Outcome", body.decision_outcome)]
    if body.consequences is not None:
        parts.append(_section("Consequences", body.consequences, level=3))
    if body.confirmation is not None:
        parts.append(_section("Confirmation", body.confirmation, level=3))
    return "\n\n".join(parts)


def _render_pros_and_cons(body: AdrBody) -> str:
    parts = ["## Pros and Cons of the Options"]
    parts.extend(_section(option.full_title, option.content, level=3) for option in body.options)
    return "\n\n".join(parts)


def _section(title: str, content: str, level: int = 2) -> str:
    heading = f"{'#' * level} {title}"
    if not content:
        return heading
    return f"{heading}\n\n{content}"
