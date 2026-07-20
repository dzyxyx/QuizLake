import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { apiRequest, ApiError, setTokens, getAccessToken, getRefreshToken } from '@/api/client'

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

describe('apiRequest', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('returns parsed JSON on success', async () => {
    ;(fetch as any).mockResolvedValueOnce(jsonResponse({ hello: 'world' }))

    const result = await apiRequest('/ping', { auth: false })

    expect(result).toEqual({ hello: 'world' })
  })

  it('attaches Authorization header when a token exists and auth is true', async () => {
    setTokens('access-1', 'refresh-1')
    ;(fetch as any).mockResolvedValueOnce(jsonResponse({ ok: true }))

    await apiRequest('/me', { auth: true })

    const [, init] = (fetch as any).mock.calls[0]
    expect(init.headers.Authorization).toBe('Bearer access-1')
  })

  it('omits Authorization header when auth is false', async () => {
    setTokens('access-1', 'refresh-1')
    ;(fetch as any).mockResolvedValueOnce(jsonResponse({ ok: true }))

    await apiRequest('/public', { auth: false })

    const [, init] = (fetch as any).mock.calls[0]
    expect(init.headers.Authorization).toBeUndefined()
  })

  it('returns undefined for a 204 response', async () => {
    ;(fetch as any).mockResolvedValueOnce(new Response(null, { status: 204 }))

    const result = await apiRequest('/thing', { method: 'DELETE' })

    expect(result).toBeUndefined()
  })

  it('throws ApiError with server-provided detail on failure', async () => {
    ;(fetch as any).mockResolvedValueOnce(jsonResponse({ detail: 'Email уже занят' }, 400))

    await expect(apiRequest('/auth/register', { method: 'POST', auth: false })).rejects.toMatchObject({
      status: 400,
      message: 'Email уже занят',
    })
  })

  it('refreshes the access token on a 401 and retries the original request', async () => {
    setTokens('expired-access', 'valid-refresh')
    const mockFetch = fetch as any
    mockFetch
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access_token: 'new-access', refresh_token: 'new-refresh' }))
      .mockResolvedValueOnce(jsonResponse({ id: 1 }))

    const result = await apiRequest('/users/me')

    expect(result).toEqual({ id: 1 })
    expect(mockFetch).toHaveBeenCalledTimes(3)
    expect(getAccessToken()).toBe('new-access')
    expect(getRefreshToken()).toBe('new-refresh')

    const retryHeaders = mockFetch.mock.calls[2][1].headers
    expect(retryHeaders.Authorization).toBe('Bearer new-access')
  })

  it('clears tokens and dispatches auth-expired when refresh itself fails', async () => {
    setTokens('expired-access', 'invalid-refresh')
    const mockFetch = fetch as any
    mockFetch
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(new Response(null, { status: 401 }))

    const listener = vi.fn()
    window.addEventListener('quizlake:auth-expired', listener)

    await expect(apiRequest('/users/me')).rejects.toBeInstanceOf(ApiError)

    expect(getAccessToken()).toBeNull()
    expect(listener).toHaveBeenCalledOnce()

    window.removeEventListener('quizlake:auth-expired', listener)
  })

  it('deduplicates concurrent refresh calls into a single request', async () => {
    setTokens('expired-access', 'valid-refresh')
    const mockFetch = fetch as any
    mockFetch
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(new Response(null, { status: 401 }))
      .mockResolvedValueOnce(jsonResponse({ access_token: 'new-access', refresh_token: 'new-refresh' }))
      .mockResolvedValueOnce(jsonResponse({ a: 1 }))
      .mockResolvedValueOnce(jsonResponse({ b: 2 }))

    const [a, b] = await Promise.all([apiRequest('/a'), apiRequest('/b')])

    expect(a).toEqual({ a: 1 })
    expect(b).toEqual({ b: 2 })

    const refreshCalls = mockFetch.mock.calls.filter(([url]: [string]) => url.includes('/auth/refresh'))
    expect(refreshCalls).toHaveLength(1)
  })
})
