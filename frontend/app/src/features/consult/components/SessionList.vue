<template>
  <div class="bg-white rounded-lg shadow">
    <div class="p-4 border-b border-gray-200">
      <h3 class="font-semibold text-gray-800">咨询记录</h3>
    </div>

    <div v-if="loading" class="p-4 text-center text-gray-500">
      加载中...
    </div>

    <div v-else-if="sessions.length === 0" class="p-4 text-center text-gray-500">
      暂无咨询记录
    </div>

    <div v-else class="divide-y divide-gray-200">
      <button
        v-for="session in sessions"
        :key="session.id"
        @click="$emit('select', session.id)"
        :class="[
          'w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors',
          selectedId === session.id ? 'bg-primary-50 border-l-4 border-primary-600' : ''
        ]"
      >
        <div class="font-medium text-gray-800">
          {{ session.created_at }}
        </div>
        <div class="text-sm text-gray-600 mt-1 truncate">
          {{ session.summary || '咨询会话' }}
        </div>
        <div class="text-xs text-gray-500 mt-1">
          {{ session.message_count || 0 }} 条消息
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
//import { defineProps, defineEmits } from 'vue'

defineProps({
  sessions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  selectedId: {
    type: [String, Number],
    default: null
  }
})

defineEmits(['select'])

function formatDate(dateString) {
  if (!dateString) return '未知时间'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
