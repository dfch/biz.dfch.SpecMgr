# `biz.dfch.specmgr.plantuml.url`

The single-endpoint PlantUML URL protocol classifier (rulebook §5 — the frozen matrix).

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
200                 real diagram SVG (no placeholder markers)                  VALID + RENDERED
400                 ``Welcome to PlantUML!`` placeholder                       SYNTAX INVALID
200                 ``Welcome to PlantUML!`` placeholder                       REQUEST ERROR
200                 ``…generated a bad URL`` explanatory                       ENCODE ERROR
anything else       —                                                          INCONCLUSIVE
==================  =========================================================  ==================

**An unrecognised response is never classified INVALID** — only the exact
``400 + placeholder`` combination is. A timeout (transport failure) also
classifies INCONCLUSIVE. INCONCLUSIVE ⇒ one retry ⇒ persistent ⇒ source
state (the result carries the §3.6 ``source_state`` vocabulary).
Import-free and stdlib-only (ADR 7a626b12; ``urllib`` only — no third-party
HTTP stack).

## Classes

### `UrlResponse`

One HTTP exchange with the ``/svg/`` endpoint.

Attributes:
    status: the HTTP status code (``None`` = the transport failed
        before a response — timeout, DNS, connection refused).
    body: the response body bytes (empty on transport failure).
    transport_error: the transport failure text (``None`` on a
        response, whatever its status).


### `UrlVerdict`

The classified outcome of validating one diagram over the URL backend.

Attributes:
    classification: one of the :data:`CLASS_*` constants.
    valid: ``True``/``False`` per the matrix; ``None`` = not a verdict
        (request error / encode error / persistent inconclusive) — never
        "run and failed" beyond the exact 400+placeholder row.
    rendered: ``True`` when the valid case's body served as the render
        proof (written to a temp file); ``None`` otherwise.
    proof_path: the temp file holding the SVG body (valid case only).
    errors: the findings to surface (the invalid case carries one).
    source_state: ``"ok"`` or, for a persistent inconclusive,
        ``"inconclusive"`` — the §3.6 vocabulary.
    reason: a non-None explanation whenever ``valid`` is not ``True``.
    fix_hint: the concrete fix for the user.


## Functions

### `_http_error_fix_hint(base_url: 'str') -> 'str'`


### `_inconclusive_reason(response: 'UrlResponse') -> 'tuple[str, str]'`


### `_write_proof(svg_bytes: 'bytes') -> 'str'`

Write the valid case's SVG body to a temp file (the render proof).


### `classify_response(status: 'int | None', body: 'bytes') -> 'str'`

Classify one (status, body) pair per the frozen §5.2 matrix.

Pure and signature-based: an unrecognised combination — including every
transport failure (``status is None``) — is INCONCLUSIVE, **never**
INVALID. Only the exact 400 + placeholder combination is INVALID.


### `clear_probe_cache() -> 'None'`

Drop every memoised URL canary probe result (test hook — never called from src/).


### `fetch_svg(url: 'str') -> 'UrlResponse'`

One GET against the ``/svg/`` endpoint (named timeout; never raises).

HTTP error statuses (4xx/5xx) are responses — their status and body come
back populated. Transport failures (timeout, DNS, connection refused,
malformed URL) return ``status=None`` with the failure text.


### `is_real_svg(body: 'bytes') -> 'bool'`

True when ``body`` is a real diagram SVG (the matrix's VALID signature).

An SVG document with **no** placeholder markers — the welcome page and
the bad-URL explanatory page are SVGs too, and they carry their markers.


### `probe_url(base_url: 'str') -> 'ProbeResult'`

Probe a URL source with the canary (rulebook §3.5).

Memoised per process per base URL. A malformed base URL (no
``scheme://``) is ``misconfigured`` without any network call; a reachable
server whose canary does not classify VALID (including a 404 — the
path-prefix diagnosis — and the request-error / bad-URL cases of a
deployment that does not decode the classic payload) is ``unavailable``
with the exact reason; a transport failure is ``unavailable`` (transient).


### `svg_url(base_url: 'str', diagram: 'str') -> 'str'`

Build the single endpoint URL: ``{base}/svg/{classic-enc}`` (rulebook §5.1).


### `validate_url(base_url: 'str', diagram: 'str', *, write_proof: 'bool' = True) -> 'UrlVerdict'`

Validate one diagram over the URL backend (matrix + one INCONCLUSIVE retry).

The valid case writes the SVG body to a temp file as the render proof
(its path is reported, the bytes never inlined). A persistent
INCONCLUSIVE (surviving exactly one retry) becomes the §3.6 source
state on the verdict.

