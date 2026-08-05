---
status: accepted
date: '2026-08-05'
id: 23a14195-339c-48af-99d2-97c9964041ae
version: 1.0.0
---

# Use ISO 8601 for all dates and times

## Context and Problem Statement

The project needs a consistent, unambiguous date and time format across all specifications, documentation, code, and filenames. Different formats (MM/DD/YYYY vs DD/MM/YYYY, various time representations) can cause confusion, parsing errors, and interoperability issues. Filenames with timestamps must work reliably on both Linux and Windows, avoiding platform-specific invalid characters.

## Decision Drivers

- Consistency across the entire codebase, documentation, and filenames
- International standard compliance (ISO 8601)
- Machine-readability and sortability
- Compatibility with JSON, APIs, and databases
- Cross-platform filename compatibility (Linux and Windows)
- Reduced risk of date/time parsing errors

## Considered Options

1. ISO 8601 (YYYY-MM-DD for dates, HH:mm:ss for times, with optional fractional seconds and timezone)
2. Unix timestamps (seconds since epoch)
3. Custom format (project-specific)
4. Platform-specific formats (varies by OS)

## Decision Outcome

Adopt **Option 1: ISO 8601 Standard Format** for all dates and times across the project, with specific rules for filenames to ensure cross-platform compatibility (Linux and Windows).

### Consequences

All existing dates and times must be migrated to ISO 8601 format. Code that parses or generates dates/times must be updated to enforce this standard. Validation rules should be implemented to prevent non-compliant formats from entering the system.

## Pros and Cons of the Options

### Option 1: ISO 8601 Standard Format

**Specification:**

#### Filename Format

When dates and times appear in filenames, use the following format to ensure cross-platform compatibility (Linux and Windows):

- **Date only:** `yyyy-MM-dd` (e.g., `2026-08-05`)
- **Time only:** `HH-mm-ss` (e.g., `14-30-45`)
- **Date and time combined:** `yyyy-MM-dd---HH-mm-ss` (e.g., `2026-08-05---14-30-45`)

**Invalid character replacement:** Any character that is invalid on either Linux or Windows filesystems must be replaced with a hyphen (`-`). This includes: `< > : " / \ | ? *` and control characters.

#### Standard Format (Non-Filename Contexts)

For all other contexts (code, APIs, documentation, ADR frontmatter):

- **Date only:** `YYYY-MM-DD` (e.g., `2026-08-05`)
- **Time only:** `HH:mm:ss` (e.g., `14:30:45`)
- **With fractional seconds:** `HH:mm:ss.fff` (e.g., `14:30:45.123`)
- **With timezone:** `HH:mm:ss±HHMM` or `HH:mm:ss.fff±HHMM` (e.g., `14:30:45+0200` or `14:30:45.123-0500`)
- **Date and time combined:** `YYYY-MM-DDTHH:mm:ss` (ISO 8601 extended format, e.g., `2026-08-05T14:30:45`)

**Pros:**
- International standard, widely recognized and supported
- Unambiguous and sortable
- Native support in most programming languages and databases
- Human-readable while remaining machine-parseable

**Cons:**
- Requires consistent enforcement across the codebase
- Existing data may need migration


### Option 2: Unix Timestamps

**Pros:**
- Compact representation
- Eliminates timezone ambiguity
- Efficient for calculations

**Cons:**
- Not human-readable
- Requires conversion for display
- Less suitable for filenames

### Option 3: Custom Project Format

**Pros:**
- Could be tailored to specific needs

**Cons:**
- Non-standard, increases learning curve
- Reduces interoperability
- Harder to integrate with external tools and libraries

