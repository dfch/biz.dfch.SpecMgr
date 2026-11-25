# The common modeling decisions

## When to Split a Container

Split when:

- Parts deploy independently
- Parts scale independently
- Parts use different technology stacks
- Parts have different availability requirements

Do NOT split when:

- It's just different modules in the same process
- You want to show internal structure (use components instead)

## When to Add Components

Add components when:

- The container's internal structure is architecturally significant
- You need to show how responsibilities are distributed
- There are important interfaces between internal parts

Skip components when:

- The container is simple enough to understand from its description
- Components would just mirror the folder structure
- The diagram would have too many elements to be useful

## When to Model External Systems

Model as an external software system when:

- You don't own or control it
- It's operated by a different team/organization
- You interact with it through a defined API/protocol

Model as a container within your system when:

- You deploy and manage it (even if it's third-party software like
  PostgreSQL)
- It's part of your system's infrastructure

In this DSL version there is no `externalSystem` keyword: an external
system is a **top-level** `softwareSystem` (or `element`) carrying the
`External` tag, outside the owned system:

```
emailProvider = softwareSystem "Email Delivery Service" "Delivers notification emails on behalf of the platform." "External"
```

The owned system's containers point at it with their relationships
(`dispatch -> emailProvider "sends notification emails to" "REST/JSON"`).
Because the keyword does not exist, the export JSON's `externalSystems`
section is never populated by this DSL — the fact to look for is the
`External` tag on a top-level element, and a third-party service that
ended up as a container inside the owned system is a modeling mistake.

## Common Mistakes

1. **Confusing containers with Docker containers** — C4 containers are
   runtime boundaries
2. **Treating libraries as containers** — JARs, packages, modules are
   code-level, not containers. When several elements share or embed a
   library, the library is still no element: no container, no component,
   no "embeds" relationship — name it in the sharing elements'
   descriptions instead
3. **Vague relationship labels** — "Uses" says nothing; describe the
   intent
4. **Missing technology on inter-container relationships** — always
   specify protocol
5. **Too many components** — only model architecturally significant
   groupings
6. **Mixing abstraction levels** — don't show components and external
   systems at the same level in a container diagram
7. **Creating component/code diagrams that won't be maintained** — if
   it'll go stale, don't create it
8. **Missing titles or legends** — every diagram needs both
9. **Modeling organizational structure** — C4 models software, not teams

## Diagram Staleness

| Level | Change Rate | Maintenance Effort |
|-------|------------|-------------------|
| System Context | Slow | Low — create and maintain |
| Container | Moderate | Low — create and maintain |
| Component | Fast during development | Medium — create only if valuable |
| Code | Very fast | None — generate on demand, don't maintain |
