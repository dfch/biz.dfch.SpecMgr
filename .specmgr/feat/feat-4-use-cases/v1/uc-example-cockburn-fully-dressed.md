# Use Case: Edit an Article

## Design Scope
🔲 System (black-box)

## Goal Level
! User Goal

---

## Primary Actor
Member (Registered User)

## Scope
A Wiki system

---

## Goal in Context
The member wants to modify the content of an article they are reading, including previewing changes and comparing versions before committing.

## Stakeholders and Interests
- **Member**: wants to make updates efficiently, with ability to preview
- **System Administrator**: wants to log all edits for audit and notification purposes
- **Other Wiki Members**: want to be notified of changes to articles they follow

---

## Preconditions
- The member is authenticated and logged in
- The article with editing enabled is presented to the member
- The article exists in the system

## Minimal Guarantees
- The system maintains an audit trail of the edit attempt (even if cancelled)
- No data is saved if the member cancels the edit

## Success Guarantees
- The article is saved with the member's changes
- An updated view of the article is displayed to the member
- An edit record is created, enabling watchers to be notified
- The member's edit summary is stored with the change

---

## Trigger
The member invokes an edit request (for the full article or just one section) on the article by clicking an "Edit" button.

---

## Main Success Scenario

1. The system provides an editor area filled with the article's current content
2. If the member is editing just a section, only that section's content is shown, with the section title pre-filled in the edit summary
3. The member modifies the article's content as needed
4. The member fills out an edit summary describing their changes
5. The member optionally selects "Watch this article" if they want notifications of future changes
6. The member clicks Submit
7. The system validates the changes (checks for conflicts, ensures content is not empty)
8. The system saves the article, logs the edit event, and processes notifications
9. The system displays the updated article view to the member

---

## Extensions

### 2a. Section editing
- The member selects a specific section to edit
- The system displays only that section's content in the editor
- Continue at step 3

### 3a. Preview changes
- The member clicks "Show Preview" to see rendered output
- The system displays: the original content, the member's changes, and a preview of the rendered result
- The system informs the member that changes are **not yet saved**
- The member returns to step 3 to continue editing or proceed to step 4

### 3b. Compare with previous version
- The member clicks "Show Changes" to see differences
- The system displays a side-by-side or inline comparison between:
  - The most recent saved version
  - The member's current edits
- The member returns to step 3 to continue editing or proceed to step 4

### 3c. Cancel the edit
- The member clicks "Cancel"
- The system discards all changes without saving
- The system redisplays the original article view
- Use case ends

### 4a. Edit summary is empty
- The member attempts to submit without filling the edit summary
- The system displays an error: "Edit summary is required"
- The system returns to step 4, with the member's content preserved
- The member fills in the summary and continues

### 7a. Edit conflict detected
- The system detects that another member has saved changes to this article since the member began editing
- The system alerts the member to the conflict
- The system offers options:
  - Review the other member's changes
  - Merge changes manually
  - Discard own changes and start fresh
- If merge is chosen, continue at step 3
- If discard is chosen, end use case

### 7b. Content validation fails
- The system detects invalid content (e.g., broken links, malformed markup)
- The system displays validation warnings and highlights the problematic sections
- The member may choose to:
  - Fix the issues (continue at step 3)
  - Save anyway (accept warnings and continue at step 8)
  - Cancel (3c)

### 8a. System timeout during save
- The save operation times out due to system load
- The system displays a timeout error
- The system offers the member the option to:
  - Copy their edits to clipboard
  - Retry the save
  - Abandon the edit

---

## Technology & Data Variations List

### Data Variations
- **Article Content**: Plain text, wikitext markup, or rich HTML depending on system configuration
- **Edit Summary**: Free-form text (e.g., "Fixed typo", "Added references", "Updated contact info")
- **Watch List**: Member may or may not have the watch feature enabled in their profile settings

### Technology Variations
- **Editor Interface**: 
  - Web-based rich text editor (WYSIWYG)
  - Plain text editor with syntax highlighting
  - Mobile-optimized editor with simplified toolbar
- **Conflict Resolution**:
  - Three-way merge (original, their version, other member's version)
  - Last-write-wins with manual conflict notification
  - Operational transformation for real-time collaboration
- **Notification**:
  - Email to watchers
  - In-app notifications
  - Both
