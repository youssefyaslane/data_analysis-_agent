# Data Analysis Agent

Application web (Flask) permettant de téléverser un fichier CSV, de l'analyser via un
**deep agent** LangChain (exploration, statistiques, génération de graphique), puis
d'afficher le rapport et la visualisation dans le navigateur.

**LLM utilisé :** Google Gemini (via `langchain-google-genai`).

## Structure du projet

```
data_analysis_agent/
├── src/
│   ├── agent/              # package d'analyse (deep agent)
│   └── web/                # application web Flask
├── tests/
├── uploads/                # CSV téléversés
├── .env.example
├── .gitignore
└── requirements.txt
```

## Prérequis

- [uv](https://docs.astral.sh/uv/) installé
- Python 3.12 (installé automatiquement par uv si besoin)
- Une clé API Google Gemini

## Installation (dev local avec uv)

```powershell
# 1. Créer l'environnement virtuel avec Python 3.12
uv venv --python 3.12

# 2. Activer l'environnement
.venv\Scripts\Activate.ps1

# 3. Installer les dépendances
uv pip install deepagents flask pandas matplotlib seaborn python-dotenv langchain-google-genai

# 4. (Optionnel) Figer les versions
uv pip freeze > requirements.txt

# 5. Vérifier l'installation
uv run python -c "import flask, pandas, deepagents, langchain_google_genai; print('OK')"
```

> Ce projet utilise le workflow `uv venv` + `uv pip install` (pas de `pyproject.toml`).

## Configuration

Copier `.env.example` vers `.env` et renseigner la clé API Gemini :

```powershell
Copy-Item .env.example .env
```
