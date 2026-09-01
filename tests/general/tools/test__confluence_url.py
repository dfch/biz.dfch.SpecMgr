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

"""Tests for the shared ``_confluence_url`` helper module."""

from __future__ import annotations

import unittest

from biz.dfch.specmgr.general.tools._confluence_url import (
    build_rest_content_url,
    extract_page_id,
    looks_like_rest_or_download_url,
    looks_like_tiny_link,
)


class TestExtractPageId(unittest.TestCase):
    """Tests for extract_page_id."""

    def test_cloud_style_pages_path_with_title_extracts_id(self) -> None:
        url = "https://example.atlassian.net/wiki/spaces/FOO/pages/123456/My+Page+Title"

        result = extract_page_id(url)

        self.assertEqual(result, "123456")

    def test_cloud_style_pages_path_without_trailing_segment_extracts_id(self) -> None:
        url = "https://example.atlassian.net/wiki/spaces/FOO/pages/123456"

        result = extract_page_id(url)

        self.assertEqual(result, "123456")

    def test_cloud_style_pages_path_with_query_string_extracts_id(self) -> None:
        url = "https://example.atlassian.net/wiki/spaces/FOO/pages/123456?foo=bar"

        result = extract_page_id(url)

        self.assertEqual(result, "123456")

    def test_server_style_query_pageid_extracts_id(self) -> None:
        url = "https://example.com/pages/viewpage.action?pageId=789"

        result = extract_page_id(url)

        self.assertEqual(result, "789")

    def test_server_style_query_pageid_mid_query_string_extracts_id(self) -> None:
        url = "https://example.com/pages/viewpage.action?spaceKey=FOO&pageId=789&other=1"

        result = extract_page_id(url)

        self.assertEqual(result, "789")

    def test_pageid_query_takes_precedence_over_pages_path(self) -> None:
        url = "https://example.com/wiki/spaces/FOO/pages/111?pageId=222"

        result = extract_page_id(url)

        self.assertEqual(result, "222")

    def test_non_matching_url_returns_none(self) -> None:
        url = "https://example.com/wiki/spaces/FOO/overview"

        result = extract_page_id(url)

        self.assertIsNone(result)

    def test_tiny_link_returns_none(self) -> None:
        url = "https://example.com/wiki/x/AbCdEf"

        result = extract_page_id(url)

        self.assertIsNone(result)

    def test_non_numeric_pages_segment_returns_none(self) -> None:
        url = "https://example.com/wiki/pages/createpage.action"

        result = extract_page_id(url)

        self.assertIsNone(result)


class TestBuildRestContentUrl(unittest.TestCase):
    """Tests for build_rest_content_url."""

    def test_without_expand(self) -> None:
        result = build_rest_content_url("https://example.com/wiki", "123")

        self.assertEqual(result, "https://example.com/wiki/rest/api/content/123")

    def test_with_expand(self) -> None:
        result = build_rest_content_url("https://example.com/wiki", "123", expand="body.storage")

        self.assertEqual(result, "https://example.com/wiki/rest/api/content/123?expand=body.storage")

    def test_base_url_with_trailing_slash_is_stripped(self) -> None:
        result = build_rest_content_url("https://example.com/wiki/", "123")

        self.assertEqual(result, "https://example.com/wiki/rest/api/content/123")

    def test_base_url_with_trailing_slash_and_expand(self) -> None:
        result = build_rest_content_url("https://example.com/wiki/", "123", expand="version,title")

        self.assertEqual(result, "https://example.com/wiki/rest/api/content/123?expand=version,title")

    def test_none_expand_omits_query_string(self) -> None:
        result = build_rest_content_url("https://example.com/wiki", "123", expand=None)

        self.assertEqual(result, "https://example.com/wiki/rest/api/content/123")


class TestLooksLikeRestOrDownloadUrl(unittest.TestCase):
    """Tests for looks_like_rest_or_download_url."""

    def test_rest_api_url_returns_true(self) -> None:
        url = "https://example.com/wiki/rest/api/content/123?expand=body.storage"

        result = looks_like_rest_or_download_url(url)

        self.assertTrue(result)

    def test_download_url_returns_true(self) -> None:
        url = "https://example.com/wiki/download/attachments/123/image.png"

        result = looks_like_rest_or_download_url(url)

        self.assertTrue(result)

    def test_plain_browsable_url_returns_false(self) -> None:
        url = "https://example.com/wiki/spaces/FOO/pages/123456/Title"

        result = looks_like_rest_or_download_url(url)

        self.assertFalse(result)

    def test_uppercase_rest_api_segment_returns_false(self) -> None:
        # Case-sensitive by design -- real Confluence paths are always lowercase.
        url = "https://example.com/wiki/REST/API/content/123"

        result = looks_like_rest_or_download_url(url)

        self.assertFalse(result)


class TestLooksLikeTinyLink(unittest.TestCase):
    """Tests for looks_like_tiny_link."""

    def test_tiny_link_returns_true(self) -> None:
        url = "https://example.com/wiki/x/AbCdEf"

        result = looks_like_tiny_link(url)

        self.assertTrue(result)

    def test_tiny_link_with_trailing_query_returns_true(self) -> None:
        url = "https://example.com/wiki/x/AbCdEf?foo=bar"

        result = looks_like_tiny_link(url)

        self.assertTrue(result)

    def test_non_tiny_link_url_returns_false(self) -> None:
        url = "https://example.com/wiki/spaces/FOO/pages/123456/Title"

        result = looks_like_tiny_link(url)

        self.assertFalse(result)

    def test_pages_path_url_returns_false(self) -> None:
        url = "https://example.com/wiki/pages/viewpage.action?pageId=789"

        result = looks_like_tiny_link(url)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
