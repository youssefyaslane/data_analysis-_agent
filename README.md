# Data Analysis Agent

Application web (Flask) permettant de téléverser un fichier CSV, de l'analyser via un
**agent LangChain** (lecture des données, statistiques, corrélations, top performeurs),
puis d'afficher le rapport d'insights dans le navigateur.

> La génération de graphique est désactivée pour l'instant (analyse textuelle
> uniquement), afin de limiter le nombre d'appels au LLM. Pourra être réactivée plus tard.

**LLM utilisé :** OpenAI (`gpt-4o-mini` par défaut, via `langchain-openai`).

## Structure du projet

```
data_analysis_agent/
├── src/
│   ├── agent/                  # package d'analyse
│   │   ├── config.py           # configuration (.env, chemins)
│   │   ├── tools.py            # outil read_csv_summary
│   │   └── analysis_agent.py   # agent LangGraph + run_analysis()
│   └── web/                    # application web Flask
├── tests/
│   └── manual_test_agent.py    # script de test manuel de l'agent
├── uploads/                    # CSV téléversés
├── .env.example
├── .gitignore
└── requirements.txt
```

## Prérequis

- [uv](https://docs.astral.sh/uv/) installé
- Python 3.12 (installé automatiquement par uv si besoin)
- Une clé API OpenAI

## Installation (dev local avec uv)

```powershell
# 1. Créer l'environnement virtuel avec Python 3.12
uv venv --python 3.12

# 2. Activer l'environnement
.venv\Scripts\Activate.ps1

# 3. Installer les dépendances
uv pip install flask pandas python-dotenv langchain langchain-openai langgraph

# 4. (Optionnel) Figer les versions
uv pip freeze > requirements.txt

# 5. Vérifier l'installation
uv run python -c "import flask, pandas, langchain_openai, langgraph; print('OK')"
```

> Ce projet utilise le workflow `uv venv` + `uv pip install` (pas de `pyproject.toml`).

## Configuration

Copier `.env.example` vers `.env` et renseigner la clé API OpenAI :

```powershell
Copy-Item .env.example .env
```

Variables lues par l'application (voir `.env.example`) :

| Variable | Rôle |
|---|---|
| `OPENAI_API_KEY` | Clé API OpenAI |
| `AGENT_MODEL` | Modèle utilisé par l'agent (déf. `openai:gpt-4o-mini`) |
| `LANGSMITH_TRACING` | Active le tracing LangSmith (`true`/`false`) |
| `LANGSMITH_API_KEY` | Clé API LangSmith |
| `LANGSMITH_PROJECT` | Nom du projet LangSmith |

## Modules

### `src/agent/config.py`

Configuration centrale du package agent :
- charge le `.env` (via `python-dotenv`) ;
- expose la config LLM (`OPENAI_API_KEY`, `AGENT_MODEL`) et LangSmith ;
- définit et crée les dossiers de travail (`uploads/`, `src/web/static/plots/`) ;
- `validate()` : vérifie la présence de la clé OpenAI et lève une erreur claire sinon.

### `src/agent/tools.py`

Outil `read_csv_summary(path)` exposé à l'agent — lit le CSV avec pandas et
retourne en un seul appel :
- dimensions, types de colonnes, valeurs manquantes ;
- corrélations entre colonnes numériques (hors colonnes identifiants, ex. `Order ID`) ;
- top 5 par colonne catégorielle à faible cardinalité (ex. meilleure région par
  chiffre d'affaires) ;
- statistiques descriptives (`describe()`) ;
- les données complètes si le fichier fait ≤ 500 lignes, sinon un échantillon de
  50 lignes (pour maîtriser le coût en tokens sur les gros fichiers).

### `src/agent/analysis_agent.py`

Construit l'agent avec `langgraph.prebuilt.create_react_agent` (agent LangChain léger,
sans framework `deepagents`) et expose `run_analysis(csv_relative_path)` :
- un seul outil (`read_csv_summary`) et un prompt système court ;
- extrait le texte des messages IA de la conversation comme rapport d'insights ;
- lève une erreur claire si l'agent ne produit aucune analyse exploitable.

> Testé de bout en bout avec `tests/manual_test_agent.py` : l'agent lit le CSV,
> calcule les agrégations pertinentes et rédige un rapport d'insights structuré.

## Avancement

- [x] Structure du projet + environnement `uv`
- [x] Configuration de l'agent (`src/agent/config.py`)
- [x] Outil d'analyse CSV (`src/agent/tools.py`)
- [x] Agent d'analyse (`src/agent/analysis_agent.py`) — testé de bout en bout
- [ ] Interface web Flask (`src/web/`)
- [ ] Lancement local de bout en bout
- [ ] Conteneurisation Docker
