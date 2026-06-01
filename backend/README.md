# CampusFlow Lite — Backend API

API REST FastAPI pour la gestion des flux, de la congestion et du routage sur un campus universitaire. Le backend s’appuie sur PostgreSQL (données persistées) et Redis (cache congestion).

Les jeux de données et le schéma SQL sont gérés dans le dossier **`../data/`** (génération CSV, `schema.sql`, `load_postgres.py`). Ce dépôt backend ne contient plus de dossiers `ml/` ni `models/` locaux.

---

## Stack technique

| Composant | Technologie | Usage |
| :--- | :--- | :--- |
| Framework | FastAPI | API REST, documentation Swagger |
| Base de données | PostgreSQL | Lieux, flux, emplois du temps, feedbacks |
| Cache | Redis | Congestion (TTL ~60 s) |
| Algorithmique | NetworkX | Itinéraires (Dijkstra) |
| ML (inférence) | scikit-learn / joblib | Prédiction via fichier `.pkl` externe |
| ORM | SQLAlchemy | Accès base de données |
| Validation | Pydantic v2 | Schémas requête / réponse |

---

## Structure du projet

```text
backend/
├── app/
│   ├── main.py              # Point d'entrée FastAPI
│   ├── config.py            # Variables d'environnement
│   ├── database/
│   │   ├── session.py       # Engine SQLAlchemy, get_db
│   │   ├── models.py        # Modèles ORM
│   │   └── init_db.py       # Initialisation (dev)
│   ├── schemas/             # Schémas Pydantic
│   ├── routers/             # Routes HTTP
│   ├── services/            # Logique métier (+ predict_service.py)
│   └── utils/               # Redis, erreurs, seed
├── docker-compose.yml       # PostgreSQL + Redis + backend
├── Dockerfile
├── .env.example
└── README.md
```

| Couche | Rôle |
| :--- | :--- |
| `database/models.py` | Entités SQL (tables) |
| `routers/` | Endpoints et injection `get_db` |
| `services/` | Congestion, flux, pathfinding, dashboard, prédiction ML |
| `schemas/` | Contrats JSON API |

---

## Prérequis

- Python 3.11+ (3.12 testé)
- PostgreSQL (données chargées depuis `data/`, voir [data/README.md](../data/README.md))
- Redis
- **Optionnel** — fichier modèle scikit-learn (`.pkl`) pour `POST /predict`

---

## Installation

Depuis la **racine du monorepo** :

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
```

Copier la configuration :

```bash
cd backend
copy .env.example .env   # Windows
# cp .env.example .env   # Linux / macOS
```

Variables utiles (`.env` ou shell) :

| Variable | Description | Exemple |
| :--- | :--- | :--- |
| `DATABASE_URL` | Connexion PostgreSQL | `postgresql://campusflow:securepass@localhost:5432/campusflow` |
| `REDIS_URL` | Connexion Redis | `redis://localhost:6379/0` |
| `ML_MODEL_PATH` | Chemin absolu vers le `.pkl` (predict) | `C:/chemin/vers/model.pkl` |
| `CORS_ORIGINS` | Origines frontend (virgules) | `http://localhost:5173` |

> **Windows / PowerShell** : pour un chemin local, utiliser des **guillemets simples**  
> `$env:ML_MODEL_PATH = 'C:/Users/.../model.pkl'`  
> (évite l’erreur d’échappement `\U` dans `c:\Users\...`).

Charger les données (une fois PostgreSQL démarré) :

```bash
# depuis la racine du repo
python data/load_postgres.py
```

---

## Lancer l’API

**Important** : exécuter uvicorn depuis le dossier `backend/` (le package Python s’appelle `app`).

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Racine : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- Swagger : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc : [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Docker Compose

```bash
cd backend
docker compose up --build
```

Adapter `docker-compose.yml` si vous montez un volume pour le modèle ML (`ML_MODEL_PATH` dans le service `backend`).

---

## Endpoints principaux

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Santé de l’API |
| `GET` | `/locations` | Liste des lieux |
| `GET` | `/congestion` | Congestion actuelle (cache Redis) |
| `GET` | `/flux/live` | Flux récents |
| `GET` | `/flux/history/{location_id}` | Historique des flux |
| `GET` | `/path` | Itinéraire optimal (NetworkX) |
| `POST` | `/predict` | Prédiction d’affluence (nécessite `ML_MODEL_PATH`) |
| `GET` | `/dashboard/stats` | Statistiques tableau de bord |
| `GET` | `/feedbacks` | Liste des feedbacks (filtres query) |

### Exemple — `POST /predict`

Corps JSON :

```json
{
  "location_id": 1,
  "datetime": "2026-05-15T14:00:00",
  "event_type": "cours"
}
```

PowerShell :

```powershell
$body = @{
  location_id = 1
  datetime    = "2026-05-15T14:00:00"
  event_type  = "cours"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method POST -ContentType "application/json" -Body $body
```

Réponses fréquentes : **200** (OK), **404** (lieu inconnu), **503** (fichier modèle absent ou non chargé), **422** (JSON invalide).

---

## Données et schéma PostgreSQL

Le schéma de référence (tables `locations`, `flux`, `schedules`, `feedbacks`) est dans **`data/db/schema.sql`**. Les CSV sont produits par les scripts sous `data/raw/`.

Le backend crée aussi les tables ORM au démarrage (`Base.metadata.create_all` dans `main.py`) ; en production, privilégier le schéma `data/` + `load_postgres.py` pour rester aligné avec les datasets.

---

## Prédiction ML (fichier externe)

L’inférence est dans `app/services/predict_service.py` : au premier appel, le service charge le modèle depuis `ML_MODEL_PATH` (défaut historique `/ml/model.pkl`, à surcharger).

1. Entraîner ou obtenir un modèle scikit-learn compatible (features : `location_id`, jour, heure, type d’événement).
2. Définir `ML_MODEL_PATH` vers ce fichier `.pkl`.
3. S’assurer que `location_id` existe en base.

Sans modèle valide, `POST /predict` renvoie **503**.

---

## Bonnes pratiques

- Validation des entrées via Pydantic (`schemas/`).
- Erreurs HTTP centralisées (`utils/errors.py`).
- Cache Redis sur la congestion pour limiter la charge PostgreSQL.
- Logique métier isolée dans `services/`, routes fines dans `routers/`.

---

## Dépannage

| Erreur | Cause probable | Action |
| :--- | :--- | :--- |
| `No module named 'app'` | uvicorn lancé hors de `backend/` | `cd backend` puis relancer |
| Syntaxe chemin Windows | `$env:VAR = "c:\Users\..."` | Guillemets simples ou `/` |
| `503` sur `/predict` | `ML_MODEL_PATH` incorrect ou fichier absent | Vérifier le chemin et `Test-Path` |
| Connexion DB | PostgreSQL arrêté ou mauvaise URL | Vérifier `DATABASE_URL` et `load_postgres.py` |

---

CampusFlow Lite.
