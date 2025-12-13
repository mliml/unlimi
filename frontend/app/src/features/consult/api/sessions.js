import axios from '@/shared/api/axios'

export const sessionsAPI = {
  checkActiveSession() {
    return axios.get('/api/sessions/active')
  },

  startSession() {
    return axios.post('/api/sessions/start')
  },

  getSession(id) {
    return axios.get(`/api/sessions/${id}`)
  },

  getSessionMessages(id) {
    return axios.get(`/api/sessions/${id}/get_messages`)
  },

  sendMessage(id, content, activeDurationSeconds) {
    return axios.post(`/api/sessions/${id}/post_message`, {
      message: content,
      active_duration_seconds: activeDurationSeconds
    })
  },

  endSession(id) {
    return axios.post(`/api/sessions/${id}/end`)
  },

  getHistorySessions() {
    return axios.get('/api/sessions/history')
  }
}

export const onboardingAPI = {
  // 获取当前 onboarding 状态
  getOnboardingStatus() {
    return axios.get('/api/onboarding')
  },

  // 提交单个问题的答案
  submitAnswer(sessionId, questionNumber, answer) {
    return axios.post('/api/onboarding/answer', {
      session_id: sessionId,
      question_number: questionNumber,
      answer: answer
    })
  }
}
