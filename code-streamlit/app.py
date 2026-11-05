import streamlit as st

from base import ouvrir_base

st.title("Réservation de salles")

# Lit les salles et les affiche.
with ouvrir_base() as conn:
    salles = conn.execute("SELECT nom FROM salles").fetchall()

st.header("Salles")
for salle in salles:
    st.write(salle["nom"])

# Exemple : ajoute une salle.
nom = st.text_input("Nom")
capacite = st.number_input("Capacité", min_value=1, value=10)
if st.button("Ajouter") and nom:
    with ouvrir_base() as conn:
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", [nom, capacite])
    st.rerun()

# Ajoutez la suite de votre application ici.
