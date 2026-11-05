-- Schéma de la base : Réservation de salles. Vous pouvez le modifier.
CREATE TABLE IF NOT EXISTS salles (
    id INTEGER PRIMARY KEY,
    nom TEXT NOT NULL,
    capacite INTEGER NOT NULL,
    projecteur INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY,
    salle_id INTEGER NOT NULL REFERENCES salles(id) ON DELETE CASCADE,
    personne TEXT NOT NULL,
    date TEXT NOT NULL,
    debut TEXT NOT NULL,
    fin TEXT NOT NULL,
    participants INTEGER NOT NULL
);

-- Données d'exemple, chargées à la création de data.db. Le 9 novembre 2026 est un lundi.
INSERT INTO salles (id, nom, capacite, projecteur) VALUES (1, 'S1', 20, 1), (2, 'S2', 8, 0);
INSERT INTO reservations (id, salle_id, personne, date, debut, fin, participants) VALUES (1, 1, 'Alice', '2026-11-09', '10:00', '12:00', 12);
