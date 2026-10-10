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

"""Tests for the specmgr://config resource (feat-51-mcp-cwd, plus the static similarity section, feat-134 Phase 7)."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR, DEFAULT_ADR_DIR
from biz.dfch.specmgr.feat.tools._paths import DEFAULT_FEAT_DIR, FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.general.resources.config import config_info
from biz.dfch.specmgr.general.tools._doc_paths import DEFAULT_DOCS_ROOT, DOCS_DIR_ENV_VAR

#: The shared domain-name source (feat-125-domain-lists Phase 4, REQ-008):
#: ``ALL_DOMAINS`` -- all document domains this resource must report on
#: (REQ-001) -- and ``WHOLE_BODY_NO_FEAT_DOMAINS`` -- the domains sharing the
#: single SPECMGR_DOCS_DIR root env var.
from biz.dfch.specmgr.general.tools._domains import ALL_DOMAINS, WHOLE_BODY_NO_FEAT_DOMAINS
from biz.dfch.specmgr.general.tools._embedding import SIMILARITY_DISABLED_ENV_VAR, SIMILARITY_MODEL_NAME
from biz.dfch.specmgr.models import ConfigInfo, SimilarityConfig

#: The env vars this resource is allowed to read/report on at all.
_KNOWN_ENV_VARS = {ADR_DIR_ENV_VAR, FEAT_DIR_ENV_VAR, DOCS_DIR_ENV_VAR}


class TestConfigResource(unittest.TestCase):
    """Tests for the `config_info` resource function (`specmgr://config`)."""

    def test_returns_config_info(self):
        """The resource must return a `ConfigInfo` instance."""
        result = config_info()
        self.assertIsInstance(result, ConfigInfo)

    def test_all_domains_present(self):
        """ACC-001: every one of the domains must have an entry."""
        result = config_info()
        self.assertEqual(set(result.domains.keys()), set(ALL_DOMAINS))

    def test_every_domain_has_non_empty_base_dir_and_env_var(self):
        """Every domain's `base_dir`/`env_var` must be non-empty strings."""
        result = config_info()
        for domain, cfg in result.domains.items():
            with self.subTest(domain=domain):
                self.assertTrue(cfg.base_dir.strip())
                self.assertTrue(cfg.env_var.strip())

    def test_base_dir_values_are_absolute(self):
        """ACC-001: `base_dir` must be resolved to an absolute path for every domain."""
        result = config_info()
        for domain, cfg in result.domains.items():
            with self.subTest(domain=domain):
                self.assertTrue(Path(cfg.base_dir).is_absolute(), f"{domain}'s base_dir is not absolute")

    def test_adr_and_feat_have_their_own_env_var(self):
        """`adr`/`feat` each report their own dedicated env var, not the shared one."""
        result = config_info()
        self.assertEqual(result.domains["adr"].env_var, ADR_DIR_ENV_VAR)
        self.assertEqual(result.domains["feat"].env_var, FEAT_DIR_ENV_VAR)

    def test_docs_dir_domains_share_env_var(self):
        """The non-adr/feat domains all report the shared `SPECMGR_DOCS_DIR` env var."""
        result = config_info()
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                self.assertEqual(result.domains[domain].env_var, DOCS_DIR_ENV_VAR)

    def test_env_var_set_reflects_controlled_environment(self):
        """`env_var_set` must reflect the actual presence of each domain's own env var."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(ADR_DIR_ENV_VAR, None)
            os.environ.pop(FEAT_DIR_ENV_VAR, None)
            os.environ.pop(DOCS_DIR_ENV_VAR, None)

            result = config_info()
            self.assertFalse(result.domains["adr"].env_var_set)
            self.assertFalse(result.domains["feat"].env_var_set)
            for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
                self.assertFalse(result.domains[domain].env_var_set, domain)

        with mock.patch.dict(os.environ, {ADR_DIR_ENV_VAR: "/tmp/custom-adr"}, clear=False):
            self.assertTrue(config_info().domains["adr"].env_var_set)

        with mock.patch.dict(os.environ, {FEAT_DIR_ENV_VAR: "/tmp/custom-feat"}, clear=False):
            self.assertTrue(config_info().domains["feat"].env_var_set)

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}, clear=False):
            result = config_info()
            for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
                with self.subTest(domain=domain):
                    self.assertTrue(result.domains[domain].env_var_set)

    def test_env_var_set_counts_a_set_but_empty_value_as_set(self):
        """The three base-dir env vars' presence checks read through the registry's raw ``get``
        accessor (feat-208 Phase 120): a set-but-empty value still reports ``env_var_set`` as
        True (the ``None``-vs-``""`` distinction preserved), while the resolved ``base_dir``
        falls back to the default (the ``empty_falls_back_to_default`` flag) -- the two
        distinctions must not bleed into each other."""
        with mock.patch.dict(
            os.environ,
            {ADR_DIR_ENV_VAR: "", FEAT_DIR_ENV_VAR: "", DOCS_DIR_ENV_VAR: ""},
            clear=False,
        ):
            result = config_info()

        self.assertTrue(result.domains["adr"].env_var_set)
        self.assertEqual(result.domains["adr"].base_dir, str(DEFAULT_ADR_DIR.resolve()))
        self.assertTrue(result.domains["feat"].env_var_set)
        self.assertEqual(result.domains["feat"].base_dir, str(DEFAULT_FEAT_DIR.resolve()))
        for domain in WHOLE_BODY_NO_FEAT_DOMAINS:
            with self.subTest(domain=domain):
                self.assertTrue(result.domains[domain].env_var_set)
                self.assertEqual(result.domains[domain].base_dir, str((DEFAULT_DOCS_ROOT / domain).resolve()))


class TestConfigResourceNonDisclosure(unittest.TestCase):
    """ACC-002: `specmgr://config` must never disclose unrelated env var values."""

    def test_unrelated_secret_env_var_never_appears_in_payload(self):
        """Setting a fake secret env var must not leak its value anywhere in the output."""
        secret_value = "super-secret-value-should-never-leak"
        with mock.patch.dict(os.environ, {"SOME_FAKE_TOKEN": secret_value}, clear=False):
            result = config_info()

            as_json = result.model_dump_json()
            as_dict = result.model_dump()

            self.assertNotIn(secret_value, as_json)
            self.assertNotIn(secret_value, json.dumps(as_dict))
            for cfg in result.domains.values():
                self.assertNotIn(secret_value, cfg.base_dir)
                self.assertNotIn(secret_value, cfg.env_var)

    def test_only_known_env_vars_are_ever_reported_as_env_var_field(self):
        """Every domain's `env_var` field must be one of the known `SPECMGR_*_DIR` names."""
        result = config_info()
        for domain, cfg in result.domains.items():
            with self.subTest(domain=domain):
                self.assertIn(cfg.env_var, _KNOWN_ENV_VARS)

    def test_fake_pat_env_var_never_appears(self):
        """A fake PAT-shaped env var must not leak into the payload either."""
        fake_pat = "ghp_ThisLooksLikeARealPersonalAccessTokenXYZ123"
        with mock.patch.dict(os.environ, {"SPECMGR_FAKE_PAT": fake_pat}, clear=False):
            result = config_info()
            as_json = result.model_dump_json()
            self.assertNotIn(fake_pat, as_json)


class TestConfigResourceSimilarity(unittest.TestCase):
    """The static ``similarity`` section (feat-134 Phase 7, REQ-013/ACC-018).

    ``specmgr://config`` reports the similarity feature's static
    install/runtime configuration -- extra installed?, opt-out flag set?,
    model name, resolved cache directory -- without ever importing
    ``fastembed`` or creating any directory (the resource's own
    side-effect-free contract, ACC-018). The section is static
    configuration only: the tools' own dynamic availability is their
    structured ``{available, reason, message}`` result, deliberately not
    part of this payload.
    """

    def test_returns_a_similarity_config(self):
        """The payload must carry a `SimilarityConfig` section."""
        result = config_info()
        self.assertIsInstance(result.similarity, SimilarityConfig)

    def test_extra_installed_reports_true_when_fastembed_spec_found(self):
        """ACC-018 matrix: the `similarity` extra installed -> `extra_installed` is True (spec lookup only)."""
        with mock.patch("biz.dfch.specmgr.general.resources.config.find_spec", return_value=object()):
            self.assertTrue(config_info().similarity.extra_installed)

    def test_extra_not_installed_reports_false_when_fastembed_spec_missing(self):
        """ACC-018 matrix: the `similarity` extra not installed -> `extra_installed` is False."""
        with mock.patch("biz.dfch.specmgr.general.resources.config.find_spec", return_value=None):
            self.assertFalse(config_info().similarity.extra_installed)

    def test_disabled_flag_unset_reports_false(self):
        """ACC-018 matrix: `SPECMGR_SIMILARITY_DISABLED` absent -> `disabled` is False."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop(SIMILARITY_DISABLED_ENV_VAR, None)
            self.assertFalse(config_info().similarity.disabled)

    def test_disabled_flag_set_reports_true(self):
        """ACC-018 matrix: `SPECMGR_SIMILARITY_DISABLED` present (any value) -> `disabled` is True."""
        with mock.patch.dict(os.environ, {SIMILARITY_DISABLED_ENV_VAR: "1"}, clear=False):
            self.assertTrue(config_info().similarity.disabled)

    def test_model_name_is_the_shared_constant(self):
        """ACC-020: `model_name` must be the shared `SIMILARITY_MODEL_NAME` constant (no duplicated literal)."""
        result = config_info()
        self.assertEqual(result.similarity.model_name, SIMILARITY_MODEL_NAME)
        self.assertEqual(result.similarity.model_name, "BAAI/bge-small-en-v1.5")

    def test_cache_dir_defaults_to_tempdir_when_unset(self):
        """ACC-018: `FASTEMBED_CACHE_PATH` unset -> the resolved `<tempdir>/fastembed_cache` default."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("FASTEMBED_CACHE_PATH", None)
            expected = str((Path(tempfile.gettempdir()) / "fastembed_cache").resolve())
            self.assertEqual(config_info().similarity.cache_dir, expected)

    def test_cache_dir_uses_fastembed_cache_path_when_set(self):
        """ACC-018: `FASTEMBED_CACHE_PATH` set -> that path resolved to absolute, never created by the read."""
        with tempfile.TemporaryDirectory() as tmp:
            target = str(Path(tmp) / "not-created-by-config-read")
            with mock.patch.dict(os.environ, {"FASTEMBED_CACHE_PATH": target}, clear=False):
                result = config_info()
            self.assertEqual(result.similarity.cache_dir, str(Path(target).resolve()))
            self.assertFalse(
                Path(result.similarity.cache_dir).exists(),
                "reading specmgr://config must never create the cache directory",
            )

    def test_cache_dir_set_but_empty_falls_back_to_default(self):
        """The one documented deviation from `fastembed.common.utils.define_cache_dir` (which would treat `""` as CWD): a set-but-empty `FASTEMBED_CACHE_PATH` falls back to the resolved `<tempdir>/fastembed_cache` default (the plan's Decisions Made entry, feat-134 Phase 7)."""
        with mock.patch.dict(os.environ, {"FASTEMBED_CACHE_PATH": ""}, clear=False):
            expected = str((Path(tempfile.gettempdir()) / "fastembed_cache").resolve())
            self.assertEqual(config_info().similarity.cache_dir, expected)

    def test_disabled_flag_set_reports_true_for_empty_and_zero_values(self):
        """The presence-based contract, symmetric with the tool-side pin (`test__embedding.py`'s `test_disabled_flag_is_presence_based_not_truthy`, which asserts the values `""`/`"0"` too): a `SPECMGR_SIMILARITY_DISABLED` of `""` or `"0"` also reports `disabled` as True."""
        for value in ("", "0"):
            with self.subTest(value=value):
                with mock.patch.dict(os.environ, {SIMILARITY_DISABLED_ENV_VAR: value}, clear=False):
                    self.assertTrue(config_info().similarity.disabled)

    def test_config_info_never_imports_fastembed(self):
        """ACC-018: `config_info()` must leave `sys.modules` byte-identical (no import at all, `fastembed` in particular)."""
        self.assertNotIn("fastembed", sys.modules, "fastembed must not already be imported by the test suite here")

        before = set(sys.modules)
        config_info()
        after = set(sys.modules)

        self.assertEqual(after, before, "config_info() must not import any module (side-effect-free)")
        self.assertNotIn("fastembed", sys.modules)


class TestConfigResourcePlantuml(unittest.TestCase):
    """The static ``plantuml`` section (feat-185-uc-diagrams Phase 120, rulebook §3.1/§3.2).

    ``specmgr://config`` reports the PlantUML validation source's static
    configuration -- presence only for the exactly-three source env vars
    (never a value: a jar path, a bin path, or a server URL would be a
    disclosure violation, REQ-002's own contract) plus ``selected``, the
    first-set-wins selection over them (``"none"`` when all unset). The
    section is static configuration only: whether the selected source
    answers its canary right now is the ``validate_plantuml`` tool's own
    ``source_state``/``available`` result, deliberately not part of this
    payload.
    """

    def test_returns_a_plantuml_config_with_the_frozen_shape(self):
        """The payload must carry a plantuml section with exactly the frozen shape: three {set: bool}
        sources plus the closed selected vocabulary."""
        from biz.dfch.specmgr.models import PlantumlConfig

        result = config_info()
        self.assertIsInstance(result.plantuml, PlantumlConfig)
        self.assertEqual(
            set(result.plantuml.model_dump()),
            {"jar", "bin", "url", "selected"},
        )
        for source in ("jar", "bin", "url"):
            with self.subTest(source=source):
                self.assertEqual(set(getattr(result.plantuml, source).model_dump()), {"set"})
                self.assertIsInstance(getattr(result.plantuml, source).set, bool)
        self.assertIn(result.plantuml.selected, ("jar", "bin", "url", "none"))

    def test_all_unset_selects_none(self):
        """All three vars absent: every {set} is False and selected is "none" (the structure-only floor)."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SPECMGR_PLANTUML_JAR", None)
            os.environ.pop("SPECMGR_PLANTUML_BIN", None)
            os.environ.pop("SPECMGR_PLANTUML_URL", None)
            result = config_info()

        self.assertFalse(result.plantuml.jar.set)
        self.assertFalse(result.plantuml.bin.set)
        self.assertFalse(result.plantuml.url.set)
        self.assertEqual(result.plantuml.selected, "none")

    def test_first_set_wins_over_the_frozen_order(self):
        """selected must follow the §3.2 order JAR -> BIN -> URL, first set wins (matrix)."""
        cases = [
            # (jar, bin, url) -> selected
            ((True, False, False), "jar"),
            ((True, True, True), "jar"),
            ((False, True, False), "bin"),
            ((False, True, True), "bin"),
            ((False, False, True), "url"),
        ]
        for (jar, bin_, url), expected in cases:
            with self.subTest(jar=jar, bin=bin_, url=url):
                env = {}
                if jar:
                    env["SPECMGR_PLANTUML_JAR"] = "/some/plantuml.jar"
                if bin_:
                    env["SPECMGR_PLANTUML_BIN"] = "/some/plantuml-adapter"
                if url:
                    env["SPECMGR_PLANTUML_URL"] = "http://localhost:8080"
                with mock.patch.dict(os.environ, env, clear=False):
                    os.environ.pop("SPECMGR_PLANTUML_JAR", None)
                    os.environ.pop("SPECMGR_PLANTUML_BIN", None)
                    os.environ.pop("SPECMGR_PLANTUML_URL", None)
                    os.environ.update(env)
                    result = config_info()
                self.assertEqual(result.plantuml.selected, expected)
                self.assertEqual(result.plantuml.jar.set, jar)
                self.assertEqual(result.plantuml.bin.set, bin_)
                self.assertEqual(result.plantuml.url.set, url)

    def test_set_but_empty_counts_as_set(self):
        """Presence-based: a set-but-empty value still counts (the chain's own strictness rule selects
        it, then probes it as misconfigured -- the section reports the presence only)."""
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SPECMGR_PLANTUML_JAR", None)
            os.environ.pop("SPECMGR_PLANTUML_BIN", None)
            os.environ.pop("SPECMGR_PLANTUML_URL", None)
            os.environ["SPECMGR_PLANTUML_JAR"] = ""
            result = config_info()

        self.assertTrue(result.plantuml.jar.set)
        self.assertEqual(result.plantuml.selected, "jar")

    def test_source_values_never_appear_in_the_payload(self):
        """REQ-002 (the resource's own no-disclosure contract, extended to the plantuml section):
        the values of the three vars (a jar path, a bin path, a server URL) must never leak."""
        secret_jar = "/secrets/plantuml.jar-should-never-leak"
        secret_bin = "/secrets/plantuml-adapter-should-never-leak"
        secret_url = "http://secrets.internal:8080/should-never-leak"
        with mock.patch.dict(
            os.environ,
            {
                "SPECMGR_PLANTUML_JAR": secret_jar,
                "SPECMGR_PLANTUML_BIN": secret_bin,
                "SPECMGR_PLANTUML_URL": secret_url,
            },
            clear=False,
        ):
            result = config_info()
            as_json = result.model_dump_json()

        for secret in (secret_jar, secret_bin, secret_url):
            with self.subTest(secret=secret):
                self.assertNotIn(secret, as_json)


if __name__ == "__main__":
    unittest.main()
