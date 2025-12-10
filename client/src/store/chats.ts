import type { Chat } from "@/hooks/chats";
import { create } from "zustand";

interface ChatStore {
	chats: Chat[];
	updateChat: (chats: Chat[]) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
	chats: [],
	updateChat: (chats: Chat[]): void =>
		set((): { chats: Chat[] } => ({ chats: chats })),
}));
