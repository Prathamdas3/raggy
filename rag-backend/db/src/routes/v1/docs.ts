import { createRouter } from "../../config/app.ts"
import z from 'zod'
import { error, success } from "src/config/response.js"
import { validator } from "hono/validator"
import { createDocs } from "src/db/queries.js"
import { tryCatch } from "src/config/trycatch.js"

const schema = z.object({
    chat_id: z.string().min(1, "chat_id must be more than 1 character"),
    user_id: z.string().min(1, "user_id must be more than 1 character"),
    original_text: z.string().min(1, "original_text must be more than 1 character"),
    title: z.string().min(1, "title must be more than 1 character")
})

const router = createRouter()

router.post(validator("json", (value, c) => {
    const { data, success, error: errorDetails } = schema.safeParse(value)

    if (!success) {
        return c.json(error(errorDetails.message, "Invalid Input"), 400)
    }

    return data
}), async (c) => {
    const { chat_id, user_id, original_text, title } = c.req.valid("json")

    const { error: dbDocStoreError } = await tryCatch(createDocs({
        chat_id,
        user_id,
        original_text,
        title
    }))

    if (dbDocStoreError) {
        return c.json(error("Failed to store document", "Database Error"), 500)
    }

    return c.json(success("Stored the data successfully", "Document stored successfully", "Success"), 201)
})

router.patch("/:doc_id")

export default router;