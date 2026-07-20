import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { QuizSession, SessionParticipant, WsNewQuestionPayload, WsAnswerRevealedPayload, LeaderboardEntry } from '@/types'
import * as sessionsApi from '@/api/sessions'
import { useQuizSocket } from '@/composables/useQuizSocket'
import { useAuthStore } from '@/stores/auth'

function participantStorageKey(sessionId: number) {
  return `quizlake_participant_${sessionId}`
}

export const useSessionStore = defineStore('session', () => {
  const session = ref<QuizSession | null>(null)
  const participants = ref<SessionParticipant[]>([])
  const myParticipantId = ref<number | null>(null)

  const currentQuestion = ref<WsNewQuestionPayload['payload'] | null>(null)
  const questionStartedAt = ref<string | null>(null)
  const answeredCount = ref<{ answered: number; total: number } | null>(null)
  const reveal = ref<WsAnswerRevealedPayload['payload'] | null>(null)
  const finalLeaderboard = ref<LeaderboardEntry[] | null>(null)
  const cancelled = ref(false)

  let socketHandle: ReturnType<typeof useQuizSocket> | null = null

  const isHost = computed(() => {
    const auth = useAuthStore()
    return !!session.value && !!auth.user && session.value.host_id === auth.user.id
  })

  function resetGameState() {
    currentQuestion.value = null
    questionStartedAt.value = null
    answeredCount.value = null
    reveal.value = null
    finalLeaderboard.value = null
    cancelled.value = false
  }

  function connectSocket() {
    if (!session.value) return
    disconnectSocket()
    socketHandle = useQuizSocket(session.value.id, {
      participant_joined: (payload) => {
        const idx = participants.value.findIndex((p) => p.id === payload.id)
        if (idx === -1) participants.value.push(payload)
        else participants.value[idx] = payload
      },
      participant_left: (payload) => {
        participants.value = participants.value.filter((p) => p.id !== payload.participant_id)
      },
      session_cancelled: () => {
        cancelled.value = true
        if (session.value) session.value.status = 'cancelled'
      },
      new_question: (payload) => {
        currentQuestion.value = payload
        questionStartedAt.value = new Date().toISOString()
        answeredCount.value = null
        reveal.value = null
        if (session.value) session.value.status = 'active'
      },
      participant_answered: (payload) => {
        answeredCount.value = { answered: payload.answered_count, total: payload.total_participants }
      },
      answer_revealed: (payload) => {
        reveal.value = payload
      },
      game_ended: (payload) => {
        finalLeaderboard.value = payload.leaderboard
        if (session.value) session.value.status = 'finished'
      },
    })
    socketHandle.connect()
  }

  function disconnectSocket() {
    socketHandle?.disconnect()
    socketHandle = null
  }

  async function loadByRoomCode(roomCode: string) {
    session.value = await sessionsApi.getSessionByCode(roomCode)
    participants.value = await sessionsApi.getParticipants(session.value.id)
    resetGameState()

    const stored = localStorage.getItem(participantStorageKey(session.value.id))
    myParticipantId.value = stored ? Number(stored) : null

    connectSocket()
    return session.value
  }

  async function createAndEnter(quizId: number) {
    session.value = await sessionsApi.createSession(quizId)
    participants.value = []
    myParticipantId.value = null
    resetGameState()
    connectSocket()
    return session.value
  }

  async function join(roomCode: string, displayName: string) {
    const participant = await sessionsApi.joinSession(roomCode, { display_name: displayName })
    myParticipantId.value = participant.id
    if (session.value) {
      localStorage.setItem(participantStorageKey(session.value.id), String(participant.id))
    }
    return participant
  }

  async function nextQuestion() {
    if (!session.value) return
    await sessionsApi.nextQuestion(session.value.id)
  }

  async function submitAnswer(selectedOptionIds: number[]) {
    if (!session.value || myParticipantId.value === null) return null
    return sessionsApi.submitAnswer(session.value.id, myParticipantId.value, selectedOptionIds)
  }

  async function revealAnswer() {
    if (!session.value) return
    await sessionsApi.revealAnswer(session.value.id)
  }

  async function endGame() {
    if (!session.value) return
    await sessionsApi.endGame(session.value.id)
  }

  function leave() {
    disconnectSocket()
    session.value = null
    participants.value = []
    myParticipantId.value = null
    resetGameState()
  }

  async function leaveRoom() {
    if (!session.value) return

    if (isHost.value) {
      await sessionsApi.cancelSession(session.value.id)
    } else if (myParticipantId.value !== null) {
      await sessionsApi.leaveSession(session.value.id, myParticipantId.value)
      localStorage.removeItem(participantStorageKey(session.value.id))
    }

    leave()
  }

  return {
    session,
    participants,
    myParticipantId,
    currentQuestion,
    questionStartedAt,
    answeredCount,
    reveal,
    finalLeaderboard,
    cancelled,
    isHost,
    loadByRoomCode,
    createAndEnter,
    join,
    nextQuestion,
    submitAnswer,
    revealAnswer,
    endGame,
    leave,
    leaveRoom,
  }
})
