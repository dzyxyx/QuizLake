<script setup lang="ts">
import { ref, computed } from 'vue'
import AppLayout from '@/layouts/AppLayout.vue'
import QuizStepper from '@/components/QuizStepper.vue'

interface OptionDraft {
  text: string
  isCorrect: boolean
}
interface QuestionDraft {
  title: string
  typeLabel: string
  badgeLabel: string
  text: string
  image: { name: string; meta: string } | null
  options: OptionDraft[]
}

const questions = ref<QuestionDraft[]>([
  {
    title: 'Год начала ВОВ',
    typeLabel: 'Текст + фото',
    badgeLabel: 'Один правильный ответ',
    text: 'В каком году началась Великая Отечественная война?',
    image: { name: '1941-nachalo-voyny.jpg', meta: 'JPG · 240 KB · 1600×900' },
    options: [
      { text: '1941', isCorrect: true },
      { text: '1939', isCorrect: false },
      { text: '1945', isCorrect: false },
      { text: '1917', isCorrect: false },
    ],
  },
  {
    title: 'Кто изображён на фото?',
    typeLabel: 'Фото',
    badgeLabel: 'Один правильный ответ',
    text: '',
    image: null,
    options: [
      { text: '', isCorrect: true },
      { text: '', isCorrect: false },
    ],
  },
  {
    title: 'Союзные республики',
    typeLabel: 'Несколько ответов',
    badgeLabel: 'Несколько правильных ответов',
    text: '',
    image: null,
    options: [
      { text: '', isCorrect: true },
      { text: '', isCorrect: true },
    ],
  },
  {
    title: 'Год распада СССР',
    typeLabel: 'Текст',
    badgeLabel: 'Один правильный ответ',
    text: '',
    image: null,
    options: [
      { text: '', isCorrect: true },
      { text: '', isCorrect: false },
    ],
  },
])

const totalCount = 7
const activeIndex = ref(0)
const active = computed(() => questions.value[activeIndex.value])

function addOption() {
  active.value.options.push({ text: '', isCorrect: false })
}

function addQuestion() {
  questions.value.push({
    title: `Вопрос ${questions.value.length + 1}`,
    typeLabel: 'Текст',
    badgeLabel: 'Один правильный ответ',
    text: '',
    image: null,
    options: [
      { text: '', isCorrect: true },
      { text: '', isCorrect: false },
    ],
  })
  activeIndex.value = questions.value.length - 1
}
</script>

<template>
  <AppLayout active-item="my-quizzes" :active-draft-id="1">
    <div class="layout-row">
      <QuizStepper :step="2" />

      <div class="card list-card">
        <div class="list-title">Вопросы ({{ totalCount }})</div>
        <button
          v-for="(q, i) in questions"
          :key="i"
          class="question-item"
          :class="{ active: i === activeIndex }"
          @click="activeIndex = i"
        >
          <span class="q-title">{{ i + 1 }}. {{ q.title }}</span>
          <span class="q-type">{{ q.typeLabel }}</span>
        </button>
        <button class="btn btn-secondary btn-block add-btn" @click="addQuestion">
          + Добавить вопрос
        </button>
      </div>

      <div class="card edit-card">
        <RouterLink to="/quizzes/create" class="back-link"
          >← Вернуться к основным настройкам</RouterLink
        >

        <div class="edit-header">
          <h1>Вопрос {{ activeIndex + 1 }}</h1>
          <span class="badge badge-success">{{ active.badgeLabel }}</span>
        </div>

        <div class="field">
          <label>Текст вопроса</label>
          <input v-model="active.text" type="text" />
        </div>

        <div class="field">
          <label>Изображение к вопросу (необязательно)</label>
          <div v-if="active.image" class="image-card">
            <span class="image-icon">🖼</span>
            <div class="image-info">
              <div class="image-name">{{ active.image.name }}</div>
              <div class="image-meta">{{ active.image.meta }}</div>
            </div>
            <button type="button" class="btn btn-secondary small">Заменить</button>
            <button type="button" class="remove-btn">✕</button>
          </div>
          <button v-else type="button" class="btn btn-secondary btn-block">
            Загрузить изображение
          </button>
        </div>

        <div class="field">
          <label>Варианты ответа</label>
          <div v-for="(opt, i) in active.options" :key="i" class="option-row">
            <span
              class="option-radio"
              :class="{ correct: opt.isCorrect }"
              @click="opt.isCorrect = !opt.isCorrect"
            />
            <input
              v-model="opt.text"
              type="text"
              class="option-input"
              :class="{ correct: opt.isCorrect }"
            />
          </div>
          <button type="button" class="btn btn-secondary add-option" @click="addOption">
            + Вариант ответа
          </button>
        </div>

        <div class="actions">
          <button type="button" class="btn btn-primary">СОХРАНИТЬ ВОПРОС</button>
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
  width: 220px;
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

.image-card {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: #fafbfd;
}
.image-icon {
  font-size: 20px;
}
.image-info {
  flex: 1;
  min-width: 0;
}
.image-name {
  font-size: 13px;
  font-weight: 600;
}
.image-meta {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.btn.small {
  padding: 8px 14px;
  font-size: 12px;
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
</style>
