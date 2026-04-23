// serx.dispatch_due_preframes — every 6 hours, ask ops-engine-x to fire
// this scheduled event. ops-engine-x's dispatcher POSTs to serx-api's
// `/api/internal/scheduler/dispatch-due-preframes` and records the outcome.
//
// All routing logic (which target path, which service's token) lives in
// the ops-engine-x scheduled_events registry + service_registry.py. This
// file is pure Trigger.dev wiring: task id + cron + "fire it."

import { schedules } from "@trigger.dev/sdk/v3";
import { fireScheduledEvent } from "./lib/fire-scheduled-event";

const CRON_EVERY_6_HOURS = "0 */6 * * *";

export const serxDispatchDuePreframes = schedules.task({
  id: "serx.dispatch_due_preframes",
  cron: CRON_EVERY_6_HOURS,
  maxDuration: 120,
  run: async (_payload, { ctx }) =>
    fireScheduledEvent("serx.dispatch_due_preframes", ctx.run.id),
});
