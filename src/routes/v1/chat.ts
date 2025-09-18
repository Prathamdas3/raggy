import { success, error } from "../../utils/response.ts";
import { createRouter } from "../../configs/app.ts";
import { tryCatch } from "../../utils/tryCatch.ts";
import { bookmarkChat, createChat, deleteChat, getChatsByUserId, updateChatName } from "../../db/queries.ts";
import { validator } from "hono/validator";
import z from "zod";

const schema = z.object({
    name: z.string()
})

const router = createRouter()

router
    .get(async (c) => {
        const user = c.get('user')
        

        if (!user) {
            return c.json(error("No user found", "Unauthorized"), 401)
        }

        const userId = user.id

        const { data, error: chatFetchError } = await tryCatch(getChatsByUserId(userId))

        if (chatFetchError) {
            return c.json(error("Failed to get all the chats", "Internal Sever Error"), 500)
        }

        return c.json(success(data === null ? [] : data), 200)
    }
    )
    .post(
        validator('json', (value, c) => {
            const parsed = schema.safeParse(value)
            if (!parsed.success) {
                return c.json(error("No chat name found", "Invalid Input"), 400)
            }
            return parsed.data
        }),
        async (c) => {
            const user = c.get('user')

            if (!user) {
                return c.json(error("No user found", "Unauthorized"), 401)
            }

            const userId = user.id
            const { name } = c.req.valid('json')

            const { data, error: chatCreateError } = await tryCatch(createChat({ user_id: userId, chat_name: name }))

            if (chatCreateError) {
                return c.json(error("Failed to create the chat", "Internal Server Error"), 500)
            }

            return c.json(success(data), 201)
        }
    )
    .patch("/:chatId",
        validator('json', (value, c) => {
            const parsed = schema.safeParse(value)

            if (!parsed.success) {
                return c.json(error("No new name found", "Invalid Input"), 400)
            }

            return parsed.data
        }),
        async (c) => {
            const user = c.get('user')
            const { chatId } = c.req.param()

            if (!user) {
                return c.json(error("No user found", "Unauthorized"), 401)
            }

            if (!chatId.trim()) {
                return c.json(error("No chat found with the id", "Invalid Input"), 400)
            }

            const userId = user.id
            const { name } = c.req.valid('json')

            const { error: chatNameError } = await tryCatch(updateChatName(chatId, name, userId))

            if (chatNameError) {
                return c.json(error("Failed to change the name of the chat", "Internal Server Error"), 500)
            }

            return c.json(success("Successfully updated the name of the chat"), 200)
        }
    )
    .delete("/:chatId", async (c) => {
        const user = c.get('user')
        const { chatId } = c.req.param()

        if (!user) {
            return c.json(error("No user found", "Unauthorized"), 401)
        }

        if (!chatId.trim()) {
            return c.json(error("No chat found with the id", "Invalid Input"), 400)
        }

        const userId = user.id

        const { error: deleteChatName } = await tryCatch(deleteChat(chatId, userId))

        if (deleteChatName) {
            return c.json(error("Failed to delete the chat", "Internal Server Error"), 500)
        }

        return c.json("Successfully deleted the chat", 200)
    }
    )

router
    .patch('/:chatId',
        async (c) => {
            const user = c.get('user')
            const { chatId } = c.req.param()
            const { bookmark } = c.req.query()

            if (!user) {
                return c.json(error("No user found", "Unauthorized"), 401)
            }

            if (!chatId.trim()) {
                return c.json(error("No chat found with the id", "Invalid Input"), 400)
            }

            if (!bookmark.trim()) {
                return c.json(error("No bookmark action found", "Invalid Input"), 400)
            }

            const userId = user.id
            const { error: bookMarkChatError } = await tryCatch(bookmarkChat(chatId, Boolean(bookmark), userId))

            if (bookMarkChatError) {
                return c.json(error("Failed to perform action on bookmark", "Internal Server Error"), 500)
            }

            const message = bookmark === "true" ? "Successfully Added the bookmark" : "Successfully Removed the bookmark"
            return c.json(success(message), 200)
        }
    )

export default router