<template>
  <div class="space-y-6">
    <div>
      <label class="block text-lg font-medium text-gray-700 mb-4">
        {{ question.question_text }}
      </label>
      <textarea
        v-model="answer"
        rows="6"
        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none"
        placeholder="请输入您的答案..."
        :disabled="submitting"
      ></textarea>
    </div>

    <div class="flex justify-end">
      <button
        @click="handleSubmit"
        :disabled="submitting || !answer.trim()"
        class="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ submitting ? '提交中...' : '下一题' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  submitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const answer = ref('')

function handleSubmit() {
  if (answer.value.trim()) {
    emit('submit', answer.value.trim())
    answer.value = ''
  }
}
</script>
