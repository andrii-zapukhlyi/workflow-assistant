"use client"

import { useEffect, useRef, useState } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { Message } from "@/lib/auth"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ExternalLink, FileText, Image as ImageIcon } from "lucide-react"

interface ChatMessagesProps {
  chatId: string
  messages: Message[]
  isLoading: boolean
  isGenerating?: boolean
}



// Image component with loading state
function InlineImage({ src, alt }: { src: string; alt?: string }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  if (error) {
    return (
      <a
        href={src}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex items-center gap-1 text-primary hover:underline text-xs"
      >
        <ImageIcon className="h-3 w-3" />
        View image
      </a>
    )
  }

  return (
    <div className="my-3">
      {loading && (
        <div className="w-full h-32 bg-muted rounded-lg animate-pulse flex items-center justify-center">
          <ImageIcon className="h-6 w-6 text-muted-foreground" />
        </div>
      )}
      <img
        src={src}
        alt={alt || "Image"}
        className={`max-w-full h-auto rounded-lg border border-border shadow-sm ${loading ? 'hidden' : 'block'}`}
        onLoad={() => setLoading(false)}
        onError={() => { setError(true); setLoading(false) }}
      />
    </div>
  )
}

// Custom component to render markdown with inline images
function MessageContent({ content }: { content: string }) {
  // First, preprocess content to handle [Image: url] and [Image (desc): url] patterns
  // Pattern: [Image: url] or [Image (description): url]
  const imageTagPattern = /\[Image(?:\s*\([^)]*\))?:\s*(https?:\/\/[^\s\]]+\.(?:png|jpg|jpeg|gif|webp|svg)(?:\?[^\s\]]*)?)\]/gi

  // Replace [Image: url] patterns with just the URL
  let processedContent = content.replace(imageTagPattern, '$1')

  // Pattern to match image URLs (Confluence attachments and common image extensions)
  const imageUrlPattern = /(https?:\/\/[^\s<>]+?\.(?:png|jpg|jpeg|gif|webp|svg)(?:\?[^\s<>.,)]*)?)/gi

  // Check if processed content contains image URLs
  const imageUrls = processedContent.match(imageUrlPattern) || []

  // If there are image URLs, we need to process them
  if (imageUrls.length > 0) {
    // Split content by image URLs and render parts
    const parts: React.ReactNode[] = []
    let lastIndex = 0
    let partKey = 0

    // Find all image URL occurrences
    const matches: { url: string; index: number; length: number }[] = []
    let match
    const regex = new RegExp(imageUrlPattern.source, 'gi')
    while ((match = regex.exec(processedContent)) !== null) {
      matches.push({ url: match[0], index: match.index, length: match[0].length })
    }

    matches.forEach((m) => {
      // Add text before the image, cleaning up any trailing punctuation before the URL
      if (m.index > lastIndex) {
        let textBefore = processedContent.slice(lastIndex, m.index)
        // Clean up text that might have artifacts from the [Image: ] pattern
        textBefore = textBefore.replace(/\[Image[^\]]*$/i, '')
        if (textBefore.trim()) {
          parts.push(
            <ReactMarkdown key={`text-${partKey++}`} remarkPlugins={[remarkGfm]}>
              {textBefore}
            </ReactMarkdown>
          )
        }
      }

      // Add the image
      parts.push(<InlineImage key={`img-${partKey++}`} src={m.url} />)

      // Skip trailing punctuation after the URL (like dots, commas)
      let endIndex = m.index + m.length
      while (endIndex < processedContent.length && /^[.,;:)\]]/.test(processedContent[endIndex])) {
        endIndex++
      }
      lastIndex = endIndex
    })

    // Add remaining text after last image
    if (lastIndex < processedContent.length) {
      const textAfter = processedContent.slice(lastIndex)
      if (textAfter.trim()) {
        parts.push(
          <ReactMarkdown key={`text-${partKey++}`} remarkPlugins={[remarkGfm]}>
            {textAfter}
          </ReactMarkdown>
        )
      }
    }

    return <>{parts}</>
  }

  // No images, render normally
  return <ReactMarkdown remarkPlugins={[remarkGfm]}>{processedContent}</ReactMarkdown>
}

// Source links component
function SourceLinks({ links, titles }: { links: string[]; titles: string[] }) {
  if (!links || links.length === 0) return null

  return (
    <div className="mt-4 pt-3 border-t border-border/50">
      <p className="text-xs text-muted-foreground mb-2 font-medium flex items-center gap-1">
        <FileText className="h-3 w-3" />
        Sources ({links.length})
      </p>
      <div className="flex flex-wrap gap-2">
        {links.map((link, index) => {
          const title = titles && titles[index] ? titles[index] : 'docs'
          return (
            <a
              key={index}
              href={link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs bg-muted/50 hover:bg-muted text-foreground rounded-lg border border-border/50 hover:border-border transition-colors group"
            >
              <span className="truncate max-w-[260px]">Confluence — {title}</span>
              <ExternalLink className="h-3 w-3 opacity-50 group-hover:opacity-100 shrink-0" />
            </a>
          )
        })}
      </div>
    </div>
  )
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
      <div className="flex-1 flex items-center justify-center bg-background">
        <div className="w-8 h-8 border-3 border-primary/30 border-t-primary rounded-full animate-spin"></div>
      </div>
    )
  }

  return (
    <ScrollArea className="flex-1 min-h-0 bg-background">
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
                : "bg-card text-card-foreground rounded-bl-none border border-border"
                }`}
            >
              <div className="break-words">
                {message.role === 'assistant' ? (
                  <>
                    <div className="prose prose-sm dark:prose-invert max-w-none markdown-content">
                      <MessageContent content={message.content} />
                    </div>
                    <SourceLinks links={message.links || []} titles={message.titles || []} />
                  </>
                ) : (
                  <span className="whitespace-pre-wrap">{message.content}</span>
                )}
              </div>
            </div>
          </div>
        ))}

        {isGenerating && (
          <div className="flex justify-start gap-4 animate-in fade-in duration-300">
            <div className="bg-card text-card-foreground px-5 py-3.5 rounded-2xl rounded-bl-none border border-border shadow-sm flex items-center space-x-2">
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
