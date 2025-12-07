import type React from "react"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Chat | ChatBot",
  description: "Multi-chat chatbot interface",
}

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
