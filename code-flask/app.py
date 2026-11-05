from flask import Flask, redirect, render_template_string, request

from base import ouvrir_base

# Le HTML de la page.
PAGE = """
<h1>Réservation de salles</h1>

<h2>Salles</h2>
<ul>
  {% for salle in salles %}
    <li>{{ salle["nom"] }}</li>
  {% endfor %}
</ul>

<form method="post" action="/salles">
  <input name="nom" placeholder="Nom" required>
  <input name="capacite" type="number" min="1" placeholder="Capacité" required>
  <button>Ajouter</button>
</form>
"""

app = Flask(__name__)


# Page d'accueil : lit les salles et affiche PAGE.
@app.get("/")
def accueil():
    with ouvrir_base() as conn:
        salles = conn.execute("SELECT nom FROM salles").fetchall()
    return render_template_string(PAGE, salles=salles)


# Exemple : reçoit le formulaire et ajoute une salle.
@app.post("/salles")
def ajouter_salle():
    nom = request.form["nom"]
    capacite = int(request.form["capacite"])
    with ouvrir_base() as conn:
        conn.execute("INSERT INTO salles (nom, capacite) VALUES (?, ?)", [nom, capacite])
    return redirect("/")


# Ajoutez vos fonctions ici. Le HTML va dans PAGE.


if __name__ == "__main__":
    app.run(debug=True)
