"""Construction et exécution de l'agent d'analyse de données (LangChain)."""
from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent

from agent import config
from agent.tools import read_csv_summary

SYSTEM_PROMPT = """Tu es un agent d'analyse de données.

Pour le fichier CSV fourni :
1. Appelle l'outil read_csv_summary pour obtenir un résumé des données.
2. Rédige des INSIGHTS clairs et concrets à partir de ce résumé : tendances,
   valeurs extrêmes, comparaisons, corrélations notables — pas seulement des
   chiffres bruts.
3. Termine par un résumé structuré de tes insights.

Ne génère PAS de graphique : uniquement une analyse textuelle.
"""


def _build_model() -> ChatOpenAI:
    model_id = config.AGENT_MODEL.split(":", 1)[-1]  # retire le préfixe "openai:"
    return ChatOpenAI(
        model=model_id,
        api_key=config.OPENAI_API_KEY,
        max_tokens=8192,
    )


def build_agent():
    return create_react_agent(
        model=_build_model(),
        tools=[read_csv_summary],
        prompt=SYSTEM_PROMPT,
        checkpointer=InMemorySaver(),
    )


def run_analysis(csv_relative_path: str) -> dict:
    """Lance l'agent sur un CSV et retourne le rapport d'insights."""
    config.validate()
    agent = build_agent()

    input_message = {
        "role": "user",
        "content": f"Analyse le fichier {csv_relative_path} et donne-moi tes insights.",
    }
    thread_config = {"configurable": {"thread_id": "analysis"}}
    result = agent.invoke({"messages": [input_message]}, thread_config)

    messages = result["messages"]

    # Insights : texte de tous les messages IA (hors appels d'outils purs)
    report_parts = [
        m.content for m in messages
        if isinstance(m, AIMessage) and isinstance(m.content, str) and m.content.strip()
    ]
    report = "\n\n".join(report_parts).strip()

    if not report:
        raise RuntimeError("L'agent n'a produit aucune analyse exploitable.")

    return {"report": report, "plot_url": None}
