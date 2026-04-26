// Reusable helper for ops-engine-x scheduled-event tasks.
//
// Every scheduled task in this project does the exact same thing:
//   POST ${OPEX_API_URL}/internal/scheduler/tick
//        Authorization: Bearer <fresh M2M JWT from auth-engine-x>
//        { event_id, trigger_run_id }
//
// ops-engine-x owns the rest:
//   - Look up event_id in scheduled_events.
//   - Resolve target_service to a base URL (ops-engine-x's Doppler).
//   - POST the actual work to the target service, attaching its own
//     M2M JWT (no per-service bearer tokens).
//   - Record the outcome in scheduler_runs.
//   - Return the summary.
//
// Trigger.dev env vars: OPEX_API_URL, AUX_API_BASE_URL, AUX_M2M_API_KEY.
// The static OPEX_AUTH_TOKEN is no longer used — every call mints a
// fresh M2M JWT via `getM2MToken()`.

import { logger } from "@trigger.dev/sdk/v3";

import { getM2MToken, invalidateM2MToken } from "./m2m";

export type TickResult = {
  event_id: string;
  ok: boolean;
  http_status: number | null;
  duration_ms: number;
  summary: unknown;
  error: string | null;
  scheduler_run_id: string;
};

/**
 * Fire a scheduled event by telling ops-engine-x to dispatch it.
 *
 * Throws on:
 *   - Missing Trigger.dev env vars (OPEX_API_URL / AUX_API_BASE_URL /
 *     AUX_M2M_API_KEY).
 *   - Non-2xx from ops-engine-x's tick endpoint itself (event not found,
 *     service not registered, credentials missing, 5xx).
 *   - The dispatch being dispatched but the target returning non-2xx
 *     (i.e. ops-engine-x replies 200 with ok=false). Trigger.dev retries.
 *
 * On success, returns the TickResult so the Trigger.dev run log shows the
 * summary.
 */
export async function fireScheduledEvent(
  eventId: string,
  triggerRunId?: string,
): Promise<TickResult> {
  const opexUrl = process.env.OPEX_API_URL;
  if (!opexUrl) {
    throw new Error(
      "OPEX_API_URL must be set in the Trigger.dev dashboard.",
    );
  }

  const tickUrl = `${opexUrl.replace(/\/$/, "")}/internal/scheduler/tick`;
  logger.info("firing scheduled event", { eventId, tickUrl });

  const callTick = async (token: string) =>
    fetch(tickUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ event_id: eventId, trigger_run_id: triggerRunId ?? null }),
    });

  let token = await getM2MToken();
  let resp = await callTick(token);
  // One automatic retry on 401 — the cached token may be stale because
  // auth-engine-x rotated keys between mint and use.
  if (resp.status === 401) {
    invalidateM2MToken();
    token = await getM2MToken();
    resp = await callTick(token);
  }

  const rawText = await resp.text();
  if (!resp.ok) {
    logger.error("tick dispatcher failed", {
      eventId,
      status: resp.status,
      body: rawText.slice(0, 2000),
    });
    throw new Error(
      `ops-engine-x tick failed for ${eventId}: HTTP ${resp.status} — ${rawText.slice(0, 500)}`,
    );
  }

  const result = JSON.parse(rawText) as TickResult;

  if (!result.ok) {
    logger.error("target dispatch failed", {
      eventId,
      target_http_status: result.http_status,
      error: result.error,
      scheduler_run_id: result.scheduler_run_id,
    });
    throw new Error(
      `target for ${eventId} failed: ${result.error ?? `HTTP ${result.http_status ?? "?"}`} (scheduler_run_id=${result.scheduler_run_id})`,
    );
  }

  logger.info("scheduled event fired", {
    eventId,
    duration_ms: result.duration_ms,
    scheduler_run_id: result.scheduler_run_id,
  });
  return result;
}
