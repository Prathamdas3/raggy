import { error, success } from "../../utils/response.ts"
import { createRouter } from "../../configs/app.ts"
import { tryCatch } from "src/utils/tryCatch.js"
import {  getDocsByChatId } from "src/db/queries.js"

const router = createRouter()

router.get('/:chatId', async c => {
    //This is for getting the summary of an uploaded docs in the chat
    const logger = c.get('logger')
    const { chatId } = c.req.param()

    const { data: summary, error: getSummaryError } = await tryCatch(getDocsByChatId(chatId))

    if (getSummaryError) {
        logger.error("Failed to get the summary from the db")
        return c.json(error("Failed to get the summary", "Internal server error"), 500)
    }

    const text = summary?.summary_text || ''

    // logger.info("Successfully got the summary data")
    return c.json(success({ summary: text, doc_id: summary?.id }))
})

export default router