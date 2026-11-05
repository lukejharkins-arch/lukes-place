# Deployment instructions

## Local (any machine with Python 3.11+, no installs)
```bash
cd on-court-only
python3 -m commerce.seed --reset      # builds data/oco.db, prints admin email and where the password was written
python3 -m agents.run all             # runs the 12-agent cycle
python3 -m reports.generate all       # daily, weekly, fortnightly, monthly reports
python3 server.py --port 8080         # http://127.0.0.1:8080  (admin: #/admin)
python3 -m unittest discover -s tests -t .
```
The admin password is random and written to `data/ADMIN_CREDENTIALS.local` (gitignored). Set `OCO_ADMIN_EMAIL` and `OCO_ADMIN_PASSWORD` to choose your own.

## Scheduled reports
`.github/workflows/oco-agents.yml` (repository root) runs the tests, the agent cycle and the right report for the day on a daily cron, and uploads the reports as a workflow artifact. GitHub only runs scheduled workflows from the default branch, so **it is not active until this branch is merged**. It does not commit, push, send or spend anything.

## Private hosted preview (when approved)
1. A small VM or container (e.g. Fly.io, Railway, Render) running `python3 server.py --host 0.0.0.0 --port $PORT` behind HTTPS.
2. Put it behind a reverse proxy with rate limiting and HTTP basic auth until launch.
3. Persist `data/oco.db` on a volume and back it up daily.
4. Never commit secrets; use environment variables.

The existing repository root `vercel.json` belongs to the unrelated Luke's Place app and was left untouched. Vercel's serverless model doesn't suit SQLite writes, so a container host is recommended for this app.

## Launch (founder approval required)
Shopify store + Payments onboarding → adapter pushes gate-passed products → webhook marks them sold. See `commerce/CHECKOUT_ARCHITECTURE.md`.
