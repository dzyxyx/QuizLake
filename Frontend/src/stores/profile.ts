import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { UserStats, ParticipationHistoryItem, HostedSessionHistoryItem } from '@/types'
import * as usersApi from '@/api/users'

export const useProfileStore = defineStore('profile', () => {
  const stats = ref<UserStats>({ played: 0, wins: 0, created: 0, avg_score_percent: 0 })
  const participationHistory = ref<ParticipationHistoryItem[]>([])
  const hostedHistory = ref<HostedSessionHistoryItem[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [statsData, participation, hosted] = await Promise.all([
        usersApi.getMyStats(),
        usersApi.getParticipationHistory(),
        usersApi.getHostedHistory(),
      ])
      stats.value = statsData
      participationHistory.value = participation
      hostedHistory.value = hosted
    } finally {
      loading.value = false
    }
  }

  return { stats, participationHistory, hostedHistory, loading, fetchAll }
})
