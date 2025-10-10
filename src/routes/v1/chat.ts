import { validator } from "hono/validator";
import z from "zod";
import { createRouter } from "../../configs/app.ts";
import {
	bookmarkChat,
	createChat,
	deleteChat,
	getChatsByUserId,
	getMessagesByParentId,
	updateChatName,
} from "../../db/queries.ts";
import { error, success } from "../../utils/response.ts";
import { tryCatch } from "../../utils/tryCatch.ts";

const schema = z.object({
	name: z.string(),
});

const router = createRouter();

router
	.get(async (c) => {
		//This is for getting all the chats for a user
		const user = c.get("user");

		if (!user) {
			return c.json(error("No user found", "Unauthorized"), 401);
		}

		const userId = user.id;

		const { data, error: chatFetchError } = await tryCatch(
			getChatsByUserId(userId),
		);

		if (chatFetchError) {
			return c.json(
				error("Failed to get all the chats", "Internal Sever Error"),
				500,
			);
		}

		return c.json(success(data === null ? [] : data), 200);
	})
	.post(
		validator("json", (value, c) => {
			const parsed = schema.safeParse(value);
			if (!parsed.success) {
				return c.json(error("No chat name found", "Invalid Input"), 400);
			}
			return parsed.data;
		}),
		async (c) => {
			//This is for creating a new chat under the user
			const user = c.get("user");

			if (!user) {
				return c.json(error("No user found", "Unauthorized"), 401);
			}

			const userId = user.id;
			const { name } = c.req.valid("json");

			const { data, error: chatCreateError } = await tryCatch(
				createChat({ user_id: userId, chat_name: name }),
			);

			if (chatCreateError) {
				return c.json(
					error("Failed to create the chat", "Internal Server Error"),
					500,
				);
			}

			if (data.length === 0) {
				return c.json(
					error(
						"Chat name already exists, Please use something else",
						"Invalid Input",
					),
					400,
				);
			}

			return c.json(success(data), 201);
		},
	)
	.patch(
		"/:chatId",
		validator("json", (value, c) => {
			const parsed = schema.safeParse(value);

			if (!parsed.success) {
				return c.json(error("No new name found", "Invalid Input"), 400);
			}

			return parsed.data;
		}),
		async (c) => {
			//This is for updating a existing chat name
			const user = c.get("user");
			const { chatId } = c.req.param();

			if (!user) {
				return c.json(error("No user found", "Unauthorized"), 401);
			}

			if (!chatId.trim()) {
				return c.json(error("No chat found with the id", "Invalid Input"), 400);
			}

			const userId = user.id;
			const { name } = c.req.valid("json");

			const { data: chatNames, error: chatNameError } = await tryCatch(
				updateChatName(chatId, name, userId),
			);

			if (chatNameError) {
				return c.json(
					error(
						"Failed to change the name of the chat",
						"Internal Server Error",
					),
					500,
				);
			}

			if (chatNames.length === 0) {
				return c.json(
					error(`No chat exits with this chatId: ${chatId}`, "Invalid Input"),
					400,
				);
			}

			return c.json(success("Successfully updated the name of the chat"), 200);
		},
	)
	.delete("/:chatId", async (c) => {
		//This is to delete a chat
		const user = c.get("user");
		const { chatId } = c.req.param();

		if (!user) {
			return c.json(error("No user found", "Unauthorized"), 401);
		}

		if (!chatId.trim()) {
			return c.json(error("No chat found with the id", "Invalid Input"), 400);
		}

		const userId = user.id;

		const { data: deleteChatName, error: deleteChatNameError } = await tryCatch(
			deleteChat(chatId, userId),
		);

		if (deleteChatNameError) {
			return c.json(
				error("Failed to delete the chat", "Internal Server Error"),
				500,
			);
		}

		if (deleteChatName.length === 0) {
			return c.json(
				error(`No chat found with this chat_id:${chatId}`, "Invalid Input"),
				400,
			);
		}

		return c.json("Successfully deleted the chat", 200);
	});

router
	.get("/:chatId", async (c) => {
		//This is to get all the messages under a chat
		const logger = c.get("logger");
		const { chatId } = c.req.param();

		if (!chatId.trim()) {
			logger.error("No chat id found to get the messages");
			return c.json(error("No chat Id found", "Invalid Input"), 400);
		}

		const { data, error: getChatsError } = await tryCatch(
			getMessagesByParentId(chatId, null),
		);

		if (getChatsError) {
			logger.error(`Failed to get all the messages for the chat_id:${chatId}`);
			return c.json(error("Failed to fetch all the messages"));
		}

		logger.info(
			`Successfully fetched all the messages for the chat_id:${chatId}`,
		);
		return c.json(success(data), 200);
	})
	.patch("/bookmark/:chatId", async (c) => {
		//This is to bookmark a perticular chat
		const user = c.get("user");
		const { chatId } = c.req.param();
		const { bookmark } = c.req.query();

		if (!user) {
			return c.json(error("No user found", "Unauthorized"), 401);
		}

		if (!chatId.trim()) {
			return c.json(error("No chat found with the id", "Invalid Input"), 400);
		}

		if (!bookmark.trim()) {
			return c.json(error("No bookmark action found", "Invalid Input"), 400);
		}

		const userId = user.id;
		const { data: bookmarks, error: bookMarkChatError } = await tryCatch(
			bookmarkChat(chatId, Boolean(bookmark), userId),
		);

		if (bookMarkChatError) {
			return c.json(
				error("Failed to perform action on bookmark", "Internal Server Error"),
				500,
			);
		}

		if (bookmarks.length === 0) {
			return c.json(
				error(`No chat found with this chat_id: ${chatId}`, "Invalid Input"),
				400,
			);
		}
		const message =
			bookmark === "true"
				? "Successfully Added the bookmark"
				: "Successfully Removed the bookmark";
		return c.json(success(message), 200);
	});

export default router;
