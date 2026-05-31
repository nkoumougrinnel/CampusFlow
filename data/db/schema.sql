
-- Extension PostGIS pour les données géospatiales
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table des lieux (locations)
CREATE TABLE IF NOT EXISTS locations (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    latitude NUMERIC(9, 6) NOT NULL,
    longitude NUMERIC(9, 6) NOT NULL,
    capacite INTEGER NOT NULL,
    type VARCHAR(100) NOT NULL,
    geom GEOMETRY(Point, 4326) -- Colonne PostGIS pour les coordonnées géographiques (SRID 4326 pour WGS84)
);

-- Index spatial pour la colonne geom
CREATE INDEX IF NOT EXISTS locations_geom_idx ON locations USING GIST (geom);

-- Table des emplois du temps (schedules)
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

-- Index sur etudiant_id et salle_id pour des recherches rapides
CREATE INDEX IF NOT EXISTS schedules_etudiant_id_idx ON schedules (etudiant_id);
CREATE INDEX IF NOT EXISTS schedules_salle_id_idx ON schedules (salle_id);

-- Table des flux (flux)
CREATE TABLE IF NOT EXISTS flux (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    nombre_etudiants INTEGER NOT NULL,
    activite_prevue INTEGER NOT NULL, -- 1 ou 0
    heure_du_jour INTEGER NOT NULL,
    jour_semaine INTEGER NOT NULL, -- 0=Lundi à 5=Samedi
    niveau_congestion VARCHAR(50) NOT NULL,
    CONSTRAINT fk_location
        FOREIGN KEY(location_id)
        REFERENCES locations(id)
);

-- Index sur location_id et timestamp pour des analyses de séries temporelles
CREATE INDEX IF NOT EXISTS flux_location_id_idx ON flux (location_id);
CREATE INDEX IF NOT EXISTS flux_timestamp_idx ON flux (timestamp);

-- Table des feedbacks (feedbacks)
CREATE TABLE IF NOT EXISTS feedbacks (
    id SERIAL PRIMARY KEY,
    etudiant_id INTEGER NOT NULL,
    texte TEXT NOT NULL,
    sentiment VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Index sur etudiant_id et timestamp pour les analyses de feedbacks
CREATE INDEX IF NOT EXISTS feedbacks_etudiant_id_idx ON feedbacks (etudiant_id);
CREATE INDEX IF NOT EXISTS feedbacks_timestamp_idx ON feedbacks (timestamp);
