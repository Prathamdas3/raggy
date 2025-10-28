import { createRouter } from "../../config/app.ts";
import z from 'zod'
import { error, success } from 'src/config/response.js'
import { tryCatch } from "src/config/trycatch.js";
import { validator } from "hono/validator";
import { addMessageAudioLink, createMessage, getAnswerMessage, getAudioLinkForAnswer } from 'src/db/queries.js'

const querySchema = z.object({
    chat_id: z.string().min(1, "chat_id must be more than 1 character"),
    content: z.string().min(1, "question must be more than 1 character")
})

const audioSchema = z.object({
    chat_id: z.string().min(1, "chat_id must be more than 1 character"),
    link: z.url().min(10, "Link should be more than 10 characters long"),

})

const router = createRouter()

router
    .post(
        validator("json", (value, c) => {
            const { data, success, error: errorDetails } = querySchema.safeParse(value)
            if (!success) {
                const prittyError = z.prettifyError(errorDetails)
                return c.json(error(prittyError, "Invalid Input"), 400)
            }
            return data
        }), async (c) => {
            // creating the question
            const { chat_id, content } = c.req.valid("json")

            const { error: dbQuestionStore, data } = await tryCatch(createMessage({
                chat_id,
                sender: "user",
                content
            }))

            if (dbQuestionStore) {
                return c.json(error(`Failed to store question, ${dbQuestionStore.message}`, "Database Error"), 500)
            }

            return c.json(success({ question_id: data[0].id }, "Question stored successfully", "Success"), 201)
        }
    )
    .post("/:question_id",
        validator("json", (value, c) => {
            const { data, success, error: errorDetails } = querySchema.safeParse(value)
            if (!success) {
                const prittyError = z.prettifyError(errorDetails)
                return c.json(error(prittyError, "Invalid Input"), 400)
            }
            return data
        }), async (c) => {
            // creating the answer
            const { question_id } = c.req.param()
            if (!question_id.trim()) {
                return c.json(error("No question id found", "Invalid Input"), 400)
            }
            const { chat_id, content } = c.req.valid("json")
            const { error: dbQuestionStore, data } = await tryCatch(createMessage({
                chat_id,
                sender: "llm",
                content
            }))
            if (dbQuestionStore) {
                return c.json(error(`Failed to store question, ${dbQuestionStore.message}`, "Database Error"), 500)
            }

            return c.json(success(`Successfully stored the answer for the question id:${data[0].id}`, "Successfully stored the answer", "Success"), 201)
        }
    )
    .patch("/:question_id",
        validator("json", (value, c) => {
            const { data, success, error: errorDetails } = audioSchema.safeParse(value)
            if (!success) {
                const prittyError = z.prettifyError(errorDetails)
                return c.json(error(prittyError, "Invalid Input"), 400)
            }
            return data
        }), async (c) => {
            // updating the audio link for the answer 
            const { question_id } = c.req.param()
            if (!question_id.trim()) {
                return c.json(error("No question id found", "Invalid Input"))
            }
            const { chat_id, link } = c.req.valid("json")
            const { error: dbUploadError, data } = await tryCatch(addMessageAudioLink({ question_id, chat_id, link }))

            if (dbUploadError) {
                return c.json(error(`Failed to update the audio link for the answer of question id:${question_id}`, "Database Error"), 500)
            }
            return c.json(success({ question_id: data[0].question_id, chat_id: data[0].chat_id, link: data[0].audio_url }, "Successfully added the audio url", "Success"), 200)
        }
    )
    .get("/:chat_id/:question_id", async (c) => {
        // get the answer of the question
        const { question_id, chat_id } = c.req.param()
        if (!question_id.trim() || !chat_id.trim()) {
            return c.json(error("No question id or chat id found", "Invalid Input"), 400)
        }
        const { error: dbGetError, data } = await tryCatch(getAnswerMessage(chat_id, question_id))
        if (dbGetError) {
            return c.json(error(`Failed to get answer content ${dbGetError.message}`, "Database Error"), 500)
        }
        return c.json(success(data, "Successfully fetched the answer", "Success"), 200)
    }
    )
    .get("/:chat_id/:question_id", async (c) => {
        const { question_id, chat_id } = c.req.param()
        if (!question_id.trim() || !chat_id.trim()) {
            return c.json(error("No question id or chat id", "Invalid Input"), 400)
        }
        const { error: dbGetAudioUrlError, data } = await tryCatch(getAudioLinkForAnswer({ question_id, chatId: chat_id }))
        if (dbGetAudioUrlError) {
            return c.json(error(`Failed to get the audio url for the question id:${question_id}`, "Database Error"), 500)
        }
        return c.json(success(data, "Successfully fetched the audio url", "Success"), 200)
    })

export default router