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

Variables lues par l'application (voir `.env.example`) :

| Variable | Rôle |
|---|---|
| `GOOGLE_API_KEY` | Clé API Google Gemini |
| `AGENT_MODEL` | Modèle utilisé par l'agent (déf. `google_genai:gemini-3.5-flash`) |
| `LANGSMITH_TRACING` | Active le tracing LangSmith (`true`/`false`) |
| `LANGSMITH_API_KEY` | Clé API LangSmith |
| `LANGSMITH_PROJECT` | Nom du projet LangSmith |

## Modules

### `src/agent/config.py`

Configuration centrale du package agent :
- charge le `.env` (via `python-dotenv`) ;
- expose la config LLM (`GOOGLE_API_KEY`, `AGENT_MODEL`) et LangSmith ;
- définit et crée les dossiers de travail (`uploads/`, `src/web/static/plots/`) ;
- `validate()` : vérifie la présence de la clé Gemini et lève une erreur claire sinon.

### `src/agent/backend.py`

Backend d'exécution local du deep agent (`LocalShellBackend`) :
- `root_dir` pointe sur la racine du projet → l'agent accède directement aux vrais
  fichiers (`uploads/`, `src/web/static/plots/`), sans étape d'upload ;
- le `PATH` transmis au backend place l'interpréteur du `.venv` du projet en tête,
  pour que les commandes `python …` lancées par l'agent utilisent le bon interpréteur
  (avec pandas / matplotlib / seaborn installés) ;
- `timeout=180` pour laisser le temps aux scripts d'analyse de s'exécuter.

> Note : ces modules sont conçus comme un package (`from agent import config`), pas
> comme des scripts autonomes. Pour un test manuel, lancer depuis la racine du projet
> avec `PYTHONPATH=src`, ou avec `python -m agent.backend` depuis `src/`.

### `src/agent/tools.py`

Outil custom `save_plot(source_path)` exposé au deep agent :
- l'agent génère un graphique (ex. `plt.savefig('output/plot.png')`) dans le vrai
  système de fichiers via le backend local ;
- l'outil vérifie que le fichier existe et est un `.png`, le copie dans
  `src/web/static/plots/` sous un nom unique (UUID) pour éviter les collisions
  entre analyses ;
- retourne l'URL web (`/static/plots/<uuid>.png`) que la page de résultat utilisera
  directement dans une balise `<img>` ;
- erreurs (fichier absent, mauvaise extension) renvoyées comme message texte à
  l'agent plutôt que comme exception, pour ne pas casser le run.

## Avancement

- [x] Structure du projet + environnement `uv`
- [x] Configuration de l'agent (`src/agent/config.py`)
- [x] Backend d'exécution (`src/agent/backend.py`)
- [x] Outils custom (`src/agent/tools.py`)
- [ ] Agent d'analyse (`src/agent/analysis_agent.py`)
- [ ] Interface web Flask (`src/web/`)
- [ ] Lancement local de bout en bout
- [ ] Conteneurisation Docker
