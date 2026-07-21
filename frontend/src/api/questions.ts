import { apiRequest } from '@/api/client'
import type { Question } from '@/types'

export interface AnswerOptionPayload {
  option_text: string
  is_correct: boolean
  order_index: number
}

export interface QuestionPayload {
  question_text: string
  image_url?: string | null
  question_type?: string
  order_index: number
  time_limit_sec?: number | null
  points?: number | null
  answer_options: AnswerOptionPayload[]
}

export function listQuestions(quizId: number) {
  return apiRequest<Question[]>(`/quizzes/${quizId}/questions`)
}

export function createQuestion(quizId: number, data: QuestionPayload) {
  return apiRequest<Question>(`/quizzes/${quizId}/questions`, { method: 'POST', body: data })
}

export function updateQuestion(quizId: number, questionId: number, data: Partial<QuestionPayload>) {
  return apiRequest<Question>(`/quizzes/${quizId}/questions/${questionId}`, { method: 'PATCH', body: data })
}

export function deleteQuestion(quizId: number, questionId: number) {
  return apiRequest<void>(`/quizzes/${quizId}/questions/${questionId}`, { method: 'DELETE' })
}
