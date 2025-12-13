<template>
  <div class="min-h-screen bg-gray-50">
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <button
              @click="$router.push('/app/overview')"
              class="text-gray-600 hover:text-gray-800"
            >
              ← 返回
            </button>
            <h1 class="text-xl font-bold text-gray-800">过往咨询</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <SessionList
            :sessions="sessions"
            :loading="sessionsLoading"
            :selected-id="selectedSessionId"
            @select="handleSelectSession"
          />
        </div>

        <div class="lg:col-span-2">
          <div v-if="!selectedSessionId" class="bg-white rounded-lg shadow p-8 text-center text-gray-500">
            请从左侧选择一个会话
          </div>

          <div v-else class="bg-white rounded-lg shadow">
            <div class="border-b border-gray-200">
              <nav class="flex -mb-px">
                <button
                  @click="activeTab = 'chat'"
                  :class="[
                    'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                    activeTab === 'chat'
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  对话记录
                </button>
                <button
                  @click="activeTab = 'plan'"
                  :class="[
                    'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                    activeTab === 'plan'
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  咨询计划
                </button>
                <button
                  @click="activeTab = 'review'"
                  :class="[
                    'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                    activeTab === 'review'
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  咨询回顾
                </button>
              </nav>
            </div>

            <div class="p-6">
              <div v-if="detailLoading" class="text-center text-gray-500 py-8">
                加载中...
              </div>

              <div v-else>
                <div v-if="activeTab === 'chat'">
                  <MessageList :messages="currentMessages" :loading="false" />
                </div>

                <div v-if="activeTab === 'plan'" class="prose max-w-none">
                  <h3 class="text-lg font-semibold text-gray-800 mb-4">咨询计划</h3>
                  <div class="text-gray-700 whitespace-pre-wrap">
                    暂无咨询计划
                  </div>
                </div>

                <div v-if="activeTab === 'review'" class="prose max-w-none">
                  <h3 class="text-lg font-semibold text-gray-800 mb-4">咨询回顾</h3>
                  <div v-if="sessionDetail && sessionDetail.review_text" class="mb-6">
                    <div class="text-gray-700 whitespace-pre-wrap">
                      {{ sessionDetail.review_text }}
                    </div>
                  </div>
                  <div v-if="sessionDetail && sessionDetail.key_events && sessionDetail.key_events.length > 0" class="mb-6">
                    <h4 class="text-md font-semibold text-gray-800 mb-2">关键事件</h4>
                    <ul class="list-disc list-inside space-y-1">
                      <li v-for="(event, index) in sessionDetail.key_events" :key="index" class="text-gray-700">
                        {{ event }}
                      </li>
                    </ul>
                  </div>
                  <div v-if="!sessionDetail || (!sessionDetail.review_text && (!sessionDetail.key_events || sessionDetail.key_events.length === 0))" class="text-gray-500">
                    暂无回顾内容
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { sessionsAPI } from '@/features/consult/api/sessions'
import SessionList from '@/features/consult/components/SessionList.vue'
import MessageList from '@/features/consult/components/MessageList.vue'

const sessions = ref([])
const sessionsLoading = ref(false)
const selectedSessionId = ref(null)
const activeTab = ref('chat')
const detailLoading = ref(false)
const messages = ref([])
const sessionDetail = ref(null)

// Transform messages for MessageList component
const currentMessages = computed(() => {
  return messages.value.map(msg => ({
    id: msg.id,
    role: msg.sender === 'user' ? 'user' : 'assistant',
    content: msg.message,
    // 兼容处理：支持 Unix timestamp (number) 和 ISO 字符串
    timestamp: typeof msg.created_at === 'number'
      ? new Date(msg.created_at * 1000).toISOString()
      : msg.created_at
  }))
})

// Format date time helper
function formatDateTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

async function loadHistory() {
  sessionsLoading.value = true
  try {
    const res = await sessionsAPI.getHistorySessions()
    sessions.value = (res.data || []).map(item => ({
      ...item,
      created_at: `第 ${item.index} 次咨询`,
      summary: `${formatDateTime(item.start_time)} ~ ${formatDateTime(item.end_time)}`
    })).reverse()

    // Auto-select the most recent session (first one in the array after reverse)
    if (sessions.value.length > 0) {
      await selectSession(sessions.value[0].id)
    }
  } catch (err) {
    console.error('Failed to load history sessions:', err)
  } finally {
    sessionsLoading.value = false
  }
}

async function selectSession(id) {
  selectedSessionId.value = id
  await Promise.all([
    loadSessionDetail(id),
    loadSessionMessages(id)
  ])
}

async function loadSessionDetail(id) {
  try {
    const res = await sessionsAPI.getSession(id)
    sessionDetail.value = res.data
  } catch (err) {
    console.error('Failed to load session detail:', err)
  }
}

async function loadSessionMessages(id) {
  detailLoading.value = true
  try {
    const res = await sessionsAPI.getSessionMessages(id)
    messages.value = res.data || []
  } catch (err) {
    console.error('Failed to load session messages:', err)
  } finally {
    detailLoading.value = false
  }
}

async function handleSelectSession(sessionId) {
  activeTab.value = 'chat'
  await selectSession(sessionId)
}

onMounted(() => {
  loadHistory()
})
</script>
