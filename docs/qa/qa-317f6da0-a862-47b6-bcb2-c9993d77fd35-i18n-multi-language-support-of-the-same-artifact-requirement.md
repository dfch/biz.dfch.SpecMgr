---
classification: null
created: '2026-10-06T11:17:59.324+02:00'
id: 317f6da0-a862-47b6-bcb2-c9993d77fd35
status: draft
type: qa
updated: '2026-10-06T11:17:59.324+02:00'
version: 1.0.0
---

# I18n: Multi-Language Support of the Same Artifact — Requirements Interview

## General

### Introduction

This Q&A session captures the requirements-elicitation interview backing
[GitHub issue #197](https://github.com/dfch/biz.dfch.SpecMgr/issues/197),
"I18n: multi-language support of the same artifact", conducted with the
repository owner (`@dfch`) ahead of drafting the corresponding `feat-197-i18n`
feature plan.

The transcript below is organized by ISO/IEC 25010:2023 quality
characteristic, plus an `Elicitation Context` section describing the
interview's origin. A number of questions were already resolved during the
initial scoping conversation and are recorded here as answered, for
traceability; the remaining questions are flagged `TODO: answer pending` and
must be resolved before `feat-197-i18n`'s Task List is finalized.

### Raw Requirements

Issue #197 states, verbatim (paraphrased into a flat list for traceability):

- specmgr must support multiple languages of the same artifact. At this
  time, an artifact has a unique id in `./docs/{type}/` and contains content
  in only one language.
- Support multiple languages for the same artifact.
- Reuse the same uuid for multiple languages of the same artifact.
- Keep the existing schema for an artifact regardless of the language.
- Keep section names regardless of the language.
- Have only one language in any file.
- Have command(s), skill(s), and agent(s) for: translation,
  sync-and-drift-detection, and listing available languages for a specific
  artifact.
- Two directory-layout options were proposed, with the author open to
  suggestions:
  1. `./docs/{type}/{language}`
  2. `./docs/{language}/{type}`
- The existing structure must remain unchanged.
- The default language is EN, stored at `./docs/{type}` (no language
  segment).

## Elicitation Context

<!-- Captured during the initial scoping conversation ahead of drafting feat-197-i18n, 2026-10-06. -->

> **0.0010**: What prompted this interview, and who participated?

This interview was prompted by GitHub issue #197, opened by the repository
owner (`@dfch`) on 2026-10-06, requesting multi-language support for specmgr
artifacts. The repository owner is the sole participant interviewed so far.

> **0.0020**: Who are the intended users/stakeholders of multi-language
> artifacts (e.g. non-English-speaking authoring teams, external auditors,
> translators)?

TODO: answer pending

## Functional Suitability

<!-- Core functional requirements from issue #197, resolved and open, elicited 2026-10-06. -->

> **1.0010**: Of the two directory-layout options in the issue
> (`./docs/{type}/{language}` vs. `./docs/{language}/{type}`), which should
> this feature use?

`./docs/{type}/{language}/` (Option 1). EN stays exactly where it is today
(`./docs/{type}`), with no migration required for the default language,
cleanly satisfying "existing structure must remain unchanged." It also fits
the existing per-domain base-directory resolution (`SPECMGR_<DOMAIN>_DIR`):
adding a language segment is just "descend one more directory below the
existing resolved base when language != default," with no change to the
resolution contract itself. It is also consistent with this codebase's
domain-first convention (ADR ece4554b-725c-4f76-bc04-5d2b760363d2) — type
stays the top organizing unit everywhere else (tools/prompts/resources,
`docs/api`, etc.).

Option 2 (`./docs/{language}/{type}`) was considered and rejected: it would
require special-casing EN as "no language prefix" to satisfy the
unchanged-structure requirement, and would require inserting a path segment
*before* the existing per-domain base-dir resolution for every domain — a
deeper, more invasive change than Option 1's "append a subdir."

> **1.0020**: Which document-type domains should be in scope for i18n
> support, and should ADR be included?

All twelve whole-body domains (req, uc, tsk, qa, prb, gol, rsk, dec, sop,
feat, vcr, sysrs) are in scope. ADR is explicitly excluded: it already has
its own separate, simpler lifecycle (schema under the shared top-level
`models/adr/`, no generic `update`/`set_status`/`delete`/`validate`
dispatch tooling), consistent with how ADR has been excluded from other
cross-cutting features in this codebase.

> **1.0030**: How should the language of a given file be recorded — a new
> frontmatter field, or inferred purely from the directory path?

Inferred purely from the directory path (`./docs/{type}/{language}/`); no
new frontmatter field is added. A moved/renamed file's perceived language
changes with it, which is accepted as the simpler trade-off versus adding a
`language` field to every domain's frontmatter schema.

> **1.0040**: What language-code format should be used in directory names?

ISO 639-1 two-letter codes (e.g. `en`, `de`, `fr`), matching the directory
example from the issue (`./docs/{type}/de/`).

> **1.0050**: Should a translated copy of an artifact derive its own
> filename/slug from its own (translated) title, or reuse the slug of the
> original-language document?

The same slug is reused across every language copy of a given artifact —
language-neutral, derived once (from the EN title, or more precisely from
whichever language the slug was first derived from) and never re-derived
per translation. This keeps filenames identical across language
subfolders (e.g. `./docs/req/my-slug.md` and `./docs/req/de/my-slug.md`),
which simplifies pairing/lookup across languages even though the uuid
inside each file's frontmatter is already the real identity key.

> **1.0060**: Do `set_status`/`set_classification` apply to a single
> language file, or to every language copy of an artifact at once? Does the
> same answer hold for content edits (the generic `update`/`edit` tools)?

`set_status` and `set_classification` apply artifact-wide, across every
language copy sharing the same id — status and classification are
properties of the artifact as a whole, not of one language's text.
`update`/`edit` (and any future `create_translation`-style tool), by
contrast, are language-specific: they operate on exactly one language's
file content and leave every other language copy untouched.

> **1.0070**: Must EN always be the first-authored ("source") language for
> a given artifact, or can an artifact originate in a non-EN language and
> be translated into EN later? If the latter, how is the "source of truth"
> language tracked, independently of the "default" language (EN, which is
> simply where the no-language-suffix folder sits)?

TODO: answer pending. Raised explicitly during elicitation: a team working
primarily in German may author an artifact in DE first (with no EN version
yet) and translate it into EN afterward to satisfy the "default language is
EN, stored at `./docs/{type}`" convention. This means the "default
language" (a fixed storage-location concept) and the "source/authoritative
language" (whichever language was most recently content-edited and is the
drift-detection reference) are two distinct concepts that must both be
defined precisely.

> **1.0080**: Should i18n capabilities be exposed as new dedicated generic
> tools (e.g. `create_translation`, `list_languages`, `check_drift`),
> or as a `language` parameter added to the existing generic/per-domain
> tools, or some combination of both?

TODO: answer pending. Flagged as needing deeper investigation: the answer
to 1.0060 already shows that different existing tools need different
behavior (`set_status`/`set_classification` artifact-wide vs.
`update`/`edit` per-language), so a single uniform answer (e.g. "just add
a `language` parameter everywhere") may not be sufficient on its own.

> **1.0090**: Does specmgr itself perform the text translation (e.g. by
> calling an LLM/translation API), or does the caller always supply
> already-translated markdown content?

The caller always supplies already-translated content; specmgr never calls
an external translation/LLM API itself, consistent with specmgr being a
pure artifact-storage/validation layer with no built-in LLM calls anywhere
else in the codebase. How the caller obtains the translated text is outside
specmgr's concern. A dedicated OpenCode skill/subagent that uses a
specialized translation-capable sub-agent to help produce that text may be
added as a follow-on convenience, but is not required for specmgr's own
tool contracts.

> **1.0100**: When a read (e.g. `get_<d>`/`list_<d>`) targets a language
> with no translated file yet, what should happen?

Silently fall back to the default language (EN) — no error, and no
fallback indicator/flag is returned to the caller.

> **1.0110**: What is explicitly out of scope for this feature?

- The ADR domain (see 1.0020).
- Machine/automatic translation — specmgr never calls an LLM/translation
  API itself (see 1.0090); a future OpenCode skill/subagent to assist with
  producing translated text is a separate, optional follow-on.
- Automatic reconciliation/auto-merge of drifted translations — drift is
  only detected/reported, never auto-resolved or auto-re-translated.
- Region-variant language tags (e.g. `en-US` vs. `en-GB`) — only plain ISO
  639-1 two-letter codes are supported.
- Migrating/renaming the existing `docs/` directory layout for EN — EN's
  existing location and files are untouched; i18n is purely additive (new
  language subfolders only).

## Performance Efficiency

<!-- Raised during elicitation: the existing per-domain DocCache (feat-107) was designed around one file per id. -->

> **2.0010**: Should the per-domain `DocCache` (feat-107-doc-cache) cache
> every language's file, or only the EN (default-language) copy?

TODO: answer pending. Flagged during elicitation: "we only want to keep a
cache for EN docs (because they are supposed to be all the same)" —
meaning the schema/structure is identical across languages even though the
text differs, so the caching value of non-EN copies may be lower. The exact
caching strategy (EN-only cache with uncached reads for other languages, a
separate lighter per-language cache, or something else) still needs to be
decided and its consequences for cache-invalidation on write worked out.

> **2.0020**: Does resolving a document by id (the existing
> `find_doc_path_by_id`-style scan) need to fan out across every language
> subfolder under a type's base directory, and if so, what is the
> performance impact versus today's single-directory scan?

TODO: answer pending.

## Compatibility

> **3.0010**: Must every existing caller that never passes a `language`
> argument continue to work exactly as it does today (i.e. is this feature
> required to be 100% backward compatible for non-i18n-aware callers)?

TODO: answer pending (expected answer: yes, but not yet formally confirmed).

## Interaction Capability

> **4.0010**: Should an OpenCode skill/command/subagent be built to help an
> agent produce translated text (e.g. via a specialized translation-model
> sub-agent), mirroring the `repair`/`refine-feature` precedents?

Yes, as a desirable follow-on — not core to this feature's own tool
contracts (see 1.0090). The skill would invoke a specialized sub-agent with
a translation model to produce the translated markdown content, which is
then handed to specmgr's own translation-storage tooling exactly like any
other caller-supplied content.

> **4.0020**: Should `list_languages`-style output be formatted for direct
> human/agent readability (e.g. which languages exist, which are drifted),
> or purely as structured data for programmatic consumption?

TODO: answer pending.

## Reliability

> **5.0010**: If a specific language's file is deleted (or never existed)
> while the id is still valid in at least one other language, what should
> `get_<d>(id, language=X)` return?

TODO: answer pending. Related to 1.0100 (missing-translation fallback for
reads), but distinct: 1.0100 covers "no translation ever existed for X";
this covers "a translation for X existed and was then removed."

## Security

> **6.0010**: Must the `classification` frontmatter value be identical
> across every language copy of one artifact, enforced by tooling, or can
> different language copies independently carry different classification
> values?

TODO: answer pending. Given 1.0060's answer that `set_classification`
applies artifact-wide, the expected answer is "must be identical, enforced
by construction" — but this has not been explicitly confirmed, and the
enforcement mechanism (e.g. what happens to a pre-existing inconsistency
found during a drift check) is undefined.

## Maintainability

> **7.0010**: Do `<TYPE> <uuid>: {title}` cross-reference bullets (used by
> `sysrs`, `vcr`'s `## Verifies`, `feat`'s `### Related Decisions`, etc.)
> need their embedded `{title}` text translated to match the containing
> document's language, or do they always keep the referenced document's
> original (e.g. EN) title regardless of the containing document's
> language?

TODO: answer pending.

## Flexibility

> **8.0010**: Is the ISO 639-1 two-letter code set strictly closed, or
> should org-internal/custom language identifiers ever be permitted?

TODO: answer pending (expected answer: strictly closed to ISO 639-1, per
1.0110's "region-variant language tags are out of scope," but not yet
formally confirmed for non-standard codes generally).

## Safety

> **9.0010**: Can a translated copy of an artifact ever carry a different
> lifecycle `status` than its source/other-language copies (e.g. the DE
> copy marked `deprecated` while the EN copy stays `accepted`)?

TODO: answer pending. Given 1.0060's answer that `set_status` applies
artifact-wide, the expected answer is "no, status is always shared across
every language copy of one artifact" — but this has not been explicitly
confirmed as a hard invariant, nor has the failure mode of a pre-existing
inconsistency (e.g. discovered during a drift check) been defined.

## More Information

This Q&A precedes, and is intended to directly feed, the `feat-197-i18n`
feature plan (tracking
[GitHub issue #197](https://github.com/dfch/biz.dfch.SpecMgr/issues/197)).
Once every `TODO: answer pending` question above has a real answer, revisit
this document, use `create_feat` (or `set_feat_id` if `feat-0-i18n` was
created first) to draft `feat-197-i18n`'s `## Plan` section directly from
these answers — in particular, the `### Requirements`/`### Design Notes`
sections should restate the Functional Suitability answers above, and the
`### Task List`'s first phase should be a dedicated design/investigation
phase (producing a new ADR, since this is cross-cutting across every
whole-body domain) resolving the Performance Efficiency, Reliability, and
Security `TODO`s before any domain code changes begin.
