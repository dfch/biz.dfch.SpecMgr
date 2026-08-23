# QA v2 Phase 8: remove qa/models/v1

**Session ID:** ses_fd1878c5effeQ6unB6VYLZOqVm
**Created:** 8/23/2026, 1:54:00 PM
**Updated:** 8/23/2026, 2:13:34 PM

---

## User

in @.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md I want to continue. I tested the functionality - looks good. What is next?

---

## Assistant (Build · Claude Sonnet 5 · 9.5s)

_Thinking:_



Looking at the plan, Phases 0–7 are fully complete (feature `status: done` in frontmatter) — the core QA v2 adjacent-pairs feature is finished and merged-ready. The only remaining work is **Phase 8: Cleanup — remove `qa/models/v1/`**, which was added afterward as an explicit follow-up and is entirely `not-started`.

Let me check the current repo state first.

**Tool: bash**

**Input:**
```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr branch --show-current && git -C /home/user/src/biz.dfch.SpecMgr status --short && git -C /home/user/src/biz.dfch.SpecMgr log --oneline -5"
}
```

**Output:**
```
feat-14
M  pyproject.toml
M  uv.lock
686902a doc(feat-14): add session transcript
1374162 docs(qa): add Phase 8 follow-up (remove qa/models/v1) to feat-14 plan
acd8bc5 docs(qa): regenerate generated docs for QA v2
fa44f4b feat(qa): update QA prompts for v2 adjacent question/answer structure
f18468a feat(qa): update QA resources (schema/example/template) for v2

```

---

## Assistant (Build · Claude Sonnet 5 · 2.4s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr diff pyproject.toml"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Claude Sonnet 5 · 2.6s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr diff --stat; git -C /home/user/src/biz.dfch.SpecMgr diff uv.lock | head -30"
}
```

**Output:**
```
(no output)
```

---

## Assistant (Build · Claude Sonnet 5 · 2.0s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr status"
}
```

**Output:**
```
On branch feat-14
Your branch is up to date with 'origin/feat-14'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	modified:   pyproject.toml
	modified:   uv.lock


```

---

## Assistant (Build · Claude Sonnet 5 · 2.6s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "git -C /home/user/src/biz.dfch.SpecMgr diff --cached"
}
```

**Output:**
```
diff --git a/pyproject.toml b/pyproject.toml
index f575800..dacb2dc 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -4,7 +4,7 @@ build-backend = "setuptools.build_meta"
 
 [project]
 name = "biz-dfch-specmgr"
-version = "0.8.0"
+version = "0.9.0"
 description = "An artifact manager for system specifications."
 readme = "README.md"
 requires-python = ">=3.11"
diff --git a/uv.lock b/uv.lock
index 6d09dab..6514a4d 100644
--- a/uv.lock
+++ b/uv.lock
@@ -109,7 +109,7 @@ wheels = [
 
 [[package]]
 name = "biz-dfch-specmgr"
-version = "0.8.0"
+version = "0.9.0"
 source = { editable = "." }
 dependencies = [
     { name = "markdown-it-py" },

```

---

## Assistant (Build · Claude Sonnet 5 · 9.5s)

These are pre-existing staged changes (a version bump to 0.9.0, unrelated to feat-14 — probably left over from a release step). I'll leave them alone unless you want them addressed separately.

## Status recap

Feature `feat-14` is functionally **done**: Phases 0–7 (the actual v2 schema, hard version cutover, and full tool/resource/prompt/docs rewiring) are complete, tested, and green. What's left is the explicitly-scoped follow-up:

### Phase 8: Cleanup — remove `qa/models/v1/` (not started)

| Task | What it does |
|---|---|
| **8.1** | Grep repo-wide for `qa.models.v1` / `qa\.models\.v1` references (don't trust the known list). Then **move** `QaFrontmatter` (and possibly `QaSummary`, per the grep results) out of `qa/models/v1/` into `qa/models/v2/` (or a new shared location), repoint every import, update `qa/models/v2/__init__.py`'s re-export. Only then delete the rest of `qa/models/v1/` (`__init__.py`, `_util.py`, `body.py`, `document.py`, `parser.py`, `summary.py` if not moved). |
| **8.2** | Delete `tests/qa/models/v1/`; fix/remove any other test importing `qa.models.v1`. |
| **8.3** | Update `AGENTS.md`'s `qa/` bullet to drop the "v1 legacy, retained on disk" language since v1 no longer exists. |
| **8.4** | Phase-end quality gate (`ruff format --check`, `ruff check`, `vulture`, full `unittest`, `specmgr docs`/`mcp-docs` drift checks — `qa/models/v1` docstrings must cleanly drop from `docs/GENERATED.md`/`docs/api/`), update Progress section, commit as `chore(qa)!: remove qa/models/v1 (superseded by v2)`. |

This is a breaking change for anyone importing `qa.models.v1` directly (none of specmgr's own tools/resources/prompts do, since Phase 4).

### Recommendation

Start with **Task 8.1**'s grep sweep to find the exact blast radius before moving/deleting anything — the plan explicitly warns not to assume the known reference list is exhaustive.

Want me to:
1. Run the grep sweep now and report exactly what needs to move/change, or
2. Delegate the whole Phase 8 to an implementation agent to execute end-to-end (move `QaFrontmatter`/`QaSummary`, delete v1, update tests/docs, run the quality gate)?

---

## User

go

---

## Assistant (Build · Claude Sonnet 5 · 3.9s)

I'll run the grep sweep first to establish the exact scope, then delegate the full Phase 8 execution.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -rn \"qa\\.models\\.v1\\|qa/models/v1\\|models\\.v1\\.frontmatter\\|models\\.v1\\.summary\\|from \\.\\.v1\\|from \\.v1\" --include=\"*.py\" --include=\"*.md\" --include=\"*.toml\" --include=\"*.yml\" --include=\"*.yaml\" src/ tests/ docs/ .pre-commit-config.yaml .github/ 2>/dev/null | grep -i qa"
}
```

**Output:**
```
src/biz/dfch/specmgr/qa/resources/qa_schema.py:36:file it reads is a ``qa/models/v1``-derived artifact -- see
src/biz/dfch/specmgr/qa/models/v2/parser.py:20:Mirrors `qa/models/v1/parser.py::parse_qa`'s structure exactly (same
src/biz/dfch/specmgr/qa/models/v2/parser.py:38:`qa/models/v1/parser.py`), matching this codebase's "v2 has zero dependency
src/biz/dfch/specmgr/qa/models/v2/parser.py:59:from ..v1.frontmatter import QaFrontmatter
src/biz/dfch/specmgr/qa/models/v2/parser.py:103:    Duplicated locally from ``qa/models/v1/parser._stringify_metadata`` (not
src/biz/dfch/specmgr/qa/models/v2/body.py:22:engine, mirroring `qa/models/v1/body.py`'s "one class per heading" shape --
src/biz/dfch/specmgr/qa/models/v2/body.py:69:verbatim from `qa/models/v1/body.py`**, not imported -- v2 has zero
src/biz/dfch/specmgr/qa/models/v2/document.py:20:Mirrors `qa.models.v1.document.QaDocument`'s own frontmatter+body pairing,
src/biz/dfch/specmgr/qa/models/v2/document.py:23:`qa.models.v1.document.QaDocument`.
src/biz/dfch/specmgr/qa/models/v2/document.py:25:`frontmatter` is `QaFrontmatter`, imported unchanged from `qa/models/v1/`
src/biz/dfch/specmgr/qa/models/v2/document.py:44:from ..v1.frontmatter import QaFrontmatter
src/biz/dfch/specmgr/qa/models/v2/document.py:56:        The YAML frontmatter block. See :class:`~biz.dfch.specmgr.qa.models.v1.frontmatter.QaFrontmatter`
src/biz/dfch/specmgr/qa/models/v2/document.py:57:        (imported unchanged from `qa/models/v1/`, per REQ-003).
src/biz/dfch/specmgr/qa/models/v2/__init__.py:20:Alongside (not replacing on disk) `qa/models/v1/`, this package models a QA
src/biz/dfch/specmgr/qa/models/v2/__init__.py:29:re-exported here unchanged from `qa/models/v1/`, per REQ-003), and
src/biz/dfch/specmgr/qa/models/v2/__init__.py:32:private/un-exported, mirroring `qa/models/v1/__init__.py`'s own choice).
src/biz/dfch/specmgr/qa/models/v2/__init__.py:47:from ..v1.frontmatter import QaFrontmatter
src/biz/dfch/specmgr/qa/models/v2/question_answer.py:20:Unlike `qa/models/v1/body.py`'s `QaSection` (one `### {free-form heading}`
src/biz/dfch/specmgr/qa/models/v2/question_answer.py:86:    Deliberately **not** heading-anchored, mirroring `qa/models/v1/body.py`'s
src/biz/dfch/specmgr/qa/models/v1/summary.py:20:Mirrors :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary`
src/biz/dfch/specmgr/qa/models/v1/summary.py:54:        :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary`).
src/biz/dfch/specmgr/qa/models/v1/_util.py:18:"""Shared, private constants for the ``qa.models.v1`` subpackage."""
src/biz/dfch/specmgr/qa/models/v1/_util.py:23:#: this package's own folder name (``qa/models/v1``) -- bump only when a
tests/general/models/test_summary.py:35:from biz.dfch.specmgr.qa.models.v1.summary import QaSummary
tests/qa/models/v2/test_parser.py:36:  `qa.models.v1.frontmatter.QaFrontmatter`, not a lookalike duplicate.
tests/qa/models/v2/test_parser.py:48:from biz.dfch.specmgr.qa.models.v1.frontmatter import QaFrontmatter as QaFrontmatterV1
tests/qa/models/v2/test_parser.py:217:    """ACC-003: `QaDocument.frontmatter`'s declared type is `qa.models.v1.frontmatter.QaFrontmatter` itself."""
tests/qa/models/v1/test_parser.py:28:from biz.dfch.specmgr.qa.models.v1 import QaDocument
tests/qa/models/v1/test_parser.py:29:from biz.dfch.specmgr.qa.models.v1.parser import parse_qa
tests/qa/models/v1/test_frontmatter.py:24:from biz.dfch.specmgr.qa.models.v1.frontmatter import QaFrontmatter
tests/qa/models/v1/test_body.py:36:from biz.dfch.specmgr.qa.models.v1.body import (
tests/qa/tools/test__write.py:27:from biz.dfch.specmgr.qa.models.v1 import QaFrontmatter
tests/qa/tools/test_list_qa.py:36:from biz.dfch.specmgr.qa.models.v1 import QaSummary
docs/GENERATED.md:125:- `qa/models/v1/__init__.py` — Question and Answer (QA) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.
docs/GENERATED.md:126:- `qa/models/v1/_util.py` — Shared, private constants for the ``qa.models.v1`` subpackage.
docs/GENERATED.md:127:- `qa/models/v1/body.py` — Question and Answer (QA) body models: whole-section fields under a single H1.
docs/GENERATED.md:128:- `qa/models/v1/document.py` — Pydantic model for a full Question and Answer (QA) document (frontmatter + body).
docs/GENERATED.md:129:- `qa/models/v1/frontmatter.py` — Question and Answer (QA) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
docs/GENERATED.md:130:- `qa/models/v1/parser.py` — Parse raw Question and Answer (QA) ``.md`` text into a :class:`QaDocument`.
docs/GENERATED.md:131:- `qa/models/v1/summary.py` — Pydantic model for one line of QA listing output.
docs/api/biz.dfch.specmgr.qa.models.v2.parser.md:5:Mirrors `qa/models/v1/parser.py::parse_qa`'s structure exactly (same
docs/api/biz.dfch.specmgr.qa.models.v2.parser.md:23:`qa/models/v1/parser.py`), matching this codebase's "v2 has zero dependency
docs/api/biz.dfch.specmgr.qa.models.v2.parser.md:52:Duplicated locally from ``qa/models/v1/parser._stringify_metadata`` (not
docs/api/biz.dfch.specmgr.qa.models.v2.document.md:5:Mirrors `qa.models.v1.document.QaDocument`'s own frontmatter+body pairing,
docs/api/biz.dfch.specmgr.qa.models.v2.document.md:8:`qa.models.v1.document.QaDocument`.
docs/api/biz.dfch.specmgr.qa.models.v2.document.md:10:`frontmatter` is `QaFrontmatter`, imported unchanged from `qa/models/v1/`
docs/api/biz.dfch.specmgr.qa.models.v2.document.md:33:    The YAML frontmatter block. See :class:`~biz.dfch.specmgr.qa.models.v1.frontmatter.QaFrontmatter`
docs/api/biz.dfch.specmgr.qa.models.v2.document.md:34:    (imported unchanged from `qa/models/v1/`, per REQ-003).
docs/api/README.md:106:- [`biz.dfch.specmgr.qa.models.v1`](biz.dfch.specmgr.qa.models.v1.md) — Question and Answer (QA) models -- Pydantic schema and parser powered by the generic ``models/md`` engine.
docs/api/README.md:107:- [`biz.dfch.specmgr.qa.models.v1._util`](biz.dfch.specmgr.qa.models.v1._util.md) — Shared, private constants for the ``qa.models.v1`` subpackage.
docs/api/README.md:108:- [`biz.dfch.specmgr.qa.models.v1.body`](biz.dfch.specmgr.qa.models.v1.body.md) — Question and Answer (QA) body models: whole-section fields under a single H1.
docs/api/README.md:109:- [`biz.dfch.specmgr.qa.models.v1.document`](biz.dfch.specmgr.qa.models.v1.document.md) — Pydantic model for a full Question and Answer (QA) document (frontmatter + body).
docs/api/README.md:110:- [`biz.dfch.specmgr.qa.models.v1.frontmatter`](biz.dfch.specmgr.qa.models.v1.frontmatter.md) — Question and Answer (QA) frontmatter, narrowing `feat-5-md-model-parser`'s generic `MarkdownFrontmatter`.
docs/api/README.md:111:- [`biz.dfch.specmgr.qa.models.v1.parser`](biz.dfch.specmgr.qa.models.v1.parser.md) — Parse raw Question and Answer (QA) ``.md`` text into a :class:`QaDocument`.
docs/api/README.md:112:- [`biz.dfch.specmgr.qa.models.v1.summary`](biz.dfch.specmgr.qa.models.v1.summary.md) — Pydantic model for one line of QA listing output.
docs/api/biz.dfch.specmgr.qa.models.v1.md:1:# `biz.dfch.specmgr.qa.models.v1`
docs/api/biz.dfch.specmgr.qa.models.v2.md:5:Alongside (not replacing on disk) `qa/models/v1/`, this package models a QA
docs/api/biz.dfch.specmgr.qa.models.v2.md:14:re-exported here unchanged from `qa/models/v1/`, per REQ-003), and
docs/api/biz.dfch.specmgr.qa.models.v2.md:17:private/un-exported, mirroring `qa/models/v1/__init__.py`'s own choice).
docs/api/biz.dfch.specmgr.qa.models.v2.body.md:7:engine, mirroring `qa/models/v1/body.py`'s "one class per heading" shape --
docs/api/biz.dfch.specmgr.qa.models.v2.body.md:54:verbatim from `qa/models/v1/body.py`**, not imported -- v2 has zero
docs/api/biz.dfch.specmgr.qa.models.v2.question_answer.md:5:Unlike `qa/models/v1/body.py`'s `QaSection` (one `### {free-form heading}`
docs/api/biz.dfch.specmgr.qa.models.v2.question_answer.md:40:Deliberately **not** heading-anchored, mirroring `qa/models/v1/body.py`'s
docs/api/biz.dfch.specmgr.qa.models.v1.body.md:1:# `biz.dfch.specmgr.qa.models.v1.body`
docs/api/biz.dfch.specmgr.qa.resources.qa_schema.md:21:file it reads is a ``qa/models/v1``-derived artifact -- see
docs/api/biz.dfch.specmgr.qa.models.v1.parser.md:1:# `biz.dfch.specmgr.qa.models.v1.parser`
docs/api/biz.dfch.specmgr.qa.resources.qa_list.md:18::func:`~biz.dfch.specmgr.qa.models.v1.parse_qa` raises) is silently
docs/api/biz.dfch.specmgr.qa.models.v1.frontmatter.md:1:# `biz.dfch.specmgr.qa.models.v1.frontmatter`
docs/api/biz.dfch.specmgr.qa.models.v1._util.md:1:# `biz.dfch.specmgr.qa.models.v1._util`
docs/api/biz.dfch.specmgr.qa.models.v1._util.md:3:Shared, private constants for the ``qa.models.v1`` subpackage.
docs/api/biz.dfch.specmgr.qa.models.v1.document.md:1:# `biz.dfch.specmgr.qa.models.v1.document`
docs/api/biz.dfch.specmgr.qa.models.v1.summary.md:1:# `biz.dfch.specmgr.qa.models.v1.summary`
docs/api/biz.dfch.specmgr.qa.models.v1.summary.md:5:Mirrors :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary`
docs/api/biz.dfch.specmgr.qa.models.v1.summary.md:34:    :class:`~biz.dfch.specmgr.tsk.models.v1.summary.TskSummary`).

```

---

## Assistant (Build · Claude Sonnet 5 · 7.2s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && grep -rn \"models\\.v1\\|from \\.\\.v1\\|from \\.v1\\|models import v1\" src/biz/dfch/specmgr/qa/tools/ 2>/dev/null"
}
```

**Output:**
```
src/biz/dfch/specmgr/qa/tools/list_qa.py:39:from ..models.v1 import QaSummary

```

---

## Assistant (Build · Claude Sonnet 5 · 11.6s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && ls -la tests/qa/models/v1/ && echo \"---v1 src---\" && ls -la src/biz/dfch/specmgr/qa/models/v1/"
}
```

**Output:**
```
total 36
drwxrwxr-x 3 user user  4096 Aug 18 18:52 .
drwxrwxr-x 5 user user  4096 Aug 23 10:56 ..
-rw-rw-r-- 1 user user     0 Aug 18 18:52 __init__.py
drwxrwxr-x 2 user user  4096 Aug 18 22:22 __pycache__
-rw-rw-r-- 1 user user 11393 Aug 18 18:52 test_body.py
-rw-rw-r-- 1 user user  2620 Aug 18 18:52 test_frontmatter.py
-rw-rw-r-- 1 user user  7738 Aug 18 18:52 test_parser.py
---v1 src---
total 56
drwxrwxr-x 3 user user  4096 Aug 19 10:18 .
drwxrwxr-x 5 user user  4096 Aug 23 10:56 ..
-rw-rw-r-- 1 user user  2159 Aug 18 18:52 __init__.py
drwxrwxr-x 2 user user  4096 Aug 22 19:18 __pycache__
-rw-rw-r-- 1 user user  1552 Aug 18 18:52 _util.py
-rw-rw-r-- 1 user user 14420 Aug 18 18:52 body.py
-rw-rw-r-- 1 user user  1992 Aug 18 18:52 document.py
-rw-rw-r-- 1 user user  3252 Aug 18 18:52 frontmatter.py
-rw-rw-r-- 1 user user  4302 Aug 18 18:52 parser.py
-rw-rw-r-- 1 user user  2132 Aug 19 10:18 summary.py

```

---

## Assistant (Build · Claude Sonnet 5 · 1030.5s)

Now I have the full, confirmed blast radius. Let me delegate Phase 8's execution to an implementation specialist with precise instructions.

**Tool: task**

**Input:**
```json
{
  "description": "Execute Phase 8: remove qa/models/v1",
  "prompt": "Repo: /home/user/src/biz.dfch.SpecMgr (branch: feat-14, already checked out — do not switch/create branches).\n\nImplement Phase 8 of `.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md` (read that file's Phase 8 section, lines ~498-548, and the \"Explicitly out of scope\" bullet in Scope, before starting). This is a mechanical cleanup: delete `qa/models/v1/` now that `qa/models/v2/` is the only tool-reachable QA schema, after moving the two still-needed shared pieces out of it first.\n\nI already ran the grep sweep. Confirmed blast radius (verified against the real repo, don't re-derive from scratch, but do a final confirmation grep after your changes to make sure nothing was missed):\n\n**Live code imports that must be repointed (functional, not docstrings):**\n- `src/biz/dfch/specmgr/qa/models/v2/parser.py:59` — `from ..v1.frontmatter import QaFrontmatter`\n- `src/biz/dfch/specmgr/qa/models/v2/document.py:44` — `from ..v1.frontmatter import QaFrontmatter`\n- `src/biz/dfch/specmgr/qa/models/v2/__init__.py:47` — `from ..v1.frontmatter import QaFrontmatter`\n- `src/biz/dfch/specmgr/qa/tools/list_qa.py:39` — `from ..models.v1 import QaSummary`\n- `tests/general/models/test_summary.py:35` — `from biz.dfch.specmgr.qa.models.v1.summary import QaSummary`\n- `tests/qa/models/v2/test_parser.py:48` — `from biz.dfch.specmgr.qa.models.v1.frontmatter import QaFrontmatter as QaFrontmatterV1` (this test explicitly cross-checks `QaDocument.frontmatter`'s declared type is the SAME `QaFrontmatter` class object — see its ACC-003 docstring/test around line 217 — update the test's own comments/assertions to reflect the new import path, but keep the identity-check intent)\n- `tests/qa/tools/test__write.py:27` — `from biz.dfch.specmgr.qa.models.v1 import QaFrontmatter`\n- `tests/qa/tools/test_list_qa.py:36` — `from biz.dfch.specmgr.qa.models.v1 import QaSummary`\n\n**Step 1 — Move, don't delete, two files:**\n- Move `src/biz/dfch/specmgr/qa/models/v1/frontmatter.py` → `src/biz/dfch/specmgr/qa/models/v2/frontmatter.py` (same `QaFrontmatter` class, content unchanged except module docstring path references and any relative imports that assumed the old location).\n- Move `src/biz/dfch/specmgr/qa/models/v1/summary.py` → `src/biz/dfch/specmgr/qa/models/v2/summary.py` (same `QaSummary` class, same treatment).\n- Update `src/biz/dfch/specmgr/qa/models/v2/__init__.py` to import both from their new local sibling modules (`.frontmatter`, `.summary`) instead of `..v1.frontmatter`, and re-export `QaSummary` too if it isn't already exported there (check current `__all__`/exports first).\n- Repoint all 8 live imports listed above to the new `qa.models.v2.frontmatter`/`qa.models.v2.summary` (or `qa.models.v2` re-export, matching each file's existing import style — e.g. `qa/tools/list_qa.py` currently does `from ..models.v1 import QaSummary`, so make it `from ..models.v2 import QaSummary` if v2's `__init__.py` re-exports it, matching that file's own convention).\n\n**Step 2 — Delete `qa/models/v1/` entirely** (after step 1's moves + repoints are done and verified working):\n- `src/biz/dfch/specmgr/qa/models/v1/__init__.py`\n- `src/biz/dfch/specmgr/qa/models/v1/_util.py`\n- `src/biz/dfch/specmgr/qa/models/v1/body.py`\n- `src/biz/dfch/specmgr/qa/models/v1/document.py`\n- `src/biz/dfch/specmgr/qa/models/v1/parser.py`\n- `src/biz/dfch/specmgr/qa/models/v1/frontmatter.py` and `summary.py` (already moved in step 1, so this dir should now be fully empty of these two as well)\n- The whole `src/biz/dfch/specmgr/qa/models/v1/` directory (including `__pycache__`)\n\n**Step 3 — Delete `tests/qa/models/v1/` entirely:**\n- `tests/qa/models/v1/__init__.py`, `test_body.py`, `test_frontmatter.py`, `test_parser.py`, and the whole directory (including `__pycache__`).\n- These tests exercised v1-only code (`QaSection`, v1's `body.py`/`parser.py`/`document.py`) that no longer exists — do not try to port them to v2, they're superseded by the existing `tests/qa/models/v2/` suite. But first double check: if any of them contain a test for `QaFrontmatter`/`QaSummary` behavior that ISN'T already covered somewhere for v2 (e.g. `test_frontmatter.py`'s status-validation cases), consider whether that coverage needs a new home — check if `tests/qa/models/v2/` or `tests/general/models/test_summary.py` already covers frontmatter/summary validation before deleting; if genuinely unique coverage would be lost, port just that test content into an appropriate v2 test file (e.g. create `tests/qa/models/v2/test_frontmatter.py` if none exists) rather than silently dropping coverage.\n\n**Step 4 — Update remaining references** (docstrings/comments only, not functional, but should be fixed for accuracy since v1 no longer exists on disk):\n- `src/biz/dfch/specmgr/qa/resources/qa_schema.py:36`\n- `src/biz/dfch/specmgr/qa/models/v2/parser.py` (module docstring mentions of `qa/models/v1/parser.py`)\n- `src/biz/dfch/specmgr/qa/models/v2/body.py` (module docstring)\n- `src/biz/dfch/specmgr/qa/models/v2/document.py` (module docstring — also update since `QaFrontmatter` moved, not \"imported unchanged from qa/models/v1/\" anymore)\n- `src/biz/dfch/specmgr/qa/models/v2/__init__.py` (module docstring)\n- `src/biz/dfch/specmgr/qa/models/v2/question_answer.py` (module docstring)\nUpdate these to describe the new reality: v1 is gone, `QaFrontmatter`/`QaSummary` now live in `qa/models/v2/` alongside the rest of the schema (QA is a single-schema domain again). Don't just delete the historical context — rephrase so the docstrings read correctly for someone with no memory of v1 ever existing, while still explaining WHY things are shaped the way they are where that context is still useful (e.g. \"fully duplicated body schema, independent of frontmatter/summary\" no longer makes sense to say once there's no v1 to be independent from — reword accordingly).\n\n**Step 5 — Update `AGENTS.md`'s `qa/` bullet** (in the repo root `AGENTS.md`, under \"## Status: six domain/cross-cutting packages implemented\"): remove the description of `qa/models/v1/` as \"legacy, retained on disk purely as historical reference, unreachable from any MCP tool/resource/prompt\" entirely, since it no longer exists on disk. QA becomes a single-schema (v2-only) domain again — reword to match how the bullet would read had v1 never existed, while KEEPING the still-accurate parts: the tool/resource/prompt lists, the `## Elicitation Context`/adjacent-pairs structural description (adjacent `<!-- comment -->` + `> question` + free-form answer, no per-question heading), and the note that it replaced v1's one-`### {heading}`-per-pair shape (a brief one-line historical note that v1 existed and was superseded is fine/expected — just drop the \"still on disk, unreachable\" framing since that's now false).\n\n**Step 6 — Final grep confirmation:**\nRun `grep -rn \"qa\\.models\\.v1\\|qa/models/v1\" src/ tests/ AGENTS.md` (excluding `docs/` and `.git/` and `__pycache__`) and confirm zero remaining hits in `src/` and `tests/` and `AGENTS.md`. (`docs/api/*.md` and `docs/GENERATED.md` will still mention v1 until regenerated — that's expected, handle in Step 7.)\n\n**Step 7 — Regenerate generated docs:**\n- `uv run --frozen specmgr docs` (regenerates `docs/api/` + `docs/GENERATED.md` — this should now drop every `qa.models.v1.*` page/listing since those modules no longer exist).\n- `uv run --frozen specmgr adr-toc` (should report no drift, unrelated to this change, but run it per the plan's phase-end gate).\n- `uv run --frozen specmgr schema --type qa` (run against both output locations the project uses: default `docs/` and `src/biz/dfch/specmgr/qa/data` — check `commands/schema.py` or prior phase notes in the feat-14 README for the exact second invocation used in Phase 5, e.g. it may need an `--output-dir` flag) — confirm it reports \"(unchanged)\"/zero drift, since QA's schema shape itself is not changing in Phase 8, only its frontmatter/summary source module locations.\n\n**Step 8 — Full quality gate:**\n```\nuv run --frozen ruff format --check\nuv run --frozen ruff check\nuv run --frozen vulture src/ whitelist.py --min-confidence 60\nuv run --frozen python -m unittest discover -v -s tests -t . -p \"test_*.py\"\n```\nAll must be green. Fix any issue found (import errors, unused imports from the old v1 paths, vulture flagging newly-moved-but-now-unused code, etc.) before proceeding.\n\n**Step 9 — Update `.specmgr/feat/feat-14-qa-v2-adjacent-qa/README.md`:**\n- Mark Task 8.1, 8.2, 8.3, 8.4 as `[x]` done with today's date (2026-08-23) and a status note, mirroring the exact level of detail/style of the Phase 0-7 entries already in that file (see how Task 1.1-7.3 are written — concise \"depends on / status: done (date)\" plus specifics of what was actually done, deviating from plan if you had to for the same reason).\n- Add a new \"Phase 8 is done\" paragraph to the Progress → Current Status section (append after the existing \"Followup added 2026-08-23...\" paragraph), describing what was moved/deleted/updated and the final quality gate result (test count, etc.), mirroring the style/detail level of the Phase 4-7 paragraphs already there.\n- Add a dated \"#### Update 2026-08-23T...\" entry to Recent Updates for Phase 8, listing what was completed, matching the existing entries' format (Completed/Next/Notes bullets).\n- Add any new non-trivial decision to \"Decisions Made\" if you had to deviate from the plan (e.g. exact destination module names, whether any v1 test coverage was ported).\n- Do NOT change the feature frontmatter `status` (it's already `done` and stays that way — Phase 8 was tracked as a followup, not a scope reopening, per the README's own existing note).\n\n**Step 10 — Commit:**\nStage everything and commit as ONE Conventional Commit:\n```\nchore(qa)!: remove qa/models/v1 (superseded by v2)\n```\nwith a commit body explaining: this is a breaking change for anyone importing `qa.models.v1` directly (even though no MCP tool/resource/prompt has referenced it since Phase 4 of feat-14); `QaFrontmatter`/`QaSummary` moved to `qa/models/v2/`; all QA schema/parsing/tooling now lives solely under `qa/models/v2/`. Do NOT push. Do not amend prior commits. Check `git status`/`git diff --cached` before committing to make sure only Phase-8-related files are staged — there are pre-existing unrelated staged changes to `pyproject.toml`/`uv.lock` (a version bump to 0.9.0) already sitting in the index from before you started; do NOT include those in your commit — unstage them first if needed (`git restore --staged pyproject.toml uv.lock`), commit only your Phase 8 changes, then re-stage those two files back exactly as they were (staged, not committed) so you leave the working tree/index in the same pre-existing state for anything unrelated to your task.\n\nAt the end, report back: (1) confirmation all quality gate steps passed with final test count, (2) the exact list of files moved/deleted/modified, (3) the commit hash, (4) whether any v1 test coverage needed porting and where it landed, (5) confirmation the unrelated pyproject.toml/uv.lock staged changes were restored to their original staged state.\n",
  "subagent_type": "implementation-specialist"
}
```

**Output:**
```
<task id="ses_fd185a99affe1Zrg3Sx359xAu9" state="completed">
<task_result>
Working tree is clean except the pre-existing unrelated `pyproject.toml`/`uv.lock` staged changes, exactly as before I started. All remaining grep hits are expected historical/descriptive references, not live imports.

## Summary

**1) Quality gate:** All green.
- `ruff format --check`: 820 files already formatted
- `ruff check`: all checks passed
- `vulture src/ whitelist.py --min-confidence 60`: no findings
- `unittest discover`: **1306 tests, all passing** (down from 1332 at Phase 7 end: −4 from deleting `tests/qa/models/v1/`'s 3 files' worth of tests, +9 from the newly-ported `test_frontmatter.py`, net −26 from dropping v1-only `test_body.py`/`test_parser.py` coverage that's fully superseded by v2's own suite)
- `specmgr docs`/`specmgr adr-toc`: regenerated cleanly, zero drift beyond QA's own changes
- `specmgr schema --type qa` (both `docs/` and `qa/data` output dirs): reported "(changed)", confirmed via `git diff` to be a docstring-only `$defs.*.description` diff, not a schema shape change (documented in Decisions Made)

**2) Files moved/deleted/modified:**
- Moved: `qa/models/v1/{frontmatter,summary}.py` → `qa/models/v2/{frontmatter,summary}.py`; `tests/qa/models/v1/test_frontmatter.py` → `tests/qa/models/v2/test_frontmatter.py`
- Deleted: rest of `qa/models/v1/` (`__init__.py`, `_util.py`, `body.py`, `document.py`, `parser.py`), all of `tests/qa/models/v1/`, and 7 orphaned `docs/api/biz.dfch.specmgr.qa.models.v1.*.md` files that `specmgr docs` doesn't auto-prune
- Modified: `qa/models/v2/{__init__,body,document,parser,question_answer}.py`, `qa/tools/list_qa.py`, `qa/resources/qa_schema.py`, `tests/general/models/test_summary.py`, `tests/qa/models/v2/test_parser.py`, `tests/qa/tools/{test__write,test_list_qa}.py`, `AGENTS.md`, `CHANGELOG.md`, plus regenerated `docs/GENERATED.md`, `docs/api/*`, both `qa_schema.json` copies, and the feature README

**3) Commit hash:** `9c129a9` — `chore(qa)!: remove qa/models/v1 (superseded by v2)`

**4) V1 test coverage porting:** `test_frontmatter.py`'s 9 field-level `QaFrontmatter` cases (type/version/status defaults, version major-gate, all-four-statuses) were genuinely unique and had no v2 equivalent — ported verbatim into `tests/qa/models/v2/test_frontmatter.py`. `test_body.py`/`test_parser.py` were dropped outright, fully superseded by the existing `tests/qa/models/v2/test_{body,parser}.py`.

**5) `pyproject.toml`/`uv.lock`:** Confirmed restored to their original pre-existing staged state (the 0.9.0 version bump) — unstaged before my commit, re-staged after, not included in the Phase 8 commit.
</task_result>
</task>
```

---

## Assistant (Build · Claude Sonnet 5 · 3.7s)

_Thinking:_



Let me verify the results independently.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && git log --oneline -3 && echo \"---status---\" && git status --short && echo \"---staged diff stat---\" && git diff --cached --stat"
}
```

**Output:**
```
9c129a9 chore(qa)!: remove qa/models/v1 (superseded by v2)
686902a doc(feat-14): add session transcript
1374162 docs(qa): add Phase 8 follow-up (remove qa/models/v1) to feat-14 plan
---status---
M  pyproject.toml
M  uv.lock
---staged diff stat---
 pyproject.toml | 2 +-
 uv.lock        | 2 +-
 2 files changed, 2 insertions(+), 2 deletions(-)

```

---

## Assistant (Build · Claude Sonnet 5 · 3.4s)

Good — the working tree is clean, only the pre-existing unrelated version-bump staged changes remain, exactly as they were before. Let me spot-check the quality gate and directory removal.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && ls src/biz/dfch/specmgr/qa/models/ && echo \"---v1 gone?---\" && ls src/biz/dfch/specmgr/qa/models/v1/ 2>&1 && echo \"---tests---\" && ls tests/qa/models/ 2>&1"
}
```

**Output:**
```
__init__.py
__pycache__
v2
---v1 gone?---
ls: cannot access 'src/biz/dfch/specmgr/qa/models/v1/': No such file or directory

```

---

## Assistant (Build · Claude Sonnet 5 · 3.6s)

_Thinking:_



**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && ls tests/qa/models/ && grep -rn \"qa\\.models\\.v1\\|qa/models/v1\" src/ tests/ AGENTS.md 2>/dev/null"
}
```

**Output:**
```
__init__.py
__pycache__
v2
src/biz/dfch/specmgr/qa/models/v2/summary.py:27:(feat-14 Phase 8: `qa/models/v1/` was removed once v2 became the domain's
src/biz/dfch/specmgr/qa/models/v2/parser.py:27:via v2's own `Qa` schema; a document shaped for the removed `qa/models/v1/`
src/biz/dfch/specmgr/qa/models/v2/frontmatter.py:30:`v1`/`v2` split (feat-14 Phase 8: `qa/models/v1/` was removed once v2 became
src/biz/dfch/specmgr/qa/models/v2/__init__.py:24:`qa/models/v1/` package (one `### {heading}` H3 per question/answer pair) has
tests/qa/models/v2/test_parser.py:37:  (feat-14 Phase 8: `QaFrontmatter` moved from the now-removed `qa/models/v1/`
tests/qa/models/v2/test_frontmatter.py:20:Ported from the now-removed `tests/qa/models/v1/test_frontmatter.py`
tests/qa/models/v2/test_frontmatter.py:21:(feat-14 Phase 8: `QaFrontmatter` moved from `qa/models/v1/` into
AGENTS.md:59:  `## Functional Suitability`. An earlier `qa/models/v1/` schema (one

```

---

## Assistant (Build · Claude Sonnet 5 · 4.0s)

Those remaining hits are all historical/descriptive (docstrings and AGENTS.md noting v1 was removed), not live imports — exactly as expected. Let me run the quality gate to independently confirm.

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen ruff check 2>&1 | tail -5 && echo \"===\" && uv run --frozen vulture src/ whitelist.py --min-confidence 60 2>&1 | tail -10"
}
```

**Output:**
```
All checks passed!
===

```

---

## Assistant (Build · Claude Sonnet 5 · 21.2s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" 2>&1 | tail -15"
}
```

**Output:**
```
['### Sec3', '', 'content', '', '#### Nested', '', 'more']
['### Sec3', '', 'content', '', '##### Nested', '', 'more']
['### Sec3', '', 'content', '', '###### Nested', '', 'more']
['### Sec3', '', 'content', '', '#### Sec4 nested', '', 'nested content']
[]
['### Sec3', '', 'content', '']


[0] # Title
[1] 
[2] Paragraph on line 2.
[3] 
[4] ## *More* `heading`

[0] # Title

```

---

## Assistant (Build · Claude Sonnet 5 · 21.8s)

**Tool: bash**

**Input:**
```json
{
  "command": "cd /home/user/src/biz.dfch.SpecMgr && uv run --frozen python -m unittest discover -s tests -t . -p \"test_*.py\" 2>&1 | grep -E \"^(OK|FAILED|Ran)\""
}
```

**Output:**
```
Ran 1306 tests in 18.228s
OK

```

---

## Assistant (Build · Claude Sonnet 5 · 8.4s)

Confirmed: 1306 tests pass, `ruff check` clean, `vulture` clean, `qa/models/v1/` and `tests/qa/models/v1/` are fully gone, no live code references remain, and the working tree is back to its pre-existing state (only the unrelated staged version bump).

## Phase 8 complete — feat-14 is now fully done

**What happened:**
- `QaFrontmatter` and `QaSummary` moved from `qa/models/v1/` into `qa/models/v2/` (their permanent home now)
- Rest of `qa/models/v1/` (`body.py`, `parser.py`, `document.py`, `_util.py`, `__init__.py`) deleted, along with `tests/qa/models/v1/` and 7 orphaned generated API doc pages
- 9 unique frontmatter test cases ported into a new `tests/qa/models/v2/test_frontmatter.py`; v1-only body/parser tests dropped as fully superseded by v2's own suite
- `AGENTS.md`, docstrings, `CHANGELOG.md`, `docs/api/`, `docs/GENERATED.md`, and both `qa_schema.json` copies regenerated/updated
- Full quality gate green (1306 tests, ruff, vulture, docs/schema drift checks)
- Committed as `9c129a9` — `chore(qa)!: remove qa/models/v1 (superseded by v2)`
- Not pushed, per your usual workflow

QA is now a clean, single-schema (v2-only) domain. With Phase 8 done, `feat-14-qa-v2-adjacent-qa` has no remaining open work — all 8 phases are complete.

One thing worth your attention separately: there's a pre-existing **staged** version bump (`pyproject.toml`/`uv.lock`, 0.8.0 → 0.9.0) sitting in the index, unrelated to this feature. It was carefully preserved untouched throughout, but you may want to commit or reconsider it separately — let me know if you'd like me to look into that.

---

