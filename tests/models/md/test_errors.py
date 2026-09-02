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

"""feat-27-validation Task 3.1: unit tests for the shared tool-boundary error wrapper.

Complements the tool-layer tests in `tests/general/tools/test_error_context.py` (ACC-003,
Task 3.4) by exercising `wrap_tool_errors` directly, in isolation from any real domain tool:
each of the three REQ-006 channels (`AssertionError`, `pydantic.ValidationError`,
`yaml.YAMLError`), the `also_catch` extension point (ADR's `AdrParseError`), the `channel`
label, and the "any other exception passes through untouched" guarantee.
"""

from __future__ import annotations

import unittest

import yaml
import yaml.error
from pydantic import BaseModel, ValidationError

from biz.dfch.specmgr.models.md._errors import BODY_CHANNEL, FRONTMATTER_CHANNEL, wrap_tool_errors


class _DemoModel(BaseModel):
    """A minimal, domain-independent model fixture for triggering a real `ValidationError`."""

    status: str


class TestWrapToolErrorsAssertionError(unittest.TestCase):
    """`AssertionError` is re-raised as the exact same type, message prefixed with context."""

    def test_prepends_domain_and_tool_with_no_channel(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="parse_tsk"):
                raise AssertionError("text left over after processing all fields")

        self.assertEqual(str(ctx.exception), "tsk parse_tsk: text left over after processing all fields")

    def test_prepends_domain_tool_and_channel_when_given(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="create_tsk", channel=BODY_CHANNEL):
                raise AssertionError("some structural failure")

        self.assertEqual(str(ctx.exception), "tsk create_tsk (body): some structural failure")

    def test_preserves_the_exact_exception_type(self) -> None:
        with self.assertRaises(AssertionError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="create_tsk"):
                raise AssertionError("boom")

        self.assertIs(type(ctx.exception), AssertionError)

    def test_chains_the_original_exception(self) -> None:
        original = AssertionError("boom")
        with self.assertRaises(AssertionError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="create_tsk"):
                raise original

        self.assertIs(ctx.exception.__cause__, original)


class TestWrapToolErrorsValidationError(unittest.TestCase):
    """`pydantic.ValidationError` is re-raised as the exact same type, each per-field message
    prefixed with context, `loc`/`input` preserved."""

    def test_prepends_context_to_each_field_message(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            with wrap_tool_errors(domain="req", tool="set_status", channel=FRONTMATTER_CHANNEL):
                _DemoModel.model_validate({"status": 123})

        self.assertIn("req set_status (frontmatter):", str(ctx.exception))

    def test_preserves_the_exact_exception_type(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            with wrap_tool_errors(domain="req", tool="set_status"):
                _DemoModel.model_validate({"status": 123})

        self.assertIs(type(ctx.exception), ValidationError)

    def test_preserves_loc_and_input(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            with wrap_tool_errors(domain="req", tool="set_status"):
                _DemoModel.model_validate({"status": 123})

        detail = ctx.exception.errors()[0]
        self.assertEqual(detail["loc"], ("status",))
        self.assertEqual(detail["input"], 123)

    def test_no_pydantic_documentation_link_suffix(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            with wrap_tool_errors(domain="req", tool="set_status"):
                _DemoModel.model_validate({"status": 123})

        self.assertNotIn("https://errors.pydantic.dev", str(ctx.exception))


class TestWrapToolErrorsYamlError(unittest.TestCase):
    """`yaml.YAMLError` is re-raised as the exact same type, marks preserved, ``context``
    prefixed with the tool-boundary label (the first line of ``MarkedYAMLError.__str__``)."""

    def test_plain_yaml_error_message_is_prefixed(self) -> None:
        with self.assertRaises(yaml.YAMLError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="parse_tsk"):
                raise yaml.YAMLError("bad yaml")

        self.assertEqual(str(ctx.exception), "tsk parse_tsk: bad yaml")

    def test_marked_error_preserves_marks_and_prefixes_context(self) -> None:
        mark = yaml.error.Mark("the frontmatter block", 0, 4, 0, None, None)
        error = yaml.scanner.ScannerError(
            context="while scanning a simple key", context_mark=mark, problem="found character", problem_mark=mark
        )

        with self.assertRaises(yaml.YAMLError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="parse_tsk"):
                raise error

        result = ctx.exception
        self.assertIs(type(result), yaml.scanner.ScannerError)
        self.assertEqual(result.context, "tsk parse_tsk: while scanning a simple key")
        self.assertIs(result.context_mark, mark)
        self.assertIs(result.problem_mark, mark)
        self.assertEqual(result.problem, "found character")

    def test_marked_error_with_no_context_uses_label_as_context(self) -> None:
        mark = yaml.error.Mark("the frontmatter block", 0, 4, 0, None, None)
        error = yaml.scanner.ScannerError(context=None, context_mark=None, problem="found bad char", problem_mark=mark)

        with self.assertRaises(yaml.YAMLError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="parse_tsk"):
                raise error

        self.assertEqual(ctx.exception.context, "tsk parse_tsk")


class TestWrapToolErrorsAlsoCatch(unittest.TestCase):
    """The ``also_catch`` extension point treats extra exception types exactly like
    ``AssertionError`` -- message-only, same-type reconstruction (ADR's ``AdrParseError``)."""

    def test_also_catch_type_gets_the_same_prefix_treatment(self) -> None:
        class _CustomStructuralError(ValueError):
            pass

        with self.assertRaises(_CustomStructuralError) as ctx:
            with wrap_tool_errors(domain="adr", tool="validate_adr", also_catch=(_CustomStructuralError,)):
                raise _CustomStructuralError("duplicate heading Foo")

        self.assertEqual(str(ctx.exception), "adr validate_adr: duplicate heading Foo")
        self.assertIs(type(ctx.exception), _CustomStructuralError)

    def test_a_plain_valueerror_not_listed_in_also_catch_passes_through_untouched(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="update"):
                raise ValueError("begin and end must be given together")

        self.assertEqual(str(ctx.exception), "begin and end must be given together")


class TestWrapToolErrorsPassthrough(unittest.TestCase):
    """Any exception outside the three REQ-006 channels (and ``also_catch``) propagates
    completely untouched -- e.g. a domain's own ``*NotFoundError``."""

    def test_unrelated_exception_type_is_not_modified(self) -> None:
        class _SomeNotFoundError(LookupError):
            pass

        with self.assertRaises(_SomeNotFoundError) as ctx:
            with wrap_tool_errors(domain="tsk", tool="update"):
                raise _SomeNotFoundError("no such id")

        self.assertEqual(str(ctx.exception), "no such id")


if __name__ == "__main__":
    unittest.main()
