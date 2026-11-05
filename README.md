# Réservation de salles

> **Permettre à chacun de réserver une salle du bâtiment, sans conflit et dans la limite de sa capacité.**

Séance 2 · En binôme · Avec un agent de code, OpenCode ou Mistral Vibe.

[Démarrer](#démarrer)

## Votre parcours

- [ ] **1. Coder et relire** : l'application en petites demandes, avec une revue de l'agent par fonctionnalité.
- [ ] **2. Ajouter les skills** : à l'annonce en séance, continuez avec les skills et regardez ce qui change.
- [ ] **3. Créer votre skill** : un skill pour la documentation de votre code.
- [ ] **4. Faire évoluer** : une demande de changement sera annoncée en séance.
- [ ] **5. Bonus** : ajouter ce qui est dans « Si vous avez fini ».

`AGENTS.md` est déjà rempli. Lisez-le et ajoutez ce que vous voulez dans « À vous d'ajouter ».

## Le contexte

Dans un bâtiment universitaire, les salles se réservent par mail auprès du secrétariat, qui tient un tableur. Les demandes se croisent, les doubles réservations sont fréquentes et certaines salles sont réservées pour des groupes trop grands. Le secrétariat veut que chacun puisse réserver lui-même, avec des règles appliquées automatiquement.

## Les données

| Objet | Ce qu’on enregistre |
|---|---|
| **Salle** | nom, capacité, présence d’un projecteur |
| **Réservation** | salle, personne, date, heure de début et de fin, nombre de participants |

## Ce que l’application doit faire

- [ ] Ajouter, modifier ou supprimer une salle
- [ ] Réserver une salle au nom d’une personne
- [ ] Annuler une réservation
- [ ] Afficher le planning d’une salle sur une semaine

## Les règles

- Deux réservations d’une même salle ne se chevauchent pas. Finir à 12 h et commencer à 12 h est autorisé.
- Le nombre de participants ne dépasse pas la capacité de la salle.
- Une réservation a lieu entre 8 h et 20 h et dure de 30 min à 4 h.
- Supprimer une salle supprime ses réservations.
- Il n’y a pas d’authentification. La semaine va du lundi au dimanche.

## Pour vérifier

Salle S1 de capacité 20, déjà réservée le lundi de 10 h à 12 h.

| Action | Résultat attendu |
|---|---|
| Lundi, 11 h à 13 h | Refusée : chevauchement |
| Lundi, 12 h à 13 h | Acceptée |
| Lundi, 14 h à 15 h, 25 participants | Refusée : capacité dépassée |
| Lundi, 7 h 30 à 9 h | Refusée : avant 8 h |
| Mardi, 14 h à 14 h 20 | Refusée : moins de 30 min |
| Mardi, 8 h à 13 h | Refusée : plus de 4 h |

## Si vous avez fini

Chercher une salle libre selon le créneau et la capacité, afficher le taux d’occupation, exporter le planning.

## Ce qui est libre

Le framework (Flask ou Streamlit), l’organisation du code et l’interface. La base SQLite est fournie avec des exemples, et vous pouvez la modifier. Python, SQLite et pytest sont imposés.

## À la fin de la séance

- Le but : une application qui fonctionne, avec les fonctionnalités demandées.
- Poussez votre travail sur GitHub.

---

# Démarrer

Python 3.11 ou plus est nécessaire.

## Préparer Git

Une seule fois par PC :

```bash
git config --global user.name "Votre nom"
git config --global user.email "votre@adresse.be"
```

GitHub n'accepte pas votre mot de passe dans le terminal. Si `git clone` refuse la connexion, installez [GitHub CLI](https://cli.github.com) et lancez `gh auth login`.

## Créer votre dépôt

1. Un membre du binôme ouvre <https://github.com/umons-ig/codelab-agent>, clique sur **Use this template**, puis **Create a new repository**, et choisit **Private**.
2. Dans **Settings**, puis **Collaborators**, il ajoute son partenaire. Le partenaire accepte l'invitation.
3. Chacun récupère le dépôt sur sa machine, puis ouvre le dossier :

```bash
git clone <adresse-de-votre-dépôt>
```

## Choisir votre dossier

- `code-streamlit` : le plus simple. [Premiers pas](https://docs.streamlit.io/get-started).
- `code-flask` : plus de contrôle. [Démarrage rapide](https://flask.palletsprojects.com/en/stable/quickstart/).

Gardez un dossier et supprimez l'autre. Chacun contient un `app.py` qui lit la base, l'affiche et donne un exemple de formulaire.

## Installer et lancer

Avec Streamlit, remplacez `code-flask` par `code-streamlit`.

macOS ou Linux, depuis la racine du dépôt :

```bash
cd code-flask
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Windows (PowerShell), depuis la racine du dépôt :

```powershell
cd code-flask
py -m venv .venv
Set-ExecutionPolicy -Scope Process RemoteSigned
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest
```

Puis lancez l'application :

- Flask : `python app.py`, puis <http://127.0.0.1:5000>
- Streamlit : `streamlit run app.py`

Sur Mac, gardez `127.0.0.1` pour Flask. Avec `localhost`, vous pouvez tomber sur AirPlay, qui utilise aussi le port 5000, et obtenir une erreur 403.

## Comprendre le code

Vous travaillez dans `app.py`. `base.py` ouvre la base : vous n'avez pas besoin de le modifier.

- **Flask** : chaque adresse a sa fonction. `accueil` lit la base et affiche `PAGE`, qui contient le HTML. `ajouter_salle` reçoit le formulaire, écrit dans la base et revient à l'accueil. Pour une nouvelle fonctionnalité, ajoutez un formulaire dans `PAGE` et une fonction.
- **Streamlit** : le fichier s'exécute de haut en bas, puis à nouveau à chaque clic. Pour une nouvelle fonctionnalité, ajoutez vos champs, vos boutons et vos requêtes à la suite du fichier.

## La base

`base.sql` contient les tables et des exemples. `data.db` se crée au premier lancement. Pour repartir de zéro, ou après un changement de `base.sql`, supprimez `data.db`. [Documentation de `sqlite3`](https://docs.python.org/3/library/sqlite3.html).

| Table | Colonnes |
|---|---|
| `salles` | `id`, `nom`, `capacite`, `projecteur` |
| `reservations` | `id`, `salle_id`, `personne`, `date`, `debut`, `fin`, `participants` |

`projecteur` vaut 1 ou 0. Les dates sont au format `2026-11-09` et les heures au format `10:00`.

## Bien travailler avec l'agent

- Une petite demande à la fois.
- Donnez les règles et un exemple à vérifier.
- Demandez des tests, puis lancez `pytest`.
- Essayez l'application et lisez le diff.
- Faites un commit à chaque étape qui marche.
- Si ça part de travers, revenez au dernier commit avec `git restore .`, supprimez les nouveaux fichiers créés par l’agent, puis reformulez.

Trop vague : « Fais-moi l'application. »

Précis : « Ajoute la réservation d'une salle. Refuse les chevauchements : finir à 12 h et commencer à 12 h est autorisé. Ajoute les tests et lance pytest. »

## Travailler à deux

Chacun travaille sur son PC. `git pull` avant de travailler, `git push` après chaque commit :

```bash
git pull
```

```bash
git add -A
git commit -m "ajout de la fonctionnalité"
git push
```

Si `git push` est refusé, votre partenaire a poussé entre-temps. Récupérez son travail, puis poussez à nouveau :

```bash
git pull --no-rebase --no-edit
git push
```

En cas de conflit, corrigez les fichiers indiqués, puis faites `git add -A`, `git commit -m "fusion"` et `git push`.

## Relire chaque fonctionnalité

1. Faites un commit de la fonctionnalité.
2. Dans une nouvelle session de l'agent, demandez : `Fais une revue de code de git show, sans rien modifier`.
3. Lancez `pytest`, ouvrez la page, puis classez chaque remarque : juste, fausse ou inutile.
4. Faites corriger les remarques justes par l'agent.

Si votre dernier commit est une fusion, `git show` n'affiche pas votre travail. Demandez alors la revue de `git show HEAD^1`.

Avant de passer à la suite, vérifiez trois points :

- Est-ce bien ce qui était demandé, sans rien en plus ?
- Un cas limite a-t-il été essayé : champ vide, doublon, conflit ?
- Savez-vous expliquer ce code ?

## Ajouter les skills

À faire à l'annonce en séance, à la racine de votre dépôt, après un `git pull`.

```bash
git clone https://github.com/umons-ig/codelab-skills ../codelab-skills
mkdir -p .agents/skills
cp -R ../codelab-skills/ajouter-fonctionnalite ../codelab-skills/commit-push .agents/skills/
git add -A
git commit -m "ajoute les skills"
git push
```

Un seul membre du binôme le fait. L'autre fait ensuite `git pull`.

Sous Windows (PowerShell), utilisez `New-Item -ItemType Directory -Force .agents/skills`, puis `Copy-Item -Recurse` pour chaque skill.

Ouvrez une nouvelle session de l'agent et continuez sur la fonctionnalité suivante :

- Pour coder, avec Mistral Vibe : `/ajouter-fonctionnalite`. Avec OpenCode : `Utilise le skill ajouter-fonctionnalite`.
- Pour faire un commit et pousser, avec Mistral Vibe : `/commit-push`. Avec OpenCode : `Utilise le skill commit-push`.

Mistral Vibe ne lit ces skills que si vous faites confiance au dossier au lancement.

Comparez avec vos premières fonctionnalités : la taille du changement, les fichiers ajoutés, les tests et ce que l'agent annonce. `git show --stat` donne la taille du dernier commit. Un seul essai ne prouve rien, car l'agent ne répond pas pareil d'une fois à l'autre.

## Créer votre skill

Chaque binôme crée un skill pour la documentation, pendant la réalisation avec les skills.

- Avec Mistral Vibe : `/skill-creator Crée un skill expliquer-code : il lit git diff, résume en 5 lignes, dessine un diagramme de séquence et un flowchart`.
- Avec OpenCode : demandez à l'agent d'écrire le fichier `.agents/skills/expliquer-code/SKILL.md`, avec la même description.

Relisez le fichier créé et raccourcissez-le si besoin. Ouvrez ensuite une nouvelle session et appelez le skill : `/expliquer-code` avec Mistral Vibe, `Utilise le skill expliquer-code` avec OpenCode.

## Lancer l'agent

Installez un des deux agents, puis tapez sa commande dans le terminal, **à la racine du dépôt**. Si vous êtes dans votre dossier de code, revenez-y avec `cd ..` :

| Agent | Installation | Lancement |
|---|---|---|
| OpenCode | `curl -fsSL https://opencode.ai/install \| bash` ou `npm install -g opencode-ai` | `opencode` |
| Mistral Vibe | `curl -LsSf https://mistral.ai/vibe/install.sh \| bash` ou `uv tool install mistral-vibe` | `vibe` |

Sous Windows, `curl … | bash` ne fonctionne pas dans PowerShell. Utilisez `npm install -g opencode-ai` (Node.js requis) ou installez uv, puis Vibe :

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
uv tool install mistral-vibe
```

Dans OpenCode, choisissez un modèle gratuit avec `/models`, puis tapez `free`.
Mistral Vibe demande de se connecter avec un compte Mistral au premier lancement.

Avant de lancer l'agent, lisez `AGENTS.md`.
