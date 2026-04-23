// oex.auth_me_probe — once a day, ask ops-engine-x to fire this scheduled
// event. ops-engine-x's dispatcher GETs oex-api's `/api/auth/me` and
// records the outcome in scheduler_runs. A green run proves:
//   (1) ops-engine-x can reach oex-api at OEX_API_URL,
//   (2) OEX_AUTH_TOKEN is valid,
//   (3) the service_registry wiring for "oex" is correct.
//
// All routing (target service, target path, HTTP method, bearer token)
// lives in the ops-engine-x scheduled_events registry + service_registry.
// This file is pure Trigger.dev wiring: task id + cron + "fire it."

import { schedules } from "@trigger.dev/sdk/v3";
import { fireScheduledEvent } from "./lib/fire-scheduled-event";

const CRON_DAILY_AT_14_UTC = "0 14 * * *";

export const oexAuthMeProbe = schedules.task({
  id: "oex.auth_me_probe",
  cron: CRON_DAILY_AT_14_UTC,
  maxDuration: 60,
  run: async (_payload, { ctx }) =>
    fireScheduledEvent("oex.auth_me_probe", ctx.run.id),
});
