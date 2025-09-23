import { createRouter } from "src/configs/app.js";
import { getAudioLinkForAnswer, getAudioLinkForSummary } from "src/db/queries.js";
import { error, success } from "src/utils/response.js";
import { tryCatch } from "src/utils/tryCatch.js";


const router = createRouter()

router.get("/:chatId", async (c) => {
    const logger = c.get("logger")
    const { chatId } = c.req.param()

    const { data, error: summayAudioLinkError } = await tryCatch(getAudioLinkForSummary(chatId))

    if (summayAudioLinkError) {
        logger.error(`Failed to fetch the audio link for the summary chat_id:${chatId}`)
        return c.json(error("Failed to fetch the audio link for the summary", "Internal Server Error"), 500)
    }

    logger.info("Successfully returned the audio link for the summay")
    return c.json(success({ audio_url: data?.audio_url, id: data?.id }), 200)
}).get("/:chatId/:answerId", async (c) => {
    const logger = c.get("logger")
    const { chatId, answerId } = c.req.param()

    const { data, error: answerAudioLinkError } = await tryCatch(getAudioLinkForAnswer(answerId, chatId))

    if (answerAudioLinkError) {
        logger.error(`Failed to get the audio link for the answer with id:${answerId} and chat_id:${chatId}`)
        return c.json(error("Failed to fetch the audio link for the answer", "Internal Server Error"), 500)
    }

    logger.info("Successfully returned the audio link for the answer")
    return c.json(success({ audio_url: data?.audio_url, id: data?.id }), 200)
})

export default router