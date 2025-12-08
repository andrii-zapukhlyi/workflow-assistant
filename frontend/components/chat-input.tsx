"use client"

import type React from "react"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Send } from "lucide-react"

interface ChatInputProps {
  chatId: string
  onMessageSent: (message: string) => Promise<void>
}

export function ChatInput({ chatId, onMessageSent }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!message.trim() || loading) return

    try {
      setLoading(true)
      const currentMessage = message
      setMessage("") // Clear input immediately for better UX
      await onMessageSent(currentMessage)
    } catch (error) {
      console.error("Failed to send message:", error)
      setMessage(message) // Restore message on error
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-border bg-background px-4 py-3 shrink-0">
      <div className="max-w-4xl mx-auto flex gap-3 items-center">
        <Input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type your message..."
          disabled={loading}
          className="flex-1 h-10"
        />
        <Button type="submit" disabled={loading || !message.trim()} size="icon" className="h-10 w-10">
          <Send className="h-4 w-4" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
    </form>
  )
}
