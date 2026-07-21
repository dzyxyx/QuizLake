<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useQuizzesStore } from '@/stores/quizzes'
import { useSessionStore } from '@/stores/session'
import { ApiError } from '@/api/client'

const props = withDefaults(
  defineProps<{
    activeItem?: 'active-quiz' | 'discover' | 'my-quizzes' | 'profile' | null
    activeDraftId?: number | null
  }>(),
  {
    activeItem: null,
    activeDraftId: null,
  },
)

const router = useRouter()
const auth = useAuthStore()
const quizzes = useQuizzesStore()
const sessionStore = useSessionStore()

const hasActiveSession = computed(() => {
  const status = sessionStore.session?.status
  return status === 'waiting' || status === 'active'
})

const activeSessionLink = computed(() => {
  const session = sessionStore.session
  if (!session) return '/join'
  switch (session.status) {
    case 'waiting':
      return `/session/${session.room_code}/waiting`
    case 'active':
      return `/session/${session.room_code}/live`
    case 'finished':
      return `/session/${session.room_code}/results`
    default:
      return '/'
  }
})

async function onLogout() {
  await auth.logout()
  router.push({ name: 'login' })
}

async function onDeleteDraft(quizId: number, title: string) {
  if (!window.confirm(`Удалить черновик «${title}»? Это действие необратимо.`)) return
  try {
    await quizzes.deleteQuiz(quizId)
  } catch (e) {
    window.alert(e instanceof ApiError ? e.message : 'Не удалось удалить черновик')
    return
  }
  if (props.activeDraftId === quizId) {
    router.push({ name: 'dashboard' })
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="logo">
      <span class="logo-dot" />
      <span class="logo-text">QuizLake</span>
    </div>

    <nav class="nav">
      <RouterLink
        :to="activeSessionLink"
        class="nav-item"
        :class="{ active: activeItem === 'active-quiz', live: hasActiveSession }"
      >
        <span class="nav-icon">▶</span>
        <span class="nav-label">Активный квиз</span>
        <span v-if="hasActiveSession" class="live-dot" />
      </RouterLink>

      <template v-if="auth.isAuthenticated">
        <RouterLink to="/discover" class="nav-item" :class="{ active: activeItem === 'discover' }">
          <span class="nav-icon">🔍</span>
          <span class="nav-label">Обзор</span>
        </RouterLink>

        <RouterLink to="/" class="nav-item" :class="{ active: activeItem === 'my-quizzes' }">
          <span class="nav-icon">▦</span>
          <span class="nav-label">Мои квизы</span>
        </RouterLink>

        <RouterLink to="/profile" class="nav-item" :class="{ active: activeItem === 'profile' }">
          <span class="nav-icon">👤</span>
          <span class="nav-label">Профиль</span>
        </RouterLink>
      </template>
    </nav>

    <div v-if="auth.isAuthenticated && quizzes.drafts.length" class="drafts">
      <div class="drafts-title">Черновики</div>
      <div v-for="draft in quizzes.drafts" :key="draft.id" class="draft-row">
        <RouterLink
          :to="`/quizzes/${draft.id}/questions`"
          class="draft-item"
          :class="{ active: draft.id === activeDraftId }"
        >
          <span class="draft-dot" />
          {{ draft.title }}
        </RouterLink>
        <button
          type="button"
          class="draft-delete-btn"
          title="Удалить черновик"
          @click="onDeleteDraft(draft.id, draft.title)"
        >
          ✕
        </button>
      </div>
    </div>

    <div class="spacer" />

    <div v-if="auth.isAuthenticated" class="user-row">
      <RouterLink to="/profile" class="user-card">
        <span class="user-avatar">{{ (auth.user?.first_name ?? 'М')[0] }}</span>
        <span class="user-info">
          <span class="user-name">{{ auth.user?.first_name }} {{ auth.user?.last_name?.[0] }}.</span>
          <span class="user-email">{{ auth.user?.email }}</span>
        </span>
      </RouterLink>
      <button type="button" class="logout-btn" title="Выйти из аккаунта" @click="onLogout">⎋</button>
    </div>
    <p v-else class="guest-hint">Вы играете как гость</p>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 250px;
  flex-shrink: 0;
  background: var(--color-card);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  padding: 24px 16px;
  min-height: 100vh;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 8px;
  margin-bottom: 28px;
}
.logo-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-primary);
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 10px;
  border-radius: var(--radius-sm);
  color: var(--color-text);
  font-size: 14px;
  font-weight: 500;
  position: relative;
}
.nav-item:hover {
  background: #f5f7fb;
}
.nav-item.active {
  background: var(--color-info-bg);
  color: var(--color-primary);
  font-weight: 600;
}
.nav-item.live {
  color: var(--color-success-text);
  background: var(--color-success-bg);
}
.nav-item.live.active {
  color: var(--color-primary);
  background: var(--color-info-bg);
}

.nav-icon {
  width: 18px;
  text-align: center;
  font-size: 14px;
}

.live-dot {
  margin-left: auto;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-success-text);
}

.drafts {
  margin-top: 24px;
}
.drafts-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  padding: 0 10px;
  margin-bottom: 8px;
}
.draft-row {
  display: flex;
  align-items: center;
  gap: 2px;
}
.draft-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  color: var(--color-text-secondary);
  flex: 1;
  min-width: 0;
}
.draft-item:hover {
  background: #f5f7fb;
}
.draft-delete-btn {
  width: 24px;
  height: 24px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--color-text-muted);
}
.draft-delete-btn:hover {
  background: var(--color-danger-bg);
  color: var(--color-danger-text);
}
.draft-item.active {
  background: var(--color-info-bg);
  color: var(--color-primary);
  font-weight: 600;
}
.draft-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  border: 1.5px solid var(--color-text-muted);
  flex-shrink: 0;
}
.draft-item.active .draft-dot {
  border-color: var(--color-primary);
}

.spacer {
  flex: 1;
}

.user-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
}
.user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: var(--radius-sm);
  flex: 1;
  min-width: 0;
}
.user-card:hover {
  background: #f5f7fb;
}
.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}
.user-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.user-name {
  font-size: 13px;
  font-weight: 700;
}
.user-email {
  font-size: 12px;
  color: var(--color-text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.logout-btn {
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: 16px;
}
.logout-btn:hover {
  background: var(--color-danger-bg);
  color: var(--color-danger-text);
}
.guest-hint {
  margin-top: 12px;
  padding: 8px;
  font-size: 12px;
  color: var(--color-text-muted);
  text-align: center;
}
</style>
