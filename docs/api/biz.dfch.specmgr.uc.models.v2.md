# `biz.dfch.specmgr.uc.models.v2`

Use Case models v2 -- rebuilt on `feat-5-md-model-parser`'s generic `models/md` engine.

See `.specmgr/feat/feat-4-use-cases/uc_model_v2_draft.py` for the design sketch this
package implements, and `uc/models/v1/` for the original custom-parser
implementation this package supersedes. `parse_uc` (Task 1.8) is the
`UcDocument`-level `from_text` entry point; `render_uc_diagram` (Task 2.1's
v1 equivalent) is ported in `uc/models/v2/renderer.py` (feat-185-uc-diagrams,
Phase 110) -- alongside the rulebook's package-diagram and sequence-skeleton
renderers (`render_use_case_package` / `render_uc_sequence_skeleton`), all
deterministic over their parsed-model inputs, the normative spec being the
frozen rulebook `specmgr://uc/plantuml` (`uc/data/uc_plantuml.md`).
