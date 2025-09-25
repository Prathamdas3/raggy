import { database } from "./index.ts";
import { chatsTable as chats, docsTable as docs, messagesTable as messages } from "./schema.ts";
import type { createChat as createChatT, createDoc, createMessage as createMessageT } from "./schema.ts";
import { and, desc, eq, isNull, asc } from "drizzle-orm";

//chats

export const createChat = async (chat: createChatT) => {
    return await database.insert(chats).values(chat).returning()
}

export const getChatsByUserId = async (userId: string) => {
    return await database.select({ id: chats.id, parent_id: chats.parent_id, is_bookmarked: chats.is_bookmarked, chat_name: chats.chat_name }).from(chats).where(eq(chats.user_id, userId)).orderBy(desc(chats.created_at))
}

export const deleteChat = async (chatId: string, userId: string) => {
    return await database.delete(chats).where(and(eq(chats.id, chatId), eq(chats.user_id, userId))).returning()
}

export const bookmarkChat = async (chatId: string, bookmark: boolean, userId: string) => {
    return await database.update(chats).set({ is_bookmarked: bookmark }).where(and(eq(chats.id, chatId), eq(chats.user_id, userId))).returning()
}

export const updateChatName = async (chatId: string, chat_name: string, userId: string) => {
    return await database.update(chats).set({ chat_name: chat_name }).where(and(eq(chats.id, chatId,), eq(chats.user_id, userId))).returning()
}

//docs

export const getDocsByChatId = async (chatId: string) => {
    return (await database.select({ summary_text: docs.summary_text, id: docs.id, chat_id: docs.chat_id }).from(docs).where(eq(docs.chat_id, chatId))).find(({ chat_id }) => chat_id === chatId)
}

export const createDocs = async (doc: createDoc) => {
    return await database.insert(docs).values(doc).returning()
}

export const updateDocs = async (chatId: string, summary: string) => {
    return await database.update(docs).set({ summary_text: summary }).where(eq(docs.chat_id, chatId)).returning()
}

export const addAudioLink = async (docId: string, link: string) => {
    return await database.update(docs).set({ audio_url: link }).where(eq(docs.chat_id, docId)).returning()
}

export const getAudioLinkForSummary = async (chatId: string) => {
    return (await database.select({ id: docs.id, chat_id: docs.chat_id, audio_url: docs.audio_url }).from(docs).where(eq(docs.chat_id, chatId))).find(({ chat_id }) => chat_id === chatId)
}

//messages

export const createMessage = async (message: createMessageT) => {
    return await database.insert(messages).values(message).returning()
}

export const updateMessage = async (newMessage: string, chatId: string, parentId: string | null) => {
    return await database.update(messages).set({ content: newMessage, parent_message_id: messages.id }).where(and(eq(messages.chat_id, chatId), parentId === null ? isNull(messages.parent_message_id) : eq(messages.parent_message_id, parentId)))
}

export const addMessageAudioLink = async (messageId: string, link: string) => {
    return await database.update(messages).set({ audio_url: link }).where(eq(messages.id, messageId))
}

export const getMessagesByParentId = async (chatId: string, parentId: string | null) => {
    return await database.select({ id: messages.id, content: messages.content, parent_id: messages.parent_message_id, question_id: messages.question_id }).from(messages).where(and(eq(messages.chat_id, chatId), parentId === null ? isNull(messages.parent_message_id) : eq(messages.parent_message_id, parentId))).orderBy(asc(messages.created_at))
}

export const getAnswerMessage = async (chatId: string, questionId: string) => {
    return (await database.select({ content: messages.content, id: messages.id, chat_id: messages.chat_id, question_id: messages.question_id }).from(messages).where(and(eq(messages.chat_id, chatId), eq(messages.question_id, questionId)))).find(({ question_id, chat_id }) => question_id === questionId && chat_id === chatId)
}

export const getAnswerById = async (answerId: string) => {
    return (await database.select({ content: messages.content, id: messages.id }).from(messages).where(and(eq(messages.id, answerId), eq(messages.sender, "llm")))).find(({ id }) => id === answerId)
}

export const getAudioLinkForAnswer = async (answerId: string, chatId: string) => {
    return (await database.select({ id: messages.id, audio_url: messages.audio_url }).from(messages).where(and(eq(messages.id, answerId), eq(messages.sender, 'llm'), eq(messages.chat_id, chatId)))).find(({ id }) => id === answerId)
}
