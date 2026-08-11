# PlantUML Compatibility Analysis: Cockburn vs Larman vs Hybrid

## Key Findings

### PlantUML Use Case Diagrams Support

**What PlantUML can render:**
- Actors (with multiple style options: stick, awesome, hollow)
- Use cases (ovals with text)
- Relationships: basic association (`-->`), include (`.>`), extend (`<|--`)
- Packages/rectangles for grouping
- Notes attached to elements
- Stereotypes (`<<label>>`) for styling
- Colors and inline styling
- Direction control (left-to-right, top-to-bottom)

**What PlantUML CANNOT easily express:**
- Preconditions, postconditions, minimal guarantees (needs notes)
- Stakeholder interests (needs notes)
- Technology variations (needs notes)
- Goal levels and scope icons (can use stereotypes)
- Detailed step-by-step flows

### PlantUML Activity Diagrams Support

**What PlantUML can render:**
- Linear actions/activities (rectangles)
- Branching (if/then/else with conditions on arrows)
- Parallel actions (synchronization bars `===`)
- Partitions (swimlanes for different actors/systems)
- Arrows with labels
- Notes on activities
- Complex nested flows

**Perfect for:**
- Main Success Scenario (linear flow)
- Extensions with conditions (branching)
- System vs. Actor interactions (swimlanes)

**NOT ideal for:**
- Preconditions/postconditions (not built-in; must use notes)
- Stakeholder information (no native support)

---

## Recommendation: Use **Larman Style (List-Based) + Custom Metadata**

Here's why:

| Criterion | Cockburn | Larman (Original) | Larman + Metadata (Recommended) |
|-----------|----------|-------------------|--------------------------------|
| **PlantUML Use Case Diagram** | Medium (text-to-diagram conversion complex) | **Easy** (actors & use cases already separated) | **Easy** (same basis) |
| **PlantUML Activity Diagram** | Medium (narrative steps need parsing) | **Better** (natural sentences name actors directly for swimlanes) | **Better** (metadata adds flow structure) |
| **Preconditions/Postconditions** | Native support | None | Add as metadata sections |
| **Stakeholder tracking** | Native support | None | Add as metadata sections |
| **Scannability** | Good | **Best** (list format, easy to scan) | **Best** (same + metadata) |
| **LLM Editability** | Good | **Best** (no table alignment) | **Best** (lists are easy to append to) |
| **Append-ability** | Hard (table re-formatting) | **Easy** (just add a line) | **Easy** (just add a line) |

---

## Proposed Hybrid Schema

**Start with Larman's list-based format** (easy to parse for PlantUML diagrams), then **add structured sections** for metadata needed by other diagrams:

```markdown
# Use Case: Edit an Article

**Actors**: Member  
**Scope**: Wiki System  
**Type**: Primary  
**Level**: User Goal (!)  

## Overview
The member edits an article, with ability to preview and compare versions before saving.

## Metadata

**Goal in Context**: The member wants to modify article content efficiently and review changes before committing.

**Stakeholders**:
- Member: wants to edit and preview efficiently
- System Administrator: wants to log all edits for audit
- Other Wiki Members: want to be notified of changes

**Preconditions**:
- Member is authenticated and logged in
- Article with editing enabled is displayed

**Trigger**: Member clicks "Edit" button on the article

**Success Guarantees**:
- Article is saved with member's changes
- Updated article view is displayed
- Edit record created for notifications

## Main Success Scenario

1. Member clicks the "Edit" button.
2. System displays the editor area with the article's current content.
3. Member optionally selects a specific section to edit.
4. System pre-fills the section title in the edit summary.
5. Member modifies the article content as needed.
6. Member fills in the edit summary and clicks "Submit".
7. System validates the content.
8. System saves the article, logs the edit event, and notifies watchers.
9. System displays the updated article view to the member.

## Alternative Flows

### 5a. Preview Changes
**Trigger**: After step 5 → Member clicks "Show Preview"

**Flow**:
- System displays original content, member's changes, and rendered preview
- System shows message: "Changes have not yet been saved"
- Member can continue editing (return to step 5) or proceed (continue to step 6)

### 5b. Conflict Detected
**Trigger**: During step 7 → Another member has edited the article

**Flow**:
- System alerts: "Conflict: another member edited this article"
- System offers: Review changes | Merge manually | Discard and restart
- If Merge: return to step 5 with new baseline
- If Discard: use case ends

## Technology Variations
- Editor: WYSIWYG vs. plain text vs. mobile-optimized
- Conflict resolution: 3-way merge vs. last-write-wins vs. operational transformation
- Notifications: Email vs. in-app vs. both
```

---

## Code Generation Path

### For Use Case Diagram
Extract:
1. **Actors**: Parse `**Actors**:` field
2. **Use Cases**: Extract from title + related alternatives
3. **Relationships**: 
   - Basic association: actor interacts with main use case
   - Include: parse "Alternative Flows" that are sub-flows
   - Extend: parse "Alternative Flows" that are conditional branches

```plantuml
left to right direction
actor Member
actor "System Admin" as Admin
usecase "Edit an Article" as UC1
usecase "Preview Changes" as UC2
usecase "Resolve Conflict" as UC3

Member --> UC1
UC1 .> UC2 : include
UC1 .> UC3 : extend
Admin --> UC1
```

### For Activity Diagram
Extract:
1. **Main flow**: Parse table rows as sequence of actions
2. **Actor/System columns**: Create swimlanes (partitions)
3. **Alternative flows**: Convert to decision branches (if/then)
4. **Step references** (3a, 3b): Create conditional paths

```plantuml
partition Member
  (*) --> "Click Edit"
end

partition System
  --> "Display Editor"
end

partition Member
  --> "Modify Content" as content
  --> {decision} preview?
end

partition System
  preview? ---> [yes] "Show Preview"
  "Show Preview" ---> content
  preview? --> [no] "Validate"
end
```

---

## Summary

**Recommend: Larman list-based format + custom metadata**

- ✅ Easiest to parse for both diagram types
- ✅ Compact and scannable — no table alignment overhead
- ✅ Natural sentences name actors directly (perfect for swimlane extraction)
- ✅ Each step is a simple numbered item — easy to append new steps
- ✅ Metadata sections capture Cockburn rigor without overhead
- ✅ PlantUML-friendly design (actors, use cases, flows are first-class)
- ✅ No markdown table formatting friction for LLMs or humans
