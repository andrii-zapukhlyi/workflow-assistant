"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { ChatMessages } from "@/components/chat-messages"
import { ChatInput } from "@/components/chat-input"
import { ChatHeader } from "@/components/chat-header"
import { useAuth } from "@/hooks/use-auth"
import { chatApi } from "@/lib/api"
import type { Message } from "@/lib/auth"

import { useRef } from "react"
import type { SidebarRef } from "@/components/sidebar"

export function ChatContainer() {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null)
  const [currentChatTitle, setCurrentChatTitle] = useState("New Chat")
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false) // For fetching history
  const [isGenerating, setIsGenerating] = useState(false) // For generating new answer
  const sidebarRef = useRef<SidebarRef>(null)
  const isCreatingChatRef = useRef(false)
  const { logout } = useAuth()

  useEffect(() => {
    if (currentChatId) {
      if (isCreatingChatRef.current) {
        isCreatingChatRef.current = false
        setIsLoading(false)
      } else {
        loadMessages(currentChatId)
      }
    } else {
      setMessages([])
      setIsLoading(false)
      setIsGenerating(false)
      setCurrentChatTitle("New Chat")
    }
  }, [currentChatId])

  const loadMessages = async (chatId: string) => {
    try {
      setIsLoading(true)
      const data = await chatApi.getMessages(chatId)
      setMessages(data)
    } catch (error) {
      console.error("Failed to load messages:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleChatSelect = (chatId: string) => {
    setCurrentChatId(chatId)
    // The title will be updated by the sidebar selection or api fetch if we stored it
  }

  const handleNewChat = () => {
    setCurrentChatId(null)
  }

  const handleSendMessage = async (content: string) => {
    // Optimistically add user message
    const tempId = Date.now().toString()
    const userMessage: Message = {
      id: tempId,
      chat_id: currentChatId || "temp",
      role: "user",
      content: content,
      created_at: new Date().toISOString()
    }
    setMessages(prev => [...prev, userMessage])
    setIsGenerating(true)

    try {
      let activeChatId = currentChatId

      // If no active chat, create one first
      if (!activeChatId) {
        const newChat = await chatApi.createChat(content.slice(0, 30) + "...")
        activeChatId = newChat.id
        isCreatingChatRef.current = true
        setCurrentChatId(activeChatId)
      }

      const response = await chatApi.sendMessage(activeChatId, content)

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        chat_id: activeChatId,
        role: "assistant",
        content: response.answer,
        created_at: new Date().toISOString(),
        links: response.links && response.links.length > 0 ? response.links : undefined,
        titles: response.titles && response.titles.length > 0 ? response.titles : undefined
      }

      setMessages(prev => [...prev, assistantMessage])

      // Update chat title if provided
      if (response.session_name) {
        setCurrentChatTitle(response.session_name)
      }

      // Refresh sidebar to update chat list order (backend sorts by last activity)
      sidebarRef.current?.refreshChats()

    } catch (error) {
      console.error("Failed to send message:", error)
      // Remove optimistic message on permanent failure
      setMessages(prev => prev.filter(m => m.id !== tempId))
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <Sidebar
        ref={sidebarRef}
        currentChatId={currentChatId || undefined}
        onChatSelect={handleChatSelect}
        onNewChat={handleNewChat}
        isGenerating={isGenerating}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-h-0 md:ml-0 relative overflow-hidden">
        {/* Chat Header with Account Info */}
        <ChatHeader currentChatTitle={currentChatTitle} onLogout={logout} />

        {currentChatId ? (
          <>
            <ChatMessages
              chatId={currentChatId}
              messages={messages}
              isLoading={isLoading}
              isGenerating={isGenerating}
            />
            <ChatInput
              chatId={currentChatId}
              onMessageSent={handleSendMessage}
            />
          </>
        ) : (
          <div className="flex-1 flex flex-col">
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground p-4">
              <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
                How can I help you today?
              </h2>
            </div>
            <ChatInput
              chatId="new"
              onMessageSent={handleSendMessage}
            />
          </div>
        )}
      </div>
    </div>
  )
}
