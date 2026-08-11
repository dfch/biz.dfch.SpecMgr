# `biz.dfch.specmgr.commands.unused_code`

``unused-code`` -- report unreferenced Python symbols, or (with ``--test``) test-only ones.

Thin, friendlier wrapper around ``vulture`` with two modes:

* **Default** -- scans ``--src`` (plus ``--whitelist``, if it exists) and reports every
  unreferenced symbol vulture finds, exactly like the enforced pre-commit hook/CI step
  (``uv run --frozen vulture src/ whitelist.py --min-confidence 60``), just without having to
  remember that invocation.
* **``--test``/``-t``** -- reports symbols vulture only considers "used" because the test suite
  references them, never production code itself. Vulture treats any reference to a name across
  every path it scans as "used", regardless of whether that reference lives in production code
  or in the test suite; this mode exploits that by scanning twice and diffing the two finding
  sets:

  1. Scan ``--src`` alone -- anything reported is either genuinely unreferenced, or only ever
     called from ``--tests``.
  2. Scan ``--src`` together with ``--tests`` -- names exercised exclusively by tests now count
     as "used" and drop out of the findings.

  Names present in (1) but not (2) are referenced exclusively from test code, never from
  production code itself -- a lead worth a manual look, since it may indicate an orphaned public
  surface, or may simply be a Pydantic field/public API that is legitimately exercised only from
  tests so far. This is a name-based heuristic, the same as vulture itself: matching is by
  symbol name, not by definition site, so a hit still needs a manual ``grep`` to confirm which
  definition it actually refers to before concluding anything should change.

See the "Detect unreferenced code with vulture" ADR for the full rationale and ``whitelist.py``
for the enforced-in-CI counterpart of the default mode.

Requires the ``test`` extra (``pip install biz-dfch-specmgr[test]``), since ``vulture`` is only
declared as a dependency there.

## Functions

### `_report_test_only_usage(vulture_cls: type, src: pathlib.Path, tests: pathlib.Path, min_confidence: int) -> bool`

Print symbol names referenced only from `tests`, never from `src` itself.

Returns:
    True if any findings were reported, False if none were found.


### `_report_unused_code(vulture_cls: type, src: pathlib.Path, whitelist: pathlib.Path, min_confidence: int) -> bool`

Print every unreferenced symbol vulture finds in `src` (plus `whitelist`, if present).

Returns:
    True if any findings were reported, False on a clean scan.


### `_scan(vulture_cls: type, paths: list[pathlib.Path], min_confidence: int) -> list`

Scan `paths` together with a fresh `Vulture` instance, returning the reported `Item`s.

Args:
    vulture_cls: The `vulture.Vulture` class, injected so the optional `vulture` import
        only has to be attempted once, by the caller.
    paths: Directories/files scanned together in a single pass -- a reference to a name in
        any one path counts as "used" for a definition in another.
    min_confidence: Vulture confidence threshold (0-100); lower reports more findings, with
        more noise.

Returns:
    The `vulture.core.Item` objects vulture reports, in vulture's own order.


### `_unused_names(vulture_cls: type, paths: list[pathlib.Path], min_confidence: int) -> set[str]`

Return just the reported symbol names from `_scan()`.

Deliberately just names, not full `Item` objects -- vulture itself matches by name, not by
definition site, so a name can be reported once even if several unrelated definitions share
it. Used by `--test` mode, which relies on exactly that name-based comparison.


### `unused_code(src: Annotated[pathlib.Path, <typer.models.OptionInfo object>] = PosixPath('/src'), tests: Annotated[pathlib.Path, <typer.models.OptionInfo object>] = PosixPath('/tests'), whitelist: Annotated[pathlib.Path, <typer.models.OptionInfo object>] = PosixPath('/whitelist.py'), min_confidence: Annotated[int, <typer.models.OptionInfo object>] = 60, test_only: Annotated[bool, <typer.models.OptionInfo object>] = False, strict: Annotated[bool, <typer.models.OptionInfo object>] = False) -> None`

Report unused code (or, with ``--test``, code referenced only by tests).

See this module's docstring for the full rationale and the limitations of ``--test``'s
name-based comparison.

