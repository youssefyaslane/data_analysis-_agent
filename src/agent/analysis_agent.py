"""Workflow LangGraph d'analyse de données : lecture CSV -> insights.

Deux étapes déterministes, tracées séparément dans LangSmith :
1. read_csv : lecture pandas + résumé structuré (aucun appel LLM)
2. generate_insights : un seul appel LLM à partir de ce résumé
"""
from __future__ import annotations

from typing import TypedDict

from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

from agent import config
from agent.tools import summarize_csv

INSIGHTS_PROMPT = """Tu es un agent d'analyse de données.

Voici le résumé structuré d'un fichier CSV :

{summary}

À partir de ce résumé, rédige des INSIGHTS clairs et concrets : tendances,
valeurs extrêmes, comparaisons, corrélations notables — pas seulement des
chiffres bruts. Termine par un résumé structuré de tes insights.

Ne génère PAS de graphique : uniquement une analyse textuelle.
"""


class AnalysisState(TypedDict):
    csv_path: str
    csv_summary: str
    report: str


def _build_model() -> ChatOpenAI:
    model_id = config.AGENT_MODEL.split(":", 1)[-1]  # retire le préfixe "openai:"
    return ChatOpenAI(
        model=model_id,
        api_key=config.OPENAI_API_KEY,
        max_tokens=8192,
    )


def read_csv_node(state: AnalysisState) -> dict:
    return {"csv_summary": summarize_csv(state["csv_path"])}


def generate_insights_node(state: AnalysisState) -> dict:
    model = _build_model()
    response = model.invoke(INSIGHTS_PROMPT.format(summary=state["csv_summary"]))
    return {"report": response.content}


def build_workflow():
    graph = StateGraph(AnalysisState)
    graph.add_node("read_csv", read_csv_node)
    graph.add_node("generate_insights", generate_insights_node)
    graph.set_entry_point("read_csv")
    graph.add_edge("read_csv", "generate_insights")
    graph.add_edge("generate_insights", END)
    return graph.compile()


def run_analysis(csv_relative_path: str) -> dict:
    """Lance le workflow sur un CSV et retourne le rapport d'insights."""
    config.validate()
    workflow = build_workflow()

    result = workflow.invoke({"csv_path": csv_relative_path})
    report = result.get("report", "").strip()

    if not report:
        raise RuntimeError("Le workflow n'a produit aucune analyse exploitable.")

    return {"report": report, "plot_url": None}
