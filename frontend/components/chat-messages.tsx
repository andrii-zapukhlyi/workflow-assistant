"use client"

import { useEffect, useRef } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { Message } from "@/lib/auth"
import ReactMarkdown from 'react-markdown'

interface ChatMessagesProps {
  chatId: string
  messages: Message[]
  isLoading: boolean
  isGenerating?: boolean
}

export function ChatMessages({ chatId, messages, isLoading, isGenerating }: ChatMessagesProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, isGenerating])

  if (isLoading) {
    return (
      <ScrollArea className="flex-1 bg-background">
        <div className="flex items-center justify-center h-full text-muted-foreground">
          <div className="flex flex-col items-center gap-2">
            <div className="w-6 h-6 border-2 border-primary/30 border-t-primary rounded-full animate-spin"></div>
            <p className="text-sm">Loading history...</p>
          </div>
        </div>
      </ScrollArea>
    )
  }

  return (
    <ScrollArea className="flex-1 bg-background">
      <div className="max-w-4xl mx-auto p-6 space-y-6">
        {messages.length === 0 && !isGenerating && (
          <div className="flex items-center justify-center h-64 text-muted-foreground">
            <p>No messages yet. Start the conversation!</p>
          </div>
        )}

        {messages.map((message, index) => (
          <div key={index} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"} gap-4`}>
            <div
              className={`max-w-3xl px-5 py-3.5 rounded-2xl shadow-sm text-sm leading-relaxed ${message.role === "user"
                  ? "bg-primary text-primary-foreground rounded-br-none"
                  : "bg-muted/80 backdrop-blur supports-[backdrop-filter]:bg-muted/60 text-foreground rounded-bl-none border border-border/50"
                }`}
            >
              <div className="whitespace-pre-wrap break-words">
                {message.role === 'assistant' ? (
                  <div className="markdown-body">
                    {/* You might want to use a markdown renderer here in the future */}
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  </div>
                ) : (
                  message.content
                )}
              </div>
            </div>
          </div>
        ))}

        {isGenerating && (
          <div className="flex justify-start gap-4 animate-in fade-in duration-300">
            <div className="bg-muted/80 backdrop-blur supports-[backdrop-filter]:bg-muted/60 text-foreground px-5 py-3.5 rounded-2xl rounded-bl-none border border-border/50 shadow-sm flex items-center space-x-2">
              <span className="w-1.5 h-1.5 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.32s]"></span>
              <span className="w-1.5 h-1.5 bg-foreground/40 rounded-full animate-bounce [animation-delay:-0.16s]"></span>
              <span className="w-1.5 h-1.5 bg-foreground/40 rounded-full animate-bounce"></span>
            </div>
          </div>
        )}

        <div ref={scrollRef} />
      </div>
    </ScrollArea>
  )
}
