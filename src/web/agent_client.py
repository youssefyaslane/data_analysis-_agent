"""Pont entre les routes Flask et l'agent d'analyse."""
from __future__ import annotations

import markdown

from agent.analysis_agent import run_analysis


class AnalysisError(Exception):
    """Erreur levée quand l'agent ne parvient pas à produire une analyse."""


def analyze_csv(filename: str) -> dict:
    """Lance l'agent sur un CSV déjà présent dans uploads/ et retourne le résultat."""
    try:
        result = run_analysis(f"uploads/{filename}")
    except Exception as e:
        raise AnalysisError(str(e)) from e

    result["report_html"] = markdown.markdown(
        result["report"], extensions=["tables", "sane_lists"]
    )
    return result
