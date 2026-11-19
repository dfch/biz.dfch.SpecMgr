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

"""Code Mode MCP-invocation detection (feat-250, Phase 110 locked harness fix).

The pinned opencode image (2.2.5) exposes NO remote-MCP tools to the model
natively (verified in the p110-prove streams: zero native `tool_use` events
with an MCP-prefixed name, and a config-schema probe confirmed no
configuration yields one); the Structurizr MCP is reachable ONLY through
opencode's "Code Mode": `execute` tool calls whose JavaScript invokes
`tools.<server>.<tool>({ ... })`, the tools being discovered via the
`tools.opencode.list_mcp_resources()` catalog. This module is the
detection layer that recovers those invocations from an event stream, with
the locked conservative rules:

- a reference is the textual pattern `tools.<server>.<tool>(` where
  `<server>` and `<tool>` are identifier-shaped (`[A-Za-z0-9_-]+`);
  dynamic access (`tools.structurizr[tool](`) is NOT a reference -- it is
  unattributable and yields no entry (the conservative direction);
- family classification matches the referenced tool against the MCP
  families (parse/validate/inspect/export), so the hyphenated export
  tools (`export-plantuml`, `export-mermaid`, `export-c4plantuml`) count
  for the `export` family;
- the `dsl` input is extracted only when the call site passes a PLAIN
  INLINE LITERAL as the `dsl` property (a backtick template literal
  without backslashes and without `${...}` interpolation, or a
  single/double-quoted string without backslashes and without a raw
  newline); a variable reference, a shorthand property, a read, a wrapped
  value, or anything the scanner cannot parse unambiguously yields
  `None` (unattributable);
- a `validate`-family entry "answers OK" only when its `execute` block
  references EXACTLY ONE `tools.<server>.<tool>(` of any kind (no other
  MCP reference in the same block), the block's status is `completed`,
  and the block's output strips to the OK marker. A multi-call block, an
  error block, or a wrapped/object output never attributes OK -- an
  unattributable call can only fail to flip a gate, never pass one.

The module is pure and stdlib-only (regex + character scanning); it never
executes a block's JavaScript, and the masking pass it uses for reference
scanning preserves positions so call-site extraction runs on the raw code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .events import TOOL_STATUS_COMPLETED, VALIDATE_OK_MARKER

#: The host tool name whose `code` input carries Code Mode JavaScript
#: (the pinned opencode 2.2.5 image).
EXECUTE_TOOL_NAME = "execute"

#: The MCP tool families (the locked vocabulary of the normalized view).
FAMILY_PARSE = "parse"
FAMILY_VALIDATE = "validate"
FAMILY_INSPECT = "inspect"
FAMILY_EXPORT = "export"

#: Every MCP family, in classification order.
MCP_FAMILIES: tuple[str, ...] = (FAMILY_PARSE, FAMILY_VALIDATE, FAMILY_INSPECT, FAMILY_EXPORT)

#: The Code Mode reference pattern: `tools.<server>.<tool>(` with
#: identifier-shaped server and tool tokens. The lookahead keeps the
#: opening parenthesis addressable (`match.end()` is its index) for the
#: call-site `dsl` extraction.
MCP_REFERENCE_RE = re.compile(r"tools\.([A-Za-z0-9_-]+)\.([A-Za-z0-9_-]+)(?=\()")


@dataclass(frozen=True)
class McpReference:
    """One `tools.<server>.<tool>(` reference found in a Code Mode block.

    Attributes:
        server: The `<server>` token (e.g. `structurizr`).
        tool: The `<tool>` token exactly as referenced
            (e.g. `export-plantuml`).
        family: The MCP family the tool belongs to, or None for
            non-family tools (e.g. `opencode`'s own catalog tools).
        call_open: The index of the `(` following the tool name; the
            masked and raw code share positions, so it addresses both.
    """

    server: str
    tool: str
    family: str | None
    call_open: int


@dataclass(frozen=True)
class CodeModeEntry:
    """One normalized MCP invocation recovered from a Code Mode block.

    Attributes:
        server: The `<server>` token of the reference.
        tool: The `<tool>` token of the reference.
        family: The MCP family (always non-None; non-family references
            emit no entry).
        dsl: The DSL input text, or None when unattributable (the locked
            plain-inline-literal rule).
        ok: Whether this entry "answered OK" per the locked attribution
            rule (validate family only; False for every other family).
    """

    server: str
    tool: str
    family: str
    dsl: str | None
    ok: bool


def family_of_tool(tool: str) -> str | None:
    """Return the MCP family a referenced tool name belongs to, or None.

    Exact family names (`parse`, `validate`, `inspect`) and the
    hyphenated/underscored export tools (`export-plantuml`,
    `export-mermaid`, `export-c4plantuml` -> `export`) match; anything
    else (including other servers' tools) returns None.
    """
    for family in MCP_FAMILIES:
        if tool == family or tool.startswith(family + "-") or tool.startswith(family + "_"):
            return family
    result: str | None = None
    return result


# ---------------------------------------------------------------------------
# the string/comment scanner (shared by masking and value skipping)
# ---------------------------------------------------------------------------


def _skip_quoted(code: str, i: int) -> int:
    """Return the index past the quoted string at `i` (`'` or `"`).

    Escape-aware (a backslash skips the following character); a raw
    newline ends the scan early (an unterminated single-line string).
    Never raises.
    """
    quote = code[i]
    n = len(code)
    j = i + 1
    while j < n:
        c = code[j]
        if c == "\\":
            j += 2
            continue
        if c == quote:
            return j + 1
        if c == "\n":
            return j
        j += 1
    result = n
    return result


def _skip_template(code: str, i: int) -> int:
    """Return the index past the template literal at `i` (a backtick).

    Escape-aware; `${...}` interpolations are skipped whole (balanced
    braces, string-aware) so a nested backtick inside an interpolation
    cannot move the closing boundary. Never raises.
    """
    n = len(code)
    j = i + 1
    while j < n:
        c = code[j]
        if c == "\\":
            j += 2
            continue
        if c == "`":
            return j + 1
        if c == "$" and j + 1 < n and code[j + 1] == "{":
            j = _skip_braced(code, j + 1)
            continue
        j += 1
    result = n
    return result


def _skip_line_comment(code: str, i: int) -> int:
    """Return the index of the newline ending the line comment at `i`."""
    n = len(code)
    j = i
    while j < n and code[j] != "\n":
        j += 1
    result = j
    return result


def _skip_block_comment(code: str, i: int) -> int:
    """Return the index past the block comment at `i` (`/*` at i/i+1)."""
    n = len(code)
    j = i + 2
    while j + 1 < n and not (code[j] == "*" and code[j + 1] == "/"):
        j += 1
    result = j + 2 if j + 1 < n else n
    return result


def _skip_braced(code: str, i: int) -> int:
    """Return the index past the balanced `{...}` block starting at `i`.

    String/template/comment aware; used for `${...}` interpolations.
    Returns len(code) when the block is unbalanced. Never raises.
    """
    n = len(code)
    depth = 0
    j = i
    while j < n:
        c = code[j]
        if c in ("'", '"'):
            j = _skip_quoted(code, j)
            continue
        if c == "`":
            j = _skip_template(code, j)
            continue
        if c == "/" and j + 1 < n:
            if code[j + 1] == "/":
                j = _skip_line_comment(code, j)
                continue
            if code[j + 1] == "*":
                j = _skip_block_comment(code, j)
                continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    result = n
    return result


def _skip_balanced(code: str, i: int, open_ch: str, close_ch: str) -> int | None:
    """Return the index past the balanced bracket pair starting at `i`.

    String/template/comment aware; None when unbalanced.
    """
    n = len(code)
    depth = 0
    j = i
    while j < n:
        c = code[j]
        if c in ("'", '"'):
            j = _skip_quoted(code, j)
            continue
        if c == "`":
            j = _skip_template(code, j)
            continue
        if c == "/" and j + 1 < n:
            if code[j + 1] == "/":
                j = _skip_line_comment(code, j)
                continue
            if code[j + 1] == "*":
                j = _skip_block_comment(code, j)
                continue
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    result: int | None = None
    return result


# ---------------------------------------------------------------------------
# masking and reference scanning
# ---------------------------------------------------------------------------


def mask_strings_and_comments(code: str) -> str:
    """Blank string/template literals and comments (positions preserved).

    The result is exactly as long as `code`: every character inside a
    string literal, template literal (including `${...}` interpolations)
    or comment becomes a space, raw newlines are preserved, everything
    else is unchanged. Reference scanning runs on the masked text so a
    `tools.<server>.<tool>(` mention inside a string or comment never
    counts (the conservative direction).
    """
    out = list(code)
    n = len(code)

    def blank(a: int, b: int) -> None:
        for k in range(a, b):
            if code[k] != "\n":
                out[k] = " "

    j = 0
    while j < n:
        c = code[j]
        if c in ("'", '"'):
            end = _skip_quoted(code, j)
            blank(j, end)
            j = end
        elif c == "`":
            end = _skip_template(code, j)
            blank(j, end)
            j = end
        elif c == "/" and j + 1 < n and code[j + 1] == "/":
            end = _skip_line_comment(code, j)
            blank(j, end)
            j = end
        elif c == "/" and j + 1 < n and code[j + 1] == "*":
            end = _skip_block_comment(code, j)
            blank(j, end)
            j = end
        else:
            j += 1
    result = "".join(out)
    return result


def find_references(code: str) -> list[McpReference]:
    """Return every `tools.<server>.<tool>(` reference in a block, in text order.

    Scans the masked code (strings/comments blanked). Non-family tools
    are returned too: the OK-attribution rule needs the full reference
    count of the block.
    """
    masked = mask_strings_and_comments(code)
    result: list[McpReference] = []
    for match in MCP_REFERENCE_RE.finditer(masked):
        tool = match.group(2)
        result.append(
            McpReference(
                server=match.group(1),
                tool=tool,
                family=family_of_tool(tool),
                call_open=match.end(),
            )
        )
    return result


# ---------------------------------------------------------------------------
# the call-site dsl extraction (the locked plain-inline-literal rule)
# ---------------------------------------------------------------------------


def _skip_ws(code: str, i: int) -> int:
    """Return the index past the whitespace starting at `i`."""
    n = len(code)
    while i < n and code[i] in " \t\r\n":
        i += 1
    result = i
    return result


def _parse_key(code: str, i: int) -> tuple[str | None, int]:
    """Parse one object key at `i`, returning (key, index past the key).

    Accepts a bare identifier or a simple quoted string without
    backslash escapes; anything else (computed keys, escapes, a raw
    newline) yields (None, i) -- the call site is then unattributable.
    """
    n = len(code)
    c = code[i]
    if c.isalpha() or c in "_$":
        j = i
        while j < n and (code[j].isalnum() or code[j] in "_$"):
            j += 1
        return code[i:j], j
    if c in ("'", '"'):
        quote = c
        j = i + 1
        while j < n and code[j] != quote and code[j] != "\n":
            if code[j] == "\\":
                return None, i
            j += 1
        if j < n and code[j] == quote:
            return code[i + 1 : j], j + 1
        return None, i
    return None, i


def _parse_plain_literal(code: str, i: int) -> str | None:
    """Return the plain literal value at `i`, or None (the locked rule).

    A backtick template literal is accepted only without backslashes
    (escape ambiguity) and without `${...}` interpolation; a
    single/double-quoted string only without backslashes and without a
    raw newline (line continuation). The returned value is the literal
    content verbatim -- under these restrictions there is nothing to
    unescape. A non-literal value (a variable, a call, ...) yields None.
    """
    n = len(code)
    c = code[i]
    if c == "`":
        j = i + 1
        while j < n:
            cc = code[j]
            if cc == "\\" or cc == "`":
                break
            if cc == "$" and j + 1 < n and code[j + 1] == "{":
                return None
            j += 1
        if j < n and code[j] == "`":
            result = code[i + 1 : j]
            return result
        return None
    if c in ("'", '"'):
        j = i + 1
        while j < n:
            cc = code[j]
            if cc == "\\" or cc == "\n" or cc == c:
                break
            j += 1
        if j < n and code[j] == c:
            result = code[i + 1 : j]
            return result
        return None
    result: str | None = None
    return result


def _skip_value(code: str, i: int) -> int | None:
    """Skip one object property value starting at `i`.

    Returns the index past the value, or None when the value cannot be
    skipped unambiguously (the call site is then unattributable).
    """
    c = code[i]
    if c in ("'", '"'):
        return _skip_quoted(code, i)
    if c == "`":
        return _skip_template(code, i)
    if c in ("{", "[", "("):
        close = {"{": "}", "[": "]", "(": ")"}[c]
        return _skip_balanced(code, i, c, close)
    if c in ("}", "]", ")", ",", ";", ":"):
        result: int | None = None
        return result
    n = len(code)
    j = i
    while j < n and code[j] not in " \t\r\n,;})]:({":
        j += 1
    while j < n:
        if code[j] in " \t\r\n":
            j += 1
            continue
        if code[j] == "(":
            k = _skip_balanced(code, j, "(", ")")
            if k is None:
                return None
            j = k
            continue
        if code[j] == ".":
            j += 1
            while j < n and (code[j].isalnum() or code[j] in "_$"):
                j += 1
            continue
        break
    result = j
    return result


def extract_inline_dsl(code: str, call_open: int) -> str | None:
    """Extract the `dsl` argument of one Code Mode call site, or None.

    `call_open` indexes the `(` of the call (raw and masked code share
    positions). The argument must be an object literal carrying a
    top-level `dsl` property whose value is a plain inline literal (see
    `_parse_plain_literal`); a shorthand/variable reference, a wrapped
    value, or anything ambiguous yields None (unattributable -- the
    locked conservative rule).
    """
    n = len(code)
    i = _skip_ws(code, call_open + 1)
    if i >= n or code[i] != "{":
        return None
    i += 1
    while True:
        i = _skip_ws(code, i)
        if i >= n:
            return None
        c = code[i]
        if c == "}":
            return None
        key, i = _parse_key(code, i)
        if key is None:
            return None
        i = _skip_ws(code, i)
        if i >= n:
            return None
        c = code[i]
        if c == ":":
            i = _skip_ws(code, i + 1)
            if key == "dsl":
                return _parse_plain_literal(code, i)
            i = _skip_value(code, i)
            if i is None:
                return None
        elif c in ",}":
            # a shorthand property `{ dsl }`: a variable reference
            if key == "dsl":
                return None
            if c == "}":
                return None
        else:
            return None
        i = _skip_ws(code, i)
        if i >= n:
            return None
        if code[i] == ",":
            i += 1
            continue
        if code[i] == "}":
            return None
        return None


# ---------------------------------------------------------------------------
# the block analysis (one normalized entry per family reference)
# ---------------------------------------------------------------------------


def analyze_execute_block(code: str, status: str, output: str) -> list[CodeModeEntry]:
    """Recover the normalized MCP invocations of one terminal execute block.

    Emits one entry per MCP-family reference (in text order); the
    block's `status`/`output` are carried on every entry by the caller
    (a block's output is the value of the block's `return`, not of any
    single call inside it). The OK-attribution rule (locked) applies to
    a `validate`-family entry only when the block references exactly
    one `tools.<server>.<tool>(` of any kind overall, the status is
    `completed`, and the output strips to the OK marker; a multi-call
    block, an error block, or a wrapped/object output never attributes
    OK.
    """
    refs = find_references(code)
    if not refs:
        result: list[CodeModeEntry] = []
        return result
    block_ok = (
        len(refs) == 1
        and refs[0].family == FAMILY_VALIDATE
        and status == TOOL_STATUS_COMPLETED
        and output.strip() == VALIDATE_OK_MARKER
    )
    result = []
    for ref in refs:
        if ref.family is None:
            continue
        result.append(
            CodeModeEntry(
                server=ref.server,
                tool=ref.tool,
                family=ref.family,
                dsl=extract_inline_dsl(code, ref.call_open),
                ok=block_ok,
            )
        )
    return result
