import { defineConfig } from 'drizzle-kit';
import { env } from './src/configs/env.ts';

export default defineConfig({
  out: './drizzle',
  schema: './src/db/schema.ts',
  dialect: 'postgresql',
  dbCredentials: {
    url: env.DATABASE_URL!,
  },
  verbose: true,
  strict: true
});
