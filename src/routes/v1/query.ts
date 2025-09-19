import { validator } from "hono/validator"
import { createRouter } from "../../configs/app.ts"
import z from "zod"
import { error, success } from "src/utils/response.js"
import { tryCatch } from "src/utils/tryCatch.js"
import { AddToQueryQueue } from "src/queues/querying.js"
import { createMessage } from "src/db/queries.js"

const schema = z.object({
    question: z.string().min(1, "Question can't be empty")
})

const router = createRouter()

router.get(c => {
    c.status(200)
    return c.json({ body: "this is query route" })
}
)
    .post("/:chatId", validator('json', (value, c) => {
        const parsed = schema.safeParse(value)

        if (!parsed.success) {
            return c.json(error("No question found", "Invalid Input"))
        }
        return parsed.data
    }),
        async (c) => {
            const logger = c.get("logger")
            const { question } = c.req.valid('json')
            const { chatId } = c.req.param()
            const user = c.get('user')

            if (!user) {
                logger.error("No user Found")
                return c.json(error("No user found", "Unauthorized"), 401)
            }
            const userId = user.id

            const { error: QueryAddingError } = await tryCatch(AddToQueryQueue({ chatId, userId, question }))

            if (QueryAddingError) {
                logger.error("Failed to add payload to the query queue")

            }

            const { error: QueryDbStoring } = await tryCatch(createMessage({ sender: "user", chat_id: chatId, content: question }))

            if (QueryDbStoring) {
                logger.error("Failed to store the question to db")
                c.json(error("Failed to store the data, Please try again", "Internal Server Error"), 500)
            }

            logger.info("Successfully queried the data and stored the data")
            return c.json(success("Successfully submited the qeustion for answer generation"))
        })


export default router