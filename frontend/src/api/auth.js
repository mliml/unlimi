import axios from './axios'

export const authAPI = {
  login(email, password, captchaSessionId, captchaText) {
    return axios.post('/api/auth/login', {
      email,
      password,
      captcha_session_id: captchaSessionId,
      captcha_text: captchaText
    })
  },

  register(email, password, invitationCode, captchaSessionId, captchaText) {
    return axios.post('/api/auth/register', {
      email,
      password,
      invitation_code: invitationCode,
      captcha_session_id: captchaSessionId,
      captcha_text: captchaText
    })
  },

  getMe() {
    return axios.get('/api/me/overview')
  }
}

export const captchaAPI = {
  generate() {
    return axios.get('/api/captcha/generate')
  }
}
