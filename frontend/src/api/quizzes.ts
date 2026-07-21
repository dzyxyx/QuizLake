import { apiRequest } from '@/api/client'
import type { DiscoverSession, Quiz, QuizStatus } from '@/types'

export interface QuizPayload {
  category_id?: number | null
  title: string
  description?: string | null
  difficulty?: string
  time_per_question_sec?: number
  speed_bonus_enabled?: boolean
  show_correct_answer?: boolean
  allow_answer_change?: boolean
  is_public?: boolean
  cover_image_url?: string | null
}

export function listMyQuizzes(status?: QuizStatus) {
  return apiRequest<Quiz[]>('/quizzes', { query: { status } })
}

export function getQuiz(quizId: number) {
  return apiRequest<Quiz>(`/quizzes/${quizId}`)
}

export function createQuiz(data: QuizPayload) {
  return apiRequest<Quiz>('/quizzes', { method: 'POST', body: data })
}

export function updateQuiz(quizId: number, data: Partial<QuizPayload & { status: QuizStatus }>) {
  return apiRequest<Quiz>(`/quizzes/${quizId}`, { method: 'PATCH', body: data })
}

export function deleteQuiz(quizId: number) {
  return apiRequest<void>(`/quizzes/${quizId}`, { method: 'DELETE' })
}

export function listDiscoverSessions() {
  return apiRequest<DiscoverSession[]>('/quizzes/discover', { auth: false })
}
