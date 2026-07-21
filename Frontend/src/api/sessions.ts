import { apiRequest } from '@/api/client'
import type { AnswerResult, Question, QuizSession, SessionParticipant } from '@/types'

export function createSession(quizId: number, scheduledStartAt?: string | null) {
  return apiRequest<QuizSession>(`/quizzes/${quizId}/sessions`, {
    method: 'POST',
    body: { scheduled_start_at: scheduledStartAt ?? null },
  })
}

export function getSessionByCode(roomCode: string) {
  return apiRequest<QuizSession>(`/sessions/${roomCode}`, { auth: false })
}

export interface JoinPayload {
  display_name: string
  avatar_url?: string | null
}

export function joinSession(roomCode: string, data: JoinPayload, useAuth = true) {
  return apiRequest<SessionParticipant>(`/sessions/${roomCode}/join`, {
    method: 'POST',
    body: data,
    auth: useAuth,
  })
}

export function getParticipants(sessionId: number) {
  return apiRequest<SessionParticipant[]>(`/sessions/${sessionId}/participants`, { auth: false })
}

export function leaveSession(sessionId: number, participantId: number) {
  return apiRequest<void>(`/sessions/${sessionId}/participants/${participantId}`, {
    method: 'DELETE',
    auth: false,
  })
}

export function cancelSession(sessionId: number) {
  return apiRequest<void>(`/sessions/${sessionId}`, { method: 'DELETE' })
}

export function nextQuestion(sessionId: number) {
  return apiRequest<Question>(`/sessions/${sessionId}/next-question`, { method: 'POST' })
}

export function submitAnswer(sessionId: number, participantId: number, selectedOptionIds: number[]) {
  return apiRequest<AnswerResult>(`/sessions/${sessionId}/participants/${participantId}/submit-answer`, {
    method: 'POST',
    body: { selected_option_ids: selectedOptionIds },
  })
}

export function revealAnswer(sessionId: number) {
  return apiRequest(`/sessions/${sessionId}/reveal-answer`, { method: 'POST' })
}

export function endGame(sessionId: number) {
  return apiRequest(`/sessions/${sessionId}/end-game`, { method: 'POST' })
}
