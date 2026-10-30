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

"""Tests for the generic tools' write-side ``language`` guard (feat-197-i18n Phase 120, ADR 38efdb66 items 2/6/10).

Pins the permanent/temporary rejection matrix: the generic ``update``/
``edit``/``set_status``/``set_classification``/``delete`` tools gained an
optional ``language`` parameter that only the pilot domain ``dec`` honors in
Phase 120; every other type (and ``feat``/``adr`` permanently) rejects a
non-default ``language`` with an actionable ``ValueError`` before any
filesystem access, while an omitted/``"en"`` language dispatches exactly as
before (ACC-013 for the write tools, ACC-002/ACC-015 surface checks,
REQ-013 surface check).
"""

from __future__ import annotations

import importlib
import inspect
import unittest
from collections.abc import Callable
from typing import Any
from unittest import mock

from biz.dfch.specmgr.adr.tools.get_adr import get_adr
from biz.dfch.specmgr.adr.tools.list_adr import list_adr
from biz.dfch.specmgr.feat.tools.create_feat import create_feat
from biz.dfch.specmgr.feat.tools.get_feat import get_feat
from biz.dfch.specmgr.feat.tools.list_feat import list_feat
from biz.dfch.specmgr.feat.tools.set_feat_id import set_feat_id
from biz.dfch.specmgr.general.tools._domains import ADR, ALL_DOMAINS, FEAT, WHOLE_BODY_DOMAINS
from biz.dfch.specmgr.general.tools._language_guard import LANGUAGE_AWARE_DOMAINS, guard_language
from biz.dfch.specmgr.general.tools.delete import delete
from biz.dfch.specmgr.general.tools.edit import edit
from biz.dfch.specmgr.general.tools.find_related import find_related
from biz.dfch.specmgr.general.tools.find_similar_text import find_similar_text
from biz.dfch.specmgr.general.tools.get_reference_diagram import get_reference_diagram
from biz.dfch.specmgr.general.tools.get_reference_diagram_all import get_reference_diagram_all
from biz.dfch.specmgr.general.tools.list_references import list_references
from biz.dfch.specmgr.general.tools.set_classification import set_classification
from biz.dfch.specmgr.general.tools.set_status import set_status
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.general.tools.validate import validate

#: ``general.tools``'s package ``__init__`` re-exports each tool *function* under its module's own name, so
#: ``from ...tools import update`` yields the function -- the modules (which own ``_ADAPTERS``) are imported
#: by dotted path instead.
delete_module = importlib.import_module("biz.dfch.specmgr.general.tools.delete")
edit_module = importlib.import_module("biz.dfch.specmgr.general.tools.edit")
set_classification_module = importlib.import_module("biz.dfch.specmgr.general.tools.set_classification")
set_status_module = importlib.import_module("biz.dfch.specmgr.general.tools.set_status")
update_module = importlib.import_module("biz.dfch.specmgr.general.tools.update")

_UUID = "00000000-0000-0000-0000-000000000000"
_FEAT_ID = "feat-1-slug"

#: The (tool name, tool function, module owning ``_ADAPTERS``, the types the tool accepts, a call
#: factory binding (type, id, language-kwargs)) per generic write tool.
_TOOLS: list[tuple[str, Callable[..., Any], Any, tuple[str, ...], Callable[..., Callable[[], Any]]]] = [
    (
        "update",
        update,
        update_module,
        WHOLE_BODY_DOMAINS,
        lambda t, i, **kw: lambda: update(id=i, type=t, content="# T\n", **kw),
    ),
    (
        "edit",
        edit,
        edit_module,
        WHOLE_BODY_DOMAINS,
        lambda t, i, **kw: lambda: edit(id=i, type=t, old_str="a", new_str="b", **kw),
    ),
    (
        "set_status",
        set_status,
        set_status_module,
        ALL_DOMAINS,
        lambda t, i, **kw: lambda: set_status(id=i, type=t, status=_status_for(t), **kw),
    ),
    (
        "set_classification",
        set_classification,
        set_classification_module,
        WHOLE_BODY_DOMAINS,
        lambda t, i, **kw: lambda: set_classification(id=i, type=t, classification="x", **kw),
    ),
    (
        "delete",
        delete,
        delete_module,
        WHOLE_BODY_DOMAINS,
        lambda t, i, **kw: lambda: delete(id=i, type=t, **kw),
    ),
]


#: The positional arguments each tool's default-language dispatch passes to its adapter, given the document id.
_DEFAULT_ADAPTER_ARGS: dict[str, Callable[[str], tuple[Any, ...]]] = {
    "update": lambda i: (i, "# T\n", None, None),
    "edit": lambda i: (i, "a", "b", False),
    "set_status": lambda i: (i, None, None),
    "set_classification": lambda i: (i, "x"),
    "delete": lambda i: (i,),
}


def _status_for(type_: str) -> str:
    """A status inside ``type_``'s own closed vocabulary (so the InvalidStatusResult pre-check passes)."""
    result = sorted(set_status_module._ALLOWED_STATUSES_BY_TYPE[type_])[0]
    return result


def _id_for(type_: str) -> str:
    """A well-formed id for ``type_`` (so every guard before the language guard passes)."""
    result = _FEAT_ID if type_ == FEAT else _UUID
    return result


def _booby_trapped_adapters(types: tuple[str, ...]) -> dict[str, mock.Mock]:
    """A dispatch table whose every adapter fails the test if it is ever reached (== any filesystem access)."""
    result = {t: mock.Mock(side_effect=AssertionError(f"adapter for {t!r} must not run")) for t in types}
    return result


class TestGuardLanguage(unittest.TestCase):
    """Unit tests of ``guard_language`` itself."""

    def test_language_aware_domains_are_the_pilot_only_in_phase_120(self):
        """Phase 120 enables ``dec`` only (Phase 125 extends the set)."""
        self.assertEqual(LANGUAGE_AWARE_DOMAINS, ("dec",))

    def test_default_language_always_passes_for_every_type(self):
        """'en' is the byte-identical flat path for every type, feat and adr included."""
        for type_ in ALL_DOMAINS:
            with self.subTest(type=type_):
                guard_language(type_, "en")

    def test_dec_with_a_usable_language_passes(self):
        """A shape-valid language with a packaged table passes for dec."""
        guard_language("dec", "de")

    def test_dec_with_a_tableless_language_is_rejected(self):
        """A shape-valid language without a packaged heading-mapping table is the loader's actionable error."""
        with self.assertRaises(ValueError) as ctx:
            guard_language("dec", "fr")
        self.assertIn("no heading-mapping table", str(ctx.exception))

    def test_shape_guard_runs_for_every_type_including_rejected_ones(self):
        """The shape error wins over the support error: a malformed value is reported as malformed for any type."""
        for type_ in ALL_DOMAINS:
            for value in ("", "d", "DE", "../../etc", "de/x", "/abs", "de3"):
                with self.subTest(type=type_, value=value):
                    with self.assertRaises(ValueError) as ctx:
                        guard_language(type_, value)
                    self.assertIn(repr(value), str(ctx.exception))
                    self.assertIn("ISO 639-1-shaped", str(ctx.exception))

    def test_feat_and_adr_rejections_are_permanent_in_wording(self):
        """feat/adr: 'always English' wording, never 'not yet'."""
        for type_ in (FEAT, ADR):
            with self.subTest(type=type_):
                with self.assertRaises(ValueError) as ctx:
                    guard_language(type_, "de")
                message = str(ctx.exception)
                self.assertIn(f"{type_} documents are always English", message)
                self.assertNotIn("not yet", message)

    def test_other_domains_are_temporarily_rejected(self):
        """The ten not-yet-enabled domains: 'not yet supported' wording naming the type."""
        for type_ in WHOLE_BODY_DOMAINS:
            if type_ in LANGUAGE_AWARE_DOMAINS or type_ == FEAT:
                continue
            with self.subTest(type=type_):
                with self.assertRaises(ValueError) as ctx:
                    guard_language(type_, "de")
                message = str(ctx.exception)
                self.assertIn(f"language 'de' is not yet supported for type {type_!r}", message)
                self.assertNotIn("always English", message)


class TestGenericToolsRejectNonDefaultLanguageBeforeAnyFilesystemAccess(unittest.TestCase):
    """The permanent/temporary rejection matrix over every generic write tool (ACC-013, ACC-002, ACC-015)."""

    def test_non_dec_types_reject_a_non_default_language_with_the_right_wording(self):
        """For every tool x every non-dec type: a non-default language is a ValueError with the right wording,
        raised before any adapter (== any filesystem access) runs."""
        for name, _tool, module, types, make_call in _TOOLS:
            with mock.patch.object(module, "_ADAPTERS", _booby_trapped_adapters(types)):
                for type_ in types:
                    if type_ in LANGUAGE_AWARE_DOMAINS:
                        continue
                    with self.subTest(tool=name, type=type_):
                        with self.assertRaises(ValueError) as ctx:
                            make_call(type_, _id_for(type_), language="de")()
                        message = str(ctx.exception)
                        if type_ in (FEAT, ADR):
                            self.assertIn(f"{type_} documents are always English", message)
                        else:
                            self.assertIn(f"language 'de' is not yet supported for type {type_!r}", message)

    def test_bad_language_is_a_shape_error_for_every_tool_and_type(self):
        """ACC-013: a path-injection-shaped language is rejected for every tool x type before any adapter runs."""
        for name, _tool, module, types, make_call in _TOOLS:
            with mock.patch.object(module, "_ADAPTERS", _booby_trapped_adapters(types)):
                for type_ in types:
                    for value in ("../../etc", "de/x", "", "DE"):
                        with self.subTest(tool=name, type=type_, value=value):
                            with self.assertRaises(ValueError) as ctx:
                                make_call(type_, _id_for(type_), language=value)()
                            self.assertIn(repr(value), str(ctx.exception))

    def test_dec_with_a_tableless_language_is_rejected_by_every_tool(self):
        """A shape-valid, table-less language ('fr') is rejected for dec before any filesystem access."""
        for name, _tool, module, types, make_call in _TOOLS:
            with (
                mock.patch.object(module, "_ADAPTERS", _booby_trapped_adapters(types)),
                mock.patch.object(module, "_LANGUAGE_ADAPTERS", _booby_trapped_adapters(("dec",))),
            ):
                with self.subTest(tool=name):
                    with self.assertRaises(ValueError) as ctx:
                        make_call("dec", _UUID, language="fr")()
                    self.assertIn("no heading-mapping table", str(ctx.exception))

    def test_default_language_dispatches_exactly_as_before(self):
        """language omitted and language='en' both dispatch through ``_ADAPTERS`` with exactly the pre-i18n
        argument shape (no language argument leaks into the default path)."""
        for name, _tool, module, types, make_call in _TOOLS:
            for kwargs in ({}, {"language": "en"}):
                for type_ in types:
                    adapters = _booby_trapped_adapters(types)
                    adapters[type_] = mock.Mock(return_value=object())
                    with mock.patch.object(module, "_ADAPTERS", adapters):
                        with self.subTest(tool=name, type=type_, kwargs=kwargs):
                            try:
                                make_call(type_, _id_for(type_), **kwargs)()
                            except (AttributeError, TypeError):
                                # the tool may post-process the sentinel result (e.g. update assembles an
                                # UpdateResult); what is pinned here is the dispatch, asserted below
                                pass
                            expected = _DEFAULT_ADAPTER_ARGS[name](_id_for(type_))
                            if name == "set_status":
                                expected = (expected[0], _status_for(type_), None)
                            adapters[type_].assert_called_once_with(*expected)

    def test_dec_non_default_language_dispatches_to_the_language_adapter_with_the_language(self):
        """A non-default dec language goes through ``_LANGUAGE_ADAPTERS`` with the language as the last argument."""
        for name, _tool, module, types, make_call in _TOOLS:
            sentinel = object()
            language_adapters = {"dec": mock.Mock(return_value=sentinel)}
            with (
                mock.patch.object(module, "_ADAPTERS", _booby_trapped_adapters(types)),
                mock.patch.object(module, "_LANGUAGE_ADAPTERS", language_adapters),
            ):
                with self.subTest(tool=name):
                    try:
                        make_call("dec", _UUID, language="de")()
                    except Exception:  # pylint: disable=broad-except
                        pass
                    language_adapters["dec"].assert_called_once()
                    self.assertEqual(language_adapters["dec"].call_args.args[0], _UUID)
                    self.assertEqual(language_adapters["dec"].call_args.args[-1], "de")

    def test_every_tool_has_a_language_parameter_defaulting_to_en(self):
        """The signature of each generic write tool ends with ``language: str = 'en'``."""
        for name, tool, _module, _types, _make_call in _TOOLS:
            with self.subTest(tool=name):
                parameter = inspect.signature(tool).parameters["language"]
                self.assertEqual(parameter.default, "en")


class TestSurfacesThatMustStayLanguageFree(unittest.TestCase):
    """Surface checks: tools that must NOT gain a ``language`` parameter (ADR items 5/10, REQ-002/009/013)."""

    def test_validate_stays_en_only(self):
        """The generic disk-free validate tool takes no language parameter (ADR item 5)."""
        self.assertNotIn("language", inspect.signature(validate).parameters)

    def test_feat_and_adr_tool_surfaces_are_unchanged(self):
        """No feat/adr-specific tool gained a language parameter (ACC-002/ACC-015, Phase 150 extends this)."""
        for fn in (create_feat, get_feat, list_feat, set_feat_id, get_adr, list_adr):
            with self.subTest(tool=fn.__name__):
                self.assertNotIn("language", inspect.signature(fn).parameters)

    def test_similarity_and_reference_tools_stay_en_only(self):
        """find_related/find_similar_text/list_references/get_reference_diagram(_all) gained no language (REQ-013)."""
        for fn in (find_related, find_similar_text, list_references, get_reference_diagram, get_reference_diagram_all):
            with self.subTest(tool=fn.__name__):
                self.assertNotIn("language", inspect.signature(fn).parameters)


if __name__ == "__main__":
    unittest.main()
