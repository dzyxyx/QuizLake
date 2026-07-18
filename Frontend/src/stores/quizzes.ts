import { defineStore } from 'pinia'
import { ref } from 'vue'

// Пока нет API — храним данные "как на макете" прямо в сторе.
// Later: эти данные будут приходить с бэкенда, а форма стора (поля) не изменится.

export interface MyQuizCard {
  id: number
  title: string
  status: 'ready' | 'draft' | 'finished'
  statusLabel: string
  questionsCount: number
  meta: string // "15 сек/вопрос" либо "128 участников"
}

export interface PublicQuizCard {
  id: number
  title: string
  category: string
  ownerName: string
  ownerColor: string
  liveState: 'live' | 'scheduled'
  liveLabel: string
  questionsCount: number
  participantsLabel: string
  actionLabel: string // "Присоединиться" | "Напомнить мне"
}

export interface DraftItem {
  id: number
  title: string
}

export const useQuizzesStore = defineStore('quizzes', () => {
  const stats = ref({
    played: 23,
    wins: 6,
    created: 8,
  })

  const myQuizzes = ref<MyQuizCard[]>([
    {
      id: 1,
      title: 'История России: XX век',
      status: 'ready',
      statusLabel: 'Готов к запуску',
      questionsCount: 12,
      meta: '15 сек/вопрос',
    },
    {
      id: 2,
      title: 'Мир кино: угадай кадр',
      status: 'draft',
      statusLabel: 'Черновик',
      questionsCount: 7,
      meta: '20 сек/вопрос',
    },
    {
      id: 3,
      title: 'География: столицы мира',
      status: 'finished',
      statusLabel: 'Проведён',
      questionsCount: 10,
      meta: '128 участников',
    },
  ])

  const drafts = ref<DraftItem[]>([
    { id: 1, title: 'История России: XX век' },
    { id: 2, title: 'Мир кино: угадай кадр' },
  ])

  const publicQuizzes = ref<PublicQuizCard[]>([
    {
      id: 1,
      title: 'Мир кино: угадай кадр',
      category: 'Кино и сериалы',
      ownerName: 'Даниил Соколов',
      ownerColor: '#3b82f6',
      liveState: 'live',
      liveLabel: 'Идёт сейчас',
      questionsCount: 7,
      participantsLabel: '18 участников',
      actionLabel: 'Присоединиться',
    },
    {
      id: 2,
      title: 'Флаги мира',
      category: 'География',
      ownerName: 'Анна Волкова',
      ownerColor: '#60a5fa',
      liveState: 'scheduled',
      liveLabel: 'Старт через 5 мин',
      questionsCount: 15,
      participantsLabel: '6 участников ожидают',
      actionLabel: 'Присоединиться',
    },
    {
      id: 3,
      title: 'IT и технологии 2026',
      category: 'Наука',
      ownerName: 'Игорь Петров',
      ownerColor: '#f59e0b',
      liveState: 'live',
      liveLabel: 'Идёт сейчас',
      questionsCount: 10,
      participantsLabel: '42 участника',
      actionLabel: 'Присоединиться',
    },
    {
      id: 4,
      title: 'Музыка 90-х',
      category: 'Музыка',
      ownerName: 'Ольга Р.',
      ownerColor: '#1d4ed8',
      liveState: 'scheduled',
      liveLabel: 'Старт через 20 мин',
      questionsCount: 12,
      participantsLabel: '3 участника ожидают',
      actionLabel: 'Напомнить мне',
    },
    {
      id: 5,
      title: 'Спортивные рекорды',
      category: 'Спорт',
      ownerName: 'Семён Т.',
      ownerColor: '#2563eb',
      liveState: 'live',
      liveLabel: 'Идёт сейчас',
      questionsCount: 9,
      participantsLabel: '9 участников',
      actionLabel: 'Присоединиться',
    },
    {
      id: 6,
      title: 'Литература XIX века',
      category: 'Литература',
      ownerName: 'Полина М.',
      ownerColor: '#3b82f6',
      liveState: 'scheduled',
      liveLabel: 'Старт через 1 час',
      questionsCount: 14,
      participantsLabel: 'пока нет участников',
      actionLabel: 'Напомнить мне',
    },
  ])

  return { stats, myQuizzes, drafts, publicQuizzes }
})
