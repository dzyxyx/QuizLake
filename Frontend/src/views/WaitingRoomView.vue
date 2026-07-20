<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { useSessionStore } from '@/stores/session'
import { ApiError } from '@/api/client'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()

const roomCode = String(route.params.code ?? '').toUpperCase()
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    await sessionStore.loadByRoomCode(roomCode)
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Комната не найдена'
  } finally {
    loading.value = false
  }
})

watch(
  () => sessionStore.currentQuestion,
  (question) => {
    if (question) {
      router.push({ name: 'session-live', params: { code: roomCode } })
    }
  },
)

watch(
  () => sessionStore.cancelled,
  (isCancelled) => {
    if (isCancelled && !sessionStore.isHost) {
      sessionStore.leave()
      router.push({ name: 'join' })
    }
  },
)

const participants = computed(() => sessionStore.participants)
const leaving = ref(false)

async function startQuiz() {
  error.value = ''
  try {
    await sessionStore.nextQuestion()
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось начать квиз'
  }
}

async function onLeave() {
  leaving.value = true
  const wasHost = sessionStore.isHost
  try {
    await sessionStore.leaveRoom()
    router.push(wasHost ? { name: 'dashboard' } : { name: 'join' })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось выйти из комнаты'
    leaving.value = false
  }
}
</script>

<template>
  <AppLayout active-item="active-quiz">
    <div v-if="loading">Загрузка…</div>
    <p v-else-if="error" class="error-text">{{ error }}</p>
    <div v-else class="layout-row">
      <div class="card code-card">
        <div class="code-label">Код комнаты</div>
        <div class="code-value">{{ roomCode }}</div>
        <div class="qr-box" />
        <p class="qr-hint">Назовите этот код или продиктуйте его участникам</p>
      </div>

      <div class="card participants-card">
        <div class="participants-header">
          <h1>Участники ({{ participants.length }})</h1>
          <div class="header-actions">
            <span class="badge badge-success"><span class="dot" />Ожидание старта</span>
            <button class="btn btn-secondary" :disabled="leaving" @click="onLeave">
              {{ sessionStore.isHost ? 'Отменить квиз' : 'Покинуть комнату' }}
            </button>
          </div>
        </div>

        <div v-if="participants.length" class="participants-grid">
          <div v-for="p in participants" :key="p.id" class="participant">
            <span class="avatar" />
            <div class="p-name">{{ p.display_name }}</div>
            <div class="p-meta">{{ p.total_score }} очков</div>
          </div>
        </div>
        <p v-else class="empty-hint">Пока никто не присоединился</p>

        <div v-if="sessionStore.isHost" class="start-row">
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
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
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
  background: var(--color-primary);
}
.p-name {
  font-size: 13px;
  font-weight: 700;
}
.p-meta {
  font-size: 11px;
  color: var(--color-text-secondary);
}

.start-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 28px;
}
.empty-hint {
  color: var(--color-text-secondary);
  font-size: 14px;
}
.error-text {
  color: var(--color-danger-text);
  font-size: 14px;
}
</style>
