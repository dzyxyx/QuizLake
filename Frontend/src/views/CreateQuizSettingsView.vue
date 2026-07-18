<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import QuizStepper from '@/components/QuizStepper.vue'

const router = useRouter()

const title = ref('История России: XX век')
const category = ref('История')
const difficulty = ref('Лёгкий')
const timePerQuestion = ref(15)
const pointsPerCorrect = ref(100)
const speedBonus = ref(true)
const showCorrectAnswer = ref(true)
const allowAnswerChange = ref(false)

function onNext() {
  router.push({ name: 'quiz-add-questions', params: { id: 1 } })
}
</script>

<template>
  <AppLayout active-item="my-quizzes" :active-draft-id="1">
    <div class="layout-row">
      <QuizStepper :step="1" />

      <div class="card form-card">
        <h1>Основные настройки квиза</h1>

        <form class="form" @submit.prevent="onNext">
          <div class="field">
            <label>Название квиза</label>
            <input v-model="title" type="text" />
          </div>

          <div class="row-2">
            <div class="field">
              <label>Категория</label>
              <select v-model="category">
                <option>История</option>
                <option>География</option>
                <option>Наука</option>
                <option>Кино и сериалы</option>
                <option>Музыка</option>
                <option>Спорт</option>
                <option>Литература</option>
              </select>
            </div>
            <div class="field">
              <label>Сложность</label>
              <select v-model="difficulty">
                <option>Лёгкий</option>
                <option>Средний</option>
                <option>Сложный</option>
              </select>
            </div>
          </div>

          <div class="row-2">
            <div class="field">
              <label>Время на вопрос, сек</label>
              <input v-model.number="timePerQuestion" type="number" min="5" />
            </div>
            <div class="field">
              <label>Баллы за верный ответ</label>
              <input v-model.number="pointsPerCorrect" type="number" min="0" step="10" />
            </div>
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
          </div>

          <div class="actions">
            <button type="submit" class="btn btn-primary">ДАЛЕЕ: ДОБАВИТЬ ВОПРОСЫ →</button>
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
</style>
