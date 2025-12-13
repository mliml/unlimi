<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
      <!-- 进度条 -->
      <div class="mb-8">
        <div class="flex justify-between items-center mb-4">
          <h1 class="text-2xl font-bold text-gray-800">初始问卷</h1>
          <span class="text-sm text-gray-500">
            {{ answered }} / {{ total }}
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2">
          <div
            class="bg-primary-600 h-2 rounded-full transition-all duration-300"
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="flex justify-center items-center h-64">
        <div class="text-gray-500">加载中...</div>
      </div>

      <!-- 错误提示 -->
      <div v-else-if="error" class="text-center">
        <p class="text-red-600 mb-4">{{ error }}</p>
        <button
          @click="loadCurrentQuestion"
          class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition duration-200"
        >
          重新加载
        </button>
      </div>

      <!-- 问题展示 -->
      <div v-else-if="currentQuestion">
        <!-- 问答题 -->
        <TextQuestion
          v-if="currentQuestion.question_type === 'text'"
          :question="currentQuestion"
          :submitting="submitting"
          @submit="submitAnswer"
        />

        <!-- 选择题 -->
        <ChoiceQuestion
          v-else-if="currentQuestion.question_type === 'choice'"
          :question="currentQuestion"
          :submitting="submitting"
          @submit="submitAnswer"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/features/auth/store/auth'
import { onboardingAPI } from '@/features/consult/api/sessions'
import TextQuestion from '@/features/onboarding/components/TextQuestion.vue'
import ChoiceQuestion from '@/features/onboarding/components/ChoiceQuestion.vue'

const router = useRouter()
const authStore = useAuthStore()

const loading = ref(true)
const submitting = ref(false)
const error = ref('')

const sessionId = ref('')
const currentQuestion = ref(null)
const answered = ref(0)
const total = ref(10)

const progressPercentage = computed(() => {
  if (total.value === 0) return 0
  return Math.round((answered.value / total.value) * 100)
})

async function loadCurrentQuestion() {
  loading.value = true
  error.value = ''

  try {
    const response = await onboardingAPI.getOnboardingStatus()
    const data = response.data

    if (data.is_complete) {
      // 情况1：已完成
      authStore.setOnboardingCompleted(true)
      router.push('/app/overview')
      return
    }

    // 情况2 & 3：展示当前问题
    sessionId.value = data.session_id
    currentQuestion.value = data.question

    // 计算进度（从 question_number 推算）
    answered.value = data.question.question_number - 1
    total.value = 10

  } catch (err) {
    console.error('Load onboarding error:', err)
    error.value = err?.response?.data?.detail || '加载失败，请刷新重试'
  } finally {
    loading.value = false
  }
}

async function submitAnswer(answer) {
  if (!currentQuestion.value) return

  submitting.value = true
  error.value = ''

  try {
    const response = await onboardingAPI.submitAnswer(
      sessionId.value,
      currentQuestion.value.question_number,
      answer
    )

    const data = response.data

    if (data.is_complete) {
      // 全部完成
      authStore.setOnboardingCompleted(true)

      // 可选：存储完成信息
      if (data.nickname) {
        // 可以更新用户昵称到 store
        console.log('Onboarding completed, nickname:', data.nickname)
      }

      router.push('/app/overview')
    } else {
      // 更新下一题
      currentQuestion.value = data.next_question
      answered.value++
    }

  } catch (err) {
    console.error('Submit answer error:', err)
    error.value = err?.response?.data?.detail || '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadCurrentQuestion()
})
</script>
