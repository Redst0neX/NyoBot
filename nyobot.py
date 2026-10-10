#!/usr/bin/env python3
"""
NyoBot script python permettant de se connecter à NyoChat.fr et recharge la page
toutes les minutes pour rester actif avec un compte.

Usage :
    1. Copiez .env.example en .env et remplissez USERNAME / PASSWORD
    2. pip install -r requirements.txt
    3. python3 nyobot.py

Pensez à vérifier les noms des champs du formulaire de login si la
connexion échoue (voir README.md).
"""

import os
import re
import sys
import time
import logging
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://nyochat.fr"
LOGIN_URL = f"{BASE_URL}/login"
HOME_URL = f"{BASE_URL}/"

USERNAME = os.getenv("NYOCHAT_USERNAME")
PASSWORD = os.getenv("NYOCHAT_PASSWORD")
INTERVAL_SECONDS = int(os.getenv("NYOBOT_INTERVAL", "60"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("nyobot")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NyoBot/1.0; personal presence script)",
}


def get_csrf_token(session: requests.Session, url: str) -> str | None:
    """Essaie de récupérer un token CSRF depuis une balise meta ou un input caché."""
    resp = session.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    # Essai 1 : meta tag (vu dans le <head> de la page login)
    meta_match = re.search(
        r'<meta[^>]+name=["\']csrf-token["\'][^>]+content=["\']([^"\']+)["\']',
        resp.text,
        re.IGNORECASE,
    )
    if meta_match:
        return meta_match.group(1)

    # Essai 2 : input caché classique
    input_match = re.search(
        r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']',
        resp.text,
        re.IGNORECASE,
    )
    if input_match:
        return input_match.group(1)

    return None


def login(session: requests.Session) -> bool:
    """Se connecte à NyoChat. Retourne True si ça a probablement marché."""
    if not USERNAME or not PASSWORD:
        log.error("NYOCHAT_USERNAME / NYOCHAT_PASSWORD manquants dans .env")
        return False

    csrf_token = get_csrf_token(session, LOGIN_URL)

    payload = {
        "username": USERNAME,
        "password": PASSWORD,
    }
    if csrf_token:
        payload["csrf_token"] = csrf_token

    resp = session.post(LOGIN_URL, data=payload, headers=HEADERS, timeout=15, allow_redirects=True)

    # Heuristique : si on est redirigé hors de /login et qu'on ne voit plus
    # le formulaire de connexion, on considère que c'est bon.
    looks_logged_in = (
        resp.status_code == 200
        and "Login to NyoChat" not in resp.text
        and resp.url != LOGIN_URL
    )

    if looks_logged_in:
        log.info("Connexion réussie (%s -> %s)", LOGIN_URL, resp.url)
    else:
        log.warning(
            "La connexion a peut-être échoué (status=%s, url finale=%s). "
            "Vérifiez les noms de champs du formulaire.",
            resp.status_code,
            resp.url,
        )

    return looks_logged_in


def ping_home(session: requests.Session) -> None:
    """Recharge la page d'accueil pour maintenir la session/présence active."""
    try:
        resp = session.get(HOME_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        log.info("Ping OK (status=%s)", resp.status_code)
    except requests.RequestException as e:
        log.error("Erreur lors du ping : %s", e)


def main() -> None:
    session = requests.Session()

    if not login(session):
        log.error("Connexion initiale échouée, arrêt du script.")
        sys.exit(1)

    log.info("NyoBot démarré, ping toutes les %s secondes.", INTERVAL_SECONDS)

    while True:
        ping_home(session)
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
