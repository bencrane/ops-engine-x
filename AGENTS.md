# AGENTS.md

Instructions for AI coding agents working in this repository. Read this before writing code.

## Project shape

- Python 3.12, FastAPI, uvicorn.
- Deployed to Railway from the `Dockerfile`.
- Secrets come from **Doppler only** (project `managed-agents-x-api`, config `prd`). Railway has exactly one environment variable: `DOPPLER_TOKEN`. The container entrypoint runs `doppler run -- uvicorn ...`, which fetches secrets and injects them into the process env before Python starts.
- There is no `.env` or `.env.example` in this repo, and you must not add one. The canonical list of secrets is `app/config.py` + the table in `README.md`.

## Rule 1: Startup must be secret-tolerant

The app **must boot successfully with zero secrets set**. `/health` must return 200 even if Doppler is unreachable, `DOPPLER_TOKEN` is missing, or a specific secret is absent from the Doppler config.

Practical consequences:

- Do **not** read secrets at import time or at module load.
- Do **not** construct API clients (Anthropic, OpenAI, database, etc.) as module-level globals that require secrets to initialize.
- Do **not** add `assert settings.foo` or raise in `app/config.py` when a value is missing.
- All new `Settings` fields must have a default (`None` for secrets, a safe default for non-secrets) so `Settings()` never raises.

## Rule 2: Use lazy, validated reads for every required secret

**Never read a required secret via `settings.<name>` directly in production code paths.** Direct reads give you `None` silently and fail with a cryptic `NoneType` or downstream 401. Use one of the two patterns below so the failure mode is always a loud, Doppler-pointing error.

There are two acceptable patterns. Pick based on context.

### Pattern A — FastAPI routes: `Depends()` factory (preferred for HTTP handlers)

For anything reached via an HTTP route, use a FastAPI dependency. This gives you a proper `503 Service Unavailable` with a clear message, and it's trivially overridable in tests.

Create it in `app/deps.py` (create the file the first time you need one):

```python
# app/deps.py
from anthropic import Anthropic
from fastapi import HTTPException
from app.config import settings

def get_anthropic() -> Anthropic:
    if not settings.anthropic_api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY not configured (check Doppler prd).",
        )
    return Anthropic(api_key=settings.anthropic_api_key)
```

Use it in a route:

```python
from fastapi import Depends
from anthropic import Anthropic
from app.deps import get_anthropic

@app.post("/summarize")
def summarize(client: Anthropic = Depends(get_anthropic)) -> SummarizeResponse:
    ...
```

### Pattern B — Everywhere else: `require()`

For code paths that aren't FastAPI routes — background workers, startup tasks, CLI entrypoints, library-style modules — use the `require()` helper from `app/config.py`. It raises `MissingSecretError` with a Doppler-pointing message.

```python
from anthropic import Anthropic
from app.config import require

def get_anthropic_client() -> Anthropic:
    return Anthropic(api_key=require("anthropic_api_key"))
```

### Do not do any of these

```python
from app.config import settings
client = Anthropic(api_key=settings.anthropic_api_key)   # silent None, cryptic failure later

_client = Anthropic(api_key=settings.anthropic_api_key)  # module-level, breaks boot tolerance

key = os.environ["ANTHROPIC_API_KEY"]                    # bypasses the contract, KeyError at import
```

### Optional / best-effort reads

If a secret is genuinely optional (the feature degrades gracefully when it's absent), read it directly from `settings` and branch on truthiness:

```python
from app.config import settings

if settings.some_optional_webhook_url:
    post_webhook(settings.some_optional_webhook_url, payload)
```

Reserve `Depends()` / `require()` for secrets whose absence should be a hard error at call time.

## Rule 3: Adding a new secret

Every new secret must be added in three places, in this order:

1. **Doppler**: add the variable to the `prd` config of the `managed-agents-x-api` project. The human operator does this; mention it in your PR description so they know.
2. **`app/config.py`**: add a typed, optional field to `Settings` using lowercase snake_case. pydantic-settings maps it to the uppercase env var automatically (case-insensitive).
3. **`README.md`**: add a row to the secrets table (name, required/optional, notes).

Then read it with `require("your_new_secret")` at the call site.

Do **not**:
- Add it to a `.env.example` (there isn't one, and there shouldn't be).
- Set it in `railway.toml` or Railway's variables UI. `DOPPLER_TOKEN` is the only Railway variable, ever.

## Rule 4: Don't touch the Doppler injection path

The following files implement the "Doppler is the only source of secrets" contract. Change them only with an explicit reason:

- `Dockerfile` — installs the Doppler CLI; must stay installed.
- `docker-entrypoint.sh` — runs `doppler run --` when `DOPPLER_TOKEN` is set, falls back to plain `uvicorn` otherwise so the container always boots. Do not remove the fallback; it is what lets `docker run` work locally without a token and preserves boot tolerance.
- `railway.toml` — Dockerfile builder + `/health` healthcheck. Do not switch to Nixpacks or move secrets into Railway variables.

## Rule 5: Verifying your change

Before opening a PR that touches config or a new integration:

1. Build and run the container with **no** env vars:
   ```bash
   docker build -t magx-api:test .
   docker run --rm -p 8088:8080 magx-api:test
   curl -f localhost:8088/health
   ```
   `/health` must return 200. The entrypoint will log that `DOPPLER_TOKEN` is not set; that is expected.

2. Hit `/`. It returns a `secrets_loaded` map showing which configured secrets are present. Without Doppler, everything should be `false` and the server should still be up.

3. If your change adds a route that calls a secret-backed service, verify that hitting it without the secret returns a clear `MissingSecretError` (500 with a readable message), not a `NoneType` traceback or a 401 from the upstream.

## Rule 6: Keep `/health` dumb

`/health` is the Railway healthcheck target. It must:
- Return 200 quickly.
- Not depend on any external service (no DB ping, no Anthropic call, no Doppler check).

If you want a deeper readiness check, add `/ready` as a separate endpoint.
