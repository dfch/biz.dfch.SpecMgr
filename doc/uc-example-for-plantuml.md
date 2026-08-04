# Use Case: Edit an Article

**Actors**: Member  
**Scope**: Wiki System  
**Type**: Primary  
**Level**: User Goal (!)  

---

## Overview
The member edits any part of an article (full or section-only), with ability to preview changes and compare versions before saving.

---

## Metadata

**Goal in Context**: The member wants to modify article content efficiently and review changes before committing them.

**Stakeholders**:
- **Member**: wants to edit and preview efficiently
- **System Administrator**: wants to log all edits for audit
- **Other Wiki Members**: want to be notified of changes

**Preconditions**:
- Member is authenticated and logged in
- Article with editing enabled is displayed

**Trigger**: 
Member clicks "Edit" button on the article

**Success Guarantees**:
- Article is saved with member's changes
- Updated article view is displayed
- Edit record created for notifications
- Edit summary stored with change

---

## Main Success Scenario

1. Member clicks the "Edit" button.
2. System displays the editor area with the article's current content.
3. Member optionally selects a specific section to edit.
4. System pre-fills the section title in the edit summary field.
5. Member modifies the article content as needed.
6. Member fills in the edit summary field describing the changes.
7. Member optionally checks "Watch this article" to receive notifications of future changes.
8. Member clicks the "Submit" button.
9. System validates the content (checks for conflicts, ensures content is not empty).
10. System saves the article, logs the edit event, and processes notifications to watchers.
11. System displays the updated article view to the member.

---

## Alternative Flows

### 5a. Preview Changes
**Trigger**: After step 5 → Member clicks "Show Preview"

**Flow**:
- System displays the original content, member's changes, and a rendered preview side-by-side.
- System shows message: "Changes have not yet been saved."
- Member can continue editing (return to step 5) or proceed with submission (continue to step 6).

### 5b. Compare with Previous Version
**Trigger**: After step 5 → Member clicks "Show Changes"

**Flow**:
- System displays a side-by-side comparison between the currently saved version and the member's edits.
- Member can continue editing (return to step 5) or proceed with submission (continue to step 6).

### 5c. Cancel Edit
**Trigger**: After step 5 → Member clicks "Cancel"

**Flow**:
- System discards all unsaved changes.
- System redisplays the original article view.
- **Use case ends.**

### 6a. Edit Summary Empty
**Trigger**: After step 9 → Validation fails because the edit summary field is blank.

**Flow**:
- System displays an error message: "Edit summary is required."
- Member's content is preserved in the editor.
- Member fills in the edit summary (return to step 6).

### 9a. Edit Conflict Detected
**Trigger**: After step 9 → Another member has edited the article since this member began editing.

**Flow**:
- System displays an alert: "Conflict detected: another member has edited this article while you were editing."
- System offers options: Review other member's changes | Merge changes manually | Discard own changes and restart.
- **If Merge is chosen**: Return to step 5 (continue editing with the other member's changes as the new baseline).
- **If Discard is chosen**: Use case ends.

### 9b. Content Validation Fails
**Trigger**: After step 9 → Content contains invalid markup or broken links.

**Flow**:
- System displays validation warnings with highlighted sections indicating problems.
- Member can choose to: Fix the issues (return to step 5) | Save anyway and accept the warnings (continue to step 10) | Cancel the edit (5c).

### 10a. System Timeout During Save
**Trigger**: During step 10 → The save operation times out due to system load or network issues.

**Flow**:
- System displays a timeout error message.
- Member can choose to: Copy edits to clipboard | Retry the save operation | Abandon the edit

---

## Technology & Data Variations

**Editor Interface**:
- Web-based WYSIWYG editor
- Plain text editor with syntax highlighting
- Mobile-optimized simplified editor

**Conflict Resolution Strategy**:
- Three-way merge (original, member's version, other member's version)
- Last-write-wins with notification
- Operational transformation (real-time collaboration)

**Notification System**:
- Email to watchers
- In-app notifications
- Both

**Article Format**:
- Plain text
- Markdown
- Wikitext markup
- Rich HTML
