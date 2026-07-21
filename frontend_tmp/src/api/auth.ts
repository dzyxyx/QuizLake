import { apiRequest } from '@/api/client'
import type { User } from '@/types'

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface RegisterPayload {
  first_name: string
  last_name: string
  nickname: string
  email: string
  password: string
}

export function register(data: RegisterPayload) {
  return apiRequest<User>('/auth/register', { method: 'POST', body: data, auth: false })
}

export function login(email: string, password: string, rememberMe: boolean) {
  return apiRequest<Token>('/auth/login', {
    method: 'POST',
    body: { email, password, remember_me: rememberMe },
    auth: false,
  })
}

export function refresh(refreshToken: string) {
  return apiRequest<Token>('/auth/refresh', {
    method: 'POST',
    body: { refresh_token: refreshToken },
    auth: false,
  })
}

export function logout(refreshToken: string) {
  return apiRequest<void>('/auth/logout', {
    method: 'POST',
    body: { refresh_token: refreshToken },
    auth: false,
  })
}
