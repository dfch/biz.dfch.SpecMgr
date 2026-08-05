# Acceptance Criteria using EARS

This document explains how to write acceptance criteria using the **Easy Approach to Requirements Syntax (EARS)** — a structured method for expressing system requirements and acceptance criteria in natural language.

EARS was developed by Alistair Mavin and colleagues at Rolls-Royce plc and is now widely adopted in industry (Airbus, Bosch, Honeywell, Intel, NASA, Siemens) and integrated into AI-assisted spec-driven development tools like Amazon Kiro.

## Why EARS?

EARS provides several advantages over unconstrained natural language:

- **Reduced ambiguity** – Fixed clause order and keyword vocabulary force explicit triggering conditions, preconditions, and expected responses
- **Low adoption barrier** – Keywords match everyday English; minimal training overhead
- **Improved testability** – Structured separation of conditions and responses makes test case derivation straightforward
- **LLM-friendly** – Constrained syntax can be parsed by both humans and large language models, improving AI-assisted development

## The 5 Core Patterns

All EARS requirements follow this general structure:

```
WHILE <optional precondition(s)>, WHEN <optional trigger>, 
the <system name> SHALL <system response>
```

A requirement must have:
- Zero or many preconditions (WHILE)
- Zero or one trigger (WHEN)
- Exactly one system name
- One or many system responses

### 1. Ubiquitous

**Always active** — no triggering condition or precondition.

```
THE <system name> SHALL <system response>
```

**Example:**
```
THE ADR document SHALL be valid YAML with a frontmatter block.
```

**When to use:** For unconditional requirements that apply at all times.

---

### 2. Event-driven

**Triggered by an event** — specifies how the system must respond when something happens.

```
WHEN <trigger>, the <system name> SHALL <system response>
```

**Example:**
```
WHEN a user clicks the "Create ADR" button, the system SHALL open the ADR creation form.
```

**When to use:** For requirements that depend on a specific action or event occurring.

---

### 3. State-driven

**Active while a condition is true** — specifies behavior that persists as long as a state remains.

```
WHILE <precondition(s)>, the <system name> SHALL <system response>
```

**Example:**
```
WHILE an ADR is in "draft" status, the system SHALL allow the user to edit all fields.
```

**When to use:** For requirements that depend on the system being in a particular state or mode.

---

### 4. Optional feature

**Applies only when a feature is included** — specifies behavior for product variants or optional capabilities.

```
WHERE <feature is included>, the <system name> SHALL <system response>
```

**Example:**
```
WHERE the MCP server extra is installed, the system SHALL expose ADR tools via the Model Context Protocol.
```

**When to use:** For requirements that apply only to certain configurations or product variants.

---

### 5. Unwanted behaviour

**Response to faults, failures, or errors** — specifies how the system must handle undesired situations.

```
IF <trigger>, THEN the <system name> SHALL <system response>
```

**Example:**
```
IF an invalid ADR ID is provided, THEN the system SHALL return a 404 error with a descriptive message.
```

**When to use:** For error handling, validation, and fault tolerance requirements.

---

## Complex Requirements (The "+1")

Simple patterns can be combined to express richer behavior:

```
WHILE <precondition(s)>, WHEN <trigger>, the <system name> SHALL <system response>
```

**Example:**
```
WHILE an ADR is in "proposed" status, WHEN a decision-maker submits a review, 
the system SHALL update the ADR's "informed" field and send a notification.
```

**When to use:** When a requirement depends on both a state and an event.

---

## Practical Examples for SpecMgr

### User Story: Create a new ADR

**User Story:** As a system architect, I want to create a new ADR so that I can document architectural decisions.

**Acceptance Criteria (in EARS):**

1. **Ubiquitous**
   ```
   THE ADR creation form SHALL display all mandatory fields: title, context and problem statement, 
   considered options, and decision outcome.
   ```

2. **Event-driven**
   ```
   WHEN the user submits the ADR creation form with valid data, the system SHALL create a new ADR 
   file with a unique ID and save it to the docs/adr/ directory.
   ```

3. **State-driven**
   ```
   WHILE the form has unsaved changes, the system SHALL display a warning if the user attempts to navigate away.
   ```

4. **Optional feature**
   ```
   WHERE the CLI extra is installed, the system SHALL allow ADR creation via the `specmgr adr create` command.
   ```

5. **Unwanted behaviour**
   ```
   IF the user submits the form with a blank title, THEN the system SHALL display a validation error 
   and prevent form submission.
   ```

6. **Complex**
   ```
   WHILE the ADR is in "draft" status, WHEN the user clicks "Save", the system SHALL persist all changes 
   to the .md file and display a success message.
   ```

---

## Writing Good EARS Acceptance Criteria

### Do's

- ✅ Use the keywords consistently: `THE`, `WHEN`, `WHILE`, `WHERE`, `IF`, `THEN`
- ✅ Keep the system name consistent throughout (e.g., "the system", "the ADR tool", "the API")
- ✅ Make triggers and preconditions explicit and testable
- ✅ Use singular, clear system responses
- ✅ Avoid multiple independent responses in one criterion (split into separate criteria)

### Don'ts

- ❌ Mix multiple unrelated conditions in a single criterion
- ❌ Use vague language like "should", "may", "might" — use "SHALL" for mandatory behavior
- ❌ Embed multiple triggers in one WHEN clause
- ❌ Omit the system name or use pronouns like "it" instead
- ❌ Write more than three preconditions in a single WHILE clause (split into separate criteria)
