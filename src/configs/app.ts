import { Hono } from "hono";
import type { AuthType } from "./auth.ts";

export function createRouter() {
    return new Hono<{ Variables: AuthType }>({ strict: false })
}

export function createApp() {
    const app = createRouter()
    return app
}