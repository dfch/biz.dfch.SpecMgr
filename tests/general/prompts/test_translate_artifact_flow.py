# Copyright (C) 2026 Ronald Rink, d-fens GmbH, http://d-fens.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""End-to-end proof of the deterministic surface the ``translate_artifact`` flow relies on (feat-197-i18n Phase 130).

The prompt (``general/data/general_translate_artifact_instructions.md``) narrates a flow around tools that already
exist; no LLM is involved in any of these tests. Instead they *simulate the flow's tool sequence* for a German
translation, with the "translation" itself supplied as literal German text (headings taken from the packaged
``de.json`` table, prose in German, every closed-vocabulary token left canonical -- exactly what the prompt tells the
agent to produce):

1. **Probe** the target (``get_<d>(id, raw=True, language="de")``): not-found => create; a document => update; a
   ``ParseFailureResult`` => stop.
2. **Create** the variant (``create_<d>(content, language="de", id=<EN id>)``) -- ACC-010: a new, schema-valid
   variant sharing the EN id and the EN basename, EN bytes untouched.
3. **Update** it (the generic ``update``/``edit`` with ``language="de"``).
4. **Verify** (``get_<d>(id, language="de")``) -- ACC-011: the variant parses to the same canonical *structure* as
   the EN document (skeleton equality, prose differing), and ACC-012: every closed-vocabulary token line is
   identical to the EN source.
5. A **negative matrix** proves the schema itself enforces REQ-010 -- translating a closed-vocabulary token (a VCR
   DTAIS method/coverage/``AC-NNN`` token, an RSK ``Probability``/``Impact`` heading or ``Strategy`` word, a REQ
   ``Level`` word, a PRB ``problem_statement``, a DEC ``Option N``/SOP ``Step N``/UC ``Extension`` heading token, a
   QA question prefix, a TSK checkbox marker) makes the write tool return the non-raising
   ``ValidateResult(valid=False)`` and write nothing -- which is what makes the prompt's bounded-retry-on-``ValidateResult``
   guidance meaningful (and why the never-translate list in ``specmgr://i18n`` may call those tokens schema-enforced).
"""

from __future__ import annotations

import re
import shutil
import unittest
from pathlib import Path
from typing import Any

from biz.dfch.specmgr.dec.tools._paths import DecNotFoundError
from biz.dfch.specmgr.dec.tools.create_dec import create_dec
from biz.dfch.specmgr.dec.tools.get_dec import get_dec
from biz.dfch.specmgr.general.models import ParseFailureResult, ValidateResult
from biz.dfch.specmgr.general.models.heading_table import load_heading_table
from biz.dfch.specmgr.general.tools.edit import edit
from biz.dfch.specmgr.general.tools.update import update
from biz.dfch.specmgr.vcr.tools._paths import VcrNotFoundError
from biz.dfch.specmgr.vcr.tools.create_vcr import create_vcr
from biz.dfch.specmgr.vcr.tools.get_vcr import get_vcr
from tests.general.tools.test_i18n_all_domains import SPECS, DomainSpec, _TempDocsMixin, translate_to_de

_SPEC = {spec.d: spec for spec in SPECS}

_DEC_EN = """# Use PostgreSQL as the primary store

## Context and Problem Statement

We need a durable store for order data.

## Considered Options

We compared PostgreSQL with a document database.

## Decision Outcome

We use PostgreSQL because it offers transactions.

### Consequences

Operations must run and monitor a database cluster.

## Roles and Responsibilities

### Accountable

The head of engineering.

### Responsible

- The platform team.

## Source

The architecture workshop of 2026-10-01.

## Pros and Cons

### Option 1: PostgreSQL

Mature and transactional.

### Option 2: Document database

Flexible schema, but weaker transactions.
"""

_DEC_DE = """# PostgreSQL als primären Speicher verwenden

## Kontext und Problembeschreibung

Wir brauchen einen dauerhaften Speicher für Bestelldaten.

## Betrachtete Optionen

Wir haben PostgreSQL mit einer Dokumentendatenbank verglichen.

## Entscheidungsergebnis

Wir verwenden PostgreSQL, weil es Transaktionen bietet.

### Folgen

Der Betrieb muss einen Datenbankcluster betreiben und überwachen.

## Rollen und Verantwortlichkeiten

### Endverantwortlich

Der Leiter der Entwicklung.

### Durchführend

- Das Plattformteam.

## Quelle

Der Architektur-Workshop vom 01.10.2026.

## Pro und Contra

### Option 1: PostgreSQL

Ausgereift und transaktional.

### Option 2: Dokumentendatenbank

Flexibles Schema, aber schwächere Transaktionen.
"""

_VCR_EN = """# Verification of order latency

## Verifies

REQ c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee: Order latency under load

This case checks that the order latency stays below the limit.

## Coverage

partial

## Acceptance Criteria

### AC-001 (Test): Latency stays below 200 ms

The p95 latency is measured under the nominal load.

#### Test Steps

1. Start the load generator with 100 users.
2. Read the p95 latency.

### AC-002 (Analysis): The capacity model confirms the headroom

The capacity model shows at least 30 percent headroom.
"""

_VCR_DE = """# Verifikation der Bestelllatenz

## Verifiziert

REQ c0ffeec0-ffee-ffee-ffee-c0ffeec0ffee: Order latency under load

Dieser Fall prüft, dass die Bestelllatenz unter dem Grenzwert bleibt.

## Abdeckung

partial

## Akzeptanzkriterien

### AC-001 (Test): Die Latenz bleibt unter 200 ms

Die p95-Latenz wird unter Nennlast gemessen.

#### Testschritte

1. Den Lastgenerator mit 100 Benutzern starten.
2. Die p95-Latenz ablesen.

### AC-002 (Analysis): Das Kapazitätsmodell bestätigt die Reserve

Das Kapazitätsmodell zeigt mindestens 30 Prozent Reserve.
"""

#: Closed-vocabulary / schema-constant token lines per domain (REQ-010): every one must be byte-identical in EN and DE.
_TOKEN_LINE = {
    "dec": re.compile(r"^### Option \d+:"),
    "vcr": re.compile(
        r"^(### AC-\d{3} \((Demonstration|Test|Analysis|Inspection|Special)\):|(full|partial|none)$|REQ )"
    ),
}


def _token_lines(domain: str, body: str) -> list[str]:
    """The closed-vocabulary token lines of ``body``, reduced to their token part (the heading's free text dropped)."""
    result: list[str] = []
    for line in body.splitlines():
        match = _TOKEN_LINE[domain].match(line)
        if match:
            result.append(match.group(0))
    return result


def _skeleton(value: Any, keep: set[str]) -> Any:
    """Reduce a ``model_dump`` to its canonical structure: dict keys, list shapes and numbers are kept; a string leaf is
    kept only when it is a canonical fixed heading or closed-vocabulary word (``keep``), else blanked (prose differs)."""
    if isinstance(value, dict):
        return {key: _skeleton(item, keep) for key, item in value.items()}
    if isinstance(value, list):
        return [_skeleton(item, keep) for item in value]
    if isinstance(value, str):
        return value if value in keep else ""
    return value


def _canonical_keep() -> set[str]:
    """The strings a skeleton keeps: every canonical fixed heading (the table's values) and the closed vocabulary."""
    result = set(load_heading_table("de").values())
    result |= {"full", "partial", "none", "Test", "Analysis"}
    return result


def _flow_probe(spec: DomainSpec, doc_id: str, language: str = "de") -> str:
    """The flow's step-4 probe: ``create`` (not-found), ``update`` (a document), or ``stop`` (a parse failure)."""
    try:
        probed = spec.fn("get")(doc_id, raw=True, language=language)
    except spec.not_found_error():
        return "create"
    if isinstance(probed, ParseFailureResult):
        return "stop"
    return "update"


class _FreshDocsMixin(_TempDocsMixin):
    """Adds :meth:`wipe`: an empty docs root and cold caches, so each sub-case of a matrix starts from scratch."""

    def wipe(self) -> None:
        for child in self.docs_root.iterdir():
            shutil.rmtree(child) if child.is_dir() else child.unlink()
        for spec in SPECS:
            spec.reset_cache()


class TestTranslateFlowCreatesAVariant(_FreshDocsMixin):
    """ACC-010/ACC-011/ACC-012 through the create path, for a dec and a closed-vocabulary-heavy vcr."""

    _CASES = (("dec", _DEC_EN, _DEC_DE), ("vcr", _VCR_EN, _VCR_DE))

    def test_the_flow_sequence_produces_a_schema_valid_variant_with_the_shared_id_and_basename(self):
        for domain, en_body, de_body in self._CASES:
            with self.subTest(domain=domain):
                spec = _SPEC[domain]
                self.wipe()
                created = spec.fn("create")(en_body)
                assert not isinstance(created, ValidateResult), created
                doc_id = created.id
                en_file = next(spec.base_dir().glob("*.md"))
                en_bytes = en_file.read_bytes()

                self.assertEqual(_flow_probe(spec, doc_id), "create")
                variant = spec.fn("create")(de_body, language="de", id=doc_id)

                # ACC-010: a new, schema-valid variant sharing the same id and the EN basename; EN untouched
                assert not isinstance(variant, ValidateResult), variant
                self.assertEqual(variant.id, doc_id)
                de_file = spec.base_dir("de") / en_file.name
                self.assertTrue(de_file.is_file())
                self.assertEqual(en_file.read_bytes(), en_bytes)
                self.assertEqual(_flow_probe(spec, doc_id), "update")
                self.assertEqual([p.name for p in spec.base_dir("de").glob("*.md")], [en_file.name])

                # the flow's verification step: a parsed document, not a failure result
                parsed_de = spec.fn("get")(doc_id, language="de")
                parsed_en = spec.fn("get")(doc_id)
                self.assertNotIsInstance(parsed_de, ParseFailureResult)
                self.assertEqual(parsed_de.frontmatter.id, parsed_en.frontmatter.id)
                self.assertEqual(parsed_de.frontmatter.type, domain)

                # the persisted text is exactly the translation (headings translated, tokens canonical)
                self.assertEqual(spec.fn("get")(doc_id, raw=True, language="de").rstrip("\n"), de_body.rstrip("\n"))

    def test_acc011_the_variant_parses_to_the_en_documents_canonical_structure(self):
        keep = _canonical_keep()
        for domain, en_body, de_body in self._CASES:
            with self.subTest(domain=domain):
                spec = _SPEC[domain]
                self.wipe()
                created = spec.fn("create")(en_body)
                assert not isinstance(created, ValidateResult), created
                spec.fn("create")(de_body, language="de", id=created.id)

                en_dump = spec.fn("get")(created.id).body.model_dump(mode="json")
                de_dump = spec.fn("get")(created.id, language="de").body.model_dump(mode="json")

                self.assertNotEqual(en_dump, de_dump, "the prose must really differ")
                self.assertEqual(_skeleton(de_dump, keep), _skeleton(en_dump, keep))
                # the very same Pydantic model class: the same schema as EN (REQ-004)
                self.assertIs(
                    type(spec.fn("get")(created.id, language="de").body), type(spec.fn("get")(created.id).body)
                )

    def test_acc012_closed_vocabulary_tokens_are_identical_to_the_en_source(self):
        for domain, en_body, de_body in self._CASES:
            with self.subTest(domain=domain):
                spec = _SPEC[domain]
                self.wipe()
                created = spec.fn("create")(en_body)
                assert not isinstance(created, ValidateResult), created
                spec.fn("create")(de_body, language="de", id=created.id)

                en_tokens = _token_lines(domain, spec.fn("get")(created.id, raw=True))
                de_tokens = _token_lines(domain, spec.fn("get")(created.id, raw=True, language="de"))

                self.assertTrue(en_tokens)
                self.assertEqual(de_tokens, en_tokens)
        # the parsed vcr tokens, by field
        spec = _SPEC["vcr"]
        spec.reset_cache()
        created = spec.fn("create")(_VCR_EN)
        spec.fn("create")(_VCR_DE, language="de", id=created.id)
        en_doc = spec.fn("get")(created.id).body
        de_doc = spec.fn("get")(created.id, language="de").body
        self.assertEqual(de_doc.coverage.value.text, en_doc.coverage.value.text)
        self.assertEqual(
            [(c.number, c.method) for c in de_doc.acceptance_criteria.criteria],
            [(c.number, c.method) for c in en_doc.acceptance_criteria.criteria],
        )
        self.assertEqual(de_doc.verifies.value.text, en_doc.verifies.value.text)

    def test_a_second_create_never_overwrites_so_the_flow_must_update_instead(self):
        spec = _SPEC["dec"]
        created = create_dec(_DEC_EN)
        create_dec(_DEC_DE, language="de", id=created.id)
        de_file = next(spec.base_dir("de").glob("*.md"))
        before = de_file.read_bytes()

        with self.assertRaises(FileExistsError):
            create_dec(_DEC_DE.replace("Wir", "Uns"), language="de", id=created.id)

        self.assertEqual(de_file.read_bytes(), before)

    def test_create_requires_the_en_source_and_a_heading_table(self):
        spec = _SPEC["dec"]
        with self.assertRaises(DecNotFoundError):
            create_dec(_DEC_DE, language="de", id="00000000-0000-4000-8000-000000000001")
        created = create_dec(_DEC_EN)
        with self.assertRaises(ValueError) as ctx:
            create_dec(_DEC_DE, language="fr", id=created.id)
        self.assertIn("no heading-mapping table", str(ctx.exception))
        self.assertEqual(list(spec.base_dir("fr").glob("*.md")) if spec.base_dir("fr").exists() else [], [])

    def test_the_flow_probe_reports_stop_for_an_unparseable_existing_variant(self):
        spec = _SPEC["dec"]
        created = create_dec(_DEC_EN)
        create_dec(_DEC_DE, language="de", id=created.id)
        de_file = next(spec.base_dir("de").glob("*.md"))
        de_file.write_text(
            de_file.read_text(encoding="utf-8").replace("\nstatus: draft\n", "\nstatus: bogus\n"), encoding="utf-8"
        )
        spec.reset_cache()

        self.assertEqual(_flow_probe(spec, created.id), "stop")
        self.assertIsInstance(get_dec(created.id, raw=True, language="de"), ParseFailureResult)

    def test_vcr_probe_not_found_error_is_the_domains_own(self):
        with self.assertRaises(VcrNotFoundError):
            get_vcr("00000000-0000-4000-8000-000000000002", raw=True, language="de")
        self.assertEqual(get_vcr.__name__, "get_vcr")
        self.assertEqual(create_vcr.__name__, "create_vcr")


class TestTranslateFlowUpdatesAVariant(_FreshDocsMixin):
    """The update path: whole-body ``update`` and surgical ``edit`` with ``language="de"``."""

    def _seed(self, spec: DomainSpec, en_body: str, de_body: str) -> tuple[str, Path, Path]:
        created = spec.fn("create")(en_body)
        assert not isinstance(created, ValidateResult), created
        spec.fn("create")(de_body, language="de", id=created.id)
        en_file = next(spec.base_dir().glob("*.md"))
        return created.id, en_file, spec.base_dir("de") / en_file.name

    def test_whole_body_update_rewrites_only_the_variant(self):
        for domain, en_body, de_body in ((("dec", _DEC_EN, _DEC_DE)), ("vcr", _VCR_EN, _VCR_DE)):
            with self.subTest(domain=domain):
                spec = _SPEC[domain]
                self.wipe()
                doc_id, en_file, de_file = self._seed(spec, en_body, de_body)
                en_bytes = en_file.read_bytes()
                revised = de_body.replace("Wir", "Unser Team").replace("Dieser Fall", "Dieser Testfall")
                self.assertNotEqual(revised, de_body)

                self.assertEqual(_flow_probe(spec, doc_id), "update")
                result = update(type=domain, id=doc_id, content=revised, language="de")

                self.assertNotIsInstance(result, (ValidateResult, ParseFailureResult), result)
                self.assertEqual(spec.fn("get")(doc_id, raw=True, language="de").rstrip("\n"), revised.rstrip("\n"))
                self.assertEqual(en_file.read_bytes(), en_bytes)  # the EN document, bytes and `updated`, is untouched
                self.assertEqual(spec.fn("get")(doc_id, language="de").frontmatter.id, doc_id)
                self.assertEqual([p.name for p in spec.base_dir("de").glob("*.md")], [en_file.name])
                self.assertEqual(_token_lines(domain, revised), _token_lines(domain, en_body))

    def test_surgical_edit_matches_the_translated_on_disk_text(self):
        spec = _SPEC["dec"]
        doc_id, en_file, _de_file = self._seed(spec, _DEC_EN, _DEC_DE)
        en_bytes = en_file.read_bytes()

        # old_str is matched against the TRANSLATED headings and prose as stored on disk
        result = edit(
            type="dec",
            id=doc_id,
            old_str="Das Plattformteam.",
            new_str="Das Plattform- und das Betriebsteam.",
            language="de",
        )

        self.assertNotIsInstance(result, (ValidateResult, ParseFailureResult), result)
        self.assertIn("Das Plattform- und das Betriebsteam.", get_dec(doc_id, raw=True, language="de"))
        self.assertEqual(en_file.read_bytes(), en_bytes)
        # an English old_str does not match the German variant (stage 1 is byte-exact)
        with self.assertRaises(ValueError):
            edit(type="dec", id=doc_id, old_str="The platform team.", new_str="x", language="de")

    def test_an_update_that_translates_a_token_returns_a_validate_result_and_changes_nothing(self):
        spec = _SPEC["vcr"]
        doc_id, _en_file, de_file = self._seed(spec, _VCR_EN, _VCR_DE)
        before = de_file.read_bytes()
        bad = _VCR_DE.replace("(Test)", "(Prüfung)")

        result = update(type="vcr", id=doc_id, content=bad, language="de")

        self.assertIsInstance(result, ValidateResult)
        self.assertFalse(result.valid)
        self.assertTrue(result.errors[0].message)
        self.assertEqual(de_file.read_bytes(), before)


#: (domain, label, transform applied to the DE-translated template body) -- each translates ONE closed-vocabulary /
#: schema-constant token and must be rejected by the unchanged schema.
_NEGATIVES: tuple[tuple[str, str, Any], ...] = (
    ("vcr", "DTAIS method word", lambda b: b.replace("(Test)", "(Prüfung)")),
    ("vcr", "Coverage word", lambda b: re.sub(r"(?m)^partial$", "teilweise", b)),
    ("vcr", "AC-NNN token", lambda b: b.replace("### AC-001 (", "### KK-001 (")),
    ("rsk", "Probability token", lambda b: b.replace("### Probability 3", "### Wahrscheinlichkeit 3", 1)),
    ("rsk", "Impact token", lambda b: b.replace("### Impact 3", "### Auswirkung 3", 1)),
    ("rsk", "Strategy word", lambda b: re.sub(r"(?m)^reduce$", "reduzieren", b)),
    ("req", "RFC 2119 Level word", lambda b: re.sub(r"(?m)^MUST$", "MUSS", b)),
    ("req", "Priority number", lambda b: re.sub(r"(?m)^50$", "fünfzig", b)),
    (
        "prb",
        "problem_statement lead paragraph",
        lambda b: b.replace(
            "The current process is causing delays, for users because of missing automation.",
            "Der aktuelle Prozess verursacht Verzögerungen für Nutzer wegen fehlender Automatisierung.",
        ),
    ),
    ("dec", "Option N token", lambda b: b.replace("### Option 1:", "### Möglichkeit 1:")),
    ("sop", "Step N token", lambda b: b.replace("### Step 1:", "### Schritt 1:")),
    ("uc", "Extension token", lambda b: b.replace("### Extension 1a.", "### Erweiterung 1a.")),
    ("qa", "question prefix", lambda b: b.replace("**1.0010**: ", "**Frage 1**: ")),
    ("tsk", "checkbox marker", lambda b: b.replace("- [x] ", "- [erledigt] ")),
)


class TestTranslatingAClosedVocabularyTokenIsRejectedBySchema(_FreshDocsMixin):
    """REQ-010/ACC-012: the schema itself enforces the never-translate list -- a translated token is a non-raising
    ``ValidateResult(valid=False)`` from the write tool and nothing is written; the untouched translation succeeds."""

    def test_every_listed_token_family_is_covered_by_a_negative_case(self):
        covered = {domain for domain, _label, _transform in _NEGATIVES}
        self.assertEqual(covered, {"vcr", "rsk", "req", "prb", "dec", "sop", "uc", "qa", "tsk"})

    def test_a_translated_token_is_rejected_on_create_and_the_correct_translation_is_accepted(self):
        for domain, label, transform in _NEGATIVES:
            with self.subTest(domain=domain, token=label):
                spec = _SPEC[domain]
                self.wipe()
                created = spec.fn("create")(spec.en_body())
                assert not isinstance(created, ValidateResult), created
                good = spec.de_body()
                bad = transform(good)
                self.assertNotEqual(bad, good, f"the transform for {label!r} changed nothing")

                rejected = spec.fn("create")(bad, language="de", id=created.id)

                self.assertIsInstance(rejected, ValidateResult)
                self.assertFalse(rejected.valid)
                self.assertEqual(len(rejected.errors), 1)
                self.assertTrue(rejected.errors[0].message)
                self.assertEqual(list(spec.base_dir("de").glob("*.md")) if spec.base_dir("de").exists() else [], [])

                accepted = spec.fn("create")(good, language="de", id=created.id)
                self.assertNotIsInstance(accepted, ValidateResult, accepted)
                self.assertEqual(accepted.id, created.id)

    def test_the_same_translated_token_is_rejected_by_update_and_leaves_the_variant_unchanged(self):
        for domain, label, transform in _NEGATIVES:
            with self.subTest(domain=domain, token=label):
                spec = _SPEC[domain]
                self.wipe()
                created = spec.fn("create")(spec.en_body())
                assert not isinstance(created, ValidateResult), created
                good = spec.de_body()
                spec.fn("create")(good, language="de", id=created.id)
                de_file = next(spec.base_dir("de").glob("*.md"))
                before = de_file.read_bytes()

                rejected = update(type=domain, id=created.id, content=transform(good), language="de")

                self.assertIsInstance(rejected, ValidateResult)
                self.assertFalse(rejected.valid)
                self.assertEqual(de_file.read_bytes(), before)

    def test_translating_headings_through_the_table_alone_never_trips_the_schema(self):
        """The control: ``translate_to_de`` (table headings only, prose and tokens untouched) is valid for all domains."""
        for spec in SPECS:
            with self.subTest(domain=spec.d):
                self.wipe()
                created = spec.fn("create")(spec.en_body())
                assert not isinstance(created, ValidateResult), created
                self.assertNotEqual(translate_to_de(spec.en_body()), spec.en_body())

                variant = spec.fn("create")(translate_to_de(spec.en_body()), language="de", id=created.id)

                self.assertNotIsInstance(variant, ValidateResult, variant)
                self.assertEqual(variant.id, created.id)


if __name__ == "__main__":
    unittest.main()
