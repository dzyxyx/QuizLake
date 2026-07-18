<script setup lang="ts">
import type { PublicQuizCard } from '@/stores/quizzes'

defineProps<{ quiz: PublicQuizCard }>()
</script>

<template>
  <div class="card quiz-card">
    <div class="top-row">
      <span class="badge badge-info">{{ quiz.category }}</span>
      <span class="badge" :class="quiz.liveState === 'live' ? 'badge-success' : 'badge-warning'">
        <span v-if="quiz.liveState === 'live'" class="dot" />
        <span v-else>⏱</span>
        {{ quiz.liveLabel }}
      </span>
    </div>

    <h3 class="quiz-title">{{ quiz.title }}</h3>

    <div class="owner">
      <span class="owner-dot" :style="{ background: quiz.ownerColor }" />
      {{ quiz.ownerName }}
    </div>

    <p class="quiz-meta">{{ quiz.questionsCount }} вопросов · {{ quiz.participantsLabel }}</p>

    <button
      class="btn btn-block"
      :class="quiz.actionLabel === 'Присоединиться' ? 'btn-primary' : 'btn-secondary'"
    >
      {{ quiz.actionLabel }}
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
}
.quiz-meta {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-bottom: 4px;
}
</style>
