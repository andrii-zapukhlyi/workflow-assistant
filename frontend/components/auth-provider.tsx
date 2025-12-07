"use client"

import React, { createContext, useContext, useEffect, useState, useCallback } from "react"
import { authService, type User } from "@/lib/auth"
import { useRouter } from "next/navigation"

interface AuthContextType {
    user: User | null
    loading: boolean
    error: string | null
    login: (email: string, password: string) => Promise<void>
    register: (
        fullName: string,
        email: string,
        password: string,
        position: string,
        department: string,
        positionLevel: string,
    ) => Promise<void>
    logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const router = useRouter()

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const token = authService.getToken()
                if (!token) {
                    setLoading(false)
                    return
                }

                try {
                    const fetchedUser = await authService.getMe()
                    setUser(fetchedUser)
                } catch (e) {
                    console.error("Failed to fetch user info", e)
                    // If we fail to get user info, verify if token is valid or just clear it?
                    // Don't auto-logout on network error, but if 401 it handles itself.
                }
            } catch (err) {
                console.error("Auth check failed", err)
            } finally {
                setLoading(false)
            }
        }

        checkAuth()
    }, [])

    const login = useCallback(async (email: string, password: string) => {
        try {
            setLoading(true)
            setError(null)
            await authService.login(email, password)
            const fetchedUser = await authService.getMe()
            setUser(fetchedUser)
            router.push("/chat")
        } catch (err) {
            const message = err instanceof Error ? err.message : "Login failed"
            setError(message)
            throw err
        } finally {
            setLoading(false)
        }
    }, [router])

    const register = useCallback(
        async (
            fullName: string,
            email: string,
            password: string,
            position: string,
            department: string,
            positionLevel: string,
        ) => {
            try {
                setLoading(true)
                setError(null)
                await authService.register(fullName, email, password, position, department, positionLevel)
                const fetchedUser = await authService.getMe()
                setUser(fetchedUser)
                router.push("/chat")
            } catch (err) {
                const message = err instanceof Error ? err.message : "Registration failed"
                setError(message)
                throw err
            } finally {
                setLoading(false)
            }
        },
        [router],
    )

    const logout = useCallback(async () => {
        try {
            await authService.logout()
            setUser(null)
            router.push("/login")
        } catch (err) {
            const message = err instanceof Error ? err.message : "Logout failed"
            setError(message)
            throw err
        }
    }, [router])

    return (
        <AuthContext.Provider value={{ user, loading, error, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuthContext() {
    const context = useContext(AuthContext)
    if (context === undefined) {
        throw new Error("useAuthContext must be used within an AuthProvider")
    }
    return context
}
