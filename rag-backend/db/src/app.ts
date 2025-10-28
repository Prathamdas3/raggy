import { requestId } from "hono/request-id";
import { createApp } from "./config/app.ts";
import docsRouter from "./routes/v1/docs.ts";
import queryRouter from './routes/v1/query.ts'

const app = createApp()
	.basePath("/api")
	.use(requestId());

app.get("/", (c) => {
	c.status(200);
	return c.json({ body: "db interface is working" });
});

app.route("/v1/docs", docsRouter)
app.route("/v1/query",queryRouter)

export default app;
