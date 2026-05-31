# Architecture de Données CampusFlow Lite

Ce dossier contient l'architecture de données complète pour le projet CampusFlow Lite, visant à simuler et optimiser les flux étudiants sur un campus fictif basé à Yaoundé.

## Contenu du Dossier

- `campus.json`: Fichier source de vérité décrivant les lieux du campus.
- `generate_flux.py`: Script Python pour générer le dataset `flux_historique.csv`.
- `flux_historique.csv`: Dataset CSV de la fréquentation étudiante réelle vs prévue.
- `generate_schedules.py`: Script Python pour générer le dataset `schedules.csv`.
- `schedules.csv`: Dataset CSV d'emplois du temps fictifs.
- `generate_feedbacks.py`: Script Python pour générer le dataset `feedbacks.csv`.
- `feedbacks.csv`: Dataset CSV de feedbacks étudiants fictifs.
- `schema.sql`: Script SQL pour la création des tables PostgreSQL.
- `load_data.py`: Script Python ETL pour charger les données CSV dans PostgreSQL.
- `README.md`: Ce document.

## 1. `campus.json`

Ce fichier JSON est la source de vérité pour tous les lieux du campus. Il contient les informations suivantes pour chaque bâtiment :

| Champ       | Type      | Description                                          |
| :---------- | :-------- | :--------------------------------------------------- |
| `id`        | `int`     | Identifiant unique du lieu                           |
| `nom`       | `string`  | Nom du lieu (ex: "Amphi", "Bibliothèque")          |
| `latitude`  | `numeric` | Latitude du lieu (basée sur Yaoundé)                 |
| `longitude` | `numeric` | Longitude du lieu (basée sur Yaoundé)                |
| `capacite`  | `int`     | Capacité maximale du lieu en nombre d'étudiants      |
| `type`      | `string`  | Type de lieu (ex: "Amphithéâtre", "Salle de cours") |

**Exemple :**

```json
[
    {
        "id": 1,
        "nom": "Amphi",
        "latitude": 3.8450,
        "longitude": 11.5020,
        "capacite": 120,
        "type": "Amphithéâtre"
    },
    ...
]
```

## 2. `generate_flux.py` et `flux historique.csv`

Ce script Python génère un fichier CSV (`flux historique.csv`) simulant la présence étudiante sur le campus sur 4 semaines, du lundi au samedi, de 7h à 21h, avec une granularité horaire. Il respecte les règles de réalisme spécifiées dans le cahier des charges.

**Colonnes de `flux_historique.csv` :**

| Colonne             | Type      | Description                                                                 |
| :------------------ | :-------- | :-------------------------------------------------------------------------- |
| `location_id`       | `int`     | Identifiant du lieu                                                         |
| `timestamp`         | `datetime`| Date et heure de l'observation (YYYY-MM-DD HH:MM:SS)                        |
| `heure_du_jour`     | `int`     | Heure de l'observation (0-23)                                               |
| `jour_semaine`      | `int`     | Jour de la semaine (0=Lundi à 5=Samedi)                                     |
| `activite_prevue`   | `int`     | Indique si une activité est prévue (1) ou non (0)                           |
| `nombre_etudiants`  | `int`     | Nombre d'étudiants présents                                                 |
| `niveau_congestion` | `string`  | Niveau de congestion ("faible" < 30%, "moyen" 30-70%, "eleve" > 70%) |

**Exécution :**

```bash
python3.11 generate_flux.py
```

## 3. `generate_schedules.py` et `schedules.csv`

Ce script génère un fichier CSV (`schedules.csv`) d'emplois du temps fictifs pour un ensemble d'étudiants. Les emplois du temps sont générés de manière cohérente avec les périodes d'activité identifiées dans `flux historique.csv`.

**Colonnes de `schedules.csv` :**

| Colonne       | Type      | Description                                     |
| :------------ | :-------- | :---------------------------------------------- |
| `id`          | `int`     | Identifiant unique de l'emploi du temps         |
| `etudiant_id` | `int`     | Identifiant de l'étudiant                       |
| `salle_id`    | `int`     | Identifiant du lieu (salle)                     |
| `heure_debut` | `datetime`| Heure de début de l'activité (YYYY-MM-DD HH:MM:SS) |
| `heure_fin`   | `datetime`| Heure de fin de l'activité (YYYY-MM-DD HH:MM:SS)   |

**Exécution :**

```bash
python3.11 generate_schedules.py
```

## 4. `generate_feedbacks.py` et `feedbacks.csv`

Ce script génère un fichier CSV (`feedbacks.csv`) contenant des feedbacks étudiants fictifs en français, avec un sentiment associé (positif, négatif, neutre). Les timestamps des feedbacks sont cohérents avec la période couverte par `flux_historique.csv`.

**Colonnes de `feedbacks.csv` :**

| Colonne       | Type      | Description                                     |
| :------------ | :-------- | :---------------------------------------------- |
| `id`          | `int`     | Identifiant unique du feedback                  |
| `etudiant_id` | `int`     | Identifiant de l'étudiant                       |
| `texte`       | `string`  | Contenu du feedback en français                 |
| `sentiment`   | `string`  | Sentiment associé au feedback ("positif", "negatif", "neutre") |
| `timestamp`   | `datetime`| Date et heure du feedback (YYYY-MM-DD HH:MM:SS) |

**Exécution :**

```bash
python3.11 generate_feedbacks.py
```

## 5. `schema.sql`

Ce fichier contient les définitions SQL pour créer les quatre tables PostgreSQL (`locations`, `schedules`, `flux`, `feedbacks`) avec les contraintes appropriées (clés primaires, clés étrangères, NOT NULL, index, et support PostGIS pour la table `locations`).

**Schéma des tables :**

### `locations`

```sql
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    capacite INTEGER NOT NULL,
    type VARCHAR(100) NOT NULL,
    geom GEOMETRY(Point, 4326) -- Colonne PostGIS pour les coordonnées géographiques (SRID 4326 pour WGS84)
);
CREATE INDEX IF NOT EXISTS locations_geom_idx ON locations USING GIST (geom);
```

### `schedules`

```sql
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER NOT NULL,
    salle_id INTEGER NOT NULL,
    heure_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    heure_fin TIMESTAMP WITH TIME ZONE NOT NULL,
    CONSTRAINT fk_salle
        FOREIGN KEY(salle_id)
        REFERENCES locations(id)
);
CREATE INDEX IF NOT EXISTS schedules_etudiant_id_idx ON schedules (etudiant_id);
CREATE INDEX IF NOT EXISTS schedules_salle_id_idx ON schedules (salle_id);
```

### `flux`

```sql
CREATE TABLE IF NOT EXISTS flux (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    nombre_etudiants INTEGER NOT NULL,
    activite_prevue INTEGER NOT NULL,
    heure_du_jour INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL,
    niveau_congestion VARCHAR(50) NOT NULL,
    CONSTRAINT fk_location
        FOREIGN KEY(location_id)
        REFERENCES locations(id)
);
CREATE INDEX IF NOT EXISTS flux_location_id_idx ON flux (location_id);
CREATE INDEX IF NOT EXISTS flux_timestamp_idx ON flux (timestamp);
```

### `feedbacks`

```sql
CREATE TABLE IF NOT EXISTS feedbacks (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER NOT NULL,
    texte TEXT NOT NULL,
    sentiment VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS feedbacks_etudiant_id_idx ON feedbacks (etudiant_id);
CREATE INDEX IF NOT EXISTS feedbacks_timestamp_idx ON feedbacks (timestamp);
```

**Exécution :**

Pour exécuter ce script, vous devez avoir une base de données PostgreSQL avec l'extension PostGIS activée. Connectez-vous à votre base de données et exécutez le fichier :

```bash
psql -U your_user -d your_database -f schema.sql
```

## 6. `load_data.py`

Ce script Python ETL (Extract, Transform, Load) est responsable du chargement des données générées (`campus.json`, `flux_historique.csv`, `schedules.csv`, `feedbacks.csv`) dans les tables PostgreSQL correspondantes. Il utilise la bibliothèque `psycopg2` pour interagir avec la base de données.

**Configuration :**

Avant l'exécution, assurez-vous de configurer les paramètres de connexion à votre base de données PostgreSQL dans la variable `DB_CONFIG` au début du script `load_data.py`.

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "campusflow_db",
    "user": "campusflow_user",
    "password": "campusflow_password"
}
```

**Exécution :**

```bash
python3.11 load_data.py
```

## 7. `requirements.txt`

Ce fichier liste toutes les dépendances Python nécessaires pour exécuter les scripts de génération et de chargement des données.

**Installation des dépendances :**

```bash
pip3 install -r requirements.txt
```

## Ordre d'exécution recommandé

1. **Installer les dépendances Python :**
   ```bash
   pip3 install -r requirements.txt
   ```
2. **Générer les datasets CSV :**
   ```bash
   python3.11 generate_flux.py
   python3.11 generate_schedules.py
   python3.11 generate_feedbacks.py
   ```
3. **Créer la base de données PostgreSQL et les tables :**
   - Assurez-vous que PostgreSQL et PostGIS sont installés et configurés.
   - Créez une base de données et un utilisateur si nécessaire.
   - Exécutez le script `schema.sql`.
   ```bash
   # Exemple de création de DB et utilisateur (à adapter)
   # sudo -u postgres createuser campusflow_user
   # sudo -u postgres createdb campusflow_db -O campusflow_user
   # sudo -u postgres psql -d campusflow_db -c "CREATE EXTENSION postgis;"
   psql -U campusflow_user -d campusflow_db -f schema.sql
   ```
4. **Charger les données dans PostgreSQL :**
   - Mettez à jour `DB_CONFIG` dans `load_data.py` si nécessaire.
   ```bash
   python3.11 load_data.py
   ```

Ce processus garantit que toutes les données sont générées, structurées et prêtes à être utilisées par les équipes ML, Backend et Frontend du projet CampusFlow Lite.
