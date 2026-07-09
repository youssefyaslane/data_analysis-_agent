"""Outils custom du deep agent.

Fournit un outil pour publier un graphique généré par l'agent dans le
dossier statique de la web app, afin qu'il soit affichable via une URL.
"""
from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from langchain.tools import tool

from agent import config


@tool(parse_docstring=True)
def save_plot(source_path: str) -> str:
    """Publie un graphique généré pour qu'il soit affichable par la web app.

    Args:
        source_path: Chemin du fichier image (.png) généré par le script
            d'analyse, relatif à la racine du projet.
    """
    resolved = (config.PROJECT_ROOT / source_path).resolve()

    if not resolved.is_file():
        return f"Erreur : fichier introuvable : {source_path}"
    if resolved.suffix.lower() != ".png":
        return f"Erreur : extension non supportée ({resolved.suffix}), seul .png est accepté"

    unique_name = f"{uuid.uuid4().hex}.png"
    destination = config.PLOTS_DIR / unique_name
    shutil.copy2(resolved, destination)

    return f"/static/plots/{unique_name}"
