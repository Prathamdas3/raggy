import z from 'zod'

const EnvSchema = z.object({
    DATABASE_URL: z.url(),
    BETTER_AUTH_SECRET: z.string(),
    BETTER_AUTH_URL: z.url(),

})

const parsed = EnvSchema.safeParse(process.env!)

if (!parsed.success) {
    const pretty = z.prettifyError(parsed?.error);
    console.log(pretty)
    process.exit(1);
}

export const env = parsed?.data