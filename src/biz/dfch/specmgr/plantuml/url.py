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

"""The single-endpoint PlantUML URL protocol classifier (rulebook §5 — the frozen matrix).

One endpoint: ``GET {base}/svg/{enc}``, where ``{enc}`` is the PlantUML
**classic** payload from :mod:`~biz.dfch.specmgr.plantuml.encode`
(custom-base64, alphabet ``0-9A-Za-z-_``, of the raw-deflate stream — the
``SoWkI…`` form, no prefix; rulebook §5.1, amended 2026-10-04 — the legacy
``~1``/``~b``/``~h`` prefixed forms are not accepted by current 1.2026.8
deployments). Every call carries the named
:data:`URL_TIMEOUT_SECONDS` timeout; a timeout classifies as INCONCLUSIVE
(one retry, then source state) — never a hang.

Classification matrix (frozen, §5.2) — **signature-based** (the body markers,
never the body size, which drifts between server builds):

==================  =========================================================  ==================
HTTP status         Body                                                       Classification
==================  =========================================================  ==================
200                 real diagram SVG (no placeholder/crash markers)            VALID + RENDERED
200                 crash page (``…has crashed.`` + the embedded Java          INVALID (crash diagnostic)
                    exception trace — the recognised 1.2026.8 crash line)      — line-0 finding carries
                                                                               the crash exception class
400                 ``Welcome to PlantUML!`` placeholder                       SYNTAX INVALID
200                 ``Welcome to PlantUML!`` placeholder                       REQUEST ERROR
200                 ``…generated a bad URL`` explanatory                       ENCODE ERROR
anything else       —                                                          INCONCLUSIVE
==================  =========================================================  ==================

**An unrecognised response is never classified INVALID** — only the exact
``400 + placeholder`` combination and the recognised ``200 + crash page``
line are. A timeout (transport failure) also classifies INCONCLUSIVE.
INCONCLUSIVE ⇒ one retry ⇒ persistent ⇒ source state (the result carries
the §3.6 ``source_state`` vocabulary). Import-free and stdlib-only (ADR
7a626b12; ``urllib`` only — no third-party HTTP stack).
"""

from __future__ import annotations

import re
import socket
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass

from .backends import CRASH_FIX_HINT, ProbeResult, scan_crash
from .encode import encode_puml
from .structure import Finding

__all__ = [
    "BAD_URL_MARKER",
    "CLASS_CRASH",
    "CLASS_ENCODE_ERROR",
    "CLASS_INCONCLUSIVE",
    "CLASS_INVALID",
    "CLASS_REQUEST_ERROR",
    "CLASS_VALID",
    "PLACEHOLDER_MARKER",
    "URL_TIMEOUT_SECONDS",
    "UrlResponse",
    "UrlVerdict",
    "classify_response",
    "clear_probe_cache",
    "fetch_svg",
    "is_real_svg",
    "probe_url",
    "svg_url",
    "validate_url",
]

#: The named timeout on every HTTP call (rulebook §5.3). A timeout
#: classifies INCONCLUSIVE — never a hang.
URL_TIMEOUT_SECONDS = 30

#: The placeholder marker: both servers' "Welcome to PlantUML!" explanatory
#: page (the 400 syntax-error placeholder AND the 200 request-error
#: placeholder carry it — the status is what separates the two rows).
PLACEHOLDER_MARKER = b"Welcome to PlantUML!"

#: The public server's "…generated a bad URL" explanatory SVG marker
#: (our payload was rejected — should be impossible; client bug/transport).
BAD_URL_MARKER = b"generated a bad URL"

# --- the frozen classifications (§5.2) ---

CLASS_VALID = "valid"
CLASS_INVALID = "invalid"
#: The recognised 200 + crash-page line (rulebook §5.2, amended 2026-10-06):
#: PlantUML crashed server-side while rendering — INVALID with a crash
#: diagnostic (the line-0 finding carries the crash exception class; the
#: fix_hint names the known 1.2026.8 self-message/note-left shape bug and
#: points at §2.9's anchored notes). A recognised row, not an unrecognised
#: response: the never-INVALID preamble covers only the unrecognised cases.
CLASS_CRASH = "crash"
CLASS_REQUEST_ERROR = "request_error"
CLASS_ENCODE_ERROR = "encode_error"
CLASS_INCONCLUSIVE = "inconclusive"


@dataclass(frozen=True)
class UrlResponse:
    """One HTTP exchange with the ``/svg/`` endpoint.

    Attributes:
        status: the HTTP status code (``None`` = the transport failed
            before a response — timeout, DNS, connection refused).
        body: the response body bytes (empty on transport failure).
        transport_error: the transport failure text (``None`` on a
            response, whatever its status).
    """

    status: int | None
    body: bytes
    transport_error: str | None = None


@dataclass(frozen=True)
class UrlVerdict:
    """The classified outcome of validating one diagram over the URL backend.

    Attributes:
        classification: one of the :data:`CLASS_*` constants.
        valid: ``True``/``False`` per the matrix; ``None`` = not a verdict
            (request error / encode error / persistent inconclusive) — never
            "run and failed" beyond the two INVALID rows (the 400+placeholder
            syntax row and the recognised 200+crash-page row).
        rendered: ``True`` when the valid case's body served as the render
            proof (written to a temp file); ``None`` otherwise.
        proof_path: the temp file holding the SVG body (valid case only).
        errors: the findings to surface (the invalid case carries one).
        source_state: ``"ok"`` or, for a persistent inconclusive,
            ``"inconclusive"`` — the §3.6 vocabulary.
        reason: a non-None explanation whenever ``valid`` is not ``True``.
        fix_hint: the concrete fix for the user.
    """

    classification: str
    valid: bool | None
    rendered: bool | None = None
    proof_path: str | None = None
    errors: list[Finding] | None = None
    source_state: str = "ok"
    reason: str | None = None
    fix_hint: str | None = None


def svg_url(base_url: str, diagram: str) -> str:
    """Build the single endpoint URL: ``{base}/svg/{classic-enc}`` (rulebook §5.1)."""
    assert isinstance(base_url, str) and base_url.strip(), base_url
    assert isinstance(diagram, str), type(diagram)
    result = f"{base_url.rstrip('/')}/svg/{encode_puml(diagram)}"
    return result


def _http_error_fix_hint(base_url: str) -> str:
    return (
        f"check SPECMGR_PLANTUML_URL (currently {base_url!r}): the base URL must be reachable and carry "
        "the server's path prefix included (bare, e.g. 'http://localhost:8080', vs '/plantuml' — "
        "rulebook §3.1/§7.5)"
    )


def fetch_svg(url: str) -> UrlResponse:
    """One GET against the ``/svg/`` endpoint (named timeout; never raises).

    HTTP error statuses (4xx/5xx) are responses — their status and body come
    back populated. Transport failures (timeout, DNS, connection refused,
    malformed URL) return ``status=None`` with the failure text.
    """
    assert isinstance(url, str), type(url)
    try:
        with urllib.request.urlopen(url, timeout=URL_TIMEOUT_SECONDS) as response:
            return UrlResponse(status=response.status, body=response.read())
    except urllib.error.HTTPError as exc:
        return UrlResponse(status=exc.code, body=exc.read())
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError, ValueError) as exc:
        detail = getattr(exc, "reason", None) or exc
        return UrlResponse(status=None, body=b"", transport_error=f"{type(exc).__name__}: {detail}")


def is_real_svg(body: bytes) -> bool:
    """True when ``body`` is a real diagram SVG (the matrix's VALID signature).

    An SVG document with **no** placeholder or crash markers — the welcome
    page, the bad-URL explanatory page, and the crash page are SVGs too, and
    they carry their markers. (The crash page must not pass as a render:
    rulebook §5.2's crash line, amended 2026-10-06 — the 1.2026.8
    self-message/note-left shape bug answers 200 with a crash page, and the
    pre-amendment classifier accepted it as a real render.)
    """
    assert isinstance(body, bytes), type(body)
    return (
        body.lstrip().startswith(b"<svg")
        and PLACEHOLDER_MARKER not in body
        and BAD_URL_MARKER not in body
        and scan_crash(body) is None
    )


def classify_response(status: int | None, body: bytes) -> str:
    """Classify one (status, body) pair per the frozen §5.2 matrix.

    Pure and signature-based: an unrecognised combination — including every
    transport failure (``status is None``) — is INCONCLUSIVE, **never**
    INVALID. Only the two INVALID rows are: the exact 400 + placeholder
    combination (syntax) and the recognised 200 + crash-page combination
    (the §5.2 crash line, amended 2026-10-06).
    """
    if status is None:
        return CLASS_INCONCLUSIVE
    if status == 400 and PLACEHOLDER_MARKER in body:
        return CLASS_INVALID
    if status == 200 and scan_crash(body) is not None:
        return CLASS_CRASH
    if status == 200 and PLACEHOLDER_MARKER in body:
        return CLASS_REQUEST_ERROR
    if status == 200 and BAD_URL_MARKER in body:
        return CLASS_ENCODE_ERROR
    if status == 200 and is_real_svg(body):
        return CLASS_VALID
    return CLASS_INCONCLUSIVE


def _write_proof(svg_bytes: bytes) -> str:
    """Write the valid case's SVG body to a temp file (the render proof)."""
    handle = tempfile.NamedTemporaryFile(prefix="plantuml-proof-", suffix=".svg", delete=False)
    with handle:
        handle.write(svg_bytes)
    result = handle.name
    return result


def _inconclusive_reason(response: UrlResponse) -> tuple[str, str]:
    if response.transport_error is not None:
        reason = f"no HTTP response from the server (transport failure: {response.transport_error})"
    else:
        reason = (
            f"an unrecognised response (status {response.status}, {len(response.body)} bytes) — "
            "the frozen matrix classifies it INCONCLUSIVE, never INVALID"
        )
    fix_hint = (
        "retry later (transient), or check the deployment (status endpoint, proxy) — an unrecognised "
        "response is never INVALID (rulebook §5.2)"
    )
    return reason, fix_hint


def validate_url(base_url: str, diagram: str, *, write_proof: bool = True) -> UrlVerdict:
    """Validate one diagram over the URL backend (matrix + one INCONCLUSIVE retry).

    The valid case writes the SVG body to a temp file as the render proof
    (its path is reported, the bytes never inlined). A persistent
    INCONCLUSIVE (surviving exactly one retry) becomes the §3.6 source
    state on the verdict.
    """
    assert isinstance(base_url, str), type(base_url)
    assert isinstance(diagram, str), type(diagram)
    assert isinstance(write_proof, bool), type(write_proof)

    url = svg_url(base_url, diagram)
    response = fetch_svg(url)
    classification = classify_response(response.status, response.body)
    if classification == CLASS_INCONCLUSIVE:
        # one retry — the matrix's INCONCLUSIVE handling (rulebook §5.2)
        response = fetch_svg(url)
        classification = classify_response(response.status, response.body)

    if classification == CLASS_VALID:
        proof_path = _write_proof(response.body) if write_proof else None
        result = UrlVerdict(
            classification=CLASS_VALID,
            valid=True,
            rendered=True,
            proof_path=proof_path,
            errors=[],
        )
        return result
    if classification == CLASS_INVALID:
        result = UrlVerdict(
            classification=CLASS_INVALID,
            valid=False,
            errors=[
                Finding(
                    0,
                    "the PlantUML server rejected the diagram: syntax error (400 + the 'Welcome to "
                    "PlantUML!' placeholder)",
                    "fix the diagram's syntax; for the parser's line-level error text use a local "
                    "source (SPECMGR_PLANTUML_JAR/SPECMGR_PLANTUML_BIN, rulebook §4)",
                )
            ],
        )
        return result
    if classification == CLASS_CRASH:
        # the recognised §5.2 crash line (amended 2026-10-06): INVALID with a
        # crash diagnostic — the line-0 finding carries the crash exception
        # class, the fix_hint names the known 1.2026.8 shape bug and points
        # at §2.9's anchored notes (a crash is never "not a verdict")
        crash = scan_crash(response.body)
        assert crash is not None  # the classifier recognised the crash page
        result = UrlVerdict(
            classification=CLASS_CRASH,
            valid=False,
            errors=[
                Finding(
                    0,
                    f"the PlantUML server crashed while rendering the diagram: {crash} (200 + the crash page)",
                    CRASH_FIX_HINT,
                )
            ],
        )
        return result
    if classification == CLASS_REQUEST_ERROR:
        result = UrlVerdict(
            classification=CLASS_REQUEST_ERROR,
            valid=None,
            reason="the server returned the request-error placeholder (200 + 'Welcome to PlantUML!'): "
            "the payload exceeded the deployment's size limit, was undecodable, or no @startuml was "
            "extracted",
            fix_hint="shrink the diagram or raise the deployment's PLANTUML_LIMIT_SIZE (rulebook §5.4) — "
            "a request error is never INVALID; verify the base URL carries the server's path prefix "
            "(rulebook §3.1)",
        )
        return result
    if classification == CLASS_ENCODE_ERROR:
        result = UrlVerdict(
            classification=CLASS_ENCODE_ERROR,
            valid=None,
            reason="the server rejected our classic payload ('generated a bad URL') — should be impossible: "
            "a client/transport defect, not a diagram problem",
            fix_hint="re-run (transient), then report the specmgr client bug with the SPECMGR_PLANTUML_URL "
            "value — the payload encoding is verified offline by the encode round-trip tests",
        )
        return result
    # persistent INCONCLUSIVE — source state (rulebook §5.2's last row)
    reason, fix_hint = _inconclusive_reason(response)
    result = UrlVerdict(
        classification=CLASS_INCONCLUSIVE,
        valid=None,
        source_state="inconclusive",
        reason=reason,
        fix_hint=fix_hint,
    )
    return result


# --- the canary probe (memoised per process, rulebook §3.5) ----------------------

_URL_PROBE_CACHE: dict[str, ProbeResult] = {}

#: An HTTP 404 from the canary: the base URL's path prefix is the usual
#: suspect (bare vs ``/plantuml`` — rulebook §3.5's own example).
_HTTP_NOT_FOUND = 404
_BASE_URL_SHAPE_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://\S+$")


def clear_probe_cache() -> None:
    """Drop every memoised URL canary probe result (test hook — never called from src/)."""
    _URL_PROBE_CACHE.clear()


def probe_url(base_url: str) -> ProbeResult:
    """Probe a URL source with the canary (rulebook §3.5).

    Memoised per process per base URL. A malformed base URL (no
    ``scheme://``) is ``misconfigured`` without any network call; a reachable
    server whose canary does not classify VALID (including a 404 — the
    path-prefix diagnosis — and the request-error / bad-URL cases of a
    deployment that does not decode the classic payload) is ``unavailable``
    with the exact reason; a transport failure is ``unavailable`` (transient).
    """
    assert isinstance(base_url, str), type(base_url)
    if base_url in _URL_PROBE_CACHE:
        result = _URL_PROBE_CACHE[base_url]
        return result

    if not _BASE_URL_SHAPE_PATTERN.match(base_url.strip()):
        result = ProbeResult(
            ok=False,
            source_state="misconfigured",
            reason=f"SPECMGR_PLANTUML_URL is set but is not an absolute URL (scheme://host[/path]): {base_url!r}",
            fix_hint=_http_error_fix_hint(base_url),
        )
        _URL_PROBE_CACHE[base_url] = result
        return result

    from .backends import CANARY_DIAGRAM  # late import: backends never imports url

    base_url = base_url.strip()
    response = fetch_svg(svg_url(base_url, CANARY_DIAGRAM))
    classification = classify_response(response.status, response.body)
    if classification == CLASS_VALID:
        result = ProbeResult(ok=True, source_state="ok")
    elif response.status == _HTTP_NOT_FOUND:
        result = ProbeResult(
            ok=False,
            source_state="misconfigured",
            reason=f"the canary URL at {base_url!r} answered 404 (no such endpoint)",
            fix_hint="check the base URL path prefix (bare vs '/plantuml') — rulebook §3.5",
        )
    elif response.status is None:
        result = ProbeResult(
            ok=False,
            source_state="unavailable",
            reason=f"the canary round-trip through {base_url!r} failed: no HTTP response ({response.transport_error})",
            fix_hint=_http_error_fix_hint(base_url),
        )
    else:
        result = ProbeResult(
            ok=False,
            source_state="unavailable",
            reason=f"the canary round-trip through {base_url!r} was classified {classification!r} "
            f"(status {response.status}) — the server did not render a known-valid diagram",
            fix_hint="verify the deployment serves the /svg/ endpoint (rulebook §5.1) and decodes the "
            "classic payload (1.2026.8 deployments answered legacy prefixed canaries with the "
            "request-error placeholder / bad-URL explanatory); select a local source "
            "(SPECMGR_PLANTUML_JAR/SPECMGR_PLANTUML_BIN) in the meantime (rulebook §7.3)",
        )
    _URL_PROBE_CACHE[base_url] = result
    return result
