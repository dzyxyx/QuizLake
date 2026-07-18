import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types'

// Стор авторизации. Пока бэкенда нет, login/register просто подделывают ответ сервера
// (создают "фейкового" пользователя и токен), чтобы можно было пройти по всем экранам.
// Когда появится реальный API — поменяется только содержимое функций login/register/logout,
// остальной код (router, компоненты) трогать не придётся.

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('quizlake_token'))
  const user = ref<User | null>(loadStoredUser())

  const isAuthenticated = computed(() => !!token.value)

  function loadStoredUser(): User | null {
    const raw = localStorage.getItem('quizlake_user')
    return raw ? (JSON.parse(raw) as User) : null
  }

  function persist() {
    if (token.value) localStorage.setItem('quizlake_token', token.value)
    else localStorage.removeItem('quizlake_token')

    if (user.value) localStorage.setItem('quizlake_user', JSON.stringify(user.value))
    else localStorage.removeItem('quizlake_user')
  }

  async function login(email: string, _password: string) {
    // TODO: заменить на реальный запрос к /auth/login, когда API будет готов
    user.value = {
      id: 1,
      first_name: 'Мария',
      last_name: 'Ковалёва',
      nickname: 'maria_quiz',
      email,
      avatar_url: null,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    token.value = 'mock-jwt-token'
    persist()
  }

  async function register(data: {
    firstName: string
    lastName: string
    email: string
    nickname?: string
  }) {
    // TODO: заменить на реальный запрос к /auth/register
    user.value = {
      id: 1,
      first_name: data.firstName,
      last_name: data.lastName,
      nickname: data.nickname ?? null,
      email: data.email,
      avatar_url: null,
      is_active: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    token.value = 'mock-jwt-token'
    persist()
  }

  function logout() {
    token.value = null
    user.value = null
    persist()
  }

  return { token, user, isAuthenticated, login, register, logout }
})
