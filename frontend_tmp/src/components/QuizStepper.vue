<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps<{
  step: 1 | 2
  quizId?: number | null
  beforeLeave?: () => boolean | Promise<boolean>
}>()

const router = useRouter()
const navigating = ref(false)

const steps = [
  { n: 1 as const, label: 'Основное' },
  { n: 2 as const, label: 'Вопросы' },
]

async function goTo(n: 1 | 2) {
  if (n === props.step) return
  if (n === 2 && !props.quizId) return
  if (navigating.value) return

  if (props.beforeLeave) {
    navigating.value = true
    try {
      const ok = await props.beforeLeave()
      if (!ok) return
    } finally {
      navigating.value = false
    }
  }

  if (n === 1) {
    router.push(
      props.quizId
        ? { name: 'quiz-edit-settings', params: { id: props.quizId } }
        : { name: 'quiz-create-settings' },
    )
  } else {
    router.push({ name: 'quiz-add-questions', params: { id: props.quizId } })
  }
}

function isDisabled(n: 1 | 2) {
  return (n === 2 && !props.quizId) || navigating.value
}
</script>

<template>
  <div class="stepper">
    <template v-for="(s, i) in steps" :key="s.n">
      <button
        type="button"
        class="step"
        :class="{ done: s.n < step, current: s.n === step, disabled: isDisabled(s.n) }"
        :disabled="isDisabled(s.n)"
        @click="goTo(s.n)"
      >
        <span class="circle">
          <span v-if="s.n < step">✓</span>
          <span v-else>{{ s.n }}</span>
        </span>
        <span class="label">{{ s.label }}</span>
      </button>
      <div v-if="i < steps.length - 1" class="connector" />
    </template>
  </div>
</template>

<style scoped>
.stepper {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 8px;
  width: 72px;
  flex-shrink: 0;
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.step:not(.disabled) {
  cursor: pointer;
}
.step.disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
.circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 700;
  background: #fff;
}
.step.current .circle {
  border-color: var(--color-primary);
  background: var(--color-primary);
  color: #fff;
}
.step.done .circle {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
.label {
  font-size: 11px;
  color: var(--color-text-muted);
  font-weight: 600;
}
.step.current .label {
  color: var(--color-primary);
}
.connector {
  width: 2px;
  height: 32px;
  background: var(--color-border);
  margin: 2px 0;
}
</style>
