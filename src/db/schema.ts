import { relations } from "drizzle-orm";
import { boolean, foreignKey, index, jsonb, pgEnum, pgTable, text, timestamp, uuid, } from "drizzle-orm/pg-core";

export const senderEnum = pgEnum('sender', ['user', 'llm'])

export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").default(false).notNull(),
  image: text("image"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .$onUpdate(() => /* @__PURE__ */ new Date())
    .notNull(),
});

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  expiresAt: timestamp("expires_at").notNull(),
  token: text("token").notNull().unique(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .$onUpdate(() => /* @__PURE__ */ new Date())
    .notNull(),
  ipAddress: text("ip_address"),
  userAgent: text("user_agent"),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
});

export const account = pgTable("account", {
  id: text("id").primaryKey(),
  accountId: text("account_id").notNull(),
  providerId: text("provider_id").notNull(),
  userId: text("user_id")
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  accessToken: text("access_token"),
  refreshToken: text("refresh_token"),
  idToken: text("id_token"),
  accessTokenExpiresAt: timestamp("access_token_expires_at"),
  refreshTokenExpiresAt: timestamp("refresh_token_expires_at"),
  scope: text("scope"),
  password: text("password"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .$onUpdate(() => /* @__PURE__ */ new Date())
    .notNull(),
});

export const verification = pgTable("verification", {
  id: text("id").primaryKey(),
  identifier: text("identifier").notNull(),
  value: text("value").notNull(),
  expiresAt: timestamp("expires_at").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at")
    .defaultNow()
    .$onUpdate(() => /* @__PURE__ */ new Date())
    .notNull(),
});

export const chatsTable = pgTable('chats', {
  id: uuid('id').primaryKey().defaultRandom(),
  user_id: text('user_id').notNull().references(() => user.id, { onDelete: "cascade" }),
  parent_id: uuid('parent_id'),
  chat_name: text('chat_name').notNull().unique(),
  is_bookmarked: boolean('is_bookmarked').default(false),
  created_at: timestamp('created_at').notNull().defaultNow(),
  updated_at: timestamp('updated_at').notNull().$onUpdate(() => new Date()),
  deleted_at: timestamp('deleted_at', { mode: "date" })
}, (self) => [
  foreignKey({
    columns: [self.parent_id],
    foreignColumns: [self.id]
  }).onDelete("cascade"),
  index("chats_user_id_idx").on(self.user_id),
  index("chats_parent_id_idx").on(self.parent_id)
])

export const docsTable = pgTable("docs", {
  id: uuid('id').primaryKey().defaultRandom(),
  user_id: text('user_id').notNull().references(() => user.id, { onDelete: "cascade" }),
  chat_id: uuid('chat_id').notNull().references(() => chatsTable.id, { onDelete: "cascade" }),
  parent_id: uuid('parent_id'),
  title: text('title').notNull(),
  original_text: jsonb('original_text'),
  summary_text: text('summary_text'),
  audio_url: text("audio_url"),
  created_at: timestamp('created_at').notNull().defaultNow(),
  updated_at: timestamp('updated_at').notNull().$onUpdate(() => new Date()),
  deleted_at: timestamp('deleted_at', { mode: "date" })
}, (self) => [
  foreignKey({
    columns: [self.parent_id],
    foreignColumns: [self.id],
  }).onDelete("cascade"),
  index("docs_user_id_idx").on(self.user_id),
  index("docs_chat_id_idx").on(self.chat_id)
])

export const messagesTable = pgTable("messages", {
  id: uuid("id").primaryKey().defaultRandom(),
  chat_id: uuid("chat_id").notNull().references(() => chatsTable.id, { onDelete: "cascade" }),
  parent_message_id: uuid("parent_message_id"),
  question_id: uuid('question_id'),
  sender: senderEnum('sender').notNull(),
  metadata: jsonb('metadata'),
  audio_url: text('audio_url'),
  content: text('content').notNull(),
  created_at: timestamp('created_at').notNull().defaultNow(),
  updated_at: timestamp('updated_at').notNull().$onUpdate(() => new Date()),
  deleted_at: timestamp('deleted_at', { mode: "date" })
}, (self) => [
  foreignKey({
    columns: [self.parent_message_id],
    foreignColumns: [self.id],
  }).onDelete("cascade"),
  foreignKey({
    columns: [self.question_id],
    foreignColumns: [self.id],
  }).onDelete("cascade"),
  index("messages_chat_id_idx").on(self.chat_id),
  index("messages_created_at_idx").on(self.created_at),
  index("messages_chat_created_idx").on(self.chat_id, self.created_at),
  index("message_question_id").on(self.question_id)
])


export const userRelations = relations(user, ({ many }) => ({
  chats: many(chatsTable),
  docs: many(docsTable),
  sessions: many(session),
  accounts: many(account)
}))

export const sessionRelations = relations(session, ({ one }) => ({
  user: one(user, {
    fields: [session.userId],
    references: [user.id]
  })
}))

export const accountRelations = relations(account, ({ one }) => ({
  user: one(user, {
    fields: [account.userId],
    references: [user.id]
  })
}))

export const chatsRelations = relations(chatsTable, ({ one, many }) => ({
  user: one(user, {
    fields: [chatsTable.user_id],
    references: [user.id]
  }),
  parent_chat: one(chatsTable, {
    fields: [chatsTable.parent_id],
    references: [chatsTable.id]
  }),
  child_chats: many(chatsTable),
  docs: one(docsTable),
  messages: many(messagesTable)
}))

export const docsRelations = relations(docsTable, ({ one, many }) => ({
  user: one(user, {
    fields: [docsTable.user_id],
    references: [user.id]
  }),
  chat: one(chatsTable, {
    fields: [docsTable.chat_id],
    references: [chatsTable.id]
  }),
  parent_summary: one(docsTable, {
    fields: [docsTable.parent_id],
    references: [docsTable.id]
  }),
  child_summary: many(docsTable)
}))

export const messageRelations = relations(messagesTable, ({ one, many }) => ({
  chat: one(chatsTable, {
    fields: [messagesTable.chat_id],
    references: [chatsTable.id]
  }),
  parent_message: one(messagesTable, {
    fields: [messagesTable.parent_message_id],
    references: [messagesTable.id]
  }),
  child_messages: many(messagesTable)
}))

export type user = typeof user.$inferSelect
export type createUser = typeof user.$inferInsert

export type chat = typeof chatsTable.$inferSelect
export type createChat = typeof chatsTable.$inferInsert

export type doc = typeof docsTable.$inferSelect
export type createDoc = typeof docsTable.$inferInsert

export type message = typeof messagesTable.$inferSelect
export type createMessage = typeof messagesTable.$inferInsert


//metadata type
// {
//   "model": "mistral-7b",
//   "sources": [
//     { "doc_id": "123", "chunk": "React is a JS library..." }
//   ],
//   "tokens_used": 204,
//   "latency_ms": 1345
// }
//original_text type Document<Record<string,any>>