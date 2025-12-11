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
            <h1 class="text-xl font-bold text-gray-800">整体回顾</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-white rounded-lg shadow">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              @click="activeTab = 'profile'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'profile'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              用户画像
            </button>
            <button
              @click="activeTab = 'timeline'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'timeline'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              重要事件
            </button>
            <button
              @click="activeTab = 'trends'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors',
                activeTab === 'trends'
                  ? 'border-primary-600 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              趋势分析
            </button>
          </nav>
        </div>

        <div class="p-6">
          <div v-if="activeTab === 'profile'">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">用户画像</h3>

            <div v-if="loading" class="bg-gray-50 rounded-lg p-6">
              <div class="flex items-center justify-center">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                <span class="ml-3 text-gray-600">加载中...</span>
              </div>
            </div>

            <div v-else-if="error" class="bg-red-50 rounded-lg p-6">
              <p class="text-red-600">{{ error }}</p>
            </div>

            <div v-else-if="profileItems.length === 0" class="bg-gray-50 rounded-lg p-6 text-gray-600">
              <p class="mb-4">基于您的咨询记录，我们为您生成了个性化的用户画像。</p>
              <div class="text-gray-600">暂无数据，请完成 onboarding 或继续咨询以生成画像</div>
            </div>

            <div v-else class="space-y-3">
              <p class="text-gray-600 mb-4">基于您的咨询记录，我们为您生成了个性化的用户画像。</p>
              <div
                v-for="item in profileItems"
                :key="item.id"
                class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div class="flex items-start justify-between">
                  <div class="flex-1">
                    <p class="text-gray-800 font-medium">{{ item.content }}</p>
                    <div class="flex items-center mt-2 space-x-3 text-sm text-gray-500">
                      <span class="flex items-center">
                        <span class="mr-1">来源:</span>
                        <span class="font-medium">{{ getSourceLabel(item.source) }}</span>
                      </span>
                      <span v-if="item.topics && item.topics.length > 0" class="flex items-center">
                        <span class="mr-1">标签:</span>
                        <span class="font-medium">{{ item.topics.join(', ') }}</span>
                      </span>
                      <span class="flex items-center">
                        <span class="mr-1">更新:</span>
                        <span>{{ formatDate(item.updated_at) }}</span>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'timeline'">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">重要事件时间线</h3>
            <div class="bg-gray-50 rounded-lg p-6 text-gray-600">
              <p class="mb-4">记录您在咨询过程中的重要时刻和转折点。</p>
              <div class="space-y-4">
                <div class="flex items-start">
                  <div class="flex-shrink-0 w-24 text-sm text-gray-500">2024-01-15</div>
                  <div class="flex-1">
                    <div class="font-medium text-gray-800">示例事件</div>
                    <div class="text-gray-600 text-sm mt-1">暂无真实数据，继续咨询后将自动生成</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="activeTab === 'trends'">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">近 5 次趋势分析</h3>
            <div class="bg-gray-50 rounded-lg p-6 text-gray-600">
              <p class="mb-4">分析您最近 5 次咨询的情绪和主题变化趋势。</p>
              <div class="space-y-6">
                <div>
                  <div class="text-sm font-medium text-gray-700 mb-2">情绪趋势</div>
                  <div class="h-40 bg-white rounded border border-gray-200 flex items-center justify-center text-gray-500">
                    图表占位（待实现）
                  </div>
                </div>
                <div>
                  <div class="text-sm font-medium text-gray-700 mb-2">主题分布</div>
                  <div class="h-40 bg-white rounded border border-gray-200 flex items-center justify-center text-gray-500">
                    图表占位（待实现）
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
import { ref, onMounted } from 'vue'
import { getUserMemories } from '@/api/profile'

const activeTab = ref('profile')
const profileItems = ref([])
const loading = ref(false)
const error = ref(null)

const fetchProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const memories = await getUserMemories()
    console.log("API raw response (memories):", memories)

    // 转换 Agno memories 格式为 profileItems 格式
    profileItems.value = memories.map(m => ({
      id: m.memory_id,
      content: m.memory,
      topics: m.topics || [],
      source: m.topics && m.topics.includes('migration') ? 'clerk' : 'clerk',
      updated_at: m.updated_at
    }))

    console.log("profileItems after set:", profileItems.value)

  } catch (err) {
    console.error('Failed to fetch memories:', err)
    error.value = err.response?.data?.detail || '加载用户画像失败'
  } finally {
    loading.value = false
  }
}

const getSourceLabel = (source) => {
  const labels = {
    onboarding: 'Onboarding',
    clerk: '咨询记录'
  }
  return labels[source] || source
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchProfile()
})
</script>
