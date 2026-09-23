---
description: List and resolve the artifacts a specmgr document references (its `<TYPE> <uuid>` cross-references), by delegating to the read-only ref-finder subagent.
agent: ref-finder
---

List the referenced artifacts for `$ARGUMENTS` -- a `<type> <id>` pair naming the source document (e.g. `sysrs 3f2a1b3c-...`, `dec 9c1f...`, or `feat feat-144-ref-artifact`).

1. Parse `<type> <id>` from my input. If it is missing or malformed, ask me for a clean pair with the `question` tool rather than guessing.
2. Apply your own workflow: call `list_references(type, id)` and, if the result is `truncated` and I want the full set, page through with higher `offset`s.
3. Report every referenced artifact as `type`, `id`, `title`, `path`, clearly flagging any that were **not found** on disk, and state the total reference count. Do not edit, write, or commit anything.
