"""
Tests pour les nouvelles fonctionnalités: B1, B2, B3
"""
import pytest
from pathlib import Path
import sqlite3
import os
from datetime import datetime, timedelta


# ============================================================================
# FONCTIONS UTILITAIRES POUR LES TESTS
# ============================================================================


def get_test_db_path():
    """Retourne le chemin de la base de test."""
    return Path(__file__).parent.parent / "test_nouveau.db"


def create_test_db():
    """Crée une base de test avec le schéma initial."""
    test_db = get_test_db_path()
    if test_db.exists():
        try:
            os.remove(test_db)
        except:
            pass
    
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    schema = (Path(__file__).parent.parent / "base.sql").read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()
    conn.close()


def get_test_conn():
    """Retourne une connexion à la base de test."""
    test_db = get_test_db_path()
    if not test_db.exists():
        create_test_db()
    conn = sqlite3.connect(test_db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ============================================================================
# FIXTURES PYTEST
# ============================================================================


@pytest.fixture(autouse=True)
def setup_test_db():
    """Initialise une base de test propre avant chaque test."""
    create_test_db()
    yield
    # Nettoyage après le test
    test_db = get_test_db_path()
    # Fermer toutes les connexions avant de supprimer
    import gc
    gc.collect()
    if test_db.exists():
        try:
            os.remove(test_db)
        except:
            pass


# ============================================================================
# TESTS POUR LES NOUVELLES FONCTIONNALITES (B1, B2, B3)
# ============================================================================


class TestB1ChevauchementPersonne:
    """Tests pour B1: une personne ne peut pas avoir deux réservations qui se chevauchent."""

    def test_chevauchement_personne_meme_date(self):
        """Test que deux réservations de la même personne ne peuvent pas se chevaucher le même jour."""
        conn = get_test_conn()
        
        # Ajouter deux salles
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S30", 15])
        salle1_id = conn.execute("SELECT id FROM salles WHERE nom = 'S30'").fetchone()["id"]
        
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S31", 20])
        salle2_id = conn.execute("SELECT id FROM salles WHERE nom = 'S31'").fetchone()["id"]
        
        # Réserver salle1 pour Alice: 10:00-12:00
        conn.execute(
            "INSERT INTO reservations (salle_id, personne, date, debut, fin, participants) VALUES (?, ?, ?, ?, ?, ?)",
            [salle1_id, "Alice", "2026-11-10", "10:00", "12:00", 5]
        )
        
        # Vérifier qu'Alice ne peut pas réserver salle2 à la même heure (10:30-11:30)
        chevauchement = conn.execute(
            """SELECT COUNT(*) FROM reservations
               WHERE personne = ? AND date = ?
               AND (
                   (debut <= '10:30' AND fin > '10:30') OR
                   (debut < '11:30' AND fin > '10:30')
               )""",
            ["Alice", "2026-11-10"]
        ).fetchone()[0]
        
        assert chevauchement == 1  # Doit trouver la réservation existante
        conn.close()

    def test_chevauchement_personne_heures_contigues(self):
        """Test que deux réservations de la même personne peuvent être contiguës (fin à 12:00, début à 12:00)."""
        conn = get_test_conn()
        
        # Ajouter une salle
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S32", 15])
        salle_id = conn.execute("SELECT id FROM salles WHERE nom = 'S32'").fetchone()["id"]
        
        # Utiliser une personne différente de celle des données d'exemple (Alice)
        # Réserver pour Bob: 10:00-12:00
        conn.execute(
            "INSERT INTO reservations (salle_id, personne, date, debut, fin, participants) VALUES (?, ?, ?, ?, ?, ?)",
            [salle_id, "Bob", "2026-11-10", "10:00", "12:00", 5]
        )
        
        # Réserver pour Bob: 12:00-14:00 (contiguë, donc valide)
        conn.execute(
            "INSERT INTO reservations (salle_id, personne, date, debut, fin, participants) VALUES (?, ?, ?, ?, ?, ?)",
            [salle_id, "Bob", "2026-11-10", "12:00", "14:00", 5]
        )
        
        bob_reservations = conn.execute(
            "SELECT * FROM reservations WHERE personne = ?", ["Bob"]
        ).fetchall()
        assert len(bob_reservations) == 2
        conn.close()

    def test_chevauchement_personne_different_jours(self):
        """Test que deux réservations de la même personne peuvent être le même jour à des heures différentes."""
        conn = get_test_conn()
        
        # Ajouter une salle
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S33", 15])
        salle_id = conn.execute("SELECT id FROM salles WHERE nom = 'S33'").fetchone()["id"]
        
        # Utiliser Charlie pour éviter les conflits avec les données d'exemple
        # Réserver pour Charlie: 10:00-12:00
        conn.execute(
            "INSERT INTO reservations (salle_id, personne, date, debut, fin, participants) VALUES (?, ?, ?, ?, ?, ?)",
            [salle_id, "Charlie", "2026-11-10", "10:00", "12:00", 5]
        )
        
        # Réserver pour Charlie: 14:00-16:00 (même jour, heures différentes, valide)
        conn.execute(
            "INSERT INTO reservations (salle_id, personne, date, debut, fin, participants) VALUES (?, ?, ?, ?, ?, ?)",
            [salle_id, "Charlie", "2026-11-10", "14:00", "16:00", 5]
        )
        
        charlie_reservations = conn.execute(
            "SELECT * FROM reservations WHERE personne = ?", ["Charlie"]
        ).fetchall()
        assert len(charlie_reservations) == 2
        conn.close()


class TestB2TypeLocal:
    """Tests pour B2: ajout du type de local."""

    def test_ajouter_salle_avec_type(self):
        """Test l'ajout d'une salle avec un type spécifique."""
        conn = get_test_conn()
        
        # Ajouter une salle avec type
        conn.execute(
            "INSERT INTO salles (nom, capacite, projecteur, type) VALUES (?, ?, ?, ?)",
            ["Amphi_A", 100, 1, "Amphithéâtre"]
        )
        
        salle = conn.execute("SELECT * FROM salles WHERE nom = 'Amphi_A'").fetchone()
        assert salle is not None
        assert salle["type"] == "Amphithéâtre"
        conn.close()

    def test_salle_type_par_defaut(self):
        """Test qu'une salle sans type spécifié a le type par défaut."""
        conn = get_test_conn()
        
        # Ajouter une salle sans type (utilise le DEFAULT)
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["Salle_B", 15])
        
        salle = conn.execute("SELECT * FROM salles WHERE nom = 'Salle_B'").fetchone()
        assert salle is not None
        assert salle["type"] == "Salle de cours"  # Valeur par défaut
        conn.close()

    def test_modifier_type_salle(self):
        """Test la modification du type d'une salle."""
        conn = get_test_conn()
        
        # Ajouter une salle
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S40", 20])
        salle_id = conn.execute("SELECT id FROM salles WHERE nom = 'S40'").fetchone()["id"]
        
        # Modifier le type
        conn.execute("UPDATE salles SET type = ? WHERE id = ?", ["Laboratoire", salle_id])
        
        salle = conn.execute("SELECT * FROM salles WHERE id = ?", [salle_id]).fetchone()
        assert salle["type"] == "Laboratoire"
        conn.close()


class TestB3ReservationsRepetees:
    """Tests pour B3: réservations répétées chaque semaine."""

    def test_creer_reservations_repetees(self):
        """Test la création de réservations répétées hebdomadairement."""
        conn = get_test_conn()
        
        # Ajouter une salle
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S50", 15])
        salle_id = conn.execute("SELECT id FROM salles WHERE nom = 'S50'").fetchone()["id"]
        
        # Date de début: 10 novembre 2026 (mardi) pour éviter conflit avec données d'exemple
        # Date de fin: 24 novembre 2026 (mardi, 2 semaines après)
        # Résultat: 3 réservations (10 nov, 17 nov, 24 nov)
        
        date_debut = "2026-11-10"
        date_fin = "2026-11-24"
        
        # Insérer manuellement les réservations répétées
        date_courante = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_dt = datetime.strptime(date_fin, "%Y-%m-%d")
        
        while date_courante <= date_fin_dt:
            conn.execute(
                """INSERT INTO reservations 
                (salle_id, personne, date, debut, fin, participants, repetition, date_fin_repetition) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [salle_id, "David", date_courante.strftime("%Y-%m-%d"), "10:00", "12:00", 10, 1, date_fin]
            )
            date_courante += timedelta(days=7)
        
        # Vérifier qu'on a 3 réservations
        reservations = conn.execute(
            "SELECT * FROM reservations WHERE salle_id = ? AND personne = ?", [salle_id, "David"]
        ).fetchall()
        assert len(reservations) == 3
        
        # Vérifier les dates
        dates = [r['date'] for r in reservations]
        assert "2026-11-10" in dates
        assert "2026-11-17" in dates
        assert "2026-11-24" in dates
        
        # Vérifier que toutes sont marquées comme répétées
        for res in reservations:
            assert res['repetition'] == 1
            assert res['date_fin_repetition'] == date_fin
        
        conn.close()

    def test_annuler_serie_reservations_repetees(self):
        """Test l'annulation d'une série complète de réservations répétées."""
        conn = get_test_conn()
        
        # Ajouter une salle
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S51", 15])
        salle_id = conn.execute("SELECT id FROM salles WHERE nom = 'S51'").fetchone()["id"]
        
        # Créer une série de réservations répétées
        date_debut = "2026-11-10"
        date_fin = "2026-11-24"
        
        date_courante = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_dt = datetime.strptime(date_fin, "%Y-%m-%d")
        
        while date_courante <= date_fin_dt:
            conn.execute(
                """INSERT INTO reservations 
                (salle_id, personne, date, debut, fin, participants, repetition, date_fin_repetition) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [salle_id, "Eve", date_courante.strftime("%Y-%m-%d"), "14:00", "16:00", 8, 1, date_fin]
            )
            date_courante += timedelta(days=7)
        
        # Vérifier qu'on a 3 réservations
        reservations = conn.execute(
            "SELECT * FROM reservations WHERE salle_id = ? AND personne = ?", [salle_id, "Eve"]
        ).fetchall()
        assert len(reservations) == 3
        
        # Annuler toutes les réservations de la série
        conn.execute(
            """DELETE FROM reservations 
            WHERE personne = ? AND date >= ? AND date <= ? 
            AND debut = ? AND fin = ? AND salle_id = ? AND repetition = 1""",
            ["Eve", date_debut, date_fin, "14:00", "16:00", salle_id]
        )
        
        # Vérifier que toutes les réservations sont supprimées
        reservations = conn.execute(
            "SELECT * FROM reservations WHERE salle_id = ? AND personne = ?", [salle_id, "Eve"]
        ).fetchall()
        assert len(reservations) == 0
        conn.close()

    def test_b1_et_b3_chevauchement_personne_reservation_repetee(self):
        """Test que B1 s'applique aussi aux réservations répétées."""
        conn = get_test_conn()
        
        # Ajouter deux salles
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S60", 15])
        salle1_id = conn.execute("SELECT id FROM salles WHERE nom = 'S60'").fetchone()["id"]
        
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", ["S61", 20])
        salle2_id = conn.execute("SELECT id FROM salles WHERE nom = 'S61'").fetchone()["id"]
        
        # Frank réserve salle1 de 10:00-12:00 le 10 nov 2026 avec répétition
        date_debut = "2026-11-10"
        date_fin = "2026-11-24"
        
        date_courante = datetime.strptime(date_debut, "%Y-%m-%d")
        date_fin_dt = datetime.strptime(date_fin, "%Y-%m-%d")
        
        while date_courante <= date_fin_dt:
            conn.execute(
                """INSERT INTO reservations 
                (salle_id, personne, date, debut, fin, participants, repetition, date_fin_repetition) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                [salle1_id, "Frank", date_courante.strftime("%Y-%m-%d"), "10:00", "12:00", 10, 1, date_fin]
            )
            date_courante += timedelta(days=7)
        
        # Vérifier que Frank a bien 3 réservations
        frank_res = conn.execute(
            "SELECT * FROM reservations WHERE personne = ?", ["Frank"]
        ).fetchall()
        assert len(frank_res) == 3
        
        # Vérifier que Frank ne peut pas réserver salle2 le 17 nov de 10:30-11:30
        # car ça chevaucherait avec sa réservation répétée de 10:00-12:00
        chevauchement = conn.execute(
            """SELECT COUNT(*) FROM reservations 
               WHERE personne = ? AND date = ?
               AND (
                   (debut <= '10:30' AND fin > '10:30') OR
                   (debut < '11:30' AND fin > '10:30')
               )""",
            ["Frank", "2026-11-17"]
        ).fetchone()[0]
        
        assert chevauchement == 1  # Doit trouver la réservation existante
        conn.close()
