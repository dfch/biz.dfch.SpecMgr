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

"""feat-27-validation Task 2.3: tests for both frontmatter error channels (Tasks 2.1/2.2).

Complements `test_validation_error_baseline.py`'s two pinned, exact-string frontmatter tests
with tests that probe the *mechanics* `models.md._frontmatter_parse` adds: the block-relative
-> document-relative line remap math (REQ-004) for `yaml.YAMLError`, the domain/field/line
context prepended to `pydantic.ValidationError` (Task 2.2), and cross-domain coverage beyond
`tsk` (`req`/`adr`) showing every domain parser applies the same enrichment uniformly.
"""

from __future__ import annotations

import unittest

import frontmatter
import yaml
from pydantic import BaseModel, ValidationError, field_validator

from biz.dfch.specmgr.models.adr.v1.parser import parse_adr
from biz.dfch.specmgr.models.md._frontmatter_parse import (
    enrich_frontmatter_validation_error,
    enrich_frontmatter_yaml_error,
    frontmatter_opening_line,
)
from biz.dfch.specmgr.req.models.v1.parser import parse_req
from biz.dfch.specmgr.tsk.models.v1.parser import parse_tsk


class _DemoFrontmatter(BaseModel):
    """A minimal, domain-independent frontmatter fixture for testing the enrichment helpers
    directly, without depending on any real document type's own schema."""

    status: str
    other: str = "x"

    @field_validator("status")
    @classmethod
    def _validate_status(cls, value: str) -> str:
        if value not in ("a", "b"):
            raise ValueError(f"status must be one of ['a', 'b'], got {value!r}")
        return value


# ---------------------------------------------------------------------------
# `frontmatter_opening_line` (the block-relative -> document-relative offset math)
# ---------------------------------------------------------------------------


class TestFrontmatterOpeningLine(unittest.TestCase):
    def test_no_leading_whitespace_returns_line_1(self) -> None:
        sut = frontmatter_opening_line
        result = sut("---\na: 1\n---\nbody\n")
        self.assertEqual(result, 1)

    def test_two_leading_blank_lines_shift_the_opening_line_by_two(self) -> None:
        sut = frontmatter_opening_line
        result = sut("\n\n---\na: 1\n---\nbody\n")
        self.assertEqual(result, 3)

    def test_leading_whitespace_only_line_counts_as_one_line(self) -> None:
        sut = frontmatter_opening_line
        result = sut("   \n---\na: 1\n---\nbody\n")
        self.assertEqual(result, 2)


# ---------------------------------------------------------------------------
# `enrich_frontmatter_yaml_error` (REQ-004/REQ-006, `yaml.YAMLError` channel)
# ---------------------------------------------------------------------------


class TestEnrichFrontmatterYamlError(unittest.TestCase):
    def test_names_the_frontmatter_block_instead_of_unicode_string(self) -> None:
        text = "---\nid: tsk-1\nstatus: [unterminated\n---\nbody\n"
        original = _malformed_yaml_error(text)

        sut = enrich_frontmatter_yaml_error
        result = sut(text, original)

        self.assertIsInstance(result, type(original))
        self.assertIn("the frontmatter block", str(result))
        self.assertNotIn("<unicode string>", str(result))

    def test_remaps_block_relative_lines_to_document_relative_ones_with_leading_blank_lines(
        self,
    ) -> None:
        # Two leading blank lines shift every document-relative line number by two versus the
        # block-relative ones PyYAML itself reports (both marks land on `status: [unterminated`
        # and the immediately following `---` line, document lines 5 and 6 respectively).
        text = "\n\n---\nid: tsk-1\nstatus: [unterminated\n---\nbody\n"
        original = _malformed_yaml_error(text)
        self.assertIn("line 3, column 9", str(original))
        self.assertIn("line 4, column 1", str(original))

        sut = enrich_frontmatter_yaml_error
        result = sut(text, original)

        self.assertIn("line 5, column 9", str(result))
        self.assertIn("line 6, column 1", str(result))

    def test_preserves_the_original_problem_and_context_detail(self) -> None:
        text = "---\nid: tsk-1\nstatus: [unterminated\n---\nbody\n"
        original = _malformed_yaml_error(text)

        sut = enrich_frontmatter_yaml_error
        result = sut(text, original)

        self.assertIn("while parsing a flow sequence", str(result))
        self.assertIn("did not find expected ',' or ']'", str(result))

    def test_a_plain_non_marked_yaml_error_is_returned_unchanged(self) -> None:
        original = yaml.YAMLError("a plain, unmarked error")

        sut = enrich_frontmatter_yaml_error
        result = sut("---\na: 1\n---\nbody\n", original)

        self.assertIs(result, original)


def _malformed_yaml_error(text: str) -> yaml.YAMLError:
    """Return the real `yaml.YAMLError` `frontmatter.loads(text)` raises for malformed YAML."""
    try:
        frontmatter.loads(text)  # type: ignore[union-attr]
    except yaml.YAMLError as error:
        return error
    raise AssertionError("expected frontmatter.loads to raise yaml.YAMLError")  # pragma: no cover


# ---------------------------------------------------------------------------
# `enrich_frontmatter_validation_error` (Task 2.2/REQ-006, `pydantic.ValidationError` channel)
# ---------------------------------------------------------------------------


class TestEnrichFrontmatterValidationError(unittest.TestCase):
    def test_names_the_domain_field_and_document_relative_line(self) -> None:
        text = "---\nother: y\nstatus: nope\n---\nbody\n"
        original = _validation_error({"status": "nope"})

        sut = enrich_frontmatter_validation_error
        result = sut(text, original, domain="demo")

        self.assertIsInstance(result, ValidationError)
        self.assertIn(
            "demo frontmatter block, field 'status' (document line 3): "
            "Value error, status must be one of ['a', 'b'], got 'nope'",
            str(result),
        )

    def test_omits_the_line_suffix_when_the_field_is_absent_from_the_frontmatter_text(
        self,
    ) -> None:
        text = "---\nother: y\n---\nbody\n"
        original = _validation_error({"other": "y"})  # `status` missing entirely

        sut = enrich_frontmatter_validation_error
        result = sut(text, original, domain="demo")

        self.assertIn("demo frontmatter block, field 'status':", str(result))
        self.assertNotIn("document line", str(result))

    def test_preserves_the_exact_exception_type(self) -> None:
        text = "---\nstatus: nope\n---\nbody\n"
        original = _validation_error({"status": "nope"})

        sut = enrich_frontmatter_validation_error
        result = sut(text, original, domain="demo")

        self.assertIsInstance(result, ValidationError)
        self.assertIs(type(result), type(original))


def _validation_error(metadata: dict[str, object]) -> ValidationError:
    """Return the real `pydantic.ValidationError` `_DemoFrontmatter.model_validate` raises."""
    try:
        _DemoFrontmatter.model_validate(metadata)
    except ValidationError as error:
        return error
    raise AssertionError("expected model_validate to raise pydantic.ValidationError")  # pragma: no cover


# ---------------------------------------------------------------------------
# Cross-domain coverage: `parse_tsk`/`parse_req`/`parse_adr` all apply the same enrichment
# uniformly (REQ-005's "applied uniformly across ... all twelve domains", frontmatter scope).
# ---------------------------------------------------------------------------

_TSK_BODY = """\
# Title

- [ ] item

## Recent Updates

### Entry

Some update text.
"""

_ADR_BODY = """\
# Title

## Context and Problem Statement

Some context.

## Considered Options

- Option 1

## Decision Outcome

Chose option 1.
"""


class TestCrossDomainFrontmatterErrorCoverage(unittest.TestCase):
    def test_parse_tsk_names_the_frontmatter_block_on_malformed_yaml(self) -> None:
        text = f"---\nid: tsk-1\nstatus: [unterminated\n---\n{_TSK_BODY}"

        with self.assertRaises(yaml.YAMLError) as ctx:
            parse_tsk(text)

        self.assertIn("the frontmatter block", str(ctx.exception))

    def test_parse_req_names_the_domain_on_an_out_of_vocabulary_status(self) -> None:
        text = "---\nid: req-1\nstatus: not-a-real-status\n---\n# Title\n\nbody\n"

        with self.assertRaises(ValidationError) as ctx:
            parse_req(text)

        self.assertIn("req frontmatter block, field 'status'", str(ctx.exception))

    def test_parse_adr_names_the_frontmatter_block_on_malformed_yaml(self) -> None:
        text = f"---\nid: adr-1\nstatus: [unterminated\n---\n{_ADR_BODY}"

        with self.assertRaises(yaml.YAMLError) as ctx:
            parse_adr(text)

        self.assertIn("the frontmatter block", str(ctx.exception))
        self.assertNotIn("<unicode string>", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
