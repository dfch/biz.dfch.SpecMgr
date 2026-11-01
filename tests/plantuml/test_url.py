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
# along with this program.
#
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for `plantuml.url` (the single-endpoint matrix classifier, rulebook §5).

Offline against the recorded byte fixtures (`tests/fixtures/plantuml/` —
provenance in that folder's README): the classification matrix is asserted on
body SIGNATURES (the placeholder / bad-URL markers, the `<svg` prefix), never
on sizes. The retry behaviour and the never-INVALID guarantee use a mocked
transport. The env-gated live tests run only when the selected source is an
available URL backend.
"""

import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.plantuml import backends, url
from tests.conftest import assert_rendered_svg, require_plantuml_source

_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "plantuml"


def _body(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


class TestClassifyResponse(unittest.TestCase):
    """The frozen matrix (rulebook §5.2) over the recorded byte fixtures."""

    def test_200_real_svg_is_valid(self):
        for name in ("jetty_real_svg.svg", "public_real_svg.svg"):
            with self.subTest(name=name):
                self.assertEqual(url.classify_response(200, _body(name)), url.CLASS_VALID)

    def test_200_crash_page_is_the_recognised_crash_line(self):
        """The recorded REAL jetty crash page (2026-10-06) is the recognised INVALID
        crash line — not VALID (the pre-amendment misread) and not unrecognised."""
        crash = _body("jetty_crash_svg.svg")

        self.assertEqual(url.classify_response(200, crash), url.CLASS_CRASH)
        self.assertFalse(url.is_real_svg(crash))
        self.assertEqual(backends.scan_crash(crash), "java.lang.ClassCastException")

    def test_200_crash_page_only_is_the_crash_line(self):
        """The crash line is the 200 row: any other status with a crash body is
        unrecognised (INCONCLUSIVE, never INVALID — the preamble holds)."""
        crash = _body("jetty_crash_svg.svg")

        for status in (None, 400, 404, 500):
            with self.subTest(status=status):
                self.assertEqual(url.classify_response(status, crash), url.CLASS_INCONCLUSIVE)

    def test_400_placeholder_is_invalid(self):
        for name in ("jetty_400_placeholder.svg", "public_400_placeholder.svg"):
            with self.subTest(name=name):
                self.assertEqual(url.classify_response(400, _body(name)), url.CLASS_INVALID)

    def test_200_placeholder_is_request_error(self):
        self.assertEqual(url.classify_response(200, _body("jetty_200_placeholder.svg")), url.CLASS_REQUEST_ERROR)

    def test_200_bad_url_is_encode_error(self):
        self.assertEqual(url.classify_response(200, _body("public_badurl_200.svg")), url.CLASS_ENCODE_ERROR)

    def test_unknown_combinations_are_inconclusive_never_invalid(self):
        cases = [
            (None, b""),  # transport failure (timeout / refused / DNS)
            (500, b"internal"),
            (509, b""),  # the public server's bandwidth-limit status (observed 2026-10-03)
            (404, b"not here"),
            (400, b"no placeholder marker"),  # 400 WITHOUT the welcome marker
            (200, b"plain text, not even svg"),
            (301, b""),
            (204, b""),
        ]
        for status, body in cases:
            with self.subTest(status=status, size=len(body)):
                self.assertEqual(url.classify_response(status, body), url.CLASS_INCONCLUSIVE)

    def test_real_svg_marker_distinguishes_the_placeholders_and_the_crash_page(self):
        real = _body("jetty_real_svg.svg")
        placeholder = _body("jetty_200_placeholder.svg")
        bad_url = _body("public_badurl_200.svg")
        crash = _body("jetty_crash_svg.svg")

        self.assertTrue(url.is_real_svg(real))
        self.assertFalse(url.is_real_svg(placeholder))
        self.assertFalse(url.is_real_svg(bad_url))
        self.assertFalse(url.is_real_svg(crash))  # the pre-amendment misread, pinned closed
        self.assertIn(url.PLACEHOLDER_MARKER, placeholder)
        self.assertIn(url.BAD_URL_MARKER, bad_url)
        self.assertIn(url.PLACEHOLDER_MARKER, _body("jetty_400_placeholder.svg"))
        self.assertIn(b"has crashed", crash)

    def test_aass_400_placeholder_stays_the_plain_syntax_invalid(self):
        """No-regression pin (2026-10-06): the canonical `aass` fixture is still the plain
        SYNTAX INVALID row — the new crash line must not absorb it (its body is the welcome
        placeholder, not a crash page)."""
        aass = _body("jetty_400_placeholder.svg")

        self.assertIsNone(backends.scan_crash(aass))
        self.assertEqual(url.classify_response(400, aass), url.CLASS_INVALID)


class TestSvgUrl(unittest.TestCase):
    """The single endpoint shape (rulebook §5.1)."""

    def test_endpoint_is_svg_with_the_classic_payload(self):
        from biz.dfch.specmgr.plantuml.encode import encode_puml

        result = url.svg_url("http://localhost:8080", "diagram")

        self.assertEqual(result, f"http://localhost:8080/svg/{encode_puml('diagram')}")

    def test_trailing_slash_on_the_base_is_collapsed(self):
        from biz.dfch.specmgr.plantuml.encode import encode_puml

        result = url.svg_url("https://www.plantuml.com/plantuml/", "diagram")

        self.assertEqual(result, f"https://www.plantuml.com/plantuml/svg/{encode_puml('diagram')}")


class TestValidateUrlMocked(unittest.TestCase):
    """The verdict mapping + the one INCONCLUSIVE retry (mocked transport, offline)."""

    def test_valid_writes_the_svg_body_to_a_temp_file(self):
        body = _body("jetty_real_svg.svg")
        with mock.patch.object(url, "fetch_svg", return_value=url.UrlResponse(status=200, body=body)):
            verdict = url.validate_url("http://x", "diagram")

        self.assertIs(verdict.valid, True)
        self.assertIs(verdict.rendered, True)
        self.assertEqual(verdict.source_state, "ok")
        self.assertIsNotNone(verdict.proof_path)
        assert verdict.proof_path is not None
        with open(verdict.proof_path, "rb") as handle:
            self.assertEqual(handle.read(), body)

    def test_invalid_maps_to_valid_false_with_one_finding(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=400, body=_body("jetty_400_placeholder.svg"))
        ):
            verdict = url.validate_url("http://x", "diagram")

        self.assertIs(verdict.valid, False)
        self.assertIsNone(verdict.rendered)
        self.assertIsNotNone(verdict.errors)
        assert verdict.errors is not None
        self.assertEqual(len(verdict.errors), 1)
        self.assertIn("syntax error", verdict.errors[0].message)
        self.assertEqual(verdict.classification, url.CLASS_INVALID)
        self.assertNotIn("crash", verdict.errors[0].message)  # the plain syntax row, not the crash line

    def test_crash_page_maps_to_valid_false_with_the_crash_finding(self):
        """The §5.2 crash line (amended 2026-10-06): INVALID with a crash diagnostic —
        the line-0 finding carries the crash exception class, the fix_hint names the
        known 1.2026.8 shape bug and points at §2.9's anchored notes."""
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("jetty_crash_svg.svg"))
        ):
            verdict = url.validate_url("http://x", "diagram")

        self.assertEqual(verdict.classification, url.CLASS_CRASH)
        self.assertIs(verdict.valid, False)
        self.assertIsNone(verdict.rendered)
        self.assertIsNotNone(verdict.errors)
        assert verdict.errors is not None
        self.assertEqual(len(verdict.errors), 1)
        self.assertEqual(verdict.errors[0].line, 0)
        self.assertIn("java.lang.ClassCastException", verdict.errors[0].message)
        self.assertIn("crashed", verdict.errors[0].message)
        self.assertIn("note left of", verdict.errors[0].fix_hint)
        self.assertIn("§2.9", verdict.errors[0].fix_hint)

    def test_request_error_is_never_invalid(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("jetty_200_placeholder.svg"))
        ):
            verdict = url.validate_url("http://x", "diagram")

        self.assertIsNone(verdict.valid)
        self.assertIsNone(verdict.rendered)
        self.assertEqual(verdict.classification, url.CLASS_REQUEST_ERROR)
        self.assertIsNotNone(verdict.reason)
        self.assertIsNotNone(verdict.fix_hint)

    def test_encode_error_is_never_invalid(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("public_badurl_200.svg"))
        ):
            verdict = url.validate_url("http://x", "diagram")

        self.assertIsNone(verdict.valid)
        self.assertEqual(verdict.classification, url.CLASS_ENCODE_ERROR)
        self.assertIn("client/transport defect", verdict.reason or "")

    def test_inconclusive_retries_exactly_once_then_reports_source_state(self):
        inconclusive = url.UrlResponse(status=500, body=b"nope")
        with mock.patch.object(url, "fetch_svg", return_value=inconclusive) as fetch:
            verdict = url.validate_url("http://x", "diagram")

        self.assertEqual(fetch.call_count, 2)  # the original call + exactly one retry
        self.assertIsNone(verdict.valid)
        self.assertEqual(verdict.source_state, "inconclusive")
        self.assertEqual(verdict.classification, url.CLASS_INCONCLUSIVE)
        self.assertIsNotNone(verdict.reason)

    def test_persistent_inconclusive_hint_names_the_dialect_limitation(self):
        """The 2026-10-08 amended hint (the CLASSIFICATION is frozen — only the hint text
        moved): under a URL source, a line-level syntax error from line 3 onward surfaces
        as inconclusive (the deployment's minimal-400 dialect carries no line detail —
        rulebook §5.2 drift note (e)); retrying cannot fix that, so the hint names the
        limitation and the remedy (a local source carries the parser's own line)."""
        # the minimal-400 dialect: a 400 WITHOUT the placeholder marker — the
        # frozen matrix classifies it INCONCLUSIVE (never INVALID)
        inconclusive = url.UrlResponse(status=400, body=b"[From string (line 3)] ... Syntax Error?")
        with mock.patch.object(url, "fetch_svg", return_value=inconclusive):
            verdict = url.validate_url("http://x", "diagram")

        self.assertEqual(verdict.classification, url.CLASS_INCONCLUSIVE)
        self.assertIsNone(verdict.valid)  # the frozen classification — unchanged
        self.assertIn("drift note (e)", verdict.fix_hint or "")
        self.assertIn("line 3 onward", verdict.fix_hint or "")
        self.assertIn("SPECMGR_PLANTUML_JAR", verdict.fix_hint or "")
        self.assertIn("SPECMGR_PLANTUML_BIN", verdict.fix_hint or "")

    def test_transport_failure_inconclusive_keeps_the_retry_hint(self):
        """The transport-failure branch is a genuine transient — the amended dialect note
        (line-3+ syntax errors) does not apply to it; the original retry hint stands."""
        inconclusive = url.UrlResponse(status=None, body=b"", transport_error="ConnectionRefusedError: [Errno 111]")
        with mock.patch.object(url, "fetch_svg", return_value=inconclusive):
            verdict = url.validate_url("http://x", "diagram")

        self.assertEqual(verdict.classification, url.CLASS_INCONCLUSIVE)
        self.assertIn("retry later", verdict.fix_hint or "")
        self.assertNotIn("drift note (e)", verdict.fix_hint or "")

    def test_inconclusive_retry_that_recovers_is_valid(self):
        first = url.UrlResponse(status=None, body=b"", transport_error="timeout")
        second = url.UrlResponse(status=200, body=_body("jetty_real_svg.svg"))
        with mock.patch.object(url, "fetch_svg", side_effect=[first, second]) as fetch:
            verdict = url.validate_url("http://x", "diagram", write_proof=False)

        self.assertEqual(fetch.call_count, 2)
        self.assertIs(verdict.valid, True)
        self.assertIs(verdict.rendered, True)


class TestProbeUrlMocked(unittest.TestCase):
    """The canary probe (mocked transport, offline)."""

    def setUp(self):
        url.clear_probe_cache()

    def test_malformed_base_url_is_misconfigured_without_network(self):
        with mock.patch.object(url, "fetch_svg") as fetch:
            result = url.probe_url("not a url")
        fetch.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "misconfigured")

    def test_valid_canary_is_ok(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("jetty_real_svg.svg"))
        ):
            result = url.probe_url("http://mock.invalid:8080")
        self.assertTrue(result.ok)
        self.assertEqual(result.source_state, "ok")

    def test_404_canary_is_misconfigured_with_the_prefix_hint(self):
        with mock.patch.object(url, "fetch_svg", return_value=url.UrlResponse(status=404, body=b"nope")):
            result = url.probe_url("http://mock.invalid:8080")
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "misconfigured")
        self.assertIn("path prefix", result.fix_hint or "")

    def test_request_error_canary_is_unavailable(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("jetty_200_placeholder.svg"))
        ):
            result = url.probe_url("http://mock.invalid:8080")
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "unavailable")
        self.assertIn("request_error", result.reason or "")

    def test_transport_failure_canary_is_unavailable(self):
        with mock.patch.object(
            url,
            "fetch_svg",
            return_value=url.UrlResponse(status=None, body=b"", transport_error="ConnectionRefusedError: [Errno 111]"),
        ):
            result = url.probe_url("http://localhost:9999")
        self.assertFalse(result.ok)
        self.assertEqual(result.source_state, "unavailable")

    def test_probe_is_memoised_per_base_url(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("jetty_real_svg.svg"))
        ) as fetch:
            first = url.probe_url("http://mock.invalid:8080")
            second = url.probe_url("http://mock.invalid:8080")
        self.assertIs(first, second)
        self.assertEqual(fetch.call_count, 1)

    def test_probe_is_memoised_on_the_stripped_base_url(self):
        with mock.patch.object(
            url, "fetch_svg", return_value=url.UrlResponse(status=200, body=_body("jetty_real_svg.svg"))
        ) as fetch:
            first = url.probe_url("http://mock.invalid:8080 ")
            second = url.probe_url("http://mock.invalid:8080")
        self.assertIs(first, second)
        self.assertEqual(fetch.call_count, 1)  # the stripped value keys the cache — one canary, not two


class TestUrlLive(unittest.TestCase):
    """Env-gated: run only when the selected source is an available URL backend."""

    def test_canary_is_valid_and_rendered(self):
        info = require_plantuml_source(self)
        if info.kind != "url":
            self.skipTest("the live URL tests apply only to a selected URL source")
        assert info.value is not None

        verdict = url.validate_url(info.value, backends.CANARY_DIAGRAM)

        self.assertIs(verdict.valid, True)
        self.assertIs(verdict.rendered, True)
        # the Phase 145 render-proof contract: the SVG body carries the diagram
        # text and no crash marker (never is_real_svg alone)
        assert verdict.proof_path is not None
        assert_rendered_svg(Path(verdict.proof_path).read_bytes(), "hello")

    def test_crashing_shape_is_invalid_with_the_crash_finding(self):
        """The recorded known-bug shape (pre-amendment unanchored `note left` after a
        self-message's note tile) ⇒ valid=False + the line-0 crash finding at the
        selected URL source (2026-10-06 — this is the misread the amendment closes)."""
        info = require_plantuml_source(self)
        if info.kind != "url":
            self.skipTest("the live URL tests apply only to a selected URL source")
        assert info.value is not None

        crash_diagram = _body("crash_shape.puml").decode("utf-8")
        verdict = url.validate_url(info.value, crash_diagram)

        self.assertEqual(verdict.classification, url.CLASS_CRASH)
        self.assertIs(verdict.valid, False)
        self.assertIsNotNone(verdict.errors)
        assert verdict.errors is not None
        self.assertEqual(verdict.errors[0].line, 0)
        self.assertIn("crashed", verdict.errors[0].message)
        self.assertIn("ClassCastException", verdict.errors[0].message)
        self.assertIn("note left of", verdict.errors[0].fix_hint)


if __name__ == "__main__":
    unittest.main()
