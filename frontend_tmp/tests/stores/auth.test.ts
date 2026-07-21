import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import * as authApi from '@/api/auth'
import * as usersApi from '@/api/users'
import { getAccessToken, getRefreshToken, setTokens } from '@/api/client'

vi.mock('@/api/auth')
vi.mock('@/api/users')

const mockUser = {
  id: 1,
  first_name: 'Test',
  last_name: 'User',
  nickname: 'tester',
  email: 'test@example.com',
  avatar_url: null,
}

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(authApi.login).mockReset()
    vi.mocked(authApi.register).mockReset()
    vi.mocked(authApi.logout).mockReset()
    vi.mocked(usersApi.getMe).mockReset()
    vi.mocked(usersApi.updateMe).mockReset()
  })

  it('starts unauthenticated with no stored user', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
  })

  it('login stores tokens and the fetched user, marking the store authenticated', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'acc',
      refresh_token: 'ref',
      token_type: 'bearer',
    })
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)

    const store = useAuthStore()
    await store.login('test@example.com', 'secret123', false)

    expect(store.isAuthenticated).toBe(true)
    expect(store.user).toEqual(mockUser)
    expect(getAccessToken()).toBe('acc')
    expect(getRefreshToken()).toBe('ref')
    expect(JSON.parse(localStorage.getItem('quizlake_user')!)).toEqual(mockUser)
  })

  it('register calls register then logs in with the same credentials', async () => {
    vi.mocked(authApi.register).mockResolvedValue(mockUser)
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'acc',
      refresh_token: 'ref',
      token_type: 'bearer',
    })
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)

    const store = useAuthStore()
    await store.register({
      first_name: 'Test',
      last_name: 'User',
      nickname: 'tester',
      email: 'test@example.com',
      password: 'secret123',
    })

    expect(authApi.register).toHaveBeenCalledOnce()
    expect(authApi.login).toHaveBeenCalledWith('test@example.com', 'secret123', true)
    expect(store.isAuthenticated).toBe(true)
  })

  it('logout clears tokens and user even if the server call rejects', async () => {
    setTokens('acc', 'ref')
    vi.mocked(authApi.logout).mockRejectedValue(new Error('network error'))

    const store = useAuthStore()
    store.user = mockUser as any

    await store.logout()

    expect(store.isAuthenticated).toBe(false)
    expect(store.user).toBeNull()
    expect(getAccessToken()).toBeNull()
    expect(localStorage.getItem('quizlake_user')).toBeNull()
  })

  it('bootstrap is a no-op when there is no stored access token', async () => {
    const store = useAuthStore()
    await store.bootstrap()

    expect(usersApi.getMe).not.toHaveBeenCalled()
    expect(store.isAuthenticated).toBe(false)
  })

  it('bootstrap loads the current user when an access token is present', async () => {
    setTokens('acc', 'ref')
    vi.mocked(usersApi.getMe).mockResolvedValue(mockUser)

    const store = useAuthStore()
    await store.bootstrap()

    expect(store.user).toEqual(mockUser)
  })

  it('bootstrap clears tokens if the stored token is no longer valid', async () => {
    setTokens('stale-acc', 'stale-ref')
    vi.mocked(usersApi.getMe).mockRejectedValue(new Error('401'))

    const store = useAuthStore()
    await store.bootstrap()

    expect(store.user).toBeNull()
    expect(getAccessToken()).toBeNull()
  })

  it('clears the user when a quizlake:auth-expired event fires', () => {
    const store = useAuthStore()
    store.user = mockUser as any

    window.dispatchEvent(new CustomEvent('quizlake:auth-expired'))

    expect(store.user).toBeNull()
  })
})
