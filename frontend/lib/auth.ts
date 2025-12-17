// JWT Token Management
const TOKEN_KEY = "jwt_token"

export const authService = {
  // Token management
  setToken: (token: string) => {
    if (typeof window !== "undefined") {
      localStorage.setItem(TOKEN_KEY, token)
      const secureFlag = window.location.protocol === 'https:' ? 'Secure;' : '';
      document.cookie = `${TOKEN_KEY}=${token}; path=/; max-age=86400; SameSite=Strict; ${secureFlag}`
    }
  },

  getToken: (): string | null => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(TOKEN_KEY)
    }
    return null
  },

  clearToken: () => {
    if (typeof window !== "undefined") {
      localStorage.removeItem(TOKEN_KEY)
      document.cookie = `${TOKEN_KEY}=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;`
    }
  },

  isAuthenticated: (): boolean => {
    return !!authService.getToken()
  },

  // API calls with token
  async apiCall<T>(
    endpoint: string,
    method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
    body?: Record<string, any> | URLSearchParams,
    customHeaders?: HeadersInit,
  ): Promise<T> {
    const token = authService.getToken()
    const headers: HeadersInit = {
      "Content-Type": "application/json",
      ...customHeaders,
    }

    if (token) {
      // @ts-ignore
      headers["Authorization"] = `Bearer ${token}`
    }

    const baseUrl = typeof window !== 'undefined'
      ? '/api'
      : (process.env.INTERNAL_API_URL || 'http://localhost:8000');

    const response = await fetch(`${baseUrl}${endpoint}`, {
      method,
      headers,
      body: body instanceof URLSearchParams ? body : body ? JSON.stringify(body) : undefined,
      credentials: "include", // Include cookies (for refresh token)
    })

    if (!response.ok) {
      // Try to refresh token on 401, but NOT if we are already trying to login/register/refresh
      // or if we are on the login page (to avoid loops)
      const isAuthEndpoint = endpoint === "/auth/login" || endpoint === "/auth/register" || endpoint === "/auth/refresh"

      if (response.status === 401 && !isAuthEndpoint) {
        try {
          await authService.refreshToken()
          // Retry the request
          return authService.apiCall<T>(endpoint, method, body, customHeaders)
        } catch (error) {
          authService.clearToken()
          window.location.href = "/login"
          throw error
        }
      }

      const errorText = await response.text()
      const errorData = JSON.parse(errorText)
      throw new Error(errorData.detail)
    }

    return response.json()
  },

  // Authentication endpoints
  async login(email: string, password: string) {
    const formData = new URLSearchParams()
    formData.append("username", email)
    formData.append("password", password)

    const data = await authService.apiCall<{ access_token: string }>(
      "/auth/login",
      "POST",
      formData,
      { "Content-Type": "application/x-www-form-urlencoded" },
    )
    authService.setToken(data.access_token)
    return data
  },

  async register(
    fullName: string,
    email: string,
    password: string,
    position: string,
    department: string,
    positionLevel: string,
  ) {
    const data = await authService.apiCall<{ access_token: string }>("/auth/register", "POST", {
      full_name: fullName,
      email,
      password,
      position,
      department,
      position_level: positionLevel,
    })
    authService.setToken(data.access_token)
    return data
  },

  async logout() {
    try {
      await authService.apiCall("/auth/logout", "POST")
    } finally {
      authService.clearToken()
      window.location.href = "/login"
    }
  },

  async refreshToken() {
    const data = await authService.apiCall<{ access_token: string }>("/auth/refresh", "POST")
    authService.setToken(data.access_token)
    return data
  },

  async getMe(): Promise<User> {
    return authService.apiCall<User>("/auth/me", "GET")
  },
}

// Types
export interface User {
  id: string
  email: string
  full_name: string
  position: string
  department: string
  position_level: string
}

export interface Chat {
  id: string
  title: string
  created_at: string
  updated_at: string
}

export interface Message {
  id: string
  chat_id: string
  role: "user" | "assistant"
  content: string
  created_at: string
  links?: string[] // Retrieved document links for assistant messages
  titles?: string[] // Retrieved document titles for assistant messages
}
