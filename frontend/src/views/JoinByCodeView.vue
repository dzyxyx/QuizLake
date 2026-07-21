<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'
import { ApiError } from '@/api/client'

const router = useRouter()
const auth = useAuthStore()
const sessionStore = useSessionStore()

const CODE_LENGTH = 8
const digits = ref<string[]>(Array(CODE_LENGTH).fill(''))
const displayName = ref('')
const inputs = ref<HTMLInputElement[]>([])
const loading = ref(false)
const error = ref('')

function onDigitInput(index: number, event: Event) {
  const target = event.target as HTMLInputElement
  const value = target.value.slice(-1).toUpperCase()
  digits.value[index] = value
  if (value && index < CODE_LENGTH - 1) {
    inputs.value[index + 1]?.focus()
  }
}

function onDigitKeydown(index: number, event: KeyboardEvent) {
  if (event.key === 'Backspace' && !digits.value[index] && index > 0) {
    inputs.value[index - 1]?.focus()
  }
}

async function onSubmit() {
  error.value = ''
  const roomCode = digits.value.join('')
  if (roomCode.length !== CODE_LENGTH) {
    error.value = `Код должен содержать ${CODE_LENGTH} символов`
    return
  }

  loading.value = true
  try {
    const session = await sessionStore.loadByRoomCode(roomCode)

    if (sessionStore.isHost) {
      if (session.status === 'cancelled') {
        error.value = 'Эта игра была отменена'
        return
      }
      const routeName =
        session.status === 'finished'
          ? 'session-results'
          : session.status === 'active'
            ? 'session-live'
            : 'session-waiting'
      router.push({ name: routeName, params: { code: roomCode } })
      return
    }

    const typedName = displayName.value.trim()
    const name = typedName || auth.user?.nickname
    if (!name) {
      error.value = 'Введите имя, под которым вас увидят другие участники'
      return
    }

    await sessionStore.join(roomCode, name, !typedName)
    router.push({ name: 'session-waiting', params: { code: roomCode } })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось найти комнату с таким кодом'
  } finally {
    loading.value = false
  }
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

    <div v-if="auth.isAuthenticated" class="identity-banner">
      Вы вошли как <strong>{{ auth.user?.nickname }}</strong>. Оставьте поле имени пустым, чтобы
      присоединиться под своим аккаунтом, или впишите любой ник — тогда войдёте как гость.
    </div>

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

      <p v-if="error" class="error-text">{{ error }}</p>

      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? 'Ищем комнату…' : 'ПРИСОЕДИНИТЬСЯ' }}
      </button>
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
  gap: 8px;
  justify-content: center;
}
.code-input {
  width: 38px;
  height: 52px;
  text-align: center;
  font-size: 20px;
  font-weight: 700;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  outline: none;
}
.code-input:focus {
  border-color: var(--color-primary);
}
.error-text {
  font-size: 13px;
  color: var(--color-danger-text);
  text-align: center;
}
.identity-banner {
  background: var(--color-info-bg);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 13px;
  text-align: center;
  margin-bottom: 20px;
  line-height: 1.5;
}
</style>
