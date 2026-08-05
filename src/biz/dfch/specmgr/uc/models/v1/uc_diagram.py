"""Render a :class:`UseCase` into a PlantUML Use Case diagram (feature plan Task 2.1).

A pure function, no file I/O and no multi-document resolution -- mirrors
``models/adr/v1/renderer.py``'s "operate purely on the schema" style. Only ever parses/renders
one :class:`UseCase` at a time: sub-use-case mentions inside actor text or extension/sub-
variation content (e.g. ``"Take Payment by Credit Card (UC-044)"``) are rendered as plain text,
never resolved into their own separate diagram nodes -- there is no id->document listing/
resolution layer yet (that is Phase 3's ``uc_list`` resource / ``_paths.py``, deliberately not
built until then).

Produces exactly one ``usecase`` node (the document itself, labeled by its ``title``) and one
``actor`` node per distinct actor name derived from ``primary_actor``/``secondary_actors``, with
a plain association edge from each actor to the use case.

**Actor label extraction** (:func:`_actor_label`): actor fields are free descriptive text, not
already-clean names, e.g. ``"Credit card company (for payment processing)"``. The label is:

1. the contents of the first double-quoted substring, if the text contains one at all (e.g.
   ``Company refers to buyer as "Buyer" (any agent...)`` -> ``"Buyer"``), taking priority over
   any trailing parenthetical even when both are present;
2. otherwise, everything before the first ``" ("``, i.e. the parenthetical aside is dropped
   (e.g. ``"Credit card company (for payment processing)"`` -> ``"Credit card company"``);
3. otherwise (no quotes, no parenthetical), the text as-is, stripped.
"""

from __future__ import annotations

import re

from .use_case import UseCase

__all__ = ["render_uc_diagram"]

#: The first double-quoted substring in actor text, if any -- takes priority over a
#: trailing parenthetical when both are present.
_QUOTED_SUBSTRING_PATTERN = re.compile(r'"([^"]+)"')

#: A PlantUML alias must be a bare identifier; anything else needs to be quoted in the
#: generated diagram source. Reuse the label text itself as the alias when it already
#: qualifies, otherwise fall back to a generated ``actorN``/``usecase`` style alias.
_BARE_ALIAS_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def render_uc_diagram(use_case: UseCase) -> str:
    """Render a single :class:`UseCase` into a complete PlantUML Use Case diagram.

    Parameters
    ----------
    use_case:
        The structured document to render. Only its ``title``,
        ``characteristic_information.primary_actor``, and
        ``characteristic_information.secondary_actors`` are consulted.

    Returns
    -------
    str
        The complete PlantUML diagram source, from ``@startuml`` to ``@enduml``, ending with
        exactly one trailing newline.
    """
    usecase_alias = "uc"
    actor_names = _actor_names(use_case)

    lines = [f"@startuml {use_case.title}", ""]

    aliases: dict[str, str] = {}
    for index, name in enumerate(actor_names, start=1):
        alias = name if _BARE_ALIAS_PATTERN.match(name) else f"actor{index}"
        aliases[name] = alias
        lines.append(_actor_declaration(name, alias))

    lines.append(_usecase_declaration(use_case.title, usecase_alias))
    lines.append("")

    for name in actor_names:
        lines.append(f"{aliases[name]} --> {usecase_alias}")

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines).strip("\n") + "\n"


def _actor_names(use_case: UseCase) -> list[str]:
    """Distinct actor labels, primary first, then secondary in document order, no duplicates."""
    info = use_case.characteristic_information
    raw_names = [info.primary_actor, *(info.secondary_actors or [])]

    names: list[str] = []
    seen: set[str] = set()
    for raw in raw_names:
        label = _actor_label(raw)
        if label not in seen:
            seen.add(label)
            names.append(label)
    return names


def _actor_label(text: str) -> str:
    """Derive a clean PlantUML actor label from free-text actor description (module docstring)."""
    quoted = _QUOTED_SUBSTRING_PATTERN.search(text)
    if quoted is not None:
        return quoted.group(1).strip()

    paren_index = text.find(" (")
    if paren_index != -1:
        return text[:paren_index].strip()

    return text.strip()


def _actor_declaration(name: str, alias: str) -> str:
    if alias == name:
        return f"actor {name}"
    return f'actor "{name}" as {alias}'


def _usecase_declaration(title: str, alias: str) -> str:
    return f'usecase "{title}" as {alias}'
