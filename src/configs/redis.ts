import { Redis } from 'ioredis'
import { env } from './env.js';

export const redis = new Redis({
    host: env.REDIS_HOST!,
    port: env.REDIS_PORT!,
    maxRetriesPerRequest: null
})

redis.on("connect", () => {
    console.log("✅ Connected to Redis!");
});

redis.on("error", (err) => {
    console.error("❌ Redis connection error:", err);
});
