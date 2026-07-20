<script setup lang="ts">
import type { Quiz } from '@/types'

defineProps<{ quiz: Quiz }>()

const emit = defineEmits<{
  edit: [quizId: number]
  publish: [quizId: number]
  launch: [quizId: number]
}>()

const statusLabel: Record<Quiz['status'], string> = {
  draft: 'Черновик',
  ready: 'Готов к запуску',
  archived: 'В архиве',
}
const statusClass: Record<Quiz['status'], string> = {
  draft: 'badge-warning',
  ready: 'badge-success',
  archived: 'badge-info',
}
</script>

<template>
  <div class="card quiz-card">
    <span class="badge" :class="statusClass[quiz.status]">
      <span class="dot" />
      {{ statusLabel[quiz.status] }}
    </span>

    <h3 class="quiz-title">{{ quiz.title }}</h3>
    <p class="quiz-meta">{{ quiz.time_per_question_sec }} сек/вопрос</p>

    <div class="actions">
      <button class="btn btn-secondary" @click="emit('edit', quiz.id)">Изменить</button>
      <button
        v-if="quiz.status === 'draft'"
        class="btn btn-primary"
        @click="emit('publish', quiz.id)"
      >
        Опубликовать
      </button>
      <button v-else-if="quiz.status === 'ready'" class="btn btn-primary" @click="emit('launch', quiz.id)">
        Запустить
      </button>
    </div>
  </div>
</template>

<style scoped>
.quiz-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
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
.quiz-meta {
  color: var(--color-text-secondary);
  font-size: 13px;
}
.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 8px;
}
.actions .btn {
  padding: 10px;
  font-size: 13px;
}
</style>
