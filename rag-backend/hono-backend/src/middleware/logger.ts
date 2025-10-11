import { getConnInfo } from "@hono/node-server/conninfo";
import { createMiddleware } from "hono/factory";
import { createLogger } from "src/configs/pino.js";
import { auth } from "../configs/auth.ts";

export const PinoLogger = createMiddleware(async (c, next) => {
	const ip = getConnInfo(c).remote.address;
	const requestId = c.get("requestId"); // from hono/request-id
	const session = await auth.api.getSession({ headers: c.req.raw.headers });
	const userId = session?.user.id ?? null;

	const logger = createLogger({
		ip,
		requestId,
		userId,
	});

	c.set("logger", logger);

	await next();
});
