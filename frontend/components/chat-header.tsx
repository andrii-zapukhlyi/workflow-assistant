"use client"
import { ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

import { useAuth } from "@/hooks/use-auth"

interface ChatHeaderProps {
  currentChatTitle?: string
  onLogout?: () => void
}

export function ChatHeader({ currentChatTitle = "New Chat", onLogout }: ChatHeaderProps) {
  const { user } = useAuth()

  if (!user) return null

  return (
    <div className="border-b border-border bg-card px-6 py-4 shrink-0">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold text-foreground">Workflow Assistant</h1>

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-2">
              <div className="flex items-center gap-2">
                <div className="text-right">
                  <p className="text-xs font-medium leading-none">{user.full_name}</p>
                  <p className="text-xs text-muted-foreground">{user.position}</p>
                </div>
              </div>
              <ChevronDown className="h-4 w-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <div className="px-2 py-1.5">
              <p className="text-xs font-medium text-muted-foreground">Account</p>
              <p className="text-sm font-semibold">{user.full_name}</p>
              <p className="text-xs text-muted-foreground">{user.email}</p>
            </div>
            <div className="border-t border-border my-1" />
            <div className="px-2 py-1.5">
              <p className="text-xs text-muted-foreground mb-1">Department: {user.department}</p>
              <p className="text-xs text-muted-foreground">Level: {user.position_level}</p>
            </div>
            <div className="border-t border-border my-1" />
            <DropdownMenuItem onClick={() => onLogout?.()} className="text-destructive">
              Logout
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  )
}
