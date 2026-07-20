<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import MyQuizCard from '@/components/MyQuizCard.vue'
import { useAuthStore } from '@/stores/auth'
import { useQuizzesStore } from '@/stores/quizzes'
import { useProfileStore } from '@/stores/profile'
import { useSessionStore } from '@/stores/session'

const router = useRouter()
const auth = useAuthStore()
const quizzes = useQuizzesStore()
const profile = useProfileStore()
const sessionStore = useSessionStore()

onMounted(() => {
  quizzes.fetchMyQuizzes()
  profile.fetchAll()
})

function onEdit(quizId: number) {
  router.push({ name: 'quiz-edit-settings', params: { id: quizId } })
}

async function onPublish(quizId: number) {
  await quizzes.updateQuiz(quizId, { status: 'ready' })
}

async function onLaunch(quizId: number) {
  const session = await sessionStore.createAndEnter(quizId)
  router.push({ name: 'session-waiting', params: { code: session.room_code } })
}
</script>

<template>
  <AppLayout active-item="my-quizzes">
    <header class="page-header">
      <div>
        <h1>С возвращением, {{ auth.user?.first_name }} 👋</h1>
        <p class="subtitle">
          {{ profile.stats.created }} созданных квизов · {{ profile.stats.played }} сыгранных
        </p>
      </div>
      <div class="header-actions">
        <RouterLink to="/join" class="btn btn-secondary">🔑 Войти по коду</RouterLink>
        <RouterLink to="/quizzes/create" class="btn btn-primary">+ СОЗДАТЬ КВИЗ</RouterLink>
      </div>
    </header>

    <section class="stats">
      <div class="card stat-card">
        <div class="stat-label">Сыграно квизов</div>
        <div class="stat-value">{{ profile.stats.played }}</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">Побед</div>
        <div class="stat-value">{{ profile.stats.wins }}</div>
      </div>
      <div class="card stat-card">
        <div class="stat-label">Создано квизов</div>
        <div class="stat-value">{{ profile.stats.created }}</div>
      </div>
    </section>

    <h2 class="section-title">Мои квизы</h2>
    <section v-if="quizzes.quizzes.length" class="quiz-grid">
      <MyQuizCard
        v-for="q in quizzes.quizzes"
        :key="q.id"
        :quiz="q"
        @edit="onEdit"
        @publish="onPublish"
        @launch="onLaunch"
      />
    </section>
    <p v-else class="empty-hint">Пока нет ни одного квиза — создайте первый.</p>
  </AppLayout>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 28px;
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
.header-actions {
  display: flex;
  gap: 12px;
}

.stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}
.stat-card {
  padding: 20px 24px;
}
.stat-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 10px;
}
.stat-value {
  font-size: 26px;
  font-weight: 800;
}

.section-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 16px;
}

.quiz-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.empty-hint {
  color: var(--color-text-secondary);
  font-size: 14px;
}
</style>
