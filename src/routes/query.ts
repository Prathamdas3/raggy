import { Hono } from "hono";

export const QueryRouter = new Hono().get(c => {
    c.status(200)
    return c.json({body:"this is query route"})
}).post()