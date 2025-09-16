import { Hono } from "hono";

export const SummaryRouter = new Hono().get(c => {
    c.status(200)
    return c.json({body:"this is summary route"})
})