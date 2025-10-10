import { serve } from "@hono/node-server";
import { config } from "dotenv";
import app from "./app.ts";
import { env } from "./configs/env.ts";

config();

serve(
	{
		fetch: app.fetch,
		hostname: "0.0.0.0",
		port: env.PORT,
	},
	(info) => {
		console.log(`Server is running on http://localhost:${info.port}`);
	},
);
