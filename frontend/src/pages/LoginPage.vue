<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2 text-center">欢迎回来</h1>
      <p class="text-gray-600 mb-8 text-center">登录您的账户</p>

      <form @submit.prevent="handleLogin" class="space-y-6">
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
          <input
            id="email"
            v-model="email"
            type="email"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            placeholder="your@email.com"
          />
        </div>

        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-2">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label for="captcha" class="block text-sm font-medium text-gray-700 mb-2">验证码</label>
          <div class="flex gap-3">
            <input
              id="captcha"
              v-model="captchaText"
              type="text"
              required
              maxlength="4"
              class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
              placeholder="请输入验证码"
            />
            <div
              v-if="captchaImage"
              @click="refreshCaptcha"
              class="cursor-pointer border border-gray-300 rounded-lg overflow-hidden hover:opacity-80 transition"
              style="width: 120px; height: 42px;"
              title="点击刷新验证码"
            >
              <img :src="captchaImage" alt="验证码" class="w-full h-full object-cover" />
            </div>
            <div
              v-else
              class="flex items-center justify-center border border-gray-300 rounded-lg bg-gray-100"
              style="width: 120px; height: 42px;"
            >
              <span class="text-xs text-gray-400">加载中...</span>
            </div>
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm">{{ error }}</div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-primary-600 text-white py-2 px-4 rounded-lg hover:bg-primary-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <router-link to="/auth/register" class="text-primary-600 hover:text-primary-700 text-sm">
          还没有账户？立即注册
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { authAPI, captchaAPI } from '@/api/auth'
import { onboardingAPI } from '@/api/sessions'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const captchaText = ref('')
const captchaSessionId = ref('')
const captchaImage = ref('')
const loading = ref(false)
const error = ref('')

async function loadCaptcha() {
  try {
    const response = await captchaAPI.generate()
    captchaSessionId.value = response.data.session_id
    captchaImage.value = `data:image/png;base64,${response.data.image_base64}`
  } catch (err) {
    console.error('Failed to load captcha:', err)
    error.value = '验证码加载失败，请刷新页面'
  }
}

async function refreshCaptcha() {
  captchaText.value = ''
  await loadCaptcha()
}

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    const response = await authAPI.login(
      email.value,
      password.value,
      captchaSessionId.value,
      captchaText.value
    )
    authStore.setToken(response.data.access_token)
    await authStore.fetchUserOverview()

    // 检查 onboarding 状态（调用新 API）
    try {
      const onboardingResp = await onboardingAPI.getOnboardingStatus()

      if (onboardingResp.data.is_complete) {
        authStore.setOnboardingCompleted(true)
        router.push('/app/overview')
      } else {
        authStore.setOnboardingCompleted(false)
        router.push('/onboarding')
      }
    } catch (err) {
      // API 失败回退到 localStorage 状态
      console.error('Check onboarding failed:', err)
      if (authStore.onboardingCompleted) {
        router.push('/app/overview')
      } else {
        router.push('/onboarding')
      }
    }
  } catch (err) {
    error.value = err.response?.data?.detail || '登录失败，请检查邮箱和密码'
    // 登录失败后刷新验证码
    await refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCaptcha()
})
</script>
