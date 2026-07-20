import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DiscoverSession } from '@/types'
import * as quizzesApi from '@/api/quizzes'

export const useDiscoverStore = defineStore('discover', () => {
  const sessions = ref<DiscoverSession[]>([])
  const loading = ref(false)

  async function fetchSessions() {
    loading.value = true
    try {
      sessions.value = await quizzesApi.listDiscoverSessions()
    } finally {
      loading.value = false
    }
  }

  return { sessions, loading, fetchSessions }
})
