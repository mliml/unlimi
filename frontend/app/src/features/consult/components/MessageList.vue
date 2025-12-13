<template>
  <div class="flex flex-col space-y-4 overflow-y-auto h-full p-4">
    <div v-if="loading" class="flex justify-center items-center h-full">
      <div class="text-gray-500">加载中...</div>
    </div>

    <div v-else-if="messages.length === 0" class="flex justify-center items-center h-full">
      <div class="text-gray-500 text-center">
        <div class="text-lg mb-2">还没有消息</div>
        <div class="text-sm">开始您的咨询吧</div>
      </div>
    </div>

    <div
      v-else
      v-for="message in messages"
      :key="message.id"
      :class="[
        'flex',
        message.role === 'user' ? 'justify-end' : 'justify-start'
      ]"
    >
      <div
        :class="[
          'max-w-[70%] rounded-lg px-4 py-3',
          message.role === 'user'
            ? 'bg-primary-600 text-white'
            : 'bg-gray-100 text-gray-800'
        ]"
      >
        <div class="whitespace-pre-wrap break-words">{{ message.content }}</div>
        <div
          :class="[
            'text-xs mt-2',
            message.role === 'user' ? 'text-primary-100' : 'text-gray-500'
          ]"
        >
          {{ formatTime(message.timestamp) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
//import { defineProps } from 'vue'

defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

function formatTime(timestamp) {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
