import pytest
from app.semantic_analysis import SemanticAnalyzer


def test_analyzer_initialization():
    """
    Vérifie que le moteur sémantique se lance correctement
    """
    analyzer = SemanticAnalyzer(
        competencies_path="data/competencies.csv",
        jobs_path="data/jobs.csv"
    )

    assert analyzer is not None
    assert analyzer.competencies_df is not None
    assert analyzer.jobs_df is not None


def test_results_summary_structure():
    """
    Vérifie la structure du résumé des résultats
    """
    analyzer = SemanticAnalyzer(
        competencies_path="data/competencies.csv",
        jobs_path="data/jobs.csv"
    )

    # Faux résultats minimaux
    analyzer.block_scores = {
        "bloc1": {"score": 0.5},
        "bloc2": {"score": 0.5},
        "bloc3": {"score": 0.5},
        "bloc4": {"score": 0.5},
        "bloc5": {"score": 0.5},
    }
    analyzer.coverage_score = 0.5
    analyzer.recommended_jobs = []

    results = analyzer.get_results_summary()

    assert "coverage_score" in results
    assert "block_scores" in results
    assert "recommended_jobs" in results
