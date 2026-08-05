"""Tests for render_uc_diagram (Task 2.1)."""

import unittest
from pathlib import Path

from biz.dfch.specmgr.uc.models.v1.parser import parse_uc
from biz.dfch.specmgr.uc.models.v1.uc_diagram import render_uc_diagram
from biz.dfch.specmgr.uc.models.v1.characteristic_information import CharacteristicInformation
from biz.dfch.specmgr.uc.models.v1.main_success_scenario import MainSuccessScenario
from biz.dfch.specmgr.uc.models.v1.step import Step
from biz.dfch.specmgr.uc.models.v1.use_case import UseCase
from biz.dfch.specmgr.uc.models.v1.use_case_frontmatter import UseCaseFrontmatter

_EXAMPLE_PATH = Path(__file__).resolve().parents[4] / ".specmgr" / "feat" / "feat-0-use-cases" / "uc_example.md"


def _make_use_case(primary_actor: str, secondary_actors: list[str] | None = None, title: str = "Buy Goods") -> UseCase:
    return UseCase(
        frontmatter=UseCaseFrontmatter(
            id="uc-001", version="1.0.0", status="draft", created="2026-08-05", updated="2026-08-05"
        ),
        title=title,
        characteristic_information=CharacteristicInformation(
            goal_in_context="Goal.",
            scope="Company.",
            level="Summary",
            preconditions=["We know Buyer"],
            success_end_condition=["Buyer has goods"],
            primary_actor=primary_actor,
            secondary_actors=secondary_actors,
            trigger="Purchase request comes in.",
        ),
        main_success_scenario=MainSuccessScenario(steps=[Step(number=1, description="Buyer calls in.")]),
    )


class TestActorLabelExtraction(unittest.TestCase):
    """Tests for the actor free-text -> PlantUML label rule (module docstring)."""

    def test_plain_text_used_as_is(self) -> None:
        """No quotes, no parenthetical: the text is used as-is."""
        uc = _make_use_case(primary_actor="Buyer")
        diagram = render_uc_diagram(uc)
        self.assertIn("actor Buyer", diagram)

    def test_trailing_parenthetical_is_stripped(self) -> None:
        """A trailing parenthetical aside is dropped from the label."""
        uc = _make_use_case(primary_actor="Buyer (any agent or computer acting for the customer)")
        diagram = render_uc_diagram(uc)
        # "Buyer" is a bare identifier, so the label is reused as its own alias, unquoted.
        self.assertIn("actor Buyer\n", diagram)
        self.assertNotIn("any agent", diagram)

    def test_quoted_substring_wins_over_parenthetical(self) -> None:
        """A quoted substring takes priority even when a parenthetical is also present."""
        uc = _make_use_case(primary_actor='Company refers to buyer as "Buyer" (any agent...)')
        diagram = render_uc_diagram(uc)
        self.assertIn("actor Buyer\n", diagram)
        self.assertNotIn("Company refers", diagram)
        self.assertNotIn("any agent", diagram)

    def test_secondary_actor_with_parenthetical(self) -> None:
        """Secondary actors go through the same label extraction as primary_actor."""
        uc = _make_use_case(primary_actor="Buyer", secondary_actors=["Credit card company (for payment processing)"])
        diagram = render_uc_diagram(uc)
        self.assertIn('actor "Credit card company" as', diagram)
        self.assertNotIn("for payment processing", diagram)

    def test_duplicate_labels_are_deduplicated(self) -> None:
        """Two actor fields resolving to the same clean label produce only one actor node."""
        uc = _make_use_case(primary_actor="Buyer (the customer)", secondary_actors=["Buyer (acting via agent)"])
        diagram = render_uc_diagram(uc)
        self.assertEqual(diagram.count("actor Buyer\n"), 1)
        self.assertEqual(diagram.count("--> uc"), 1)


class TestDiagramStructure(unittest.TestCase):
    """Tests for the overall PlantUML document structure."""

    def test_starts_and_ends_with_plantuml_markers(self) -> None:
        uc = _make_use_case(primary_actor="Buyer")
        diagram = render_uc_diagram(uc)
        self.assertTrue(diagram.startswith("@startuml Buy Goods"))
        self.assertTrue(diagram.rstrip("\n").endswith("@enduml"))
        self.assertTrue(diagram.endswith("\n"))
        self.assertFalse(diagram.endswith("\n\n"))

    def test_single_usecase_node_for_the_document(self) -> None:
        uc = _make_use_case(primary_actor="Buyer")
        diagram = render_uc_diagram(uc)
        self.assertIn('usecase "Buy Goods" as uc', diagram)
        self.assertEqual(diagram.count("usecase "), 1)

    def test_association_edge_per_actor(self) -> None:
        uc = _make_use_case(primary_actor="Buyer", secondary_actors=["Bank"])
        diagram = render_uc_diagram(uc)
        self.assertIn("Buyer --> uc", diagram)
        self.assertIn("Bank --> uc", diagram)

    def test_no_secondary_actors_yields_only_primary_association(self) -> None:
        uc = _make_use_case(primary_actor="Buyer")
        diagram = render_uc_diagram(uc)
        self.assertEqual(diagram.count("--> uc"), 1)

    def test_bare_identifier_actor_name_reused_as_alias(self) -> None:
        """A single-word, already-identifier-shaped actor name is used as its own alias."""
        uc = _make_use_case(primary_actor="Buyer")
        diagram = render_uc_diagram(uc)
        self.assertIn("actor Buyer\n", diagram)
        self.assertNotIn('actor "Buyer" as', diagram)


class TestFullExampleRoundTrip(unittest.TestCase):
    """Diagram generation against the full worked uc_example.md document."""

    def test_renders_all_actors_from_full_example(self) -> None:
        use_case = parse_uc(_EXAMPLE_PATH.read_text(encoding="utf-8"))
        diagram = render_uc_diagram(use_case)

        self.assertIn("@startuml Buy Goods", diagram)
        self.assertIn('usecase "Buy Goods" as uc', diagram)
        # Primary actor: "Buyer (any agent or computer acting for the customer)" -> "Buyer",
        # a bare identifier, so it is reused as its own (unquoted) alias.
        self.assertIn("actor Buyer\n", diagram)
        # Secondary actors, parenthetical asides stripped. "Bank" is also a bare identifier.
        self.assertIn('actor "Credit card company" as', diagram)
        self.assertIn("actor Bank\n", diagram)
        self.assertIn('actor "Shipping service" as', diagram)
        self.assertNotIn("for payment processing", diagram)
        self.assertNotIn("for delivery", diagram)

    def test_every_actor_has_an_association_edge(self) -> None:
        use_case = parse_uc(_EXAMPLE_PATH.read_text(encoding="utf-8"))
        diagram = render_uc_diagram(use_case)
        self.assertEqual(diagram.count("--> uc"), 4)


if __name__ == "__main__":
    unittest.main()
