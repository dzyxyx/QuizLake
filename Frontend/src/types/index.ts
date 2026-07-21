export interface User {
  id: number
  first_name: string
  last_name: string
  nickname: string
  email: string
  avatar_url: string | null
}

export interface Category {
  id: number
  name: string
  slug: string
  icon: string | null
}

export type QuizDifficulty = 'easy' | 'medium' | 'hard'
export type QuizStatus = 'draft' | 'ready' | 'archived'

export interface Quiz {
  id: number
  owner_id: number
  category_id: number | null
  title: string
  description: string | null
  difficulty: QuizDifficulty
  time_per_question_sec: number
  speed_bonus_enabled: boolean
  show_correct_answer: boolean
  allow_answer_change: boolean
  is_public: boolean
  status: QuizStatus
  cover_image_url: string | null
}

export type QuestionType = 'single' | 'multiple'

export interface AnswerOption {
  id: number
  option_text: string
  is_correct: boolean
  order_index: number
}

export interface Question {
  id: number
  question_text: string
  image_url: string | null
  question_type: QuestionType
  order_index: number
  time_limit_sec: number | null
  points: number | null
  answer_options: AnswerOption[]
}

export type SessionStatus = 'waiting' | 'active' | 'finished' | 'cancelled'

export interface QuizSession {
  id: number
  quiz_id: number
  host_id: number
  room_code: string
  status: SessionStatus
  current_question_id: number | null
  current_question_started_at: string | null
  scheduled_start_at: string | null
  started_at: string | null
  ended_at: string | null
}

export interface SessionParticipant {
  id: number
  session_id: number
  user_id: number | null
  display_name: string
  avatar_url: string | null
  total_score: number
  correct_answers_count: number
  final_rank: number | null
  is_connected: boolean
  joined_at: string
  left_at: string | null
}

export interface AnswerResult {
  id: number
  session_id: number
  question_id: number
  participant_id: number
  selected_option_ids: number[]
  is_correct: boolean
  response_time_ms: number | null
  points_awarded: number
  answered_at: string
}

export interface DiscoverSession {
  session_id: number
  room_code: string
  quiz_id: number
  title: string
  category_name: string | null
  owner_nickname: string
  status: 'waiting' | 'active'
  scheduled_start_at: string | null
  questions_count: number
  participants_count: number
}

export interface UserStats {
  played: number
  wins: number
  created: number
  hosted_sessions_count: number
  avg_score_percent: number
}

export interface ParticipationHistoryItem {
  session_id: number
  room_code: string
  quiz_title: string
  ended_at: string | null
  participants_count: number
  final_rank: number | null
}

export interface HostedSessionHistoryItem {
  session_id: number
  room_code: string
  quiz_title: string
  ended_at: string | null
  participants_count: number
}

export interface OptionStat {
  option_id: number
  option_text: string
  is_correct: boolean
  selected_count: number
  selected_percent: number
}

export interface LeaderboardEntry {
  participant_id: number
  display_name: string
  total_score: number
  correct_answers_count: number
  final_rank?: number
}

export interface WsParticipantJoinedPayload {
  type: 'participant_joined'
  payload: SessionParticipant
}

export interface WsNewQuestionPayload {
  type: 'new_question'
  payload: Omit<Question, 'answer_options'> & {
    answer_options: Omit<AnswerOption, 'is_correct'>[]
  }
}

export interface WsParticipantAnsweredPayload {
  type: 'participant_answered'
  payload: { answered_count: number; total_participants: number }
}

export interface WsAnswerRevealedPayload {
  type: 'answer_revealed'
  payload: {
    question_id: number
    correct_option_ids: number[]
    option_stats: OptionStat[]
    leaderboard: LeaderboardEntry[]
  }
}

export interface WsGameEndedPayload {
  type: 'game_ended'
  payload: { leaderboard: LeaderboardEntry[] }
}

export interface WsParticipantLeftPayload {
  type: 'participant_left'
  payload: { participant_id: number }
}

export interface WsSessionCancelledPayload {
  type: 'session_cancelled'
  payload: Record<string, never>
}

export type WsMessage =
  | WsParticipantJoinedPayload
  | WsNewQuestionPayload
  | WsParticipantAnsweredPayload
  | WsAnswerRevealedPayload
  | WsGameEndedPayload
  | WsParticipantLeftPayload
  | WsSessionCancelledPayload
