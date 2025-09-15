import z from 'zod'
// import 'dotenv'

const EnvSchema = z.object({
    DATABASE_URL: z.url(),
    BETTER_AUTH_SECRET: z.string(),
    BETTER_AUTH_URL: z.url(),
    QDRANT_URL: z.url(),
    HUGGINGFACEHUB_API_KEY: z.string()
})

console.log(process.env)
const parsed = EnvSchema.safeParse(process.env!)

if (!parsed.success) {
    const pretty = z.prettifyError(parsed?.error);
    console.log(pretty)
    process.exit(1);
}

export const env = parsed?.data