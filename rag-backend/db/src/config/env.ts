import "dotenv/config";
import z from "zod";

const EnvSchema = z.object({
	BETTER_AUTH_SECRET: z.string(),
	DATABASE_URL: z.url(),
	BETTER_AUTH_URL: z.url(),
	QDRANT_URL: z.url(),
	PORT: z
		.string()
		.transform((val) => parseInt(val, 10))
		.refine((val) => !Number.isNaN(val), { message: "PORT must be a number" }),
	LEVEL: z.string(),
});

const parsed = EnvSchema.safeParse(process.env);

if (!parsed.success) {
	const pretty = z.prettifyError(parsed?.error);
	console.log(pretty);
	process.exit(1);
}

export const env = parsed?.data;
