import { createRouter } from "../configs/app.ts";
import { auth } from "../configs/auth.ts";

const router = createRouter();

router.on(["POST", "GET"], "/auth/*", (c) => {
	return auth.handler(c.req.raw);
});

export default router;
