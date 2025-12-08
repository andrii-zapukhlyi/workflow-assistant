import { authService } from "./auth"
import type { Chat, Message } from "./auth"

export const chatApi = {
  // Chat operations
  async createChat(title = "New Chat"): Promise<Chat> {
    const data = await authService.apiCall<{ session_id: number; name: string | null }>("/chat/chats", "POST")
    return {
      id: data.session_id.toString(),
      title: data.name || title,
      created_at: new Date().toISOString(), // Backend doesn't return this
      updated_at: new Date().toISOString(),
    }
  },

  async deleteChat(chatId: string): Promise<void> {
    await authService.apiCall(`/chat/chats/${chatId}`, "DELETE")
  },

  async renameChat(chatId: string, title: string): Promise<Chat> {
    const data = await authService.apiCall<{ id: number; name: string }>(
      `/chat/chats/${chatId}/rename`,
      "PUT",
      { new_name: title }
    )
    return {
      id: data.id.toString(),
      title: data.name,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
  },

  async getChats(): Promise<Chat[]> {
    const data = await authService.apiCall<{ id: number; name: string }[]>("/chat/chats", "GET")
    return data.map((s) => ({
      id: s.id.toString(),
      title: s.name,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }))
  },

  async getMessages(chatId: string): Promise<Message[]> {
    const data = await authService.apiCall<{ role: string; content: string; links?: string[]; titles?: string[] }[]>(
      `/chat/chats/${chatId}/messages`,
      "GET"
    )
    return data.map((m, index) => ({
      id: `${chatId}-${index}`,
      chat_id: chatId,
      role: m.role as "user" | "assistant",
      content: m.content,
      created_at: new Date().toISOString(),
      links: m.links,
      titles: m.titles,
    }))
  },

  async sendMessage(chatId: string, message: string): Promise<{ answer: string; links: string[]; titles: string[]; session_name: string }> {
    const data = await authService.apiCall<{
      answer: string
      links: string[]
      titles: string[]
      session_name: string
    }>(`/chat/chats/${chatId}/ask`, "POST", { query: message })
    return data
  },
}