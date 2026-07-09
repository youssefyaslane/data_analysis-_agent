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

# ─── LLM : Google Gemini ─────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
AGENT_MODEL = os.getenv("AGENT_MODEL", "google_genai:gemini-3.5-flash")

# ─── LangSmith (tracing) ─────────────────────────────
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "false")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "data-analysis-agent")

# ─── Chemins de travail ──────────────────────────────
UPLOADS_DIR = PROJECT_ROOT / "uploads"
PLOTS_DIR = PROJECT_ROOT / "src" / "web" / "static" / "plots"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def validate() -> None:
    """Vérifie que la configuration minimale est présente."""
    if not GOOGLE_API_KEY:
        raise RuntimeError(
            "GOOGLE_API_KEY manquante : renseigne-la dans le fichier .env "
            "(voir .env.example)."
        )
