<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

interface Option {
  label: string
  text: string
  percent: number
  isCorrect: boolean
}

const questionNumber = 3
const totalQuestions = 10
const yourRank = 2

const options = ref<Option[]>([
  { label: 'A', text: 'Нил', percent: 8, isCorrect: false },
  { label: 'B', text: 'Амазонка', percent: 61, isCorrect: true },
  { label: 'C', text: 'Янцзы', percent: 19, isCorrect: false },
  { label: 'D', text: 'Миссисипи', percent: 12, isCorrect: false },
])

const selectedLabel = ref<string | null>('B')
const secondsLeft = ref(9)
const revealed = ref(false)
let timer: number | undefined

onMounted(() => {
  timer = window.setInterval(() => {
    if (secondsLeft.value > 0) {
      secondsLeft.value -= 1
    } else {
      revealed.value = true
      clearInterval(timer)
    }
  }, 1000)
})
onUnmounted(() => {
  if (timer) clearInterval(timer)
})

function selectOption(label: string) {
  if (revealed.value) return
  selectedLabel.value = label
}

const correctOption = computed(() => options.value.find((o) => o.isCorrect))

function close() {
  router.push({ name: 'session-results', params: { code: route.params.code } })
}
</script>

<template>
  <div class="live-page">
    <aside class="side-strip">
      <span class="logo-dot" />
      <button class="close-btn" @click="close">✕</button>
    </aside>

    <main class="live-content">
      <div class="top-row">
        <span class="badge badge-info">Вопрос {{ questionNumber }} из {{ totalQuestions }}</span>

        <div v-if="!revealed" class="timer-circle">{{ String(secondsLeft).padStart(2, '0') }}</div>
        <span v-else class="badge badge-success">Время вышло · показаны результаты</span>

        <span class="badge badge-warning">🏆 Ваше место: {{ yourRank }}</span>
      </div>

      <div class="card question-card">
        <h1>Какая река является самой длинной в мире?</h1>

        <div v-if="!revealed" class="image-placeholder">🖼 изображение к вопросу</div>

        <div class="options" :class="{ revealed }">
          <button
            v-for="opt in options"
            :key="opt.label"
            class="option"
            :class="{
              selected: !revealed && selectedLabel === opt.label,
              correct: revealed && opt.isCorrect,
              wrong: revealed && !opt.isCorrect,
            }"
            @click="selectOption(opt.label)"
          >
            <div v-if="revealed" class="fill-bar" :style="{ width: opt.percent + '%' }" />
            <span class="option-content">
              <span class="option-label">
                <span v-if="revealed && opt.isCorrect">✓</span>
                {{ opt.label }} · {{ opt.text }}
              </span>
              <span v-if="revealed && selectedLabel === opt.label" class="your-answer-badge"
                >✓ Ваш ответ</span
              >
            </span>
            <span v-if="revealed" class="percent">{{ opt.percent }}%</span>
            <span v-else-if="selectedLabel === opt.label" class="check-badge">✓</span>
          </button>
        </div>

        <p v-if="!revealed" class="footer-hint">
          Ответ принят — ожидайте окончания времени на вопрос
        </p>
        <p v-else class="footer-hint">Правильный ответ — {{ correctOption?.text }}.</p>
      </div>

      <div v-if="revealed" class="score-toast">
        <span class="score-icon">✓</span>
        <div>
          <div class="score-value">+100 очков</div>
          <div class="score-label">Ответ верный!</div>
        </div>
      </div>
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

.top-row {
  width: 100%;
  max-width: 820px;
  display: flex;
  align-items: center;
  justify-content: space-between;
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

.image-placeholder {
  height: 180px;
  border-radius: var(--radius-sm);
  background: #f5f7fb;
  border: 1px dashed var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
  font-size: 13px;
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
.option.selected {
  border-color: var(--color-primary);
}
.option.correct {
  border-color: var(--color-success-text);
  background: var(--color-success-bg);
}
.option.wrong {
  background: #fff;
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
.check-badge {
  position: absolute;
  top: -6px;
  right: -6px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
}

.footer-hint {
  text-align: center;
  font-size: 13px;
  color: var(--color-text-secondary);
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
</style>
