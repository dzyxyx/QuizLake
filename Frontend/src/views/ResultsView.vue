<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'

interface Podium {
  rank: number
  name: string
  score: number
  color: string
}

const podium: Podium[] = [
  { rank: 2, name: 'Даниил С.', score: 860, color: '#60a5fa' },
  { rank: 1, name: 'Мария К.', score: 980, color: '#f59e0b' },
  { rank: 3, name: 'Анна В.', score: 790, color: '#2563eb' },
]

const rest = [
  { rank: 4, name: 'Игорь П.', correct: '8 / 10', score: 720 },
  { rank: 5, name: 'Ольга Р.', correct: '7 / 10', score: 650 },
]
</script>

<template>
  <AppLayout active-item="active-quiz">
    <div class="results-page">
      <p class="eyebrow">История России: XX век · Завершён</p>
      <h1>Результаты квиза</h1>

      <div class="podium">
        <div
          v-for="p in podium"
          :key="p.rank"
          class="podium-slot"
          :class="{ winner: p.rank === 1, order2: p.rank === 2, order3: p.rank === 3 }"
        >
          <span class="avatar" :style="{ background: p.color }" />
          <div class="p-name">{{ p.name }}</div>
          <div class="p-score">{{ p.score }} очков</div>
          <div class="rank-box">
            <span v-if="p.rank === 1">🏆</span>
            {{ p.rank }}
          </div>
        </div>
      </div>

      <div class="card table-card">
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
            <tr v-for="r in rest" :key="r.rank">
              <td>{{ r.rank }}</td>
              <td>{{ r.name }}</td>
              <td>{{ r.correct }}</td>
              <td class="score-cell">{{ r.score }}</td>
            </tr>
          </tbody>
        </table>
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
