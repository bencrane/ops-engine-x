// Reusable helper for ops-engine-x scheduled ticks.
//
// Every scheduled task in this project follows the same pattern:
//   1. POST an empty body to an internal endpoint on some backend service
//      (serx-api, future oex-api, etc.), with the service's bearer token.
//   2. Record the outcome (status, body, duration, error) to ops-engine-x's
//      `scheduler_runs` table by POSTing to
//      `${OPEX_API_URL}/internal/scheduler/runs` with `OPEX_AUTH_TOKEN`.
//
// Task files stay tiny — they just declare cron, task id, target, and call
// this helper. All boilerplate (timing, truncation, logging, throwing on
// failure so Trigger.dev shows the run as errored) lives here.

import { logger } from "@trigger.dev/sdk/v3";

export type TickConfig = {
  /** Trigger.dev task id, also used as `task_id` in the log row. */
  taskId: string;
  /**
   * Base URL of the target service, e.g. `process.env.SERX_API_URL`.
   * Trailing slashes are trimmed.
   */
  targetBaseUrl: string | undefined;
  /** Path appended to `targetBaseUrl`. Must start with `/`. */
  targetPath: string;
  /**
   * Bearer token for the target service (must live in the Trigger.dev
   * dashboard env, per environment), e.g. `process.env.SERX_AUTH_TOKEN`.
   */
  targetToken: string | undefined;
  /** Optional JSON-serialisable body. Defaults to `{}`. */
  body?: unknown;
  /**
   * Trigger.dev run id, for cross-linking log rows to the Trigger.dev
   * dashboard. Pass `ctx.run.id` from the task.
   */
  triggerRunId?: string;
};

// Hard cap on how much response body we store per run. 8KB is plenty for
// a "dispatched 3, skipped 0" summary; anything bigger is almost certainly
// a stack trace or a full payload echo and not useful in the log table.
const MAX_SUMMARY_BYTES = 8 * 1024;

/**
 * Execute the tick and record it to ops-engine-x.
 *
 * Throws on any non-2xx from the target, after logging, so Trigger.dev
 * shows the run as errored in its own dashboard. The log row to ops-engine-x
 * is best-effort — if *that* request fails, we log a warning but do not
 * mask the original target failure.
 */
export async function tickAndLog(cfg: TickConfig): Promise<unknown> {
  const opexUrl = process.env.OPEX_API_URL;
  const opexToken = process.env.OPEX_AUTH_TOKEN;

  if (!cfg.targetBaseUrl || !cfg.targetToken) {
    throw new Error(
      `Missing target env for task ${cfg.taskId}: targetBaseUrl and targetToken must be set in the Trigger.dev dashboard.`,
    );
  }
  if (!opexUrl || !opexToken) {
    throw new Error(
      `Missing OPEX_API_URL / OPEX_AUTH_TOKEN in the Trigger.dev dashboard — cannot log run of ${cfg.taskId}.`,
    );
  }

  const targetUrl = `${cfg.targetBaseUrl.replace(/\/$/, "")}${cfg.targetPath}`;
  const bodyPayload = JSON.stringify(cfg.body ?? {});

  const startedAt = new Date();
  let finishedAt: Date;
  let ok = false;
  let httpStatus: number | null = null;
  let summary: unknown = null;
  let errorText: string | null = null;

  try {
    logger.info("tick dispatching", { taskId: cfg.taskId, targetUrl });
    const response = await fetch(targetUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${cfg.targetToken}`,
        "Content-Type": "application/json",
      },
      body: bodyPayload,
    });
    finishedAt = new Date();
    httpStatus = response.status;
    ok = response.ok;

    const rawText = await response.text();
    summary = truncateAndParse(rawText);

    if (!ok) {
      errorText = `HTTP ${response.status}`;
      logger.error("tick target non-2xx", {
        taskId: cfg.taskId,
        status: response.status,
        summary,
      });
    } else {
      logger.info("tick target ok", { taskId: cfg.taskId, summary });
    }
  } catch (err) {
    finishedAt = new Date();
    ok = false;
    errorText = err instanceof Error ? err.message : String(err);
    logger.error("tick fetch failed", { taskId: cfg.taskId, error: errorText });
  }

  const durationMs = finishedAt.getTime() - startedAt.getTime();

  // Best-effort log to ops-engine-x. A failure here does not mask the
  // target result — we still throw below if the target run was not ok.
  await recordRun({
    opexUrl,
    opexToken,
    taskId: cfg.taskId,
    targetUrl,
    startedAt,
    finishedAt,
    durationMs,
    ok,
    httpStatus,
    summary,
    error: errorText,
    triggerRunId: cfg.triggerRunId,
  });

  if (!ok) {
    throw new Error(
      `${cfg.taskId} failed: ${errorText ?? `HTTP ${httpStatus ?? "?"}`}`,
    );
  }
  return summary;
}

function truncateAndParse(raw: string): unknown {
  const text = raw.length > MAX_SUMMARY_BYTES
    ? raw.slice(0, MAX_SUMMARY_BYTES)
    : raw;
  if (text.length === 0) return null;
  try {
    return JSON.parse(text);
  } catch {
    return { raw_text: text, truncated: raw.length > MAX_SUMMARY_BYTES };
  }
}

type RecordRunInput = {
  opexUrl: string;
  opexToken: string;
  taskId: string;
  targetUrl: string;
  startedAt: Date;
  finishedAt: Date;
  durationMs: number;
  ok: boolean;
  httpStatus: number | null;
  summary: unknown;
  error: string | null;
  triggerRunId?: string;
};

async function recordRun(input: RecordRunInput): Promise<void> {
  const logUrl = `${input.opexUrl.replace(/\/$/, "")}/internal/scheduler/runs`;
  try {
    const resp = await fetch(logUrl, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${input.opexToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        task_id: input.taskId,
        target_url: input.targetUrl,
        started_at: input.startedAt.toISOString(),
        finished_at: input.finishedAt.toISOString(),
        duration_ms: input.durationMs,
        ok: input.ok,
        http_status: input.httpStatus,
        summary: input.summary,
        error: input.error,
        trigger_run_id: input.triggerRunId ?? null,
      }),
    });
    if (!resp.ok) {
      logger.warn("scheduler_runs log insert failed", {
        taskId: input.taskId,
        status: resp.status,
        body: (await resp.text()).slice(0, 500),
      });
    }
  } catch (err) {
    logger.warn("scheduler_runs log request errored", {
      taskId: input.taskId,
      error: err instanceof Error ? err.message : String(err),
    });
  }
}
