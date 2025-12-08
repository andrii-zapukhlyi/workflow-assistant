"use client"

import React from "react"

import { useState, useEffect, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Plus, LogOut, Menu, X, Trash2, Edit2, Check, XIcon } from "lucide-react"
import { useAuth } from "@/hooks/use-auth"
import { chatApi } from "@/lib/api"
import type { Chat } from "@/lib/auth"
import { Input } from "@/components/ui/input"

interface SidebarProps {
  currentChatId?: string
  onChatSelect?: (chatId: string) => void
  onNewChat?: () => void
  isGenerating?: boolean
}

export interface SidebarRef {
  refreshChats: () => void
  updateChatTitle: (chatId: string, newTitle: string) => void
}

export const Sidebar = React.forwardRef<SidebarRef, SidebarProps>(({ currentChatId, onChatSelect, onNewChat, isGenerating }, ref) => {
  const [chats, setChats] = useState<Chat[]>([])
  const [loading, setLoading] = useState(true)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingTitle, setEditingTitle] = useState("")
  const { logout } = useAuth()

  useEffect(() => {
    loadChats()
  }, [])

  React.useImperativeHandle(ref, () => ({
    refreshChats: () => loadChats(true),
    updateChatTitle: (chatId: string, newTitle: string) => {
      setChats(prev => prev.map(chat => chat.id === chatId ? { ...chat, title: newTitle } : chat))
    }
  }))

  const loadChats = async (isRefresh = false) => {
    try {
      if (!isRefresh) setLoading(true)
      const data = await chatApi.getChats()
      setChats(data || [])
    } catch (error) {
      console.error("Failed to load chats:", error)
    } finally {
      if (!isRefresh) setLoading(false)
    }
  }

  const handleNewChat = () => {
    onNewChat?.()
    setMobileOpen(false)
  }

  const handleDeleteChat = async (e: React.MouseEvent, chatId: string) => {
    e.stopPropagation()
    if (!window.confirm("Are you sure you want to delete this chat?")) return

    try {
      await chatApi.deleteChat(chatId)
      setChats((prev) => prev.filter((chat) => chat.id !== chatId))
      if (currentChatId === chatId) {
        onChatSelect?.(chats[0]?.id || "")
      }
    } catch (error) {
      console.error("Failed to delete chat:", error)
    }
  }

  const handleRenameChat = async (chatId: string) => {
    if (!editingTitle.trim()) {
      setEditingId(null)
      return
    }

    try {
      const updatedChat = await chatApi.renameChat(chatId, editingTitle)
      setChats((prev) => prev.map((chat) => (chat.id === chatId ? updatedChat : chat)))
      setEditingId(null)
    } catch (error) {
      console.error("Failed to rename chat:", error)
    }
  }

  const startEditingChat = (chat: Chat) => {
    setEditingId(chat.id)
    setEditingTitle(chat.title || "") // Ensure fallback
  }

  const handleChatClick = useCallback((chatId: string) => {
    if (isGenerating) return
    onChatSelect?.(chatId)
    setMobileOpen(false)
  }, [isGenerating, onChatSelect])

  // Chat list content - extracted to avoid duplication
  const chatListContent = (
    <div className="space-y-2 p-4">
      {loading ? (
        <div className="text-xs text-sidebar-foreground/50 text-center py-8">Loading chats...</div>
      ) : !chats?.length ? (
        <div className="text-xs text-sidebar-foreground/50 text-center py-8">No chats yet</div>
      ) : (
        chats.map((chat, index) => (
          <div
            key={chat.id || `chat-${index}`}
            onClick={() => handleChatClick(chat.id)}
            className={`p-3 rounded-lg transition-colors text-sm group flex items-center gap-2 ${isGenerating && currentChatId !== chat.id
              ? "opacity-50 cursor-not-allowed"
              : "cursor-pointer"
              } ${currentChatId === chat.id
                ? "bg-sidebar-primary text-sidebar-primary-foreground"
                : "text-sidebar-foreground hover:bg-sidebar-accent"
              }`}
          >
            {editingId === chat.id ? (
              <div className="flex-1 flex gap-2" onClick={(e) => e.stopPropagation()}>
                <Input
                  value={editingTitle}
                  onChange={(e) => setEditingTitle(e.target.value)}
                  className="h-7 text-xs"
                  autoFocus
                />
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7"
                  onClick={(e) => {
                    e.stopPropagation()
                    handleRenameChat(chat.id)
                  }}
                >
                  <Check className="h-3 w-3" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7"
                  onClick={(e) => {
                    e.stopPropagation()
                    setEditingId(null)
                  }}
                >
                  <XIcon className="h-3 w-3" />
                </Button>
              </div>
            ) : (
              <>
                <span className="flex-1 truncate">{chat.title}</span>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7 opacity-0 group-hover:opacity-100"
                  disabled={isGenerating}
                  onClick={(e) => {
                    e.stopPropagation()
                    if (!isGenerating) startEditingChat(chat)
                  }}
                >
                  <Edit2 className="h-3 w-3" />
                </Button>
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7 opacity-0 group-hover:opacity-100 text-destructive"
                  disabled={isGenerating}
                  onClick={(e) => !isGenerating && handleDeleteChat(e, chat.id)}
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </>
            )}
          </div>
        ))
      )}
    </div>
  )

  return (
    <>
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <Button variant="outline" size="icon" onClick={() => setMobileOpen(!mobileOpen)} className="bg-background">
          {mobileOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
        </Button>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex md:w-90 md:h-screen md:flex-col">
        <div className="flex flex-col h-full bg-sidebar overflow-hidden border-r border-border">
          {/* New Chat Button */}
          <div className="p-4 border-b border-sidebar-border shrink-0">
            <Button
              onClick={handleNewChat}
              className="w-full gap-2"
              size="sm"
              disabled={isGenerating}
            >
              <Plus className="h-4 w-4" />
              New Chat
            </Button>
          </div>

          {/* Chat History */}
          <ScrollArea className="flex-1 min-h-0">
            {chatListContent}
          </ScrollArea>

          {/* Logout Button */}
          <div className="px-4 py-3 border-t border-sidebar-border shrink-0">
            <Button
              onClick={() => logout()}
              variant="ghost"
              className="w-full gap-2 text-sidebar-foreground hover:bg-sidebar-accent h-10"
              size="sm"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 md:hidden bg-black/20">
          <div className="absolute inset-y-0 left-0 w-90 bg-sidebar">
            <div className="flex flex-col h-full bg-sidebar overflow-hidden border-r border-border">
              {/* New Chat Button */}
              <div className="p-4 border-b border-sidebar-border shrink-0">
                <Button
                  onClick={handleNewChat}
                  className="w-full gap-2"
                  size="sm"
                  disabled={isGenerating}
                >
                  <Plus className="h-4 w-4" />
                  New Chat
                </Button>
              </div>

              {/* Chat History */}
              <ScrollArea className="flex-1 min-h-0">
                {chatListContent}
              </ScrollArea>

              {/* Logout Button */}
              <div className="px-4 py-3 border-t border-sidebar-border shrink-0">
                <Button
                  onClick={() => logout()}
                  variant="ghost"
                  className="w-full gap-2 text-sidebar-foreground hover:bg-sidebar-accent h-10"
                  size="sm"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  )
})
Sidebar.displayName = "Sidebar"
