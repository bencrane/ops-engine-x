"""Thin HTTP client for the Anthropic Managed Agents API.

We use httpx directly rather than the anthropic SDK because the beta managed
agents endpoints are easier to debug over raw HTTP and we want the exact JSON
body from Anthropic stored verbatim as our forensic `raw` snapshot.
"""

from __future__ import annotations

from typing import Iterator

import httpx

from app.config import require

BASE_URL = "https://api.anthropic.com"
API_VERSION = "2023-06-01"
BETA_HEADER = "managed-agents-2026-04-01"


def _headers() -> dict[str, str]:
    return {
        "x-api-key": require("anthropic_api_key"),
        "anthropic-version": API_VERSION,
        "anthropic-beta": BETA_HEADER,
        "content-type": "application/json",
    }


def list_agents(include_archived: bool = False) -> Iterator[dict]:
    """Yield every agent across all pages."""
    params: dict[str, str | int] = {"limit": 100}
    if include_archived:
        params["include_archived"] = "true"
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        while True:
            resp = client.get("/v1/agents", params=params, headers=_headers())
            resp.raise_for_status()
            body = resp.json()
            for agent in body.get("data", []):
                yield agent
            next_page = body.get("next_page")
            if not next_page:
                return
            params["page"] = next_page


def get_agent(agent_id: str) -> dict:
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        resp = client.get(f"/v1/agents/{agent_id}", headers=_headers())
        resp.raise_for_status()
        return resp.json()
