"""Backend d'exécution du deep agent (dev local).

En local, le backend opère directement sur le vrai dossier du projet :
les fichiers déposés dans uploads/ sont donc accessibles sans upload.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from deepagents.backends import LocalShellBackend

from agent import config


def create_backend() -> LocalShellBackend:
    """Crée le backend local pour exécuter le code d'analyse."""
    # Met le venv du projet en tête du PATH pour que `python` = interpréteur
    # du projet (pandas, matplotlib, seaborn disponibles).
    venv_scripts = str(Path(sys.executable).parent)
    path = venv_scripts + os.pathsep + os.environ.get("PATH", "")

    return LocalShellBackend(
        root_dir=str(config.PROJECT_ROOT),
        virtual_mode=False,
        inherit_env=True,
        env={"PATH": path},
        timeout=180,
    )
