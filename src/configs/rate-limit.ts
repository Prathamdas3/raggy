import { rateLimiter } from "hono-rate-limiter";

export const rateLimitRag = rateLimiter({
	windowMs: 1 * 60 * 1000, // 15 minutes
	limit: 100, // Limit each IP to 100 requests per `window` (here, per 15 minutes).
	standardHeaders: "draft-6",
	keyGenerator: (c) => c.req.header("cf-connecting-ip") ?? "",
	// store: new RedisStore({ client: redis }) as unknown as Store
});
