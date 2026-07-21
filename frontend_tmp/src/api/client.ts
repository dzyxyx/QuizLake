const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? 'http://localhost:8000/api/v1'

const ACCESS_TOKEN_KEY = 'quizlake_access_token'
const REFRESH_TOKEN_KEY = 'quizlake_refresh_token'

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken)
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
}

export class ApiError extends Error {
  status: number
  detail: unknown

  constructor(status: number, message: string, detail?: unknown) {
    super(message)
    this.status = status
    this.detail = detail
  }
}

interface RequestOptions {
  method?: string
  body?: unknown
  auth?: boolean
  query?: Record<string, string | number | boolean | undefined>
}

function buildUrl(path: string, query?: RequestOptions['query']): string {
  const url = new URL(API_BASE_URL + path)
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined) url.searchParams.set(key, String(value))
    }
  }
  return url.toString()
}

let refreshPromise: Promise<boolean> | null = null

async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  if (!refreshPromise) {
    refreshPromise = (async () => {
      try {
        const response = await fetch(buildUrl('/auth/refresh'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh_token: refreshToken }),
        })
        if (!response.ok) return false
        const data = await response.json()
        setTokens(data.access_token, data.refresh_token)
        return true
      } catch {
        return false
      } finally {
        refreshPromise = null
      }
    })()
  }
  return refreshPromise
}

function handleAuthFailure() {
  clearTokens()
  localStorage.removeItem('quizlake_user')
  window.dispatchEvent(new CustomEvent('quizlake:auth-expired'))
}

export async function apiRequest<T = unknown>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true, query } = options

  async function doFetch(): Promise<Response> {
    const headers: Record<string, string> = {}
    if (body !== undefined) headers['Content-Type'] = 'application/json'
    if (auth) {
      const token = getAccessToken()
      if (token) headers['Authorization'] = `Bearer ${token}`
    }
    return fetch(buildUrl(path, query), {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  }

  let response = await doFetch()

  if (response.status === 401 && auth) {
    const refreshed = await refreshAccessToken()
    if (refreshed) {
      response = await doFetch()
    } else {
      handleAuthFailure()
    }
  }

  if (!response.ok) {
    let detail: unknown = null
    try {
      detail = await response.json()
    } catch {
    }
    const detailText =
      detail && typeof detail === 'object' && 'detail' in detail && typeof (detail as any).detail === 'string'
        ? (detail as any).detail
        : null
    throw new ApiError(response.status, detailText ?? `Ошибка запроса (${response.status})`, detail)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function wsUrl(path: string): string {
  const base = (import.meta.env.VITE_WS_BASE_URL as string | undefined) ?? 'ws://localhost:8000/api/v1'
  return base + path
}
