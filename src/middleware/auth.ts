import { createMiddleware } from "hono/factory";
import { auth } from "../configs/auth.ts";
import { error } from "../utils/response.ts";

export const authMiddle = createMiddleware(async (c, next) => {
	const session = await auth.api.getSession({ headers: c.req.raw.headers });

	if (!session) {
		return c.json(error("No user found", "Unauthorized"), 401);
	}

	c.set("user", session.user);
	c.set("session", session.session);
	return next();
});
