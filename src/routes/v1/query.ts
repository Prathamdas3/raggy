import { validator } from "hono/validator"
import { createRouter } from "../../configs/app.ts"
import z from "zod"
import { error, success } from "src/utils/response.js"
import { tryCatch } from "src/utils/tryCatch.js"
import { AddToQueryQueue } from "src/queues/querying.js"
import { createMessage, getAnswerMessage } from "src/db/queries.js"

const schema = z.object({
    question: z.string().min(1, "Question can't be empty")
})

const router = createRouter()

router
    .post("/:chatId", validator('json', (value, c) => {
        const parsed = schema.safeParse(value)

        if (!parsed.success) {
            return c.json(error("No question found", "Invalid Input"))
        }
        return parsed.data
    }),
        async (c) => {
            // this is to get the answer of a question
            const logger = c.get("logger")
            const { question } = c.req.valid('json')
            const { chatId } = c.req.param()
            const user = c.get('user')

            if (!user) {
                logger.error("No user Found")
                return c.json(error("No user found", "Unauthorized"), 401)
            }
            const userId = user.id

            const { data: details, error: QueryDbStoring } = await tryCatch(createMessage({ sender: "user", chat_id: chatId, content: question }))

            if (QueryDbStoring) {
                logger.error("Failed to store the question to db")
                return c.json(error("Failed to store the data, Please try again", "Internal Server Error"), 500)
            }

            const { error: QueryAddingError } = await tryCatch(AddToQueryQueue({ chatId, userId, question, questionId: details[0].id }))

            if (QueryAddingError) {
                logger.error("Failed to add payload to the query queue")

            }

            logger.info("Successfully queried the data and stored the data")
            return c.json(success({ message: "Successfully submited the qeustion for answer generation", question_id: details[0].id }))
        }
    )
    .get('/:chat_id/:question_id', async (c) => {
        //This is to get a perticular answer for a particular question
        const logger = c.get("logger")
        const { question_id, chat_id } = c.req.param()
        if (!question_id.trim() || !chat_id.trim()) {
            logger.error("No chat_id or question_id found")
            return c.json(error("No question id or chat id found", "Invalid Input"), 400)
        }

        const { data, error: getAnswerError } = await tryCatch(getAnswerMessage(chat_id, question_id))

        if (getAnswerError) {
            logger.error(`Failed to fetch the answer for the chat_id:${chat_id} and question_id:${question_id}`)
            return c.json(error("Failed to fetch the answer", "Internal Server Error"), 500)
        }

        logger.info("Successfully fetched the answer")
        return c.json(success({ content: data?.content, answer_id: data?.id }), 200)
    })

export default router