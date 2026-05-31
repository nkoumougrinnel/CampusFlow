
import psycopg2
import pandas as pd
import json

# Configuration de la base de données (à adapter si nécessaire)
DB_CONFIG = {
    "host": "localhost",
    "database": "campusflow_db",
    "user": "campusflow_user",
    "password": "campusflow_password"
}

def load_locations(cursor, conn):
    print("Chargement des données de locations...")
    with open("campusflow_data/campus.json", "r", encoding="utf-8") as f:
        locations_data = json.load(f)

    for loc in locations_data:
        # Utilisation de ST_MakePoint et ST_SetSRID pour la colonne GEOMETRY
        insert_query = """
        INSERT INTO locations (id, nom, latitude, longitude, capacite, type, geom)
        VALUES (%s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
        ON CONFLICT (id) DO UPDATE SET
            nom = EXCLUDED.nom,
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude,
            capacite = EXCLUDED.capacite,
            type = EXCLUDED.type,
            geom = EXCLUDED.geom;
        """
        cursor.execute(insert_query, (
            loc["id"],
            loc["nom"],
            loc["latitude"],
            loc["longitude"],
            loc["capacite"],
            loc["type"],
            loc["longitude"], # Longitude pour ST_MakePoint
            loc["latitude"]  # Latitude pour ST_MakePoint
        ))
    conn.commit()
    print(f"{len(locations_data)} locations chargées.")

def load_flux(cursor, conn):
    print("Chargement des données de flux...")
    flux_df = pd.read_csv("campusflow_data/flux_historique.csv")
    flux_df["timestamp"] = pd.to_datetime(flux_df["timestamp"])

    for index, row in flux_df.iterrows():
        insert_query = """
        INSERT INTO flux (location_id, timestamp, nombre_etudiants, activite_prevue, heure_du_jour, jour_semaine, niveau_congestion)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(insert_query, (
            row["location_id"],
            row["timestamp"],
            row["nombre_etudiants"],
            row["activite_prevue"],
            row["heure_du_jour"],
            row["jour_semaine"],
            row["niveau_congestion"]
        ))
    conn.commit()
    print(f"{len(flux_df)} enregistrements de flux chargés.")

def load_schedules(cursor, conn):
    print("Chargement des données de schedules...")
    schedules_df = pd.read_csv("campusflow_data/schedules.csv")
    schedules_df["heure_debut"] = pd.to_datetime(schedules_df["heure_debut"])
    schedules_df["heure_fin"] = pd.to_datetime(schedules_df["heure_fin"])

    for index, row in schedules_df.iterrows():
        insert_query = """
        INSERT INTO schedules (id, etudiant_id, salle_id, heure_debut, heure_fin)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            etudiant_id = EXCLUDED.etudiant_id,
            salle_id = EXCLUDED.salle_id,
            heure_debut = EXCLUDED.heure_debut,
            heure_fin = EXCLUDED.heure_fin;
        """
        cursor.execute(insert_query, (
            row["id"],
            row["etudiant_id"],
            row["salle_id"],
            row["heure_debut"],
            row["heure_fin"]
        ))
    conn.commit()
    print(f"{len(schedules_df)} enregistrements de schedules chargés.")

def load_feedbacks(cursor, conn):
    print("Chargement des données de feedbacks...")
    feedbacks_df = pd.read_csv("campusflow_data/feedbacks.csv")
    feedbacks_df["timestamp"] = pd.to_datetime(feedbacks_df["timestamp"])

    for index, row in feedbacks_df.iterrows():
        insert_query = """
        INSERT INTO feedbacks (id, etudiant_id, texte, sentiment, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            etudiant_id = EXCLUDED.etudiant_id,
            texte = EXCLUDED.texte,
            sentiment = EXCLUDED.sentiment,
            timestamp = EXCLUDED.timestamp;
        """
        cursor.execute(insert_query, (
            row["id"],
            row["etudiant_id"],
            row["texte"],
            row["sentiment"],
            row["timestamp"]
        ))
    conn.commit()
    print(f"{len(feedbacks_df)} enregistrements de feedbacks chargés.")

def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        load_locations(cursor, conn)
        load_flux(cursor, conn)
        load_schedules(cursor, conn)
        load_feedbacks(cursor, conn)

    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Connexion à la base de données fermée.")

if __name__ == "__main__":
    main()
