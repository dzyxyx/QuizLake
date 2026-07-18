<script setup lang="ts">
import { ref } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import PublicQuizCard from '@/components/PublicQuizCard.vue'
import { useQuizzesStore } from '@/stores/quizzes'

const quizzes = useQuizzesStore()
const search = ref('')
const category = ref('Все категории')
</script>

<template>
  <AppLayout active-item="discover">
    <header class="page-header">
      <h1>Публичные квизы</h1>
      <p class="subtitle">Присоединяйтесь к квизам, которые сейчас идут или скоро начнутся</p>
    </header>

    <div class="filters">
      <input
        v-model="search"
        type="text"
        class="search-input"
        placeholder="Найти квиз или организатора"
      />
      <select v-model="category" class="category-select">
        <option>Все категории</option>
      </select>
      <RouterLink to="/join" class="btn btn-secondary">🔑 Войти по коду</RouterLink>
    </div>

    <section class="quiz-grid">
      <PublicQuizCard v-for="q in quizzes.publicQuizzes" :key="q.id" :quiz="q" />
    </section>
  </AppLayout>
</template>

<style scoped>
.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  font-size: 24px;
  font-weight: 700;
}
.subtitle {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-top: 6px;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
}
.search-input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
  background: #fff;
}
.search-input:focus {
  border-color: var(--color-primary);
}
.category-select {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 14px;
  background: #fff;
  outline: none;
  min-width: 180px;
}

.quiz-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
</style>
