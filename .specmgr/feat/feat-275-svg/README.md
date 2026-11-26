---
created: '2026-11-26T15:04:57.925+01:00'
id: feat-275-svg
status: planning
type: feat
updated: '2026-11-26T15:16:48.788+01:00'
version: 1.0.0
---

# Feature: SVG artifact type with embedded frontmatter

## Plan

### Overview

A new whole-body document type `svg`: an SVG image that carries the regular specmgr frontmatter embedded inside the SVG itself. It is the first non-markdown domain. specmgr never produces or draws the images; it only parses, validates, adopts and maintains the metadata of SVG files that other tools or people create: it embeds the frontmatter when missing, checks that an existing one is correct, and bumps `updated` on every write. Apart from that, `svg` is treated as much like the other UUID whole-body domains as possible: the same frontmatter rules, the same generic mutation tools, the same non-raising result contracts, the uniform sharded per-language layout (feat-245), multi-language variants (feat-197), the reference vocabulary, the similarity search and the reference graph. Implements issue #275.

### Requirements

- REQ-001: `svg` is a whole-body document type, registered in `general/tools/_domains.py`'s `WHOLE_BODY_DOMAINS` (canonical position after `set`), with UUID ids, its own package `svg/` (`models/v1/`, `tools/`, `resources/`, `prompts/`, `data/`) per the domain-first layout, and the reference tag `SVG`.
- REQ-002: Documents live in the uniform sharded per-language layout of feat-245: `docs/svg/{lang}/{id[:2]}/{uuid}-{slug}.svg`, `en` included, no type prefix in the file name, the shared `SPECMGR_DOCS_DIR`-rooted base (no `SPECMGR_SVG_DIR`).
- REQ-003: The frontmatter is a YAML document (`---` delimited, exactly the shape of every other domain's frontmatter block) inside the CDATA section of an SVG `metadata` element whose `id` attribute is `specmgr`: `<metadata id="specmgr"><![CDATA[---` ... `---]]></metadata>`. It is parsed by the existing shared frontmatter parser and validated by `SvgFrontmatter`, a `MarkdownFrontmatter` subclass narrowing `type` to `Literal["svg"]`.
- REQ-004: An SVG may contain any number of `metadata` elements, but exactly one with `id="specmgr"` (zero is the not-adopted state of REQ-016, more than one is a validation error). Its position inside the document is not checked, because SVG tools reorder elements. When specmgr inserts the block, it is always the first child element of the root `svg` element.
- REQ-005: The artifact title is the text of the root `title` element (the first `title` element that is a direct child of the root `svg` element, whitespace-normalized); it is mandatory and must not be empty. The root `desc` element (the first direct-child `desc`) is optional. Nested `title`/`desc` elements of other elements are not the artifact title and are ignored by specmgr.
- REQ-006: The slug derives from the EN title via the existing `slugify`; the file name is fixed at creation and never re-derived on a later title change (the behavior of every other domain).
- REQ-007: The title procedure of `create_svg`/`adopt_svg` is exactly: (1) a non-blank `title` parameter is used, replacing the text of an existing root `title` or inserting a new one; (2) otherwise an existing root `title` with text is used unchanged; (3) otherwise the first sentence of a non-empty root `desc` (up to the first `.`, `!`, `?` or line break, cut at a word boundary to at most 60 characters, no ellipsis) is inserted as the root `title`; (4) otherwise the fallback `SVG <first 8 hex digits of the uuid> (<created as yyyy-MM-dd>)` is inserted as the root `title`. An inserted root `title` is placed directly after the specmgr metadata block.
- REQ-008: `SvgFrontmatter` follows the same rules as every other UUID domain: `type` is `svg`, `id` is a canonical UUID equal to the UUID in the file name, `version` is semver, `created`/`updated` are ISO 8601 date-times (DEC 23a14195), `classification` is the shared free-text field.
- REQ-009: The status vocabulary is the closed set `draft`/`review`/`final` (default `draft`), and the status state machine (`_STATUS_TRANSITIONS`, feat-108) is exactly `draft -> review`, `review -> draft`, `review -> final`, `final -> draft`; there is no terminal state and `draft -> final` is not allowed.
- REQ-010: Every specmgr write to an SVG is a text splice: only the text of the specmgr metadata block and, where the title procedure or `set_svg_title` requires it, the text of the root `title` element are replaced or inserted. Every other byte of the file is preserved. The XML is never re-serialized.
- REQ-011: Before any XML parsing, the raw text is rejected when it contains a `<!DOCTYPE` or `<!ENTITY` declaration (XXE, entity expansion), exceeds the maximum file size of 4 MiB, or holds a specmgr metadata block larger than 64 KiB. Parsing uses the Python standard library only; no new dependency is added.
- REQ-012: A valid SVG is well-formed XML whose root element is `svg` in the SVG namespace `http://www.w3.org/2000/svg`. No schema validation and no render check are performed.
- REQ-013: The security profile applies to the whole tree in every namespace, including XHTML inside `foreignObject`, and rejects: (a) the elements `script`, `iframe`, `object`, `embed`, `frame`; (b) any attribute whose local name starts with `on`; (c) URL-carrying attributes (`href`, `xlink:href`, `src`, `action`, `formaction`) whose value is not one of: a `#fragment`, a relative reference, `http:`/`https:`/`mailto:` on an `a` element only, `data:image/png|jpeg|gif|webp` on an `image` element only; (d) external `http:`/`https:` loads in `use`, `image`, `feImage`, and in CSS `url()`/`@import` inside `style` elements and `style` attributes; (e) `animate`/`set` elements whose `attributeName` is `href` or `xlink:href`. URL values are checked after XML decoding with leading/trailing whitespace and control characters stripped. `foreignObject` itself and ordinary `https` links on `a` are allowed.
- REQ-014: specmgr's own writes are injection-safe: a frontmatter value containing `]]>` is rejected, title text written by specmgr is XML-escaped, and every write re-parses and fully re-validates the resulting text before it reaches the disk (nothing is written on any failure).
- REQ-015: Reads have no side effects: `get_svg`, `list_svg`, `parse_svg`, `validate`, `list_languages`, `check_translation_drift`, `list_references`, the similarity tools, the diagram tools and `specmgr lint` never write, move or rename a file.
- REQ-016: A file that is valid SVG but has no specmgr metadata block is reported as a distinct, non-raising not-adopted state: an inline `list_svg` row and a `get_svg` `ParseFailureResult` whose `error` names the missing block and points to `adopt_svg`; `specmgr lint` fails on it with the same pointer.
- REQ-017: `adopt_svg(path, title=None, id=None)` makes an existing SVG file a specmgr document, idempotently: no block present inserts one (REQ-004) and runs the title procedure (REQ-007); a valid block present writes nothing and returns the frontmatter; an invalid block present returns a non-raising `ValidateResult` and writes nothing (the fix goes through the `repair` prompt). The uuid is taken from a `<uuid>-<slug>.svg` file name when present, otherwise generated; the file is then moved to its sharded location (REQ-002). `created` and `updated` are the adoption time. `path` must resolve inside the `svg` domain base directory (`_path_safety` confinement, checked before any file access); the language is the path's language directory, and for a non-default language `id` is mandatory and must name an existing EN source (the feat-197 create rule).
- REQ-018: `create_svg(content, ..., id=None, language="en")` writes a caller-supplied SVG text as a new document: the specmgr block is inserted when missing (a present block's `id` must be absent or equal to the new id), the title procedure runs, and the file is written to its sharded location. The feat-197 rules for `id` and `language` apply unchanged (a non-default language requires the EN source's `id`; `id` is forbidden for EN). A content-validation failure returns the non-raising `ValidateResult` (DEC f14f125e chain).
- REQ-019: The domain tools are `create_svg`, `adopt_svg`, `parse_svg`, `list_svg`, `get_svg`, `get_svg_example`, `get_svg_template`, `get_svg_schema` and `set_svg_title(id, title, language="en")`; the resources are `specmgr://svg/example` and `specmgr://svg/template`, plus the static rulebook `specmgr://svg/rules`; the prompts are `create_svg` and `update_svg`. `get_svg(raw=True)` returns the complete file text (there is no frontmatter-stripped body), with the read-style `offset`/`limit` windowing and `numbered` over its lines.
- REQ-020: The generic tools accept `type="svg"` (`validate`'s `full` with the D1 semantics of the Design Notes): `update` (whole file only; line-range mode is a caller-usage `ValueError`), `edit` (exact match on the raw file text; a match that overlaps the specmgr metadata block is a caller-usage `ValueError`), `set_status`, `set_classification`, `delete` and `validate`, each with the same non-raising result contracts as for the markdown domains and with the `language` parameter of feat-197.
- REQ-021: `update(type="svg", id, content)` replaces the image while keeping the on-disk frontmatter: any specmgr block in `content` is replaced by the on-disk block with `updated` bumped; a block in `content` whose `id` differs from the target `id` is a validation failure (non-raising `ValidateResult`). The root `title` of the new content is taken as is (re-titling does not rename the file); a missing root `title` is a validation failure.
- REQ-022: The text set used by `find_related`/`find_similar_text` and scanned by `list_references` consists of the root `title` text and the root `desc` text only (no nested `title`/`desc`, no `text`/`tspan`/`textPath` labels, no `foreignObject` text, no attribute values, no `metadata`/`style` content). The set is documented in the `specmgr://svg/rules` resource.
- REQ-023: `SVG` is added to the shared reference-tag vocabulary as both a reference source (its text set, REQ-022) and a reference target (resolved in the `svg` domain), and the reference-graph palette gains a 16th entry for `SVG`, coloured `Plum` (before `UNRESOLVED`); the `specmgr://reference-graph` rulebook is amended accordingly.
- REQ-024: `svg` is one of the language-aware domains: one file per language with the same `id` and the same basename (feat-197 + feat-245). A language code is valid for `svg` exactly when it is valid for the markdown domains (a packaged heading table exists), even though `svg` applies no heading mapping.
- REQ-025: `check_translation_drift(type="svg", ...)` reports staleness (the source `updated` newer than the variant's) and structural drift: the two files' element trees compared with all character data removed, by element qualified name, order and `id` attribute, excluding every `metadata` element and the root `title`/`desc` text. `list_languages` works for `svg` unchanged.
- REQ-026: `specmgr lint` and the `specmgr-lint` pre-commit hook recognize `.svg` documents in the sharded layout (all three drift-pinned copies of the artifact pattern), run the full `parse_svg` validation, and report the repair pointer (`/repair svg <id>`, or `adopt_svg` for a not-adopted file).
- REQ-027: Every phase of this feature ends with a fully green CI gate (the complete pre-commit set and the complete test suite on 3.11/3.12/3.13 plus the 3.13 documentation drift checks); there is no known-red intermediate phase.

### Acceptance Criteria

- [ ] ACC-001: For a plain SVG without a specmgr block, `create_svg` writes `docs/svg/en/<id[:2]>/<uuid>-<slug>.svg` whose first child of the root `svg` is the specmgr metadata block, and every byte outside the inserted block and an inserted root `title` is identical to the input (REQ-002, REQ-004, REQ-010).
- [ ] ACC-002: The four title-procedure branches each produce the specified title and slug, asserted by one test per branch including the 60-character word-boundary cut and the uuid/date fallback (REQ-006, REQ-007).
- [ ] ACC-003: A file with two `metadata id="specmgr"` elements, a frontmatter with a wrong `type`, an `id` different from the file-name uuid, a non-semver `version`, a malformed timestamp, or an out-of-vocabulary status each fails `parse_svg` with an actionable message; a specmgr block in any position (not first) parses (REQ-003, REQ-004, REQ-008).
- [ ] ACC-004: `set_status` accepts exactly the four transitions of REQ-009 and returns `InvalidStatusTransitionResult` for every other pair, nothing written (REQ-009).
- [ ] ACC-005: After `set_status`, `set_classification`, `set_svg_title` and `update`, the file differs from the previous version only inside the specmgr block (and the root `title` for `set_svg_title`), and `updated` is bumped (REQ-010, REQ-021).
- [ ] ACC-006: A DOCTYPE with an external entity, a "billion laughs" internal entity set, a file of 4 MiB + 1 byte and a metadata block of 64 KiB + 1 byte are each rejected (and files of exactly 4 MiB and blocks of exactly 64 KiB accepted) before any XML parsing, asserted by a test that patches the XML parser to fail if called (REQ-011).
- [ ] ACC-007: A non-SVG XML root, an SVG root in the wrong namespace and a truncated file each fail validation; a well-formed SVG with Inkscape/sodipodi/draw.io namespaces and a `foreignObject` passes (REQ-012, REQ-013).
- [ ] ACC-008: One test per REQ-013 rule (a) to (e) fails validation, including a `script` element in the XHTML namespace inside `foreignObject`, an `onload` attribute in a foreign namespace, `jav&#x61;script:` with embedded whitespace, `<use href="https://...">`, CSS `url(https://...)` and `<set attributeName="href" to="javascript:...">`; an `a` element with `https:` and an `image` with `data:image/png` pass (REQ-013).
- [ ] ACC-009: A `classification` value containing `]]>` is rejected and nothing is written; a title containing `</title><script>` is written XML-escaped and the resulting file passes validation (REQ-014).
- [ ] ACC-010: For a not-adopted file, `list_svg` reports an inline row and `get_svg` a `ParseFailureResult`, both naming `adopt_svg`, and the file is byte-unchanged afterwards; `specmgr lint` fails on it with the same pointer (REQ-015, REQ-016, REQ-026).
- [ ] ACC-011: `adopt_svg` run twice on the same file writes once (the second run is a no-op returning the same frontmatter); a file named `<uuid>-<slug>.svg` keeps its uuid; a file named `diagram.svg` gets a new uuid and ends up in its sharded location; a path outside the `svg` base directory and a traversal path are rejected before any file access; an invalid block returns `ValidateResult` with nothing written (REQ-017).
- [ ] ACC-012: `update` with a line range and `edit` with a match overlapping the specmgr block each raise `ValueError` with nothing written; `update` with content carrying a block of another `id` returns `ValidateResult` (REQ-020, REQ-021).
- [ ] ACC-013: `find_similar_text` matches an `svg` document on a word that only appears in its root `desc`, and does not match on a word that only appears in a nested `title` or a `text` label; `list_references` on an `svg` finds a `REQ <uuid>` in its root `desc` and ignores one in a `text` label (REQ-022).
- [ ] ACC-014: `list_references` on a markdown document resolves an `SVG <uuid>` reference to the `svg` document's title and path, and `get_reference_diagram` renders the `svg` node with the 16th palette entry (REQ-023).
- [ ] ACC-015: A `de` variant created with the EN source's `id` lives at `docs/svg/de/<id[:2]>/<same basename>`, is listed by `list_languages`, and `check_translation_drift` reports no drift for a translation that changes only text, and structural drift for an added element or a changed `id` attribute (REQ-024, REQ-025).
- [ ] ACC-016: The EN-only consumers (`find_related`, `find_similar_text`, `list_references`, `get_reference_diagram(_all)`) never see an `svg` language variant (REQ-024).
- [ ] ACC-017: Every phase's final commit has a green CI run on the feature branch, recorded in Progress (REQ-027).
- [ ] ACC-018: `validate(type="svg", full=False)` accepts a plain SVG without a specmgr block or root `title`; `full=True` on the same content returns `valid=False` naming `adopt_svg`; neither raises (D1, REQ-020).

### Scope

#### Included

- The `svg` domain package: model, safe parser, security profile, metadata-block locate/splice, title procedure, text-set extraction, tools, resources (incl. the `specmgr://svg/rules` rulebook), prompts, packaged example/template SVGs and schema.
- The generic tools `update`, `edit`, `set_status`, `set_classification`, `delete`, `validate` for `type="svg"`, EN and language variants.
- The file-suffix generalization of the shared sharded path helpers (feat-245) and of `specmgr lint` (path mode, sweeps, placement validator, the three drift-pinned artifact patterns).
- The cross-domain consumers: reference vocabulary, `list_references`, similarity corpus, reference graph palette and rulebook, `set` items (via the shared vocabulary), `repair` prompt, `specmgr://config`.
- i18n: language variants, `list_languages`, `check_translation_drift`, `translate_artifact`/`specmgr://i18n` guidance for `svg`.
- The OpenCode host surface: the `svg-adopt` skill (the adopt flow), the `specmgr-svg` skill (every other `svg` task), the `/svg-adopt <path>` command that references the `svg-adopt` skill, and the regenerated harness bundle.
- A new DEC for the embedding format and the first non-markdown domain.
- Documentation: AGENTS.md domain bullet, `server.py` docstring, README, CHANGELOG `[Unreleased]`, regenerated `docs/api/`, `docs/GENERATED.md`, `docs/MCP.md`, `docs/svg_schema.json`.

#### Explicitly Out Of Scope

- Producing, drawing, converting or optimizing images (specmgr never generates SVG content).
- Sanitizing SVG files (specmgr rejects; it never strips or rewrites offending content).
- SVG schema validation (RelaxNG/DTD) and render checks (resvg/cairosvg).
- Other image formats (PNG, draw.io XML); a later domain may follow this one's pattern.
- SVG-native multi-language (`switch`/`systemLanguage` inside one file).
- Nested `title`/`desc` and label text in the similarity/reference text set.
- `sysrs` typed sections for `SVG` references.
- A migration of existing SVGs in the repo (`docs/coverage.svg` is not a specmgr document and stays outside `docs/svg/`).

### Dependencies

#### Depends On

- feat-245-shard-docs (PR #266): the uniform sharded per-language layout and the sharded lint gate; this feature branches from `dev` only after PR #266 is merged.
- feat-197-i18n: the language-variant machinery (`_language_guard`, `_LANGUAGE_ADAPTERS`, `list_languages`, `check_translation_drift`).
- feat-108-fsm: the per-domain status state machines and `_status_fsm.py`.
- feat-207-reference-graph: the reference-graph palette and rulebook.

#### Blocks

- None known.

### Design Notes

**Embedding format.** The YAML frontmatter is stored verbatim, including its `---` delimiters, in `<metadata id="specmgr"><![CDATA[` ... `]]></metadata>`. `metadata` is the SVG-native container for non-rendered data and is preserved by Inkscape and most editors; comments are dropped more often. CDATA keeps the YAML free of XML escaping, so the existing `_frontmatter_parse` code parses it unchanged. Optimizers such as SVGO remove `metadata` and comments by default; no embedding survives them, which is why adopting an already-named file keeps its uuid (REQ-017). The serialized block specmgr writes is fixed: `<metadata id="specmgr"><![CDATA[` + newline + the YAML frontmatter block (as the markdown domains write it) + `]]></metadata>`, followed by a newline and the root element's indentation when one can be detected.

**Locating and splicing the block.** The block is located on the raw text by a scanner that skips comments, CDATA sections and processing instructions, accepts any attribute order and both quote styles, and matches a `metadata` element (any namespace prefix bound to the SVG namespace) with `id="specmgr"`. The full XML parse then confirms the scanner's result (exactly one such element, same position); a disagreement is a validation error. Splices replace the exact character range the scanner returned, so every other byte is preserved (REQ-010). The insertion point for a new block is immediately after the end of the root element's start tag.

**Read performance.** The whole file is always read: the block position is not fixed (REQ-004) and `DocCache` validates every hit against a hash of the full content. `list_svg` and `get_svg` both go through the full parse via `DocCache`, which keeps the DEC 9080b37c byte-identity between a `list_svg` failed row and the `get_svg` `ParseFailureResult` unconditional (the feat-187 two-stage cache had to time-qualify it for `feat`). Task 120.150 benchmarks a cold `list_svg` over a synthetic corpus; only if it is too slow does a follow-up introduce a scanner-only dirty stage.

**Safe parsing with the standard library.** `xml.etree.ElementTree` (expat) never fetches external entities, and with no DTD present only the five predefined entities exist. Rejecting `<!DOCTYPE`/`<!ENTITY` in the raw text before parsing (REQ-011) therefore removes XXE and entity expansion without `defusedxml`. The limits are module constants: 4 MiB (4 194 304 bytes) per file and 64 KiB (65 536 bytes) per specmgr block, both measured on the UTF-8 encoded text (no env var; a later env var goes through `_envregistry`). The YAML is loaded with the safe loader the existing frontmatter parser already uses.

**Security model.** There are three attack surfaces: specmgr parsing a file (REQ-011), specmgr writing a file (REQ-014: a `]]>` in a frontmatter value would close the CDATA and inject markup; unescaped title text would break out of `title`), and people viewing the file in a browser or IDE preview (REQ-013). Schema validation and render checks add no protection: schema-valid SVG may contain `script`, and a render check executes hostile content. The REQ-013 denylist lowers the risk but is not a sanitizer guarantee; the `specmgr://svg/rules` resource states this and recommends embedding through `img`, where browsers never run scripts. A blanket ban on `foreignObject` and external links is not needed, because rules (a) to (e) cover the dangerous content inside them, and draw.io exports use `foreignObject` for labels.

**Title, slug and i18n.** The root `title` is the accessible name of the image (the first `title` child). It is placed after the metadata block when specmgr inserts it; screen readers use the first `title` child, not the first child, so this order is safe. In a language variant the root `title` is translated, while the basename keeps the EN slug (feat-197 + feat-245).

**Validate semantics (D1, settled).** For the markdown domains, `full` selects between two content shapes (body only vs. frontmatter plus body), and a shape mismatch is a caller-usage `ValueError`. An SVG has only one shape: it is always a complete XML file, with or without a specmgr block. `full` therefore selects the question instead of the shape:

- `full=False` (default): "is this acceptable input for `create_svg`/`update`?" It runs the pre-check, the well-formedness and SVG-root check and the security profile (REQ-011 to REQ-013). A root `title` is not required (the title procedure can derive one). A specmgr block is optional; if present it must be valid (REQ-003, REQ-004, REQ-008, REQ-014).
- `full=True`: "is this a complete stored `svg` document?" It runs everything above and also requires exactly one valid specmgr block and a non-empty root `title` (REQ-005).
- A missing block under `full=True` is a content defect, not a shape mismatch: it returns `valid=False` with the `adopt_svg` pointer and never raises. Neither value of `full` raises `ValueError` for `svg`.
- The match between the frontmatter `id` and the file-name uuid cannot be checked here (`validate` is disk-free and id-free); `parse_svg`, the `get_svg`/`list_svg` read path and `specmgr lint` check it.

**Generic-tool coupling and the temporary pending mapping.** The generic tools assert at import time that their adapter sets equal the registry (`set(_ADAPTERS) == set(WHOLE_BODY_DOMAINS)` and `set(_LANGUAGE_ADAPTERS) == set(LANGUAGE_AWARE_DOMAINS)`, e.g. `general/tools/update.py`), and the cross-domain consumers iterate the registry. Adding `svg` to the registry at once would force every adapter into one oversized phase. Phase 130 therefore adds `_INTEGRATION_PENDING: dict[str, frozenset[str]]` to `_domains.py` (domain -> the tools and consumers not yet supporting it), and each tool and consumer derives its domain set, its `type` `Literal` and its asserts from "registry minus the domains pending for me" (the same derivation pattern as `LANGUAGE_AWARE_DOMAINS` excluding `feat`). Each later phase adds one group's adapters and removes that group from the pending set. Phase 180 deletes the mapping and its derivation, and a test pins that it no longer exists. The MCP schema of each generic tool gains `"svg"` in the phase that adds its adapter, so `docs/MCP.md` changes step by step.

**Phase 100 and dead-code checking.** The pure library has no `src/` caller until Phase 120, so `vulture` would flag it. Phase 100 adds temporary `whitelist.py` entries, each commented with `feat-275 Phase 100, removed in Phase 120`; Task 120.170 removes them.

**Existing tests that will need care.** `tests/regression/test_issue_67.py` globs `*_template.md`/`*_example.md` only, so the timestamps in the `svg` template/example would escape its check: Task 120.130 extends it to `*_template.svg`/`*_example.svg`. The registry-driven tests (`tests/test_schema_surface_registration.py`, `tests/test_agent_facing_wording.py`, `tests/general/tools/test__domains.py`, `test_i18n_all_domains.py`, `test_set_status_fsm_domains.py`, `tests/commands/test_lint.py`) start covering `svg` in Phase 130 and must honour the pending mapping. No test requires every domain package to be in the registry (checked 2026-11-26), so Phase 120 can register the standalone domain in the server before the registry entry.

**Decisions D1 to D4:**

- D1: the `validate` `full` semantics described above — settled.
- D2: the size limits are 4 MiB per file and 64 KiB per specmgr block — settled.
- D3: the reference-graph colour for `SVG` is `Plum` — settled.
- D4: the OpenCode command is `/svg-adopt <path>`, with no dedicated subagent — settled. It references the `svg-adopt` skill, which holds the flow, so an agent can use the same flow without the command (see "OpenCode host surface" below) — settled.

**OpenCode host surface.** The adopt flow lives in exactly one place, the `svg-adopt` skill, so the `/svg-adopt` command and any agent that adopts SVGs on its own run the same steps. The command only parses `$1`, tells the agent to follow the `svg-adopt` skill, and reports. The skill holds:

- its trigger phrasings ("adopt this SVG", "register diagram.svg as a specmgr document", "add the specmgr frontmatter to this image", and a newly found SVG without a specmgr block reported by `list_svg`, `get_svg` or `specmgr lint`);
- the precondition checks: the path lies inside the `svg` base directory; for a non-English file, the existing English source's `id` is required, asked for with the `question` tool when unknown;
- the title choice: pass `title` only when the user named one, otherwise let the REQ-007 procedure decide; ask with the `question` tool when the root `title`/`desc` are both missing and a fallback title would be unhelpful;
- the call `adopt_svg(path, title, id)` and the three outcomes: inserted (report the new path after the sharded move), already adopted (report the no-op), invalid block (stop and hand over to the `repair` flow; never delete or overwrite the block);
- the rule that reads never adopt a file, so the agent must call `adopt_svg` itself, and that it never commits.

The `specmgr-svg` skill covers every other `svg` task (`create_svg`, `set_svg_title`, the generic `update`/`edit`/`set_status`/`set_classification`/`delete`/`validate`, the `specmgr://svg/rules` resource). Its description explicitly defers adopt requests to `svg-adopt`, so the two skills never compete for the same request.

### Related Decisions

- 38efdb66-8025-45c5-bbe8-45b25fc7a772 (dec): multi-language artifact variants (directory layout, same id, same basename).
- 9abe91e7-99d2-48ba-9084-6a4da7d1e311 (dec): uniform sharded per-language layout (feat-245, on branch `feat-245` until PR #266 merges).
- 36905d5b-8057-4294-8665-c7eed5534db0 (dec): dispatch-only domains; no per-domain `update_<d>`/`set_status_<d>`.
- c4efbde6-fd19-4aa8-8668-95316ed62dcc (dec): single source of truth for the domain-name set.
- a79608e4-88cd-498f-8ca1-445df4d04f92 (dec): per-domain status state machines.
- 519d1206-4d2a-4500-9046-6db635209996 (dec): non-raising structured results.
- 9080b37c-82b3-4f63-81f1-79641d0bf14c (dec): `ParseFailureResult` and the `list_<d>`/`get_<d>` error byte-identity.
- 33c5ab08-ff58-4c73-8c32-23abaf3838e3 (dec): the filesystem is the sole source of truth (reads have no side effects).
- bfd76370-b59b-4d65-b550-a969f6c93c9d (dec): content-hash-validated per-domain read cache.
- 750842b2-aca4-4649-ba0c-855ec8e1f505 (dec): embedding-based similarity search.

### Task List

#### Phase 100: Decision record and pure library

- [ ] Task 100.100: Write the DEC "Embed specmgr frontmatter in an SVG metadata element; svg as the first non-markdown domain" (embedding format, block rules, title procedure, security model, no new dependency, text splice, the options considered: metadata+CDATA, XML comment, namespaced XML attributes).
- [ ] Task 100.110: `svg/models/v1/frontmatter.py`: `SvgFrontmatter` (`type: Literal["svg"]`, closed status set, `_STATUS_TRANSITIONS` table with the import-time invariants) (REQ-008, REQ-009).
- [ ] Task 100.120: `svg/models/v1/_precheck.py`: the raw-text pre-check (DOCTYPE/ENTITY, file size, block size) (REQ-011).
- [ ] Task 100.130: `svg/models/v1/_block.py`: the metadata-block scanner (skips comments, CDATA, processing instructions; attribute order; quote styles; namespace prefixes), the splice and the first-child insertion, the `]]>` guard (REQ-003, REQ-004, REQ-010, REQ-014).
- [ ] Task 100.140: `svg/models/v1/_security.py`: the REQ-013 profile over the parsed tree, every namespace, URL normalization (REQ-013).
- [ ] Task 100.150: `svg/models/v1/_title.py`: root `title`/`desc` lookup, the four-branch title procedure, the escaped title splice (REQ-005, REQ-007, REQ-014).
- [ ] Task 100.160: `svg/models/v1/_text.py`: the REQ-022 text set (root `title` + root `desc`, whitespace-normalized) (REQ-022).
- [ ] Task 100.170: `svg/models/v1/parser.py` + `document.py`: `parse_svg(text, *, language=None, path=None)` returning `SvgDocument` (frontmatter, title, desc, text set), cross-checking scanner and parse results, the not-adopted state as its own exception type caught by the shared parse-failure channels, actionable messages in the `models/md/_errors` style (REQ-003 to REQ-005, REQ-012, REQ-016).
- [ ] Task 100.180: Unit tests for 100.110 to 100.170, including the ACC-003, ACC-006, ACC-007, ACC-008 and ACC-009 cases and the parser-not-called pin for the pre-check (ACC-002 for the pure title logic).
- [ ] Task 100.190: Temporary `whitelist.py` entries for the not-yet-called library symbols; full CI gate green (REQ-027).

#### Phase 110: Shared prerequisites (behavior-preserving)

- [ ] Task 110.100: Add a `suffix: str = ".md"` parameter to `sharded_doc_path`, `iter_doc_paths`, `iter_doc_paths_all_languages`, `find_doc_path_by_id` and `find_parse_failure` in `general/tools/_doc_paths.py`; every existing call site keeps the default (REQ-002).
- [ ] Task 110.110: Generalize `commands/lint.py` (`_infer_type`, the placement validator, the `--type`/`--all` sweeps) to a per-domain file suffix; markdown domains keep `.md` (REQ-026).
- [ ] Task 110.120: Unit tests for the suffix parameter (`.svg` listing, sharded path, id lookup, parse-failure probe) and a pin that the `.md` behavior is unchanged; full CI gate green (REQ-027).

#### Phase 120: Standalone svg domain

- [ ] Task 120.100: `svg/tools/_paths.py`, `_lock.py`, `_cache.py` (`DocCache` over `parse_svg`), `_io.py`, `_write.py` (splice-then-validate-then-write, atomic) (REQ-002, REQ-010, REQ-014).
- [ ] Task 120.110: `create_svg`, `adopt_svg`, `parse_svg`, `list_svg`, `get_svg` (incl. `raw`/`offset`/`limit`/`numbered`, `ParseFailureResult`, `language`), `set_svg_title` (REQ-015 to REQ-019).
- [ ] Task 120.120: `get_svg_example`, `get_svg_template`, `get_svg_schema`; packaged `svg/data/svg_example.svg`, `svg_template.svg`, `svg_rules.md`, `svg_schema.json`, the create/update prompt instruction files (REQ-019).
- [ ] Task 120.130: Resources `specmgr://svg/example`, `specmgr://svg/template`, `specmgr://svg/rules`; prompts `create_svg`, `update_svg`; extend `tests/regression/test_issue_67.py` to the `.svg` template/example (REQ-019).
- [ ] Task 120.140: Register the `svg` package in `server.py` (import line and module docstring); regenerate `docs/MCP.md`, `docs/api/`, `docs/GENERATED.md`, `docs/svg_schema.json`.
- [ ] Task 120.150: Benchmark a cold `list_svg` over 500 synthetic SVGs of mixed size (incl. files close to the 4 MiB limit with embedded base64 images); record the result in Progress; open a follow-up only if a cold call exceeds 5 s.
- [ ] Task 120.160: Tool tests for ACC-001, ACC-002, ACC-005 (`set_svg_title`), ACC-010, ACC-011 and the feat-197 `language`/`id` rules of `create_svg`.
- [ ] Task 120.170: Remove the Phase 100 `whitelist.py` entries; full CI gate green (REQ-027).

#### Phase 130: Registry entry, pending mapping and validate

- [ ] Task 130.100: Add `svg` to `WHOLE_BODY_DOMAINS` and its `WholeBodyDomain` adapters (base dir, `.svg` path iterator, `load_by_id`, `parse_text`) (REQ-001).
- [ ] Task 130.110: Add `_INTEGRATION_PENDING` with `svg` pending for `update`, `edit`, `set_status`, `set_classification`, `delete`, `repair`, `lint`, `config`, `references`, `similarity`, `reference_graph`, `i18n_drift`; derive each tool's and consumer's domain set, `type` `Literal` and import-time asserts from it.
- [ ] Task 130.120: `validate` adapter for `svg` with the D1 `full` semantics (no `ValueError` shape check for `svg`); update the `validate` tool docstring accordingly; remove `validate` from the pending set (REQ-020).
- [ ] Task 130.130: Update the registry-driven tests to honour the pending mapping; tests for the derivation (a pending domain is absent from the tool's `Literal`, its asserts and its behavior) and for the `svg` `validate` cases incl. ACC-018; regenerate docs; full CI gate green (REQ-027).

#### Phase 140: set_status and set_classification

- [ ] Task 140.100: Register the `svg` FSM table in `_status_fsm.py`; `set_status` EN and language adapters (block splice, `updated` bumped, `InvalidStatusResult`/`InvalidStatusTransitionResult`/`ParseFailureResult` channels) (REQ-009, REQ-020).
- [ ] Task 140.110: `set_classification` EN and language adapters with the `]]>` guard (REQ-014, REQ-020).
- [ ] Task 140.120: Remove both from the pending set; tests for ACC-004, ACC-005 and ACC-009 through the generic tools; regenerate docs; full CI gate green (REQ-027).

#### Phase 150: update and edit

- [ ] Task 150.100: `update` EN and language adapters: whole file only, line-range `ValueError`, keep the on-disk block, foreign-id check, root-`title` check (REQ-020, REQ-021).
- [ ] Task 150.110: `edit` EN and language adapters: exact match on the raw text, the block-overlap `ValueError`, full re-validation (REQ-020).
- [ ] Task 150.120: Remove both from the pending set; tests for ACC-005 (`update`) and ACC-012; regenerate docs; full CI gate green (REQ-027).

#### Phase 160: delete, repair, lint and config

- [ ] Task 160.100: `delete` EN and language adapters (REQ-020).
- [ ] Task 160.110: The `repair` prompt and its instructions cover `svg` (host-native repair of the raw file, `validate(type="svg", full=True)` loop).
- [ ] Task 160.120: `specmgr lint` for `svg` (path mode, sweeps, repair and adopt pointers); the anchored artifact pattern in `.pre-commit-config.yaml`, `.github/workflows/ci.yml` and `tests/commands/test_lint.py` extended to `.svg` (REQ-026).
- [ ] Task 160.130: `specmgr://config` lists the `svg` base directory; update the config golden fixture per its capture README.
- [ ] Task 160.140: Remove the four groups from the pending set; tests incl. ACC-010's lint part; regenerate docs; full CI gate green (REQ-027).

#### Phase 170: Cross-domain consumers

- [ ] Task 170.100: Add `SVG` to the shared reference-tag vocabulary (source and target) and to `list_references`; `set` items accept `SVG` bullets through the shared vocabulary (REQ-023).
- [ ] Task 170.110: Similarity corpus over the REQ-022 text set (REQ-022).
- [ ] Task 170.120: The 16th reference-graph palette entry (`SVG` coloured `Plum`, D3) and the `specmgr://reference-graph` rulebook amendment (REQ-023).
- [ ] Task 170.130: Remove the three groups from the pending set; tests for ACC-013, ACC-014 and ACC-016; regenerate docs; full CI gate green (REQ-027).

#### Phase 180: i18n drift, host surface, close-out

- [ ] Task 180.100: `check_translation_drift` structural comparison for `svg` (REQ-025); remove `i18n_drift` from the pending set.
- [ ] Task 180.110: `translate_artifact` instructions and `specmgr://i18n` guidance for `svg` (what to translate: root `title`, root `desc`, visible text; what never to translate: the specmgr block, `id` attributes, structure) (REQ-024).
- [ ] Task 180.120: Delete `_INTEGRATION_PENDING` and its derivation; a test pins that it no longer exists.
- [ ] Task 180.130: OpenCode `svg-adopt` skill (`.opencode/skill/svg-adopt/SKILL.md`), self-triggering, the single home of the adopt flow (see the Design Notes "OpenCode host surface"), with its pinning test `tests/opencode/test_skill_svg_adopt.py`.
- [ ] Task 180.133: OpenCode `specmgr-svg` skill (`.opencode/skill/specmgr-svg/SKILL.md`) for every other `svg` task, deferring adopt requests to the `svg-adopt` skill, with its pinning test `tests/opencode/test_skill_svg.py`.
- [ ] Task 180.136: The `/svg-adopt <path>` command (D4, `.opencode/command/svg-adopt.md`, no dedicated subagent) as a thin wrapper that runs the `svg-adopt` skill's flow for `$1` and reports; a pinning test that the command references the skill and does not restate the flow; the regenerated harness bundle.
- [ ] Task 180.140: AGENTS.md `svg/` bullet and the cross-cutting enumerations (domain counts, tag vocabulary, palette, language-aware domains), README, CHANGELOG `[Unreleased]`.
- [ ] Task 180.150: Tests for ACC-015; final regeneration; full CI gate green (REQ-027).

## Progress

### Current Status

**As of 2026-11-26**: plan drafted from the elicitation with the user; not yet refined. Implementation waits for feat-245 (PR #266) to be merged to `dev`.

### Blockers

- [ ] feat-245-shard-docs (PR #266) must be merged to `dev` before Phase 100 starts.

### Updates

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26 15:16:48.788+01:00 - D1 settled

The user accepted the D1 `validate` `full` semantics; all four open decisions are now settled.

#### 2026-11-26 15:13:53.502+01:00 - Separate svg-adopt skill

The adopt flow moves into its own `svg-adopt` skill that the `/svg-adopt` command references, so agents can use it without the command. Task 180.130 rewritten, Tasks 180.133 and 180.136 added; the Scope and the Design Notes ("OpenCode host surface") updated.

#### 2026-11-26 15:11:03.631+01:00 - Decisions D2 to D4 settled, D1 proposed

D2 (4 MiB / 64 KiB), D3 (`Plum`) and D4 (`/svg-adopt`, no subagent) applied to REQ-011, REQ-023, ACC-006 and Tasks 120.150, 170.120, 180.130. D1 written out in the Design Notes as a proposal, with the new ACC-018 and an amended Task 130.120; it awaits the user's confirmation.

#### 2026-11-26 15:04:57.925+01:00 - Plan drafted

Plan written from the elicitation conversation with the user (2026-11-24 to 2026-11-26). Issue #275 holds a short summary; this plan holds all details. Open decisions D1 to D4 are listed in the Design Notes.

### Decisions Made

<!-- Newest entry first -- prepend new entries directly below this comment. -->

#### 2026-11-26 15:16:48.788+01:00 - Validate semantics for svg

Settled with the user (D1): for `svg`, `full=False` checks acceptable input for `create_svg`/`update` (block and root `title` optional), `full=True` checks a complete stored document (exactly one valid block and a non-empty root `title`); a missing block under `full=True` is `valid=False` with the `adopt_svg` pointer, and `validate` never raises `ValueError` for `svg`.

#### 2026-11-26 15:13:53.502+01:00 - Adopt flow in its own skill

Settled with the user: a dedicated `svg-adopt` skill holds the adopt flow; the `/svg-adopt` command is a thin wrapper that references it, and the general `specmgr-svg` skill defers adopt requests to it.

#### 2026-11-26 15:11:03.631+01:00 - Size limits, graph colour, command name

Settled with the user: D2 — a maximum of 4 MiB per file and 64 KiB per specmgr metadata block, as module constants. D3 — the reference-graph colour for `SVG` is `Plum`. D4 — the OpenCode command is `/svg-adopt <path>`, with no dedicated subagent.

#### 2026-11-26 15:04:57.925+01:00 - Elicitation results

Settled with the user: type name `svg`; frontmatter in `metadata id="specmgr"` with CDATA; any number of `metadata` elements but exactly one specmgr block, position free, inserted as the first child; root `title` mandatory, root `desc` optional, slug from the title; the four-step title procedure and `set_svg_title`; `created` is the adoption time when a block is re-added; status `draft`/`review`/`final` with the REQ-009 machine; text splices only; standard library only with the DOCTYPE pre-check; the REQ-013 security profile with `foreignObject` and `https` links allowed; reads without side effects, `adopt_svg` idempotent, the generic `update` instead of a per-domain one; all generic tools and all cross-domain consumers in scope from the start; the similarity/reference text set is root `title` + root `desc` only; one file per language in the feat-245 layout; drift is staleness plus structure; a full green CI gate after every phase, with Phase 130 split into Phases 130 to 180 through a temporary pending mapping.

### Related PRs / Commits

- [Issue #275](https://github.com/dfch/biz.dfch.SpecMgr/issues/275): tracking issue for this feature.
- [PR #266](https://github.com/dfch/biz.dfch.SpecMgr/pull/266): feat-245 uniform sharded layout (dependency).

### More Information

The lint gap for language subfolders raised during the elicitation is already closed by feat-245 (open-depth artifact pattern, all-language sweeps); this feature only extends it to `.svg`.
