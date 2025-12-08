import type React from "react"
import type { Metadata } from "next"

export const metadata: Metadata = {
  title: "Workflow Assistant",
  description: "Multi-chat chatbot interface",
}

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}
