import { swaggerUI } from '@hono/swagger-ui'
import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { csrf } from 'hono/csrf'
import { requestId } from 'hono/request-id'
import { UploadRouter } from './routes/upload.js'

const app = new Hono().basePath("/api")

app.use('/api/*', cors()).use(requestId())

app.get('/ui', swaggerUI({ url: '/doc' }))
app.get("/", c => c.json({ body: "Api is working start your journey" }))

app.route("/upload", UploadRouter)

export default app 
