<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const rememberMe = ref(true)
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    router.push({ name: 'dashboard' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout
    heading="Один аккаунт — чтобы играть и создавать"
    description="Присоединяйтесь к чужим квизам по коду комнаты или создавайте собственные"
  >
    <h2 class="title">Вход</h2>
    <p class="subtitle">Войдите, чтобы продолжить</p>

    <form class="form" @submit.prevent="onSubmit">
      <div class="field">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="ivan.petrov@mail.ru" required />
      </div>

      <div class="field">
        <label>Пароль</label>
        <input v-model="password" type="password" placeholder="••••••••" required />
      </div>

      <div class="row">
        <label class="checkbox">
          <input v-model="rememberMe" type="checkbox" />
          Запомнить меня
        </label>
        <a href="#" class="link">Забыли пароль?</a>
      </div>

      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? 'Входим…' : 'ВОЙТИ' }}
      </button>

      <div class="divider"><span>или</span></div>

      <RouterLink to="/join" class="btn btn-secondary btn-block"
        >🔑 Есть код комнаты? Войти по коду</RouterLink
      >

      <p class="bottom-text">
        Нет аккаунта?
        <RouterLink to="/register" class="link-strong">Зарегистрироваться</RouterLink>
      </p>
    </form>
  </AuthLayout>
</template>

<style scoped>
.title {
  font-size: 26px;
  font-weight: 700;
}
.subtitle {
  color: var(--color-text-secondary);
  margin-top: 6px;
  margin-bottom: 24px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: -4px;
}
.checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text);
}
.checkbox input {
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}
.link {
  font-size: 13px;
  color: var(--color-primary);
  font-weight: 600;
}
.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 12px;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-top: 1px solid var(--color-border);
}
.divider span {
  padding: 0 12px;
}
.bottom-text {
  text-align: center;
  font-size: 14px;
  color: var(--color-text-secondary);
}
.link-strong {
  color: var(--color-primary);
  font-weight: 700;
}
</style>
