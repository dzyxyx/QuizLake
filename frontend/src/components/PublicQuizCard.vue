<script setup lang="ts">
import type { DiscoverSession } from '@/types'

const props = defineProps<{ session: DiscoverSession }>()
const emit = defineEmits<{ join: [roomCode: string] }>()

function timeLabel(session: DiscoverSession): string {
  if (session.status === 'active') return 'Идёт сейчас'
  if (!session.scheduled_start_at) return 'Ожидание участников'

  const diffMs = new Date(session.scheduled_start_at).getTime() - Date.now()
  const minutes = Math.round(diffMs / 60000)
  if (minutes <= 0) return 'Вот-вот начнётся'
  if (minutes < 60) return `Старт через ${minutes} мин`
  return `Старт через ${Math.round(minutes / 60)} ч`
}
</script>

<template>
  <div class="card quiz-card">
    <div class="top-row">
      <span class="badge badge-info">{{ session.category_name ?? 'Без категории' }}</span>
      <span class="badge" :class="session.status === 'active' ? 'badge-success' : 'badge-warning'">
        <span v-if="session.status === 'active'" class="dot" />
        <span v-else>⏱</span>
        {{ timeLabel(props.session) }}
      </span>
    </div>

    <h3 class="quiz-title">{{ session.title }}</h3>

    <div class="owner">
      <span class="owner-dot" />
      {{ session.owner_nickname }}
    </div>

    <p class="quiz-meta">{{ session.questions_count }} вопросов · {{ session.participants_count }} участников</p>

    <button class="btn btn-block btn-primary" @click="emit('join', session.room_code)">
      Присоединиться
    </button>
  </div>
</template>

<style scoped>
.quiz-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.badge .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}
.quiz-title {
  font-size: 17px;
  font-weight: 700;
  margin-top: 4px;
}
.owner {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}
.owner-dot {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary);
}
.quiz-meta {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-bottom: 4px;
}
</style>
