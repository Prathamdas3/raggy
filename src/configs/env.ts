import 'dotenv/config'
import z from 'zod'

const EnvSchema = z.object({
  BETTER_AUTH_SECRET: z.string(),
  MISTRALAI_API_KEY: z.string(),
  DATABASE_URL: z.url(),
  BETTER_AUTH_URL: z.url(),
  QDRANT_URL: z.url(),
  REDIS_HOST: z.string(),
  REDIS_PORT: z
    .string()
    .transform((val) => parseInt(val, 10))
    .refine((val) => !isNaN(val), { message: "REDIS_PORT must be a number" }),
  PORT: z
    .string()
    .transform((val) => parseInt(val, 10))
    .refine((val) => !isNaN(val), { message: "PORT must be a number" }),
  LEVEL: z.string(),
  MAILTRAP_HOST: z.string(),
  MAILTRAP_PORT: z.string()
    .transform((val) => parseInt(val, 10))
    .refine((val) => !isNaN(val), { message: "PORT must be a number" }),
  MAILTRAP_AUTH_USER: z.email(),
  MAILTRAP_AUTH_PASS: z.string(),
  SUMMARY_INSTRUCTION: z.string(),
  QUERY_INSTRUCTION: z.string()
});

const parsed = EnvSchema.safeParse(process.env!)

if (!parsed.success) {
  const pretty = z.prettifyError(parsed?.error);
  console.log(pretty)
  process.exit(1);
}

export const env = parsed?.data