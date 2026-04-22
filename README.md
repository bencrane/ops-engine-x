# managed-agents-x-api

FastAPI service deployed to Railway with secrets managed via Doppler.

## Architecture

- **Runtime**: Python 3.12, FastAPI, uvicorn
- **Secrets**: Doppler (project `managed-agents-x-api`, config `prd`) is the single source of truth
- **Deployment**: Railway builds the `Dockerfile`; the only Railway env var is `DOPPLER_TOKEN`
- **Secret injection**: the container runs `doppler run -- uvicorn ...`, which fetches and injects all Doppler secrets at process start

The app is designed to boot successfully even with zero secrets configured. Any feature that needs a secret reads it lazily via `app.config.require("...")` and fails clearly at call time if the secret is missing.

> **For AI agents working in this repo:** read [`AGENTS.md`](AGENTS.md) first. It codifies the secret-handling conventions (use `require()`, never module-level clients, `DOPPLER_TOKEN` is the only Railway var) that are specific to this project.

## Secret contract

The canonical list of secrets lives in [`app/config.py`](app/config.py). No `.env` or `.env.example` is maintained in this repo — Doppler is the source of truth.

Current secrets:

| Name | Required | Notes |
| ---- | -------- | ----- |
| `ANTHROPIC_API_KEY` | lazy | Needed only by code paths that call Anthropic |

## Local development

Install the Doppler CLI once:

```bash
brew install dopplerhq/cli/doppler
doppler login
doppler setup   # select project: managed-agents-x-api, config: prd
```

Install Python deps and run:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
doppler run -- uvicorn app.main:app --reload --port 8080
```

Smoke test:

```bash
curl localhost:8080/health   # {"status":"ok"}
curl localhost:8080/         # includes secrets_loaded map
```

## Railway deployment

1. Connect the GitHub repo to a Railway service.
2. In Doppler, generate a service token for the `prd` config.
3. In Railway → Variables, set a single variable: `DOPPLER_TOKEN` = (that token).
4. Deploy. Railway builds the Dockerfile and runs the entrypoint.

`railway.toml` configures the Dockerfile build, `/health` healthcheck, and `on_failure` restart policy.

## Adding a new secret

1. Add it to the Doppler `prd` config.
2. Add a typed field to `Settings` in `app/config.py`.
3. At the call site that needs it, use `require("new_secret_name")`.
4. Redeploy (Railway will pick up the new value on next boot via `doppler run --`).
