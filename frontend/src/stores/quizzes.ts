import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Quiz, QuizStatus } from '@/types'
import * as quizzesApi from '@/api/quizzes'

export const useQuizzesStore = defineStore('quizzes', () => {
  const quizzes = ref<Quiz[]>([])
  const loaded = ref(false)
  const loading = ref(false)

  const drafts = computed(() => quizzes.value.filter((q) => q.status === 'draft'))

  async function fetchMyQuizzes(force = false) {
    if (loaded.value && !force) return
    loading.value = true
    try {
      quizzes.value = await quizzesApi.listMyQuizzes()
      loaded.value = true
    } finally {
      loading.value = false
    }
  }

  async function getQuiz(quizId: number) {
    return quizzesApi.getQuiz(quizId)
  }

  async function createQuiz(data: quizzesApi.QuizPayload) {
    const quiz = await quizzesApi.createQuiz(data)
    quizzes.value.push(quiz)
    return quiz
  }

  async function updateQuiz(quizId: number, data: Partial<quizzesApi.QuizPayload & { status: QuizStatus }>) {
    const updated = await quizzesApi.updateQuiz(quizId, data)
    const idx = quizzes.value.findIndex((q) => q.id === quizId)
    if (idx !== -1) quizzes.value[idx] = updated
    return updated
  }

  async function deleteQuiz(quizId: number) {
    await quizzesApi.deleteQuiz(quizId)
    quizzes.value = quizzes.value.filter((q) => q.id !== quizId)
  }

  function reset() {
    quizzes.value = []
    loaded.value = false
  }

  return { quizzes, drafts, loading, fetchMyQuizzes, getQuiz, createQuiz, updateQuiz, deleteQuiz, reset }
})
