import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import * as sessionsApi from '@/api/sessions'
import { useQuizSocket } from '@/composables/useQuizSocket'

vi.mock('@/api/sessions')
vi.mock('@/composables/useQuizSocket')

const baseSession = {
  id: 42,
  quiz_id: 1,
  host_id: 7,
  room_code: 'ABCD1234',
  status: 'waiting' as const,
  current_question_id: null,
  current_question_started_at: null,
  scheduled_start_at: null,
  started_at: null,
  ended_at: null,
}

function mockSocketFactory() {
  let capturedHandlers: any = null
  vi.mocked(useQuizSocket).mockImplementation((_sessionId, handlers) => {
    capturedHandlers = handlers
    return { connect: vi.fn(), disconnect: vi.fn(), connected: { value: false } as any }
  })
  return () => capturedHandlers
}

describe('session store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.mocked(sessionsApi.getSessionByCode).mockReset()
    vi.mocked(sessionsApi.getParticipants).mockReset()
    vi.mocked(sessionsApi.leaveSession).mockReset()
    vi.mocked(sessionsApi.cancelSession).mockReset()
    vi.mocked(sessionsApi.joinSession).mockReset()
    vi.mocked(useQuizSocket).mockReset()
  })

  it('stores the joined participant id in sessionStorage, not localStorage', async () => {
    mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])
    vi.mocked(sessionsApi.joinSession).mockResolvedValue({
      id: 5,
      session_id: 42,
      user_id: null,
      display_name: 'Alex',
      avatar_url: null,
      total_score: 0,
      correct_answers_count: 0,
      final_rank: null,
      is_connected: true,
      joined_at: '2026-07-20T00:00:00Z',
      left_at: null,
    })

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')
    await store.join('ABCD1234', 'Alex')

    expect(store.myParticipantId).toBe(5)
    expect(sessionStorage.getItem('quizlake_participant_42')).toBe('5')
    expect(localStorage.getItem('quizlake_participant_42')).toBeNull()
  })

  it('forwards useAuth=false to joinSession when the caller explicitly requests a guest join', async () => {
    mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])
    vi.mocked(sessionsApi.joinSession).mockResolvedValue({
      id: 9,
      session_id: 42,
      user_id: null,
      display_name: 'Guest',
      avatar_url: null,
      total_score: 0,
      correct_answers_count: 0,
      final_rank: null,
      is_connected: true,
      joined_at: '2026-07-20T00:00:00Z',
      left_at: null,
    })

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')
    await store.join('ABCD1234', 'Guest', false)

    expect(sessionsApi.joinSession).toHaveBeenCalledWith(
      'ABCD1234',
      { display_name: 'Guest' },
      false,
    )
  })

  it('loads a session by room code and connects the socket', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    expect(store.session).toEqual(baseSession)
    expect(store.participants).toEqual([])
    expect(getHandlers()).not.toBeNull()
  })

  it('appends a new participant on participant_joined', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    const participant = {
      id: 1,
      session_id: 42,
      user_id: null,
      display_name: 'Alex',
      avatar_url: null,
      total_score: 0,
      correct_answers_count: 0,
      final_rank: null,
      is_connected: true,
      joined_at: '2026-07-20T00:00:00Z',
      left_at: null,
    }
    getHandlers().participant_joined(participant)

    expect(store.participants).toHaveLength(1)
    expect(store.participants[0].display_name).toBe('Alex')
  })

  it('removes a participant on participant_left', async () => {
    const getHandlers = mockSocketFactory()
    const existing = {
      id: 1,
      session_id: 42,
      user_id: null,
      display_name: 'Alex',
      avatar_url: null,
      total_score: 0,
      correct_answers_count: 0,
      final_rank: null,
      is_connected: true,
      joined_at: '2026-07-20T00:00:00Z',
      left_at: null,
    }
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([existing])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')
    expect(store.participants).toHaveLength(1)

    getHandlers().participant_left({ participant_id: 1 })

    expect(store.participants).toHaveLength(0)
  })

  it('marks the session cancelled on session_cancelled', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    getHandlers().session_cancelled({})

    expect(store.cancelled).toBe(true)
    expect(store.session?.status).toBe('cancelled')
  })

  it('tracks the active question and resets per-question state on new_question', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    const question = {
      id: 1,
      question_text: '2+2?',
      image_url: null,
      question_type: 'single' as const,
      order_index: 1,
      time_limit_sec: 30,
      points: 100,
      answer_options: [{ id: 1, option_text: '4', order_index: 1 }],
    }
    getHandlers().new_question(question)

    expect(store.currentQuestion).toEqual(question)
    expect(store.session?.status).toBe('active')
    expect(store.answeredCount).toBeNull()
    expect(store.reveal).toBeNull()
  })

  it('updates answeredCount on participant_answered', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    getHandlers().participant_answered({ answered_count: 3, total_participants: 5 })

    expect(store.answeredCount).toEqual({ answered: 3, total: 5 })
  })

  it('stores the reveal payload on answer_revealed', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    const revealPayload = {
      question_id: 1,
      correct_option_ids: [1],
      option_stats: [],
      leaderboard: [],
    }
    getHandlers().answer_revealed(revealPayload)

    expect(store.reveal).toEqual(revealPayload)
  })

  it('stores the final leaderboard and marks the session finished on game_ended', async () => {
    const getHandlers = mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')

    const leaderboard = [
      { participant_id: 1, display_name: 'Alex', total_score: 100, correct_answers_count: 1, final_rank: 1 },
    ]
    getHandlers().game_ended({ leaderboard })

    expect(store.finalLeaderboard).toEqual(leaderboard)
    expect(store.session?.status).toBe('finished')
  })

  it('isHost is true only when the logged-in user owns the session', async () => {
    mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])

    const store = useSessionStore()
    const auth = useAuthStore()
    await store.loadByRoomCode('ABCD1234')

    expect(store.isHost).toBe(false)

    auth.user = { id: 7, first_name: 'Host', last_name: 'X', nickname: 'host', email: 'h@x.com', avatar_url: null }
    expect(store.isHost).toBe(true)
  })

  it('leaveRoom cancels the session when the current user is the host', async () => {
    mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])
    vi.mocked(sessionsApi.cancelSession).mockResolvedValue(undefined)

    const store = useSessionStore()
    const auth = useAuthStore()
    auth.user = { id: 7, first_name: 'Host', last_name: 'X', nickname: 'host', email: 'h@x.com', avatar_url: null }
    await store.loadByRoomCode('ABCD1234')

    await store.leaveRoom()

    expect(sessionsApi.cancelSession).toHaveBeenCalledWith(42)
    expect(sessionsApi.leaveSession).not.toHaveBeenCalled()
    expect(store.session).toBeNull()
  })

  it('leaveRoom leaves as a participant when the current user is not the host', async () => {
    mockSocketFactory()
    vi.mocked(sessionsApi.getSessionByCode).mockResolvedValue(baseSession)
    vi.mocked(sessionsApi.getParticipants).mockResolvedValue([])
    vi.mocked(sessionsApi.leaveSession).mockResolvedValue(undefined)

    const store = useSessionStore()
    await store.loadByRoomCode('ABCD1234')
    ;(store as any).myParticipantId = 99

    await store.leaveRoom()

    expect(sessionsApi.leaveSession).toHaveBeenCalledWith(42, 99)
    expect(sessionsApi.cancelSession).not.toHaveBeenCalled()
    expect(store.session).toBeNull()
  })
})
