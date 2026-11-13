"""
tests/test_quiz.py – Tests for financial literacy quiz data.
Run: pytest tests/ -v
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest


class TestQuizData:
    """Test quiz data integrity and completeness."""

    def test_all_modules_have_quizzes(self):
        from quizzes.quiz_data import QUIZZES, get_all_modules
        modules = get_all_modules()
        assert len(modules) >= 10, "Must have quizzes for at least 10 modules"

    def test_quiz_question_structure(self):
        from quizzes.quiz_data import QUIZZES
        required_keys = {"q", "options", "answer", "explanation"}
        for module, questions in QUIZZES.items():
            for i, q in enumerate(questions):
                missing = required_keys - set(q.keys())
                assert not missing, f"Module {module}, Q{i+1} missing: {missing}"

    def test_quiz_answers_valid(self):
        """All answers must be valid option letters (A, B, C, D)."""
        from quizzes.quiz_data import QUIZZES
        valid_answers = {"A", "B", "C", "D"}
        for module, questions in QUIZZES.items():
            for q in questions:
                assert q["answer"] in valid_answers, (
                    f"Module {module}, Q: '{q['q'][:30]}' has invalid answer: {q['answer']}"
                )

    def test_quiz_options_count(self):
        """Each question must have exactly 4 options."""
        from quizzes.quiz_data import QUIZZES
        for module, questions in QUIZZES.items():
            for q in questions:
                assert len(q["options"]) == 4, (
                    f"Module {module}, Q: '{q['q'][:30]}' must have 4 options"
                )

    def test_quiz_options_labeled(self):
        """Options must start with A., B., C., D."""
        from quizzes.quiz_data import QUIZZES
        for module, questions in QUIZZES.items():
            for q in questions:
                for expected_letter, option in zip(["A", "B", "C", "D"], q["options"]):
                    assert option.startswith(expected_letter + "."), (
                        f"Option '{option}' should start with '{expected_letter}.'"
                    )

    def test_get_quiz_returns_list(self):
        from quizzes.quiz_data import get_quiz
        questions = get_quiz("upi_payments")
        assert isinstance(questions, list)
        assert len(questions) > 0

    def test_get_quiz_invalid_module(self):
        from quizzes.quiz_data import get_quiz
        questions = get_quiz("nonexistent_module")
        assert questions == []

    def test_explanations_reference_sources(self):
        """Explanations should reference official sources."""
        from quizzes.quiz_data import QUIZZES
        source_refs = ["RBI", "NPCI", "SEBI", "IRDAI", "npci.org.in", "rbi.org.in",
                      "sebi.gov.in", "irdai.gov.in", "cybercrime.gov.in", "1930",
                      "Source:", "Ministry"]
        no_source_count = 0
        for module, questions in QUIZZES.items():
            for q in questions:
                exp = q["explanation"]
                has_source = any(ref in exp for ref in source_refs)
                if not has_source:
                    no_source_count += 1
        # Allow at most 20% of questions to not have explicit source references
        total = sum(len(qs) for qs in QUIZZES.values())
        assert no_source_count <= (total * 0.2), (
            f"{no_source_count}/{total} quiz explanations lack source references"
        )

    def test_all_quiz_modules_match_knowledge_base(self):
        """Quiz modules should correspond to knowledge base modules."""
        from quizzes.quiz_data import QUIZZES
        from rag.knowledge_base import get_module_metadata
        kb_modules = set(get_module_metadata().keys())
        quiz_modules = set(QUIZZES.keys())
        # All quiz modules should exist in knowledge base
        missing = quiz_modules - kb_modules
        assert not missing, f"Quiz modules not in knowledge base: {missing}"
