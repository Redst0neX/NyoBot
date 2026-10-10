# NyoBot
An automatic bot to stay active on nyochat.fr

# NyoBot — script de présence pour NyoChat.fr

Ce script se connecte à votre compte NyoChat et recharge la page d'accueil
toutes les 60 secondes (configurable) pour garder une présence active.

## Installation sur le Raspberry Pi

```bash
# 1. Copier le dossier nyobot/ sur le Pi, par exemple dans /home/pi/nyobot

# 2. Installer les dépendances
cd /home/pi/nyobot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Configurer les identifiants
cp .env.example .env
nano .env   # remplir NYOCHAT_USERNAME et NYOCHAT_PASSWORD

# 4. Tester en direct (Ctrl+C pour arrêter)
python3 nyobot.py
```

Si le script affiche "La connexion a peut-être échoué" : voir la section
**Dépannage** ci-dessous, les noms des champs du formulaire doivent être
ajustés.

## Lancer en permanence avec systemd

```bash
# Adapter nyobot.service si besoin (chemin, utilisateur, ou utiliser le venv :
# ExecStart=/home/pi/nyobot/venv/bin/python3 /home/pi/nyobot/nyobot.py)

sudo cp nyobot.service /etc/systemd/system/nyobot.service
sudo systemctl daemon-reload
sudo systemctl enable nyobot
sudo systemctl start nyobot

# Vérifier que ça tourne
sudo systemctl status nyobot

# Voir les logs en direct
journalctl -u nyobot -f
```

## Dépannage : la connexion échoue

Le script devine les noms des champs du formulaire (`username`, `password`,
`csrf_token`). Si ça ne marche pas :

1. Ouvrez https://nyochat.fr/login dans votre navigateur.
2. Clic droit sur le champ "Username" → **Inspecter**.
3. Repérez l'attribut `name="..."` du `<input>` (et faites pareil pour le mot
   de passe).
4. Ouvrez aussi l'onglet **Réseau** (Network) de votre navigateur, faites
   "Login", et regardez la requête POST envoyée : ça vous donnera les noms
   exacts des champs et l'URL cible si elle diffère de `/login`.
5. Ajustez le dictionnaire `payload` dans `nyobot.py` en conséquence.

## Sécurité

- Le mot de passe est stocké uniquement dans `.env`, jamais dans le code.
- Ne partagez jamais votre fichier `.env`.
- Le script n'envoie aucune donnée ailleurs qu'à nyochat.fr.
