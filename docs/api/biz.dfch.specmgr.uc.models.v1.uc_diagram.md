# `biz.dfch.specmgr.uc.models.v1.uc_diagram`

Render a :class:`UseCase` into a PlantUML Use Case diagram (feature plan Task 2.1).

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

## Functions

### `_actor_declaration(name: 'str', alias: 'str') -> 'str'`


### `_actor_label(text: 'str') -> 'str'`

Derive a clean PlantUML actor label from free-text actor description (module docstring).


### `_actor_names(use_case: 'UseCase') -> 'list[str]'`

Distinct actor labels, primary first, then secondary in document order, no duplicates.


### `_usecase_declaration(title: 'str', alias: 'str') -> 'str'`


### `render_uc_diagram(use_case: 'UseCase') -> 'str'`

Render a single :class:`UseCase` into a complete PlantUML Use Case diagram.

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

