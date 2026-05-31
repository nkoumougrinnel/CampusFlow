# CampusFlow Lite — Data Engineer (Vick)

## Ordre d'exécution obligatoire

```
1. Configurer .env
2. Appliquer le schéma SQL
3. Lancer le pipeline ETL
4. Valider avec Germain & Abdourahim (session H0)
```

## Setup

```bash
# 1. Environnement Python
pip install -r etl/requirements.txt

# 2. Copier et remplir les variables DB
cp .env.example .env

# 3. Créer la base et appliquer le schéma (PostGIS requis)
psql -U postgres -c "CREATE DATABASE campusflow;"
psql -U postgres -d campusflow -f db/schema.sql

# 4. Lancer le pipeline
python etl/pipeline.py
```

## Fichiers sources attendus dans data/raw/

| Fichier | Obligatoire | Notes |
|---|---|---|
| campus.json | ✅ OUI | Déjà généré |
| frequentation.csv | ✅ OUI | Colonnes : location_id, timestamp, nombre_etudiants |
| emplois_du_temps/*.ics | ✅ OUI | Nommage : etudiant_<id>.ics, LOCATION = location_id |
| capteurs.json | ✅ OUI | Liste d'objets {location_id, timestamp, nombre_etudiants} |
| feedbacks.csv | ⚠️ BONUS | Colonnes : etudiant_id, texte, timestamp |

## Contrat d'interface (figé à H2)

Le schéma PostgreSQL NE DOIT PAS changer après H2.
Toute modification doit être validée avec Germain ET Abdourahim.
