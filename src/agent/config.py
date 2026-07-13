"""Configuration centrale du package agent.

Charge les variables d'environnement (.env) et expose la configuration
utilisée par le backend, les outils et l'agent d'analyse.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Racine du projet : src/agent/config.py -> remonte de 3 niveaux
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Charge le .env situé à la racine du projet
load_dotenv(PROJECT_ROOT / ".env")

# ─── LLM : OpenAI ─────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
AGENT_MODEL = os.getenv("AGENT_MODEL", "openai:gpt-4o-mini")

# ─── LangSmith (tracing) ─────────────────────────────
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "data-analysis-agent")

# ─── Chemins de travail ──────────────────────────────
UPLOADS_DIR = PROJECT_ROOT / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def validate() -> None:
    """Vérifie que la configuration minimale est présente."""
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY manquante : renseigne-la dans le fichier .env "
            "(voir .env.example)."
        )
