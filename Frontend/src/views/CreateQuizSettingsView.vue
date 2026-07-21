<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import QuizStepper from '@/components/QuizStepper.vue'
import { useQuizzesStore } from '@/stores/quizzes'
import { useCategoriesStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import type { QuizDifficulty } from '@/types'
import { ApiError } from '@/api/client'

const route = useRoute()
const router = useRouter()
const quizzesStore = useQuizzesStore()
const categoriesStore = useCategoriesStore()
const auth = useAuthStore()

const quizId = computed(() => (route.params.id ? Number(route.params.id) : null))
const isEdit = computed(() => quizId.value !== null)

const title = ref('')
const description = ref('')
const categoryId = ref<number | null>(null)
const difficulty = ref<QuizDifficulty>('medium')
const timePerQuestion = ref(15)
const speedBonus = ref(false)
const showCorrectAnswer = ref(true)
const allowAnswerChange = ref(false)
const isPublic = ref(false)

const loading = ref(false)
const error = ref('')
const accessDenied = ref(false)

onMounted(async () => {
  categoriesStore.fetchCategories()
  if (quizId.value !== null) {
    try {
      const quiz = await quizzesStore.getQuiz(quizId.value)
      if (quiz.owner_id !== auth.user?.id) {
        accessDenied.value = true
        return
      }
      title.value = quiz.title
      description.value = quiz.description ?? ''
      categoryId.value = quiz.category_id
      difficulty.value = quiz.difficulty
      timePerQuestion.value = quiz.time_per_question_sec
      speedBonus.value = quiz.speed_bonus_enabled
      showCorrectAnswer.value = quiz.show_correct_answer
      allowAnswerChange.value = quiz.allow_answer_change
      isPublic.value = quiz.is_public
    } catch {
      accessDenied.value = true
    }
  }
})

function buildPayload() {
  return {
    title: title.value,
    description: description.value || null,
    category_id: categoryId.value,
    difficulty: difficulty.value,
    time_per_question_sec: timePerQuestion.value,
    speed_bonus_enabled: speedBonus.value,
    show_correct_answer: showCorrectAnswer.value,
    allow_answer_change: allowAnswerChange.value,
    is_public: isPublic.value,
  }
}

async function saveIfEditing(): Promise<boolean> {
  if (!isEdit.value || quizId.value === null) return true
  error.value = ''

  if (!title.value.trim()) {
    error.value = 'Введите название квиза, прежде чем переходить к вопросам'
    return false
  }

  try {
    await quizzesStore.updateQuiz(quizId.value, buildPayload())
    return true
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось сохранить квиз'
    return false
  }
}

async function onNext() {
  error.value = ''
  loading.value = true

  try {
    if (isEdit.value && quizId.value !== null) {
      const ok = await saveIfEditing()
      if (!ok) return
      router.push({ name: 'quiz-add-questions', params: { id: quizId.value } })
    } else {
      const quiz = await quizzesStore.createQuiz(buildPayload())
      router.push({ name: 'quiz-add-questions', params: { id: quiz.id } })
    }
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось сохранить квиз'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout active-item="my-quizzes" :active-draft-id="quizId">
    <div v-if="accessDenied" class="card form-card">
      <RouterLink to="/" class="exit-link">← Выйти из редактора</RouterLink>
      <p class="error-text">Этот квиз вам не принадлежит — редактировать его нельзя.</p>
    </div>

    <div v-else class="layout-row">
      <QuizStepper :step="1" :quiz-id="quizId" :before-leave="saveIfEditing" />

      <div class="card form-card">
        <RouterLink to="/" class="exit-link">← Выйти из редактора</RouterLink>
        <h1>Основные настройки квиза</h1>

        <form class="form" @submit.prevent="onNext">
          <div class="field">
            <label>Название квиза</label>
            <input v-model="title" type="text" required />
          </div>

          <div class="field">
            <label>Описание (необязательно)</label>
            <textarea v-model="description" rows="2" />
          </div>

          <div class="row-2">
            <div class="field">
              <label>Категория</label>
              <select v-model.number="categoryId">
                <option :value="null">Без категории</option>
                <option v-for="c in categoriesStore.categories" :key="c.id" :value="c.id">
                  {{ c.name }}
                </option>
              </select>
            </div>
            <div class="field">
              <label>Сложность</label>
              <select v-model="difficulty">
                <option value="easy">Лёгкий</option>
                <option value="medium">Средний</option>
                <option value="hard">Сложный</option>
              </select>
            </div>
          </div>

          <div class="field">
            <label>Время на вопрос по умолчанию, сек</label>
            <input v-model.number="timePerQuestion" type="number" min="5" />
            <p class="field-hint">
              Баллы за верный ответ настраиваются отдельно для каждого вопроса на следующем шаге
            </p>
          </div>

          <div class="field">
            <label>Правила проведения</label>
            <label class="checkbox">
              <input v-model="speedBonus" type="checkbox" />
              Бонус за скорость ответа
            </label>
            <label class="checkbox">
              <input v-model="showCorrectAnswer" type="checkbox" />
              Показывать правильный ответ после вопроса
            </label>
            <label class="checkbox">
              <input v-model="allowAnswerChange" type="checkbox" />
              Разрешить смену ответа до истечения времени
            </label>
            <label class="checkbox">
              <input v-model="isPublic" type="checkbox" />
              Публичный квиз (виден всем в разделе «Обзор», когда идёт сессия)
            </label>
          </div>

          <p v-if="error" class="error-text">{{ error }}</p>

          <div class="actions">
            <button type="submit" class="btn btn-primary" :disabled="loading">
              {{ loading ? 'Сохраняем…' : 'ДАЛЕЕ: ДОБАВИТЬ ВОПРОСЫ →' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.layout-row {
  display: flex;
  gap: 24px;
}
.form-card {
  flex: 1;
  padding: 32px;
  max-width: 700px;
}
.exit-link {
  display: inline-block;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 16px;
}
.exit-link:hover {
  color: var(--color-primary);
}
h1 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 24px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-text);
  text-transform: none;
  margin-top: 4px;
}
.checkbox input {
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}
.actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
.error-text {
  font-size: 13px;
  color: var(--color-danger-text);
}
.field-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}
</style>
