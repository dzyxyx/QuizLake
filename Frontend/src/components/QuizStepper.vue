<script setup lang="ts">
defineProps<{
  step: 1 | 2 | 3
}>()

const steps = [
  { n: 1, label: 'Основное' },
  { n: 2, label: 'Вопросы' },
  { n: 3, label: 'Проверка' },
]
</script>

<template>
  <div class="stepper">
    <template v-for="(s, i) in steps" :key="s.n">
      <div class="step" :class="{ done: s.n < step, current: s.n === step }">
        <span class="circle">
          <span v-if="s.n < step">✓</span>
          <span v-else>{{ s.n }}</span>
        </span>
        <span class="label">{{ s.label }}</span>
      </div>
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
