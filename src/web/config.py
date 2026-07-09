"""Configuration de l'application web Flask."""
from __future__ import annotations

import os

from agent import config as agent_config

UPLOAD_FOLDER = agent_config.UPLOADS_DIR
ALLOWED_EXTENSIONS = {"csv"}

_MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "10"))
MAX_CONTENT_LENGTH = _MAX_UPLOAD_MB * 1024 * 1024

SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key-change-in-production")


def allowed_file(filename: str) -> bool:
    """Vérifie que le fichier a une extension autorisée."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
