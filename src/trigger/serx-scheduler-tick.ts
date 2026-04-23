// Scheduled tick that tells serx-api (service-engine-x) to dispatch any
// time-based events that are due (today: meeting preframes).
//
// Trigger.dev stays dumb: fire cron → POST → log. All "what's due / who
// to dispatch to / idempotency" logic lives in serx-api's handler at
// /api/internal/scheduler/dispatch-due-preframes.
//
// Tune the cadence via CRON_EVERY_6_HOURS. Do not inline the cron string
// elsewhere.

import { schedules } from "@trigger.dev/sdk/v3";
import { tickAndLog } from "./lib/tick-and-log";

const CRON_EVERY_6_HOURS = "0 */6 * * *";
const TARGET_PATH = "/api/internal/scheduler/dispatch-due-preframes";

export const serxSchedulerTick = schedules.task({
  id: "serx:scheduler-tick",
  cron: CRON_EVERY_6_HOURS,
  maxDuration: 120,
  run: async (_payload, { ctx }) => {
    return tickAndLog({
      taskId: "serx:scheduler-tick",
      targetBaseUrl: process.env.SERX_API_URL,
      targetPath: TARGET_PATH,
      targetToken: process.env.SERX_AUTH_TOKEN,
      triggerRunId: ctx.run.id,
    });
  },
});
