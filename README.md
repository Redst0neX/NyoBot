# NyoBot

A lightweight presence bot for [NyoChat](https://nyochat.fr/). It logs in with
your credentials and pings the homepage at a fixed interval (default: every
60 seconds) to keep your account looking active.

## How it works

1. On startup, the script performs a standard form login against
   `POST /login`, attempting to extract and submit a CSRF token found in the
   page (`<meta name="csrf-token">` or a hidden `csrf_token` input).
2. It reuses a `requests.Session`, so cookies (and therefore the
   authenticated session) persist across requests.
3. Every `NYOBOT_INTERVAL` seconds, it issues a `GET /` to keep the session
   alive and simulate presence.

No scheduler, headless browser, or external service is used — it's a single
long-running Python process.

## Requirements

- Python 3.9+
- A NyoChat account
- (Optional) a Raspberry Pi or any always-on Linux machine, if you want this
  to run continuously

## Installation

```bash
git clone <this-repo-url>
cd nyobot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env with your credentials
```

## Configuration

All configuration is done via environment variables, loaded from `.env`
(see `.env.example`):

| Variable            | Required | Default | Description                          |
|---------------------|----------|---------|---------------------------------------|
| `NYOCHAT_USERNAME`  | yes      | —       | Your NyoChat username                 |
| `NYOCHAT_PASSWORD`  | yes      | —       | Your NyoChat password                 |
| `NYOBOT_INTERVAL`   | no       | `60`    | Seconds between each homepage ping    |

`.env` is git-ignored — never commit it. `.env.example` contains placeholders
only and is safe to version.

## Usage

```bash
python3 nyobot.py
```

The script logs to stdout:

```
2026-10-10 10:00:00 [INFO] Login succeeded (https://nyochat.fr/login -> https://nyochat.fr/)
2026-10-10 10:00:00 [INFO] NyoBot started, pinging every 60 seconds.
2026-10-10 10:01:00 [INFO] Ping OK (status=200)
```

Stop with `Ctrl+C`.

## Running as a systemd service (Raspberry Pi / Linux)

A sample unit file is provided in `nyobot.service`. Adjust `User`,
`WorkingDirectory` and `ExecStart` to match your install path (and point
`ExecStart` at your virtualenv's Python if you used one):

```bash
sudo cp nyobot.service /etc/systemd/system/nyobot.service
sudo systemctl daemon-reload
sudo systemctl enable --now nyobot

# check status / logs
sudo systemctl status nyobot
journalctl -u nyobot -f
```

The unit restarts the process automatically on failure (`Restart=on-failure`,
15s backoff).

## Project structure

```
nyobot/
├── nyobot.py          # main script
├── requirements.txt   # Python dependencies
├── .env.example       # credential template (safe to commit)
├── .gitignore         # excludes .env, venv/, __pycache__
├── nyobot.service      # systemd unit template
└── README.md
```

## Known limitations

- **Login form field names are inferred**, not scraped from a verified DOM
  structure (`username`, `password`, `csrf_token`). NyoChat is built on
  [SocialPlace](https://github.com/ChatHivernal/SocialPlace), so field names
  should be close to Flask/Django conventions, but if login fails:
  1. Open `https://nyochat.fr/login` in a browser and inspect the form
     inputs' `name` attributes.
  2. Check the Network tab for the actual `POST` payload on submit.
  3. Update the `payload` dict in `login()` in `nyobot.py` accordingly.
- No retry/backoff logic beyond the systemd-level restart — a failed ping is
  logged and the loop continues; a failed *login* at startup exits the
  process.
- No support for 2FA/CAPTCHA login flows.

## Security notes

- Credentials are read from environment variables only, never hardcoded.
- The script only talks to `nyochat.fr` — no third-party requests, no
  telemetry.
- Treat `.env` like a password: don't share it, don't commit it.

## Contributing

PRs welcome — in particular, a confirmed/verified login payload (exact field
names) would let the heuristics in `get_csrf_token()` / `login()` be
simplified.

## License

MIT.
