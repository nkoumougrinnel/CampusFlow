
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
-- Alignée sur raw/schedules.csv (groupe, type_activite, jour_semaine).
-- En dev, si l'ancienne table existe encore : DROP TABLE IF EXISTS schedules CASCADE;
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    groupe VARCHAR(20) NOT NULL,
    type_activite VARCHAR(10) NOT NULL,
    salle_id INTEGER NOT NULL,
    heure_debut TIMESTAMP WITH TIME ZONE NOT NULL,
    heure_fin TIMESTAMP WITH TIME ZONE NOT NULL,
    jour_semaine SMALLINT NOT NULL,
    CONSTRAINT fk_schedules_salle
        FOREIGN KEY (salle_id)
        REFERENCES locations (id),
    CONSTRAINT chk_schedules_type_activite
        CHECK (type_activite IN ('cours', 'tp')),
    CONSTRAINT chk_schedules_jour_semaine
        CHECK (jour_semaine >= 0 AND jour_semaine <= 5),
    CONSTRAINT chk_schedules_heures
        CHECK (heure_fin > heure_debut)
);

CREATE INDEX IF NOT EXISTS schedules_groupe_idx ON schedules (groupe);
CREATE INDEX IF NOT EXISTS schedules_salle_id_idx ON schedules (salle_id);
CREATE INDEX IF NOT EXISTS schedules_jour_semaine_idx ON schedules (jour_semaine);
CREATE INDEX IF NOT EXISTS schedules_type_activite_idx ON schedules (type_activite);
CREATE INDEX IF NOT EXISTS schedules_heure_debut_idx ON schedules (heure_debut);

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
