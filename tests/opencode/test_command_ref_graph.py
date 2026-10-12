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

"""feat-207-reference-graph Phase 140, Task 140.120: ACC-005 drift pin for the /ref-graph command.

The project OpenCode command ``.opencode/command/ref-graph.md`` (the
reference-graph counterpart of feat-152's ``/refs`` single-document command
and feat-185's ``/uc-diagram`` host surface) runs the deterministic
``specmgr diagram refs`` CLI — the scoped ``<type> <id>`` arity (plus
optional ``depth`` / ``--reverse`` / ``--no-feat``) or the literal ``all``
— reports the written path + the ``specmgr plantuml-check`` validation
verdict, and never edits, writes (beyond the CLI's own ``.puml``
artifact), or commits. These tests pin: the file's location; its
frontmatter (exactly the ``description`` key — **no** ``agent:`` field,
there is no dedicated subagent, the flow is the deterministic CLI itself —
naming ``$1`` and the CLI); and the body's load-bearing wording (both
usage lines, the rulebook URI read-first pointer, the report shape — the
written path + the check verdict — and the never-edit/write/commit
contract). All pins are mechanical string checks on the committed file;
none of them import from ``src/``, so the test guards the command wording,
not the CLI behavior.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_COMMAND_PATH = _REPO_ROOT / ".opencode" / "command" / "ref-graph.md"
_CLI_USAGE_SCOPED = "specmgr diagram refs <type> <id> [--depth N] [--reverse] [--no-feat]"
_CLI_USAGE_ALL = "specmgr diagram refs all"
_RULEBOOK_URI = "specmgr://reference-graph"
_VERDICT_TOOL = "specmgr plantuml-check"
_REPORT_PHRASES: tuple[str, ...] = ("Report the written path", "validation verdict")
_NEVER_PHRASES: tuple[str, ...] = ("Do not edit, write, or commit", "Never commit")


def _read_text(path: Path) -> str:
    """Read a committed host-artifact file verbatim (a missing file is a hard failure)."""
    assert path.is_file(), path
    result = path.read_text(encoding="utf-8")
    return result


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split the leading ``---`` YAML block from the body (simple line split, no yaml dependency)."""
    lines = text.splitlines()
    assert lines and lines[0] == "---", "command file must open with a --- frontmatter delimiter"
    closing = [index for index in range(1, len(lines)) if lines[index] == "---"]
    assert closing, "command file frontmatter has no closing --- delimiter"
    frontmatter: str = "\n".join(lines[1 : closing[0]])
    body: str = "\n".join(lines[closing[0] + 1 :])
    result: tuple[str, str] = (frontmatter, body)
    return result


def _parse_frontmatter(frontmatter: str) -> dict[str, str]:
    """Parse the single-line ``key: value`` frontmatter entries (no yaml dependency)."""
    result: dict[str, str] = {}
    for line in frontmatter.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.partition(":")
        assert separator, f"frontmatter line is not key: value: {line}"
        result[key.strip()] = value.strip()
    return result


def _normalize_whitespace(text: str) -> str:
    """Collapse every whitespace run to one space (the command files wrap at ~80 columns)."""
    result = re.sub(r"\s+", " ", text)
    return result


class TestCommandFileLocation(unittest.TestCase):
    """The command exists at its committed path."""

    def test_command_file_exists(self):
        self.assertTrue(_COMMAND_PATH.is_file())


class TestCommandFrontmatter(unittest.TestCase):
    """Exactly one frontmatter key (``description``, naming ``$1`` + the CLI);
    no ``agent:`` field (no dedicated subagent — the flow is the
    deterministic CLI itself, the ``uc-diagram`` command precedent)."""

    def test_frontmatter_carries_a_description_only(self):
        frontmatter, _ = _split_frontmatter(_read_text(_COMMAND_PATH))

        result = _parse_frontmatter(frontmatter)

        self.assertEqual(set(result), {"description"})
        self.assertIn("$1", result["description"])
        self.assertIn("specmgr diagram refs", result["description"])
        self.assertNotIn("agent", result)


class TestCommandBodyWording(unittest.TestCase):
    """The load-bearing wording: both usage lines, the rulebook read-first
    pointer, the report shape (written path + the check verdict), and the
    never-edit/write/commit contract (beyond the CLI's own ``.puml``
    artifact)."""

    def test_usage_lines_present(self):
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))

        self.assertIn(_CLI_USAGE_SCOPED, body)
        self.assertIn(_CLI_USAGE_ALL, body)
        self.assertIn(_RULEBOOK_URI, body)

    def test_report_shape_present(self):
        """The command reports the written path + the validation verdict
        (``specmgr plantuml-check`` over the written file)."""
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))

        normalized_body = _normalize_whitespace(body)

        for phrase in _REPORT_PHRASES:
            self.assertIn(phrase, normalized_body)
        self.assertIn(_VERDICT_TOOL, body)

    def test_never_edit_write_commit_contract_present(self):
        """The read-only-over-documents + never-commit contract is stated."""
        _, body = _split_frontmatter(_read_text(_COMMAND_PATH))

        normalized_body = _normalize_whitespace(body)

        for phrase in _NEVER_PHRASES:
            self.assertIn(phrase, normalized_body)


if __name__ == "__main__":
    unittest.main()
