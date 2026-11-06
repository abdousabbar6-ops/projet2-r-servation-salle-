import streamlit as st
from datetime import datetime, timedelta
from base import ouvrir_base


def get_lundi(date):
    """Retourne le lundi de la semaine contenant la date donnée."""
    return date - timedelta(days=date.weekday())


def heurs_valides(debut, fin):
    """Vérifie que l'heure est entre 8h et 20h."""
    d = datetime.strptime(debut, "%H:%M")
    f = datetime.strptime(fin, "%H:%M")
    return d.hour >= 8 and f.hour <= 20


def duree_valide(debut, fin):
    """Vérifie que la durée est entre 30 min et 4h."""
    d = datetime.strptime(debut, "%H:%M")
    f = datetime.strptime(fin, "%H:%M")
    duree = (f - d).total_seconds() / 3600  # en heures
    return 0.5 <= duree <= 4


def chevauchement_existe(conn, salle_id, date, debut, fin, reservation_id=None):
    """Vérifie s'il y a un chevauchement avec d'autres réservations de la même salle."""
    params = [salle_id, date, debut, fin]
    query = """
        SELECT COUNT(*) as cnt FROM reservations 
        WHERE salle_id = ? AND date = ? AND id != ?
        AND (
            (debut <= ? AND fin > ?) OR
            (debut < ? AND fin > ?)
        )
    """
    if reservation_id:
        query = query.replace("AND id != ?", "AND id != ?")
        params.insert(2, reservation_id)
    else:
        query = query.replace("AND id != ?", "")
    
    count = conn.execute(query, params).fetchone()[0]
    return count > 0


# --- Configuration de la page ---
st.set_page_config(page_title="Réservation de salles", layout="wide")
st.title("📅 Réservation de salles")


# --- Initialisation session_state ---
if "salle_a_modifier" not in st.session_state:
    st.session_state.salle_a_modifier = None
if "reservation_a_annuler" not in st.session_state:
    st.session_state.reservation_a_annuler = None


# ============================================================================
# SECTION 1: GESTION DES SALLES
# ============================================================================
st.header("🏢 Gestion des salles")

with ouvrir_base() as conn:
    salles = conn.execute("SELECT id, nom, capacite, projecteur FROM salles").fetchall()

# --- Afficher la liste des salles ---
st.subheader("Liste des salles")
if salles:
    cols = st.columns([3, 1, 1, 1, 1])
    cols[0].write("**Nom**")
    cols[1].write("**Capacité**")
    cols[2].write("**Projecteur**")
    cols[3].write("**Modifier**")
    cols[4].write("**Supprimer**")
    
    for salle in salles:
        cols = st.columns([3, 1, 1, 1, 1])
        cols[0].write(f"{salle['nom']}")
        cols[1].write(f"{salle['capacite']}")
        cols[2].write("✅" if salle['projecteur'] else "❌")
        
        if cols[3].button("✏️", key=f"mod_{salle['id']}"):
            st.session_state.salle_a_modifier = salle['id']
            st.rerun()
        
        if cols[4].button("🗑️", key=f"sup_{salle['id']}"):
            conn.execute("DELETE FROM salles WHERE id = ?", [salle['id']])
            st.success(f"Salle {salle['nom']} supprimée !")
            st.rerun()
else:
    st.info("Aucune salle disponible.")


# --- Ajouter une salle ---
st.subheader("Ajouter une salle")
with st.form("ajouter_salle"):
    nom_nouvelle = st.text_input("Nom de la salle", key="nom_ajout")
    capacite_nouvelle = st.number_input("Capacité", min_value=1, value=10, key="capacite_ajout")
    projecteur_nouveau = st.checkbox("Avec projecteur", value=False, key="projecteur_ajout")
    
    if st.form_submit_button("Ajouter"):
        if not nom_nouvelle:
            st.error("Le nom est obligatoire !")
        else:
            with ouvrir_base() as conn:
                conn.execute(
                    "INSERT INTO salles (nom, capacite, projecteur) VALUES (?, ?, ?)",
                    [nom_nouvelle, capacite_nouvelle, 1 if projecteur_nouveau else 0]
                )
            st.success(f"Salle {nom_nouvelle} ajoutée !")
            st.rerun()


# --- Modifier une salle ---
if st.session_state.salle_a_modifier:
    st.subheader("Modifier une salle")
    with ouvrir_base() as conn:
        salle = conn.execute(
            "SELECT * FROM salles WHERE id = ?", [st.session_state.salle_a_modifier]
        ).fetchone()
    
    with st.form("modifier_salle"):
        nouveau_nom = st.text_input("Nouveau nom", value=salle['nom'], key="nom_modif")
        nouvelle_capacite = st.number_input("Nouvelle capacité", value=salle['capacite'], min_value=1, key="capacite_modif")
        nouveau_projecteur = st.checkbox("Avec projecteur", value=bool(salle['projecteur']), key="projecteur_modif")
        
        if st.form_submit_button("Enregistrer"):
            if not nouveau_nom:
                st.error("Le nom est obligatoire !")
            else:
                # Vérifier que la nouvelle capacité >= max(participants) des réservations existantes
                with ouvrir_base() as conn:
                    max_participants = conn.execute(
                        "SELECT MAX(participants) as max_p FROM reservations WHERE salle_id = ?",
                        [salle['id']]
                    ).fetchone()['max_p'] or 0
                    
                    if nouvelle_capacite < max_participants:
                        st.error(f"La capacité doit être >= {max_participants} (participants des réservations existantes) !")
                    else:
                        conn.execute(
                            "UPDATE salles SET nom = ?, capacite = ?, projecteur = ? WHERE id = ?",
                            [nouveau_nom, nouvelle_capacite, 1 if nouveau_projecteur else 0, salle['id']]
                        )
                        st.success(f"Salle {salle['nom']} modifiée !")
                        st.session_state.salle_a_modifier = None
                        st.rerun()
        
        if st.button("Annuler la modification"):
            st.session_state.salle_a_modifier = None
            st.rerun()


# ============================================================================
# SECTION 2: RESERVER UNE SALLE
# ============================================================================
st.header("📝 Réserver une salle")

with st.form("reserver_salle"):
    # Sélection de la salle
    if salles:
        salle_ids = [s['id'] for s in salles]
        salle_noms = [s['nom'] for s in salles]
        salle_selectionnee = st.selectbox("Salle", options=salle_noms, key="salle_reservation")
        salle_id = salle_ids[salle_noms.index(salle_selectionnee)]
        
        # Informations de la salle
        with ouvrir_base() as conn:
            salle_info = conn.execute("SELECT capacite FROM salles WHERE id = ?", [salle_id]).fetchone()
            capacite_salle = salle_info['capacite']
        
        st.write(f"Capacité maximale: {capacite_salle} personnes")
        
        # Personne
        personne = st.text_input("Nom de la personne", key="personne_reservation")
        
        # Date
        date_reservation = st.date_input("Date", key="date_reservation", min_value=datetime.now().date())
        
        # Heures
        col1, col2 = st.columns(2)
        with col1:
            heure_debut = st.time_input("Heure de début", key="heure_debut", value=datetime.strptime("08:00", "%H:%M").time())
        with col2:
            heure_fin = st.time_input("Heure de fin", key="heure_fin", value=datetime.strptime("10:00", "%H:%M").time())
        
        # Participants
        participants = st.number_input("Nombre de participants", min_value=1, value=1, key="participants_reservation")
        
        if st.form_submit_button("Réserver"):
            if not personne:
                st.error("Le nom de la personne est obligatoire !")
            elif participants > capacite_salle:
                st.error(f"Le nombre de participants ({participants}) dépasse la capacité de la salle ({capacite_salle}) !")
            else:
                debut_str = heure_debut.strftime("%H:%M")
                fin_str = heure_fin.strftime("%H:%M")
                date_str = date_reservation.strftime("%Y-%m-%d")
                
                # Vérifier les heures
                if not heurs_valides(debut_str, fin_str):
                    st.error("Les heures doivent être entre 8h et 20h !")
                elif not duree_valide(debut_str, fin_str):
                    st.error("La durée doit être entre 30 minutes et 4 heures !")
                else:
                    # Vérifier les chevauchements
                    with ouvrir_base() as conn:
                        if chevauchement_existe(conn, salle_id, date_str, debut_str, fin_str):
                            st.error("Il y a déjà une réservation qui chevauche cet horaire pour cette salle !")
                        else:
                            conn.execute(
                                "INSERT INTO reservations (salle_id, personne, date, debut, fin, participants) VALUES (?, ?, ?, ?, ?, ?)",
                                [salle_id, personne, date_str, debut_str, fin_str, participants]
                            )
                            st.success(f"Réservation confirmée pour {personne} dans {salle_selectionnee} le {date_str} de {debut_str} à {fin_str} !")
                            st.rerun()
    else:
        st.warning("Ajoutez d'abord une salle pour pouvoir réserver.")


# ============================================================================
# SECTION 3: ANNULER UNE RESERVATION
# ============================================================================
st.header("🗑️ Annuler une réservation")

with ouvrir_base() as conn:
    reservations = conn.execute(
        """SELECT r.id, r.salle_id, s.nom as salle_nom, r.personne, r.date, r.debut, r.fin, r.participants
           FROM reservations r
           JOIN salles s ON r.salle_id = s.id
           ORDER BY r.date, r.debut"""
    ).fetchall()

if reservations:
    st.subheader("Liste des réservations")
    
    for res in reservations:
        cols = st.columns([2, 2, 1, 1, 1, 1])
        cols[0].write(f"{res['salle_nom']}")
        cols[1].write(f"{res['personne']}")
        cols[2].write(f"{res['date']}")
        cols[3].write(f"{res['debut']}-{res['fin']}")
        cols[4].write(f"{res['participants']} pers.")
        
        if cols[5].button("Annuler", key=f"ann_{res['id']}"):
            with ouvrir_base() as conn:
                conn.execute("DELETE FROM reservations WHERE id = ?", [res['id']])
            st.success(f"Réservation annulée : {res['salle_nom']} - {res['personne']} le {res['date']} de {res['debut']} à {res['fin']}")
            st.rerun()
else:
    st.info("Aucune réservation à annuler.")


# ============================================================================
# SECTION 4: PLANNING D'UNE SALLE SUR UNE SEMAINE
# ============================================================================
st.header("📆 Planning d'une salle sur une semaine")

if salles:
    salle_planning = st.selectbox("Sélectionnez une salle", options=salle_noms, key="salle_planning")
    salle_id_planning = salle_ids[salle_noms.index(salle_planning)]
    
    date_planning = st.date_input("Date de début (lundi)", key="date_planning", value=datetime.now().date())
    
    # Calculer le lundi de la semaine
    lundi = get_lundi(date_planning)
    
    # Récupérer les réservations pour cette salle sur la semaine
    with ouvrir_base() as conn:
        reservations_semaine = conn.execute(
            """SELECT id, date, debut, fin, personne, participants
               FROM reservations 
               WHERE salle_id = ? AND date >= ? AND date <= ?
               ORDER BY date, debut""",
            [salle_id_planning, lundi.strftime("%Y-%m-%d"), (lundi + timedelta(days=6)).strftime("%Y-%m-%d")]
        ).fetchall()
    
    # Afficher le planning par jour
    st.subheader(f"Planning de {salle_planning} - Semaine du {lundi.strftime('%Y-%m-%d')}")
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    dates_affichage = [lundi + timedelta(days=i) for i in range(7)]
    
    for i, (jour, date_aff) in enumerate(zip(jours, dates_affichage)):
        st.markdown(f"### {jour} {date_aff.strftime('%Y-%m-%d')}")
        
        # Réservations pour ce jour
        res_jour = [r for r in reservations_semaine if r['date'] == date_aff.strftime("%Y-%m-%d")]
        
        if res_jour:
            for res in res_jour:
                st.write(f"- **{res['debut']}-{res['fin']}** : {res['personne']} ({res['participants']} personnes)")
        else:
            st.write("Aucune réservation.")
        st.markdown("---")
else:
    st.warning("Ajoutez d'abord une salle pour voir son planning.")
