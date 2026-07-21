<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import * as quizzesApi from '@/api/quizzes'
import type { LeaderboardEntry } from '@/types'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()
const auth = useAuthStore()

const roomCode = String(route.params.code ?? '').toUpperCase()
const quizTitle = ref('')
const loading = ref(true)

onMounted(async () => {
  if (!sessionStore.session || sessionStore.session.room_code !== roomCode || !sessionStore.finalLeaderboard) {
    await sessionStore.loadByRoomCode(roomCode)
  }

  if (sessionStore.session) {
    try {
      const quiz = await quizzesApi.getQuiz(sessionStore.session.quiz_id)
      quizTitle.value = quiz.title
    } catch {
      quizTitle.value = ''
    }
  }
  loading.value = false
})

const leaderboard = computed<LeaderboardEntry[]>(() => {
  if (sessionStore.finalLeaderboard) return sessionStore.finalLeaderboard
  return [...sessionStore.participants]
    .sort((a, b) => (a.final_rank ?? 999) - (b.final_rank ?? 999) || b.total_score - a.total_score)
    .map((p, i) => ({
      participant_id: p.id,
      display_name: p.display_name,
      total_score: p.total_score,
      correct_answers_count: p.correct_answers_count,
      final_rank: p.final_rank ?? i + 1,
    }))
})

const podium = computed(() => leaderboard.value.slice(0, 3))
const rest = computed(() => leaderboard.value.slice(3))

function onExit() {
  sessionStore.leave()
  router.push(auth.isAuthenticated ? { name: 'dashboard' } : { name: 'join' })
}
</script>

<template>
  <AppLayout active-item="active-quiz">
    <div v-if="loading">Загрузка…</div>
    <div v-else class="results-page">
      <p class="eyebrow">{{ quizTitle }} · Завершён</p>
      <h1>Результаты квиза</h1>

      <div class="podium">
        <div
          v-for="p in podium"
          :key="p.participant_id"
          class="podium-slot"
          :class="{
            winner: p.final_rank === 1,
            order2: p.final_rank === 2,
            order3: p.final_rank === 3,
          }"
        >
          <span class="avatar" />
          <div class="p-name">{{ p.display_name }}</div>
          <div class="p-score">{{ p.total_score }} очков</div>
          <div class="rank-box">
            <span v-if="p.final_rank === 1">🏆</span>
            {{ p.final_rank }}
          </div>
        </div>
      </div>

      <div v-if="rest.length" class="card table-card">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Участник</th>
              <th>Верных ответов</th>
              <th>Очки</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in rest" :key="r.participant_id">
              <td>{{ r.final_rank }}</td>
              <td>{{ r.display_name }}</td>
              <td>{{ r.correct_answers_count }}</td>
              <td class="score-cell">{{ r.total_score }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="exit-row">
        <button type="button" class="btn btn-primary" @click="onExit">Готово</button>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.results-page {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}
.eyebrow {
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}
h1 {
  font-size: 26px;
  font-weight: 700;
  margin-bottom: 40px;
}

.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 24px;
  margin-bottom: 40px;
}
.podium-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 130px;
}
.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--color-primary);
}
.p-name {
  font-weight: 700;
  font-size: 14px;
}
.p-score {
  font-size: 13px;
  color: var(--color-primary);
}
.rank-box {
  margin-top: 8px;
  width: 100%;
  height: 60px;
  background: #fff;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  box-shadow: var(--shadow-card);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-weight: 800;
  font-size: 18px;
}
.podium-slot.winner .rank-box {
  height: 90px;
  background: #fdf3d9;
}
.podium-slot.order2,
.podium-slot.order3 {
  padding-bottom: 30px;
}

.table-card {
  padding: 8px 0;
  text-align: left;
}
.exit-row {
  display: flex;
  justify-content: center;
  margin-top: 32px;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  text-align: left;
  padding: 16px 24px;
}
td {
  padding: 16px 24px;
  border-top: 1px solid var(--color-border);
  font-size: 14px;
}
.score-cell {
  font-weight: 700;
}
</style>
