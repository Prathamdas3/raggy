import { serve } from '@hono/node-server'
import {config} from 'dotenv'
import app from './app.ts'

config()

serve({
  fetch: app.fetch,
  port: 8000
}, (info) => {
  console.log(`Server is running on http://localhost:${info.port}`)
})
