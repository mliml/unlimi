<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-2 text-center">创建账户</h1>
      <p class="text-gray-600 mb-8 text-center">开始您的心理咨询之旅</p>

      <form @submit.prevent="handleRegister" class="space-y-6">
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
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label for="invitationCode" class="block text-sm font-medium text-gray-700 mb-2">邀请码</label>
          <input
            id="invitationCode"
            v-model="invitationCode"
            type="text"
            required
            maxlength="20"
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
            placeholder="请输入邀请码"
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
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <div class="mt-6 text-center">
        <router-link to="/auth/login" class="text-primary-600 hover:text-primary-700 text-sm">
          已有账户？立即登录
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/features/auth/store/auth'
import { authAPI, captchaAPI } from '@/features/auth/api/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const invitationCode = ref('')
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

async function handleRegister() {
  loading.value = true
  error.value = ''

  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    loading.value = false
    return
  }

  try {
    // 执行注册（后端会直接返回 access_token）
    const response = await authAPI.register(
      email.value,
      password.value,
      invitationCode.value,
      captchaSessionId.value,
      captchaText.value
    )

    // 保存 token（注册接口已经返回了 token）
    authStore.setToken(response.data.access_token)

    // 跳转到 onboarding
    router.push('/onboarding')
  } catch (err) {
    error.value = err.response?.data?.detail || '注册失败，请稍后重试'
    // 注册失败后刷新验证码
    await refreshCaptcha()
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadCaptcha()
})
</script>
