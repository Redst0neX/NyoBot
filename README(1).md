# Follower Invite Bot

Bot Scratch qui surveille tes nouveaux followers et les invite automatiquement
dans un studio, avec un délai aléatoire de 2 à 8 minutes pour éviter un
comportement trop robotique.

## ⚠️ À lire avant de déployer

- Ce bot automatise une action sur un compte Scratch réel. Même s'il respecte
  un rythme raisonnable, l'automatisation de compte reste dans une zone grise
  des règles de Scratch. Utilise-le avec modération et surveille ses logs.
- **Ne mets jamais ton mot de passe en clair dans un fichier versionné**
  (`.env`, `bot.py`, etc.). Utilise toujours les variables d'environnement de
  bot-hosting.net.
- Au premier lancement, le bot **n'invite personne** : il enregistre juste la
  liste actuelle de tes followers comme référence, puis n'invite que les
  *nouveaux* followers détectés ensuite. Ça évite d'inviter d'un coup des
  centaines de personnes déjà présentes.

## Installation locale (test)

```bash
pip install -r requirements.txt
```

Copie `.env.example` en `.env` et remplis tes identifiants, puis :

```bash
python bot.py
```

## Déploiement sur bot-hosting.net

1. Crée un nouveau bot de type **Python**
2. Upload tous les fichiers du dossier (`bot.py`, `requirements.txt`)
3. Dans l'onglet **Variables/Environnement**, ajoute :
   - `SCRATCH_USERNAME` et `SCRATCH_PASSWORD`
     (ou `SCRATCH_SESSION_ID` à la place du mot de passe — plus sûr)
   - `STUDIO_ID` → l'ID de ton studio (dans l'URL du studio)
4. Définis la commande de démarrage : `python bot.py`
5. Démarre le bot

## Comment récupérer un Session ID (recommandé, évite de stocker ton mdp)

1. Connecte-toi à scratch.mit.edu dans ton navigateur
2. Ouvre les outils développeur (F12) → onglet "Application"/"Stockage" → Cookies
3. Copie la valeur du cookie `scratchsessionsid`
4. Mets cette valeur dans la variable `SCRATCH_SESSION_ID`

## Fichiers

- `bot.py` — logique principale
- `requirements.txt` — dépendances Python
- `data/known_followers.json` — mémoire persistante des followers déjà traités
  (créé automatiquement, ne pas supprimer sinon le bot ré-inviterait tout le monde)
- `bot.log` — journal des actions du bot

## Personnalisation

Dans `bot.py`, tu peux ajuster :
- `CHECK_INTERVAL` → fréquence de vérification des nouveaux followers (secondes)
- `MIN_DELAY` / `MAX_DELAY` → plage du délai aléatoire avant invitation (secondes)
