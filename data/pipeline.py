"""
CampusFlow Lite — Pipeline ETL
Data Engineer : Vick

Charge dans l'ordre :
  1. campus.json       → table locations
  2. frequentation.csv → table flux  (historique)
  3. emplois_du_temps/ → table schedules (fichiers .ics)
  4. capteurs.json     → table flux  (temps réel simulé)
  5. feedbacks.csv     → table feedbacks (texte brut, sentiment null = à remplir par HF)

Utilisation :
  pip install psycopg2-binary pandas icalendar python-dotenv
  python etl/pipeline.py
"""

import json
import os
import logging
from pathlib import Path
from datetime import timezone

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from icalendar import Calendar
from dotenv import load_dotenv

# ── Configuration ─────────────────────────────────────────────────────────────
load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "campusflow"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


# ── Connexion ──────────────────────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# ── 1. Locations (campus.json) ─────────────────────────────────────────────────
def load_locations(conn) -> int:
    path = DATA_DIR / "campus.json"
    with open(path, encoding="utf-8") as f:
        buildings = json.load(f)

    rows = [
        (b["id"], b["nom"], b["latitude"], b["longitude"], b["capacite"], b["type"])
        for b in buildings
    ]

    with conn.cursor() as cur:
        # INSERT OR UPDATE (upsert) pour idempotence
        execute_values(
            cur,
            """
            INSERT INTO locations (id, nom, latitude, longitude, capacite, type)
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET
                nom       = EXCLUDED.nom,
                latitude  = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                capacite  = EXCLUDED.capacite,
                type      = EXCLUDED.type
            """,
            rows,
        )
    conn.commit()
    log.info(f"locations : {len(rows)} bâtiments chargés depuis {path.name}")
    return len(rows)


# ── 2. Flux historique (frequentation.csv) ────────────────────────────────────
def load_flux_csv(conn) -> int:
    path = DATA_DIR / "frequentation.csv"
    if not path.exists():
        log.warning(f"Fichier introuvable : {path} — étape flux CSV ignorée")
        return 0

    df = pd.read_csv(path, parse_dates=["timestamp"])

    # Colonnes attendues : location_id, timestamp, nombre_etudiants
    required = {"location_id", "timestamp", "nombre_etudiants"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {path.name} : {missing}")

    # Normalisation UTC
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize("UTC")
    else:
        df["timestamp"] = df["timestamp"].dt.tz_convert("UTC")

    # Suppression des nulls interdits (contrainte CdC)
    before = len(df)
    df = df.dropna(subset=["location_id", "timestamp", "nombre_etudiants"])
    dropped = before - len(df)
    if dropped:
        log.warning(f"flux CSV : {dropped} lignes supprimées (valeurs NULL)")

    rows = list(df[["location_id", "timestamp", "nombre_etudiants"]].itertuples(index=False, name=None))

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO flux (location_id, timestamp, nombre_etudiants) VALUES %s",
            rows,
        )
    conn.commit()
    log.info(f"flux (CSV) : {len(rows)} enregistrements insérés")
    return len(rows)


# ── 3. Schedules (fichiers .ics) ──────────────────────────────────────────────
def load_schedules_ics(conn) -> int:
    ics_dir = DATA_DIR / "emplois_du_temps"
    if not ics_dir.exists():
        log.warning(f"Dossier introuvable : {ics_dir} — étape schedules ignorée")
        return 0

    ics_files = list(ics_dir.glob("*.ics"))
    if not ics_files:
        log.warning("Aucun fichier .ics trouvé")
        return 0

    rows = []
    for ics_path in ics_files:
        # Convention de nommage : etudiant_<id>.ics
        try:
            etudiant_id = int(ics_path.stem.split("_")[1])
        except (IndexError, ValueError):
            log.warning(f"Nom de fichier non conforme (attendu etudiant_<id>.ics) : {ics_path.name}")
            continue

        with open(ics_path, "rb") as f:
            cal = Calendar.from_ical(f.read())

        for component in cal.walk():
            if component.name != "VEVENT":
                continue

            dtstart = component.get("DTSTART")
            dtend   = component.get("DTEND")
            location = component.get("LOCATION")  # doit être un location_id (int)

            if not (dtstart and dtend and location):
                continue

            try:
                salle_id = int(str(location))
                debut = dtstart.dt
                fin   = dtend.dt

                # Normalisation UTC
                if hasattr(debut, "astimezone"):
                    debut = debut.astimezone(timezone.utc)
                    fin   = fin.astimezone(timezone.utc)

                rows.append((etudiant_id, salle_id, debut, fin))
            except (ValueError, TypeError) as e:
                log.warning(f"Événement ignoré dans {ics_path.name} : {e}")

    if not rows:
        log.warning("Aucun événement valide extrait des fichiers ICS")
        return 0

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO schedules (etudiant_id, salle_id, heure_debut, heure_fin) VALUES %s",
            rows,
        )
    conn.commit()
    log.info(f"schedules : {len(rows)} événements insérés depuis {len(ics_files)} fichiers ICS")
    return len(rows)


# ── 4. Flux temps réel simulé (capteurs.json) ────────────────────────────────
def load_flux_json(conn) -> int:
    path = DATA_DIR / "capteurs.json"
    if not path.exists():
        log.warning(f"Fichier introuvable : {path} — étape flux JSON ignorée")
        return 0

    with open(path, encoding="utf-8") as f:
        records = json.load(f)

    # Format attendu : [{"location_id": 1, "timestamp": "2024-01-15T08:00:00Z", "nombre_etudiants": 42}, ...]
    rows = []
    for r in records:
        try:
            ts = pd.Timestamp(r["timestamp"]).tz_convert("UTC")
            rows.append((int(r["location_id"]), ts, int(r["nombre_etudiants"])))
        except (KeyError, ValueError) as e:
            log.warning(f"Enregistrement capteur ignoré : {e} — {r}")

    if not rows:
        return 0

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO flux (location_id, timestamp, nombre_etudiants) VALUES %s",
            rows,
        )
    conn.commit()
    log.info(f"flux (JSON capteurs) : {len(rows)} enregistrements insérés")
    return len(rows)


# ── 5. Feedbacks (feedbacks.csv) ──────────────────────────────────────────────
def load_feedbacks(conn) -> int:
    path = DATA_DIR / "feedbacks.csv"
    if not path.exists():
        log.warning(f"Fichier introuvable : {path} — étape feedbacks ignorée")
        return 0

    df = pd.read_csv(path)

    # Colonnes attendues : etudiant_id, texte, timestamp
    # sentiment laissé à NULL → sera rempli par l'endpoint Hugging Face (Abdourahim)
    required = {"etudiant_id", "texte", "timestamp"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes dans {path.name} : {missing}")

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["sentiment"] = df.get("sentiment", None)  # optionnel à l'ETL

    rows = [
        (int(row.etudiant_id), str(row.texte), row.timestamp, row.sentiment if pd.notna(row.sentiment) else None)
        for row in df.itertuples(index=False)
    ]

    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO feedbacks (etudiant_id, texte, timestamp, sentiment) VALUES %s",
            rows,
        )
    conn.commit()
    log.info(f"feedbacks : {len(rows)} entrées insérées")
    return len(rows)


# ── Main ───────────────────────────────────────────────────────────────────────
def run_pipeline():
    log.info("═══ Démarrage du pipeline ETL CampusFlow ═══")
    conn = get_connection()

    try:
        n_locations  = load_locations(conn)
        n_flux_csv   = load_flux_csv(conn)
        n_schedules  = load_schedules_ics(conn)
        n_flux_json  = load_flux_json(conn)
        n_feedbacks  = load_feedbacks(conn)

        log.info("═══ Pipeline terminé ═══")
        log.info(f"  locations  : {n_locations:>6} lignes")
        log.info(f"  flux (CSV) : {n_flux_csv:>6} lignes")
        log.info(f"  schedules  : {n_schedules:>6} lignes")
        log.info(f"  flux (JSON): {n_flux_json:>6} lignes")
        log.info(f"  feedbacks  : {n_feedbacks:>6} lignes")

    except Exception as e:
        conn.rollback()
        log.error(f"Erreur pipeline : {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_pipeline()
