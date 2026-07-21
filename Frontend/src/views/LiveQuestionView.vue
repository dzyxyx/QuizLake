<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSessionStore } from '@/stores/session'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'
import type { AnswerResult } from '@/types'

const route = useRoute()
const router = useRouter()
const sessionStore = useSessionStore()
const auth = useAuthStore()

const roomCode = String(route.params.code ?? '').toUpperCase()

const selectedOptionIds = ref<number[]>([])
const hasAnswered = ref(false)
const lastAnswerResult = ref<AnswerResult | null>(null)
const submitError = ref('')
const nextError = ref('')

onMounted(async () => {
  let session = sessionStore.session
  if (!session || session.room_code !== roomCode) {
    session = await sessionStore.loadByRoomCode(roomCode)
  }

  if (session.status === 'finished') {
    router.replace({ name: 'session-results', params: { code: roomCode } })
    return
  }
  if (session.status === 'waiting') {
    router.replace({ name: 'session-waiting', params: { code: roomCode } })
    return
  }
  if (session.status === 'cancelled') {
    sessionStore.leave()
    router.replace({ name: 'join' })
  }
})

const now = ref(Date.now())
let tickTimer: number | undefined
onMounted(() => {
  tickTimer = window.setInterval(() => {
    now.value = Date.now()
  }, 500)
})
onUnmounted(() => {
  if (tickTimer) window.clearInterval(tickTimer)
})

const question = computed(() => sessionStore.currentQuestion)

const secondsLeft = computed(() => {
  const q = question.value
  if (!q || q.time_limit_sec == null || !sessionStore.questionStartedAt) return null
  const elapsed = (now.value - new Date(sessionStore.questionStartedAt).getTime()) / 1000
  return Math.max(0, Math.ceil(q.time_limit_sec - elapsed))
})

const optionLabels = ['A', 'B', 'C', 'D', 'E', 'F']

function optionStat(optionId: number) {
  return sessionStore.reveal?.option_stats.find((s) => s.option_id === optionId) ?? null
}

function isCorrectOption(optionId: number) {
  return sessionStore.reveal?.correct_option_ids.includes(optionId) ?? false
}

function toggleOption(optionId: number) {
  if (hasAnswered.value || sessionStore.reveal || !question.value) return

  if (question.value.question_type === 'single') {
    selectedOptionIds.value = [optionId]
    submitSelected()
    return
  }

  const idx = selectedOptionIds.value.indexOf(optionId)
  if (idx === -1) selectedOptionIds.value.push(optionId)
  else selectedOptionIds.value.splice(idx, 1)
}

async function submitSelected() {
  if (selectedOptionIds.value.length === 0) return
  submitError.value = ''
  try {
    lastAnswerResult.value = await sessionStore.submitAnswer(selectedOptionIds.value)
    hasAnswered.value = true
  } catch (e) {
    submitError.value = e instanceof ApiError ? e.message : 'Не удалось отправить ответ'
  }
}

watch(question, () => {
  selectedOptionIds.value = []
  hasAnswered.value = false
  lastAnswerResult.value = null
  submitError.value = ''
  nextError.value = ''
})

watch(secondsLeft, (value) => {
  if (sessionStore.isHost && value === 0 && !sessionStore.reveal) {
    sessionStore.revealAnswer().catch(() => {})
  }
})

watch(
  () => sessionStore.finalLeaderboard,
  (leaderboard) => {
    if (leaderboard) {
      router.push({ name: 'session-results', params: { code: roomCode } })
    }
  },
)

async function onReveal() {
  await sessionStore.revealAnswer()
}

async function onNext() {
  nextError.value = ''
  try {
    await sessionStore.nextQuestion()
  } catch (e) {
    nextError.value =
      e instanceof ApiError && e.status === 400
        ? 'Вопросы закончились — нажмите «Завершить игру»'
        : 'Не удалось перейти к следующему вопросу'
  }
}

async function onEndGame() {
  await sessionStore.endGame()
}

const myIdentityLabel = computed(() => {
  if (sessionStore.isHost) return auth.user?.nickname ?? null
  const me = sessionStore.participants.find((p) => p.id === sessionStore.myParticipantId)
  return me?.display_name ?? null
})

function close() {
  sessionStore.leave()
  router.push(auth.isAuthenticated ? { name: 'dashboard' } : { name: 'login' })
}
</script>

<template>
  <div class="live-page">
    <aside class="side-strip">
      <span class="logo-dot" />
      <button class="close-btn" @click="close">✕</button>
    </aside>

    <main class="live-content">
      <div v-if="myIdentityLabel" class="identity-strip">
        Вы в этой вкладке: <strong>{{ myIdentityLabel }}</strong>
      </div>
      <div v-if="!question">Ожидаем вопрос…</div>
      <template v-else>
        <div class="top-row">
          <span class="badge badge-info">Вопрос {{ question.order_index }}</span>

          <div v-if="secondsLeft !== null && !sessionStore.reveal" class="timer-circle">
            {{ String(secondsLeft).padStart(2, '0') }}
          </div>
          <span v-else-if="sessionStore.reveal" class="badge badge-success">Ответ показан</span>

          <span v-if="sessionStore.answeredCount" class="badge badge-warning">
            Ответили: {{ sessionStore.answeredCount.answered }} / {{ sessionStore.answeredCount.total }}
          </span>
        </div>

        <div class="card question-card">
          <h1>{{ question.question_text }}</h1>

          <img v-if="question.image_url" :src="question.image_url" class="question-image" alt="" />

          <div class="options" :class="{ revealed: sessionStore.reveal }">
            <button
              v-for="(opt, i) in question.answer_options"
              :key="opt.id"
              class="option"
              :class="{
                selected: !sessionStore.reveal && selectedOptionIds.includes(opt.id),
                correct: sessionStore.reveal && isCorrectOption(opt.id),
                wrong:
                  sessionStore.reveal && !isCorrectOption(opt.id) && selectedOptionIds.includes(opt.id),
              }"
              :disabled="sessionStore.isHost || hasAnswered || !!sessionStore.reveal"
              @click="toggleOption(opt.id)"
            >
              <div
                v-if="sessionStore.reveal"
                class="fill-bar"
                :style="{ width: (optionStat(opt.id)?.selected_percent ?? 0) + '%' }"
              />
              <span class="option-content">
                <span class="option-label">
                  <span v-if="sessionStore.reveal && isCorrectOption(opt.id)">✓</span>
                  {{ optionLabels[i] }} · {{ opt.option_text }}
                </span>
                <span v-if="sessionStore.reveal && selectedOptionIds.includes(opt.id)" class="your-answer-badge">
                  ✓ Ваш ответ
                </span>
              </span>
              <span v-if="sessionStore.reveal" class="percent">{{ optionStat(opt.id)?.selected_percent ?? 0 }}%</span>
            </button>
          </div>

          <button
            v-if="question.question_type === 'multiple' && !hasAnswered && !sessionStore.reveal && !sessionStore.isHost"
            class="btn btn-primary btn-block"
            @click="submitSelected"
          >
            Ответить
          </button>

          <p v-if="submitError" class="error-text">{{ submitError }}</p>

          <p v-if="!sessionStore.reveal && hasAnswered" class="footer-hint">
            Ответ принят — ожидайте окончания времени на вопрос
          </p>
          <p v-else-if="!sessionStore.reveal && !hasAnswered && !sessionStore.isHost" class="footer-hint">
            Выберите ответ
          </p>
        </div>

        <div v-if="lastAnswerResult && sessionStore.reveal" class="score-toast">
          <span class="score-icon">{{ lastAnswerResult.is_correct ? '✓' : '✕' }}</span>
          <div>
            <div class="score-value">+{{ lastAnswerResult.points_awarded }} очков</div>
            <div class="score-label">{{ lastAnswerResult.is_correct ? 'Ответ верный!' : 'Ответ неверный' }}</div>
          </div>
        </div>

        <div v-if="sessionStore.isHost" class="host-controls">
          <button v-if="!sessionStore.reveal" class="btn btn-secondary" @click="onReveal">
            Показать ответ
          </button>
          <template v-else>
            <button class="btn btn-secondary" @click="onNext">Следующий вопрос</button>
            <button class="btn btn-primary" @click="onEndGame">Завершить игру</button>
          </template>
          <p v-if="nextError" class="error-text">{{ nextError }}</p>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.live-page {
  display: flex;
  min-height: 100vh;
}
.side-strip {
  width: 60px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}
.logo-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-primary);
}
.close-btn {
  margin-top: auto;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border);
  color: var(--color-text-secondary);
}
.close-btn:hover {
  background: #f5f7fb;
}

.live-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px;
  position: relative;
}

.identity-strip {
  width: 100%;
  max-width: 820px;
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: right;
  margin-bottom: 8px;
}

.top-row {
  width: 100%;
  max-width: 820px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 28px;
}

.timer-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
}

.question-card {
  width: 100%;
  max-width: 820px;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.question-card h1 {
  font-size: 20px;
  font-weight: 700;
  text-align: center;
}
.question-image {
  max-height: 220px;
  width: 100%;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

.options {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}
.option {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 16px 18px;
  text-align: left;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fff;
}
.option:disabled {
  cursor: default;
}
.option.selected {
  border-color: var(--color-primary);
}
.option.correct {
  border-color: var(--color-success-text);
  background: var(--color-success-bg);
}
.fill-bar {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  background: var(--color-danger-bg);
  z-index: 0;
}
.option.correct .fill-bar {
  background: rgba(23, 165, 88, 0.15);
}
.option-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}
.your-answer-badge {
  font-size: 11px;
  font-weight: 700;
  color: var(--color-success-text);
  background: #fff;
  border: 1px solid var(--color-success-text);
  border-radius: 999px;
  padding: 2px 8px;
}
.percent {
  position: relative;
  z-index: 1;
  font-weight: 700;
}

.footer-hint {
  text-align: center;
  font-size: 13px;
  color: var(--color-text-secondary);
}
.error-text {
  text-align: center;
  font-size: 13px;
  color: var(--color-danger-text);
}

.score-toast {
  position: fixed;
  bottom: 32px;
  right: 32px;
  background: #fff;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-card);
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.score-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-success-bg);
  color: var(--color-success-text);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.score-value {
  font-weight: 700;
  font-size: 14px;
}
.score-label {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.host-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 24px;
}
</style>
