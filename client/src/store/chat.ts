import { create } from 'zustand'

interface ChatContent {
  id: string
  content: string | File | null
}

interface ChatStore {
  contents: ChatContent[]
  setContent: (data: ChatContent) => void
  getContent: (id: string) => ChatContent | undefined
}

export const useChatCreate = create<ChatStore>((set, get) => ({
  contents: [],

  setContent: (data) =>
    set((state) => {
      const exists = state.contents.find((c) => c.id === data.id)
      if (exists) {
        // update if id already exists
        return {
          contents: state.contents.map((c) => (c.id === data.id ? data : c)),
        }
      }
      return { contents: [...state.contents, data] }
    }),

  getContent: (id) => get().contents.find((c) => c.id === id),
}))