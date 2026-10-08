# `biz.dfch.specmgr.plantuml.chain`

The strict first-set-wins validation chain + the frozen result model (rulebook §3).

Selection is strict and configuration-driven over **exactly three** env vars
(§3.1 — no defaults, no PATH discovery, no opt-in flags): the first of
``SPECMGR_PLANTUML_JAR`` → ``SPECMGR_PLANTUML_BIN`` → ``SPECMGR_PLANTUML_URL``
that is **set** is the *only* source used. **No fall-through on
misconfiguration** (the privacy invariant, ADR 7a626b12): a set-but-unavailable
JAR with a set public URL never contacts the public URL — a typo'd local
source must never silently send diagram content to plantuml.com. A
set-but-unavailable source is a **hard validation failure** (``source_state``
= ``misconfigured``/``unavailable``/``inconclusive``, ``reason`` + ``fix_hint``
naming the exact problem, no write, no other source, no network); only the
all-unset state degrades — to the structure-only floor
(``source_state="none"``, ``available=False``).

The chain always runs the structure checker first; on structure red the
parser is **never called** (no subprocess, no network — the frozen
short-circuit, §3.7) and the result carries the structure errors with
``valid=None``/``rendered=None``/``checked_by="structure"`` (``None`` means
"not run", never "run and failed").

The result model (§3.6) is a non-raising structured result — the ADR 519d1206
chain precedent: :func:`validate_plantuml` never raises for validation
content; it returns a :class:`PlantumlValidationResult` carrying the verdict.
Import-free and stdlib-only (ADR 7a626b12).

## Classes

### `PlantumlValidationResult`

The non-raising validation result (rulebook §3.6 — the frozen shape).

``None`` on ``valid``/``rendered`` means **"not run"** — never "run and
failed". On a structure-red short-circuit (§3.7) and on the all-unset
floor, ``checked_by`` is ``"structure"``, ``valid``/``rendered`` are
``None``, and ``source_state``/``available`` report the source situation
(``"none"`` + ``False`` when the source was never probed — all-unset, or
the short-circuit with or without a configured source; the ``reason``
text disambiguates the two).


### `SourceAvailability`

The selected source's canary state (the env-gate helper, rulebook §3.5).

Attributes:
    kind: ``"jar"``/``"bin"``/``"url"`` or ``None`` (all unset).
    value: the configured value (``None`` when all unset).
    available: the canary answered (``False`` for the all-unset floor and
        for every set-but-unavailable source).
    reason: why the source is not available (``None`` when available).
    fix_hint: the concrete fix (``None`` when available).


## Functions

### `clear_probe_caches() -> 'None'`

Drop every memoised canary probe (test hook — the session gate re-probes).

Clears both the jar/bin probe cache (:func:`backends.clear_probe_cache`)
and the URL probe cache (:func:`url.clear_probe_cache`), so a changed
environment is re-probed from scratch. Because FAILURE outcomes
(``misconfigured`` / ``unavailable``) are memoised for the process
lifetime exactly like successes (rulebook §3.5, operator note
2026-10-08), this hook is also the only mid-process remedy for a
stale failure in a long-lived process (e.g. a running MCP server) after
the configuration is fixed — otherwise the restart is. Never called
from ``src/``.


### `select_source(env: 'Mapping[str, str] | None' = None) -> 'tuple[str, str] | None'`

Select the validation source: first SET of JAR → BIN → URL wins (§3.2).

The returned ``(kind, value)`` is the **only** source the chain will ever
use — there is no fall-through to any other variable. A variable that is
present but empty is still *set* (it selects, and the probe then reports
it as misconfigured — strictness over convenience).

Parameters
----------
env:
    The environment mapping to read (defaults to ``os.environ``); the
    parameter exists so tests can pin the configuration without touching
    the process environment.

Returns
-------
tuple[str, str] | None
    ``(kind, value)`` for the first set variable, or ``None`` when all
    three are unset (the structure-only floor, §3.4).


### `source_availability(env: 'Mapping[str, str] | None' = None) -> 'SourceAvailability'`

Select the source and probe its canary (memoised per process).

The one entry point the test-suite env gate (:mod:`tests.conftest`) and
the later ``specmgr://config`` plantuml section build on: selection per
§3.2, then exactly one canary round-trip through the selected source
(memoised — a second call in the same process costs nothing). No
fall-through: only the selected source is ever probed.


### `validate_plantuml(text: 'str', env: 'Mapping[str, str] | None' = None) -> 'PlantumlValidationResult'`

Validate one diagram through the strict chain (rulebook §3).

Always: the structure check first (preflight mode when a source is
selected — the lenient set as warnings; standalone mode on the all-unset
floor — the lenient set promoted to errors). On structure red: the frozen
short-circuit (§3.7) — the parser is never called (no subprocess, no
network) and the result carries the structure errors with
``valid=None``/``rendered=None``/``checked_by="structure"``. On structure
green: the selected source's canary (memoised) gates the real check —
set-but-unavailable is a hard failure (``source_state`` + ``reason`` +
``fix_hint``, no write, no other source, no network); available runs the
authoritative check (+ render proof) and reports its verdict.

Never raises for validation content (the non-raising structured-result
precedent); configuration is read from ``env`` (default ``os.environ``).

