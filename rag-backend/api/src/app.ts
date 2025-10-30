import { requestId } from "hono/request-id";
import { createApp } from "./config/app.ts";

const app = createApp()
    .basePath("/api")
    .use(requestId())

app.get("/", (c) => {
    return c.json({ body: "client server working" }, 200)
})

export default app