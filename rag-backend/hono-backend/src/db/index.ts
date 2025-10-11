import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import { env } from "../configs/env.js";
import * as schema from "./schema.js";

const pool = new Pool({
	connectionString: env.DATABASE_URL,
});
const database = drizzle(pool, {
	schema,
	logger: true,
});

export { database, pool };
