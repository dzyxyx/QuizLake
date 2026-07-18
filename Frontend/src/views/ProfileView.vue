<script setup lang="ts">
import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useQuizzesStore } from '@/stores/quizzes'

const auth = useAuthStore()
const quizzes = useQuizzesStore()

const rankBadge: Record<number, string> = {
  1: 'badge-success',
  2: 'badge-info',
  3: 'badge-warning',
}

const participationHistory = [
  { title: 'История России: XX век', date: '12 июля 2026', participants: 14, rank: 2 },
  { title: 'Мир кино: угадай кадр', date: '3 июля 2026', participants: 22, rank: 1 },
  { title: 'География: столицы мира', date: '28 июня 2026', participants: 9, rank: 4 },
  { title: 'Наука для всех', date: '15 июня 2026', participants: 17, rank: 3 },
]

const hostedQuizzes = [
  { title: 'История России: XX век', date: '22 июля 2025', participants: 18 },
  { title: 'Мир кино: угадай кадр', date: '3 июля 2026', participants: 22 },
  { title: 'География: столицы мира', date: '28 июня 2026', participants: 9 },
  { title: 'Наука для всех', date: '15 июня 2026', participants: 17 },
]
</script>

<template>
  <AppLayout active-item="profile">
    <div class="layout-row">
      <div class="card profile-card">
        <span class="avatar-big" />
        <h1>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</h1>
        <p class="since">С апреля 2025</p>

        <div class="stats-list">
          <div class="stat-row">
            <span>Сыграно квизов</span>
            <strong>{{ quizzes.stats.played }}</strong>
          </div>
          <div class="stat-row">
            <span>Побед</span>
            <strong>{{ quizzes.stats.wins }}</strong>
          </div>
          <div class="stat-row">
            <span>Создано квизов</span>
            <strong>{{ quizzes.stats.created }}</strong>
          </div>
          <div class="stat-row">
            <span>Средний результат</span>
            <strong>78%</strong>
          </div>
        </div>

        <RouterLink to="/profile/edit" class="btn btn-secondary btn-block"
          >Редактировать профиль</RouterLink
        >
      </div>

      <div class="right-col">
        <div class="card list-card">
          <h2>История участия</h2>
          <div v-for="item in participationHistory" :key="item.title" class="list-row">
            <div>
              <div class="row-title">{{ item.title }}</div>
              <div class="row-meta">{{ item.date }} · {{ item.participants }} участников</div>
            </div>
            <span class="badge" :class="rankBadge[item.rank] ?? 'badge-info'">
              🏅 {{ item.rank }} место
            </span>
          </div>
        </div>

        <div class="card list-card">
          <h2>Проведённые квизы</h2>
          <div v-for="item in hostedQuizzes" :key="item.title" class="list-row">
            <div>
              <div class="row-title">{{ item.title }}</div>
              <div class="row-meta">{{ item.date }} · {{ item.participants }} участников</div>
            </div>
            <button class="btn btn-primary small">Показать итоги</button>
          </div>
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

.profile-card {
  width: 270px;
  flex-shrink: 0;
  padding: 32px 24px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.avatar-big {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: var(--color-primary);
  margin-bottom: 12px;
}
.profile-card h1 {
  font-size: 18px;
  font-weight: 700;
}
.since {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-bottom: 20px;
}
.stats-list {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}
.stat-row strong {
  font-weight: 800;
}

.right-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.list-card {
  padding: 28px;
}
.list-card h2 {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 18px;
}
.list-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 0;
  border-top: 1px solid var(--color-border);
}
.list-row:first-of-type {
  border-top: none;
}
.row-title {
  font-size: 14px;
  font-weight: 700;
}
.row-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
  margin-top: 2px;
}
.btn.small {
  padding: 8px 16px;
  font-size: 12px;
}
</style>
