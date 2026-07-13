"""Étape de lecture CSV du workflow d'analyse.

Fonction déterministe (aucun appel LLM) qui lit un CSV et retourne un
résumé structuré, utilisé comme première étape du workflow LangGraph.
"""
from __future__ import annotations

import pandas as pd

from agent import config

# Au-delà de ce nombre de lignes, on n'envoie plus le CSV entier au modèle
# (coût de tokens) mais un échantillon, complété par les statistiques agrégées.
MAX_FULL_ROWS = 500


def summarize_csv(path: str) -> str:
    """Lit un fichier CSV et retourne un résumé structuré de son contenu."""
    resolved = (config.PROJECT_ROOT / path).resolve()

    if not resolved.is_file():
        return f"Erreur : fichier introuvable : {path}"

    try:
        df = pd.read_csv(resolved)
    except Exception as e:  # noqa: BLE001 - remonter l'erreur au workflow plutôt que planter
        return f"Erreur lors de la lecture du CSV : {e}"

    parts = [
        f"Dimensions : {df.shape[0]} lignes, {df.shape[1]} colonnes",
        "",
        "Colonnes et types :",
        df.dtypes.to_string(),
        "",
        "Valeurs manquantes par colonne :",
        df.isna().sum().to_string(),
    ]

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    # Colonnes numériques exploitables comme métriques : on exclut les
    # identifiants probables (nom contenant "id").
    metric_cols = [c for c in numeric_cols if "id" not in c.lower()]

    if len(metric_cols) >= 2:
        parts += [
            "",
            "Corrélations entre colonnes numériques :",
            df[metric_cols].corr().round(3).to_string(),
        ]

    if metric_cols:
        categorical_cols = [
            c for c in df.columns
            if c not in numeric_cols and df[c].nunique() <= 15
        ]
        for col in categorical_cols:
            top = (
                df.groupby(col)[metric_cols]
                .sum()
                .sort_values(metric_cols[0], ascending=False)
                .head(5)
            )
            parts += [
                "",
                f"Top 5 '{col}' par {metric_cols[0]} (somme) :",
                top.to_string(),
            ]

    parts += [
        "",
        "Statistiques descriptives :",
        df.describe(include="all").to_string(),
    ]

    if df.shape[0] <= MAX_FULL_ROWS:
        parts += ["", f"Données complètes ({df.shape[0]} lignes) :", df.to_string()]
    else:
        sample = df.sample(50, random_state=0)
        parts += [
            "",
            f"Fichier volumineux ({df.shape[0]} lignes) : échantillon de "
            "50 lignes ci-dessous, appuie-toi sur les statistiques "
            "ci-dessus pour le reste.",
            sample.to_string(),
        ]

    return "\n".join(parts)
