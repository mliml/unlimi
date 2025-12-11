<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 顶部导航栏 -->
    <nav class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <button
              @click="$router.push('/app/overview')"
              class="text-gray-600 hover:text-gray-800 transition"
            >
              ← 返回
            </button>
            <h1 class="text-xl font-bold text-gray-800">管理后台</h1>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区 -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <!-- 侧边栏 + 内容区域 -->
      <div class="flex gap-6">
        <!-- 侧边栏 -->
        <div class="w-64 flex-shrink-0">
          <div class="bg-white rounded-lg shadow p-4">
            <nav class="space-y-2">
              <button
                @click="activeSidebarTab = 'prompts'"
                :class="[
                  'w-full text-left px-4 py-2 rounded-lg transition',
                  activeSidebarTab === 'prompts'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                提示词配置
              </button>
              <button
                @click="activeSidebarTab = 'session-config'"
                :class="[
                  'w-full text-left px-4 py-2 rounded-lg transition',
                  activeSidebarTab === 'session-config'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                咨询时间配置
              </button>
              <button
                @click="activeSidebarTab = 'invitation-codes'"
                :class="[
                  'w-full text-left px-4 py-2 rounded-lg transition',
                  activeSidebarTab === 'invitation-codes'
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 hover:bg-gray-100'
                ]"
              >
                邀请码管理
              </button>
              <button
                :class="[
                  'w-full text-left px-4 py-2 rounded-lg transition',
                  'text-gray-700 hover:bg-gray-100 opacity-50 cursor-not-allowed'
                ]"
                disabled
              >
                系统配置 <span class="text-xs">(未来)</span>
              </button>
              <button
                :class="[
                  'w-full text-left px-4 py-2 rounded-lg transition',
                  'text-gray-700 hover:bg-gray-100 opacity-50 cursor-not-allowed'
                ]"
                disabled
              >
                日志查看 <span class="text-xs">(未来)</span>
              </button>
            </nav>
          </div>
        </div>

        <!-- 主内容区 -->
        <div class="flex-1">
          <!-- 提示词配置 Tab -->
          <div v-if="activeSidebarTab === 'prompts'" class="bg-white rounded-lg shadow">
            <!-- Prompt Tab 标签 -->
            <div v-if="!initialLoading" class="border-b border-gray-200">
              <div class="flex space-x-4 px-6 overflow-x-auto">
                <button
                  v-for="(tab, index) in tabs"
                  :key="tab.key"
                  @click="switchTab(index)"
                  :class="[
                    'py-4 px-4 border-b-2 font-medium text-sm transition whitespace-nowrap',
                    activeTabIndex === index
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  {{ tab.label }}
                </button>
              </div>
            </div>

            <!-- 初始加载状态 -->
            <div v-if="initialLoading" class="p-12 text-center">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p class="mt-4 text-gray-600">加载中...</p>
            </div>

            <!-- 初始错误状态 -->
            <div v-else-if="initialError" class="p-12 text-center">
              <div class="text-red-600 mb-4">
                <svg class="mx-auto h-12 w-12 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p class="font-medium">加载失败</p>
                <p class="text-sm mt-2">{{ initialError }}</p>
              </div>
              <button
                @click="initPage"
                class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition"
              >
                重试
              </button>
            </div>

            <!-- 提示词编辑器 -->
            <div v-else class="p-6">
              <!-- 治疗师选择器 (仅 therapist-person tab) -->
              <div v-if="currentTab.type === 'therapist'" class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  选择治疗师
                </label>
                <select
                  v-model="selectedTherapistId"
                  @change="onTherapistChange"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option
                    v-for="therapist in therapists"
                    :key="therapist.id"
                    :value="therapist.id"
                  >
                    {{ therapist.id }} - {{ therapist.name }}
                  </option>
                </select>
                <p v-if="currentTherapistInfo" class="text-sm text-gray-500 mt-2">
                  {{ currentTherapistInfo }}
                </p>
              </div>

              <!-- Tab 标题 -->
              <div class="mb-6">
                <h2 class="text-lg font-semibold text-gray-800">
                  {{ currentTab.label }}
                  <span v-if="currentTab.type === 'therapist' && selectedTherapistId" class="text-gray-500 font-normal text-base">
                    - {{ selectedTherapistId }}
                  </span>
                </h2>
                <p v-if="currentTab.type === 'file'" class="text-sm text-gray-600 mt-1">
                  文件: {{ currentFilePromptPath }}
                </p>
              </div>

              <!-- 提示词内容编辑器 -->
              <div class="mb-4">
                <div class="flex justify-between items-center mb-2">
                  <label class="block text-sm font-medium text-gray-700">
                    提示词内容
                  </label>
                  <span class="text-sm text-gray-500">
                    {{ currentContent.length }} 字符
                  </span>
                </div>
                <textarea
                  v-model="currentContent"
                  rows="20"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
                  placeholder="输入系统提示词..."
                  @input="markAsModified"
                ></textarea>
              </div>

              <!-- 操作按钮 -->
              <div class="flex justify-between items-center">
                <div>
                  <span v-if="isModified" class="text-sm text-orange-600 font-medium">
                    ⚠️ 未保存的更改
                  </span>
                </div>
                <div class="flex gap-3">
                  <button
                    @click="resetContent"
                    :disabled="!isModified"
                    class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    重置
                  </button>
                  <button
                    @click="save"
                    :disabled="saving || !isModified"
                    class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    {{ saving ? '保存中...' : '保存' }}
                  </button>
                </div>
              </div>

              <!-- 成功提示 -->
              <transition name="fade">
                <div
                  v-if="saveSuccess"
                  class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800 flex items-center"
                >
                  <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  保存成功！配置已更新。
                </div>
              </transition>

              <!-- 错误提示 -->
              <transition name="fade">
                <div
                  v-if="saveError"
                  class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 flex items-start"
                >
                  <svg class="h-5 w-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p class="font-medium">保存失败</p>
                    <p class="text-sm mt-1">{{ saveError }}</p>
                  </div>
                </div>
              </transition>
            </div>
          </div>

          <!-- 咨询时间配置 Tab -->
          <div v-else-if="activeSidebarTab === 'session-config'" class="bg-white rounded-lg shadow">
            <!-- 初始加载状态 -->
            <div v-if="sessionConfigLoading" class="p-12 text-center">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p class="mt-4 text-gray-600">加载中...</p>
            </div>

            <!-- 配置表单 -->
            <div v-else class="p-6">
              <div class="mb-6">
                <h2 class="text-lg font-semibold text-gray-800">咨询时间配置</h2>
                <p class="text-sm text-gray-600 mt-1">配置单次咨询的建议时长和对话轮数，修改后需要重启后端服务生效</p>
              </div>

              <!-- 配置项 -->
              <div class="space-y-6 max-w-2xl">
                <!-- 建议时长 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    建议咨询时长（分钟）
                  </label>
                  <input
                    v-model.number="sessionConfig.suggested_duration_minutes"
                    type="number"
                    min="1"
                    max="120"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    @input="markSessionConfigModified"
                  />
                  <p class="text-sm text-gray-500 mt-1">范围：1-120 分钟，超过建议时长且超过建议轮数后会提示用户</p>
                </div>

                <!-- 建议轮数 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    建议对话轮数
                  </label>
                  <input
                    v-model.number="sessionConfig.suggested_turns"
                    type="number"
                    min="1"
                    max="200"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    @input="markSessionConfigModified"
                  />
                  <p class="text-sm text-gray-500 mt-1">范围：1-200 轮，一轮 = 用户提问 + AI 回答</p>
                </div>

                <!-- 提示间隔 -->
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    提示间隔（轮）
                  </label>
                  <input
                    v-model.number="sessionConfig.reminder_interval"
                    type="number"
                    min="1"
                    max="10"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    @input="markSessionConfigModified"
                  />
                  <p class="text-sm text-gray-500 mt-1">范围：1-10 轮，超时后每 N 轮提示一次</p>
                </div>
              </div>

              <!-- 操作按钮 -->
              <div class="flex justify-between items-center mt-8 max-w-2xl">
                <div>
                  <span v-if="sessionConfigModified" class="text-sm text-orange-600 font-medium">
                    ⚠️ 未保存的更改
                  </span>
                </div>
                <div class="flex gap-3">
                  <button
                    @click="resetSessionConfig"
                    :disabled="!sessionConfigModified"
                    class="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    重置
                  </button>
                  <button
                    @click="saveSessionConfig"
                    :disabled="sessionConfigSaving || !sessionConfigModified"
                    class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                  >
                    {{ sessionConfigSaving ? '保存中...' : '保存' }}
                  </button>
                </div>
              </div>

              <!-- 成功提示 -->
              <transition name="fade">
                <div
                  v-if="sessionConfigSuccess"
                  class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800 flex items-center max-w-2xl"
                >
                  <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                  保存成功！配置已更新到 .env 文件，请重启后端服务生效。
                </div>
              </transition>

              <!-- 错误提示 -->
              <transition name="fade">
                <div
                  v-if="sessionConfigError"
                  class="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 flex items-start max-w-2xl"
                >
                  <svg class="h-5 w-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p class="font-medium">保存失败</p>
                    <p class="text-sm mt-1">{{ sessionConfigError }}</p>
                  </div>
                </div>
              </transition>
            </div>
          </div>

          <!-- 邀请码管理 Tab -->
          <div v-else-if="activeSidebarTab === 'invitation-codes'" class="bg-white rounded-lg shadow">
            <!-- 头部 -->
            <div class="p-6 border-b border-gray-200">
              <div class="flex justify-between items-center">
                <div>
                  <h2 class="text-lg font-semibold text-gray-800">邀请码管理</h2>
                  <p class="text-sm text-gray-600 mt-1">生成和管理用户注册邀请码</p>
                </div>
                <button
                  @click="generateInvitationCode"
                  :disabled="invitationCodesLoading"
                  class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                  </svg>
                  生成新邀请码
                </button>
              </div>
            </div>

            <!-- 成功提示 -->
            <transition name="fade">
              <div
                v-if="invitationCodesSuccess"
                class="mx-6 mt-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-800 flex items-center"
              >
                <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {{ invitationCodesSuccess }}
              </div>
            </transition>

            <!-- 错误提示 -->
            <transition name="fade">
              <div
                v-if="invitationCodesError"
                class="mx-6 mt-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 flex items-start"
              >
                <svg class="h-5 w-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <p class="font-medium">操作失败</p>
                  <p class="text-sm mt-1">{{ invitationCodesError }}</p>
                </div>
              </div>
            </transition>

            <!-- 加载状态 -->
            <div v-if="invitationCodesLoading" class="p-12 text-center">
              <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
              <p class="mt-4 text-gray-600">加载中...</p>
            </div>

            <!-- 邀请码列表 -->
            <div v-else class="p-6">
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        邀请码
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        状态
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        注册账号
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        创建时间
                      </th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        操作
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="code in invitationCodes" :key="code.id" class="hover:bg-gray-50">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center gap-2">
                          <span class="font-mono text-sm font-medium text-gray-900">{{ code.code }}</span>
                          <span
                            v-if="code.is_universal"
                            class="px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800"
                          >
                            万能
                          </span>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span
                          :class="[
                            'px-2 py-1 text-xs font-medium rounded-full',
                            code.is_used
                              ? 'bg-gray-100 text-gray-800'
                              : 'bg-green-100 text-green-800'
                          ]"
                        >
                          {{ code.is_used ? '已使用' : '未使用' }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {{ code.used_by_email || '-' }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {{ formatDate(code.created_at) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          v-if="!code.is_universal && !code.is_used"
                          @click="deleteInvitationCode(code.id)"
                          class="text-red-600 hover:text-red-900 transition"
                        >
                          删除
                        </button>
                        <span v-else class="text-gray-400">-</span>
                      </td>
                    </tr>
                    <tr v-if="invitationCodes.length === 0">
                      <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                        暂无邀请码，点击上方按钮生成
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <!-- 其他 Tab (占位) -->
          <div v-else class="bg-white rounded-lg shadow p-12 text-center">
            <p class="text-gray-500">该功能即将上线...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  getFilePrompts,
  updateFilePrompt,
  getTherapists,
  getTherapist,
  updateTherapistPrompt,
  getSessionConfig,
  updateSessionConfig,
  getInvitationCodes,
  createInvitationCode,
  deleteInvitationCodeById
} from '@/api/admin'

// ============ Tab 配置 ============

const tabs = [
  { key: 'onboarding', label: 'Onboarding', type: 'file' },
  { key: 'clerk', label: 'Clerk', type: 'file' },
  { key: 'clerk_over', label: 'Clerk Over', type: 'file' },
  { key: 'therapist-general', label: 'Therapist General', type: 'file' },
  { key: 'therapist-person', label: 'Therapist Person', type: 'therapist' }
]

// ============ 状态管理 ============

// 侧边栏
const activeSidebarTab = ref('prompts')

// Tab 状态
const activeTabIndex = ref(0)

// 文件型 prompts 缓存
const filePrompts = ref([])

// 治疗师数据
const therapists = ref([])
const selectedTherapistId = ref(null)

// 编辑状态
const currentContent = ref('')
const originalContent = ref('')
const isModified = ref(false)

// UI 状态
const initialLoading = ref(false)
const initialError = ref(null)
const saving = ref(false)
const saveSuccess = ref(false)
const saveError = ref(null)

// Session 配置状态
const sessionConfig = ref({
  suggested_duration_minutes: 30,
  suggested_turns: 30,
  reminder_interval: 3
})
const originalSessionConfig = ref({})
const sessionConfigModified = ref(false)
const sessionConfigLoading = ref(false)
const sessionConfigSaving = ref(false)
const sessionConfigSuccess = ref(false)
const sessionConfigError = ref(null)

// 邀请码管理状态
const invitationCodes = ref([])
const invitationCodesLoading = ref(false)
const invitationCodesSuccess = ref('')
const invitationCodesError = ref('')

// ============ 计算属性 ============

const currentTab = computed(() => {
  return tabs[activeTabIndex.value]
})

const currentFilePromptPath = computed(() => {
  if (currentTab.value.type !== 'file') return ''
  const prompt = filePrompts.value.find(p => p.key === currentTab.value.key)
  return prompt?.file_path || ''
})

const currentTherapistInfo = computed(() => {
  if (!selectedTherapistId.value) return ''
  const therapist = therapists.value.find(t => t.id === selectedTherapistId.value)
  return therapist ? `${therapist.age}岁 - ${therapist.info}` : ''
})

// ============ 核心逻辑 ============

/**
 * 页面初始化
 */
const initPage = async () => {
  initialLoading.value = true
  initialError.value = null

  try {
    console.log('开始初始化 Admin 页面...')

    // 1. 加载文件型 prompts
    const filePromptsData = await getFilePrompts()
    console.log('文件型 prompts 加载成功:', filePromptsData)
    filePrompts.value = filePromptsData.prompts

    // 2. 加载治疗师列表
    const therapistsData = await getTherapists()
    console.log('治疗师列表加载成功:', therapistsData)
    therapists.value = therapistsData

    // 3. 初始化第一个 tab
    await switchTab(0, true)

    console.log('Admin 页面初始化完成')
  } catch (err) {
    console.error('初始化失败:', err)
    initialError.value = err.response?.data?.detail || err.message || '加载失败，请检查后端服务是否启动'
  } finally {
    initialLoading.value = false
  }
}

/**
 * 切换 Tab
 */
const switchTab = async (tabIndex, isInit = false) => {
  // 检查是否有未保存的更改（初始化时跳过）
  if (!isInit && isModified.value) {
    const confirmed = confirm('有未保存的更改，确定要切换吗？')
    if (!confirmed) return
  }

  console.log(`切换到 Tab ${tabIndex}: ${tabs[tabIndex].label}`)

  const tab = tabs[tabIndex]
  activeTabIndex.value = tabIndex

  try {
    if (tab.type === 'file') {
      // 文件型 tab: 从缓存加载
      const prompt = filePrompts.value.find(p => p.key === tab.key)
      if (!prompt) {
        throw new Error(`Prompt not found: ${tab.key}`)
      }
      currentContent.value = prompt.content
      originalContent.value = prompt.content
      console.log(`加载文件 prompt: ${tab.key}, ${prompt.content.length} 字符`)
    } else {
      // 治疗师 tab: 加载第一个治疗师
      if (therapists.value.length === 0) {
        throw new Error('没有可用的治疗师')
      }
      selectedTherapistId.value = therapists.value[0].id
      await loadTherapistPrompt(therapists.value[0].id)
    }

    isModified.value = false
    saveSuccess.value = false
    saveError.value = null
  } catch (err) {
    console.error('切换 Tab 失败:', err)
    initialError.value = err.message
  }
}

/**
 * 治疗师选择器变化
 */
const onTherapistChange = async () => {
  // 检查是否有未保存的更改
  if (isModified.value) {
    const confirmed = confirm('有未保存的更改，确定要切换吗？')
    if (!confirmed) {
      // 恢复选择（这里需要保存之前的值，简化处理：重新选择）
      return
    }
  }

  await loadTherapistPrompt(selectedTherapistId.value)
}

/**
 * 加载治疗师 prompt
 */
const loadTherapistPrompt = async (therapistId) => {
  try {
    console.log(`加载治疗师 ${therapistId} 的 prompt...`)
    const therapist = await getTherapist(therapistId)
    console.log(`治疗师 prompt 加载成功: ${therapist.prompt?.length || 0} 字符`)

    currentContent.value = therapist.prompt || ''
    originalContent.value = therapist.prompt || ''
    isModified.value = false
    saveSuccess.value = false
    saveError.value = null
  } catch (err) {
    console.error('加载治疗师 prompt 失败:', err)
    saveError.value = err.response?.data?.detail || err.message || '加载失败'
  }
}

/**
 * 标记为已修改
 */
const markAsModified = () => {
  const hasChanged = currentContent.value !== originalContent.value
  isModified.value = hasChanged
  saveSuccess.value = false
  saveError.value = null
}

/**
 * 重置内容
 */
const resetContent = () => {
  currentContent.value = originalContent.value
  isModified.value = false
  saveSuccess.value = false
  saveError.value = null
}

/**
 * 保存
 */
const save = async () => {
  saving.value = true
  saveError.value = null
  saveSuccess.value = false

  try {
    console.log('开始保存...')
    const tab = currentTab.value

    if (tab.type === 'file') {
      // 保存文件型 prompt
      console.log(`保存文件 prompt: ${tab.key}`)
      const result = await updateFilePrompt(tab.key, currentContent.value)
      console.log('保存成功:', result)

      // 更新缓存
      const prompt = filePrompts.value.find(p => p.key === tab.key)
      if (prompt) {
        prompt.content = result.prompt.content
      }
      originalContent.value = currentContent.value
    } else {
      // 保存治疗师 prompt
      console.log(`保存治疗师 ${selectedTherapistId.value} 的 prompt`)
      await updateTherapistPrompt(selectedTherapistId.value, currentContent.value)
      console.log('保存成功')
      originalContent.value = currentContent.value
    }

    isModified.value = false
    saveSuccess.value = true

    // 3秒后隐藏成功提示
    setTimeout(() => {
      saveSuccess.value = false
    }, 3000)
  } catch (err) {
    console.error('保存失败:', err)
    saveError.value = err.response?.data?.detail || err.message || '保存失败，请稍后重试'
  } finally {
    saving.value = false
  }
}

// ============ Session 配置管理 ============

/**
 * 加载 Session 配置
 */
const loadSessionConfig = async () => {
  sessionConfigLoading.value = true
  sessionConfigError.value = null

  try {
    console.log('加载 Session 配置...')
    const data = await getSessionConfig()
    console.log('Session 配置加载成功:', data)

    sessionConfig.value = {
      suggested_duration_minutes: data.suggested_duration_minutes,
      suggested_turns: data.suggested_turns,
      reminder_interval: data.reminder_interval
    }
    originalSessionConfig.value = { ...sessionConfig.value }
    sessionConfigModified.value = false
  } catch (err) {
    console.error('加载 Session 配置失败:', err)
    sessionConfigError.value = err.response?.data?.detail || err.message || '加载失败'
  } finally {
    sessionConfigLoading.value = false
  }
}

/**
 * 标记配置已修改
 */
const markSessionConfigModified = () => {
  const hasChanged =
    sessionConfig.value.suggested_duration_minutes !== originalSessionConfig.value.suggested_duration_minutes ||
    sessionConfig.value.suggested_turns !== originalSessionConfig.value.suggested_turns ||
    sessionConfig.value.reminder_interval !== originalSessionConfig.value.reminder_interval

  sessionConfigModified.value = hasChanged
  sessionConfigSuccess.value = false
  sessionConfigError.value = null
}

/**
 * 重置配置
 */
const resetSessionConfig = () => {
  sessionConfig.value = { ...originalSessionConfig.value }
  sessionConfigModified.value = false
  sessionConfigSuccess.value = false
  sessionConfigError.value = null
}

/**
 * 保存配置
 */
const saveSessionConfig = async () => {
  sessionConfigSaving.value = true
  sessionConfigError.value = null
  sessionConfigSuccess.value = false

  try {
    console.log('保存 Session 配置:', sessionConfig.value)
    const result = await updateSessionConfig(sessionConfig.value)
    console.log('保存成功:', result)

    // 更新原始配置
    originalSessionConfig.value = { ...sessionConfig.value }
    sessionConfigModified.value = false
    sessionConfigSuccess.value = true

    // 3秒后隐藏成功提示
    setTimeout(() => {
      sessionConfigSuccess.value = false
    }, 3000)
  } catch (err) {
    console.error('保存 Session 配置失败:', err)
    sessionConfigError.value = err.response?.data?.detail || err.message || '保存失败，请稍后重试'
  } finally {
    sessionConfigSaving.value = false
  }
}

// ============ 邀请码管理 ============

/**
 * 加载邀请码列表
 */
const loadInvitationCodes = async () => {
  invitationCodesLoading.value = true
  invitationCodesError.value = ''

  try {
    console.log('加载邀请码列表...')
    const data = await getInvitationCodes()
    console.log('邀请码列表加载成功:', data)
    invitationCodes.value = data.codes
  } catch (err) {
    console.error('加载邀请码列表失败:', err)
    invitationCodesError.value = err.response?.data?.detail || err.message || '加载失败'
  } finally {
    invitationCodesLoading.value = false
  }
}

/**
 * 生成新邀请码
 */
const generateInvitationCode = async () => {
  invitationCodesError.value = ''
  invitationCodesSuccess.value = ''

  try {
    console.log('生成新邀请码...')
    const newCode = await createInvitationCode()
    console.log('邀请码生成成功:', newCode)

    invitationCodesSuccess.value = `邀请码 ${newCode.code} 生成成功！`

    // 重新加载列表
    await loadInvitationCodes()

    // 3秒后隐藏成功提示
    setTimeout(() => {
      invitationCodesSuccess.value = ''
    }, 3000)
  } catch (err) {
    console.error('生成邀请码失败:', err)
    invitationCodesError.value = err.response?.data?.detail || err.message || '生成失败'
  }
}

/**
 * 删除邀请码
 */
const deleteInvitationCode = async (codeId) => {
  if (!confirm('确定要删除这个邀请码吗？')) {
    return
  }

  invitationCodesError.value = ''
  invitationCodesSuccess.value = ''

  try {
    console.log('删除邀请码:', codeId)
    await deleteInvitationCodeById(codeId)
    console.log('邀请码删除成功')

    invitationCodesSuccess.value = '邀请码删除成功！'

    // 重新加载列表
    await loadInvitationCodes()

    // 3秒后隐藏成功提示
    setTimeout(() => {
      invitationCodesSuccess.value = ''
    }, 3000)
  } catch (err) {
    console.error('删除邀请码失败:', err)
    invitationCodesError.value = err.response?.data?.detail || err.message || '删除失败'
  }
}

/**
 * 格式化日期
 */
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// ============ 监听器 ============

// 监听侧边栏 Tab 切换
watch(activeSidebarTab, (newTab) => {
  if (newTab === 'session-config') {
    // 切换到咨询时间配置时加载数据
    loadSessionConfig()
  } else if (newTab === 'invitation-codes') {
    // 切换到邀请码管理时加载数据
    loadInvitationCodes()
  }
})

// ============ 生命周期 ============

onMounted(() => {
  console.log('AdminPage mounted')
  initPage()
})
</script>

<style scoped>
/* 过渡动画 */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
