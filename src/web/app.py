"""Point d'entrée de l'application web Flask."""
from __future__ import annotations

import sys
from pathlib import Path

# Permet de lancer ce fichier directement (python src/web/app.py) en ajoutant
# src/ au chemin d'import, quel que soit le dossier courant.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from flask import Flask

from web import config as web_config
from web.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=web_config.SECRET_KEY,
        MAX_CONTENT_LENGTH=web_config.MAX_CONTENT_LENGTH,
        UPLOAD_FOLDER=str(web_config.UPLOAD_FOLDER),
    )
    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
