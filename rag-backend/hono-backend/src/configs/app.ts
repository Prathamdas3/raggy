import { Hono } from "hono";
import type pino from "pino";
import type { auth } from "./auth.ts";

export type AuthType = {
	user: typeof auth.$Infer.Session.user | null;
	session: typeof auth.$Infer.Session.session | null;
	logger: pino.Logger<"logs", boolean>;
};

export function createRouter() {
	return new Hono<{ Variables: AuthType }>({ strict: false });
}

export function createApp() {
	const app = createRouter();
	return app;
}
