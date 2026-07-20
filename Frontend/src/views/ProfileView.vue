<script setup lang="ts">
import { onMounted } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useProfileStore } from '@/stores/profile'

const auth = useAuthStore()
const profile = useProfileStore()

onMounted(() => {
  profile.fetchAll()
})

const rankBadge: Record<number, string> = {
  1: 'badge-success',
  2: 'badge-info',
  3: 'badge-warning',
}

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}
</script>

<template>
  <AppLayout active-item="profile">
    <div class="layout-row">
      <div class="card profile-card">
        <span class="avatar-big" />
        <h1>{{ auth.user?.first_name }} {{ auth.user?.last_name }}</h1>
        <p class="since">@{{ auth.user?.nickname }}</p>

        <div class="stats-list">
          <div class="stat-row">
            <span>Сыграно квизов</span>
            <strong>{{ profile.stats.played }}</strong>
          </div>
          <div class="stat-row">
            <span>Побед</span>
            <strong>{{ profile.stats.wins }}</strong>
          </div>
          <div class="stat-row">
            <span>Создано квизов</span>
            <strong>{{ profile.stats.created }}</strong>
          </div>
          <div class="stat-row">
            <span>Средний результат</span>
            <strong>{{ profile.stats.avg_score_percent }}%</strong>
          </div>
        </div>

        <RouterLink to="/profile/edit" class="btn btn-secondary btn-block"
          >Редактировать профиль</RouterLink
        >
      </div>

      <div class="right-col">
        <div class="card list-card">
          <h2>История участия</h2>
          <div
            v-for="item in profile.participationHistory"
            :key="item.session_id"
            class="list-row"
          >
            <div>
              <div class="row-title">{{ item.quiz_title }}</div>
              <div class="row-meta">
                {{ formatDate(item.ended_at) }} · {{ item.participants_count }} участников
              </div>
            </div>
            <span
              v-if="item.final_rank"
              class="badge"
              :class="rankBadge[item.final_rank] ?? 'badge-info'"
            >
              🏅 {{ item.final_rank }} место
            </span>
          </div>
          <p v-if="!profile.participationHistory.length" class="empty-hint">
            Пока нет сыгранных квизов
          </p>
        </div>

        <div class="card list-card">
          <h2>Проведённые квизы</h2>
          <div v-for="item in profile.hostedHistory" :key="item.session_id" class="list-row">
            <div>
              <div class="row-title">{{ item.quiz_title }}</div>
              <div class="row-meta">
                {{ formatDate(item.ended_at) }} · {{ item.participants_count }} участников
              </div>
            </div>
            <RouterLink
              :to="{ name: 'session-results', params: { code: item.room_code } }"
              class="btn btn-primary small"
            >
              Показать итоги
            </RouterLink>
          </div>
          <p v-if="!profile.hostedHistory.length" class="empty-hint">Пока нет проведённых квизов</p>
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
.empty-hint {
  color: var(--color-text-secondary);
  font-size: 13px;
  padding: 8px 0;
}
</style>
