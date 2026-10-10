# scratch-relay-worker

Worker Cloudflare qui relaie les requêtes vers `api.scratch.mit.edu`,
pour contourner les erreurs 429 rencontrées par certains hébergeurs
(Replit, Render, etc.) quand ils appellent l'API Scratch directement.

Le worker ne fait **aucune** logique métier : il transmet tel quel
n'importe quel chemin `/api/<chemin scratch>` vers
`https://api.scratch.mit.edu/<chemin scratch>` et renvoie la réponse
brute (même status, même JSON).

## Déploiement

```bash
npm install -g wrangler
wrangler login
cd scratch-relay-worker

# Optionnel mais recommandé : protéger le worker par un token
wrangler secret put RELAY_TOKEN
# (choisis une valeur aléatoire longue, ex: openssl rand -hex 32)

wrangler deploy
```

Après déploiement, tu obtiens une URL du type :

```
https://scratch-relay-worker.<ton-sous-domaine>.workers.dev
```

## Test rapide

```bash
curl https://scratch-relay-worker.<ton-sous-domaine>.workers.dev/health
# -> {"ok":true}

curl https://scratch-relay-worker.<ton-sous-domaine>.workers.dev/api/users/griffpatch
# -> proxy transparent de https://api.scratch.mit.edu/users/griffpatch
```

Avec un token configuré :

```bash
curl -H "Authorization: Bearer <ton_token>" \
  https://scratch-relay-worker.<ton-sous-domaine>.workers.dev/api/users/griffpatch
```

## Intégration côté bot.py

Voir `bot_relay_patch.md` pour la marche à suivre exacte : il s'agit
de remplacer les appels directs à `api.scratch.mit.edu` dans
`get_total_views()` par des appels vers ce worker.

Note : `session.connect_user()` (via `scratchattach`) fait aussi des
appels à l'API Scratch en interne, mais scratchattach ne permet pas
nativement de rediriger son host cible. Le patch fourni migre
uniquement `get_total_views()`, qui est le point le plus simple et
le plus consommateur de requêtes (jusqu'à 10 appels par utilisateur).
Si le 429 persiste spécifiquement sur `connect_user()`, il faudra
soit patcher scratchattach plus en profondeur, soit faire un appel
manuel via `requests` vers le worker pour récupérer les infos de
profil aussi (followers, projects, join date) au lieu d'utiliser
`session.connect_user()`.
