"""Tests for the OpenIssues Pydantic model."""

import unittest

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import OpenIssues


class TestOpenIssues(unittest.TestCase):
    """Tests for the OpenIssues Pydantic model."""

    def test_valid_open_issues_creation(self):
        """A valid open issues object with items must be created."""
        issues = OpenIssues(items=["Issue 1", "Issue 2", "Issue 3"])
        self.assertEqual(len(issues.items), 3)
        self.assertEqual(issues.items[0], "Issue 1")

    def test_items_can_be_empty_list(self):
        """Items list can be empty (no open issues)."""
        issues = OpenIssues(items=[])
        self.assertEqual(len(issues.items), 0)

    def test_no_extra_fields_allowed(self):
        """Extra fields must be rejected."""
        with self.assertRaises(ValidationError):
            OpenIssues(
                items=["Issue 1"],
                extra="field",
            )


if __name__ == "__main__":
    unittest.main()
