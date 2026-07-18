<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthLayout from '@/layouts/AuthLayout.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const nickname = ref('')
const password = ref('')
const passwordConfirm = ref('')
const agree = ref(false)
const loading = ref(false)

async function onSubmit() {
  loading.value = true
  try {
    await auth.register({
      firstName: firstName.value,
      lastName: lastName.value,
      email: email.value,
      nickname: nickname.value || undefined,
    })
    router.push({ name: 'dashboard' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLayout
    heading="Создайте аккаунт за полминуты"
    description="Регистрация одна для всех: сразу после неё вы можете присоединиться к квизу или создать свой."
  >
    <template #side-extra>
      <ol class="steps">
        <li><span class="step-num">1</span> Зарегистрируйтесь</li>
        <li><span class="step-num">2</span> Создайте квиз или введите код</li>
        <li><span class="step-num">3</span> Играйте и приглашайте друзей</li>
      </ol>
    </template>

    <h2 class="title">Создать аккаунт</h2>
    <p class="subtitle">Это займёт меньше минуты</p>

    <form class="form" @submit.prevent="onSubmit">
      <div class="row-2">
        <div class="field">
          <label>Имя</label>
          <input v-model="firstName" type="text" placeholder="Иван" required />
        </div>
        <div class="field">
          <label>Фамилия</label>
          <input v-model="lastName" type="text" placeholder="Петров" required />
        </div>
      </div>

      <div class="field">
        <label>Email</label>
        <input v-model="email" type="email" placeholder="ivan@mail.ru" required />
      </div>

      <div class="field">
        <label>Псевдоним (по желанию)</label>
        <input v-model="nickname" type="text" placeholder="Будет отображаться другим участникам" />
      </div>

      <div class="row-2">
        <div class="field">
          <label>Пароль</label>
          <input v-model="password" type="password" placeholder="••••••••" required />
        </div>
        <div class="field">
          <label>Повтор пароля</label>
          <input v-model="passwordConfirm" type="password" placeholder="••••••••" required />
        </div>
      </div>

      <label class="checkbox">
        <input v-model="agree" type="checkbox" required />
        Согласен с условиями использования
      </label>

      <button type="submit" class="btn btn-primary btn-block" :disabled="loading">
        {{ loading ? 'Создаём…' : 'ЗАРЕГИСТРИРОВАТЬСЯ' }}
      </button>

      <p class="bottom-text">
        Уже есть аккаунт?
        <RouterLink to="/login" class="link-strong">Войти</RouterLink>
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
.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
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
.bottom-text {
  text-align: center;
  font-size: 14px;
  color: var(--color-text-secondary);
}
.link-strong {
  color: var(--color-primary);
  font-weight: 700;
}

.steps {
  list-style: none;
  padding: 0;
  margin: 24px 0 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.steps li {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  font-size: 14px;
  font-weight: 600;
}
.step-num {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  flex-shrink: 0;
}
</style>
