
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

# Charger les données des lieux depuis campus.json
with open("campusflow_data/campus.json", "r", encoding="utf-8") as f:
    locations_data = json.load(f)
locations_df = pd.DataFrame(locations_data)

# Charger les données de flux pour s'assurer d'une certaine cohérence
try:
    flux_df = pd.read_csv("campusflow_data/flux_historique.csv")
except FileNotFoundError:
    print("flux_historique.csv non trouvé. Veuillez le générer d'abord.")
    exit()

# Paramètres de génération
num_students = 200 # Nombre d'étudiants fictifs
num_schedules_per_student = 5 # Nombre moyen d'activités par étudiant sur la période

all_schedules = []
student_ids = np.arange(1, num_students + 1)

# Filtrer les flux pour les périodes avec activité
active_flux = flux_df[flux_df["nombre_etudiants"] > 0].copy()
active_flux["datetime"] = pd.to_datetime(active_flux["timestamp"])

# Assurez-vous qu'il y a suffisamment de données actives pour générer des emplois du temps
if active_flux.empty:
    print("Aucune activité enregistrée dans flux_historique.csv. Impossible de générer des emplois du temps cohérents.")
    exit()

for student_id in student_ids:
    for _ in range(np.random.randint(3, num_schedules_per_student + 3)): # Variation du nombre d'activités
        # Choisir une activité existante aléatoirement pour la cohérence
        random_activity = active_flux.sample(1).iloc[0]

        salle_id = random_activity["location_id"]
        heure_debut = random_activity["datetime"]

        # Durée aléatoire de l'activité (1 à 3 heures)
        duration_hours = np.random.choice([1, 2, 3])
        heure_fin = heure_debut + timedelta(hours=int(duration_hours))

        # S'assurer que l'heure de fin ne dépasse pas 21h (fin de journée)
        if heure_fin.hour >= 22:
            heure_fin = heure_debut.replace(hour=21, minute=0, second=0)

        all_schedules.append({
            "etudiant_id": student_id,
            "salle_id": salle_id,
            "heure_debut": heure_debut.strftime("%Y-%m-%d %H:%M:%S"),
            "heure_fin": heure_fin.strftime("%Y-%m-%d %H:%M:%S")
        })

schedules_df = pd.DataFrame(all_schedules)
schedules_df.index.name = "id"
schedules_df.reset_index(inplace=True)
schedules_df["id"] = schedules_df.index + 1 # Ajouter un ID auto-incrémenté

schedules_df.to_csv("schedules.csv", index=False, encoding="utf-8")
print("schedules.csv généré avec succès.")
