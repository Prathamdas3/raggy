import { error, success } from "../../utils/response.ts"
import { createRouter } from "../../configs/app.ts"
import { tryCatch } from "src/utils/tryCatch.js"
import { getDocsByChatId } from "src/db/queries.js"

const router = createRouter()

router.get('/:chatId', async c => {
    const logger = c.get('logger')
    const { chatId } = c.req.param()

    if (!chatId.trim()) {
        logger.info("No chat it found in the request")
        return c.json(error("No chat id found", "Invalid Input"), 400)
    }

    const { data: summary, error: getSummaryError } = await tryCatch(getDocsByChatId(chatId))

    if (getSummaryError) {
        logger.error("Failed to get the summary from the db")
        return c.json(error("Failed to get the summary", "Internal server error"), 500)
    }

    const text = summary[0].summary_text || ''

    logger.info("Successfully got the summary data")
    return c.json(success({ summary: text, doc_id: summary[0].id }))
})

export default router