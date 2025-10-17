import { requestId } from "hono/request-id";
import { createApp } from "./config/app.ts";

const app = createApp().basePath("/api/db").use(requestId());

app.get("/check", (c) => {
	c.status(200);
	return c.json({ body: "db interface is working" });
});

export default app;
