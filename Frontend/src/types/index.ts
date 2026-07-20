// Типы сущностей, повторяющие схему БД

export interface User {
  id: number
  first_name: string
  last_name: string
  nickname: string | null
  email: string
  avatar_url: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Category {
  id: number
  name: string
  slug: string
  icon: string | null
}

export type QuizDifficulty = 'easy' | 'medium' | 'hard'
export type QuizStatus = 'draft' | 'ready' | 'active' | 'finished'

export interface Quiz {
  id: number
  owner_id: number
  category_id: number | null
  title: string
  description: string | null
  difficulty: QuizDifficulty
  time_per_question_sec: number
  points_per_correct: number
  speed_bonus_enabled: boolean
  show_correct_answer: boolean
  allow_answer_change: boolean
  is_public: boolean
  status: QuizStatus
  cover_image_url: string | null
  created_at: string
  updated_at: string
}

export type QuestionType = 'single' | 'multiple' | 'text'

export interface Question {
  id: number
  quiz_id: number
  question_text: string
  image_url: string | null
  question_type: QuestionType
  order_index: number
  time_limit_sec: number
  points: number
}

export interface AnswerOption {
  id: number
  question_id: number
  option_text: string
  is_correct: boolean
  order_index: number
}

export type SessionStatus = 'waiting' | 'live' | 'finished'

export interface QuizSession {
  id: number
  quiz_id: number
  host_id: number
  room_code: string
  status: SessionStatus
  current_question_id: number | null
  current_question_started_at: string | null
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
}

export interface ParticipantAnswer {
  id: number
  session_id: number
  question_id: number
  participant_id: number
  is_correct: boolean | null
  response_time_ms: number | null
  points_awarded: number
  answered_at: string
}
