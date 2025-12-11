import axios from './axios'

export const authAPI = {
  login(email, password) {
    return axios.post('/api/auth/login', {
      email,
      password
    })
  },

  register(email, password) {
    return axios.post('/api/auth/register', {
      email,
      password
    })
  },

  getMe() {
    return axios.get('/api/me/overview')
  }
}
