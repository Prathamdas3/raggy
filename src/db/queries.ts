import { database } from "./index.ts";
import { chatsTable as chats, docsTable as docs, messagesTable as messages } from "./schema.ts";
import type { createChat as createChatT, createDoc, createMessage as createMessageT } from "./schema.ts";
import { and, desc, eq, isNull } from "drizzle-orm";

export const createChat = async (chat: createChatT) => {
    return await database.insert(chats).values(chat).returning()
}

export const getChatsByUserId = async (userId: string) => {
    return await database.select().from(chats).where(eq(chats.user_id, userId)).orderBy(desc(chats.created_at))
}

export const deleteChat = async (chatId: string, userId: string) => {
    return await database.delete(chats).where(and(eq(chats.id, chatId), eq(chats.user_id, userId))).returning()
}

export const bookmarkChat = async (chatId: string, bookmark: boolean, userId: string) => {
    return await database.update(chats).set({ is_bookmarked: bookmark }).where(and(eq(chats.id, chatId), eq(chats.user_id, userId)))
}

export const updateChatName = async (chatId: string, chat_name: string, userId: string) => {
    return await database.update(chats).set({ chat_name: chat_name }).where(and(eq(chats.id, chatId,), eq(chats.user_id, userId)))
}

export const getDocsByChatId = async (chatId: string) => {
    return await database.select().from(docs).where(eq(docs.chat_id, chatId))
}

export const createDocs = async (doc: createDoc) => {
    return await database.insert(docs).values(doc).returning()
}

export const updateDocs = async (docId: string, summary: string) => {
    return await database.update(docs).set({ summary_text: summary }).where(eq(docs.id, docId))
}

export const createMessage = async (message: createMessageT) => {
    return await database.insert(messages).values(message).returning()
}

export const updateMessage = async (newMessage: string, chatId: string, parentId: string | null) => {
    return await database.update(messages).set({ content: newMessage, parent_message_id: messages.id }).where(and(eq(messages.chat_id, chatId), parentId === null ? isNull(messages.parent_message_id) : eq(messages.parent_message_id, parentId)))
}

export const getMessagesByParentId = async (chatId: string, parentId: string | null) => {
    return await database.select().from(messages).where(and(eq(messages.chat_id, chatId), parentId === null ? isNull(messages.parent_message_id) : eq(messages.parent_message_id, parentId)))
}

export const getAnswerMessage = async (chatId: string, questionId: string) => {
    return await database.select().from(messages).where(and(eq(messages.chat_id, chatId), eq(messages.question_id, questionId)))
}
