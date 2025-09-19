import { createMiddleware } from "hono/factory";
import pino from "pino";
import { getConnInfo } from "@hono/node-server/conninfo";
import { auth } from "../configs/auth.ts";

// Optional custom levels
const customLevels = {
    logs: 35,
};

export const PinoLogger = createMiddleware(async (c, next) => {
    const ip = getConnInfo(c).remote.address;
    const requestId = c.get("requestId"); // from hono/request-id
    const session = await auth.api.getSession({ headers: c.req.raw.headers });
    const userId = session?.user.id ?? null;

    const logger = pino({
        customLevels,
        transport: {
            target: 'pino-pretty',
            options: {
                colorize: true
            }
        },
        timestamp: pino.stdTimeFunctions.isoTime,
        enabled: true,
        formatters: {
            bindings: (bindings) => ({
                pid: bindings.pid,
                host: bindings.hostname,
            }),
            level: (label) => ({ level: label.toUpperCase() }),
        },
        base: {
            ip,
            requestId,
            userId,
        },
    });

    c.set("logger", logger);

    await next();
});
