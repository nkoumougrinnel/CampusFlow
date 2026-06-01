# CampusFlow Lite — Backend API

**CampusFlow Lite** est le cœur opérationnel d'une plateforme de gestion des flux et de la congestion sur un campus universitaire. Développé dans le cadre du **Hackathon 2025**, ce backend expose une API REST performante pour centraliser la logique métier, le routage optimal, et les prédictions par Machine Learning.

---

## 🚀 Stack Technique

Le projet repose sur une stack moderne et robuste, choisie pour sa rapidité de développement et ses performances :

| Composant | Technologie | Usage |
| :--- | :--- | :--- |
| **Framework** | **FastAPI** | Création de l'API REST haute performance. |
| **Base de données** | **PostgreSQL** | Stockage persistant des données (locations, flux, feedbacks). |
| **Cache / Temps réel** | **Redis** | Mise en cache de la congestion avec TTL (60s). |
| **Algorithmique** | **NetworkX** | Calcul d'itinéraires optimaux (Dijkstra). |
| **Machine Learning** | **Scikit-learn** | Prédiction de l'affluence via Random Forest. |
| **ORM** | **SQLAlchemy** | Abstraction et gestion de la base de données. |
| **Validation** | **Pydantic v2** | Garantie de l'intégrité des données d'entrée/sortie. |

---

## 🏗️ Architecture du Projet

Le projet suit une structure modulaire et scalable, séparant clairement les responsabilités :

```text
app/
├── main.py             # Point d'entrée FastAPI
├── database/           # Configuration SQLAlchemy & sessions
├── models/             # Modèles ORM (PostgreSQL)
├── schemas/            # Schémas de validation Pydantic
├── routers/            # Définition des endpoints API
├── services/           # Logique métier (congestion, pathfinding, ML)
├── utils/              # Helpers (Redis, erreurs, réponses)
└── ml/                 # Inférence Machine Learning (Random Forest)
```

### Responsabilités des Couches
*   **Models** : Définition des entités SQL sans logique métier.
*   **Routers** : Gestion des routes HTTP et injection de dépendances.
*   **Services** : Cœur de la logique métier (calculs NetworkX, agrégations).
*   **ML Layer** : Module d'inférence isolé chargeant le modèle au démarrage.

---

## 🛠️ Installation et Configuration

### Prérequis
*   Python 3.11+
*   PostgreSQL
*   Redis

### Installation
1.  **Cloner le dépôt** :
    ```bash
    git clone https://github.com/votre-repo/campusflow-lite-backend.git
    cd campusflow-lite-backend
    ```
2.  **Installer les dépendances** :
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configurer les variables d'environnement** (`.env`) :
    ```env
    DATABASE_URL=postgresql://user:password@localhost/campusflow
    REDIS_URL=redis://localhost:6379/0
    ```
4.  **Lancer l'application** :
    ```bash
    uvicorn app.main:app --reload
    ```

---

## 📡 Documentation de l'API (Endpoints)

L'API est documentée automatiquement via Swagger à l'adresse `/docs`. Voici les endpoints principaux :

### Gestion du Campus
*   `GET /locations` : Liste des bâtiments avec coordonnées GPS et métadonnées.
*   `GET /path` : Calcul de l'itinéraire optimal entre deux points (NetworkX).

### Flux & Congestion
*   `GET /congestion` : Niveau de congestion actuel (données cachées dans Redis).
*   `GET /flux/live` : Flux de personnes en temps réel.
*   `GET /flux/history/{id}` : Historique des flux pour un bâtiment spécifique.

### Intelligence Artificielle
*   `POST /predict` : Prédiction de l'affluence future basée sur le modèle Random Forest.
*   `GET /dashboard/stats` : Statistiques agrégées pour le tableau de bord.

### Feedbacks
*   `GET /feedbacks` : Liste des retours étudiants.
*   `POST /feedbacks` : Soumission d'un nouveau feedback avec analyse de sentiment.

---

## 📊 Modèles de Données

Le schéma PostgreSQL comprend quatre tables principales :
1.  **`locations`** : Identifiants, noms, coordonnées GPS, types de bâtiments.
2.  **`flux`** : Enregistrements temporels du nombre de personnes par lieu.
3.  **`schedules`** : Emplois du temps et événements planifiés.
4.  **`feedbacks`** : Commentaires et notes laissés par les utilisateurs.

---

## 🔒 Sécurité et Bonnes Pratiques

*   **Validation stricte** : Utilisation systématique de Pydantic pour éviter les injections et erreurs de type.
*   **Gestion des erreurs** : Centralisation des exceptions via des gestionnaires globaux dans `utils/errors.py`.
*   **Performance** : Mise en cache Redis avec TTL pour soulager la base de données sur les endpoints critiques.
*   **Abstraction** : Utilisation du pattern *Service* pour isoler la logique métier des routes HTTP.

---

## 📅 Plan d'Implémentation (Hackathon 24h)

Le projet a été structuré pour une livraison rapide :
*   **H0 - H4** : Setup DB, modèles ORM et initialisation FastAPI.
*   **H4 - H12** : Développement des services de base (locations, flux) et intégration Redis.
*   **H12 - H18** : Logique complexe (Pathfinding NetworkX & Inférence ML).
*   **H18 - H24** : Tests, documentation Swagger et déploiement.

---

> **CampusFlow Lite** — Hackathon 2025.
