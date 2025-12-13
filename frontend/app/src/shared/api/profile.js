import axios from './axios'

// 保留旧的 API（兼容性，可选）
export const getUserProfile = async () => {
  const response = await axios.get('/api/me/profile')
  return response.data
}

// 新增：获取 Agno memories
export const getUserMemories = async () => {
  const response = await axios.get('/api/me/memories')
  return response.data  // 直接返回数组
}
