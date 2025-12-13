<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <button
              @click="handleBackClick"
              class="text-gray-600 hover:text-gray-800"
            >
              ← 返回
            </button>
            <h1 class="text-xl font-bold text-gray-800">咨询中</h1>
          </div>
          <button
            @click="handleEndSessionClick"
            :disabled="!currentSessionId"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            结束咨询
          </button>
        </div>
      </div>
    </nav>

    <!-- 调试信息面板 -->
    <div v-if="currentSessionId" class="bg-yellow-50 border-b border-yellow-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-6 text-sm">
            <div>
              <span class="font-medium text-gray-700">前端计时:</span>
              <span class="ml-2 text-gray-900">{{ formatDuration(frontendDuration) }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-700">后端计时:</span>
              <span class="ml-2 text-gray-900">{{ formatDuration(sessionMetadata.active_duration_seconds) }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-700">对话轮数:</span>
              <span class="ml-2 text-gray-900">{{ sessionMetadata.turn_count }}</span>
            </div>
            <div>
              <span class="font-medium text-gray-700">需要提示:</span>
              <span class="ml-2" :class="sessionMetadata.should_remind ? 'text-red-600 font-bold' : 'text-green-600'">
                {{ sessionMetadata.should_remind ? '是' : '否' }}
              </span>
            </div>
            <div>
              <span class="font-medium text-gray-700">提示次数:</span>
              <span class="ml-2 text-gray-900">{{ sessionMetadata.overtime_reminder_count }}</span>
            </div>
          </div>
          <button
            @click="refreshMetadata"
            class="text-xs px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700"
          >
            刷新
          </button>
        </div>
      </div>
    </div>

    <div class="flex-1 max-w-4xl w-full mx-auto px-4 py-6 flex flex-col">
      <MessageList :messages="messages" :loading="messagesLoading" class="flex-1" />
      <ChatInput @send="handleSendMessage" :disabled="sending || !currentSessionId" />
    </div>

    <!-- 结束咨询确认弹窗 -->
    <ConfirmEndSessionModal
      :show="showConfirmModal"
      :loading="isEndingSession"
      @confirm="handleConfirmEnd"
      @leave="handleLeave"
      @close="() => showConfirmModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { sessionsAPI } from '@/features/consult/api/sessions'
import MessageList from '@/features/consult/components/MessageList.vue'
import ChatInput from '@/features/consult/components/ChatInput.vue'
import ConfirmEndSessionModal from '@/features/consult/components/ConfirmEndSessionModal.vue'

const router = useRouter()
const route = useRoute()

const currentSessionId = ref(null)
const messages = ref([])
const messagesLoading = ref(false)
const sending = ref(false)

// 新增：弹窗相关状态
const showConfirmModal = ref(false)
const isEndingSession = ref(false)
const pendingAction = ref(null) // "back" 或 "end"

// 新增：计时器和调试相关状态
const frontendDuration = ref(0) // 前端计时器累计秒数
const sessionMetadata = ref({
  active_duration_seconds: 0,
  turn_count: 0,
  overtime_reminder_count: 0,
  should_remind: false
})
let timer = null // SessionTimer 实例
let displayInterval = null // 用于更新显示的定时器

// SessionTimer 类
class SessionTimer {
  constructor(sessionId) {
    this.sessionId = sessionId
    this.startTime = 0
    this.accumulatedSeconds = 0
    this.isActive = false

    // 从 localStorage 恢复
    this.loadFromStorage()
  }

  start() {
    if (this.isActive) return
    this.isActive = true
    this.startTime = Date.now()
    this.saveToStorage()
  }

  pause() {
    if (!this.isActive) return
    this.updateAccumulated()
    this.isActive = false
    this.saveToStorage()
  }

  updateAccumulated() {
    if (this.isActive) {
      const elapsed = Math.floor((Date.now() - this.startTime) / 1000)
      this.accumulatedSeconds += elapsed
      this.startTime = Date.now()
    }
  }

  getAccumulatedSeconds() {
    this.updateAccumulated()
    return this.accumulatedSeconds
  }

  saveToStorage() {
    if (!this.sessionId) return
    const data = {
      accumulatedSeconds: this.accumulatedSeconds,
      isActive: this.isActive,
      startTime: this.startTime
    }
    localStorage.setItem(`session_timer_${this.sessionId}`, JSON.stringify(data))
  }

  loadFromStorage() {
    if (!this.sessionId) return
    const stored = localStorage.getItem(`session_timer_${this.sessionId}`)
    if (stored) {
      try {
        const data = JSON.parse(stored)
        this.accumulatedSeconds = data.accumulatedSeconds || 0
        this.isActive = data.isActive || false
        this.startTime = data.startTime || Date.now()

        // 如果之前是活跃状态，继续计时
        if (this.isActive) {
          this.start()
        }
      } catch (e) {
        console.error('Failed to load timer from storage:', e)
      }
    }
  }

  clear() {
    if (!this.sessionId) return
    localStorage.removeItem(`session_timer_${this.sessionId}`)
  }
}

// 格式化时长显示（秒 -> MM:SS）
function formatDuration(seconds) {
  if (!seconds) return '00:00'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
}

// 初始化计时器
function initTimer(sessionId) {
  if (timer) {
    timer.pause()
    clearInterval(displayInterval)
  }

  timer = new SessionTimer(sessionId)
  timer.start()

  // 每秒更新显示
  displayInterval = setInterval(() => {
    frontendDuration.value = timer.getAccumulatedSeconds()
  }, 1000)

  console.log('Timer initialized for session:', sessionId)
}

// 刷新元数据
async function refreshMetadata() {
  if (!currentSessionId.value) return
  try {
    const response = await sessionsAPI.getSession(currentSessionId.value)
    sessionMetadata.value = {
      active_duration_seconds: response.data.active_duration_seconds || 0,
      turn_count: response.data.turn_count || 0,
      overtime_reminder_count: response.data.overtime_reminder_count || 0,
      should_remind: response.data.should_remind || false
    }
  } catch (err) {
    console.error('Failed to refresh metadata:', err)
  }
}

async function startSession() {
  try {
    const response = await sessionsAPI.startSession()
    currentSessionId.value = response.data.session_id

    // 初始化计时器
    initTimer(currentSessionId.value)

    // Load opening message from therapist
    // Add a small delay to ensure backend has finished generating
    await new Promise(resolve => setTimeout(resolve, 500))
    await loadExistingSession(currentSessionId.value)
  } catch (err) {
    console.error('Failed to start session:', err)
  }
}

async function loadExistingSession(sessionId) {
  messagesLoading.value = true
  try {
    currentSessionId.value = sessionId

    // 初始化计时器（如果还没有）
    if (!timer || timer.sessionId !== sessionId) {
      initTimer(sessionId)
    }

    const response = await sessionsAPI.getSessionMessages(sessionId)
    // 后端返回的是直接的消息数组，需要转换格式
    const backendMessages = response.data || []
    messages.value = backendMessages.map(msg => ({
      id: msg.id,
      role: msg.sender === 'user' ? 'user' : 'assistant',
      content: msg.message,
      // 兼容处理：支持 Unix timestamp (number) 和 ISO 字符串
      timestamp: typeof msg.created_at === 'number'
        ? new Date(msg.created_at * 1000).toISOString()
        : msg.created_at
    }))

    // 刷新元数据
    await refreshMetadata()
  } catch (err) {
    console.error('Failed to load session messages:', err)
    messages.value = []
  } finally {
    messagesLoading.value = false
  }
}

async function handleSendMessage(content) {
  if (!currentSessionId.value || !content.trim()) return

  // 立即显示用户消息（临时 ID）
  const tempUserMessage = {
    id: `temp-user-${Date.now()}`,
    role: 'user',
    content: content.trim(),
    timestamp: new Date().toISOString()
  }
  messages.value.push(tempUserMessage)

  sending.value = true

  try {
    // 获取当前累计时长
    const activeDurationSeconds = timer ? timer.getAccumulatedSeconds() : 0
    console.log('Sending message with duration:', activeDurationSeconds, 'seconds')

    // 发送消息到后端（后端会保存用户消息和生成系统回复）
    await sessionsAPI.sendMessage(currentSessionId.value, content.trim(), activeDurationSeconds)

    // 发送成功后，从后端重新加载所有消息以确保同步
    // 这样可以获取真实的消息 ID 和时间戳
    await loadExistingSession(currentSessionId.value)
  } catch (err) {
    console.error('Failed to send message:', err)
    // 移除临时用户消息
    messages.value = messages.value.filter(msg => msg.id !== tempUserMessage.id)

    // 显示错误消息
    const errorMessage = {
      id: `error-${Date.now()}`,
      role: 'assistant',
      content: '抱歉，发送消息失败，请稍后重试。',
      timestamp: new Date().toISOString()
    }
    messages.value.push(errorMessage)
  } finally {
    sending.value = false
  }
}

// 修改：返回按钮点击处理
function handleBackClick() {
  pendingAction.value = 'back'
  showConfirmModal.value = true
}

// 修改：结束咨询按钮点击处理
function handleEndSessionClick() {
  if (!currentSessionId.value) return
  pendingAction.value = 'end'
  showConfirmModal.value = true
}

// 新增：处理"暂时离开"
function handleLeave() {
  showConfirmModal.value = false
  router.push('/app/overview')
}

// 新增：处理"结束咨询"
async function handleConfirmEnd() {
  if (!currentSessionId.value) return

  isEndingSession.value = true

  try {
    await sessionsAPI.endSession(currentSessionId.value)
    isEndingSession.value = false
    showConfirmModal.value = false
    router.push('/app/overview?refresh=1')
  } catch (err) {
    console.error('Failed to end session:', err)
    isEndingSession.value = false
    // 保持弹窗打开，用户可以重试或选择暂时离开
  }
}

onMounted(async () => {
  const sessionId = route.query.session_id
  if (sessionId) {
    // Check if session is closed before loading
    try {
      const sessionResponse = await sessionsAPI.getSession(sessionId)
      const session = sessionResponse.data

      // Redirect to overview if session is closed
      if (session.is_closed || session.end_time) {
        router.replace('/app/overview')
        return
      }

      // Session is active, load messages
      loadExistingSession(sessionId)
    } catch (err) {
      console.error('Failed to get session:', err)
      router.replace('/app/overview')
    }
  } else {
    // No session_id in URL, check if user has an active session
    try {
      const activeResponse = await sessionsAPI.checkActiveSession()
      if (activeResponse.data.active && activeResponse.data.session_id) {
        // User has an active session, resume it
        console.log('Resuming active session:', activeResponse.data.session_id)
        loadExistingSession(activeResponse.data.session_id)
      } else {
        // No active session, start a new one
        console.log('No active session, starting new session')
        startSession()
      }
    } catch (err) {
      console.error('Failed to check active session:', err)
      // If check fails, still start a new session
      startSession()
    }
  }

  // 监听页面可见性变化
  const handleVisibilityChange = () => {
    if (document.hidden) {
      // 页面隐藏，暂停计时
      if (timer) {
        timer.pause()
        console.log('Page hidden, timer paused')
      }
    } else {
      // 页面显示，恢复计时
      if (timer) {
        timer.start()
        console.log('Page visible, timer resumed')
      }
    }
  }

  document.addEventListener('visibilitychange', handleVisibilityChange)

  // 保存监听器引用以便清理
  window._visibilityChangeHandler = handleVisibilityChange
})

onUnmounted(() => {
  // 清理计时器
  if (timer) {
    timer.pause()
    timer.saveToStorage()
  }
  if (displayInterval) {
    clearInterval(displayInterval)
  }

  // 移除页面可见性监听
  if (window._visibilityChangeHandler) {
    document.removeEventListener('visibilitychange', window._visibilityChangeHandler)
    delete window._visibilityChangeHandler
  }

  console.log('ConsultPage unmounted, timer saved')
})
</script>
