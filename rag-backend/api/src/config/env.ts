import "dotenv/config";
import z from "zod";

const EnvSchema = z.object({
	BETTER_AUTH_SECRET: z.string().optional(),
	BETTER_AUTH_URL: z.url().optional(),
	DB_URL: z.url(),
	RAG_URL: z.url(),
	INPUT_API_URL: z.url()
});

const parsed = EnvSchema.safeParse(process.env);

if (!parsed.success) {
	const pretty = z.prettifyError(parsed?.error);
	console.log(pretty);
	process.exit(1);
}

export const env = parsed?.data;