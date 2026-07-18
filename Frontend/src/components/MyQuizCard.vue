<script setup lang="ts">
import type { MyQuizCard } from '@/stores/quizzes'

defineProps<{ quiz: MyQuizCard }>()

const statusClass: Record<MyQuizCard['status'], string> = {
  ready: 'badge-success',
  draft: 'badge-warning',
  finished: 'badge-info',
}
</script>

<template>
  <div class="card quiz-card">
    <span class="badge" :class="statusClass[quiz.status]">
      <span class="dot" />
      {{ quiz.statusLabel }}
    </span>

    <h3 class="quiz-title">{{ quiz.title }}</h3>
    <p class="quiz-meta">{{ quiz.questionsCount }} вопросов · {{ quiz.meta }}</p>

    <div class="actions">
      <template v-if="quiz.status === 'finished'">
        <button class="btn btn-secondary">Результаты</button>
        <button class="btn btn-primary">Копия</button>
      </template>
      <template v-else>
        <button class="btn btn-secondary">Изменить</button>
        <button class="btn" :class="quiz.status === 'ready' ? 'btn-primary' : 'btn-secondary'">
          Запустить
        </button>
      </template>
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
