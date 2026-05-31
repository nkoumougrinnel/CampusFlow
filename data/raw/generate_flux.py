
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

# Charger les données des lieux depuis campus.json
with open('campusflow_data/campus.json', 'r', encoding='utf-8') as f:
    locations_data = json.load(f)

locations_df = pd.DataFrame(locations_data)

# Paramètres de génération
start_date = datetime(2026, 5, 1)
num_weeks = 4
days_of_week = range(0, 6)  # Lundi (0) à Samedi (5)
hours_of_day = range(7, 22) # 7h à 21h (exclusif pour 22h)

data = []

for week in range(num_weeks):
    for day_offset in days_of_week:
        current_date = start_date + timedelta(weeks=week, days=day_offset)
        if current_date.weekday() == 6: # Skip Sunday
            continue

        for hour in hours_of_day:
            for _, location in locations_df.iterrows():
                location_id = location['id']
                capacite = location['capacite']
                nom_lieu = location['nom']

                timestamp = current_date.replace(hour=hour, minute=0, second=0)
                jour_semaine = current_date.weekday() # 0=Lundi, 5=Samedi
                heure_du_jour = hour

                activite_prevue = 0
                nombre_etudiants = 0

                # Règles de réalisme
                if nom_lieu == "Bibliothèque":
                    activite_prevue = 0
                    if 12 <= heure_du_jour < 14 or heure_du_jour >= 17:
                        nombre_etudiants = int(np.random.uniform(0.20, 0.40) * capacite) # Peaks
                    else:
                        nombre_etudiants = int(np.random.uniform(0.00, 0.20) * capacite)
                elif nom_lieu == "Amphi":
                    if jour_semaine in [0, 2, 4]: # Lundi, Mercredi, Vendredi
                        activite_prevue = 1
                elif capacite == 15: # Petites salles de TP (C5, C6, C13, L26, L28)
                    if jour_semaine in [1, 3]: # Mardi, Jeudi
                        activite_prevue = 1
                else:
                    # Activité par défaut pour les autres salles
                    if np.random.rand() > 0.5: # 50% chance d'activité prévue
                        activite_prevue = 1

                # Ajustement nombre_etudiants selon activite_prevue
                if activite_prevue == 1:
                    nombre_etudiants = int(np.random.uniform(0.60, 0.95) * capacite)
                elif activite_prevue == 0 and nom_lieu != "Bibliothèque": # Already handled for Biblio
                    nombre_etudiants = int(np.random.uniform(0.00, 0.40) * capacite)

                # Réduction d'activité le Samedi
                if jour_semaine == 5: # Samedi
                    nombre_etudiants = int(nombre_etudiants * np.random.uniform(0.50, 0.80)) # 20-50% de réduction

                # Ajouter du bruit aléatoire
                nombre_etudiants = max(0, min(capacite, nombre_etudiants + np.random.randint(-5, 5)))

                # Calcul niveau_congestion
                taux_occupation = nombre_etudiants / capacite
                if taux_occupation < 0.30:
                    niveau_congestion = "faible"
                elif 0.30 <= taux_occupation <= 0.70:
                    niveau_congestion = "moyen"
                else:
                    niveau_congestion = "eleve"

                data.append({
                    "location_id": location_id,
                    "timestamp": timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    "heure_du_jour": heure_du_jour,
                    "jour_semaine": jour_semaine,
                    "activite_prevue": activite_prevue,
                    "nombre_etudiants": nombre_etudiants,
                    "niveau_congestion": niveau_congestion
                })

df = pd.DataFrame(data)

# Assurer un minimum de 5000 lignes (le calcul actuel devrait en générer beaucoup plus)
# 4 semaines * 6 jours/semaine * 15 heures/jour * 17 lieux = 6120 lignes

df.to_csv('flux_historique.csv', index=False, encoding='utf-8')
print("flux_historique.csv généré avec succès.")
