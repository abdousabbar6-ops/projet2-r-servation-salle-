# Réservation de salles

## Le projet
Permettre au personnel d'un bâtiment universitaire de réserver lui-même une salle, sans conflit et dans la limite de sa capacité.

## Technologies
Python, SQLite, pytest. Framework : Flask (`code-flask`) ou Streamlit (`code-streamlit`).

## Commandes
- Lancer l'application : `python app.py` dans `code-flask`, `streamlit run app.py` dans `code-streamlit`
- Lancer les tests : `pytest` dans le dossier de code

## Base de données
Tables et exemples dans `base.sql`. `data.db` se crée au premier lancement. Supprimer `data.db` après un changement de `base.sql`.

## Règles métier
- Deux réservations d'une même salle ne se chevauchent pas. Finir à 12 h et commencer à 12 h est autorisé.
- Le nombre de participants ne dépasse pas la capacité de la salle.
- Une réservation a lieu entre 8 h et 20 h et dure de 30 min à 4 h.
- Supprimer une salle supprime ses réservations.
- Il n'y a pas d'authentification. La semaine va du lundi au dimanche.

## Façon de travailler
- Une fonctionnalité à la fois.
- Ajouter ou mettre à jour les tests à chaque fonctionnalité, puis lancer `pytest`.
- Ne pas ajouter d'autre dépendance sans le demander.
- Ne faire `git push` que si le binôme le demande.

## À vous d'ajouter
<!-- Ajoutez ici ce que vous voulez que l'agent respecte. Par exemple :
- Ne rien ajouter qui n'est pas demandé.
- Mettre les règles dans un fichier `regles.py`, sans framework.
- Utiliser une base séparée pour les tests.
-->
