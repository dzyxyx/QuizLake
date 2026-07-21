import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'
import * as authApi from '@/api/auth'
import * as usersApi from '@/api/users'
import { setTokens, clearTokens, getAccessToken, getRefreshToken } from '@/api/client'
import { useQuizzesStore } from '@/stores/quizzes'
import { useProfileStore } from '@/stores/profile'

function resetUserScopedStores() {
  useQuizzesStore().reset()
  useProfileStore().reset()
}

const USER_STORAGE_KEY = 'quizlake_user'

function loadStoredUser(): User | null {
  const raw = localStorage.getItem(USER_STORAGE_KEY)
  return raw ? (JSON.parse(raw) as User) : null
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(loadStoredUser())
  const isAuthenticated = computed(() => !!user.value)
  let bootstrapped = false

  function persistUser() {
    if (user.value) localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user.value))
    else localStorage.removeItem(USER_STORAGE_KEY)
  }

  async function login(email: string, password: string, rememberMe: boolean) {
    const tokens = await authApi.login(email, password, rememberMe)
    setTokens(tokens.access_token, tokens.refresh_token)
    resetUserScopedStores()
    user.value = await usersApi.getMe()
    persistUser()
  }

  async function register(data: authApi.RegisterPayload) {
    await authApi.register(data)
    await login(data.email, data.password, true)
  }

  async function logout() {
    const refreshToken = getRefreshToken()
    if (refreshToken) {
      try {
        await authApi.logout(refreshToken)
      } catch {
      }
    }
    clearTokens()
    user.value = null
    persistUser()
    resetUserScopedStores()
  }

  async function updateProfile(data: usersApi.UpdateMePayload) {
    user.value = await usersApi.updateMe(data)
    persistUser()
    return user.value
  }

  async function bootstrap() {
    if (bootstrapped) return
    bootstrapped = true
    if (!getAccessToken()) return

    try {
      user.value = await usersApi.getMe()
      persistUser()
    } catch {
      clearTokens()
      user.value = null
      persistUser()
      resetUserScopedStores()
    }
  }

  window.addEventListener('quizlake:auth-expired', () => {
    user.value = null
    persistUser()
    resetUserScopedStores()
  })

  return { user, isAuthenticated, login, register, logout, updateProfile, bootstrap }
})
