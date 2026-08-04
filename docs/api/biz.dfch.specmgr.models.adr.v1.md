# `biz.dfch.specmgr.models.adr.v1`

ADR schema version 1 (``SCHEMA_MAJOR_VERSION == 1``).

Holds every model class for this schema major version. See
``doc/adr-tool-plan.md`` §6 for the versioning strategy: a new major schema
version gets its own sibling package (``models/adr/v2/``, ...) containing
*only* the classes that actually changed for that version -- unchanged
classes are imported from the previous version's package rather than
duplicated -- plus a ``migrate_v1_to_v2()``-style adapter function. This
package is never itself duplicated wholesale; it is the frozen v1 baseline
that later versions diff against.
