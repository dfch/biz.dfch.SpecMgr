# `biz.dfch.specmgr.tsk.models.v1`

TaskList (TSK) models -- Pydantic schema and (in a later phase) parser powered by ``models/md``.

Mirrors the ``req/models/v1`` layout: body classes map directly to heading
sections in a ``tsk`` markdown file -- see ``body.py``/``task_item.py`` for
the full hierarchy -- and ``frontmatter.py`` narrows the generic
``MarkdownFrontmatter`` for the ``tsk`` document type.

Per `.specmgr/feat/feat-10-add-artifact-type-tasklist/README.md` Phase 1
("Specification"), only the frontmatter and body models exist so far. There is
no ``TskDocument``/``parse_tsk``/``TskSummary`` yet -- those are Phase 2 -- so,
unlike ``req.models.v1``, this package does not yet export them.
