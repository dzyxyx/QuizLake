<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'

const route = useRoute()
const router = useRouter()

const roomCode = ref(String(route.params.code ?? '7K4X').toUpperCase())

interface Participant {
  name: string
  color: string
  meta: string
}

const participants = ref<Participant[]>([
  { name: 'Мария К.', color: '#2563eb', meta: '12 квизов · 3 победы' },
  { name: 'Даниил С.', color: '#3b82f6', meta: '30 квизов · 9 побед' },
  { name: 'Анна В.', color: '#2563eb', meta: '6 квизов · 1 победа' },
  { name: 'Игорь П.', color: '#60a5fa', meta: '18 квизов · 4 победы' },
  { name: 'Ольга Р.', color: '#2563eb', meta: '9 квизов · 2 победы' },
  { name: 'Семён Т.', color: '#f59e0b', meta: '4 квиза · 0 побед' },
  { name: 'Полина М.', color: '#2563eb', meta: '21 квиз · 6 побед' },
  { name: 'Артём Б.', color: '#3b82f6', meta: '15 квизов · 5 побед' },
  { name: 'Вера Н.', color: '#2563eb', meta: '3 квиза · 0 побед' },
  { name: 'Кирилл Д.', color: '#f59e0b', meta: '27 квизов · 8 побед' },
  { name: 'Юлия Ф.', color: '#2563eb', meta: '11 квизов · 2 победы' },
])

const extraCount = 3

function startQuiz() {
  router.push({ name: 'session-live', params: { code: roomCode.value } })
}
</script>

<template>
  <AppLayout active-item="active-quiz">
    <div class="layout-row">
      <div class="card code-card">
        <div class="code-label">Код комнаты</div>
        <div class="code-value">{{ roomCode }}</div>
        <div class="qr-box" />
        <p class="qr-hint">Отсканируйте QR-код или введите код на quizlake.ru/join</p>
      </div>

      <div class="card participants-card">
        <div class="participants-header">
          <h1>Участники ({{ participants.length + extraCount }})</h1>
          <span class="badge badge-success"><span class="dot" />Ожидание старта</span>
        </div>

        <div class="participants-grid">
          <div v-for="p in participants" :key="p.name" class="participant">
            <span class="avatar" :style="{ background: p.color }" />
            <div class="p-name">{{ p.name }}</div>
            <div class="p-meta">{{ p.meta }}</div>
          </div>
          <div class="participant extra">
            <span class="avatar extra-avatar" />
            <div class="p-name">+{{ extraCount }} ещё</div>
          </div>
        </div>

        <div class="start-row">
          <button class="btn btn-primary" @click="startQuiz">▶ НАЧАТЬ КВИЗ</button>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.layout-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.code-card {
  width: 300px;
  flex-shrink: 0;
  padding: 32px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.code-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}
.code-value {
  font-size: 42px;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin-bottom: 24px;
}
.qr-box {
  width: 140px;
  height: 140px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 20px;
}
.qr-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.participants-card {
  flex: 1;
  padding: 32px;
}
.participants-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}
.participants-header h1 {
  font-size: 20px;
  font-weight: 700;
}
.badge .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.participants-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}
.participant {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 6px;
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}
.p-name {
  font-size: 13px;
  font-weight: 700;
}
.p-meta {
  font-size: 11px;
  color: var(--color-text-secondary);
}
.extra-avatar {
  background: var(--color-border);
}
.extra .p-name {
  color: var(--color-text-secondary);
  font-weight: 600;
}

.start-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 28px;
}
</style>
