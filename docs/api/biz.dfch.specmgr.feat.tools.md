# `biz.dfch.specmgr.feat.tools`

MCP tool wrappers for features (mirrors ``dec/tools/``'s own shape).

Bespoke, folder-per-document addressing (``_paths.py``, ``_io.py``,
``_lock.py``, ``_write.py`` -- *not* built on
``general/tools/_doc_paths.py``, since ``feat`` documents live one per
folder at ``<base>/<id>/README.md`` with a non-UUID id) underpins the eight
lifecycle tools below.

``parse_feat`` reads a raw filepath, parses, and validates it into a
structured document model. ``get_feat_example`` returns a complete, valid
sample feature document as raw markdown; ``get_feat_template`` returns a
document with every field present but populated with short placeholder
("blind text") content instead -- both read a packaged, build-guaranteed
data file rather than anything on the caller's filesystem (the packaged
files themselves are Phase 3's job -- see each tool's own module docstring).

``get_feat`` reads, parses, and returns a full feature document by id -- the
sole id-based read path for FEAT (there is no ``specmgr://feat/{id}``
resource, ADR ddfb1109-422d-4507-8dbc-dc5e4bec9614). ``list_feat`` returns
one page of id/title/status/ref/path summaries of every feature, shipped as
a paged tool from day one (ADR ec9f5262-9912-49d0-903f-fcfb54f28c13).
``create_feat`` assigns the next ``feat-NNN-slug`` id, builds the
frontmatter itself, and writes a new document (body markdown only, no
frontmatter) under ``<base>/<id>/README.md`` (``feat.tools._paths``/
``_lock``/``_io``/``_write``). Whole-body and line-range updates of an
existing document go through the generic ``update`` tool in
``general.tools`` (``type="feat"``), preserving every frontmatter field
except ``updated``. Status changes of an existing document go through the
generic ``set_status`` tool in ``general.tools`` (``type="feat"``), also
bumping ``updated``, leaving the body untouched. There is no
``update_feat``/``set_status_feat`` tool of ``feat``'s own. Deletion of
``feat`` documents goes through the generic ``delete`` tool in
``general.tools`` (``type="feat"``). ``set_feat_id`` renames an existing
feature's ``feat-NNN-slug`` id: it validates the new id's shape, refuses if
the target folder already exists, renames ``<base>/<id>/`` to
``<base>/<new_id>/``, rewrites the frontmatter ``id`` and ``updated``
fields, and leaves the body byte-identical -- the one path that ever
changes a ``feat`` document's id after ``create_feat`` assigns it (see
``set_feat_id.py``'s own module docstring for the ``feat_create_lock()``
+ ``feat_lock(id)`` locking order). ``validate_feat`` is a disk-free,
id-free dry run against a submitted ``content`` string, independent of the
other tools. Import this package to register all feature tools at once::

    from biz.dfch.specmgr.feat import tools  # noqa: F401 (side-effects only)
