import { createMiddleware } from "hono/factory";
import pino from 'pino'
import { env } from '../configs/env.ts';
import { getConnInfo } from '@hono/node-server/conninfo'
import { auth } from "../configs/auth.ts";

const customLevels = {
    logs: 35
}

const transports = pino.transport({
    target: 'pino-pretty',
    options: { destination: 1, colorize: true },
})

export const PinoLogger = createMiddleware(async (c, next) => {
    c.env.incoming.id = c.var.requestId;
    const ip = getConnInfo(c).remote.address
    const requestId = c.get('requestId')
    const userId = (await auth.api.getSession({ headers: c.req.raw.headers }))?.user.id || null

    c.set('logger', pino({
        transport: transports,
        customLevels: customLevels,
        level: env.LEVEL || "info",
        timestamp: pino.stdTimeFunctions.isoTime,
        enabled: true,
        formatters: {
            bindings: (bindings) => {
                return {
                    pid: bindings.pid,
                    host: bindings.hostname
                }
            },
            level: (label) => {
                return { level: label.toUpperCase() }
            }
        },
        base: {
            ip: ip,
            requestId: requestId,
            userId:userId
        },
    }))
    await next();
})