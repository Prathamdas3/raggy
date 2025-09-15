import { serve } from '@hono/node-server'
import { swaggerUI } from '@hono/swagger-ui'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
// import { csrf } from 'hono/csrf'
import { requestId } from 'hono/request-id'
import { UploadRouter } from './routes/upload.js'
import { QueryRouter } from './routes/query.js'
import { SummaryRouter } from './routes/summary.js'
import { env } from './configs/env.js'

const app = new Hono().basePath("/api")

app
  .use('/api/*', cors())
  .use(requestId())

app.get("/", c => c.json({ body: "Api is working start your journey" }))
app.get('/ui', swaggerUI({ url: '/doc' }))

app
  .route("/upload", UploadRouter)
  .route('/query', QueryRouter)
  .route('/summary', SummaryRouter)


serve({
  fetch: app.fetch,
  port: env.PORT
}, (info) => {
  console.log(`Server is running on http://localhost:${info.port}`)
})
