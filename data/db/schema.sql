-- ============================================================
-- CampusFlow Lite — Schéma PostgreSQL
-- Data Engineer : Vick
-- ⚠️  Contrat d'interface figé à H2 — ne pas modifier après
-- ============================================================

-- Extension PostGIS (à activer une seule fois par base)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ────────────────────────────────────────────────────────────
-- TABLE 1 : locations
-- Source : campus.json (généré par Vick)
-- Consommateurs : Abdourahim (API), Aurel (carte), Germain (ML)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS locations (
    id          SERIAL PRIMARY KEY,
    nom         VARCHAR(100)    NOT NULL,
    latitude    DOUBLE PRECISION NOT NULL,
    longitude   DOUBLE PRECISION NOT NULL,
    capacite    INTEGER         NOT NULL CHECK (capacite > 0),
    type        VARCHAR(20)     NOT NULL CHECK (type IN ('amphi', 'salle', 'labo')),
    geom        GEOMETRY(Point, 4326)   -- PostGIS : calculé à l'INSERT via trigger
);

-- Trigger : remplit automatiquement geom depuis lat/lon
CREATE OR REPLACE FUNCTION set_location_geom()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_location_geom
BEFORE INSERT OR UPDATE ON locations
FOR EACH ROW EXECUTE FUNCTION set_location_geom();

-- Index spatial PostGIS
CREATE INDEX IF NOT EXISTS idx_locations_geom ON locations USING GIST(geom);


-- ────────────────────────────────────────────────────────────
-- TABLE 2 : schedules
-- Source : fichiers ICS (parsing Python icalendar)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS schedules (
    id              SERIAL PRIMARY KEY,
    etudiant_id     INTEGER         NOT NULL,
    salle_id        INTEGER         NOT NULL REFERENCES locations(id),
    heure_debut     TIMESTAMPTZ     NOT NULL,   -- UTC
    heure_fin       TIMESTAMPTZ     NOT NULL,
    CONSTRAINT chk_schedule_dates CHECK (heure_fin > heure_debut)
);

CREATE INDEX IF NOT EXISTS idx_schedules_salle     ON schedules(salle_id);
CREATE INDEX IF NOT EXISTS idx_schedules_etudiant  ON schedules(etudiant_id);
CREATE INDEX IF NOT EXISTS idx_schedules_debut     ON schedules(heure_debut);


-- ────────────────────────────────────────────────────────────
-- TABLE 3 : flux
-- Source : CSV historique + JSON capteurs simulés
-- Contraintes strictes : pas de NULL sur location_id, timestamp, nombre_etudiants
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS flux (
    id                  SERIAL PRIMARY KEY,
    location_id         INTEGER         NOT NULL REFERENCES locations(id),
    timestamp           TIMESTAMPTZ     NOT NULL,   -- UTC
    nombre_etudiants    INTEGER         NOT NULL CHECK (nombre_etudiants >= 0)
);

-- Index critiques pour les requêtes temps réel (section 3.4 du CdC)
CREATE INDEX IF NOT EXISTS idx_flux_location_id ON flux(location_id);
CREATE INDEX IF NOT EXISTS idx_flux_timestamp   ON flux(timestamp DESC);
-- Index composé : couvre les requêtes GET /flux/live filtrées par lieu + heure
CREATE INDEX IF NOT EXISTS idx_flux_loc_ts      ON flux(location_id, timestamp DESC);


-- ────────────────────────────────────────────────────────────
-- TABLE 4 : feedbacks
-- Source : texte brut → analyse Hugging Face (bonus IA)
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS feedbacks (
    id              SERIAL PRIMARY KEY,
    etudiant_id     INTEGER         NOT NULL,
    texte           TEXT            NOT NULL,
    sentiment       VARCHAR(10)     CHECK (sentiment IN ('positif', 'neutre', 'negatif')),
    timestamp       TIMESTAMPTZ     NOT NULL DEFAULT NOW()   -- UTC
);

CREATE INDEX IF NOT EXISTS idx_feedbacks_sentiment  ON feedbacks(sentiment);
CREATE INDEX IF NOT EXISTS idx_feedbacks_timestamp  ON feedbacks(timestamp DESC);


-- ────────────────────────────────────────────────────────────
-- Commentaires de documentation des tables
-- ────────────────────────────────────────────────────────────
COMMENT ON TABLE locations  IS 'Bâtiments du campus fictif — source de vérité issue de campus.json';
COMMENT ON TABLE schedules  IS 'Emplois du temps étudiants parsés depuis les fichiers ICS';
COMMENT ON TABLE flux       IS 'Fréquentation en temps réel et historique par bâtiment';
COMMENT ON TABLE feedbacks  IS 'Retours étudiants avec score de sentiment Hugging Face';
