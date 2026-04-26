// Mint short-lived M2M JWTs for the Trigger.dev project.
//
// Trigger.dev tasks call ops-engine-x's `/internal/scheduler/tick` route,
// which is now M2M-guarded (require_m2m, verified against auth-engine-x's
// JWKS). Static `OPEX_AUTH_TOKEN` no longer works.
//
// This helper is the TS-side counterpart of `aux_m2m_client` (Python). It
// POSTs to auth-engine-x's M2M token endpoint, gets back an EdDSA JWT
// (~5min TTL), and caches it in-memory across task runs in the same
// Trigger.dev process.
//
// Env vars required in the Trigger.dev dashboard:
//   AUX_API_BASE_URL  — auth-engine-x base URL
//   AUX_M2M_API_KEY   — this Trigger.dev project's M2M API key
//
// Refresh leeway: refresh ~30s before expiry to avoid serving a token
// that races the receiver's clock-skew tolerance.

const REFRESH_LEEWAY_MS = 30_000;

let cachedToken: string | null = null;
let cachedExpMs = 0;

function decodeExpMs(jwt: string): number {
  // JWT = header.payload.signature ; payload is base64url-encoded JSON.
  const parts = jwt.split(".");
  if (parts.length < 2) {
    throw new Error("Malformed JWT from auth-engine-x: missing payload");
  }
  const padded = parts[1] + "===".slice((parts[1].length + 3) % 4);
  const payload = JSON.parse(
    Buffer.from(padded, "base64").toString("utf-8"),
  ) as { exp?: number };
  if (typeof payload.exp !== "number") {
    throw new Error("M2M JWT has no `exp` claim");
  }
  return payload.exp * 1000;
}

async function mint(): Promise<string> {
  const baseUrl = process.env.AUX_API_BASE_URL;
  const apiKey = process.env.AUX_M2M_API_KEY;
  if (!baseUrl || !apiKey) {
    throw new Error(
      "AUX_API_BASE_URL and AUX_M2M_API_KEY must be set in the Trigger.dev dashboard.",
    );
  }
  const url = `${baseUrl.replace(/\/$/, "")}/api/auth/m2m/token`;
  const resp = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });
  const text = await resp.text();
  if (!resp.ok) {
    throw new Error(
      `auth-engine-x rejected M2M mint (HTTP ${resp.status}): ${text.slice(0, 500)}`,
    );
  }
  let parsed: { token?: string; access_token?: string; jwt?: string };
  try {
    parsed = JSON.parse(text);
  } catch {
    throw new Error("M2M mint response was not JSON");
  }
  const token = parsed.token ?? parsed.access_token ?? parsed.jwt;
  if (!token) {
    throw new Error(
      `M2M mint response missing token field: keys=${Object.keys(parsed).join(",")}`,
    );
  }
  return token;
}

/**
 * Get a valid M2M JWT, minting (or refreshing) if needed.
 *
 * Safe to call from any Trigger.dev task; the cache is process-local and
 * keyed by nothing (one identity per process). On a cache miss or near-
 * expiry, mints a fresh token from auth-engine-x.
 */
export async function getM2MToken(): Promise<string> {
  const now = Date.now();
  if (cachedToken && cachedExpMs - now > REFRESH_LEEWAY_MS) {
    return cachedToken;
  }
  const token = await mint();
  cachedToken = token;
  cachedExpMs = decodeExpMs(token);
  return token;
}

/** Drop the cached token (used after a 401 on a downstream call). */
export function invalidateM2MToken(): void {
  cachedToken = null;
  cachedExpMs = 0;
}
