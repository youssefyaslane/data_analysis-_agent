# Data Analysis Agent

Application web (Flask) permettant de téléverser un fichier CSV, de l'analyser via un
**workflow LangGraph** (lecture des données, statistiques, corrélations, top performeurs,
génération d'insights), puis d'afficher le rapport dans le navigateur.

Le workflow est volontairement un **graphe à étapes fixes** plutôt qu'un agent autonome :
la lecture du CSV (pandas, aucun appel LLM) précède un unique appel au LLM pour rédiger
les insights. Résultat : coût et nombre d'appels prévisibles, et une trace LangSmith nette
(un nœud par étape) plutôt qu'une boucle d'agent imprévisible.

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
│   │   └── analysis_agent.py   # workflow LangGraph (StateGraph) + run_analysis()
│   └── web/                    # application web Flask
│       ├── config.py           # config Flask (.env, upload)
│       ├── agent_client.py     # pont vers l'agent + rendu Markdown
│       ├── routes.py           # blueprint : / et /analyze
│       ├── app.py              # create_app()
│       ├── templates/          # base.html, index.html, result.html
│       └── static/css/         # style.css
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
uv pip install flask pandas python-dotenv langchain langchain-openai langgraph markdown

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
| `FLASK_SECRET_KEY` | Clé secrète Flask (sessions, messages flash) |
| `MAX_UPLOAD_MB` | Taille max d'upload en Mo (déf. 10) |

## Modules

### `src/agent/config.py`

Configuration centrale du package agent :
- charge le `.env` (via `python-dotenv`) ;
- expose la config LLM (`OPENAI_API_KEY`, `AGENT_MODEL`) et LangSmith ;
- définit et crée les dossiers de travail (`uploads/`, `src/web/static/plots/`) ;
- `validate()` : vérifie la présence de la clé OpenAI et lève une erreur claire sinon.

### `src/agent/tools.py`

`summarize_csv(path)` — fonction déterministe (aucun appel LLM), lit le CSV avec
pandas et retourne un résumé structuré :
- dimensions, types de colonnes, valeurs manquantes ;
- corrélations entre colonnes numériques (hors colonnes identifiants, ex. `Order ID`) ;
- top 5 par colonne catégorielle à faible cardinalité (ex. meilleure région par
  chiffre d'affaires) ;
- statistiques descriptives (`describe()`) ;
- les données complètes si le fichier fait ≤ 500 lignes, sinon un échantillon de
  50 lignes (pour maîtriser le coût en tokens sur les gros fichiers).

### `src/agent/analysis_agent.py`

Workflow `langgraph.graph.StateGraph` à deux nœuds, et `run_analysis(csv_relative_path)` :
- **`read_csv`** — appelle `summarize_csv` (étape déterministe, pas de LLM) ;
- **`generate_insights`** — un seul appel au LLM à partir du résumé, pour rédiger
  le rapport d'insights ;
- lève une erreur claire si le workflow ne produit aucune analyse exploitable.

> Testé de bout en bout avec `tests/manual_test_agent.py`. Tracing LangSmith vérifié
> (projet `data-analysis-agent`) : le graphe apparaît avec ses 2 nœuds distincts et un
> seul appel `ChatOpenAI`, confirmant le comportement déterministe du workflow.

### `src/web/config.py`

Configuration Flask : dossier d'upload (réutilise `agent.config.UPLOADS_DIR`),
extensions autorisées (`.csv`), taille max d'upload, clé secrète.

### `src/web/agent_client.py`

Pont entre les routes et l'agent :
- appelle `run_analysis()` et enveloppe toute erreur dans `AnalysisError` (message
  propre affiché à l'utilisateur plutôt qu'une trace Python) ;
- convertit le rapport Markdown de l'agent en HTML (`markdown`) pour un rendu
  correctement mis en forme (titres, gras, listes) côté navigateur.

### `src/web/routes.py`

Blueprint `main` :
- `GET /` — formulaire d'upload ;
- `POST /analyze` — valide le fichier (présence, extension), le sauvegarde avec
  un nom sécurisé, lance l'analyse et affiche le résultat (ou un message d'erreur
  via `flash` en cas d'échec).

### `src/web/app.py`

Fabrique `create_app()` : configure Flask depuis `web.config`, enregistre le
blueprint. Un bootstrap ajoute `src/` à `sys.path` pour pouvoir lancer
`python src/web/app.py` directement, quel que soit le dossier courant.

### Templates & CSS

Design moderne (cartes avec ombre, accent indigo, thème clair/sombre automatique) :
- `base.html` — en-tête, messages flash, structure commune ;
- `index.html` — formulaire d'upload ;
- `result.html` — rapport rendu en HTML sémantique (titres, listes, gras) +
  graphique optionnel ;
- `static/css/style.css` — sans dépendance externe (pas de CDN).

## Lancer l'application

```powershell
.venv\Scripts\Activate.ps1
python src\web\app.py
```

Ouvrir http://127.0.0.1:5000, téléverser un CSV, cliquer "Analyser".

## Avancement

- [x] Structure du projet + environnement `uv`
- [x] Configuration de l'agent (`src/agent/config.py`)
- [x] Outil d'analyse CSV (`src/agent/tools.py`)
- [x] Agent d'analyse (`src/agent/analysis_agent.py`) — testé de bout en bout
- [x] Interface web Flask (`src/web/`) — testée de bout en bout dans le navigateur
- [x] Lancement local de bout en bout
- [ ] Conteneurisation Docker
