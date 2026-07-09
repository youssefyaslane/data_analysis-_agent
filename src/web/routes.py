"""Routes de l'application web : upload et affichage des résultats."""
from __future__ import annotations

from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from web import config as web_config
from web.agent_client import AnalysisError, analyze_csv

bp = Blueprint("main", __name__)


@bp.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@bp.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("csv_file")

    if file is None or file.filename == "":
        flash("Merci de sélectionner un fichier CSV.")
        return redirect(url_for("main.index"))

    if not web_config.allowed_file(file.filename):
        flash("Seuls les fichiers .csv sont acceptés.")
        return redirect(url_for("main.index"))

    filename = secure_filename(file.filename)
    destination = Path(web_config.UPLOAD_FOLDER) / filename
    file.save(destination)

    try:
        result = analyze_csv(filename)
    except AnalysisError as e:
        flash(f"L'analyse a échoué : {e}")
        return redirect(url_for("main.index"))

    return render_template(
        "result.html",
        filename=filename,
        report_html=result["report_html"],
        plot_url=result["plot_url"],
    )
