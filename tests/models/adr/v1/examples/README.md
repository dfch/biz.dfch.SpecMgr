# MADR 4.0.0 example templates

Verbatim, byte-for-byte copies of the four official MADR 4.0.0 templates
(plan §2's source document), used as parser fixtures in
`tests/models/adr/v1/test_examples.py`:

- `adr-template-bare-minimal.md`
- `adr-template-bare.md`
- `adr-template-minimal.md`
- `adr-template.md`

Source: <https://github.com/adr/madr/tree/4.0.0/template>
License: CC0-1.0 OR MIT (per `adr/madr`'s `LICENSE`/`LICENSE.CC0-1.0`/
`LICENSE.MIT`), not `biz.dfch.SpecMgr`'s AGPL-3.0-or-later -- these files are
third-party fixtures, not this project's own source, so they intentionally
carry no SPDX header of their own.

These are unfilled placeholder templates, not real ADRs -- see
`test_examples.py` for which ones are expected to parse successfully as-is
versus raise `AdrParseError`/`pydantic.ValidationError` because a mandatory
section, or `status`, still holds template placeholder text.

## Renderer golden file

`adr-full-golden.md` is a project-authored fixture (not a MADR upstream
file, so it carries no third-party license note): the exact, byte-for-byte
markdown that `render_adr` must produce for the fully-populated `Adr` built
by `_full_adr()` in `test_renderer.py`'s `TestRenderAdrGoldenFile`.
