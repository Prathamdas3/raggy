import { serve } from '@hono/node-server'
import { swaggerUI } from '@hono/swagger-ui'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { requestId } from 'hono/request-id'
import { UploadRouter } from './routes/v1/upload.js'
import { QueryRouter } from './routes/v1/query.js'
import { SummaryRouter } from './routes/v1/summary.js'
import { env } from './configs/env.js'
import { auth } from './configs/auth.ts'
// import { csrf } from 'hono/csrf'

const app = new Hono().basePath("/api")

app
  .use('/api/*', cors())
  .use(requestId())

app.on(["POST", "GET"], "/auth/*", (c) => auth.handler(c.req.raw));
app.get("/", c => c.json({ body: "Api is working start your journey" }))
app.get('/ui', swaggerUI({ url: '/doc' }))

app
  .route("/v1/upload", UploadRouter)
  .route('/v1/query', QueryRouter)
  .route('/v1/summary', SummaryRouter)


serve({
  fetch: app.fetch,
  port: env.PORT
}, (info) => {
  console.log(`Server is running on http://localhost:${info.port}`)
})
