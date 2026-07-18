<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'

const router = useRouter()

const digits = ref(['', '', '', ''])
const displayName = ref('')
const inputs = ref<HTMLInputElement[]>([])

function onDigitInput(index: number, event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.value.slice(-1).toUpperCase()
  digits.value[index] = value
  if (value && index < 3) {
    inputs.value[index + 1]?.focus()
  }
}

function onDigitKeydown(index: number, event: KeyboardEvent) {
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    inputs.value[index - 1]?.focus()
  }
}

function onSubmit() {
  const code = digits.value.join('')
  router.push({ name: 'session-waiting', params: { code } })
}
</script>

<template>
  <AuthLayout
    heading="Готовы играть?"
    description="Введите код, который назвал организатор — и попадёте прямо в комнату ожидания."
  >
    <template #top-right>
      <RouterLink to="/" class="top-link">На главную →</RouterLink>
    </template>

    <h2 class="title">Код комнаты</h2>

    <form class="form" @submit.prevent="onSubmit">
      <div class="code-row">
        <input
          v-for="(digit, i) in digits"
          :key="i"
          :ref="
            (el) => {
              if (el) inputs[i] = el as HTMLInputElement
            }
          "
          :value="digit"
          class="code-input"
          maxlength="1"
          @input="onDigitInput(i, $event)"
          @keydown="onDigitKeydown(i, $event)"
        />
      </div>

      <div class="field">
        <label>Имя в игре (необязательно, если вы уже в аккаунте)</label>
        <input v-model="displayName" type="text" placeholder="Отображается для других игроков" />
      </div>

      <button type="submit" class="btn btn-primary btn-block">ПРИСОЕДИНИТЬСЯ</button>
    </form>
  </AuthLayout>
</template>

<style scoped>
.title {
  font-size: 20px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 20px;
}
.top-link {
  position: absolute;
  top: 40px;
  right: 40px;
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary);
}
.form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.code-row {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.code-input {
  width: 56px;
  height: 56px;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  outline: none;
}
.code-input:focus {
  border-color: var(--color-primary);
}
</style>
