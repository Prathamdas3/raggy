import { createRouter } from "../../config/app.ts"
import z from 'zod'
import { error, success } from "src/config/response.js"
import { validator } from "hono/validator"
import { addAudioLink, createDocs, getAudioLinkForSummary, getDocsByChatIdForOriginalText, getDocsByChatIdForSummary, updateDocs } from "src/db/queries.js"
import { tryCatch } from "src/config/trycatch.js"

const schema = z.object({
    chat_id: z.string().min(1, "chat_id must be more than 1 character"),
    user_id: z.string().min(1, "user_id must be more than 1 character"),
    original_text: z.array(z.object({
        content: z.string().min(10, "content must be more than 10 character"),
        metadata: z.object({
            user_id: z.string().min(1, "user_id in metadata must be more than 1 character"),
            chat_id: z.string().min(1, "chat_id in metadata must be more than 1 character"),
            chunk_index: z.number().nonnegative()
        })
    })),
})

const schemaUpdate = z.object({
    chat_id: z.string().min(1, "chat_id must be more than 1 character"),
    summary_text: z.string().min(10, "summary_text must be more than 10 character").optional(),
    audio_url: z.url("audio_url must be a valid URL").optional(),
})

const router = createRouter()

router
    .post(
        validator("json", (value, c) => {
            const { data, success, error: errorDetails } = schema.safeParse(value)
            if (!success) {
                const prittyError = z.prettifyError(errorDetails)
                return c.json(error(prittyError, "Invalid Input"), 400)
            }

            return data
        }), async (c) => {
            const { chat_id, user_id, original_text } = c.req.valid("json")

            const { error: dbDocStoreError } = await tryCatch(createDocs({
                chat_id,
                user_id,
                original_text,
            }))

            if (dbDocStoreError) {
                return c.json(error("Failed to store document", "Database Error"), 500)
            }

            return c.json(success("Stored the data successfully", "Document stored successfully", "Success"), 201)
        })
    .patch(
        validator("json", (value, c) => {
            const { data, success, error: errorDetails } = schemaUpdate.safeParse(value)

            if (!success) {
                return c.json(error(errorDetails.message, "Invalid Input"), 400)
            }
            return data
        }), async (c) => {
            const { chat_id, summary_text, audio_url } = c.req.valid("json")

            if (summary_text) {
                const { error: dbDocSummaryUpdateError } = await tryCatch(updateDocs(chat_id, summary_text))
                if (dbDocSummaryUpdateError) {
                    return c.json(error("Failed to update document summary", "Database Error"), 500)
                }
                return c.json(success("Updated the document summary successfully", "Document summary updated successfully", "Success"), 200)
            }

            if (audio_url) {
                const { error: dbDocAudioUpdateError } = await tryCatch(addAudioLink(chat_id, audio_url))
                if (dbDocAudioUpdateError) {
                    return c.json(error("Failed to update document audio link", "Database Error"), 500)
                }
                return c.json(success("Updated the document audio link successfully", "Document audio link updated successfully", "Success"), 200)
            }

            return c.json(error("No valid fields to update", "Invalid Input"), 400)
        })


router.
    get("/:chatId/original-text", async (c) => {
        const { chatId } = c.req.param();
        const { data: doc, error: dbDocFetchError } = await tryCatch(getDocsByChatIdForOriginalText(chatId));
        if (dbDocFetchError) {
            return c.json(error("Failed to fetch document", "Database Error"), 500);
        }
        return c.json(success(doc, "Fetched the document successfully", "Success"), 200);
    })
    .get("/:chatId/summary-text", async (c) => {
        const { chatId } = c.req.param();
        const { data, error: dbDocFetchError } = await tryCatch(getDocsByChatIdForSummary(chatId))
        if (dbDocFetchError) {
            return c.json(error("Failed to fetch document summary", "Database Error"), 500);
        }
        return c.json(success(data, "Fetched the document summary successfully", "Success"), 200);
    })
    .get("/:chatId/audio-url", async (c) => {
        const { chatId } = c.req.param();
        const { data, error: dbDocFetchError } = await tryCatch(getAudioLinkForSummary(chatId))
        if (dbDocFetchError) {
            return c.json(error("Failed to fetch document audio URL", "Database Error"), 500);
        }
        return c.json(success(data, "Fetched the document audio URL successfully", "Success"), 200);
    })

export default router;