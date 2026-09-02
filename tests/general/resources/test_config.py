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

"""Tests for the specmgr://config resource (feat-51-mcp-cwd)."""

import json
import os
import unittest
from pathlib import Path
from unittest import mock

from biz.dfch.specmgr.adr.tools._paths import ADR_DIR_ENV_VAR
from biz.dfch.specmgr.feat.tools._paths import FEAT_DIR_ENV_VAR
from biz.dfch.specmgr.general.resources.config import config_info
from biz.dfch.specmgr.general.tools._doc_paths import DOCS_DIR_ENV_VAR
from biz.dfch.specmgr.models import ConfigInfo

#: All twelve document domains this resource must report on (REQ-001).
_ALL_DOMAINS = ["adr", "req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "feat", "vcr"]

#: The ten domains sharing the single SPECMGR_DOCS_DIR root env var.
_DOCS_DIR_DOMAINS = ["req", "uc", "tsk", "qa", "prb", "gol", "rsk", "dec", "sop", "vcr"]

#: The env vars this resource is allowed to read/report on at all.
_KNOWN_ENV_VARS = {ADR_DIR_ENV_VAR, FEAT_DIR_ENV_VAR, DOCS_DIR_ENV_VAR}


class TestConfigResource(unittest.TestCase):
    """Tests for the `config_info` resource function (`specmgr://config`)."""

    def test_returns_config_info(self):
        """The resource must return a `ConfigInfo` instance."""
        result = config_info()
        self.assertIsInstance(result, ConfigInfo)

    def test_all_twelve_domains_present(self):
        """ACC-001: every one of the twelve domains must have an entry."""
        result = config_info()
        self.assertEqual(set(result.domains.keys()), set(_ALL_DOMAINS))

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

    def test_ten_domains_share_docs_dir_env_var(self):
        """The ten non-adr/feat domains all report the shared `SPECMGR_DOCS_DIR` env var."""
        result = config_info()
        for domain in _DOCS_DIR_DOMAINS:
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
            for domain in _DOCS_DIR_DOMAINS:
                self.assertFalse(result.domains[domain].env_var_set, domain)

        with mock.patch.dict(os.environ, {ADR_DIR_ENV_VAR: "/tmp/custom-adr"}, clear=False):
            self.assertTrue(config_info().domains["adr"].env_var_set)

        with mock.patch.dict(os.environ, {FEAT_DIR_ENV_VAR: "/tmp/custom-feat"}, clear=False):
            self.assertTrue(config_info().domains["feat"].env_var_set)

        with mock.patch.dict(os.environ, {DOCS_DIR_ENV_VAR: "/tmp/custom-docs"}, clear=False):
            result = config_info()
            for domain in _DOCS_DIR_DOMAINS:
                with self.subTest(domain=domain):
                    self.assertTrue(result.domains[domain].env_var_set)


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
        """Every domain's `env_var` field must be one of the twelve known SPECMGR_*_DIR names."""
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


if __name__ == "__main__":
    unittest.main()
