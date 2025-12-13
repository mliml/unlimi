<template>
  <div class="space-y-6">
    <div>
      <label class="block text-lg font-medium text-gray-700 mb-6">
        {{ question.question_text }}
      </label>

      <div class="space-y-3">
        <div
          v-for="option in question.options"
          :key="option"
          @click="selectOption(option)"
          class="p-4 border-2 rounded-lg cursor-pointer transition-all duration-200"
          :class="{
            'border-primary-600 bg-primary-50': selectedOption === option,
            'border-gray-300 hover:border-primary-400': selectedOption !== option,
            'opacity-50 cursor-not-allowed': submitting
          }"
        >
          <div class="flex items-center">
            <div
              class="w-5 h-5 rounded-full border-2 mr-3 flex items-center justify-center transition-all"
              :class="{
                'border-primary-600 bg-primary-600': selectedOption === option,
                'border-gray-400': selectedOption !== option
              }"
            >
              <div v-if="selectedOption === option" class="w-2 h-2 bg-white rounded-full"></div>
            </div>
            <span class="text-gray-800">{{ option }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="flex justify-end">
      <button
        @click="handleSubmit"
        :disabled="submitting || !selectedOption"
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

const selectedOption = ref('')

function selectOption(option) {
  if (!props.submitting) {
    selectedOption.value = option
  }
}

function handleSubmit() {
  if (selectedOption.value) {
    emit('submit', selectedOption.value)
    selectedOption.value = ''
  }
}
</script>
