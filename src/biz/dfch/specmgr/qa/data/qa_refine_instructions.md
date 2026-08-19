You are refining an existing Question and Answer (QA) document by adding
new, currently-unanswered interview questions to it, identified by:
$id_or_name

Requested scope: $scope

Follow this sequence exactly. Do not write raw markdown yourself beyond
the body content you pass to `update_qa` -- every change to the document
goes through the specmgr MCP tools listed below.

Make a todo list and use the `question` tool whenever this prompt tells
you to -- do not guess when something is ambiguous.

## 1. Resolve the target document
Call the `list_qa` tool and find the one entry whose `id`
equals `$id_or_name` exactly, or -- if none does -- whose `title` best
matches it. If exactly one match is found, use its `id`. If none, or
more than one plausible match, is found, ask the user to disambiguate
with the `question` tool before proceeding -- never guess which document
was meant. Then call `get_qa(id)` to load the document's current
frontmatter and body. Never assume prior state -- the on-disk file is
always the source of truth and may have been hand-edited since you last
saw it.

## 2. Determine which characteristics and how many questions each
"Requested scope" above typically takes one of these shapes:
- A named subset with a shared count, e.g. "5 questions each about
  Functional Suitability, Security, Maintainability".
- All nine with a shared count, e.g. "3 questions for each of the 9
  main characteristics".
If the count, or the set of characteristics, is missing, unclear, or
says "(not given)", use the `question` tool to ask the user explicitly
for:
- how many new questions to add per characteristic (a number), and
- which of the nine ISO/IEC 25010:2023 characteristics to target --
  offer each of `Functional Suitability`, `Performance Efficiency`,
  `Compatibility`, `Interaction Capability`, `Reliability`, `Security`,
  `Maintainability`, `Flexibility`, `Safety` as its own selectable
  option (multi-select), plus an "all nine" shortcut.
Do not proceed to step 3 until both are unambiguous.

## 3. Look up each targeted characteristic's definition first
For every characteristic you are about to add questions to, fetch the
`specmgr://iso25010` resource and read that characteristic's (and,
where useful, its sub-characteristics') description before drafting any
question -- this keeps every question grounded in the actual ISO/IEC
25010:2023 definition rather than an assumed one. Do not invent
characteristic names beyond the nine returned by that resource, and do
not rename or reorder the document's own nine fixed `##` category
headings.

## 4. Draft the new questions
For each targeted characteristic, append the requested number of new
`### {question-ish heading}` Q&A pairs under that category's existing
`## {Characteristic}` heading (a free-form H3 per pair, phrased as a
genuine open question relevant to that characteristic's definition from
step 3). Each new pair consists of exactly:
- `> {the question}` as a block quote, and
- immediately below it, on its own line, the literal placeholder text
  `_(awaiting response)_` -- nothing else.
This placeholder is not the interviewee's answer -- it only marks where
a human will later type their actual answer directly into the document.
Do not add an HTML comment or a `#### Requirement` callout to these new
pairs: those are only ever added later, once an answer has actually been
given and a requirement can genuinely be derived from it. Never touch
any existing Q&A pair (question, comment, requirement, or answer) --
only append new pairs under the requested categories.

## 5. Whole-body replace
`update_qa` is a whole-body replace: carry forward every section of the
document exactly as read in step 1 (including all nine fixed category
headings, even ones you are not adding questions to this time, and every
existing Q&A pair within a category you *are* adding to), and only
append the new placeholder pairs from step 4. Call `update_qa(id,
content)` with the full resulting body markdown (no frontmatter block).

## 6. Report back, and point at the next step
Once `update_qa` succeeds, tell the user:
- exactly how many questions you added, and to which characteristic(s);
- that they should now open the document and answer each new question
  by replacing its `_(awaiting response)_` placeholder with their own
  answer, directly in the file;
- that once they are done answering, they should run the `/resolve`
  command to continue to the next step.
Do not attempt to run `/resolve` yourself -- it is a separate,
user-triggered step that happens after this prompt returns.
