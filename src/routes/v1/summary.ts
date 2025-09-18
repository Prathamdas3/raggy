import { error, success } from "../../utils/response.ts"
import { createRouter } from "../../configs/app.ts"
import { tryCatch } from "src/utils/tryCatch.js"
import { getDocsByChatId } from "src/db/queries.js"
import {streamText} from 'hono/streaming'

const router = createRouter()

router.get('/:chatId', async c => {
    const { chatId } = c.req.param()
    if (!chatId.trim()) {
        return c.json(error("No chat id found", "Invalid Input"), 400)
    }

    const { data: summary, error: getSummaryError } = await tryCatch(getDocsByChatId(chatId))

    if (getSummaryError) {
        return c.json(error("Failed to get the summary", "Internal server error"), 500)
    }

    return streamText(c,async(stream)=>{})
})

export default router