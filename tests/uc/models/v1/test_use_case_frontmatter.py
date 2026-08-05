"""Tests for the UseCaseFrontmatter Pydantic model."""

import unittest
from datetime import date

from pydantic import ValidationError

from biz.dfch.specmgr.uc.models import UseCaseFrontmatter


class TestUseCaseFrontmatter(unittest.TestCase):
    """Tests for the UseCaseFrontmatter Pydantic model."""

    def test_valid_frontmatter_creation(self):
        """A valid frontmatter with all required fields must be created successfully."""
        fm = UseCaseFrontmatter(
            id="uc-001",
            version="1.0.0",
            status="draft",
            created=date(2026, 8, 5),
            updated=date(2026, 8, 5),
        )
        self.assertEqual(fm.id, "uc-001")
        self.assertEqual(fm.version, "1.0.0")
        self.assertEqual(fm.status, "draft")
        self.assertEqual(fm.created, date(2026, 8, 5))
        self.assertEqual(fm.updated, date(2026, 8, 5))

    def test_id_pattern_validation(self):
        """ID must match pattern 'uc-NNN' where NNN are digits."""
        # Valid IDs
        for valid_id in ["uc-001", "uc-0", "uc-999999"]:
            with self.subTest(id=valid_id):
                fm = UseCaseFrontmatter(
                    id=valid_id,
                    version="1.0.0",
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                )
                self.assertEqual(fm.id, valid_id)

        # Invalid IDs
        for invalid_id in ["UC-001", "uc-abc", "uc-", "001", "uc-001-extra"]:
            with self.subTest(id=invalid_id):
                with self.assertRaises(ValidationError):
                    UseCaseFrontmatter(
                        id=invalid_id,
                        version="1.0.0",
                        status="draft",
                        created=date(2026, 8, 5),
                        updated=date(2026, 8, 5),
                    )

    def test_version_pattern_validation(self):
        """Version must match semantic versioning pattern 'X.Y.Z'."""
        # Valid versions
        for valid_version in ["1.0.0", "0.0.0", "10.20.30"]:
            with self.subTest(version=valid_version):
                fm = UseCaseFrontmatter(
                    id="uc-001",
                    version=valid_version,
                    status="draft",
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                )
                self.assertEqual(fm.version, valid_version)

        # Invalid versions
        for invalid_version in ["1.0", "1.0.0.0", "v1.0.0", "1.a.0"]:
            with self.subTest(version=invalid_version):
                with self.assertRaises(ValidationError):
                    UseCaseFrontmatter(
                        id="uc-001",
                        version=invalid_version,
                        status="draft",
                        created=date(2026, 8, 5),
                        updated=date(2026, 8, 5),
                    )

    def test_status_enum_validation(self):
        """Status must be one of the allowed enum values."""
        # Valid statuses
        for valid_status in ["draft", "proposed", "accepted", "deprecated", "superseded"]:
            with self.subTest(status=valid_status):
                fm = UseCaseFrontmatter(
                    id="uc-001",
                    version="1.0.0",
                    status=valid_status,
                    created=date(2026, 8, 5),
                    updated=date(2026, 8, 5),
                )
                self.assertEqual(fm.status, valid_status)

        # Invalid status
        with self.assertRaises(ValidationError):
            UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="in-review",
                created=date(2026, 8, 5),
                updated=date(2026, 8, 5),
            )

    def test_date_fields_required(self):
        """Both created and updated dates must be provided."""
        with self.assertRaises(ValidationError):
            UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="draft",
                created=date(2026, 8, 5),
                # missing updated
            )

    def test_all_fields_required(self):
        """All frontmatter fields are required."""
        required_fields = ["id", "version", "status", "created", "updated"]
        for field in required_fields:
            with self.subTest(field=field):
                kwargs = {
                    "id": "uc-001",
                    "version": "1.0.0",
                    "status": "draft",
                    "created": date(2026, 8, 5),
                    "updated": date(2026, 8, 5),
                }
                del kwargs[field]
                with self.assertRaises(ValidationError):
                    UseCaseFrontmatter(**kwargs)

    def test_no_extra_fields_allowed(self):
        """Extra fields not in the schema must be rejected."""
        with self.assertRaises(ValidationError):
            UseCaseFrontmatter(
                id="uc-001",
                version="1.0.0",
                status="draft",
                created=date(2026, 8, 5),
                updated=date(2026, 8, 5),
                extra_field="should fail",
            )


if __name__ == "__main__":
    unittest.main()
