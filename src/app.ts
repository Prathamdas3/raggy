import { createApp } from "./configs/app.ts";
import { cors } from 'hono/cors'
import { requestId } from 'hono/request-id'
import auth from "./routes/auth.ts";
import summary from "./routes/v1/summary.ts"
import upload from './routes/v1/upload.ts'
import query from './routes/v1/query.ts'
import { swaggerUI } from "@hono/swagger-ui";

const app = createApp()
    .basePath("/api")
    .use('/api/*', cors())
    .use(requestId())

const routes = [auth] as const;

routes.forEach((route) => {
    app.route("/", route)
})

app.route('/v1/summary', summary)
    .route('/v1/query', query)
    .route('/v1/upload', upload)


app.get('/', (c) => {
    c.status(200)
    return c.json({ body: "Api is working start your journey" })
})

app.get('/docs', swaggerUI({ url: '/docs' }))

export type AppType = (typeof routes)[number]

export default app