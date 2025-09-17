import { createRouter } from "../../configs/app.ts"

const router = createRouter()

router.get(c => {
    c.status(200)
    return c.json({ body: "this is query route" })
}).post()


export default router