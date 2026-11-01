"""Shared helpers for the throw-away ADR -> DEC migration scripts of feat-46.

Used by 100-110-survey-adrs.sh, 200-110-convert-adr.sh and 200-120-verify-converted.sh
(and, for the manifest, the 300-/400- scripts). Throw-away: removed together with the
migration; not shipped, not covered by the test suite.

The conversion rules implemented here are the rules of the "Convert an ADR to a DEC" SOP
(docs/sop/sop-81d73e92-...); this file is the mechanical form of that SOP, the SOP stays
the authority.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
FEAT_DIR = Path(__file__).resolve().parent.parent
MANIFEST = FEAT_DIR / "adr-manifest.json"

#: The one actor mapping rule: these `decision-makers` elements are not a role and map to the owner.
OWNER = "dfch"
NON_ROLE_ELEMENTS = {"user decision": OWNER}
KNOWN_ELEMENTS = {OWNER, "OpenCode agent"} | set(NON_ROLE_ELEMENTS)

PROS_ADR = "## Pros and Cons of the Options"
PROS_DEC = "## Pros and Cons"


def repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True)
    return Path(out.stdout.strip())


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], capture_output=True, text=True, check=True, cwd=repo_root())
    return out.stdout.strip()


def adr_files() -> list[Path]:
    return sorted(p for p in (repo_root() / "docs" / "adr").glob("*.md") if p.name != "README.md")


# --------------------------------------------------------------------------------------------
# reading
# --------------------------------------------------------------------------------------------


def split_document(text: str) -> tuple[dict, str]:
    match = re.match(r"---\n(.*?)\n---\n(.*)\Z", text, re.S)
    assert match, "no frontmatter block"
    return yaml.safe_load(match.group(1)), match.group(2)


def title_of(body: str) -> str:
    match = re.search(r"^# (.+)$", body, re.M)
    assert match, "no H1"
    return match.group(1).strip()


def h2_blocks(body: str) -> list[tuple[str, list[str]]]:
    """Split the body at top-level `## ` headings (fence aware). First block has heading ''."""
    blocks: list[tuple[str, list[str]]] = [("", [])]
    fence = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fence = not fence
        if line.startswith("## ") and not fence:
            blocks.append((line, [line]))
        else:
            blocks[-1][1].append(line)
    return blocks


def git_dates(path: Path) -> tuple[str, str]:
    """(created, updated) = first / last commit author date of the file, `.000` millis, offset kept."""
    rel = str(path.relative_to(repo_root()))
    first = git("log", "--follow", "--diff-filter=A", "--format=%aI", "--", rel).splitlines()[-1]
    last = git("log", "-1", "--format=%aI", "--", rel)
    return _millis(first), _millis(last)


def _millis(iso: str) -> str:
    return re.sub(r"(\d{2}:\d{2}:\d{2})(Z|[+-]\d{2}:\d{2})$", r"\1.000\2", iso)


def context_issue(body: str) -> list[str]:
    ctx = next((b for h, b in h2_blocks(body) if h == "## Context and Problem Statement"), [])
    seen: list[str] = []
    for num in re.findall(r"issue #(\d+)", "\n".join(ctx), re.I):
        if num not in seen:
            seen.append(num)
    return seen


# --------------------------------------------------------------------------------------------
# bare <token> wrapping (raw HTML is rejected in a DEC body)
# --------------------------------------------------------------------------------------------

_TOKEN = re.compile(r"<[A-Za-z_][\w-]*>")
_RUN = re.compile(r"[^\s`]*<[A-Za-z_][\w-]*>[^\s`]*")


def wrap_bare_tokens(body: str) -> tuple[str, list[str]]:
    """Wrap every whitespace-delimited run containing a bare `<tok>` in a code span.

    Fenced code blocks and existing inline code spans are left alone. Leading `(`/`[`/quote
    and trailing punctuation stay outside the span. Returns the new body and the list of the
    wrapped runs (in order), which the manifest records so the fidelity check can undo them.
    """
    wrapped: list[str] = []
    out: list[str] = []
    fence = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fence = not fence
            out.append(line)
            continue
        if fence or not _TOKEN.search(line):
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)  # odd indexes are code spans
        for i in range(0, len(parts), 2):
            parts[i] = _RUN.sub(lambda m: _wrap_run(m, wrapped), parts[i])
        out.append("".join(parts))
    return "\n".join(out), wrapped


def _wrap_run(match: re.Match, wrapped: list[str]) -> str:
    run = match.group(0)
    lead = re.match(r"^[(\[\"'*_]*", run).group(0)
    trail = re.search(r"[)\].,;:!?\"'*_]*$", run).group(0)
    core = run[len(lead) : len(run) - len(trail)]
    if not _TOKEN.search(core):  # punctuation swallowed the token; fall back to the token itself
        lead, trail, core = "", "", match.group(0)
    wrapped.append(core)
    return f"{lead}`{core}`{trail}"


def unwrap_runs(body: str, wrapped: list[str]) -> str:
    for core in wrapped:
        body = body.replace(f"`{core}`", core, 1)
    return body


# --------------------------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------------------------


def load_manifest() -> dict:
    assert MANIFEST.exists(), f"{MANIFEST} missing -- run 100-110-survey-adrs.sh --write first"
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def survey_entry(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    fm, body = split_document(text)
    uid = fm["id"]
    assert path.name.startswith(uid), f"{path.name}: frontmatter id {uid} differs from the file name"
    status = str(fm.get("status", "draft"))
    superseded_by = None
    if status.startswith("superseded by "):
        superseded_by = status.split()[-1]
        status = "superseded"
    makers = fm.get("decision-makers")
    defaults: list[str] = []
    if makers:
        elements = [e.strip() for e in str(makers).split(" + ")]
        responsible = [NON_ROLE_ELEMENTS.get(e, e) for e in elements]
        responsible = list(dict.fromkeys(responsible))
        unknown = [e for e in elements if e not in KNOWN_ELEMENTS]
    else:
        responsible, unknown = [OWNER], []
        defaults.append("decision-makers")
    issues = context_issue(body)
    if issues:
        source = f"GitHub issue #{issues[0]}"
    else:
        source = OWNER
        defaults.append("source")
    created, updated = git_dates(path)
    _, wrapped = wrap_bare_tokens(body)
    return {
        "id": uid,
        "stem": path.stem,
        "title": title_of(body),
        "status": status,
        "superseded_by": superseded_by,
        "supersedes": [],  # filled by the caller (reverse map)
        "adr_date": str(fm["date"]) if fm.get("date") else None,
        "decision_makers": makers,
        "accountable": OWNER,
        "responsible": responsible,
        "unknown_makers": unknown,
        "source": source,
        "source_issues": issues,
        "defaults": defaults,
        "created": created,
        "updated": updated,
        "wrapped_tokens": wrapped,
        "has_pros_heading": any(h == PROS_ADR for h, _ in h2_blocks(body)),
    }


# --------------------------------------------------------------------------------------------
# conversion
# --------------------------------------------------------------------------------------------


def convert(entry: dict, manifest: dict, adr_text: str) -> str:
    """Build the candidate DEC document text for one ADR (SOP Step 2 + Step 3)."""
    fm, body = split_document(adr_text)
    assert fm["id"] == entry["id"]
    body, wrapped = wrap_bare_tokens(body)
    assert wrapped == entry["wrapped_tokens"], "wrapped tokens differ from the manifest (stale manifest?)"
    lines = body.split("\n")

    # boundary: first `## ` after `## Decision Outcome` (fence aware), else end of body
    start = next(i for i, ln in enumerate(lines) if ln == "## Decision Outcome")
    fence, boundary = False, None
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("```"):
            fence = not fence
        if lines[i].startswith("## ") and not fence:
            boundary = i
            break
    eof = boundary is None
    if eof:
        boundary = len(lines) - 1 if lines and lines[-1] == "" else len(lines)

    ins: list[str] = ["## Roles and Responsibilities", "", "### Accountable", "", entry["accountable"], ""]
    ins += ["### Responsible", ""] + [f"- {name}" for name in entry["responsible"]] + [""]
    ins += ["## Source", "", entry["source"], ""]
    superseded = [manifest["adrs"][sid] for sid in entry["supersedes"]]
    if superseded:
        ins += ["## Related Artifacts", "", "### Decisions", ""]
        ins += [f"- DEC {old['id']}: {old['title']}" for old in superseded] + [""]

    before = lines[:boundary]
    while before and before[-1] == "":
        before.pop()
    rest = lines[boundary:]
    while rest and rest[-1] == "":
        rest.pop()
    new = before + [""] + ins
    if rest:
        new += rest + [""]
    new = [(PROS_DEC if ln == PROS_ADR else ln) for ln in new]
    new += [
        "## Updates",
        "",
        f"### {entry['updated']} - Converted from ADR",
        "",
        f'Converted from ADR {entry["id"]} per the "Convert an ADR to a DEC" SOP (GitHub issue #46).',
        "",
    ]
    frontmatter = (
        "---\nclassification: null\n"
        f"created: '{entry['created']}'\nid: {entry['id']}\nstatus: {entry['status']}\ntype: dec\n"
        f"updated: '{entry['updated']}'\nversion: 1.0.0\n---\n"
    )
    return frontmatter + "\n".join(new)


def unconvert(dec_text: str, entry: dict) -> str:
    """Undo the allowed transformations of `convert`, for the fidelity comparison."""
    _, body = split_document(dec_text)
    kept: list[str] = []
    skip = False
    fence = False
    for line in body.split("\n"):
        if line.startswith("```"):
            fence = not fence
        if line.startswith("## ") and not fence:
            skip = line in ("## Roles and Responsibilities", "## Source", "## Related Artifacts", "## Updates")
        if not skip:
            kept.append(line)
    text = "\n".join(kept)
    if entry["has_pros_heading"]:
        text = re.sub(r"^## Pros and Cons$", PROS_ADR, text, flags=re.M)
    return unwrap_runs(text, entry["wrapped_tokens"])


def normalise(text: str) -> str:
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip("\n")


def parse_error(dec_text: str) -> str | None:
    from biz.dfch.specmgr.dec.models.v1.parser import parse_dec

    try:
        parse_dec(dec_text)
    except Exception as exc:  # noqa: BLE001 - throw-away script, report anything
        return str(exc).splitlines()[0][:300] if str(exc) else repr(exc)
    return None


def classify(error: str | None) -> str:
    if error is None:
        return "clean"
    if "DecisionOutcome: text left over" in error:
        return "blocked-by-247"
    return "needs-judgment"


def die(message: str, code: int = 2) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


# --------------------------------------------------------------------------------------------
# reference scanning / retagging (300- scripts)
# --------------------------------------------------------------------------------------------

#: Tiers of tracked files, in retag order. A path falls in the first matching tier.
TIERS = {
    "G": "generated (regenerate instead of editing)",
    "A": "live artifacts (docs/**, feature READMEs, other markdown the tools read)",
    "B": "src and tests",
    "C": "prose (CHANGELOG.md, README.md, AGENTS.md, .opencode, conventions)",
    "D": "transcripts and other feature-folder sibling files",
}
_GENERATED = re.compile(r"^(docs/api/|docs/GENERATED\.md$|docs/MCP\.md$|docs/adr/README\.md$|docs/.*_schema\.json$)")


def tier_of(rel: str) -> str | None:
    """Tier letter of a tracked path, or None when excluded (the ADR sources, the feat-46 folder)."""
    if rel.startswith("docs/adr/") and rel != "docs/adr/README.md":
        return None
    if rel.startswith(".specmgr/feat/feat-46-remove-adr/"):
        return None
    if _GENERATED.match(rel) or rel.endswith((".json", ".lock")) and "schema" in rel:
        return "G"
    if rel.startswith(("src/", "tests/")):
        return "B"
    if rel in ("CHANGELOG.md", "README.md", "AGENTS.md") or rel.startswith((".opencode/", ".specmgr/conventions")):
        return "C"
    if re.match(r"^\.specmgr/feat/[^/]+/README\.md$", rel) or rel.startswith("docs/") and rel.endswith(".md"):
        return "A"
    if rel.startswith(".specmgr/"):
        return "D"
    return "C" if rel.endswith((".md", ".py", ".yaml", ".yml", ".toml")) else None


def tracked_text_files() -> list[tuple[str, str]]:
    root = repo_root()
    result = []
    for rel in git("ls-files").splitlines():
        tier = tier_of(rel)
        if tier is None:
            continue
        try:
            (root / rel).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        result.append((rel, tier))
    return result


def reference_patterns(tag_from: str, manifest: dict) -> dict[str, re.Pattern]:
    """The three citation shapes: full uuid, 8-hex short prefix, and a docs/adr/ path."""
    tag = re.escape(tag_from)
    return {
        "full": re.compile(rf"\b({tag})([ \t-]+)({UUID})", re.I),
        "short": re.compile(rf"\b({tag})([ \t-]+)([0-9a-f]{{8}})\b(?![-0-9a-f])", re.I),
        "path": re.compile(
            r"(docs/)adr(/)((?:" + "|".join(re.escape(e["stem"]) for e in manifest["adrs"].values()) + r")(?:\.md)?)"
        ),
    }


def short_map(manifest: dict) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for uid in manifest["adrs"]:
        result.setdefault(uid[:8], []).append(uid)
    return result


#: Lines containing this marker are provenance statements that must keep saying ADR.
KEEP_MARKER = "Converted from ADR"


def scan_refs(tag_from: str, manifest: dict, tiers: set[str]):
    """Yield one dict per citation: file, tier, line, kind (full/short/path), text, id, status.

    status: `retag` (id in the manifest, unambiguous), `foreign` (a uuid/prefix that is not a
    migrated ADR -- never touched), `ambiguous` (short prefix matching several ADRs), `keep`
    (provenance marker line), `manual` (generic docs/adr/ path cite without a file stem).
    """
    root = repo_root()
    patterns = reference_patterns(tag_from, manifest)
    smap = short_map(manifest)
    for rel, tier in tracked_text_files():
        if tier not in tiers:
            continue
        text = (root / rel).read_text(encoding="utf-8")
        for lineno, line in enumerate(text.split("\n"), 1):
            keep = KEEP_MARKER in line
            for m in patterns["full"].finditer(line):
                uid = m.group(3).lower()
                status = "keep" if keep else ("retag" if uid in manifest["adrs"] else "foreign")
                yield {
                    "file": rel,
                    "tier": tier,
                    "line": lineno,
                    "kind": "full",
                    "text": m.group(0),
                    "id": uid,
                    "status": status,
                }
            for m in patterns["short"].finditer(line):
                hits = smap.get(m.group(3).lower(), [])
                status = "keep" if keep else ("foreign" if not hits else "retag" if len(hits) == 1 else "ambiguous")
                yield {
                    "file": rel,
                    "tier": tier,
                    "line": lineno,
                    "kind": "short",
                    "text": m.group(0),
                    "id": hits[0] if len(hits) == 1 else m.group(3),
                    "status": status,
                }
            for m in patterns["path"].finditer(line):
                yield {
                    "file": rel,
                    "tier": tier,
                    "line": lineno,
                    "kind": "path",
                    "text": m.group(0),
                    "id": m.group(3),
                    "status": "keep" if keep else "retag",
                }
            if re.search(r"docs/adr/(?!README)", line) and not patterns["path"].search(line) and not keep:
                yield {
                    "file": rel,
                    "tier": tier,
                    "line": lineno,
                    "kind": "path",
                    "text": "docs/adr/...",
                    "id": "",
                    "status": "manual",
                }


def _case(tag: str, to: str) -> str:
    return to.upper() if tag.isupper() else to.lower() if tag.islower() else to.capitalize()


def retag_text(text: str, tag_from: str, tag_to: str, manifest: dict) -> tuple[str, int]:
    """Apply the three retag rules to one file's text; returns (new text, replacements)."""
    patterns = reference_patterns(tag_from, manifest)
    smap = short_map(manifest)
    count = 0
    out = []
    for line in text.split("\n"):
        if KEEP_MARKER in line:
            out.append(line)
            continue

        def full(m):
            nonlocal count
            if m.group(3).lower() not in manifest["adrs"]:
                return m.group(0)
            count += 1
            return f"{_case(m.group(1), tag_to)}{m.group(2)}{m.group(3)}"

        def short(m):
            nonlocal count
            if len(smap.get(m.group(3).lower(), [])) != 1:
                return m.group(0)
            count += 1
            return f"{_case(m.group(1), tag_to)}{m.group(2)}{m.group(3)}"

        def path(m):
            nonlocal count
            count += 1
            return f"{m.group(1)}dec{m.group(2)}{m.group(3)}"

        line = patterns["full"].sub(full, line)
        line = patterns["short"].sub(short, line)
        line = patterns["path"].sub(path, line)
        out.append(line)
    return "\n".join(out), count
