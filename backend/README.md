# CampusFlow Lite — Backend

> API REST FastAPI pour la visualisation de congestion du campus, le calcul d'itinéraires, la prédiction ML et la gestion des feedbacks étudiants.

---

## Table des matières

- [Stack technique](#stack-technique)
- [Structure du projet](#structure-du-projet)
- [Endpoints API](#endpoints-api)
- [Lancement](#lancement)
- [Tests](#tests)
- [Bonnes pratiques](#bonnes-pratiques)
- [Évolutions possibles](#évolutions-possibles)
- [Dépannage](#dépannage)

---

## Stack technique

| Outil | Rôle |
|---|---|
| **FastAPI** | Framework web, validation Pydantic, Swagger auto-généré |
| **PostgreSQL** | Base de données relationnelle persistante |
| **Redis** | Cache distribué pour la congestion temps réel (TTL 60s) |
| **SQLAlchemy** | ORM pour l'abstraction de la base de données |
| **NetworkX** | Calcul du plus court chemin (Dijkstra) |
| **Scikit-learn** | Modèle Random Forest pour la prédiction de congestion |
| **Docker Compose** | Orchestration des services (backend, PostgreSQL, Redis) |

---

## Structure du projet

```
campusflow-backend/
├── app/
│   ├── main.py                   # Point d'entrée FastAPI (CORS, routes, erreurs)
│   ├── database/
│   │   ├── session.py            # Configuration SQLAlchemy
│   │   └── models.py             # Tables ORM : Location, Flux, Schedule, Feedback
│   ├── schemas/                  # Modèles Pydantic (validation & sérialisation)
│   ├── routers/                  # Endpoints API (locations, congestion, flux, path…)
│   ├── services/                 # Logique métier (algorithmes, calculs, accès DB)
│   ├── ml/
│   │   └── model.py              # Chargement et inférence du modèle Random Forest
│   └── utils/
│       ├── redis_client.py       # Client Redis
│       ├── errors.py             # Handler global d'erreurs HTTP
│       └── seed.py               # Peuplement initial de la base
├── tests/                        # Tests unitaires et d'intégration (pytest)
├── models/                       # Modèle ML entraîné : congestion_rf.pkl
├── migrations/                   # Scripts Alembic
├── requirements.txt
├── requirements-dev.txt          # pytest, httpx, fakeredis
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Endpoints API

**Base URL :** `http://localhost:8000` — Documentation interactive : [`/docs`](http://localhost:8000/docs)

### `GET /locations`
Liste des bâtiments actifs.  
Paramètres : `?type=amphi` · `?active=false`  
Réponse : `[{id, name, latitude, longitude, type, capacity, is_active, …}]`

### `GET /congestion`
Niveau de congestion actuel (Redis ou PostgreSQL).  
Paramètre : `?location_id=5`  
Réponse : `[{location_id, level, occupancy_rate, current_count, updated_at}]`

### `GET /flux/live`
Flux entrants/sortants sur les dernières minutes.  
Paramètre : `?window=5`  
Réponse : `[{location_id, entries, exits, net_flow, timestamp}]`

### `GET /flux/history/{location_id}`
Historique d'un bâtiment sur une plage de dates.  
Paramètres : `?from=ISO8601&to=ISO8601&granularity=hour`  
Réponse : `{location_id, period, granularity, data: [{timestamp, count, entries, exits}]}`

### `GET /path`
Plus court chemin entre deux bâtiments (Dijkstra).  
Paramètres : `?from=1&to=7&avoid_congestion=true`  
Réponse : `{path, total_distance, estimated_time, waypoints: [{lat, lng}]}`

### `POST /predict`
Prédiction de congestion future via Random Forest.  
Body : `{location_id, datetime, event_type?}`  
Réponse : `{location_id, predicted_level, confidence, predicted_occupancy_rate, model_version}`

### `GET /feedbacks`
Feedbacks étudiants avec filtres et pagination.  
Paramètres : `?location_id=1&sentiment=negative&limit=20&offset=0`  
Réponse : `{total, limit, offset, items: [{id, content, rating, sentiment, …}]}`

### `GET /dashboard/stats`
Agrégats pour le tableau de bord.  
Paramètre : `?period=week` (`day` / `week` / `month`)  
Réponse : `{top_locations, peak_hours, avg_congestion_by_day, feedback_summary, total_flux}`

---

## Lancement

### Prérequis

- Docker & Docker Compose installés
- Ports `8000`, `5432`, `6379` libres

### Démarrage

```bash
# 1. Configurer les variables d'environnement
cp .env.example .env

# 2. Construire et lancer les conteneurs
docker-compose up --build
```

L'API est accessible sur **http://localhost:8000**.

### Peupler la base de données

```bash
docker exec -it campusflow-backend-backend-1 bash
python -c "
from app.database.session import SessionLocal
from app.utils.seed import seed_database
db = SessionLocal()
seed_database(db)
db.close()
"
```

### Vérification

```bash
curl http://localhost:8000/
```

### Arrêt

```bash
docker-compose down
```

---

## Tests

Les tests utilisent une base **SQLite en mémoire** et **fakeredis** — aucun service Docker requis.

```bash
# Installer les dépendances de développement
pip install -r requirements-dev.txt

# Lancer tous les tests
pytest tests/ -v

# Lancer un test spécifique
pytest tests/test_path.py -v

# Ou via Docker
docker-compose run --rm backend pytest tests/
```

**Couverture des tests :**
- Validité des réponses HTTP (200, 404, 422…)
- Comportement des services (Dijkstra, cache Redis, agrégations SQL)
- Cas limites (bâtiment introuvable, chemin identique, paramètres invalides)

---

## Bonnes pratiques

- **Validation stricte** — corps de requête validés par Pydantic, erreurs `422` avec détails
- **Gestion centralisée des erreurs** — format JSON uniforme via `http_exception_handler`
- **Cache Redis** — données de congestion mises en cache 60 secondes
- **Architecture en couches** — `routers → services → modèles`
- **Configuration par variables d'environnement** — aucune donnée sensible en dur
- **Docker Compose production-ready** — healthchecks et politiques de redémarrage

---

## Évolutions possibles

- **Graphe NetworkX** — remplacer les distances euclidiennes par des arêtes réelles
- **Authentification** — ajouter JWT (`/auth/login`, `/auth/register`)
- **WebSockets** — polling temps réel plus efficace que les requêtes GET périodiques
- **ML avancé** — remplacer Random Forest par XGBoost ou un réseau LSTM
- **Monitoring** — intégrer Prometheus + Grafana (latence, taux d'erreur)

---

## Dépannage

| Problème | Solution |
|---|---|
| `ModuleNotFoundError` au démarrage | Vérifier que `PYTHONPATH=/app` est défini dans le Dockerfile |
| Redis refuse la connexion | Vérifier que le service `redis` est healthy : `docker-compose ps` |
| Les endpoints retournent `[]` | Base vide — exécuter le script `seed.py` |
| `/predict` renvoie `503` | `congestion_rf.pkl` introuvable — lancer `train_model.py` |
| Tests en échec avec `ImportError` | Installer les dépendances ou utiliser `docker-compose run` |

---

Bon hackathon ! 🚀