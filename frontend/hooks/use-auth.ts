"use client"

import { useAuthContext } from "@/components/auth-provider"
import { authService } from "@/lib/auth"

export function useAuth() {
  const context = useAuthContext()

  return {
    ...context,
    isAuthenticated: authService.isAuthenticated(),
  }
}
