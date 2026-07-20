<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import QuizStepper from '@/components/QuizStepper.vue'
import * as questionsApi from '@/api/questions'
import { useQuizzesStore } from '@/stores/quizzes'
import type { QuestionType } from '@/types'
import { ApiError } from '@/api/client'

interface OptionDraft {
  id?: number
  option_text: string
  is_correct: boolean
}
interface QuestionDraft {
  id?: number
  question_text: string
  image_url: string
  question_type: QuestionType
  time_limit_sec: number | null
  points: number | null
  answer_options: OptionDraft[]
}

const route = useRoute()
const router = useRouter()
const quizzesStore = useQuizzesStore()

const quizId = Number(route.params.id)

const questions = ref<QuestionDraft[]>([])
const activeIndex = ref(0)
const active = computed(() => questions.value[activeIndex.value] ?? null)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

function typeLabel(type: QuestionType) {
  return type === 'single' ? 'Один правильный ответ' : 'Несколько правильных ответов'
}

function blankQuestion(): QuestionDraft {
  return {
    question_text: '',
    image_url: '',
    question_type: 'single',
    time_limit_sec: 15,
    points: 100,
    answer_options: [
      { option_text: '', is_correct: true },
      { option_text: '', is_correct: false },
    ],
  }
}

onMounted(async () => {
  try {
    const loaded = await questionsApi.listQuestions(quizId)
    questions.value = loaded
      .sort((a, b) => a.order_index - b.order_index)
      .map((q) => ({
        id: q.id,
        question_text: q.question_text,
        image_url: q.image_url ?? '',
        question_type: q.question_type,
        time_limit_sec: q.time_limit_sec,
        points: q.points,
        answer_options: q.answer_options
          .sort((a, b) => a.order_index - b.order_index)
          .map((o) => ({ id: o.id, option_text: o.option_text, is_correct: o.is_correct })),
      }))
    if (questions.value.length === 0) {
      questions.value.push(blankQuestion())
    }
  } finally {
    loading.value = false
  }
})

function addOption() {
  active.value?.answer_options.push({ option_text: '', is_correct: false })
}

function removeOption(index: number) {
  if (active.value && active.value.answer_options.length > 2) {
    active.value.answer_options.splice(index, 1)
  }
}

function selectCorrect(index: number) {
  if (!active.value) return
  const option = active.value.answer_options[index]
  if (active.value.question_type === 'single') {
    active.value.answer_options.forEach((o, i) => (o.is_correct = i === index))
  } else {
    option.is_correct = !option.is_correct
  }
}

function addQuestion() {
  questions.value.push(blankQuestion())
  activeIndex.value = questions.value.length - 1
}

async function removeQuestion(index: number) {
  const question = questions.value[index]
  if (question.id) {
    try {
      await questionsApi.deleteQuestion(quizId, question.id)
    } catch (e) {
      error.value = e instanceof ApiError ? e.message : 'Не удалось удалить вопрос'
      return
    }
  }
  questions.value.splice(index, 1)
  if (activeIndex.value >= questions.value.length) {
    activeIndex.value = Math.max(0, questions.value.length - 1)
  }
}

async function saveActiveQuestion() {
  if (!active.value) return
  error.value = ''

  if (!active.value.question_text.trim()) {
    error.value = 'Введите текст вопроса'
    return
  }
  if (active.value.answer_options.some((o) => !o.option_text.trim())) {
    error.value = 'Заполните текст всех вариантов ответа'
    return
  }
  if (!active.value.answer_options.some((o) => o.is_correct)) {
    error.value = 'Отметьте хотя бы один правильный вариант'
    return
  }

  saving.value = true
  try {
    const payload: questionsApi.QuestionPayload = {
      question_text: active.value.question_text,
      image_url: active.value.image_url || null,
      question_type: active.value.question_type,
      order_index: activeIndex.value + 1,
      time_limit_sec: active.value.time_limit_sec,
      points: active.value.points,
      answer_options: active.value.answer_options.map((o, i) => ({
        option_text: o.option_text,
        is_correct: o.is_correct,
        order_index: i + 1,
      })),
    }

    const saved = active.value.id
      ? await questionsApi.updateQuestion(quizId, active.value.id, payload)
      : await questionsApi.createQuestion(quizId, payload)

    questions.value[activeIndex.value] = {
      id: saved.id,
      question_text: saved.question_text,
      image_url: saved.image_url ?? '',
      question_type: saved.question_type,
      time_limit_sec: saved.time_limit_sec,
      points: saved.points,
      answer_options: saved.answer_options.map((o) => ({
        id: o.id,
        option_text: o.option_text,
        is_correct: o.is_correct,
      })),
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось сохранить вопрос'
  } finally {
    saving.value = false
  }
}

async function publishQuiz() {
  error.value = ''
  const unsaved = questions.value.some((q) => !q.id)
  if (unsaved) {
    error.value = 'Сохраните все вопросы (кнопка «Сохранить вопрос»), прежде чем публиковать квиз'
    return
  }
  try {
    await quizzesStore.updateQuiz(quizId, { status: 'ready' })
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось опубликовать квиз'
  }
}
</script>

<template>
  <AppLayout active-item="my-quizzes" :active-draft-id="quizId">
    <div v-if="loading">Загрузка…</div>
    <div v-else class="layout-row">
      <QuizStepper :step="2" />

      <div class="card list-card">
        <div class="list-title">Вопросы ({{ questions.length }})</div>
        <button
          v-for="(q, i) in questions"
          :key="q.id ?? `draft-${i}`"
          class="question-item"
          :class="{ active: i === activeIndex }"
          @click="activeIndex = i"
        >
          <span class="q-title">{{ i + 1 }}. {{ q.question_text || '(без текста)' }}</span>
          <span class="q-type">{{ typeLabel(q.question_type) }}<span v-if="!q.id"> · не сохранён</span></span>
        </button>
        <button class="btn btn-secondary btn-block add-btn" @click="addQuestion">
          + Добавить вопрос
        </button>
        <button class="btn btn-primary btn-block" @click="publishQuiz">Готово: опубликовать квиз</button>
      </div>

      <div v-if="active" class="card edit-card">
        <RouterLink :to="{ name: 'quiz-edit-settings', params: { id: quizId } }" class="back-link">
          ← Вернуться к основным настройкам
        </RouterLink>

        <div class="edit-header">
          <h1>Вопрос {{ activeIndex + 1 }}</h1>
          <div class="header-right">
            <select v-model="active.question_type" class="type-select">
              <option value="single">Один правильный ответ</option>
              <option value="multiple">Несколько правильных ответов</option>
            </select>
            <button
              v-if="questions.length > 1"
              type="button"
              class="remove-btn"
              title="Удалить вопрос"
              @click="removeQuestion(activeIndex)"
            >
              ✕
            </button>
          </div>
        </div>

        <div class="field">
          <label>Текст вопроса</label>
          <input v-model="active.question_text" type="text" />
        </div>

        <div class="field">
          <label>Изображение к вопросу (ссылка, необязательно)</label>
          <input v-model="active.image_url" type="text" placeholder="https://…" />
        </div>

        <div class="row-2">
          <div class="field">
            <label>Время на вопрос, сек</label>
            <input v-model.number="active.time_limit_sec" type="number" min="5" />
          </div>
          <div class="field">
            <label>Баллы за верный ответ</label>
            <input v-model.number="active.points" type="number" min="0" step="10" />
          </div>
        </div>

        <div class="field">
          <label>Варианты ответа</label>
          <div v-for="(opt, i) in active.answer_options" :key="i" class="option-row">
            <span
              class="option-radio"
              :class="{ correct: opt.is_correct }"
              @click="selectCorrect(i)"
            />
            <input
              v-model="opt.option_text"
              type="text"
              class="option-input"
              :class="{ correct: opt.is_correct }"
            />
            <button
              v-if="active.answer_options.length > 2"
              type="button"
              class="remove-btn small"
              @click="removeOption(i)"
            >
              ✕
            </button>
          </div>
          <button type="button" class="btn btn-secondary add-option" @click="addOption">
            + Вариант ответа
          </button>
        </div>

        <p v-if="error" class="error-text">{{ error }}</p>

        <div class="actions">
          <button type="button" class="btn btn-primary" :disabled="saving" @click="saveActiveQuestion">
            {{ saving ? 'Сохраняем…' : 'СОХРАНИТЬ ВОПРОС' }}
          </button>
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

.list-card {
  width: 240px;
  flex-shrink: 0;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.list-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}
.question-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 10px;
  border-radius: var(--radius-sm);
  text-align: left;
}
.question-item:hover {
  background: #f5f7fb;
}
.question-item.active {
  background: var(--color-info-bg);
}
.q-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text);
}
.q-type {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.add-btn {
  margin-top: 12px;
  margin-bottom: 8px;
}

.edit-card {
  flex: 1;
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 22px;
}
.back-link {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary);
}
.edit-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.edit-header h1 {
  font-size: 22px;
  font-weight: 700;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.type-select {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 8px 10px;
  font-size: 13px;
}

.remove-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: var(--color-text-secondary);
  font-size: 14px;
}
.remove-btn:hover {
  background: #eee;
}
.remove-btn.small {
  width: 24px;
  height: 24px;
  font-size: 12px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.option-radio {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  flex-shrink: 0;
  cursor: pointer;
}
.option-radio.correct {
  background: var(--color-success-text);
  border-color: var(--color-success-text);
}
.option-input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
}
.option-input.correct {
  border-color: var(--color-success-text);
}
.option-input:focus {
  border-color: var(--color-primary);
}
.add-option {
  margin-top: 4px;
}

.actions {
  display: flex;
  justify-content: flex-end;
}
.error-text {
  font-size: 13px;
  color: var(--color-danger-text);
}
</style>
