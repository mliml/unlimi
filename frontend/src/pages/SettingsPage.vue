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
            <h1 class="text-xl font-bold text-gray-800">设置</h1>
          </div>
        </div>
      </div>
    </nav>

    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="bg-white rounded-lg shadow">
        <div class="p-6 space-y-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-800 mb-4">咨询偏好</h3>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  咨询时长
                </label>
                <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-600">
                  45 分钟（只读）
                </div>
                <p class="text-xs text-gray-500 mt-1">系统默认时长，暂不支持修改</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  咨询师风格
                </label>
                <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-600">
                  温暖、共情、支持性（只读）
                </div>
                <p class="text-xs text-gray-500 mt-1">基于您的问卷自动生成</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  个性化咨询师 Prompt
                </label>
                <textarea
                  rows="6"
                  readonly
                  class="w-full px-4 py-3 bg-gray-50 rounded-lg text-gray-600 resize-none border border-gray-200"
                  :value="customPrompt"
                ></textarea>
                <p class="text-xs text-gray-500 mt-1">系统根据您的情况自动生成，暂不支持编辑</p>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-200 pt-6">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">账户信息</h3>

            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  邮箱
                </label>
                <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-600">
                  user@example.com
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  注册时间
                </label>
                <div class="px-4 py-3 bg-gray-50 rounded-lg text-gray-600">
                  2024-01-15
                </div>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-200 pt-6">
            <button
              @click="handleDeleteAccount"
              class="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              删除账户
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const customPrompt = ref(`你是一位专业的心理咨询师，具有温暖、共情和支持性的特点。

在咨询过程中，你会：
- 倾听来访者的困扰，理解他们的感受
- 提供专业的心理学见解和建议
- 帮助来访者探索问题的根源
- 支持来访者找到自己的解决方案

请保持专业、尊重和保密的原则。`)

function handleDeleteAccount() {
  const confirmed = confirm('确定要删除账户吗？此操作无法撤销。')
  if (confirmed) {
    alert('删除账户功能暂未实现')
  }
}
</script>
