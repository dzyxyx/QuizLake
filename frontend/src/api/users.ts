import { apiRequest } from '@/api/client'
import type { User, UserStats, ParticipationHistoryItem, HostedSessionHistoryItem } from '@/types'

export interface UpdateMePayload {
  first_name?: string
  last_name?: string
  nickname?: string
  email?: string
  password?: string
  avatar_url?: string
}

export function getMe() {
  return apiRequest<User>('/users/me')
}

export function updateMe(data: UpdateMePayload) {
  return apiRequest<User>('/users/me', { method: 'PATCH', body: data })
}

export function getMyStats() {
  return apiRequest<UserStats>('/users/me/stats')
}

export function getParticipationHistory() {
  return apiRequest<ParticipationHistoryItem[]>('/users/me/participation-history')
}

export function getHostedHistory() {
  return apiRequest<HostedSessionHistoryItem[]>('/users/me/hosted-history')
}
